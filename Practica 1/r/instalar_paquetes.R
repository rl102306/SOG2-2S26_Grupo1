paquetes <- c("readr", "dplyr", "ggplot2", "tidyr", "stringr", "lubridate")
faltantes <- setdiff(paquetes, rownames(installed.packages()))
if (length(faltantes) > 0) install.packages(faltantes, repos="https://cloud.r-project.org")
message("Paquetes listos.")
