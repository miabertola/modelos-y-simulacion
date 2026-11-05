"""Auditoría independiente de forward, backpropagation y separación de datos."""

import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import practica_13_red_neuronal as red


def perdida_independiente(xs, ys, pesos):
    """No utiliza ni predecir, ni sigmoid, ni perdida_gradiente del programa."""
    a, c, b = pesos
    return sum((c / (1 + math.exp(-(a * x + b))) - y) ** 2
               for x, y in zip(xs, ys)) / (2 * len(xs))


def gradiente_numerico(xs, ys, pesos):
    paso = 1e-5
    resultado = []
    for j in range(3):
        mas, menos = list(pesos), list(pesos)
        mas[j] += paso
        menos[j] -= paso
        resultado.append((perdida_independiente(xs, ys, mas)
                          - perdida_independiente(xs, ys, menos)) / (2 * paso))
    return resultado


class AuditoriaRed(unittest.TestCase):
    def test_forward_y_datos_del_manual(self):
        xs = red.datos_red_x()
        self.assertEqual(xs, [i / 100 for i in range(100)])
        self.assertEqual(red.datos_red_y(xs),
                         [0.2 + 0.6 * x + 0.15 * math.sin(8 * x) for x in xs])
        esperado = -0.2 / (1 + math.exp(-0.05))
        self.assertAlmostEqual(red.predecir([0.5], red.INICIALES)[0], esperado, places=14)

    def test_gradientes_en_distintos_pesos(self):
        xs = [0, 0.1, 0.4, 0.79]
        ys = [0.2, 0.37, 0.43, 0.68]
        for pesos in [red.INICIALES, (1.1, 0.8, -0.25), (-2, 1.4, 0.8), (0, 0, 0)]:
            with self.subTest(pesos=pesos):
                loss, gradiente = red.perdida_gradiente(xs, ys, pesos)
                self.assertAlmostEqual(loss, perdida_independiente(xs, ys, pesos), places=13)
                for analitico, numerico in zip(gradiente, gradiente_numerico(xs, ys, pesos)):
                    self.assertAlmostEqual(analitico, numerico, delta=1e-9)

    def test_entrenamiento_con_gradiente_numerico_independiente(self):
        xs = [i / 100 for i in range(80)]
        ys = [0.2 + 0.6 * x + 0.15 * math.sin(8 * x) for x in xs]
        pesos = red.INICIALES
        for _ in range(2000):
            gradiente = gradiente_numerico(xs, ys, pesos)
            pesos = tuple(w - 0.1 * g for w, g in zip(pesos, gradiente))
        actual, _ = red.entrenar(xs, ys, epocas=2000)
        for a, b in zip(actual, pesos):
            self.assertAlmostEqual(a, b, delta=1e-8)

    def test_evaluacion_no_entrena_con_test(self):
        # Se prueba la función completa que realiza el corte, no solo entrenar().
        generador = red.datos_red_y

        def test_alterado(xs, oscilacion=True):
            ys = generador(xs, oscilacion)
            return ys[:red.CORTE] + [999.0] * (len(ys) - red.CORTE)

        with tempfile.TemporaryDirectory() as carpeta, patch.object(red, "SALIDA", Path(carpeta)):
            base = red.evaluar("original")
            with patch.object(red, "datos_red_y", test_alterado):
                alterado = red.evaluar("alterado")
        self.assertEqual(base["pesos_finales"], alterado["pesos_finales"])
        self.assertEqual(base["regresion"], alterado["regresion"])
        self.assertEqual(base["baseline"], alterado["baseline"])
        self.assertNotEqual(base["metricas"]["red"]["mae_test"],
                            alterado["metricas"]["red"]["mae_test"])

    def test_metricas_con_caso_manual(self):
        self.assertEqual(red.mae([1, 3, 5], [2, 1, 5]), 1)
        self.assertAlmostEqual(red.mse([1, 3, 5], [2, 1, 5]), 5 / 3)


if __name__ == "__main__":
    unittest.main()
