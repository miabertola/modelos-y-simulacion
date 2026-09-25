# Práctica 1 · Reconocimiento y modelización de un sistema
# ¿Con 2 servidorrs el P95 de demora queda por debajo de 15 min, también en hora pico?
# generar_logs(), media(), percentil(), etc. ya están integradas en este laboratorio.

N=200
REPLICAS=5
SEMILLA=2026
FACTOR_PICO=0.7
OBJETIVO_P95=15

datos = generar_logs(20)
estados = {"entradas": len(datos), "procesadas": 0}

print("Sistema: plataforma de turnos")
print("Entradas observadas:", estados["entradas"])
print("Frontera: llegada -> cola -> servidor -> salida")

# TODO 1: definí qué representa el entorno del sistema.
entorno = "Usuarios que piden turnos, horarios pico y red de internet"
print("Entorno:", entorno)

# TODO 2: escribí al menos tres supuestos explícitos del modelo.
supuestos = ["Las solicitudes llegan en promedio cada 3 minutos", "No hay fallas en los servidores", "Se atiende por orden de llegada"]
print("Supuestos:", supuestos)

# TODO 3: proponé tres escenarios cambiando una condición relevante.
escenarios = ["Escenario 1: demanda normal, 2 servidores", "Escenario 2: pico (30% mas demanda), 2 servidores", "Escenario 3: pico, 3 servidores"]
print("Escenarios:", escenarios)

# Caso controlado
caso = [{"id": 1, "llegada": 0, "servicio": 3, "prioridad": "normal"}, {"id": 2, "llegada": 1, "servicio": 2, "prioridad": "normal"}, {"id": 3, "llegada": 2, "servicio": 1, "prioridad": "normal"}]
print("Caso controlado:", simular_cola(caso, 1)["latencias"])

# Corre un escenario varias veces y promedia el P95
def correr(factor, servidores):
    p95s = []
    for r in range(REPLICAS):
        lista = []
        for d in generar_logs(N, SEMILLA + r):
            lista.append({"id": d["id"], "llegada": d["llegada"] * factor, "servicio": d["servicio"], "prioridad": d["prioridad"]})
        p95s.append(simular_cola(lista, servidores)["p95"])
    return media(p95s)

print("E1 P95:", round(correr(1, 2), 1), "min")
print("E2 P95:", round(correr(FACTOR_PICO, 2), 1), "min")
print("E3 P95:", round(correr(FACTOR_PICO, 3), 1), "min")
print("Objetivo: P95 <=", OBJETIVO_P95, "min")
