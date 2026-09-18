import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# Permite importar los módulos de app/
APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from analisis import (
    obtener_datos,
    estadisticas_basicas,
    ventas_por_mes,
    ventas_por_metodo_pago,
    ventas_por_navegador,
)


st.set_page_config(
    page_title="Dashboard - Ventas 2025",
    page_icon="📊",
    layout="wide",
)


st.markdown("""
<style>
    .block-container {
        max-width: 1200px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .titulo {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="titulo">Dashboard de Ventas 2025</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Información obtenida directamente desde Cloud SQL'
    '</div>',
    unsafe_allow_html=True
)


try:
    df = obtener_datos()

except Exception as e:
    st.error("No fue posible obtener los datos desde Cloud SQL.")
    st.code(str(e))
    st.stop()


# ---------------------------------------------------------
# Indicadores principales
# ---------------------------------------------------------
total_ventas = df["monto_compra"].sum()
ticket_promedio = df["monto_compra"].mean()
total_clientes = df["id_cliente"].nunique()
total_registros = len(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Registros",
        f"{total_registros:,}"
    )

with col2:
    st.metric(
        "Clientes",
        f"{total_clientes:,}"
    )

with col3:
    st.metric(
        "Ventas",
        f"${total_ventas:,.2f}"
    )

with col4:
    st.metric(
        "Ticket promedio",
        f"${ticket_promedio:,.2f}"
    )


st.divider()


# ---------------------------------------------------------
# Estadísticas
# ---------------------------------------------------------
st.subheader("Estadísticas básicas")

stats = estadisticas_basicas(df)

st.dataframe(
    stats,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ---------------------------------------------------------
# Ventas por mes
# ---------------------------------------------------------
st.subheader("Ventas por mes")

ventas_mes = ventas_por_mes(df)

st.line_chart(
    ventas_mes,
    x="mes",
    y="ventas",
    use_container_width=True
)

mes_mayor = ventas_mes.loc[
    ventas_mes["ventas"].idxmax()
]

mes_menor = ventas_mes.loc[
    ventas_mes["ventas"].idxmin()
]

col1, col2 = st.columns(2)

with col1:
    st.info(
        f"Mayor venta mensual: "
        f"{mes_mayor['mes']} - "
        f"${mes_mayor['ventas']:,.2f}"
    )

with col2:
    st.info(
        f"Menor venta mensual: "
        f"{mes_menor['mes']} - "
        f"${mes_menor['ventas']:,.2f}"
    )


st.divider()


# ---------------------------------------------------------
# Métodos de pago
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("Ventas por método de pago")

    pagos = ventas_por_metodo_pago(df)

    st.bar_chart(
        pagos,
        x="metodo",
        y="ventas",
        use_container_width=True
    )


with col2:

    st.subheader("Ventas por navegador / canal")

    navegadores = ventas_por_navegador(df)

    st.bar_chart(
        navegadores,
        x="canal",
        y="ventas",
        use_container_width=True
    )


st.divider()


# ---------------------------------------------------------
# Venta total vs edad
# ---------------------------------------------------------
st.subheader("Relación entre edad y venta total")

st.scatter_chart(
    df,
    x="edad",
    y="venta_total",
    use_container_width=True
)


st.divider()


# ---------------------------------------------------------
# Género
# ---------------------------------------------------------
st.subheader("Ventas por género")

genero_df = df.copy()

genero_df["genero_nombre"] = genero_df["genero"].map({
    0: "Masculino",
    1: "Femenino",
})

ventas_genero = (
    genero_df
    .groupby(
        "genero_nombre",
        as_index=False
    )["monto_compra"]
    .sum()
)

st.bar_chart(
    ventas_genero,
    x="genero_nombre",
    y="monto_compra",
    use_container_width=True
)


st.divider()


# ---------------------------------------------------------
# Boletín
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.subheader("Ventas según boletín")

    boletin_df = df.copy()

    boletin_df["boletin_nombre"] = (
        boletin_df["boletin"]
        .map({
            0: "No",
            1: "Sí",
        })
    )

    ventas_boletin = (
        boletin_df
        .groupby(
            "boletin_nombre",
            as_index=False
        )["monto_compra"]
        .sum()
    )

    st.bar_chart(
        ventas_boletin,
        x="boletin_nombre",
        y="monto_compra",
        use_container_width=True
    )


with col2:

    st.subheader("Ventas según vale")

    vale_df = df.copy()

    vale_df["vale_nombre"] = (
        vale_df["vale"]
        .map({
            0: "No",
            1: "Sí",
        })
    )

    ventas_vale = (
        vale_df
        .groupby(
            "vale_nombre",
            as_index=False
        )["monto_compra"]
        .sum()
    )

    st.bar_chart(
        ventas_vale,
        x="vale_nombre",
        y="monto_compra",
        use_container_width=True
    )


st.divider()


# ---------------------------------------------------------
# Uso de boletines y vales por mes
# ---------------------------------------------------------
st.subheader("Uso de boletines y vales por mes")

uso_df = df.copy()

uso_df["mes"] = (
    uso_df["fecha_compra"]
    .dt.to_period("M")
    .astype(str)
)

uso_mes = (
    uso_df
    .groupby(
        "mes",
        as_index=False
    )
    .agg({
        "boletin": "sum",
        "vale": "sum",
    })
)

uso_mes = uso_mes.rename(columns={
    "boletin": "Boletines",
    "vale": "Vales",
})

st.line_chart(
    uso_mes,
    x="mes",
    y=["Boletines", "Vales"],
    use_container_width=True
)
