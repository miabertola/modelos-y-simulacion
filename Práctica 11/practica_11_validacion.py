"""Práctica 11 · Verificación y validación de una cola.

Cola única, servidores idénticos, sin interrupciones, pérdidas ni reintentos.
Tiempo continuo en unidades abstractas. Las prioridades sólo afectan la regla
"prioridad"; FIFO desempata las llegadas simultáneas por orden de entrada.
Se atienden todas las solicitudes, aunque se deba esperar para vaciar la cola.
Sólo usa la biblioteca estándar de Python.
"""

import csv
import heapq
import json
import math
from pathlib import Path


CARPETA = Path(__file__).resolve().parent
REFERENCIA = CARPETA / "datos" / "referencia_sintetica.csv"
RESULTADOS = CARPETA / "resultados"
TOLERANCIA = 1e-9  # Coincidencia numérica con una referencia sintética exacta.
CASO_MANUAL = [
    {"id": 1, "llegada": 0, "servicio": 2, "prioridad": "normal"},
    {"id": 2, "llegada": 1, "servicio": 2, "prioridad": "normal"},
]


def percentil(valores, porcentaje):
    """Percentil con interpolación lineal; devuelve cero para una lista vacía."""
    ordenados = sorted(valores)
    if not ordenados:
        return 0.0
    posicion = (len(ordenados) - 1) * porcentaje / 100
    inferior, superior = math.floor(posicion), math.ceil(posicion)
    return (ordenados[inferior]
            + (ordenados[superior] - ordenados[inferior]) * (posicion - inferior))


def simular_cola(datos, servidores=1, regla="fifo"):
    """Simula llegadas y finalizaciones mediante un calendario de eventos.

    Se liberan los servidores antes de asignar solicitudes en el mismo instante.
    La prioridad es no expropiativa: no interrumpe una atención en curso.
    Devuelve una traza por solicitud en orden de inicio de atención.
    """
    if type(servidores) is not int or servidores < 1:
        raise ValueError("servidores debe ser un entero positivo")
    if regla not in ("fifo", "prioridad"):
        raise ValueError("regla debe ser 'fifo' o 'prioridad'")
    solicitudes = []
    identificadores = set()
    for orden, original in enumerate(datos):
        solicitud = dict(original)
        identificador = solicitud["id"]
        if identificador in identificadores:
            raise ValueError("Los identificadores deben ser únicos")
        identificadores.add(identificador)
        for campo in ("llegada", "servicio"):
            valor = solicitud[campo]
            if (isinstance(valor, bool) or not isinstance(valor, (int, float))
                    or not math.isfinite(valor) or valor < 0
                    or (campo == "servicio" and valor == 0)):
                raise ValueError(f"{campo} debe ser finito y "
                                 + ("positivo" if campo == "servicio" else "no negativo"))
        solicitud.setdefault("prioridad", "normal")
        if solicitud["prioridad"] not in ("normal", "alta"):
            raise ValueError("prioridad debe ser 'normal' o 'alta'")
        solicitudes.append((solicitud["llegada"], orden, solicitud))
    solicitudes.sort(key=lambda fila: (fila[0], fila[1]))

    libres = list(range(1, servidores + 1))
    ocupados = []  # (instante de finalización, servidor)
    cola = []  # (prioridad, llegada, orden original, solicitud)
    eventos = []
    indice, reloj = 0, 0.0
    while indice < len(solicitudes) or cola:
        while ocupados and ocupados[0][0] <= reloj:
            _, servidor = heapq.heappop(ocupados)
            heapq.heappush(libres, servidor)
        while indice < len(solicitudes) and solicitudes[indice][0] <= reloj:
            llegada, orden, solicitud = solicitudes[indice]
            prioridad = int(regla == "prioridad" and solicitud["prioridad"] != "alta")
            heapq.heappush(cola, (prioridad, llegada, orden, solicitud))
            indice += 1
        while libres and cola:
            _, llegada, _, solicitud = heapq.heappop(cola)
            servidor = heapq.heappop(libres)
            fin = reloj + solicitud["servicio"]
            if not math.isfinite(fin) or fin <= reloj:
                raise ValueError("El tiempo excede la precisión numérica disponible")
            eventos.append({**solicitud, "inicio": reloj, "fin": fin,
                            "espera": reloj - llegada, "servidor": servidor})
            heapq.heappush(ocupados, (fin, servidor))
        if indice < len(solicitudes) or cola:
            siguientes = [ocupados[0][0]] if ocupados else []
            if indice < len(solicitudes):
                siguientes.append(solicitudes[indice][0])
            reloj = min(siguientes)

    esperas = [e["espera"] for e in eventos]
    latencias = [e["fin"] - e["llegada"] for e in eventos]
    horizonte = max((e["fin"] for e in eventos), default=0.0)
    trabajo = sum(e["servicio"] for e in eventos)
    return {
        "eventos": eventos, "esperas": esperas, "latencias": latencias,
        "promedio": sum(latencias) / len(latencias) if latencias else 0.0,
        "p95": percentil(latencias, 95), "p99": percentil(latencias, 99),
        "throughput": len(eventos) / horizonte if horizonte else 0.0,
        "utilizacion": trabajo / (horizonte * servidores) if horizonte else 0.0,
        "horizonte": horizonte,
    }


