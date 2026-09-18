from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def limpiar_numero(valor):
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip()
    texto = texto.replace("$", "").replace('"', "").replace("'", "").strip()

    if texto == "":
        return np.nan

    # Si únicamente hay coma, se considera separador decimal.
    if "," in texto and "." not in texto:
        texto = texto.replace(",", ".")
    elif "," in texto and "." in texto:
        texto = texto.replace(",", "")

    try:
        return float(texto)
    except ValueError:
        return np.nan


def normalizar_genero(valor):
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip().lower().replace("í", "i")

    if texto in {"0", "0.0", "masculino"}:
        return 0
    if texto in {"1", "1.0", "femenino"}:
        return 1

    return np.nan


def normalizar_si_no(valor):
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip().lower().replace("í", "i")

    if texto in {"0", "0.0", "no"}:
        return 0
    if texto in {"1", "1.0", "si"}:
        return 1

    return np.nan


def convertir_fecha(valor):
    if pd.isna(valor):
        return pd.NaT

    texto = str(valor).strip()

    formatos = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for formato in formatos:
        try:
            return pd.to_datetime(texto, format=formato)
        except (ValueError, TypeError):
            pass

    return pd.NaT


def moda(serie):
    resultado = serie.mode(dropna=True)
    return resultado.iloc[0] if not resultado.empty else np.nan


def limpiar_datos(ruta_csv: str, salida_csv: str, reporte_txt: str):
    df = pd.read_csv(ruta_csv)

    filas_iniciales = len(df)

    # 1. Normalización de nombres de columnas
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Boletín": "Boletin"})

    columnas_requeridas = [
        "Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras",
        "FechaCompra", "MontoCompra", "MetodoPago", "Tiempo",
        "Navegador", "Boletin", "Vale"
    ]

    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")

    # 2. Duplicados
    duplicados = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # 3. Conversión / estandarización
    df["Genero"] = df["Genero"].apply(normalizar_genero)
    df["Boletin"] = df["Boletin"].apply(normalizar_si_no)
    df["Vale"] = df["Vale"].apply(normalizar_si_no)

    for columna in ["Venta_total", "MontoCompra"]:
        df[columna] = df[columna].apply(limpiar_numero)

    for columna in ["Id_cliente", "Edad", "N_Compras", "MetodoPago", "Tiempo", "Navegador"]:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df["FechaCompra"] = df["FechaCompra"].apply(convertir_fecha)

    # 4. Validación de reglas
    df.loc[(df["Edad"] < 0) | (df["Edad"] > 100), "Edad"] = np.nan
    df.loc[df["Venta_total"] < 0, "Venta_total"] = np.nan
    df.loc[df["MontoCompra"] < 0, "MontoCompra"] = np.nan

    df.loc[~df["MetodoPago"].isin([0, 1, 2]), "MetodoPago"] = np.nan
    df.loc[~df["Navegador"].isin([0, 1, 2, 3, 4]), "Navegador"] = np.nan

    faltantes_antes = df.isna().sum().to_dict()

    # 5. Imputación de faltantes / inválidos
    categoricas = ["Genero", "MetodoPago", "Navegador", "Boletin", "Vale"]
    for columna in categoricas:
        valor_moda = moda(df[columna])
        if not pd.isna(valor_moda):
            df[columna] = df[columna].fillna(valor_moda)

    numericas = ["Edad", "Venta_total", "N_Compras", "MontoCompra", "Tiempo"]
    for columna in numericas:
        mediana = df[columna].median()
        df[columna] = df[columna].fillna(mediana)

    # Si alguna fecha no pudo convertirse, se elimina la fila porque
    # no puede utilizarse correctamente en el análisis mensual.
    fechas_invalidas = int(df["FechaCompra"].isna().sum())
    df = df.dropna(subset=["FechaCompra"]).copy()

    # 6. Tipos finales
    for columna in [
        "Id_cliente", "Genero", "N_Compras",
        "MetodoPago", "Navegador", "Boletin", "Vale"
    ]:
        df[columna] = df[columna].round().astype(int)

    df["FechaCompra"] = df["FechaCompra"].dt.strftime("%Y-%m-%d")

    # 7. Guardar
    salida = Path(salida_csv)
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8-sig")

    faltantes_despues = df.isna().sum().to_dict()

    reporte = [
        "REPORTE DE LIMPIEZA",
        "===================",
        f"Filas originales: {filas_iniciales}",
        f"Duplicados eliminados: {duplicados}",
        f"Fechas inválidas eliminadas: {fechas_invalidas}",
        f"Filas finales: {len(df)}",
        "",
        "VALORES FALTANTES / INVÁLIDOS DETECTADOS ANTES DE IMPUTAR",
    ]

    for columna, cantidad in faltantes_antes.items():
        reporte.append(f"- {columna}: {cantidad}")

    reporte.extend([
        "",
        "VALORES FALTANTES DESPUÉS DE LA LIMPIEZA",
    ])

    for columna, cantidad in faltantes_despues.items():
        reporte.append(f"- {columna}: {cantidad}")

    reporte.extend([
        "",
        "CRITERIOS UTILIZADOS",
        "- Edad válida: 0 a 100 años.",
        "- Genero válido: 0 = Masculino, 1 = Femenino.",
        "- MetodoPago válido: 0, 1 o 2.",
        "- Navegador válido: 0, 1, 2, 3 o 4.",
        "- Boletin y Vale válidos: 0 o 1.",
        "- Montos negativos se consideran inválidos.",
        "- Numéricos faltantes/inválidos: mediana.",
        "- Categóricos faltantes/inválidos: moda.",
        "- Duplicados exactos: eliminados.",
    ])

    Path(reporte_txt).write_text("\n".join(reporte), encoding="utf-8")

    print(f"Archivo limpio: {salida.resolve()}")
    print(f"Reporte: {Path(reporte_txt).resolve()}")
    print(f"Filas finales: {len(df)}")


def main():
    parser = argparse.ArgumentParser(description="Limpieza de ventas online 2025")
    parser.add_argument("csv", nargs="?", default="../ventas_online_2025.csv")
    parser.add_argument(
        "--salida",
        default="ventas_online_2025_limpio.csv"
    )
    parser.add_argument(
        "--reporte",
        default="reporte_limpieza.txt"
    )
    args = parser.parse_args()

    limpiar_datos(args.csv, args.salida, args.reporte)


if __name__ == "__main__":
    main()
