# Práctica 9 · Diseño de experimentos
# Factores y niveles definidos por la práctica.

niveles_servidores = [1, 2, 4]
niveles_carga = [500, 1000, 2000]
replicas = 10

for servidores in niveles_servidores:
    for carga in niveles_carga:
        valores = []

        for rep in range(replicas):
            datos = generar_logs(carga, 1000 + rep)

            r = simular_cola(datos, servidores)
            valores.append(r["p95"])

        p95_medio = media(valores)
        print("Servidores:", servidores, "Carga:", carga, "-> P95 medio:", round(p95_medio, 2), "| desvío:", round(desvio(valores), 2))
