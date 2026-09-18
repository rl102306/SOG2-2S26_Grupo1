import sys
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

sys.path.insert(0, str(APP_DIR))

from analisis import (
    obtener_datos,
    estadisticas_basicas,
    ventas_por_mes,
    ventas_por_metodo_pago,
    ventas_por_navegador,
)


mcp = FastMCP("sog2-ventas-mcp")


@mcp.tool()
def resumen_general() -> dict:
    """Devuelve un resumen general de las ventas."""

    df = obtener_datos()

    return {
        "registros": int(len(df)),
        "clientes_unicos": int(df["id_cliente"].nunique()),
        "ventas_totales": round(float(df["monto_compra"].sum()), 2),
        "ticket_promedio": round(float(df["monto_compra"].mean()), 2),
    }


@mcp.tool()
def obtener_estadisticas_basicas() -> list:
    """Devuelve estadísticas básicas de las variables numéricas."""

    df = obtener_datos()
    resultado = estadisticas_basicas(df)

    return resultado.to_dict(orient="records")


@mcp.tool()
def consultar_ventas_por_mes() -> list:
    """Devuelve las ventas agrupadas por mes."""

    df = obtener_datos()

    return ventas_por_mes(df).to_dict(
        orient="records"
    )


@mcp.tool()
def consultar_ventas_por_metodo_pago() -> list:
    """Devuelve las ventas agrupadas por método de pago."""

    df = obtener_datos()

    return ventas_por_metodo_pago(df).to_dict(
        orient="records"
    )


@mcp.tool()
def consultar_ventas_por_navegador() -> list:
    """Devuelve las ventas agrupadas por navegador o canal."""

    df = obtener_datos()

    return ventas_por_navegador(df).to_dict(
        orient="records"
    )


@mcp.tool()
def consultar_correlacion_edad_venta() -> dict:
    """Calcula la correlación de Pearson entre edad y venta total."""

    df = obtener_datos()

    correlacion = df[
        ["edad", "venta_total"]
    ].corr(method="pearson").iloc[0, 1]

    return {
        "variable_x": "edad",
        "variable_y": "venta_total",
        "correlacion_pearson": round(
            float(correlacion),
            6,
        ),
    }


@mcp.tool()
def consultar_ventas_por_genero() -> list:
    """Devuelve compras, ventas y ticket promedio por género."""

    df = obtener_datos()

    datos = df.copy()

    datos["genero_nombre"] = datos["genero"].map({
        0: "Masculino",
        1: "Femenino",
    })

    resultado = (
        datos.groupby(
            "genero_nombre",
            as_index=False,
        )
        .agg(
            compras=("monto_compra", "count"),
            ventas=("monto_compra", "sum"),
            ticket_promedio=("monto_compra", "mean"),
        )
    )

    return resultado.to_dict(
        orient="records"
    )


@mcp.tool()
def consultar_segmentacion_edad() -> list:
    """Agrupa clientes por rango de edad."""

    df = obtener_datos()

    datos = df.copy()

    datos["grupo_edad"] = pd.cut(
        datos["edad"],
        bins=[
            -1,
            17,
            25,
            35,
            45,
            55,
            65,
            float("inf"),
        ],
        labels=[
            "0-17",
            "18-25",
            "26-35",
            "36-45",
            "46-55",
            "56-65",
            "66+",
        ],
    )

    resultado = (
        datos.groupby(
            "grupo_edad",
            observed=False,
        )
        .agg(
            clientes=("id_cliente", "nunique"),
            compras=("monto_compra", "count"),
            ventas=("monto_compra", "sum"),
            ticket_promedio=("monto_compra", "mean"),
        )
        .reset_index()
    )

    resultado["grupo_edad"] = (
        resultado["grupo_edad"].astype(str)
    )

    return resultado.to_dict(
        orient="records"
    )


@mcp.tool()
def consultar_boletines_vales_por_mes() -> list:
    """Devuelve el uso de boletines y vales agrupado por mes."""

    df = obtener_datos()

    datos = df.copy()

    datos["mes"] = (
        datos["fecha_compra"]
        .dt.to_period("M")
        .astype(str)
    )

    resultado = (
        datos.groupby(
            "mes",
            as_index=False,
        )
        .agg(
            boletines=("boletin", "sum"),
            vales=("vale", "sum"),
        )
    )

    return resultado.to_dict(
        orient="records"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
