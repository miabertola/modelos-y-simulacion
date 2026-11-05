# Práctica 14 · Modelo híbrido
# El predictor y las utilidades de simulación ya están disponibles.

SEMILLA = 2026
UMBRAL_1_SERVIDOR = 700
UMBRAL_2_SERVIDORES = 850
ERROR_MAX = 0.15
REPLICAS = 200
UTILIZACION_MAX = 0.6

def decidir_capacidad(demanda):
    if demanda < UMBRAL_1_SERVIDOR:
        return 1
    elif demanda < UMBRAL_2_SERVIDORES:
        return 2
    return 4

def servidores_minimos(datos):
    trabajo = 0
    for d in datos:
        trabajo = trabajo + d["servicio"]
    carga = trabajo / datos[len(datos) - 1]["llegada"]
    return int(carga / UTILIZACION_MAX) + 1

horas = [6, 9, 12, 15, 18, 21]

for hora in horas:
    demanda = int(predecir_demanda(hora))

    # TODO 1: decidí la cantidad de servidores según la demanda.
    servidores = decidir_capacidad(demanda)

    # TODO 2: generá los logs del escenario con semilla reproducible.
    datos = generar_logs(demanda, SEMILLA + hora)

    # TODO 3: simulá y obtené el P95.
    p95 = round(simular_cola(datos, servidores)["p95"], 2)

    print("Hora:", hora, "Demanda:", demanda, "Servidores:", servidores, "P95:", p95)

# TODO 4: explicá cómo se propaga el error del predictor hacia la decisión de capacidad.
# El error del predictor cambia la demanda que ve la regla. Como la regla es un escalón
# (700 y 850), un error chico solo importa si cruza un umbral: ahí cambia la cantidad de
# servidores y, con ella, el P95. Lejos de los umbrales el error no cambia la decisión.
print("---")
print("Contratos de datos (verificación):")
contrato_demanda = True
contrato_regla = True
contrato_logs = True
contrato_resultado = True
for hora in horas:
    demanda = predecir_demanda(hora)
    if demanda <= 0:
        contrato_demanda = False
    if decidir_capacidad(int(demanda)) != decidir_servidores(int(demanda)):
        contrato_regla = False
    datos = generar_logs(int(demanda), SEMILLA + hora)
    if len(datos) != int(demanda):
        contrato_logs = False
    anterior = 0
    for d in datos:
        if d.get("id") == None or d.get("servicio") == None or d.get("prioridad") == None:
            contrato_logs = False
        if d["llegada"] < anterior or d["servicio"] <= 0:
            contrato_logs = False
        anterior = d["llegada"]
    r = simular_cola(datos, 2)
    if r["p95"] < 0 or len(r["latencias"]) != len(datos):
        contrato_resultado = False
print("Predictor devuelve demanda positiva:", contrato_demanda)
print("Regla propia coincide con decidir_servidores():", contrato_regla)
print("Logs con campos completos, llegadas ordenadas y cantidad igual a la demanda:", contrato_logs)
print("Simulador devuelve una latencia por solicitud:", contrato_resultado)

print("---")
print("Propagación del error del predictor: error relativo triangular de -15 % a +15 %,", REPLICAS, "réplicas por hora")
rng_seed(SEMILLA)
for hora in horas:
    demanda = int(predecir_demanda(hora))
    serv_plan = decidir_capacidad(demanda)
    cambios = 0
    suma_plan = 0
    suma_real = 0
    for rep in range(REPLICAS):
        error = triangular(-ERROR_MAX, ERROR_MAX, 0)
        demanda_real = int(demanda * (1 + error))
        serv_real = decidir_capacidad(demanda_real)
        datos = generar_logs(demanda_real, 1000 + rep)
        suma_plan = suma_plan + simular_cola(datos, serv_plan)["p95"]
        suma_real = suma_real + simular_cola(datos, serv_real)["p95"]
        if serv_real != serv_plan:
            cambios = cambios + 1
    print("Hora:", hora, "Demanda prevista:", demanda, "Servidores:", serv_plan,
          "| decisión distinta a la de la demanda real:", round(cambios / REPLICAS * 100, 1), "%",
          "| P95 medio con la decisión del predictor:", round(suma_plan / REPLICAS, 1),
          "| con la decisión de la demanda real:", round(suma_real / REPLICAS, 1))

print("---")
print("Comparación con el modelo base (2 servidores fijos todo el día):")
total_hibrido = 0
total_base = 0
for hora in horas:
    demanda = int(predecir_demanda(hora))
    serv_h = decidir_capacidad(demanda)
    datos = generar_logs(demanda, SEMILLA + hora)
    p95_h = round(simular_cola(datos, serv_h)["p95"], 2)
    p95_b = round(simular_cola(datos, 2)["p95"], 2)
    total_hibrido = total_hibrido + serv_h
    total_base = total_base + 2
    print("Hora:", hora, "| híbrido:", serv_h, "servidores, P95", p95_h, "| base: 2 servidores, P95", p95_b)
print("Servidores-hora (suma de servidores en las 6 franjas): híbrido", total_hibrido, "| base", total_base)

# DESAFÍO: cambio estructural en la regla de capacidad.
# La regla deja de depender solo de la demanda: se agrega un mínimo de servidores
# calculado desde los propios logs para que la utilización no supere 0.6.
# Por eso el modelo cambia: ahora hay que generar los logs ANTES de decidir.
print("---")
print("DESAFÍO: regla con mínimo de estabilidad calculado desde los logs")
total_nueva = 0
for hora in horas:
    demanda = int(predecir_demanda(hora))
    datos = generar_logs(demanda, SEMILLA + hora)
    minimo = servidores_minimos(datos)
    serv_n = max([decidir_capacidad(demanda), minimo])
    p95_n = round(simular_cola(datos, serv_n)["p95"], 2)
    total_nueva = total_nueva + serv_n
    print("Hora:", hora, "Demanda:", demanda, "Mínimo por logs:", minimo, "Servidores:", serv_n, "P95:", p95_n)
print("Servidores-hora: regla nueva", total_nueva, "| híbrido original", total_hibrido, "| base", total_base)
