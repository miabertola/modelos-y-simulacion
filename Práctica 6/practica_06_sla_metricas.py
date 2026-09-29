"""Práctica 6 · Latencia, throughput y acuerdos de servicio.

Evalúa el cumplimiento de un SLA para tres niveles de carga y propone la
capacidad mínima que cumple el objetivo en cada escenario.
"""

import csv
import math
import random
from pathlib import Path


SEMILLA = 2026
SERVIDORES_BASE = 2
UMBRAL_P95 = 10.0
TASA_MAX_ERRORES = 0.01
UMBRAL_TIMEOUT = 15.0
MAX_SERVIDORES_A_EVALUAR = 8
RESULTADOS = Path(__file__).parent / "resultados"

# El factor indica cuán intensa es la demanda respecto del escenario medio.
ESCENARIOS = [
    {"nombre": "baja", "solicitudes": 500, "factor_demanda": 0.75},
    {"nombre": "media", "solicitudes": 1000, "factor_demanda": 1.00},
    {"nombre": "alta", "solicitudes": 2000, "factor_demanda": 2.00},
]


def percentil(valores, porcentaje):
    ordenados = sorted(valores)
    posicion = (len(ordenados) - 1) * porcentaje / 100
    inferior = math.floor(posicion)
    superior = math.ceil(posicion)
    if inferior == superior:
        return ordenados[inferior]
    return (ordenados[inferior] * (superior - posicion)
            + ordenados[superior] * (posicion - inferior))


def generar_logs(cantidad, semilla, factor_demanda):
    """Genera llegadas y servicios reproducibles.

    Un factor mayor a uno reduce el tiempo entre llegadas y representa una
    demanda más intensa. Los tiempos de servicio se mantienen comparables.
    """
    rng = random.Random(semilla)
    datos = []
    llegada = 0.0
    for identificador in range(1, cantidad + 1):
        llegada += rng.expovariate(factor_demanda / 3)
        prioridad = "alta" if rng.random() < 0.2 else "normal"
        mediana = 5.5 if prioridad == "alta" else 3.5
        servicio = max(0.1, rng.lognormvariate(math.log(mediana), 0.35))
        datos.append({"id": identificador, "llegada": llegada,
                      "servicio": servicio, "prioridad": prioridad})
    return datos


def simular_cola(datos, servidores):
    """Simula una cola FIFO con servidores idénticos."""
    disponibles = [0.0] * servidores
    latencias = []
    for solicitud in datos:
        indice = min(range(servidores), key=lambda i: disponibles[i])
        inicio = max(solicitud["llegada"], disponibles[indice])
        fin = inicio + solicitud["servicio"]
        disponibles[indice] = fin
        latencias.append(fin - solicitud["llegada"])

    horizonte = max(disponibles)
    trabajo_total = sum(solicitud["servicio"] for solicitud in datos)
    errores = sum(latencia > UMBRAL_TIMEOUT for latencia in latencias)
    return {
        "promedio": sum(latencias) / len(latencias),
        "p95": percentil(latencias, 95),
        "p99": percentil(latencias, 99),
        "throughput": len(datos) / horizonte,
        "utilizacion": trabajo_total / (horizonte * servidores),
        "errores": errores,
        "tasa_errores": errores / len(datos),
    }


def cumple_sla(resultado):
    return resultado["p95"] < UMBRAL_P95 and resultado["tasa_errores"] <= TASA_MAX_ERRORES


def capacidad_recomendada(datos):
    """Busca la menor cantidad de servidores que cumple ambos objetivos del SLA."""
    for servidores in range(1, MAX_SERVIDORES_A_EVALUAR + 1):
        resultado = simular_cola(datos, servidores)
        if cumple_sla(resultado):
            return servidores, resultado
    return None, None


