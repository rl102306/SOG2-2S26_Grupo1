suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(stringr)
  library(lubridate)
})

args <- commandArgs(trailingOnly = TRUE)

ruta_csv <- ifelse(
  length(args) >= 1,
  args[1],
  "../ventas_online_2025.csv"
)

salida_csv <- ifelse(
  length(args) >= 2,
  args[2],
  "ventas_online_2025_limpio.csv"
)

reporte_txt <- ifelse(
  length(args) >= 3,
  args[3],
  "reporte_limpieza.txt"
)

limpiar_numero <- function(x) {
  x <- as.character(x)
  x <- str_trim(x)
  x <- str_replace_all(x, fixed("$"), "")
  x <- str_replace_all(x, fixed('"'), "")
  x <- str_replace_all(x, fixed("'"), "")

  resultado <- sapply(x, function(v) {
    if (is.na(v) || v == "") {
      return(NA_real_)
    }

    if (str_detect(v, ",") && !str_detect(v, fixed("."))) {
      v <- str_replace_all(v, ",", ".")
    } else if (str_detect(v, ",") && str_detect(v, fixed("."))) {
      v <- str_replace_all(v, ",", "")
    }

    suppressWarnings(as.numeric(v))
  })

  as.numeric(resultado)
}

normalizar_genero <- function(x) {
  x <- as.character(x)
  x <- str_to_lower(str_trim(x))
  x <- str_replace_all(x, "í", "i")

  case_when(
    x %in% c("0", "0.0", "masculino") ~ 0,
    x %in% c("1", "1.0", "femenino") ~ 1,
    TRUE ~ NA_real_
  )
}

normalizar_si_no <- function(x) {
  x <- as.character(x)
  x <- str_to_lower(str_trim(x))
  x <- str_replace_all(x, "í", "i")

  case_when(
    x %in% c("0", "0.0", "no") ~ 0,
    x %in% c("1", "1.0", "si") ~ 1,
    TRUE ~ NA_real_
  )
}

moda <- function(x) {
  x <- x[!is.na(x)]
  if (length(x) == 0) {
    return(NA_real_)
  }

  valores <- unique(x)
  valores[which.max(tabulate(match(x, valores)))]
}

df <- read_csv(ruta_csv, show_col_types = FALSE)

filas_iniciales <- nrow(df)

names(df) <- str_trim(names(df))
names(df)[names(df) == "Boletín"] <- "Boletin"

requeridas <- c(
  "Id_cliente", "Edad", "Genero", "Venta_total",
  "N_Compras", "FechaCompra", "MontoCompra",
  "MetodoPago", "Tiempo", "Navegador",
  "Boletin", "Vale"
)

faltan <- setdiff(requeridas, names(df))
if (length(faltan) > 0) {
  stop(
    paste(
      "Faltan columnas requeridas:",
      paste(faltan, collapse = ", ")
    )
  )
}

duplicados <- sum(duplicated(df))
df <- distinct(df)

df$Genero <- normalizar_genero(df$Genero)
df$Boletin <- normalizar_si_no(df$Boletin)
df$Vale <- normalizar_si_no(df$Vale)

df$Venta_total <- limpiar_numero(df$Venta_total)
df$MontoCompra <- limpiar_numero(df$MontoCompra)

for (columna in c(
  "Id_cliente", "Edad", "N_Compras",
  "MetodoPago", "Tiempo", "Navegador"
)) {
  df[[columna]] <- suppressWarnings(as.numeric(df[[columna]]))
}

df$FechaCompra <- suppressWarnings(
  parse_date_time(
    as.character(df$FechaCompra),
    orders = c(
      "Y-m-d",
      "Y/m/d",
      "d-m-Y",
      "d/m/Y",
      "m/d/Y"
    )
  )
)

df$FechaCompra <- as.Date(df$FechaCompra)

# Reglas de validez
df$Edad[df$Edad < 0 | df$Edad > 100] <- NA
df$Venta_total[df$Venta_total < 0] <- NA
df$MontoCompra[df$MontoCompra < 0] <- NA

df$MetodoPago[!df$MetodoPago %in% c(0, 1, 2)] <- NA
df$Navegador[!df$Navegador %in% c(0, 1, 2, 3, 4)] <- NA

faltantes_antes <- sapply(df, function(x) sum(is.na(x)))

# Imputación categórica con moda
for (columna in c(
  "Genero", "MetodoPago", "Navegador",
  "Boletin", "Vale"
)) {
  valor_moda <- moda(df[[columna]])

  if (!is.na(valor_moda)) {
    df[[columna]][is.na(df[[columna]])] <- valor_moda
  }
}

# Imputación numérica con mediana
for (columna in c(
  "Edad", "Venta_total", "N_Compras",
  "MontoCompra", "Tiempo"
)) {
  mediana <- median(df[[columna]], na.rm = TRUE)
  df[[columna]][is.na(df[[columna]])] <- mediana
}

fechas_invalidas <- sum(is.na(df$FechaCompra))
df <- df |>
  filter(!is.na(FechaCompra))

# Enteros finales
for (columna in c(
  "Id_cliente", "Genero", "N_Compras",
  "MetodoPago", "Navegador", "Boletin", "Vale"
)) {
  df[[columna]] <- as.integer(round(df[[columna]]))
}

faltantes_despues <- sapply(df, function(x) sum(is.na(x)))

write_csv(df, salida_csv)

reporte <- c(
  "REPORTE DE LIMPIEZA",
  "===================",
  paste("Filas originales:", filas_iniciales),
  paste("Duplicados eliminados:", duplicados),
  paste("Fechas inválidas eliminadas:", fechas_invalidas),
  paste("Filas finales:", nrow(df)),
  "",
  "VALORES FALTANTES / INVÁLIDOS DETECTADOS ANTES DE IMPUTAR"
)

for (nombre in names(faltantes_antes)) {
  reporte <- c(
    reporte,
    paste("-", nombre, ":", faltantes_antes[[nombre]])
  )
}

reporte <- c(
  reporte,
  "",
  "VALORES FALTANTES DESPUÉS DE LA LIMPIEZA"
)

for (nombre in names(faltantes_despues)) {
  reporte <- c(
    reporte,
    paste("-", nombre, ":", faltantes_despues[[nombre]])
  )
}

reporte <- c(
  reporte,
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
  "- Duplicados exactos: eliminados."
)

writeLines(reporte, reporte_txt, useBytes = TRUE)

message("Archivo limpio: ", normalizePath(salida_csv))
message("Reporte: ", normalizePath(reporte_txt))
