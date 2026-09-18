import pandas as pd

from database import obtener_engine


def obtener_datos():
    """
    Obtiene los datos directamente desde Cloud SQL.
    """

    engine = obtener_engine()

    consulta = """
        SELECT
            id_cliente,
            edad,
            genero,
            venta_total,
            n_compras,
            fecha_compra,
            monto_compra,
            metodo_pago,
            tiempo,
            navegador,
            boletin,
            vale
        FROM ventas_online_2025
        ORDER BY fecha_compra
    """

    df = pd.read_sql(
        consulta,
        engine
    )

    df["fecha_compra"] = pd.to_datetime(
        df["fecha_compra"]
    )

    return df


def estadisticas_basicas(df):
    """
    Media, mediana y moda de las variables numéricas.
    """

    columnas = [
        "edad",
        "venta_total",
        "n_compras",
        "monto_compra",
        "tiempo",
    ]

    resultados = []

    for columna in columnas:

        moda = df[columna].mode()

        resultados.append({
            "Variable": columna,
            "Media": df[columna].mean(),
            "Mediana": df[columna].median(),
            "Moda": moda.iloc[0] if not moda.empty else None,
            "Mínimo": df[columna].min(),
            "Máximo": df[columna].max(),
            "Desviación estándar": df[columna].std(),
        })

    return pd.DataFrame(resultados)


def ventas_por_mes(df):

    datos = df.copy()

    datos["mes"] = (
        datos["fecha_compra"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        datos.groupby(
            "mes",
            as_index=False
        )["monto_compra"]
        .sum()
        .rename(
            columns={
                "monto_compra": "ventas"
            }
        )
    )


def ventas_por_metodo_pago(df):

    nombres = {
        0: "Efectivo",
        1: "Tarjeta de Crédito",
        2: "Tarjeta de Débito",
    }

    datos = df.copy()

    datos["metodo"] = (
        datos["metodo_pago"]
        .map(nombres)
    )

    return (
        datos.groupby(
            "metodo",
            as_index=False
        )["monto_compra"]
        .sum()
        .rename(
            columns={
                "monto_compra": "ventas"
            }
        )
    )


def ventas_por_navegador(df):

    nombres = {
        0: "Tienda Física",
        1: "Navegador 1",
        2: "Navegador 2",
        3: "Navegador 3",
        4: "Navegador 4",
    }

    datos = df.copy()

    datos["canal"] = (
        datos["navegador"]
        .map(nombres)
    )

    return (
        datos.groupby(
            "canal",
            as_index=False
        )["monto_compra"]
        .sum()
        .rename(
            columns={
                "monto_compra": "ventas"
            }
        )
    )