def guardar_csv(nombre, filas):
    destino = RESULTADOS / nombre
    RESULTADOS.mkdir(exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as archivo:
        columnas = list(filas[0].keys())
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    return destino


def mostrar_tabla_prueba(filas, nombre_escenario):
    """Muestra en consola la comparación de servidores de un escenario."""
    print(f"\nComparación de capacidad · carga {nombre_escenario}")
    print("Serv. | P95     | P99     | Throughput | Utilización | Errores | SLA")
    print("------|---------|---------|------------|-------------|---------|----")
    for fila in filas:
        print(f"{fila['servidores']:>5} | {fila['p95']:>7.2f} | {fila['p99']:>7.2f} | "
              f"{fila['throughput']:>10.3f} | {fila['utilizacion_porcentaje']:>10.2f}% | "
              f"{fila['tasa_errores_porcentaje']:>6.2f}% | {fila['cumple_sla']}")


def main():
    filas_sla = []
    filas_capacidad = []
    filas_comparacion = []
    print("Práctica 6 · Latencia, throughput y acuerdos de servicio")
    print(f"SLA: P95 < {UMBRAL_P95} y tasa de errores <= {TASA_MAX_ERRORES:.0%}")
    print(f"Un error se registra cuando la latencia supera {UMBRAL_TIMEOUT}.\n")

    for indice, escenario in enumerate(ESCENARIOS):
        datos = generar_logs(escenario["solicitudes"], SEMILLA + indice,
                             escenario["factor_demanda"])
        base = simular_cola(datos, SERVIDORES_BASE)
        cumple = cumple_sla(base)
        comparacion_escenario = []

        for servidores in range(1, MAX_SERVIDORES_A_EVALUAR + 1):
            candidato = simular_cola(datos, servidores)
            fila_comparacion = {
                "escenario": escenario["nombre"],
                "servidores": servidores,
                "p95": round(candidato["p95"], 4),
                "p99": round(candidato["p99"], 4),
                "throughput": round(candidato["throughput"], 4),
                "utilizacion_porcentaje": round(candidato["utilizacion"] * 100, 2),
                "errores": candidato["errores"],
                "tasa_errores_porcentaje": round(candidato["tasa_errores"] * 100, 2),
                "cumple_sla": "SI" if cumple_sla(candidato) else "NO",
            }
            comparacion_escenario.append(fila_comparacion)
            filas_comparacion.append(fila_comparacion)

        recomendados, resultado_recomendado = capacidad_recomendada(datos)

        fila_sla = {
            "escenario": escenario["nombre"],
            "solicitudes": escenario["solicitudes"],
            "factor_demanda": escenario["factor_demanda"],
            "servidores_evaluados": SERVIDORES_BASE,
            "p95": round(base["p95"], 4),
            "p99": round(base["p99"], 4),
            "throughput": round(base["throughput"], 4),
            "utilizacion_porcentaje": round(base["utilizacion"] * 100, 2),
            "errores": base["errores"],
            "tasa_errores_porcentaje": round(base["tasa_errores"] * 100, 2),
            "cumple_sla": "SI" if cumple else "NO",
        }
        filas_sla.append(fila_sla)

        filas_capacidad.append({
            "escenario": escenario["nombre"],
            "servidores_recomendados": recomendados or "No encontrado",
            "p95_con_capacidad_recomendada": round(resultado_recomendado["p95"], 4)
            if resultado_recomendado else "-",
            "tasa_errores_porcentaje": round(resultado_recomendado["tasa_errores"] * 100, 2)
            if resultado_recomendado else "-",
        })

        print(f"Escenario: {escenario['nombre']} | solicitudes: {escenario['solicitudes']}")
        print(f"P95: {base['p95']:.2f} | P99: {base['p99']:.2f} | "
              f"Throughput: {base['throughput']:.3f}")
        print(f"Errores: {base['errores']} ({base['tasa_errores']:.2%}) | "
              f"Cumple SLA: {'Sí' if cumple else 'No'}")
        print(f"Capacidad recomendada: {recomendados or 'no encontrada'} servidores\n")
        mostrar_tabla_prueba(comparacion_escenario, escenario["nombre"])

    tabla_sla = guardar_csv("evaluacion_sla.csv", filas_sla)
    tabla_comparacion = guardar_csv("comparacion_capacidad.csv", filas_comparacion)
    tabla_capacidad = guardar_csv("plan_capacidad.csv", filas_capacidad)
    print(f"Resultados guardados en:\n- {tabla_sla}\n- {tabla_comparacion}\n- {tabla_capacidad}")


if __name__ == "__main__":
    main()
