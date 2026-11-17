# -*- coding: utf-8 -*-
"""
Módulo de Enrutamiento: Rutas Mínimas (Dijkstra y Bellman-Ford)
Proyecto - Bitácora 2
"""

import heapq
from typing import Any, Dict, List, Optional, Set, Tuple

class NegativeWeightError(ValueError):
    """Excepción lanzada cuando Dijkstra detecta un enlace con peso negativo."""
    pass

class NegativeCycleError(ValueError):
    """Excepción lanzada al detectar un ciclo de absorción negativa en la red."""
    pass

# Estructura del Grafo de Red (Lista de Adyacencia):
# {nodo_origen: {nodo_destino: costo_o_latencia}}
GrafoRed = Dict[Any, Dict[Any, float]]

def dijkstra(
    grafo: GrafoRed, origen: Any
) -> Tuple[Dict[Any, float], Dict[Any, Optional[Any]]]:
    """Calcula las rutas de menor latencia usando Dijkstra (Min-Heap).

    Complejidad Temporal: O((V + E) log V)
    Complejidad Espacial: O(V + E)

    Precondición:
        Todos los pesos de los enlaces deben ser NO NEGATIVOS (peso >= 0).

    Postcondición:
        Retorna (distancias_minimas, predecesores_ruta).

    Raises:
        NegativeWeightError: Si existe algún enlace con crédito/peso negativo.
    """
    if origen not in grafo and not grafo:
        return {}, {}

    vertices: Set[Any] = set(grafo.keys())
    for u in grafo:
        for v in grafo[u]:
            vertices.add(v)

    distancias: Dict[Any, float] = {v: float("inf") for v in vertices}
    predecesores: Dict[Any, Optional[Any]] = {v: None for v in vertices}

    if origen in distancias:
        distancias[origen] = 0.0

    # Min-Heap: (costo_acumulado, nodo_actual)
    cola_prioridad: List[Tuple[float, Any]] = [(0.0, origen)]

    while cola_prioridad:
        costo_u, u = heapq.heappop(cola_prioridad)

        if costo_u > distancias[u]:
            continue

        for v, peso in grafo.get(u, {}).items():
            # Validación de la restricción fundamental de Dijkstra
            if peso < 0:
                raise NegativeWeightError(
                    f"[ERROR DIJKSTRA] Enlace de red no permitido ({u} -> {v}) con costo negativo: {peso}."
                )

            # Pasada de Relajación
            if distancias[u] + peso < distancias[v]:
                distancias[v] = distancias[u] + peso
                predecesores[v] = u
                heapq.heappush(cola_prioridad, (distancias[v], v))

    return distancias, predecesores


def bellman_ford(
    grafo: GrafoRed, origen: Any
) -> Tuple[Dict[Any, float], Dict[Any, Optional[Any]]]:
    """Calcula las rutas mínimas aceptando créditos de balanceo (pesos negativos).

    Complejidad Temporal: O(V * E)
    Complejidad Espacial: O(V)

    Precondición:
        Admite enlaces con pesos negativos.

    Postcondición:
        Retorna (distancias_minimas, predecesores_ruta).

    Raises:
        NegativeCycleError: Si detecta un ciclo de absorción negativa en la red.
    """
    vertices: Set[Any] = set(grafo.keys())
    aristas: List[Tuple[Any, Any, float]] = []

    for u in grafo:
        for v, peso in grafo[u].items():
            vertices.add(v)
            aristas.append((u, v, peso))

    if origen not in vertices and not grafo:
        return {}, {}

    distancias: Dict[Any, float] = {v: float("inf") for v in vertices}
    predecesores: Dict[Any, Optional[Any]] = {v: None for v in vertices}

    if origen in distancias:
        distancias[origen] = 0.0

    num_vertices = len(vertices)

    # V - 1 Pasadas de Relajación
    for _ in range(num_vertices - 1):
        hubo_cambio = False
        for u, v, peso in aristas:
            if (
                distancias[u] != float("inf")
                and distancias[u] + peso < distancias[v]
            ):
                distancias[v] = distancias[u] + peso
                predecesores[v] = u
                hubo_cambio = True

        # Optimización: parada temprana si el sistema converge antes
        if not hubo_cambio:
            break

    # Detección de Ciclos de Absorción Negativa (Pasada V)
    for u, v, peso in aristas:
        if (
            distancias[u] != float("inf")
            and distancias[u] + peso < distancias[v]
        ):
            raise NegativeCycleError(
                f"[ALERTA DE RED] Ciclo de absorción negativa detectado a través del enlace ({u} -> {v}). "
                "Configuración de red inválida."
            )

    return distancias, predecesores


