suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(ggplot2)
  library(tidyr)
})

args <- commandArgs(trailingOnly = TRUE)

ruta_csv <- ifelse(
  length(args) >= 1,
  args[1],
  "ventas_online_2025_limpio.csv"
)

salida <- ifelse(
  length(args) >= 2,
  args[2],
  "salida_r"
)

dir.create(salida, showWarnings = FALSE, recursive = TRUE)
dir.create(
  file.path(salida, "graficos"),
  showWarnings = FALSE,
  recursive = TRUE
)
dir.create(
  file.path(salida, "tablas"),
  showWarnings = FALSE,
  recursive = TRUE
)

# IMPORTANTE:
# Este script NO hace limpieza.
# Lee el archivo generado por 01_limpieza_datos.R.
df <- read_csv(ruta_csv, show_col_types = FALSE)

df$FechaCompra <- as.Date(df$FechaCompra)

df <- df |>
  mutate(
    Mes = format(FechaCompra, "%Y-%m"),
    Genero_desc = ifelse(
      Genero == 1,
      "Femenino",
      "Masculino"
    ),
    MetodoPago_desc = case_when(
      MetodoPago == 0 ~ "Efectivo",
      MetodoPago == 1 ~ "Tarjeta de Crédito",
      MetodoPago == 2 ~ "Tarjeta de Débito"
    ),
    Navegador_desc = case_when(
      Navegador == 0 ~ "Tienda Física",
      Navegador == 1 ~ "Navegador 1",
      Navegador == 2 ~ "Navegador 2",
      Navegador == 3 ~ "Navegador 3",
      Navegador == 4 ~ "Navegador 4"
    ),
    Boletin_desc = ifelse(Boletin == 1, "Sí", "No"),
    Vale_desc = ifelse(Vale == 1, "Sí", "No")
  )

moda <- function(x) {
  valores <- unique(x)
  valores[which.max(tabulate(match(x, valores)))]
}

# Estadísticas
columnas <- c(
  "Edad", "Venta_total", "N_Compras",
  "MontoCompra", "Tiempo"
)

estadisticas <- bind_rows(
  lapply(columnas, function(columna) {
    x <- df[[columna]]

    data.frame(
      Variable = columna,
      Media = mean(x),
      Mediana = median(x),
      Moda = moda(x),
      Desviacion_estandar = sd(x),
      Minimo = min(x),
      Maximo = max(x)
    )
  })
)

write_csv(
  estadisticas,
  file.path(salida, "tablas", "estadisticas_basicas.csv")
)

# Ventas por mes
ventas_mes <- df |>
  group_by(Mes) |>
  summarise(
    Ventas = sum(MontoCompra),
    .groups = "drop"
  ) |>
  arrange(Mes)

write_csv(
  ventas_mes,
  file.path(salida, "tablas", "ventas_por_mes.csv")
)

p <- ggplot(
  ventas_mes,
  aes(Mes, Ventas, group = 1)
) +
  geom_line() +
  geom_point() +
  labs(
    title = "Ventas por mes",
    x = "Mes",
    y = "Monto de ventas"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(
      angle = 45,
      hjust = 1
    )
  )

ggsave(
  file.path(salida, "graficos", "01_ventas_por_mes.png"),
  p,
  width = 10,
  height = 5,
  dpi = 160
)

# Método de pago
pago <- df |>
  group_by(MetodoPago_desc) |>
  summarise(
    Ventas = sum(MontoCompra),
    .groups = "drop"
  )

write_csv(
  pago,
  file.path(salida, "tablas", "ventas_por_metodo_pago.csv")
)

p <- ggplot(
  pago,
  aes(reorder(MetodoPago_desc, Ventas), Ventas)
) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Ventas por método de pago",
    x = "Método de pago",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "02_ventas_por_metodo_pago.png"),
  p,
  width = 8,
  height = 5,
  dpi = 160
)

# Navegador
navegador <- df |>
  group_by(Navegador_desc) |>
  summarise(
    Ventas = sum(MontoCompra),
    .groups = "drop"
  )

write_csv(
  navegador,
  file.path(salida, "tablas", "ventas_por_navegador.csv")
)

p <- ggplot(
  navegador,
  aes(reorder(Navegador_desc, Ventas), Ventas)
) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Ventas por navegador/canal",
    x = "Navegador / canal",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "03_ventas_por_navegador.png"),
  p,
  width = 9,
  height = 5,
  dpi = 160
)

# Boletín
boletin <- df |>
  group_by(Boletin_desc) |>
  summarise(
    Ventas = sum(MontoCompra),
    .groups = "drop"
  )

write_csv(
  boletin,
  file.path(salida, "tablas", "ventas_por_boletin.csv")
)

p <- ggplot(
  boletin,
  aes(Boletin_desc, Ventas)
) +
  geom_col() +
  labs(
    title = "Ventas según uso de boletín",
    x = "Boletín",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "04_ventas_por_boletin.png"),
  p,
  width = 7,
  height = 5,
  dpi = 160
)

# Vale
vale <- df |>
  group_by(Vale_desc) |>
  summarise(
    Ventas = sum(MontoCompra),
    .groups = "drop"
  )

write_csv(
  vale,
  file.path(salida, "tablas", "ventas_por_vale.csv")
)

p <- ggplot(
  vale,
  aes(Vale_desc, Ventas)
) +
  geom_col() +
  labs(
    title = "Ventas según uso de vale",
    x = "Vale",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "05_ventas_por_vale.png"),
  p,
  width = 7,
  height = 5,
  dpi = 160
)

