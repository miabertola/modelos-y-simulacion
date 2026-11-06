# Práctica 16 · Auditoría e integración final

estructura = {
    "README.md": True,
    "src": True,
    "resultados": True,
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
    ["Eventos discretos", "calendario de eventos (engine.py)", "casos manuales y eventos simultáneos"],
    ["Colas y capacidad", "5 cajas, prioridad no expropiativa", "sin superposición ni exceso de capacidad"],
    ["Monte Carlo", "30 semanas por política, entradas comunes", "reproducibilidad por semilla"],
    ["Diseño experimental", "6 políticas, referencia 5/4/3", "misma demanda y personal en cada comparación"],
    ["Sensibilidad", "demanda, escaneo, efectivo, promoción", "plan sensibilidad"],
    ["Verificación y validación", "108 tests e invariantes", "validación con datos reales pendiente"]
]
for fila in matriz:
    print(fila[0], "|", fila[1], "|", fila[2])

corrida_1 = 25.05
corrida_2 = 25.05
tests_ok = 108
tests_total = 108
invariantes_ok = True

print("\nReproducible:", corrida_1 == corrida_2, "| espera media:", corrida_1, "min")
print("\nTests:", tests_ok, "de", tests_total, "| invariantes ok:", invariantes_ok)

controles = {
    "tests": True,
    "validacion_empirica": False
}

pendientes = []
for control in ["tests", "validacion_empirica"]:
    if controles[control] == False:
        pendientes.append(control)

print("\nControles pendientes:", pendientes)