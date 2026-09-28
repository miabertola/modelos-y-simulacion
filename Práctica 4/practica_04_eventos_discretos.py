# Práctica 4 · Primera simulación de eventos discretos
# Caso determinístico proporcionado por la cátedra.

datos = [
    {"id": 1, "llegada": 0, "servicio": 3, "prioridad": "normal"},
    {"id": 2, "llegada": 1, "servicio": 2, "prioridad": "normal"},
    {"id": 3, "llegada": 2, "servicio": 1, "prioridad": "normal"}
]

print("Caso determinístico cargado:", datos)

# TODO 1: ejecutá la simulación con un servidor.
r = simular_cola(datos, 1)

# TODO 2: recorré r["eventos"] y mostralos en orden.
for e in r["eventos"]:
    print("Solicitud", e["id"], "| llega:", e["llegada"], "| inicia:", e["inicio"], "| termina:", e["fin"], "| espera:", e["espera"])

# TODO 3: mostrá promedio, P95 y utilización.
print("Promedio:", round(r["promedio"], 2), "| P95:", round(r["p95"], 2), "| Utilización:", round(r["utilizacion"] * 100), "%")

# DESAFÍO (cambio estructural): cambiar la regla de la cola.
# FIFO atiende por orden de llegada; SJF atiende primero al que tarda menos.
def simular_sjf(lista):
    pendientes = list(lista)
    reloj = 0
    demoras = []
    while len(pendientes) > 0:
        # entre los que ya llegaron, elegir el de menor servicio
        k = -1
        for i in range(len(pendientes)):
            if pendientes[i]["llegada"] <= reloj:
                if k == -1 or pendientes[i]["servicio"] < pendientes[k]["servicio"]:
                    k = i
        # si no llegó nadie, el reloj avanza hasta la próxima llegada
        if k == -1:
            reloj = pendientes[0]["llegada"]
            for p in pendientes:
                if p["llegada"] < reloj:
                    reloj = p["llegada"]
            continue
        p = pendientes[k]
        pendientes[k] = pendientes[len(pendientes) - 1]
        pendientes.pop()
        reloj = reloj + p["servicio"]
        demoras.append(reloj - p["llegada"])
    return demoras

def comparar(nombre, lista):
    fifo = simular_cola(lista, 1)["latencias"]
    sjf = simular_sjf(lista)
    print(nombre, "| FIFO promedio:", round(media(fifo), 1), "P95:", round(percentil(fifo, 95), 1), "máx:", round(max(fifo), 1))
    print(nombre, "| SJF  promedio:", round(media(sjf), 1), "P95:", round(percentil(sjf, 95), 1), "máx:", round(max(sjf), 1))

print("")
comparar("Caso", datos)
# 200 solicitudes con atención 40 % más rápida, para que 1 servidor no se sature
comparar("200 solicitudes", escalar_servicio(generar_logs(200), 0.6))
