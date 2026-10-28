# Práctica 8 · Riesgo y viabilidad
# Alternativas de referencia: nombre, costo, disponibilidad y plazo.

opciones = [
    ["fija", 120000, 99.5, 120],
    ["autoescalado", 150000, 99.95, 90],
    ["administrado", 180000, 99.99, 60]
]

for opcion in opciones:
    nombre = opcion[0]
    costo = opcion[1]
    disponibilidad = opcion[2]
    plazo = opcion[3]

    nota_disp = (disponibilidad - 99.5) / (99.99 - 99.5)
    nota_costo = (180000 - costo) / (180000 - 120000)
    nota_plazo = (120 - plazo) / (120 - 60)
    puntaje = 0.4 * nota_disp + 0.3 * nota_costo + 0.3 * nota_plazo

    print(nombre, "-> puntaje:", round(puntaje, 3))

print("")
print("Prueba de estrés (SLA: P95 < 20)")
datos = generar_logs(1000, 2026)
estres = escalar_servicio(datos, 2.0)
servidores = [2, 4, 4]

i = 0
for opcion in opciones:
    r = simular_cola(estres, servidores[i])
    print(opcion[0], "-> P95:", round(r["p95"], 2), "| utilización:", round(r["utilizacion"], 2), "| cumple:", r["p95"] < 20)
    i += 1
    
