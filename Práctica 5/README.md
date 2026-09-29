# Práctica 5 · Colas, capacidad y rendimiento

Este directorio contiene el código, los resultados y el informe de la Práctica 5.

## Estructura

- `practica_05_colas_rendimiento.py`: simulación y comparación de configuraciones.
- `resultados/`: tablas y salidas de las ejecuciones.
- `informe/`: informe breve de la práctica.

## Ejecución

Se requiere Python 3. Ejecutar desde esta carpeta:

```bash
python3 practica_05_colas_rendimiento.py
```

El programa genera `resultados/tabla_comparativa.csv` con las métricas de las
configuraciones de 1, 2 y 4 servidores. La semilla fija (`2026`) asegura que
las tres configuraciones usen exactamente las mismas llegadas y servicios.
