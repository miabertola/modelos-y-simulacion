"""Práctica 12 · Predicción de demanda. Ejecutable con Python 3 estándar."""

import csv
import json
import math
from pathlib import Path
import random
import statistics


CANTIDAD = 100
CORTE = 80
SEMILLA = 2026
CANTIDAD_SEMILLAS = 100
DIRECTORIO = Path(__file__).resolve().parent / "resultados"


def serie_demanda(n=100, semilla=2026):
    """Misma fórmula del manual; ruido normal con el generador de Python.

    Reproducible localmente, pero no idéntico al generador JavaScript del HTML.
    Las unidades de tiempo y demanda son abstractas.
    """
    rng = random.Random(semilla)
    return [100 + 4 * t + 25 * math.sin(t / 3) + rng.gauss(0, 8)
            for t in range(n)]


def regresion_lineal(x, y):
    """Devuelve intercepto y pendiente por mínimos cuadrados ordinarios."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Se requieren al menos dos pares de observaciones.")
    media_x = sum(x) / len(x)
    media_y = sum(y) / len(y)
    denominador = sum((t - media_x) ** 2 for t in x)
    if denominador == 0:
        raise ValueError("Los tiempos deben tener variación.")
    pendiente = sum((t - media_x) * (valor - media_y)
                    for t, valor in zip(x, y)) / denominador
    return media_y - pendiente * media_x, pendiente


def mae(real, predicho):
    """Error absoluto medio; exige una predicción por cada valor real."""
    if not real or len(real) != len(predicho):
        raise ValueError("Las listas deben ser no vacías y del mismo tamaño.")
    return sum(abs(r - p) for r, p in zip(real, predicho)) / len(real)


def evaluar(serie, corte=CORTE):
    """Ajusta solo con el pasado y evalúa un horizonte fijo sin actualizarse."""
    if not 2 <= corte < len(serie):
        raise ValueError("El corte debe dejar al menos dos datos de train y uno de test.")
    train = serie[:corte]
    test = serie[corte:]

    # TODO 1 resuelto: mantener el último valor del train durante todo el test.
    baseline = [train[-1]] * len(test)

    # TODO 2 resuelto: ajustar usando exclusivamente los primeros 80 instantes.
    intercepto, pendiente = regresion_lineal(list(range(corte)), train)

    # TODO 3 resuelto: extrapolar a los instantes 80 ... 99.
    predicciones = [intercepto + pendiente * t for t in range(corte, len(serie))]

    # TODO 4 resuelto: comparar ambos métodos sobre el mismo conjunto de prueba.
    resumen = {
        "cantidad_train": len(train),
        "cantidad_test": len(test),
        "intercepto": intercepto,
        "pendiente": pendiente,
        "ultimo_valor_train": train[-1],
        "mae_baseline": mae(test, baseline),
        "mae_regresion": mae(test, predicciones),
    }
    filas = []
    for t, real, base, pred in zip(range(corte, len(serie)), test, baseline, predicciones):
        filas.append([t, real, base, pred, real - base, real - pred,
                      abs(real - base), abs(real - pred)])
    return resumen, filas


def guardar_csv(ruta, columnas, filas):
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(columnas)
        writer.writerows(filas)


def comparar_semillas():
    """Compara métodos emparejados: misma serie y corte en cada réplica."""
    filas = []
    for semilla in range(SEMILLA, SEMILLA + CANTIDAD_SEMILLAS):
        resultado, _ = evaluar(serie_demanda(CANTIDAD, semilla), CORTE)
        base = resultado["mae_baseline"]
        regresion = resultado["mae_regresion"]
        filas.append([semilla, base, regresion, base - regresion])
    resumen = {"cantidad_semillas": CANTIDAD_SEMILLAS,
               "semilla_inicial": SEMILLA,
               "semilla_final": SEMILLA + CANTIDAD_SEMILLAS - 1}
    for nombre, columna in [("baseline", 1), ("regresion", 2)]:
        errores = [fila[columna] for fila in filas]
        resumen[nombre] = {
            "mae_promedio": statistics.mean(errores),
            "desvio_mae": statistics.stdev(errores) if len(errores) > 1 else 0.0,
            "mae_minimo": min(errores),
            "mae_maximo": max(errores),
        }
    resumen["victorias_regresion"] = sum(f[2] < f[1] for f in filas)
    resumen["victorias_baseline"] = sum(f[1] < f[2] for f in filas)
    resumen["empates"] = sum(f[1] == f[2] for f in filas)
    base_promedio = resumen["baseline"]["mae_promedio"]
    resumen["reduccion_mae_promedio_porcentaje"] = (
        100 * (1 - resumen["regresion"]["mae_promedio"] / base_promedio)
        if base_promedio else None
    )
    return resumen, filas


def main():
    if CANTIDAD_SEMILLAS < 1:
        raise ValueError("Debe utilizarse al menos una semilla.")
    serie = serie_demanda(CANTIDAD, SEMILLA)
    resumen, filas = evaluar(serie, CORTE)
    DIRECTORIO.mkdir(parents=True, exist_ok=True)
    guardar_csv(DIRECTORIO / "serie_demanda.csv", ["t", "demanda", "particion"],
                [[t, valor, "train" if t < CORTE else "test"]
                 for t, valor in enumerate(serie)])
    guardar_csv(DIRECTORIO / "predicciones.csv",
                ["t", "real", "baseline", "regresion", "error_baseline",
                 "error_regresion", "error_absoluto_baseline", "error_absoluto_regresion"],
                filas)

    # Desafío adicional: un salto permanente de demanda desde el inicio del test.
    # Representa un cambio de régimen no observado durante el entrenamiento.
    salto = 150
    serie_desafio = [valor + (salto if t >= CORTE else 0)
                     for t, valor in enumerate(serie)]
    desafio, filas_desafio = evaluar(serie_desafio, CORTE)
    guardar_csv(DIRECTORIO / "predicciones_cambio_regimen.csv",
                ["t", "real", "baseline", "regresion", "error_baseline",
                 "error_regresion", "error_absoluto_baseline", "error_absoluto_regresion"],
                filas_desafio)
    comparacion, filas_semillas = comparar_semillas()
    guardar_csv(DIRECTORIO / "comparacion_100_semillas.csv",
                ["semilla", "mae_baseline", "mae_regresion", "reduccion_mae"],
                filas_semillas)
    evidencia = {"semilla": SEMILLA, "base": resumen,
                 "cambio_regimen": {"salto": salto, **desafio},
                 "comparacion_semillas": comparacion}
    with (DIRECTORIO / "resumen.json").open("w", encoding="utf-8") as archivo:
        json.dump(evidencia, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")

    print("Práctica 12 · Predicción de demanda")
    print(f"Entrenamiento: {CORTE} datos (0 a {CORTE - 1})")
    print(f"Prueba: {len(serie) - CORTE} datos ({CORTE} a {len(serie) - 1})")
    print(f"Recta: demanda = {resumen['intercepto']:.4f} + {resumen['pendiente']:.4f} * t")
    print(f"Baseline constante: {resumen['ultimo_valor_train']:.4f}")
    for nombre, resultado in [("Base", resumen), ("Cambio de régimen", desafio)]:
        print(f"\n{nombre}: MAE baseline = {resultado['mae_baseline']:.4f}; "
              f"MAE regresión = {resultado['mae_regresion']:.4f}")
    print("\nEl menor MAE identifica el mejor método en este horizonte sintético.")
    print("Ante cambios de régimen conviene monitorear errores y revisar el modelo.")
    print(f"\nComparación con {CANTIDAD_SEMILLAS} semillas "
          f"({SEMILLA} a {SEMILLA + CANTIDAD_SEMILLAS - 1}):")
    for nombre in ["baseline", "regresion"]:
        valores = comparacion[nombre]
        print(f"{nombre}: MAE promedio = {valores['mae_promedio']:.4f}; "
              f"desvío = {valores['desvio_mae']:.4f}; "
              f"mínimo = {valores['mae_minimo']:.4f}; máximo = {valores['mae_maximo']:.4f}")
    print(f"Victorias regresión: {comparacion['victorias_regresion']}; "
          f"baseline: {comparacion['victorias_baseline']}; empates: {comparacion['empates']}")
    reduccion = comparacion["reduccion_mae_promedio_porcentaje"]
    if reduccion is not None:
        print(f"Reducción del MAE promedio: {reduccion:.2f}%")
    print("Las semillas cambian el ruido; no cambian el patrón de demanda ni el horizonte.")
    print(f"Resultados guardados en: {DIRECTORIO}")


if __name__ == "__main__":
    main()
