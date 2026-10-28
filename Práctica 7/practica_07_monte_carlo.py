# Práctica 7 · Monte Carlo aplicado a costos y plazos
# Utilidades disponibles: rng_seed(), triangular(), lognormal() y percentil().

rng_seed(2026)
costos = []
plazos = []
paralelo = []
replicas = 10000

for i in range(replicas):
    # TODO 1: simulá la duración total de las tres tareas.
    t1 = triangular(8, 15, 10)
    t2 = triangular(12, 24, 16)
    t3 = triangular(5, 12, 8)
    duracion = t1 + t2 + t3

    # TODO 2: simulá el costo total de tres componentes.
    # Cada componente puede obtenerse con lognormal(10.2, 0.18).
    costo = lognormal(10.2, 0.18) + lognormal(10.2, 0.18) + lognormal(10.2, 0.18)

    plazos.append(duracion)
    costos.append(costo)
    # DESAFÍO: plazo si la tarea 3 se hace en paralelo con la tarea 2
    paralelo.append(t1 + max([t2, t3]))

# TODO 3: calculá P50, P80, P90 y P95 para plazo y costo.
print("Réplicas realizadas:", len(plazos))
for p in [50, 80, 90, 95]:
    print("P" + str(p), "plazo:", round(percentil(plazos, p), 1), "días | costo:", round(percentil(costos, p)))

# TODO 4: calculá la probabilidad de que el plazo supere 45 días.
cuenta = 0
for d in plazos:
    if d > 45:
        cuenta = cuenta + 1
print("Probabilidad de superar 45 días:", round(cuenta / len(plazos) * 100, 2), "%")

# DESAFÍO: comparación con la tarea 3 en paralelo
cuenta = 0
for d in paralelo:
    if d > 45:
        cuenta = cuenta + 1
print("Paralelo, P90 del plazo:", round(percentil(paralelo, 90), 1), "días")
print("Paralelo, probabilidad de superar 45 días:", round(cuenta / len(paralelo) * 100, 2), "%")