def reconstruir_ruta(
    predecesores: Dict[Any, Optional[Any]], origen: Any, destino: Any
) -> Optional[List[Any]]:
    """Reconstruye la secuencia de nodos desde el origen hasta el destino."""
    if destino not in predecesores or (
        destino != origen and predecesores[destino] is None
    ):
        return None

    ruta = []
    actual = destino
    visitados = set()

    while actual is not None:
        if actual in visitados:
            return None  # Prevenir bucles en datos anómalos
        visitados.add(actual)
        ruta.append(actual)

        if actual == origen:
            break
        actual = predecesores[actual]

    if ruta[-1] != origen:
        return None

    ruta.reverse()
    return ruta


def enrutar_red(
    grafo: GrafoRed, origen: Any, destino: Any, forzar_algoritmo: Optional[str] = None
) -> Dict[str, Any]:
    """Selector Inteligente de Enrutamiento para el Caso de Uso Profesional.

    Analiza la topología de la red y selecciona automáticamente la estrategia óptima:
    - Si todos los enlaces son >= 0 -> Ejecuta Dijkstra por eficiencia O((V+E) log V).
    - Si existen créditos negativos -> Selecciona Bellman-Ford O(V*E).
    """
    tiene_pesos_negativos = any(
        peso < 0
        for adyacentes in grafo.values()
        for peso in adyacentes.values()
    )

    algoritmo_usado = ""
    distancias = {}
    predecesores = {}

    if forzar_algoritmo == "dijkstra" or (
        not tiene_pesos_negativos and forzar_algoritmo != "bellman_ford"
    ):
        algoritmo_usado = "Dijkstra (Optimizado para Latencias No Negativas)"
        distancias, predecesores = dijkstra(grafo, origen)
    else:
        algoritmo_usado = (
            "Bellman-Ford (Soporte para Créditos de Balanceo)"
        )
        distancias, predecesores = bellman_ford(grafo, origen)

    ruta = reconstruir_ruta(predecesores, origen, destino)
    costo_total = distancias.get(destino, float("inf"))

    return {
        "origen": origen,
        "destino": destino,
        "algoritmo_seleccionado": algoritmo_usado,
        "costo_total": costo_total,
        "ruta_nodos": ruta,
        "tiene_pesos_negativos": tiene_pesos_negativos,
    }

if __name__ == "__main__":
    # ==========================================
    # DEFINICIÓN DE REDES DE PRUEBA
    # ==========================================

    # Red de Telecomunicaciones Regional (Nodos = Sedes / Enrutadores)
    red_telecom: GrafoRed = {
        "Caracas": {"Valencia": 10.0, "PuertoOrdaz": 25.0},
        "Valencia": {"Barquisimeto": 12.0, "Maracaibo": 45.0},
        "PuertoOrdaz": {"Valencia": 8.0, "Maturin": 5.0},
        "Barquisimeto": {
            "Maracaibo": 15.0,
            "Maturin": -10.0,
        },  # Enlace con crédito de balanceo (-10)
        "Maturin": {"Maracaibo": 20.0},
        "Maracaibo": {},
    }

    # Red con Ciclo de Absorción Negativa (Inestabilidad en la red)
    red_invalida: GrafoRed = {
        "NodoA": {"NodoB": 5.0},
        "NodoB": {"NodoC": -4.0},
        "NodoC": {"NodoB": -2.0},  # Ciclo B -> C -> B con peso total -6 (Bucle infinito de reducción de costo)
    }

    # ==========================================
    # EJECUCIÓN DE CASOS DE PRUEBA
    # ==========================================

    print("=== CASO 1: ENRUTAMIENTO AUTOMÁTICO (DETECTA CRÉDITOS NEGATIVOS) ===")
    resultado = enrutar_red(red_telecom, origen="Caracas", destino="Maracaibo")
    print(f"Algoritmo: {resultado['algoritmo_seleccionado']}")
    print(f"Ruta Óptima: {' -> '.join(resultado['ruta_nodos'])}")
    print(f"Costo Total de Transmisión: {resultado['costo_total']} ms\n")

    print(
        "=== CASO 2: FALLO CONTROLADO AL FORZAR DIJKSTRA EN PESOS NEGATIVOS ==="
    )
    try:
        enrutar_red(
            red_telecom,
            origen="Caracas",
            destino="Maracaibo",
            forzar_algoritmo="dijkstra",
        )
    except NegativeWeightError as e:
        print(f"Captura de Excepción Exitosa: {e}\n")

    print("=== CASO 3: DETECCIÓN DE CICLO DE ABSORCIÓN NEGATIVA ===")
    try:
        bellman_ford(red_invalida, "NodoA")
    except NegativeCycleError as e:
        print(f"Alerta de Red Activada: {e}")