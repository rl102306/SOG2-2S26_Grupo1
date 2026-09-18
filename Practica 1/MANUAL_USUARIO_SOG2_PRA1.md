# Manual de Usuario
## Práctica 1 – Análisis de Ventas Online 2025

## 1. ¿Para qué sirve?

La aplicación permite:

```text
1. Cargar un archivo CSV.
2. Limpiarlo.
3. Guardarlo en Cloud SQL.
4. Consultar un dashboard.
5. Hacer preguntas mediante IA.
```

---

## 2. Direcciones de acceso

Frontend:

```text
http://localhost:8501
```

Chat de IA:

```text
http://127.0.0.1:8001
```

---

## 3. Cargar el CSV

Abrir el frontend.

En:

```text
1. Carga de datos
```

presionar el botón de carga y seleccionar el CSV.

Columnas esperadas:

```text
Id_cliente
Edad
Genero
Venta_total
N_Compras
FechaCompra
MontoCompra
MetodoPago
Tiempo
Navegador
Boletin
Vale
```

Después de cargarlo se mostrarán:

- Registros encontrados.
- Cantidad de columnas.
- Vista previa.

---

## 4. Limpiar los datos

Ir a:

```text
2. Limpieza de datos
```

Presionar:

```text
Limpiar datos
```

El sistema realiza automáticamente:

- Eliminación de duplicados.
- Validación de edades.
- Conversión de fechas.
- Limpieza de montos.
- Normalización de género.
- Validación del método de pago.
- Validación del navegador.
- Normalización de boletines.
- Normalización de vales.
- Imputación de valores inválidos.

Para el archivo utilizado durante las pruebas se obtuvo:

```text
Registros originales: 1008
Registros limpios: 1003
Registros eliminados: 5
```

También puede abrirse:

```text
Ver reporte de limpieza
```

---

## 5. Descargar CSV limpio

Presionar:

```text
Descargar CSV limpio
```

El archivo se llama:

```text
ventas_online_2025_limpio.csv
```

También queda guardado automáticamente en:

```text
data/ventas_online_2025_limpio.csv
```

---

## 6. Cargar a Cloud SQL

Después de limpiar aparecerá:

```text
3. Base de datos
```

Si la conexión está disponible se verá:

```text
Conexión a Cloud SQL correcta.
```

Presionar:

```text
Cargar datos a Cloud SQL
```

Al finalizar debe mostrarse un mensaje similar a:

```text
1003 registros cargados correctamente.
```

---

## 7. Dashboard

En el menú lateral seleccionar:

```text
Dashboard
```

El dashboard muestra:

- Registros.
- Clientes.
- Ventas totales.
- Ticket promedio.
- Estadísticas básicas.
- Ventas por mes.
- Ventas por método de pago.
- Ventas por navegador.
- Edad vs venta total.
- Ventas por género.
- Ventas según boletín.
- Ventas según vale.
- Uso de boletines y vales por mes.

---

## 8. Chat de IA

Abrir:

```text
http://127.0.0.1:8001
```

Seleccionar:

```text
ventas_agent
```

Escribir preguntas en lenguaje natural.

Ejemplos:

```text
¿Cuántos registros hay en la base?
```

```text
¿Cuál fue el mes con mayores ventas?
```

```text
¿Cómo se comportan las ventas por género?
```

```text
¿Cuál fue el método de pago con mayores ventas?
```

```text
¿Existe correlación entre la edad y la venta total?
```

```text
¿Qué navegador generó más ventas?
```

```text
¿En qué meses se utilizaron más boletines y vales?
```

El usuario no necesita ejecutar SQL manualmente.

---

## 9. Flujo completo

```text
CSV
 ↓
Carga en Streamlit
 ↓
Limpieza
 ↓
Carga a Cloud SQL
 ↓
Dashboard
 ↓
Chat IA
```

---

## 10. Ejemplo de uso

1. Abrir `http://localhost:8501`.
2. Subir `ventas_online_2025.csv`.
3. Presionar `Limpiar datos`.
4. Revisar los resultados.
5. Presionar `Cargar datos a Cloud SQL`.
6. Abrir `Dashboard`.
7. Abrir `http://127.0.0.1:8001`.
8. Seleccionar `ventas_agent`.
9. Realizar preguntas.

---

## 11. Problemas comunes

### No conecta con Cloud SQL

Posible causa:

```text
Cloud SQL Auth Proxy no está ejecutándose.
```

Contactar al administrador/desarrollador.

### No aparecen datos en Dashboard

Verificar que:

```text
1. El CSV haya sido limpiado.
2. Los datos hayan sido cargados a Cloud SQL.
```

### El chat no responde

Verificar que Google ADK esté disponible en:

```text
http://127.0.0.1:8001
```

### El CSV no puede procesarse

Comprobar que tenga las columnas esperadas.

---

## 12. Resumen rápido

```text
1. Abrir Streamlit.
2. Cargar CSV.
3. Limpiar.
4. Cargar a Cloud SQL.
5. Revisar Dashboard.
6. Abrir Chat IA.
7. Consultar los datos.
```
