# Práctica 15 · Gemelo digital simplificado
# Estado digital inicial.

SEMILLA = 2026
SERVIDORES_ACTUALES = 2
SERVIDORES_ALTERNATIVOS = 4
UMBRAL_P95 = 10

def cola_al_cierre(resultado, datos):
    ultima = datos[len(datos) - 1]["llegada"]
    esperando = 0
    for e in resultado["eventos"]:
        if e["inicio"] > ultima:
            esperando = esperando + 1
    return esperando

def con_cola_inicial(datos, cola):
    trabajo = 0
    for d in datos:
        trabajo = trabajo + d["servicio"]
    medio = trabajo / len(datos)
    lista = []
    for k in range(cola):
        lista.append({"id": 0, "llegada": 0, "servicio": medio, "prioridad": "normal"})
    for d in datos:
        lista.append(d)
    return lista

rng_seed(SEMILLA)
estado = {"cpu": 20, "memoria": 40, "cola": 0, "latencia": 0}
suma_actual = 0
suma_alternativo = 0
ciclos_con_mejora = 0

for ciclo in range(5):
    cantidad = randint(200, 399)
    datos = generar_logs(cantidad, SEMILLA + ciclo)
    actual = simular_cola(datos, SERVIDORES_ACTUALES)

    # TODO 1: actualizá CPU, cola y latencia del estado digital.
    estado["cpu"] = round(actual["utilizacion"] * 100)
    estado["cola"] = cola_al_cierre(actual, datos)
    estado["latencia"] = round(actual["promedio"], 2)

    print("Ciclo:", ciclo, "Estado:", estado)

    # TODO 2: ejecutá un escenario "qué pasaría si" con 4 servidores.
    alternativo = simular_cola(datos, SERVIDORES_ALTERNATIVOS)

    # TODO 3: compará el P95 actual con el escenario alternativo.
    p95_actual = round(actual["p95"], 2)
    p95_alternativo = round(alternativo["p95"], 2)
    mejora = round(p95_actual - p95_alternativo, 2)
    suma_actual = suma_actual + p95_actual
    suma_alternativo = suma_alternativo + p95_alternativo
    if mejora > 0:
        ciclos_con_mejora = ciclos_con_mejora + 1
    print("   Solicitudes:", cantidad, "| P95 actual (2 servidores):", p95_actual, "| P95 con 4 servidores:", p95_alternativo, "| mejora:", mejora)

print("---")
print("P95 promedio de los 5 ciclos: actual", round(suma_actual / 5, 2), "| con 4 servidores", round(suma_alternativo / 5, 2))
print("Ciclos en que 4 servidores mejoran el P95:", ciclos_con_mejora, "de 5")

# TODO 4: registrá riesgos de gobernanza y seguridad de la telemetría.
riesgos = [
    "Integridad: una métrica falsa o alterada lleva al gemelo a decidir con un estado incorrecto.",
    "Retraso o pérdida de datos: el gemelo queda desactualizado y los escenarios parten de un estado viejo.",
    "Confidencialidad: la telemetría puede revelar la carga y los puntos débiles del servicio.",
    "Acceso: quién puede leer el estado y quién puede ejecutar escenarios debe estar controlado y registrado.",
    "Calidad: sin validar rangos (CPU entre 0 y 100, cola no negativa) un dato corrupto pasa como real.",
    "Responsabilidad: el gemelo recomienda, pero la decisión de cambiar capacidad la toma una persona."
]
print("---")
print("Riesgos de gobernanza y seguridad de la telemetría:")
for r in riesgos:
    print("-", r)

# DESAFÍO: cambio estructural. Una falla de capacidad y una cola que se arrastra entre ciclos.
# Hasta acá cada ciclo era independiente y arrancaba con la cola vacía.
# Ahora un servidor falla en los ciclos 2 y 3 (queda 1) y se repara en el 4. La cola de
# un ciclo pasa al siguiente, así que el gemelo debe guardar la cola y parte desde ella.
print("---")
print("DESAFÍO: falla de un servidor en los ciclos 2 y 3, con la cola heredada entre ciclos")
rng_seed(SEMILLA)
servidores_ciclo = [2, 2, 1, 1, 2]
cola_heredada = 0
for ciclo in range(5):
    cantidad = randint(200, 399)
    datos = generar_logs(cantidad, SEMILLA + ciclo)
    independiente = simular_cola(datos, servidores_ciclo[ciclo])
    datos_con_cola = con_cola_inicial(datos, cola_heredada)
    con_estado = simular_cola(datos_con_cola, servidores_ciclo[ciclo])
    cola_heredada = cola_al_cierre(con_estado, datos_con_cola)
    print("Ciclo:", ciclo, "Servidores:", servidores_ciclo[ciclo], "| P95 sin arrastrar cola:", round(independiente["p95"], 2), "| P95 arrastrando cola:", round(con_estado["p95"], 2), "| cola al cierre:", cola_heredada)