def comprobar_invariantes(datos, resultado, servidores):
    """Devuelve infracciones temporales, de conservación y de capacidad."""
    errores = []
    eventos = resultado["eventos"]
    originales = {d["id"]: d for d in datos}
    ids = [e["id"] for e in eventos]
    if len(ids) != len(datos) or len(set(ids)) != len(ids) or set(ids) != set(originales):
        errores.append("No se conserva exactamente una salida por solicitud")
    por_servidor = {s: [] for s in range(1, servidores + 1)}
    for e in eventos:
        etiqueta = f"Solicitud {e['id']}"
        if not all(math.isfinite(e[c]) for c in ("llegada", "inicio", "fin", "espera")):
            errores.append(etiqueta + ": tiempo no finito")
        if not e["fin"] >= e["inicio"] >= e["llegada"]:
            errores.append(etiqueta + ": debe cumplirse fin >= inicio >= llegada")
        if not math.isclose(e["fin"] - e["inicio"], e["servicio"], abs_tol=TOLERANCIA):
            errores.append(etiqueta + ": duración de servicio incorrecta")
        if not math.isclose(e["espera"], e["inicio"] - e["llegada"], abs_tol=TOLERANCIA):
            errores.append(etiqueta + ": espera incorrecta")
        if e["id"] in originales:
            d = originales[e["id"]]
            if e["llegada"] != d["llegada"] or e["servicio"] != d["servicio"]:
                errores.append(etiqueta + ": se alteraron los datos de entrada")
        if e["servidor"] not in por_servidor:
            errores.append(etiqueta + ": servidor inexistente")
        else:
            por_servidor[e["servidor"]].append(e)
    for servidor, atendidas in por_servidor.items():
        atendidas.sort(key=lambda e: e["inicio"])
        for anterior, actual in zip(atendidas, atendidas[1:]):
            if actual["inicio"] < anterior["fin"] - TOLERANCIA:
                errores.append(f"Servidor {servidor}: atenciones superpuestas")
    if not 0 <= resultado["utilizacion"] <= 1 + TOLERANCIA:
        errores.append("Utilización fuera de [0, 1]")
    return errores


def cargar_referencia():
    """Lee observaciones sintéticas fijadas antes de ejecutar el simulador."""
    with REFERENCIA.open(encoding="utf-8", newline="") as archivo:
        return [{**fila, "id": int(fila["id"]),
                 **{c: float(fila[c]) for c in
                    ("llegada", "servicio_base", "inicio_referencia", "fin_referencia")}}
                for fila in csv.DictReader(archivo)]


def calibrar_factor(referencias):
    """Ajusta un factor de servicio sólo con el subconjunto de calibración.

    Estimador: suma de duraciones observadas / suma de servicios nominales.
    No se ajustan la regla de cola ni las llegadas.
    """
    ajuste = [f for f in referencias if f["conjunto"] == "calibracion"]
    if not ajuste or any(f["servicio_base"] <= 0
                         or f["fin_referencia"] <= f["inicio_referencia"] for f in ajuste):
        raise ValueError("La calibración requiere duraciones positivas")
    return (sum(f["fin_referencia"] - f["inicio_referencia"] for f in ajuste)
            / sum(f["servicio_base"] for f in ajuste))


def evaluar_referencia(referencias, conjunto, factor):
    filas = [f for f in referencias if f["conjunto"] == conjunto]
    if not filas:
        raise ValueError("No hay referencias para ese conjunto")
    datos = [{"id": f["id"], "llegada": f["llegada"],
              "servicio": f["servicio_base"] * factor} for f in filas]
    resultado = simular_cola(datos)
    por_id = {e["id"]: e for e in resultado["eventos"]}
    comparaciones = []
    for f in filas:
        e = por_id[f["id"]]
        comparaciones.append({
            "conjunto": conjunto, "factor": factor, "id": f["id"],
            "inicio_referencia": f["inicio_referencia"], "inicio_simulado": e["inicio"],
            "fin_referencia": f["fin_referencia"], "fin_simulado": e["fin"],
            "error_inicio": abs(e["inicio"] - f["inicio_referencia"]),
            "error_fin": abs(e["fin"] - f["fin_referencia"]),
        })
    mae = sum(f["error_fin"] for f in comparaciones) / len(comparaciones)
    return comparaciones, mae, comprobar_invariantes(datos, resultado, 1)