# Venta total vs edad
p <- ggplot(
  df,
  aes(Edad, Venta_total)
) +
  geom_point(alpha = 0.6) +
  labs(
    title = "Venta total vs edad",
    x = "Edad",
    y = "Venta total"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "06_venta_total_vs_edad.png"),
  p,
  width = 8,
  height = 5,
  dpi = 160
)

# Segmentación por edad
df <- df |>
  mutate(
    GrupoEdad = cut(
      Edad,
      breaks = c(
        -Inf, 17, 25, 35,
        45, 55, 65, Inf
      ),
      labels = c(
        "<=17", "18-25", "26-35",
        "36-45", "46-55", "56-65", "66+"
      )
    )
  )

edad <- df |>
  group_by(GrupoEdad) |>
  summarise(
    Compras = n(),
    Ventas = sum(MontoCompra),
    TicketPromedio = mean(MontoCompra),
    .groups = "drop"
  )

write_csv(
  edad,
  file.path(salida, "tablas", "segmentacion_por_edad.csv")
)

p <- ggplot(
  edad,
  aes(GrupoEdad, Ventas)
) +
  geom_col() +
  labs(
    title = "Ventas por grupo de edad",
    x = "Grupo de edad",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "07_ventas_por_grupo_edad.png"),
  p,
  width = 9,
  height = 5,
  dpi = 160
)

# Género
genero <- df |>
  group_by(Genero_desc) |>
  summarise(
    Compras = n(),
    Ventas = sum(MontoCompra),
    TicketPromedio = mean(MontoCompra),
    .groups = "drop"
  )

write_csv(
  genero,
  file.path(salida, "tablas", "comparacion_genero.csv")
)

p <- ggplot(
  genero,
  aes(Genero_desc, Ventas)
) +
  geom_col() +
  labs(
    title = "Ventas por género",
    x = "Género",
    y = "Monto de ventas"
  ) +
  theme_minimal()

ggsave(
  file.path(salida, "graficos", "08_ventas_por_genero.png"),
  p,
  width = 7,
  height = 5,
  dpi = 160
)

# Boletines y vales por mes
uso_mes <- df |>
  group_by(Mes) |>
  summarise(
    Boletines = sum(Boletin),
    Vales = sum(Vale),
    .groups = "drop"
  )

write_csv(
  uso_mes,
  file.path(
    salida,
    "tablas",
    "uso_boletines_vales_por_mes.csv"
  )
)

uso_largo <- uso_mes |>
  pivot_longer(
    cols = c(Boletines, Vales),
    names_to = "Tipo",
    values_to = "Cantidad"
  )

p <- ggplot(
  uso_largo,
  aes(
    Mes,
    Cantidad,
    group = Tipo,
    linetype = Tipo
  )
) +
  geom_line() +
  geom_point() +
  labs(
    title = "Uso de boletines y vales por mes",
    x = "Mes",
    y = "Cantidad"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(
      angle = 45,
      hjust = 1
    )
  )

ggsave(
  file.path(
    salida,
    "graficos",
    "09_boletines_vales_por_mes.png"
  ),
  p,
  width = 10,
  height = 5,
  dpi = 160
)

# Correlaciones
pearson <- cor.test(
  df$Edad,
  df$Venta_total,
  method = "pearson"
)

tabla_genero_pago <- table(
  df$Genero_desc,
  df$MetodoPago_desc
)

tabla_boletin_vale <- table(
  df$Boletin_desc,
  df$Vale_desc
)

cramers_v <- function(tabla) {
  chi <- suppressWarnings(
    chisq.test(
      tabla,
      correct = FALSE
    )$statistic
  )

  n <- sum(tabla)
  dimensiones <- dim(tabla)
  denominador <- min(
    dimensiones[1] - 1,
    dimensiones[2] - 1
  )

  if (denominador <= 0) {
    return(NA_real_)
  }

  as.numeric(
    sqrt((chi / n) / denominador)
  )
}

v_genero_pago <- cramers_v(tabla_genero_pago)
v_boletin_vale <- cramers_v(tabla_boletin_vale)

mes_mayor <- ventas_mes[
  which.max(ventas_mes$Ventas),
]

mes_menor <- ventas_mes[
  which.min(ventas_mes$Ventas),
]

frecuencia_nav <- sort(
  table(df$Navegador_desc),
  decreasing = TRUE
)

navegador_mas <- names(frecuencia_nav)[1]
navegador_menos <- names(frecuencia_nav)[length(frecuencia_nav)]

total_efectivo <- sum(
  df$MontoCompra[df$MetodoPago == 0]
)

resumen <- c(
  "RESUMEN DEL ANÁLISIS",
  "====================",
  sprintf(
    "Mes con mayores ventas: %s | %.2f",
    mes_mayor$Mes,
    mes_mayor$Ventas
  ),
  sprintf(
    "Mes con menores ventas: %s | %.2f",
    mes_menor$Mes,
    mes_menor$Ventas
  ),
  paste(
    "Navegador/canal más utilizado:",
    navegador_mas
  ),
  paste(
    "Navegador/canal menos utilizado:",
    navegador_menos
  ),
  sprintf(
    "Total pagado en efectivo: %.2f",
    total_efectivo
  ),
  sprintf(
    "Pearson Edad vs Venta_total: r=%.4f, p=%.6f",
    unname(pearson$estimate),
    pearson$p.value
  ),
  sprintf(
    "Cramér V Genero vs MetodoPago: %.4f",
    v_genero_pago
  ),
  sprintf(
    "Cramér V Boletin vs Vale: %.4f",
    v_boletin_vale
  )
)

writeLines(
  resumen,
  file.path(salida, "resumen.txt"),
  useBytes = TRUE
)

message(
  "Análisis terminado: ",
  normalizePath(salida)
)
