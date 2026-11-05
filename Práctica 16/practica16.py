# Práctica 16 · Auditoría e integración final
# En el navegador no se accede automáticamente al sistema de archivos.
# Indicá True/False según la estructura real de tu entrega.

estructura = {
    "README.md": True,
    "src": True,
    "resultados": False,
    "informe": True
}

requeridos = ["README.md", "src", "resultados", "informe"]
faltantes = []

for elemento in requeridos:
    if estructura[elemento] == False:
        faltantes.append(elemento)

print("Elementos faltantes:", faltantes)

print("\nMatriz de trazabilidad")
matriz = [
    ["¿FIFO o SJF?", "P4", "promedio 12,5 vs 9,1 / máximo 33 vs 134"],
    ["¿Qué infraestructura?", "P8", "puntaje 0,3 / 0,667 / 0,7 y P95 en estrés"],
    ["¿Cuántos servidores?", "P9", "matriz 3x3, P95 1053,98 / 13,57 / 7,43"],
    ["¿Cómo predecir demanda?", "P12", "MAE baseline 23,53 vs regresión 15,7"],
    ["¿Conviene una red neuronal?", "P13", "MAE red 0,2585 vs baseline 0,4034"]
]
for fila in matriz:
    print(fila[0], "|", fila[1], "|", fila[2])


r1 = simular_cola(generar_logs(1000, 2026), 2)
r2 = simular_cola(generar_logs(1000, 2026), 2)
print("\nReproducible:", r1["p95"] == r2["p95"], "| P95:", round(r1["p95"], 2))

caso = [
    {"id": 1, "llegada": 0, "servicio": 3, "prioridad": "normal"},
    {"id": 2, "llegada": 1, "servicio": 2, "prioridad": "normal"},
    {"id": 3, "llegada": 2, "servicio": 1, "prioridad": "normal"}
]
r = simular_cola(caso, 1)
print("\nValidación caso a mano -> promedio:", round(r["promedio"], 2), "| esperado: 3.67")

valores = []
for rep in range(10):
    r = simular_cola(generar_logs(1000, 1000 + rep), 2)
    valores.append(r["p95"])
print("\nP95 con 10 semillas -> media:", round(media(valores), 2), "| mín:", round(min(valores), 2), "| máx:", round(max(valores), 2))
