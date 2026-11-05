# Análisis de la práctica 13

La red implementada aprende, pero con esta configuración no mejora la predicción
en las 20 muestras reservadas. El baseline tiene el menor MAE de test.

| Modelo | MAE train | MAE test |
|---|---:|---:|
| Último valor observado | 0.242471 | 0.160901 |
| Regresión lineal | 0.060601 | 0.275692 |
| Red mínima | 0.060147 | 0.299004 |

El MAE de la red en test es aproximadamente 86 % mayor que el del baseline.
Estas cifras pertenecen a la escala sintética del manual, no a solicitudes reales.

## Qué aprendió

El MSE de entrenamiento baja de 0.298874 a 0.004832, una reducción aproximada
del 98.4 %. El descenso confirma que el entrenamiento modifica los parámetros
de manera útil para su objetivo. No garantiza buena predicción fuera de train.

Los pesos finales producen la función:

```text
predicción = 0.806018 * sigmoid(1.079474*x - 0.249493)
```

En x=0.40, predice 0.439642 frente a 0.431244 real: representa razonablemente
esa zona. En x=0.99, predice 0.559428 frente a 0.943673 real: subestima el tramo
final. El baseline predice allí 0.679521 y la regresión 0.588989.

## Por qué ocurre

La curva generadora combina una tendencia con una oscilación. En cambio,
w2*sigmoid(w1*x+b) es monótona o constante: su derivada tiene el signo fijo
de w1*w2. Una sola sigmoide no puede representar todos los ascensos y descensos
de la relación del manual. Además, con estos pesos su salida está acotada por
0.806018, mientras el último valor real alcanza 0.943673.

El test contiene valores de x superiores a todos los observados durante train.
Por tanto, la comparación mide extrapolación. La red y la recta ajustan una
relación global al tramo inicial; el último valor de train queda más cerca del
ascenso final en este corte concreto. Su ventaja no demuestra que siempre sea
el mejor predictor.

El MAE de entrenamiento de la red es levemente menor que el de la regresión,
pero su MAE de test es mayor. No alcanza para diagnosticar sobreajuste por sí
solo: también intervienen la capacidad limitada de la arquitectura, el presupuesto
de optimización y el cambio de rango entre train y test.

## Desafío: eliminar la oscilación

Se vuelve a entrenar sobre y=0.2+0.6*x con la misma configuración.

| Modelo | MAE test |
|---|---:|
| Último valor observado | 0.063000 |
| Regresión lineal | 0.000000 |
| Red mínima | 0.015417 |

La red mejora mucho al desaparecer la oscilación y supera al baseline. La
regresión reproduce exactamente la relación lineal sin ruido. El desafío
demuestra que el desempeño depende de la estructura de los datos y que una
arquitectura neuronal no garantiza ventaja sobre un modelo sencillo.

## Interpretación para las prácticas

La decisión apoyada es qué predictor conviene incorporar posteriormente al
modelo de capacidad de la práctica 14. En el caso base, esta red no justifica
su complejidad frente al baseline. En el desafío lineal, conviene la regresión.

Los supuestos decisivos son la forma de la relación, el corte de evaluación y
la arquitectura. Los gradientes se verifican con diferencias finitas, la salida
inicial con un caso manual y la separación de train con una modificación de las
respuestas del test que no altera el entrenamiento.

La expectativa de que una red mejore por ser más compleja no se cumple aquí:
el resultado reservado favorece el método más simple. Las conclusiones se
limitan a estos datos determinísticos, esta partición y esta configuración.
No validan un predictor sobre demanda real ni permiten decidir una cantidad
de servidores sin integrarlo y evaluar sus efectos en el simulador.

Una futura ampliación podría usar varias neuronas ocultas y contrastar distintas
inicializaciones, con selección mediante validación separada. Eso permitiría
investigar la limitación de capacidad sin reutilizar este test para elegir el modelo.

## Auditoría posterior de implementación y presupuesto

Se contrastó la implementación con un entrenamiento independiente que obtiene
los gradientes mediante diferencias finitas, sin usar las funciones de forward
o de gradiente del programa. Tras 2000 épocas, la máxima diferencia entre pesos
es 3.74e-11 aproximadamente. Las pruebas incluyen distintos pesos, un cálculo
manual de forward y métricas y una evaluación completa con respuestas del test
alteradas: cambian sus errores, pero no los parámetros de los modelos.

Además, se extendió el presupuesto de entrenamiento como diagnóstico posterior:

| Épocas | MSE train | MAE test | Norma del gradiente |
|---|---:|---:|---:|
| 10 000 | 0.00483230 | 0.299004 | 0.00038306 |
| 100 000 | 0.00474506 | 0.278376 | 0.00002211 |

Por tanto, 10 000 épocas no deben interpretarse como convergencia demostrada.
Más entrenamiento mejora el resultado, aunque el baseline (MAE 0.160901) conserva
la ventaja en estas corridas. La arquitectura sigue siendo monótona para cualquier
cantidad de épocas. Este diagnóstico no cambia los resultados base ni constituye
una selección de hiperparámetros validada; el test ya ha sido inspeccionado.
