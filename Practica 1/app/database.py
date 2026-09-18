import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def obtener_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(
        url,
        pool_pre_ping=True
    )


def probar_conexion():
    engine = obtener_engine()

    with engine.connect() as conexion:
        conexion.execute(text("SELECT 1"))

    return True


def cargar_csv_limpio(ruta_csv):
    df = pd.read_csv(ruta_csv)

    df = df.rename(columns={
        "Id_cliente": "id_cliente",
        "Edad": "edad",
        "Genero": "genero",
        "Venta_total": "venta_total",
        "N_Compras": "n_compras",
        "FechaCompra": "fecha_compra",
        "MontoCompra": "monto_compra",
        "MetodoPago": "metodo_pago",
        "Tiempo": "tiempo",
        "Navegador": "navegador",
        "Boletin": "boletin",
        "Vale": "vale",
    })

    df["fecha_compra"] = pd.to_datetime(
        df["fecha_compra"]
    ).dt.date

    engine = obtener_engine()

    with engine.begin() as conexion:

        conexion.execute(
            text("TRUNCATE TABLE ventas_online_2025")
        )

        df.to_sql(
            "ventas_online_2025",
            conexion,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500
        )

    return len(df)

def contar_registros():
    engine = obtener_engine()

    with engine.connect() as conexion:
        cantidad = conexion.execute(
            text(
                "SELECT COUNT(*) "
                "FROM ventas_online_2025"
            )
        ).scalar()

    return cantidad
