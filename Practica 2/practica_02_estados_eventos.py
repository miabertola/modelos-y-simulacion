# Pregunta: si los servidores fallan y hay reintentos, cuantas solicitudes
# terminan fallidas y cuanto aumenta la demora (P95)?

# Configuracion (tiempo en minutos)
N = 200
REPLICAS = 5
SEMILLA = 2026
MAX_REINTENTOS = {"alta": 3, "normal": 2}
ESPERA_REINTENTO = 2

ESTADOS = ["creada", "esperando", "procesando", "finalizada", "fallida", "reintento"]
datos = generar_logs(5)

print("Estados posibles:", ESTADOS)

for d in datos:
    traza = []
    llegada = round(d["llegada"], 2)
    traza.append([llegada, "creada"])

    # TODO 1: agrega la transicion a "esperando".
    traza.append([llegada, "esperando"])

    # TODO 2: agrega la transicion a "procesando".
    traza.append([llegada, "procesando"])

    # TODO 3: calcula el instante de finalizacion usando llegada + servicio
    # y agrega la transicion correspondiente.
    pendiente = True
    traza.append([round(d["llegada"] + d["servicio"], 2), "finalizada"])
    pendiente = False

    print("Solicitud", d["id"], "->", traza)

# TODO 4: reglas ante falla y reintento.
# Si un intento falla y quedan reintentos: pasa a "reintento", espera y vuelve a la cola.
# La espera se duplica en cada reintento (2, 4, 8 min).
# Prioridad alta: hasta 3 reintentos. Normal: hasta 2. Si se agotan: "fallida".

def simular(lista, servidores, prob_falla):
    libres = []
    for s in range(servidores):
        libres.append(0)
    pendientes = []
    for d in lista:
        pendientes.append({"d": d, "t": d["llegada"], "intento": 0})
    demoras = []
    fallidas = 0
    while len(pendientes) > 0:
        # proximo evento: el intento que ocurre primero
        k = 0
        for i in range(len(pendientes)):
            if pendientes[i]["t"] < pendientes[k]["t"]:
                k = i
        p = pendientes[k]
        pendientes[k] = pendientes[len(pendientes) - 1]
        pendientes.pop()
        # servidor que se libera primero
        j = 0
        for i in range(servidores):
            if libres[i] < libres[j]:
                j = i
        inicio = p["t"]
        if libres[j] > inicio:
            inicio = libres[j]
        fin = inicio + p["d"]["servicio"]
        libres[j] = fin
        if randint(1, 100) > prob_falla:
            demoras.append(fin - p["d"]["llegada"])
        else:
            prioridad = p["d"]["prioridad"]
            if p["intento"] < MAX_REINTENTOS[prioridad]:
                espera = ESPERA_REINTENTO
                for x in range(p["intento"]):
                    espera = espera * 2
                pendientes.append({"d": p["d"], "t": fin + espera, "intento": p["intento"] + 1})
            else:
                fallidas = fallidas + 1
    return [fallidas / N * 100, percentil(demoras, 95)]

# Base: servidor siempre libre (N servidores). Desafío: solo 2 servidores.
# Con 2 servidores y 0 % de fallas debe dar 14.1, igual que la Práctica 1 (verificación).
for servidores in [N, 2]:
    for prob in [0, 10, 20]:
        fallidas = []
        p95s = []
        for r in range(REPLICAS):
            rng_seed(SEMILLA + r)
            res = simular(generar_logs(N, SEMILLA + r), servidores, prob)
            fallidas.append(res[0])
            p95s.append(res[1])
        print("Servidores:", servidores, "| fallas:", prob, "% | fallidas:", round(media(fallidas), 1), "% | P95:", round(media(p95s), 1), "min")
