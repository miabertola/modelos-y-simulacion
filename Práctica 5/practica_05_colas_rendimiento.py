"""Práctica 5 · Colas, capacidad y rendimiento.

Compara configuraciones equivalentes de 1, 2 y 4 servidores con el mismo
conjunto de llegadas. No requiere librerías externas.
"""

import csv
import math
import random
from pathlib import Path


SEMILLA = 2026
CANTIDAD_SOLICITUDES = 1500
CONFIGURACIONES = [1, 2, 4]
ARCHIVO_RESULTADOS = Path(__file__).parent / "resultados" / "tabla_comparativa.csv"


def percentil(valores, porcentaje):
    """Calcula un percentil mediante interpolación lineal."""
    ordenados = sorted(valores)
    if not ordenados:
        return 0.0
    posicion = (len(ordenados) - 1) * porcentaje / 100
    inferior = math.floor(posicion)
    superior = math.ceil(posicion)
    if inferior == superior:
        return ordenados[inferior]
    return (ordenados[inferior] * (superior - posicion)
            + ordenados[superior] * (posicion - inferior))


def generar_logs(cantidad, semilla):
    """Genera llegadas exponenciales y tiempos de servicio lognormales."""
    rng = random.Random(semilla)
    datos = []
    tiempo = 0.0
    for identificador in range(1, cantidad + 1):
        tiempo += rng.expovariate(1 / 3)
        prioridad = "alta" if rng.random() < 0.2 else "normal"
        mediana_servicio = 5.5 if prioridad == "alta" else 3.5
        servicio = max(0.1, rng.lognormvariate(math.log(mediana_servicio), 0.35))
        datos.append({
            "id": identificador,
            "llegada": tiempo,
            "servicio": servicio,
            "prioridad": prioridad,
        })
    return datos


def simular_cola(datos, servidores):
    """Simula una cola FIFO asignando cada llegada al servidor libre primero."""
    disponibles = [0.0] * servidores
    latencias = []
    esperas = []
    eventos = []
    for solicitud in datos:
        indice = min(range(servidores), key=lambda i: disponibles[i])
        inicio = max(solicitud["llegada"], disponibles[indice])
        fin = inicio + solicitud["servicio"]
        espera = inicio - solicitud["llegada"]
        latencia = fin - solicitud["llegada"]
        disponibles[indice] = fin
        esperas.append(espera)
        latencias.append(latencia)
        eventos.append({**solicitud, "inicio": inicio, "fin": fin,
                        "espera": espera, "servidor": indice + 1})

    horizonte = max(evento["fin"] for evento in eventos)
    trabajo_total = sum(evento["servicio"] for evento in eventos)
    return {
        "eventos": eventos,
        "latencias": latencias,
        "esperas": esperas,
        "promedio": sum(latencias) / len(latencias),
        "p95": percentil(latencias, 95),
        "p99": percentil(latencias, 99),
        "throughput": len(eventos) / horizonte,
        "utilizacion": trabajo_total / (horizonte * servidores),
    }


def resumen(servidores, resultado):
    """Devuelve una fila comparable de métricas para una configuración."""
    return {
        "servidores": servidores,
        "latencia_promedio": resultado["promedio"],
        "p95": resultado["p95"],
        "p99": resultado["p99"],
        "throughput": resultado["throughput"],
        "utilizacion_porcentaje": resultado["utilizacion"] * 100,
        "espera_promedio": sum(resultado["esperas"]) / len(resultado["esperas"]),
        "espera_maxima": max(resultado["esperas"]),
    }


def guardar_tabla(filas, destino):
    """Guarda las métricas de cada escenario en CSV para incluir en el informe."""
    destino.parent.mkdir(exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as archivo:
        columnas = list(filas[0].keys())
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({clave: f"{valor:.4f}" if isinstance(valor, float) else valor
                               for clave, valor in fila.items()})


def mostrar_tabla(filas):
    print("\nTabla comparativa (unidades de tiempo del modelo):")
    print("Serv. | Promedio | P95     | P99     | Throughput | Utilización")
    print("------|----------|---------|---------|------------|------------")
    for fila in filas:
        print(f"{fila['servidores']:>5} | {fila['latencia_promedio']:>8.2f} | "
              f"{fila['p95']:>7.2f} | {fila['p99']:>7.2f} | "
              f"{fila['throughput']:>10.4f} | "
              f"{fila['utilizacion_porcentaje']:>10.2f}%")


def main():
    datos = generar_logs(CANTIDAD_SOLICITUDES, SEMILLA)
    filas = []
    print("Práctica 5 · Colas, capacidad y rendimiento")
    print(f"Registros cargados: {len(datos)} (semilla: {SEMILLA})")
    print(f"Servidores a comparar: {CONFIGURACIONES}")
    for servidores in CONFIGURACIONES:
        resultado = simular_cola(datos, servidores)
        filas.append(resumen(servidores, resultado))
    mostrar_tabla(filas)
    guardar_tabla(filas, ARCHIVO_RESULTADOS)
    print(f"\nTabla guardada en: {ARCHIVO_RESULTADOS}")


if __name__ == "__main__":
    main()
