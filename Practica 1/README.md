# Práctica SOG2 - Python y R

En esta versión el proceso quedó separado en dos etapas:

1. **Limpieza de datos**
2. **Análisis de datos**

El análisis ya no limpia el archivo original. Primero se genera un CSV limpio y luego ese archivo se usa para todos los cálculos y gráficas.

## Flujo recomendado

### Python

```bash
cd python
pip install -r requirements.txt

python 01_limpieza_datos.py ../ventas_online_2025.csv
python 02_analisis_datos.py ventas_online_2025_limpio.csv
```

### R

```bash
cd r
Rscript instalar_paquetes.R

Rscript 01_limpieza_datos.R ../ventas_online_2025.csv
Rscript 02_analisis_datos.R ventas_online_2025_limpio.csv
```

## Qué hace la limpieza

- normaliza el encabezado `Boletín` a `Boletin`;
- elimina filas completamente duplicadas;
- limpia `$`, comillas, espacios y coma decimal en montos;
- convierte las fechas a un formato uniforme `YYYY-MM-DD`;
- normaliza `Genero`:
  - 0 / Masculino -> 0
  - 1 / Femenino -> 1
- normaliza `Boletin` y `Vale`:
  - No / 0 -> 0
  - Si / Sí / 1 -> 1
- valida:
  - Edad: 0 a 100
  - MetodoPago: 0, 1 o 2
  - Navegador: 0, 1, 2, 3 o 4
  - Boletin y Vale: 0 o 1
- considera negativos en `Venta_total` y `MontoCompra` como datos inválidos;
- reemplaza valores numéricos inválidos/faltantes con mediana;
- reemplaza valores categóricos inválidos/faltantes con moda;
- crea un reporte de limpieza;
- genera `ventas_online_2025_limpio.csv`.

## Carpetas de salida

El script de análisis genera:

- `salida_python/graficos/` o `salida_r/graficos/`
- `salida_python/tablas/` o `salida_r/tablas/`
- `resumen.txt`

Se generan 9 gráficas para cubrir el requisito mínimo de 7.
