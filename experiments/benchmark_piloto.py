import os
import platform
import random
import statistics
import sys
import time
import matplotlib.pyplot as plt

# Importar desde src/ estando dentro de experiments/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ejercico_rutas_minimas import bellman_ford, dijkstra


def obtener_entorno() -> str:
    """Detecta automáticamente CPU, RAM, SO y versión de Python."""
    py_ver = platform.python_version()
    so = f"{platform.system()} {platform.release()}"
    cpu = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "CPU desconocida")
    nucleos = os.cpu_count()

    ram_str = "No detectada"
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        ram_str = f"{ram_gb:.1f} GB"
    except ImportError:
        if os.name == "nt":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX(dwLength=ctypes.sizeof(MEMORYSTATUSEX))
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_str = f"{stat.ullTotalPhys / (1024 ** 3):.1f} GB"

    return f"Python {py_ver} | {so} | CPU: {cpu} ({nucleos} núcleos) | RAM: {ram_str}"


def generar_red_sintetica(num_nodos: int, grado_salida: int = 4, seed: int = 42):
    rng = random.Random(seed)
    nodos = [f"R{i}" for i in range(num_nodos)]
    grafo = {n: {} for n in nodos}

    for i, u in enumerate(nodos):
        if i + 1 < num_nodos:
            grafo[u][nodos[i + 1]] = round(rng.uniform(1.0, 20.0), 2)
        while len(grafo[u]) < min(grado_salida, num_nodos - 1):
            v = rng.choice(nodos)
            if v != u and v not in grafo[u]:
                grafo[u][v] = round(rng.uniform(1.0, 50.0), 2)

    aristas = sum(len(adj) for adj in grafo.values())
    return grafo, aristas


def medir_algoritmo(func, grafo, origen: str, repeticiones: int = 15) -> float:
    tiempos_ms = []
    func(grafo, origen)  # Warm-up
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        func(grafo, origen)
        fin = time.perf_counter()
        tiempos_ms.append((fin - inicio) * 1000.0)
    return round(statistics.median(tiempos_ms), 4)


def ejecutar_piloto():
    entorno = obtener_entorno()
    print("=== AMBIENTE DE EJECUCIÓN ===")
    print(entorno, "\n")

    tamanos_v = [50, 150, 300, 600]
    tiempos_dijk = []
    tiempos_bf = []

    print(f"{'|V|':>6} | {'|E|':>6} | {'Dijkstra (ms)':>15} | {'Bellman-Ford (ms)':>18} | {'Ratio':>8}")
    print("-" * 64)

    for v in tamanos_v:
        grafo, e = generar_red_sintetica(num_nodos=v, grado_salida=4, seed=42)
        td = medir_algoritmo(dijkstra, grafo, "R0", repeticiones=15)
        tbf = medir_algoritmo(bellman_ford, grafo, "R0", repeticiones=15)
        tiempos_dijk.append(td)
        tiempos_bf.append(tbf)
        ratio = round(tbf / td, 2) if td > 0 else 0.0
        print(f"{v:>6} | {e:>6} | {td:>15.4f} | {tbf:>18.4f} | {ratio:>7.2f}x")

    # Guardar la gráfica directamente dentro de la carpeta experiments/
    ruta_grafica = os.path.join(os.path.dirname(__file__), "grafica_piloto.png")
    
    plt.figure(figsize=(7.5, 4.2), dpi=300)
    plt.plot(tamanos_v, tiempos_dijk, marker="o", linewidth=2, label="Dijkstra O((V + E) log V)")
    plt.plot(tamanos_v, tiempos_bf, marker="s", linewidth=2, label="Bellman-Ford O(V · E)")
    plt.title("Medición Piloto: Tiempo de Ejecución vs. Tamaño de Red (|E| ≈ 4|V|)")
    plt.xlabel("Número de Routers (|V|)")
    plt.ylabel("Tiempo Mediano de Ejecución (ms)")
    plt.xticks(tamanos_v)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ruta_grafica)
    print(f"\nGráfica guardada exitosamente como '{ruta_grafica}'")


if __name__ == "__main__":
    ejecutar_piloto()