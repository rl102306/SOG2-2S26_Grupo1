from __future__ import annotations

import argparse
from pathlib import Path
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, chi2_contingency


MAP_GENERO = {0: "Masculino", 1: "Femenino"}
MAP_PAGO = {
    0: "Efectivo",
    1: "Tarjeta de Crédito",
    2: "Tarjeta de Débito"
}
MAP_NAVEGADOR = {
    0: "Tienda Física",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4"
}
MAP_SI_NO = {0: "No", 1: "Sí"}


def moda_serie(serie):
    m = serie.mode(dropna=True)
    return m.iloc[0] if not m.empty else np.nan


def cramers_v(tabla):
    chi2, _, _, _ = chi2_contingency(tabla)
    n = tabla.to_numpy().sum()

    if n == 0:
        return np.nan

    filas, columnas = tabla.shape
    denominador = min(filas - 1, columnas - 1)

    if denominador <= 0:
        return np.nan

    return math.sqrt((chi2 / n) / denominador)


def guardar(fig, ruta):
    fig.tight_layout()
    fig.savefig(ruta, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Análisis de ventas YA LIMPIAS")
    parser.add_argument(
        "csv_limpio",
        nargs="?",
        default="ventas_online_2025_limpio.csv"
    )
    parser.add_argument("--salida", default="salida_python")
    args = parser.parse_args()

    salida = Path(args.salida)
    graficos = salida / "graficos"
    tablas = salida / "tablas"

    graficos.mkdir(parents=True, exist_ok=True)
    tablas.mkdir(parents=True, exist_ok=True)

    # IMPORTANTE:
    # Aquí no se realiza limpieza. Se asume que el archivo ya fue
    # generado con 01_limpieza_datos.py.
    df = pd.read_csv(args.csv_limpio)
    df["FechaCompra"] = pd.to_datetime(df["FechaCompra"], format="%Y-%m-%d")

    df["Mes"] = df["FechaCompra"].dt.to_period("M").astype(str)
    df["Genero_desc"] = df["Genero"].map(MAP_GENERO)
    df["MetodoPago_desc"] = df["MetodoPago"].map(MAP_PAGO)
    df["Navegador_desc"] = df["Navegador"].map(MAP_NAVEGADOR)
    df["Boletin_desc"] = df["Boletin"].map(MAP_SI_NO)
    df["Vale_desc"] = df["Vale"].map(MAP_SI_NO)

    # 1. Estadísticas básicas
    columnas = ["Edad", "Venta_total", "N_Compras", "MontoCompra", "Tiempo"]

    estadisticas = []
    for columna in columnas:
        estadisticas.append({
            "Variable": columna,
            "Media": df[columna].mean(),
            "Mediana": df[columna].median(),
            "Moda": moda_serie(df[columna]),
            "Desviacion_estandar": df[columna].std(),
            "Minimo": df[columna].min(),
            "Maximo": df[columna].max()
        })

    pd.DataFrame(estadisticas).to_csv(
        tablas / "estadisticas_basicas.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # 2. Ventas por mes
    ventas_mes = (
        df.groupby("Mes", as_index=False)["MontoCompra"]
        .sum()
        .rename(columns={"MontoCompra": "Ventas"})
    )
    ventas_mes.to_csv(tablas / "ventas_por_mes.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ventas_mes["Mes"], ventas_mes["Ventas"], marker="o")
    ax.set_title("Ventas por mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Monto de ventas")
    ax.tick_params(axis="x", rotation=45)
    guardar(fig, graficos / "01_ventas_por_mes.png")

    # 3. Método de pago
    pago = (
        df.groupby("MetodoPago_desc")["MontoCompra"]
        .sum()
        .sort_values(ascending=False)
    )
    pago.to_csv(tablas / "ventas_por_metodo_pago.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8, 5))
    pago.plot(kind="bar", ax=ax)
    ax.set_title("Ventas por método de pago")
    ax.set_xlabel("Método de pago")
    ax.set_ylabel("Monto de ventas")
    ax.tick_params(axis="x", rotation=20)
    guardar(fig, graficos / "02_ventas_por_metodo_pago.png")

    # 4. Navegador / canal
    navegador = (
        df.groupby("Navegador_desc")["MontoCompra"]
        .sum()
        .sort_values(ascending=False)
    )
    navegador.to_csv(tablas / "ventas_por_navegador.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(9, 5))
    navegador.plot(kind="bar", ax=ax)
    ax.set_title("Ventas por navegador/canal")
    ax.set_xlabel("Navegador / canal")
    ax.set_ylabel("Monto de ventas")
    ax.tick_params(axis="x", rotation=25)
    guardar(fig, graficos / "03_ventas_por_navegador.png")

    # 5. Boletín
    boletin = df.groupby("Boletin_desc")["MontoCompra"].sum()
    boletin.to_csv(tablas / "ventas_por_boletin.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 5))
    boletin.plot(kind="bar", ax=ax)
    ax.set_title("Ventas según uso de boletín")
    ax.set_xlabel("Boletín")
    ax.set_ylabel("Monto de ventas")
    ax.tick_params(axis="x", rotation=0)
    guardar(fig, graficos / "04_ventas_por_boletin.png")

    # 6. Vale
    vale = df.groupby("Vale_desc")["MontoCompra"].sum()
    vale.to_csv(tablas / "ventas_por_vale.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 5))
    vale.plot(kind="bar", ax=ax)
    ax.set_title("Ventas según uso de vale")
    ax.set_xlabel("Vale")
    ax.set_ylabel("Monto de ventas")
    ax.tick_params(axis="x", rotation=0)
    guardar(fig, graficos / "05_ventas_por_vale.png")

    # 7. Correlación venta total vs edad
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["Edad"], df["Venta_total"], alpha=0.6)
    ax.set_title("Venta total vs edad")
    ax.set_xlabel("Edad")
    ax.set_ylabel("Venta total")
    guardar(fig, graficos / "06_venta_total_vs_edad.png")

    # 8. Segmentación por edad
    intervalos = [0, 17, 25, 35, 45, 55, 65, np.inf]
    etiquetas = ["<=17", "18-25", "26-35", "36-45", "46-55", "56-65", "66+"]

    df["GrupoEdad"] = pd.cut(
        df["Edad"],
        bins=intervalos,
        labels=etiquetas,
        include_lowest=True
    )

    edad = (
        df.groupby("GrupoEdad", observed=False)["MontoCompra"]
        .agg(Compras="count", Ventas="sum", TicketPromedio="mean")
        .reset_index()
    )
    edad.to_csv(tablas / "segmentacion_por_edad.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(edad["GrupoEdad"].astype(str), edad["Ventas"])
    ax.set_title("Ventas por grupo de edad")
    ax.set_xlabel("Grupo de edad")
    ax.set_ylabel("Monto de ventas")
    guardar(fig, graficos / "07_ventas_por_grupo_edad.png")

    # 9. Comparación entre géneros
    genero = (
        df.groupby("Genero_desc")["MontoCompra"]
        .agg(Compras="count", Ventas="sum", TicketPromedio="mean")
        .reset_index()
    )
    genero.to_csv(tablas / "comparacion_genero.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(genero["Genero_desc"], genero["Ventas"])
    ax.set_title("Ventas por género")
    ax.set_xlabel("Género")
    ax.set_ylabel("Monto de ventas")
    guardar(fig, graficos / "08_ventas_por_genero.png")

    # 10. Uso de boletines y vales por mes
    uso_mes = (
        df.groupby("Mes", as_index=False)
        .agg(
            Boletines=("Boletin", "sum"),
            Vales=("Vale", "sum")
        )
    )
    uso_mes.to_csv(
        tablas / "uso_boletines_vales_por_mes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(uso_mes["Mes"], uso_mes["Boletines"], marker="o", label="Boletines")
    ax.plot(uso_mes["Mes"], uso_mes["Vales"], marker="o", label="Vales")
    ax.set_title("Uso de boletines y vales por mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cantidad")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    guardar(fig, graficos / "09_boletines_vales_por_mes.png")

    # Correlaciones
    r_edad, p_edad = pearsonr(df["Edad"], df["Venta_total"])

    tabla_genero_pago = pd.crosstab(
        df["Genero_desc"],
        df["MetodoPago_desc"]
    )

    tabla_boletin_vale = pd.crosstab(
        df["Boletin_desc"],
        df["Vale_desc"]
    )

    tabla_genero_pago.to_csv(
        tablas / "contingencia_genero_metodo_pago.csv",
        encoding="utf-8-sig"
    )
    tabla_boletin_vale.to_csv(
        tablas / "contingencia_boletin_vale.csv",
        encoding="utf-8-sig"
    )

    v_genero_pago = cramers_v(tabla_genero_pago)
    v_boletin_vale = cramers_v(tabla_boletin_vale)

    mes_mayor = ventas_mes.loc[ventas_mes["Ventas"].idxmax()]
    mes_menor = ventas_mes.loc[ventas_mes["Ventas"].idxmin()]

    frecuencia_nav = df["Navegador_desc"].value_counts()
    navegador_mas = frecuencia_nav.idxmax()
    navegador_menos = frecuencia_nav.idxmin()

    total_efectivo = df.loc[
        df["MetodoPago"] == 0,
        "MontoCompra"
    ].sum()

    resumen = [
        "RESUMEN DEL ANÁLISIS",
        "====================",
        f"Mes con mayores ventas: {mes_mayor['Mes']} | {mes_mayor['Ventas']:.2f}",
        f"Mes con menores ventas: {mes_menor['Mes']} | {mes_menor['Ventas']:.2f}",
        f"Navegador/canal más utilizado: {navegador_mas}",
        f"Navegador/canal menos utilizado: {navegador_menos}",
        f"Total pagado en efectivo: {total_efectivo:.2f}",
        f"Pearson Edad vs Venta_total: r={r_edad:.4f}, p={p_edad:.6f}",
        f"Cramér V Genero vs MetodoPago: {v_genero_pago:.4f}",
        f"Cramér V Boletin vs Vale: {v_boletin_vale:.4f}",
    ]

    (salida / "resumen.txt").write_text(
        "\n".join(resumen),
        encoding="utf-8"
    )

    print(f"Análisis terminado: {salida.resolve()}")


if __name__ == "__main__":
    main()
