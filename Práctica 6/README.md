# Práctica 6 · Latencia, throughput y acuerdos de servicio

El programa evalúa si un sistema con dos servidores cumple un SLA y propone la
capacidad mínima necesaria para cada escenario de carga.

## Requisitos

- Python 3
- No se requieren librerías externas.

## Ejecución

Desde esta carpeta, ejecutar:

```bash
python3 practica_06_sla_metricas.py
```

## Criterio de SLA

- P95 menor a 10 unidades de tiempo.
- Tasa máxima de errores de 1 %.
- Una solicitud se considera errónea cuando su latencia supera 15 unidades de
  tiempo, que representa un timeout del servicio.

## Archivos generados

- `resultados/evaluacion_sla.csv`: métricas y cumplimiento con dos servidores.
- `resultados/comparacion_capacidad.csv`: comparación de 1 a 8 servidores
  para cada escenario, con sus métricas y cumplimiento de SLA.
- `resultados/plan_capacidad.csv`: cantidad mínima de servidores que cumple el
  SLA en cada escenario.