def guardar_csv(nombre, filas):
    with (RESULTADOS / nombre).open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    RESULTADOS.mkdir(exist_ok=True)
    r = simular_cola(CASO_MANUAL, 1)
    print("Práctica 11 · Verificación y validación")
    print("Eventos:", r["eventos"])

    # TODO 1 del manual: comprobar la finalización de la primera solicitud.
    prueba_1 = math.isclose(r["eventos"][0]["fin"], 2, abs_tol=TOLERANCIA)
    # TODO 2: comprobar la espera de la segunda solicitud.
    prueba_2 = math.isclose(r["eventos"][1]["espera"], 1, abs_tol=TOLERANCIA)
    # TODO 3: comprobar el invariante temporal para todas las solicitudes.
    prueba_3 = all(e["fin"] >= e["inicio"] >= e["llegada"] for e in r["eventos"])
    pruebas = {"prueba_1": prueba_1, "prueba_2": prueba_2, "prueba_3": prueba_3}
    errores = comprobar_invariantes(CASO_MANUAL, r, 1)
    for nombre, cumple in pruebas.items():
        print(f"{nombre}: {cumple}")
    guardar_csv("traza_caso_manual.csv", r["eventos"])

    referencias = cargar_referencia()
    factor = calibrar_factor(referencias)
    comparaciones, resumen = [], []
    for conjunto in ("calibracion", "validacion"):
        for etapa, valor in (("antes", 1.0), ("despues", factor)):
            filas, mae, infracciones = evaluar_referencia(referencias, conjunto, valor)
            comparaciones.extend({"etapa": etapa, **f} for f in filas)
            errores.extend(infracciones)
            resumen.append({"conjunto": conjunto, "etapa": etapa,
                            "factor": valor, "mae_fin": mae,
                            "cumple_tolerancia": all(
                                f["error_inicio"] <= TOLERANCIA
                                and f["error_fin"] <= TOLERANCIA for f in filas)})
            print(f"{conjunto}, {etapa}: MAE de finalización = {mae:.4f}")
    guardar_csv("comparacion_referencia.csv", comparaciones)
    guardar_csv("calibracion.csv", resumen)

    # Desafío: prioridad no expropiativa frente a FIFO; mismo servidor y datos.
    desafio = [
        {"id": 1, "llegada": 0, "servicio": 4, "prioridad": "normal"},
        {"id": 2, "llegada": 1, "servicio": 3, "prioridad": "normal"},
        {"id": 3, "llegada": 2, "servicio": 1, "prioridad": "alta"},
    ]
    tabla = []
    for regla in ("fifo", "prioridad"):
        resultado = simular_cola(desafio, regla=regla)
        errores.extend(comprobar_invariantes(desafio, resultado, 1))
        guardar_csv(f"traza_desafio_{regla}.csv", resultado["eventos"])
        tabla.append({"regla": regla, "latencia_promedio": resultado["promedio"],
                      "p95": resultado["p95"],
                      "espera_alta": next(e["espera"] for e in resultado["eventos"]
                                          if e["prioridad"] == "alta"),
                      "espera_normal_promedio": sum(e["espera"] for e in resultado["eventos"]
                                                     if e["prioridad"] == "normal") / 2})
    guardar_csv("comparacion_reglas.csv", tabla)

    # TODO 4: verificar comprueba la implementación contra las reglas definidas;
    # validar contrasta el modelo con referencias del sistema estudiado.
    # Aquí sólo hay referencias sintéticas, por lo que no se acredita validez real.
    expediente = {
        "origen_referencia": "Sintética, calculada manualmente; no son datos reales",
        "alcance": "Cola FIFO de un servidor en los casos de referencia",
        "criterio": "Errores absolutos de inicio y fin <= tolerancia",
        "tolerancia": TOLERANCIA, "factor_calibrado": factor,
        "pruebas_manual": pruebas, "infracciones_invariantes": errores,
        "comparacion": resumen,
        "limitaciones": ["No demuestra correspondencia con una plataforma real",
                         "Sin fallas, abandonos, reintentos ni tiempos de traslado",
                         "La prioridad puede postergar solicitudes normales"],
    }
    (RESULTADOS / "evidencia_validacion.json").write_text(
        json.dumps(expediente, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Factor calibrado: {factor:.4f}")
    print("Referencia sintética: la validación con datos reales queda pendiente.")
    print(f"Trazas y evidencia guardadas en: {RESULTADOS}")
    if (not all(pruebas.values()) or errores
            or not all(f["cumple_tolerancia"] for f in resumen if f["etapa"] == "despues")):
        raise SystemExit("Falló una comprobación; revisar la evidencia guardada")


if __name__ == "__main__":
    main()
