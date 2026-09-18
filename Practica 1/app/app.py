from pathlib import Path
import subprocess
import sys

import pandas as pd
import streamlit as st

from database import (
    cargar_csv_limpio,
    contar_registros,
    probar_conexion,
)


# ---------------------------------------------------------
# Rutas
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PYTHON_DIR = BASE_DIR / "python"

CSV_ORIGINAL = DATA_DIR / "ventas_online_2025.csv"
CSV_LIMPIO = DATA_DIR / "ventas_online_2025_limpio.csv"
REPORTE_LIMPIEZA = DATA_DIR / "reporte_limpieza.txt"

SCRIPT_LIMPIEZA = PYTHON_DIR / "01_limpieza_datos.py"

DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Configuración de Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="SOG2 - Análisis de Ventas",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Estilos
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        .titulo-principal {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitulo {
            color: #666666;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Encabezado
# ---------------------------------------------------------
st.markdown(
    '<div class="titulo-principal">Análisis de Ventas Online 2025</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitulo">'
    'Práctica 1 - Sistemas Organizacionales y Gerenciales 2'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# ---------------------------------------------------------
# 1. Carga del CSV
# ---------------------------------------------------------
st.subheader("1. Carga de datos")

archivo = st.file_uploader(
    "Selecciona el archivo CSV de ventas",
    type=["csv"],
)

if archivo is None:
    st.info(
        "Carga el archivo ventas_online_2025.csv para comenzar."
    )
    st.stop()


# Guardar archivo original
CSV_ORIGINAL.write_bytes(
    archivo.getvalue()
)


try:
    df_original = pd.read_csv(
        CSV_ORIGINAL
    )
except Exception as e:
    st.error(
        f"No fue posible leer el archivo CSV: {e}"
    )
    st.stop()


st.success(
    "Archivo cargado correctamente."
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Registros encontrados",
        len(df_original),
    )

with col2:
    st.metric(
        "Columnas",
        len(df_original.columns),
    )


st.markdown("#### Vista previa")

st.dataframe(
    df_original.head(10),
    use_container_width=True,
)


st.divider()


# ---------------------------------------------------------
# 2. Limpieza
# ---------------------------------------------------------
st.subheader("2. Limpieza de datos")

st.write(
    "El proceso revisa duplicados, valores faltantes o "
    "inválidos, tipos de datos y formatos antes de "
    "generar el archivo limpio."
)


if st.button(
    "Limpiar datos",
    type="primary",
    use_container_width=True,
):
    with st.spinner(
        "Limpiando datos..."
    ):
        proceso = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_LIMPIEZA),
                str(CSV_ORIGINAL),
                "--salida",
                str(CSV_LIMPIO),
                "--reporte",
                str(REPORTE_LIMPIEZA),
            ],
            capture_output=True,
            text=True,
        )

    if proceso.returncode != 0:
        st.error(
            "Ocurrió un error durante la limpieza."
        )

        st.code(
            proceso.stderr
            or proceso.stdout
        )

        st.stop()

    st.success(
        "Proceso de limpieza finalizado."
    )


# ---------------------------------------------------------
# Mostrar resultado si ya existe CSV limpio
# ---------------------------------------------------------
if CSV_LIMPIO.exists():

    df_limpio = pd.read_csv(
        CSV_LIMPIO
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Registros originales",
            len(df_original),
        )

    with col2:
        st.metric(
            "Registros limpios",
            len(df_limpio),
        )

    with col3:
        st.metric(
            "Registros eliminados",
            len(df_original) - len(df_limpio),
        )

    st.markdown(
        "#### Datos después de la limpieza"
    )

    st.dataframe(
        df_limpio.head(10),
        use_container_width=True,
    )

    if REPORTE_LIMPIEZA.exists():

        with st.expander(
            "Ver reporte de limpieza"
        ):
            reporte = (
                REPORTE_LIMPIEZA
                .read_text(
                    encoding="utf-8"
                )
            )

            st.code(
                reporte
            )

    st.download_button(
        "Descargar CSV limpio",
        data=CSV_LIMPIO.read_bytes(),
        file_name="ventas_online_2025_limpio.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()


    # -----------------------------------------------------
    # 3. Cloud SQL
    # -----------------------------------------------------
    st.subheader("3. Base de datos")

    try:

        probar_conexion()

        st.success(
            "Conexión a Cloud SQL correcta."
        )

        registros_actuales = (
            contar_registros()
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Registros listos para cargar",
                len(df_limpio),
            )

        with col2:
            st.metric(
                "Registros actuales en Cloud SQL",
                registros_actuales,
            )

        if st.button(
            "Cargar datos a Cloud SQL",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Cargando datos a Cloud SQL..."
            ):

                cantidad = cargar_csv_limpio(
                    CSV_LIMPIO
                )

            st.success(
                f"{cantidad} registros "
                "cargados correctamente."
            )

            st.metric(
                "Registros en Cloud SQL",
                contar_registros(),
            )

    except Exception as e:

        st.error(
            "No fue posible conectar "
            "con Cloud SQL."
        )

        st.code(
            str(e)
        )

else:

    st.info(
        "Ejecuta la limpieza para continuar "
        "con la carga a Cloud SQL."
    )
