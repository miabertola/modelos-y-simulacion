"""Pruebas reproducibles: python3 -m unittest discover -s 'Práctica 11' -v."""

import copy
import random
import unittest

from practica_11_validacion import (
    CASO_MANUAL, calibrar_factor, cargar_referencia, comprobar_invariantes,
    evaluar_referencia, simular_cola,
)


def solicitud(identificador, llegada, servicio, prioridad="normal"):
    return {"id": identificador, "llegada": llegada, "servicio": servicio,
            "prioridad": prioridad}


class PruebasCola(unittest.TestCase):
    def test_todo_1_primera_finalizacion(self):
        self.assertEqual(simular_cola(CASO_MANUAL)["eventos"][0]["fin"], 2)

    def test_todo_2_segunda_espera(self):
        self.assertEqual(simular_cola(CASO_MANUAL)["eventos"][1]["espera"], 1)

    def test_todo_3_orden_temporal(self):
        for e in simular_cola(CASO_MANUAL)["eventos"]:
            self.assertGreaterEqual(e["fin"], e["inicio"])
            self.assertGreaterEqual(e["inicio"], e["llegada"])

    def test_traza_manual_completa_y_metricas(self):
        r = simular_cola(CASO_MANUAL)
        self.assertEqual([(e["inicio"], e["fin"], e["espera"]) for e in r["eventos"]],
                         [(0, 2, 0), (2, 4, 1)])
        self.assertEqual(r["latencias"], [2, 3])
        self.assertEqual(r["promedio"], 2.5)
        self.assertAlmostEqual(r["p95"], 2.95)
        self.assertAlmostEqual(r["p99"], 2.99)
        self.assertEqual(r["throughput"], 0.5)
        self.assertEqual(r["utilizacion"], 1)

    def test_referencia_practica_4(self):
        datos = [solicitud(1, 0, 3), solicitud(2, 1, 2), solicitud(3, 2, 1)]
        r = simular_cola(datos)
        self.assertEqual([e["fin"] for e in r["eventos"]], [3, 5, 6])
        self.assertEqual(r["esperas"], [0, 2, 3])

    def test_sistema_vacio(self):
        r = simular_cola([])
        self.assertEqual(r["eventos"], [])
        for campo in ("promedio", "p95", "p99", "throughput", "utilizacion"):
            self.assertEqual(r[campo], 0)

    def test_servidor_ocioso_y_horizonte_desde_cero(self):
        r = simular_cola([solicitud(1, 5, 2), solicitud(2, 10, 1)])
        self.assertEqual(r["esperas"], [0, 0])
        self.assertEqual(r["horizonte"], 11)
        self.assertAlmostEqual(r["utilizacion"], 3 / 11)

    def test_finalizacion_y_llegada_simultaneas(self):
        r = simular_cola([solicitud(1, 0, 2), solicitud(2, 2, 1)])
        self.assertEqual(r["esperas"], [0, 0])

    def test_llegadas_simultaneas_conservan_orden_fifo(self):
        r = simular_cola([solicitud(9, 0, 2), solicitud(3, 0, 1), solicitud(1, 0, 3)])
        self.assertEqual([e["id"] for e in r["eventos"]], [9, 3, 1])
        self.assertEqual(r["esperas"], [0, 2, 3])

    def test_entrada_desordenada(self):
        r = simular_cola([CASO_MANUAL[1], CASO_MANUAL[0]])
        self.assertEqual([e["id"] for e in r["eventos"]], [1, 2])
        self.assertEqual(r["esperas"], [0, 1])

    def test_dos_servidores_traza_manual(self):
        datos = [solicitud(1, 0, 4), solicitud(2, 0, 2), solicitud(3, 1, 1)]
        r = simular_cola(datos, 2)
        self.assertEqual([(e["servidor"], e["inicio"], e["fin"]) for e in r["eventos"]],
                         [(1, 0, 4), (2, 0, 2), (2, 2, 3)])
        self.assertAlmostEqual(r["utilizacion"], 7 / 8)

    def test_capacidad_suficiente_sin_espera(self):
        datos = [solicitud(i, 0, i + 1) for i in range(5)]
        self.assertEqual(simular_cola(datos, 5)["esperas"], [0] * 5)

    def test_no_modifica_entrada(self):
        datos = copy.deepcopy(CASO_MANUAL)
        simular_cola(datos)
        self.assertEqual(datos, CASO_MANUAL)

    def test_prioridad_no_interrumpe_atencion(self):
        datos = [solicitud(1, 0, 4), solicitud(2, 1, 3), solicitud(3, 2, 1, "alta")]
        fifo = simular_cola(datos)
        prioridad = simular_cola(datos, regla="prioridad")
        self.assertEqual([e["id"] for e in fifo["eventos"]], [1, 2, 3])
        self.assertEqual([e["id"] for e in prioridad["eventos"]], [1, 3, 2])
        self.assertEqual([e["inicio"] for e in prioridad["eventos"]], [0, 4, 5])
        self.assertEqual([e["fin"] for e in prioridad["eventos"]], [4, 5, 8])

    def test_prioridad_empates_y_llegada_al_finalizar(self):
        datos = [solicitud(1, 0, 2), solicitud(2, 1, 1),
                 solicitud(3, 2, 1, "alta"), solicitud(4, 2, 1, "alta")]
        r = simular_cola(datos, regla="prioridad")
        self.assertEqual([e["id"] for e in r["eventos"]], [1, 3, 4, 2])

    def test_sistema_dd1_con_solucion_analitica(self):
        # Llegadas cada a unidades, servicio b > a: W_i = i * (b - a).
        for a, b in ((1, 2), (2, 5), (0.5, 0.75)):
            datos = [solicitud(i, i * a, b) for i in range(100)]
            r = simular_cola(datos)
            self.assertEqual(r["esperas"], [i * (b - a) for i in range(100)])

    def test_invariantes_en_escenarios_reproducibles(self):
        for semilla in range(10):
            rng = random.Random(semilla)
            datos = [solicitud(i, rng.randint(0, 30), rng.uniform(0.1, 8),
                               rng.choice(["normal", "alta"])) for i in range(100)]
            for servidores in (1, 2, 4):
                for regla in ("fifo", "prioridad"):
                    with self.subTest(semilla=semilla, servidores=servidores, regla=regla):
                        r = simular_cola(datos, servidores, regla)
                        self.assertEqual(comprobar_invariantes(datos, r, servidores), [])

    def test_detector_rechaza_traza_corrupta(self):
        for campo, valor in (("inicio", -1), ("fin", 1), ("espera", 9), ("servidor", 2)):
            with self.subTest(campo=campo):
                r = simular_cola(CASO_MANUAL)
                r["eventos"][0][campo] = valor
                self.assertTrue(comprobar_invariantes(CASO_MANUAL, r, 1))
        r = simular_cola(CASO_MANUAL)
        r["eventos"].pop()
        self.assertTrue(comprobar_invariantes(CASO_MANUAL, r, 1))

    def test_detector_rechaza_superposicion_temporalmente_coherente(self):
        r = simular_cola(CASO_MANUAL)
        r["eventos"][1].update(inicio=1, fin=3, espera=0)
        self.assertIn("Servidor 1: atenciones superpuestas",
                      comprobar_invariantes(CASO_MANUAL, r, 1))

    def test_servidores_y_regla_invalidos(self):
        for servidores in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                simular_cola([], servidores)
        with self.assertRaises(ValueError):
            simular_cola([], regla="desconocida")

    def test_datos_invalidos(self):
        for campo, valores in (("llegada", [-1, float("nan"), float("inf"), True, "0"]),
                               ("servicio", [0, -1, float("nan"), float("inf"), True])):
            for valor in valores:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    d = solicitud(1, 0, 1)
                    d[campo] = valor
                    simular_cola([d])
        with self.assertRaises(ValueError):
            simular_cola([solicitud(1, 0, 1), solicitud(1, 2, 1)])
        with self.assertRaises(ValueError):
            simular_cola([solicitud(1, 0, 1, "desconocida")])


