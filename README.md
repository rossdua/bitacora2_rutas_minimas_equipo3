# Bitácora 2: Rutas Míminas Dijkstra y Bellman-Ford (Equipo 3)

Implementación, validación formal y evaluación experimental de los algoritmos de rutas mínimas **Dijkstra** (O((V+E)\log V)) y **Bellman-Ford** (O(VE)) aplicados a redes de telecomunicaciones.

## Estructura del Repositorio

```text
bitacora2_rutas_minimas_equipo3/
├── README.md
├── requirements.txt
├── src/
│   └── ejercico_rutas_minimas.py
├── tests/
│   └── test_rutas_minimas.py
└── experiments/
    ├── benchmark_piloto.py
    └── grafica_piloto.png
```

## Requisitos e Instalación

1. **Clonar el repositorio y acceder al directorio:**
   ```bash
   git clone <url-del-repositorio>
   cd bitacora2_rutas_minimas_equipo3
   ```

2. **(Opcional) Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux / macOS:
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   python -m pip install -r requirements.txt
   ```

## Comandos de Ejecución

* **Ejecutar demostración del enrutador inteligente (caso de uso):**
  ```bash
  python src/ejercico_rutas_minimas.py
  ```

* **Ejecutar suite completa de pruebas (unitarias, propiedades y diferencial con NetworkX):**
  ```bash
  pytest -v
  ```

* **Reproducir medición piloto y generar la gráfica comparativa:**
  ```bash
  python experiments/benchmark_piloto.py
  ```
  *(El gráfico resultante se guardará automáticamente en `experiments/grafica_piloto.png`).*