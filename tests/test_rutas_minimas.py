import os
import random
import unittest
import sys
import networkx as nx
from hypothesis import HealthCheck, given, settings, strategies as st

# Importar desde src/ estando dentro de la carpeta tests/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ejercico_rutas_minimas import (
    NegativeCycleError,
    NegativeWeightError,
    bellman_ford,
    dijkstra,
)


class TestRutasMinimas(unittest.TestCase):

    def setUp(self):
        # Semilla fija y reproducible exigida para la prueba diferencial
        random.seed(42)

    # ==========================================
    # 5 PRUEBAS UNITARIAS (CASOS LÍMITE)
    # ==========================================

    def test_grafo_vacio(self):
        """Caso 1: Grafo sin nodos ni aristas."""
        grafo = {}
        dist, prev = dijkstra(grafo, "A")
        self.assertEqual(dist, {})
        self.assertEqual(prev, {})

    def test_un_solo_nodo(self):
        """Caso 2: Grafo con un único nodo aislado."""
        grafo = {"A": {}}
        dist, _ = dijkstra(grafo, "A")
        self.assertEqual(dist["A"], 0.0)

    def test_nodos_desconectados(self):
        """Caso 3: Destino inalcanzable (distancia debe ser infinito)."""
        grafo = {"A": {"B": 5}, "B": {}, "C": {"D": 2}, "D": {}}
        dist, _ = bellman_ford(grafo, "A")
        self.assertEqual(dist["C"], float("inf"))

    def test_dijkstra_falla_pesos_negativos(self):
        """Caso 4: Dijkstra debe abortar si detecta enlaces negativos."""
        grafo = {"A": {"B": 5}, "B": {"C": -2}, "C": {}}
        with self.assertRaises(NegativeWeightError):
            dijkstra(grafo, "A")

    def test_bellman_ford_detecta_ciclo_negativo(self):
        """Caso 5: Bellman-Ford debe detectar ciclos de absorción negativa."""
        grafo = {
            "A": {"B": 1},
            "B": {"C": -5},
            "C": {"A": 2},
        }  # Ciclo: 1 - 5 + 2 = -2
        with self.assertRaises(NegativeCycleError):
            bellman_ford(grafo, "A")

    # ==========================================
    # 2 PRUEBAS BASADAS EN PROPIEDADES (HYPOTHESIS)
    # ==========================================

    # Generador de grafos válidos con pesos NO negativos para Hypothesis
    @st.composite
    def grafos_positivos_strategy(draw):
        nodos = draw(
            st.lists(
                st.integers(min_value=1, max_value=20),
                min_size=2,
                max_size=10,
                unique=True,
            )
        )
        grafo = {n: {} for n in nodos}
        for u in nodos:
            # Selecciona de 0 a 3 vecinos aleatorios
            vecinos = draw(
                st.lists(
                    st.sampled_from(nodos), min_size=0, max_size=3, unique=True
                )
            )
            for v in vecinos:
                if u != v:
                    grafo[u][v] = draw(
                        st.floats(min_value=0.1, max_value=100.0)
                    )
        return grafo, nodos[0]  # Retorna grafo y nodo origen aleatorio

    # Se desactiva la alerta de lentitud para la generación aleatoria de grafos
    @settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(grafos_positivos_strategy())
    def test_propiedad_cota_relajacion(self, datos_generados):
        """Propiedad 1: Invariante de relajación d(v) <= d(u) + w(u, v).

        Para toda arista del grafo, la distancia óptima a 'v' nunca puede ser
        mayor que la distancia a 'u' más el peso de la arista (u,v).
        """
        grafo, origen = datos_generados
        dist, _ = bellman_ford(grafo, origen)

        for u in grafo:
            for v, peso in grafo[u].items():
                # Validación de la desigualdad triangular en la red
                if dist[u] != float("inf"):
                    self.assertLessEqual(
                        round(dist[v], 5), round(dist[u] + peso, 5)
                    )

    # Se desactiva la alerta de lentitud para la generación aleatoria de grafos
    @settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(grafos_positivos_strategy())
    def test_propiedad_consistencia_algoritmica(self, datos_generados):
        """Propiedad 2: Consistencia Dijkstra vs Bellman-Ford.

        Dado un grafo estrictamente >= 0, ambos algoritmos deben retornar
        exactamente los mismos costos de ruta, a pesar de su distinta
        complejidad.
        """
        grafo, origen = datos_generados
        dist_dj, _ = dijkstra(grafo, origen)
        dist_bf, _ = bellman_ford(grafo, origen)

        # Las distancias calculadas por O((V+E)logV) y O(VE) deben ser idénticas
        for nodo in dist_dj:
            self.assertAlmostEqual(dist_dj[nodo], dist_bf[nodo], places=5)

    # ==========================================
    # 1 PRUEBA DIFERENCIAL (CONTRA NETWORKX)
    # ==========================================

    def test_prueba_diferencial_networkx(self):
        """Prueba Diferencial: Contraste de nuestra implementación de Dijkstra

        contra el estándar de la industria (NetworkX) en un grafo
        pseudo-aleatorio fijo.
        """
        # 1. Construir un grafo pseudo-aleatorio complejo con semilla fija
        nodos = [f"N{i}" for i in range(50)]
        mi_grafo = {n: {} for n in nodos}
        G_nx = nx.DiGraph()

        for u in nodos:
            G_nx.add_node(u)
            for _ in range(5):  # 5 aristas salientes por nodo
                v = random.choice(nodos)
                if u != v:
                    peso = random.uniform(1.0, 50.0)
                    mi_grafo[u][v] = peso
                    G_nx.add_edge(u, v, weight=peso)

        origen = "N0"

        # 2. Ejecutar nuestra implementación
        mis_distancias, _ = dijkstra(mi_grafo, origen)

        # 3. Ejecutar implementación de referencia (NetworkX)
        nx_distancias = nx.single_source_dijkstra_path_length(G_nx, origen)

        # 4. Aserción Diferencial Nodo por Nodo
        for nodo in nodos:
            mi_dist = mis_distancias.get(nodo, float("inf"))
            nx_dist = nx_distancias.get(nodo, float("inf"))

            # Ambas implementaciones deben coincidir hasta el 5to decimal
            if mi_dist == float("inf"):
                self.assertNotIn(nodo, nx_distancias)
            else:
                self.assertAlmostEqual(mi_dist, nx_dist, places=5)


if __name__ == "__main__":
    unittest.main()