class PruebasReferencia(unittest.TestCase):
    def test_calibracion_con_factor_conocido(self):
        self.assertAlmostEqual(calibrar_factor(cargar_referencia()), 1.25)

    def test_validacion_independiente_antes_y_despues(self):
        referencias = cargar_referencia()
        _, error_antes, _ = evaluar_referencia(referencias, "validacion", 1)
        filas, error_despues, errores = evaluar_referencia(
            referencias, "validacion", calibrar_factor(referencias))
        self.assertGreater(error_antes, 0)
        self.assertEqual(error_despues, 0)
        self.assertTrue(all(f["error_inicio"] == 0 for f in filas))
        self.assertEqual(errores, [])

    def test_datos_validacion_no_influyen_en_ajuste(self):
        referencias = cargar_referencia()
        factor = calibrar_factor(referencias)
        for fila in referencias:
            if fila["conjunto"] == "validacion":
                fila["fin_referencia"] += 100
        self.assertEqual(calibrar_factor(referencias), factor)
        _, error, _ = evaluar_referencia(referencias, "validacion", factor)
        self.assertGreater(error, 0)

    def test_sin_datos_de_ajuste(self):
        with self.assertRaises(ValueError):
            calibrar_factor([])


if __name__ == "__main__":
    unittest.main(verbosity=2)
