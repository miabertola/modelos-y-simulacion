# Practica 3 · Logs, variabilidad y datos sinteticos
# Pregunta: que valores usar para simular la plataforma y que pasa si los logs tienen errores?
LIMITE = 60

datos = generar_logs(1000)
servicios = []

for d in datos:
    servicios.append(d["servicio"])

print("Cantidad de registros:", len(servicios))

# TODO 1: calculá media, mediana y desvío.
media_servicio = round(media(servicios), 2)
mediana_servicio = round(mediana(servicios), 2)
desvio_servicio = round(desvio(servicios), 2)

# TODO 2: calculá P95 y P99.
p95 = round(percentil(servicios, 95), 2)
p99 = round(percentil(servicios, 99), 2)

print("Media:", media_servicio)
print("Mediana:", mediana_servicio)
print("Desvío:", desvio_servicio)
print("P95:", p95)
print("P99:", p99)

# TODO 3: compará por separado las prioridades "alta" y "normal".
def resumen(nombre, xs):
    print(nombre, "| n:", len(xs), "| media:", round(media(xs), 2), "| mediana:", round(mediana(xs), 2), "| desvío:", round(desvio(xs), 2), "| P95:", round(percentil(xs, 95), 2))

alta = []
normal = []
for d in datos:
    if d["prioridad"] == "alta":
        alta.append(d["servicio"])
    else:
        normal.append(d["servicio"])
resumen("Alta  ", alta)
resumen("Normal", normal)

# Parámetros para simular
entre = []
for i in range(1, len(datos)):
    entre.append(datos[i]["llegada"] - datos[i - 1]["llegada"])
print("Entre llegadas | media:", round(media(entre), 2), "| desvío:", round(desvio(entre), 2), "| % alta:", round(len(alta) / 10, 1))

# Perfil de calidad + limpieza: descarta faltantes, inválidos (<= 0 o > LIMITE) y duplicados
def limpiar(lista):
    limpios = []
    vistos = {}
    for d in lista:
        s = d["servicio"]
        if s != None and s > 0 and s <= LIMITE and not (d["id"] in vistos):
            limpios.append(s)
        vistos[d["id"]] = True
    print("Perfil | registros:", len(lista), "| descartados:", len(lista) - len(limpios))
    return limpios

limpiar(datos)

# DESAFÍO (cambio estructural): los logs vienen con errores, hay que agregar una etapa de limpieza.
sucios = []
for i in range(len(datos)):
    d = dict(datos[i])
    if i % 50 == 1:
        d["servicio"] = None
    if i % 50 == 2:
        d["servicio"] = -d["servicio"]
    if i % 50 == 3:
        d["servicio"] = d["servicio"] * 100
    sucios.append(d)
    if i % 50 == 4:
        sucios.append(dict(d))

sin_limpiar = []
for d in sucios:
    if d["servicio"] != None:
        sin_limpiar.append(d["servicio"])
resumen("Sin limpiar", sin_limpiar)
resumen("Limpios    ", limpiar(sucios))
