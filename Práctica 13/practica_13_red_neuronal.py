"""Práctica 13: red mínima del manual. Python 3, sin dependencias externas."""

import csv
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape


CANTIDAD = 100
CORTE = 80
EPOCAS = 10_000
LR = 0.1
INICIALES = (0.1, -0.2, 0.0)  # w1, w2, b del manual
SALIDA = Path(__file__).resolve().parent / "resultados"


def datos_red_x(n=100):
    """Se conserva i/100 del HTML, incluso si se modifica n."""
    return [i / 100 for i in range(n)]


def datos_red_y(xs, oscilacion=True):
    return [0.2 + 0.6 * x + (0.15 * math.sin(8 * x) if oscilacion else 0)
            for x in xs]


def sigmoid(z):
    # Forma estable sin recortar la función: conserva su derivada matemática.
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1 + ez)


def predecir(xs, pesos):
    w1, w2, b = pesos
    return [w2 * sigmoid(w1 * x + b) for x in xs]


def mae(real, pred):
    return sum(abs(y - p) for y, p in zip(real, pred)) / len(real)


def mse(real, pred):
    return sum((y - p) ** 2 for y, p in zip(real, pred)) / len(real)


def perdida_gradiente(xs, ys, pesos):
    """Pérdida = MSE/2; gradientes promedio, evaluados con los mismos pesos."""
    w1, w2, b = pesos
    perdida = dw1 = dw2 = db = 0.0
    for x, y in zip(xs, ys):
        h = sigmoid(w1 * x + b)
        error = w2 * h - y
        delta = error * w2 * h * (1 - h)
        perdida += error ** 2 / 2
        dw1 += delta * x
        dw2 += error * h
        db += delta
    n = len(xs)
    return perdida / n, (dw1 / n, dw2 / n, db / n)


def entrenar(xs, ys, epocas=EPOCAS, lr=LR):
    """Solo recibe train. Descenso por gradiente de lote completo, sin azar."""
    pesos = INICIALES
    historia = []
    for epoca in range(epocas + 1):
        perdida, gradiente = perdida_gradiente(xs, ys, pesos)
        if epoca % 100 == 0 or epoca == epocas:
            historia.append((epoca, pesos, 2 * perdida))
        if epoca < epocas:
            pesos = tuple(w - lr * g for w, g in zip(pesos, gradiente))
    return pesos, historia


def regresion_lineal(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    pendiente = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum(
        (x - mx) ** 2 for x in xs)
    return my - pendiente * mx, pendiente


def guardar_csv(nombre, columnas, filas):
    with (SALIDA / nombre).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columnas)
        writer.writerows(filas)


def grafico(nombre, titulo, xs, series, eje_x, eje_y, corte=None, log=False):
    """SVG autónomo para abrir en navegador; coordenadas a partir de los datos."""
    ancho, alto = 960, 510
    izquierda, derecha, arriba, abajo = 85, 30, 90, 65
    tx = lambda v: v
    ty = math.log10 if log else lambda v: v
    xmin, xmax = min(xs), max(xs)
    valores = [ty(v) for _, ys, _, _ in series for v in ys]
    ymin, ymax = min(valores), max(valores)
    margen = (ymax - ymin) * 0.08 or 0.1
    ymin, ymax = ymin - margen, ymax + margen
    px = lambda x: izquierda + (tx(x) - xmin) / (xmax - xmin) * (ancho - izquierda - derecha)
    py = lambda y: alto - abajo - (ty(y) - ymin) / (ymax - ymin) * (alto - arriba - abajo)
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" role="img">',
              f'<title>{escape(titulo)}</title>',
              '<rect width="100%" height="100%" fill="white"/>',
              '<g font-family="sans-serif" font-size="14" fill="#222">',
              f'<text x="{izquierda}" y="28" font-size="20">{escape(titulo)}</text>']
    if corte is not None:
        x = px(corte)
        partes += [f'<rect x="{x}" y="{arriba}" width="{ancho-derecha-x}" height="{alto-arriba-abajo}" fill="#edf2f7"/>',
                   f'<text x="{x+8}" y="{arriba+20}">Prueba</text>']
    for i in range(6):
        xv = xmin + (xmax - xmin) * i / 5
        yv = ymin + (ymax - ymin) * i / 5
        yoriginal = 10 ** yv if log else yv
        y = py(yoriginal)
        partes += [f'<path d="M {izquierda} {y} H {ancho-derecha}" stroke="#ddd"/>',
                   f'<text x="{izquierda-10}" y="{y+5}" text-anchor="end">{yoriginal:.3g}</text>',
                   f'<text x="{px(xv)}" y="{alto-abajo+25}" text-anchor="middle">{xv:.3g}</text>']
    for i, (etiqueta, ys, color, dash) in enumerate(series):
        puntos = " ".join(f'{px(x):.2f},{py(y):.2f}' for x, y in zip(xs, ys))
        estilo = f' stroke-dasharray="{dash}"' if dash else ''
        partes += [f'<polyline points="{puntos}" fill="none" stroke="{color}" stroke-width="2.5"{estilo}/>',
                   f'<path d="M {izquierda+i*210} 56 h 25" stroke="{color}" stroke-width="3"{estilo}/>',
                   f'<text x="{izquierda+i*210+32}" y="61">{escape(etiqueta)}</text>']
    partes += [f'<text x="{ancho/2}" y="{alto-12}" text-anchor="middle">{escape(eje_x)}</text>',
               f'<text transform="translate(22 {alto/2}) rotate(-90)" text-anchor="middle">{escape(eje_y)}</text>',
               '</g></svg>']
    (SALIDA / nombre).write_text("\n".join(partes) + "\n", encoding="utf-8")


