# Práctica 10 · Análisis de sensibilidad
# Se parte de un único conjunto base para comparar de manera controlada.

base = generar_logs(1000)
factores = [0.70, 0.85, 1.00, 1.15, 1.30]

for factor in factores:
    # La utilidad escalar_servicio() conserva llegadas y prioridades.
    datos_modificados = escalar_servicio(base, factor)

    # TODO 1: calculá el P95 con 2 servidores.
    p95 = round(simular_cola(datos_modificados, 2)["p95"], 2)
    print("Factor de servicio:", factor, "P95:", p95)

# TODO 2: repetí el análisis variando servidores entre 1, 2, 3 y 4.
print("---")
print("P95 por servidores (filas) y factor de servicio (columnas):", factores)
tabla = []
utilizaciones = []
for servidores in [1, 2, 3, 4]:
    fila = []
    fila_util = []
    for factor in factores:
        r = simular_cola(escalar_servicio(base, factor), servidores)
        fila.append(round(r["p95"], 2))
        fila_util.append(round(r["utilizacion"], 2))
    tabla.append(fila)
    utilizaciones.append(fila_util)
    print("Servidores:", servidores, "P95:", fila, "Utilización:", fila_util)

# TODO 3: identificá umbrales y posibles no linealidades.
print("---")
print("Incremento del P95 entre factores consecutivos (2 servidores):")
for j in range(1, 5):
    salto = round(tabla[1][j] - tabla[1][j - 1], 2)
    print("Factor", factores[j - 1], "a", factores[j], "-> +", salto)

print("Primer factor con P95 mayor a 10 para cada cantidad de servidores:")
for i in range(4):
    primero = "ninguno"
    for j in range(5):
        if tabla[i][j] > 10 and primero == "ninguno":
            primero = factores[j]
    print("Servidores:", i + 1, "->", primero)

# Sensibilidad uno por vez y diagrama tornado.
# Caso base: factor 1.00 y 2 servidores. Se mueve una variable por vez.
p95_base = tabla[1][2]

p95_factor_bajo = tabla[1][1]
p95_factor_alto = tabla[1][3]

p95_serv_mas = tabla[2][2]

semillas = []
for s in range(2026, 2031):
    semillas.append(simular_cola(generar_logs(1000, s), 2)["p95"])

nombres = ["Factor de servicio (0.85 a 1.15)", "Servidores (2 a 3)", "Semilla de los datos (2026 a 2030)"]
saltos = [abs(p95_factor_alto - p95_factor_bajo), abs(p95_base - p95_serv_mas), max(semillas) - min(semillas)]

print("---")
print("Diagrama tornado (variación del P95 respecto del caso base, P95 base:", p95_base, ")")
print("Con 1 servidor el sistema se satura (utilización 1.0) y el P95 es", tabla[0][2], "; se analiza aparte.")
orden = []
for k in range(3):
    mejor = -1
    for j in range(3):
        if j not in orden:
            if mejor == -1:
                mejor = j
            elif saltos[j] > saltos[mejor]:
                mejor = j
    orden.append(mejor)

primero = orden[0]
mayor = saltos[primero]
for j in orden:
    largo = int(saltos[j] / mayor * 40)
    if largo < 1:
        largo = 1
    barra = ""
    for k in range(largo):
        barra = barra + "#"
    print(nombres[j], "|", barra, round(saltos[j], 2))

# Interacción: ¿el efecto del factor de servicio depende de la cantidad de servidores?
print("---")
print("Efecto de pasar el factor de 0.70 a 1.30 según servidores (sin interacción serían iguales):")
for i in range(4):
    print("Servidores:", i + 1, "-> cambio del P95:", round(tabla[i][4] - tabla[i][0], 2))

# DESAFÍO: un servidor dedicado a prioridad alta (dos colas separadas) frente a un único pool.
alta = []
normal = []
for d in base:
    if d["prioridad"] == "alta":
        alta.append(d)
    else:
        normal.append(d)

print("---")
print("DESAFÍO: pool único frente a un servidor dedicado a prioridad alta")
print("Solicitudes de prioridad alta:", len(alta), "de", len(base))
for total in [2, 3, 4]:
    pool = simular_cola(base, total)
    r_alta = simular_cola(alta, 1)
    r_normal = simular_cola(normal, total - 1)
    latencias = []
    for x in r_alta["latencias"]:
        latencias.append(x)
    for x in r_normal["latencias"]:
        latencias.append(x)
    print("Servidores:", total, "P95 pool:", round(pool["p95"], 2), "P95 separado:", round(percentil(latencias, 95), 2), "P95 alta:", round(r_alta["p95"], 2), "P95 normal:", round(r_normal["p95"], 2))
