# Práctica 13 · Red neuronal aplicada

Desde la raíz del repositorio:

```bash
python3 "Práctica 13/practica_13_red_neuronal.py"
python3 -m unittest discover -s "Práctica 13" -p "test_*.py" -v
```

Requiere únicamente Python 3 estándar. Regenera los resultados y ejecuta tres
comprobaciones: gradientes por diferencias finitas, predicción inicial manual
y entrenamiento independiente de las respuestas del test.
La suite adicional contrasta el entrenamiento completo con un optimizador de
gradiente numérico independiente durante 2000 épocas, verifica distintos pesos,
las métricas con un caso manual y la separación de datos a través de `evaluar()`.

## Datos y preprocesamiento

Se reproducen las funciones del HTML del manual:

```text
x[i] = i / 100, i = 0 … 99
y = 0.2 + 0.6*x + 0.15*sin(8*x)
```

Son datos sintéticos determinísticos, sin ruido ni semilla aleatoria. Las primeras
80 muestras (x=0 … 0.79) forman train; las últimas 20 (x=0.80 … 0.99) forman test.
El orden se conserva. Esto evalúa extrapolación fuera del intervalo observado.
El manual usa la expresión «normalizado», pero no especifica una transformación
desde demanda física. Se conserva su escala pequeña sin ajustar otro escalador.
No se pueden interpretar los errores como cantidades de solicitudes reales.

## Modelo y entrenamiento

Se conserva la arquitectura inicial, sin sesgo de salida:

```text
h = sigmoid(w1*x + b)
predicción = w2*h
```

Los pesos iniciales son w1=0.1, w2=-0.2, b=0 y la tasa de aprendizaje es 0.1.
Se realizan 10 000 épocas con gradiente de lote completo, minimizando MSE/2.
Para cada muestra, e=predicción-y y los gradientes son:

```text
dL/dw2 = e*h
dL/dw1 = e*w2*h*(1-h)*x
dL/db  = e*w2*h*(1-h)
```

Se promedian sobre train y se actualizan simultáneamente los tres parámetros.
La sigmoide usa una evaluación numéricamente estable sin recorte; el HTML recorta
su argumento a [-30,30]. En esta corrida los argumentos están dentro de ese rango.

Se guardan mediciones cada 100 épocas, incluida la época 0. El MSE de test se
calcula para diagnóstico con copias de los pesos; no participa en las actualizaciones
ni en una selección automática de época. No se realizó búsqueda de hiperparámetros:
10 000 épocas es el presupuesto de demostración, sin garantía de óptimo o convergencia.
Si se ajustaran decisiones tras estudiar estos resultados, sería necesario un
conjunto de validación separado y una nueva evaluación independiente.

## Comparaciones

Todos los modelos usan los mismos datos y el mismo corte:

- Baseline: último y de train, constante durante todo el test.
- Regresión lineal: mínimos cuadrados, ajustada exclusivamente con train.
- Red mínima: tres parámetros, entrenada exclusivamente con train.

Se informa MAE y MSE por partición. El error del baseline sobre train es descriptivo:
la constante usa el último valor de ese tramo y no representa pronósticos históricos.
El MAE de test es el criterio principal de comparación entre modelos.

## Evidencia

En `resultados/` se guardan:

- `base_predicciones.csv`: datos, partición, predicciones y error absoluto de la red.
- `base_aprendizaje.csv`: épocas, pesos y MSE por partición.
- `base_predicciones.svg` y `base_aprendizaje.svg`: gráficos para abrir en navegador.
- Los mismos cuatro archivos con prefijo `sin_oscilacion` para el desafío.
- `resumen.json`: configuración, parámetros, métricas y verificaciones.

El desafío elimina el componente periódico: y=0.2+0.6*x. Cambia la estructura de
la relación, conservando entradas, partición, arquitectura e hiperparámetros;
cada modelo se vuelve a entrenar desde el inicio. No representa un cambio que
aparece sorpresivamente durante test. El análisis está en `ANALISIS.md`.
