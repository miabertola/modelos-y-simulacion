# Práctica 11 · Verificación y validación

Implementación local en Python 3, sin dependencias externas. El informe se
redactará por separado; este archivo contiene instrucciones de uso y supuestos.

Desde la carpeta general del repositorio:

```bash
python3 "Práctica 11/practica_11_validacion.py"
python3 -m unittest discover -s "Práctica 11" -p "test_*.py" -v
```

El primer comando ejecuta el caso del manual, la calibración con referencia
sintética y la comparación FIFO/prioridad. Regenera los CSV y el JSON de
`resultados/`. Devuelve un error si falla una comprobación. El segundo comando
ejecuta las pruebas unitarias, referencias manuales, caso analítico D/D/1,
invariantes en escenarios con semillas fijas y detección de trazas corruptas.

## Modelo

- Una cola y servidores idénticos, inicialmente libres en t = 0.
- Llegadas no negativas, servicios positivos y finitos, identificadores únicos.
- FIFO por llegada; los empates respetan el orden original de los registros.
- El calendario libera servidores y registra llegadas antes de asignar atención
  en ese instante. Se elige el servidor libre de menor número.
- La regla alternativa da precedencia a prioridad alta entre quienes esperan.
  No interrumpe servicios en curso. Los empates dentro de cada prioridad son FIFO.
- Sin fallas, pérdidas, abandonos, reintentos ni cambios de capacidad.
- Se termina de atender a todas las solicitudes. No se impone un horizonte de corte.
- Las unidades de tiempo son abstractas. Latencia = fin − llegada; espera =
  inicio − llegada. La utilización y el throughput consideran el intervalo desde
  t = 0 hasta la última finalización, incluidos los períodos ociosos iniciales.
- Para una entrada vacía se devuelven trazas vacías y métricas iguales a cero.

## Referencia y calibración

`datos/referencia_sintetica.csv` contiene dos secuencias distintas, cada una con
su propio origen temporal y un servidor FIFO. Son datos **sintéticos**, calculados
manualmente con servicios iguales a `servicio_base × 1.25`. Las columnas de inicio
y fin son referencias fijas, no salidas generadas por el simulador al ejecutarlo.

El factor se estima sólo a partir de las duraciones observadas del conjunto
`calibracion`: suma de (fin − inicio) dividida por suma de servicio_base. El
conjunto `validacion` queda separado del ajuste. Se comparan inicios y finales
antes y después de calibrar, y se registra el MAE de finalización.

La aceptación exige que cada error absoluto de inicio y fin sea como máximo
1e-9, apropiado para esta referencia sintética exacta. Este umbral no es un
criterio de aceptación para mediciones reales con ruido. El ejemplo demuestra
el procedimiento de calibración y la concordancia con los casos de referencia;
no acredita que el modelo represente una plataforma real. Esa evaluación requiere
registros observados independientes y un margen de error acordado para su uso.

## Archivos generados

- `traza_caso_manual.csv`: atención de las dos solicitudes del manual.
- `comparacion_referencia.csv`: inicios, finales y errores individuales.
- `calibracion.csv`: factor, MAE y aceptación por conjunto y etapa.
- `traza_desafio_fifo.csv` y `traza_desafio_prioridad.csv`: cambio estructural.
- `comparacion_reglas.csv`: latencia, P95 y esperas por prioridad.
- `evidencia_validacion.json`: comprobaciones, criterios y alcance técnico.

El desafío usa exactamente las mismas llegadas, servicios y capacidad para
ambas reglas. Permite observar la reducción de espera de prioridad alta y el
costo para las solicitudes normales. La conveniencia de esa política depende
del objetivo de atención y del riesgo de postergar solicitudes normales; no se
concluye una mejora general a partir de un único escenario pequeño.

Las pruebas automáticas deben ejecutarse además del programa principal. Las
cinco preguntas de interpretación se integrarán en el informe futuro, en prosa.