def evaluar(nombre, oscilacion=True):
    xs = datos_red_x(CANTIDAD)
    ys = datos_red_y(xs, oscilacion)
    # Preprocesamiento: datos ya en escala pequeña, sin transformación ajustada.
    # TODO 1 y 2: forward y descenso por gradiente sobre las primeras 80 muestras.
    pesos, historia = entrenar(xs[:CORTE], ys[:CORTE])
    intercepto, pendiente = regresion_lineal(xs[:CORTE], ys[:CORTE])
    # TODO 3 y 4: predicciones reservadas y comparación sobre las mismas muestras.
    predicciones = {
        "baseline": [ys[CORTE - 1]] * len(xs),
        "regresion": [intercepto + pendiente * x for x in xs],
        "red": predecir(xs, pesos),
    }
    metricas = {}
    for modelo, pred in predicciones.items():
        metricas[modelo] = {
            "mae_train": mae(ys[:CORTE], pred[:CORTE]),
            "mae_test": mae(ys[CORTE:], pred[CORTE:]),
            "mse_train": mse(ys[:CORTE], pred[:CORTE]),
            "mse_test": mse(ys[CORTE:], pred[CORTE:]),
        }
    filas_curva = [(e, *w, train_mse, mse(ys[CORTE:], predecir(xs[CORTE:], w)))
                   for e, w, train_mse in historia]
    guardar_csv(f"{nombre}_aprendizaje.csv", ["epoca", "w1", "w2", "b", "mse_train", "mse_test"], filas_curva)
    guardar_csv(f"{nombre}_predicciones.csv",
                ["x", "real", "particion", "baseline", "regresion", "red", "error_absoluto_red"],
                [[x, y, "train" if i < CORTE else "test",
                  *(predicciones[m][i] for m in ("baseline", "regresion", "red")),
                  abs(y - predicciones["red"][i])]
                 for i, (x, y) in enumerate(zip(xs, ys))])
    grafico(f"{nombre}_predicciones.svg", f"{nombre}: valores y predicciones", xs,
            [("Real", ys, "#222222", ""),
             ("Red", predicciones["red"], "#b45309", ""),
             ("Regresión", predicciones["regresion"], "#2563eb", "7 4"),
             ("Baseline", predicciones["baseline"], "#15803d", "2 5")],
            "x (escala del manual)", "y (unidades normalizadas)", corte=xs[CORTE])
    grafico(f"{nombre}_aprendizaje.svg", f"{nombre}: curva de aprendizaje", [r[0] for r in filas_curva],
            [("Train", [r[4] for r in filas_curva], "#2563eb", ""),
             ("Test (diagnóstico)", [r[5] for r in filas_curva], "#b45309", "7 4")],
            "Época", "MSE (escala logarítmica)", log=True)
    return {"pesos_finales": dict(zip(("w1", "w2", "b"), pesos)),
            "regresion": {"intercepto": intercepto, "pendiente": pendiente},
            "baseline": ys[CORTE - 1], "metricas": metricas,
            "mse_train_inicial": historia[0][2]}


def verificar():
    """Comprobaciones del cálculo y de la separación del entrenamiento."""
    xs, ys, pesos = [0.1, 0.4, 0.7], [0.3, 0.5, 0.6], (0.3, -0.4, 0.2)
    _, gradiente = perdida_gradiente(xs, ys, pesos)
    eps = 1e-6
    for j, g in enumerate(gradiente):
        mas, menos = list(pesos), list(pesos)
        mas[j] += eps
        menos[j] -= eps
        numerico = (perdida_gradiente(xs, ys, mas)[0] - perdida_gradiente(xs, ys, menos)[0]) / (2 * eps)
        if not math.isclose(g, numerico, rel_tol=1e-6, abs_tol=1e-9):
            raise AssertionError("Gradiente incompatible con diferencias finitas")
    if predecir([0], INICIALES) != [-0.1]:
        raise AssertionError("Falló la predicción manual para x=0")
    entradas = datos_red_x()
    salidas = datos_red_y(entradas)
    a, _ = entrenar(entradas[:CORTE], salidas[:CORTE], epocas=20)
    salidas[CORTE:] = [999] * (len(salidas) - CORTE)
    b, _ = entrenar(entradas[:CORTE], salidas[:CORTE], epocas=20)
    if a != b:
        raise AssertionError("El entrenamiento depende del test")
    return ["Gradientes contrastados por diferencias finitas",
            "Predicción inicial contrastada con cálculo manual",
            "Cambiar las respuestas del test no modifica el entrenamiento"]


def main():
    verificaciones = verificar()
    SALIDA.mkdir(parents=True, exist_ok=True)
    evidencia = {"configuracion": {"cantidad": CANTIDAD, "corte": CORTE,
                  "epocas": EPOCAS, "lr": LR, "pesos_iniciales": INICIALES,
                  "optimizador": "gradiente de lote completo sobre MSE/2"},
                 "verificaciones": verificaciones,
                 "base": evaluar("base"),
                 "desafio_sin_oscilacion": evaluar("sin_oscilacion", False)}
    (SALIDA / "resumen.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Práctica 13 · Red neuronal aplicada")
    print(f"Train: {CORTE}; test: {CANTIDAD-CORTE}; épocas: {EPOCAS}; lr: {LR}")
    for escenario in ("base", "desafio_sin_oscilacion"):
        print(f"\n{escenario}")
        for modelo, metricas in evidencia[escenario]["metricas"].items():
            print(f"  {modelo:10s} MAE train={metricas['mae_train']:.6f} MAE test={metricas['mae_test']:.6f}")
    print(f"\nVerificaciones: {len(verificaciones)} correctas. Resultados: {SALIDA}")


if __name__ == "__main__":
    main()
