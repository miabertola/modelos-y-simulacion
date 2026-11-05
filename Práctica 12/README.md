# Práctica 12 · Predicción de demanda

Programa local en Python 3 sin dependencias externas. Desde el repositorio:

```bash
python3 "Práctica 12/practica_12_prediccion.py"
```

Genera 100 observaciones con semilla 2026 mediante
`100 + 4*t + 25*sin(t/3) + ruido normal(0, 8)`. Usa el generador aleatorio de
Python: conserva la fórmula del manual, pero los valores no son idénticos a
los del generador JavaScript integrado en el HTML. No modifica el azar global.

Entrena con los instantes 0 a 79 y evalúa con 80 a 99, sin mezclar datos ni
ajustar parámetros con el test. Compara un baseline constante (último valor del
train) con una regresión lineal por mínimos cuadrados. Ambos pronostican los
20 pasos desde un mismo origen, sin incorporar observaciones nuevas del test.
El MAE expresa el error absoluto promedio en unidades de demanda.

La regresión usa solo el tiempo; no incluye hora, día ni actividad reciente.
Puede captar la tendencia, pero no representa explícitamente las oscilaciones.
Los datos son sintéticos y las unidades abstractas; el resultado no acredita
capacidad de predicción sobre un servicio real.

En `resultados/` se regeneran:

- `serie_demanda.csv`: serie completa y partición temporal.
- `predicciones.csv`: valores reales, pronósticos, errores con signo
  (real menos predicción) y errores absolutos.
- `resumen.json`: configuración, coeficientes y MAE de ambos escenarios.
- `comparacion_100_semillas.csv`: MAE de cada método y diferencia por semilla.
  El nombre se conserva aunque se modifique `CANTIDAD_SEMILLAS`.
- `predicciones_cambio_regimen.csv`: desafío con un salto permanente de 150
  unidades desde t=80, conservando el entrenamiento y el ruido del caso base.

El desafío cambia la estructura de la serie al introducir una discontinuidad.
Ninguno de los modelos dispone de información anticipada sobre ese salto.
La comparación permite estudiar el riesgo de extrapolar una tendencia pasada:
si se detectan cambios de régimen, conviene revisar supuestos y actualizar el
modelo con nuevas observaciones antes de usarlo para decidir capacidad.

## Análisis entre semillas

Cada ejecución también compara 100 semillas (2026 a 2125). Para cada semilla
se genera una nueva serie y se vuelven a entrenar y evaluar ambos métodos con
el mismo corte 80/20. Dentro de cada réplica comparten exactamente los mismos
datos. El experimento usa el escenario base, sin el salto del desafío.
Repetir la semilla 2026 reproduce los mismos datos; cambiarla permite evaluar
cuánto depende la comparación del ruido aleatorio.

Con la configuración original se obtienen:

| Métrica entre réplicas | Baseline | Regresión |
|---|---:|---:|
| MAE promedio | 26,81 | 17,49 |
| Desvío muestral del MAE | 4,26 | 1,67 |
| MAE mínimo | 20,50 | 12,81 |
| MAE máximo | 43,82 | 21,74 |

La regresión obtiene menor MAE en las 100 réplicas. La reducción del MAE
promedio es del 34,77 %, calculada como
`100 * (1 - promedio_MAE_regresion / promedio_MAE_baseline)`; no es el promedio
de los porcentajes individuales. Además, la menor dispersión de sus MAE indica
resultados más estables frente a los distintos ruidos evaluados.

Esta evidencia apoya el uso de la regresión para este generador con tendencia.
Las semillas conservan la tendencia, las oscilaciones y los instantes de corte:
no prueban distintos patrones, horizontes ni datos reales. No se eligió una
semilla ganadora ni se ajustó el modelo con los resultados de prueba.
El resumen numérico actualizado se guarda también en `resumen.json`, bajo
`comparacion_semillas`, y se imprime en consola.

Las constantes al comienzo del programa permiten modificar tamaño, corte,
semilla inicial y cantidad de semillas. La tabla anterior corresponde solo a
la configuración original. El informe de la práctica se redactará por separado a partir de esta
evidencia y de las preguntas de interpretación del manual.
