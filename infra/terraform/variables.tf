variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Region de GCP"
  type        = string
  default     = "us-central1"
}

variable "instance_name" {
  description = "Nombre de la instancia Cloud SQL"
  type        = string
  default     = "sog2-pra1-postgres"
}

variable "database_name" {
  description = "Nombre de la base PostgreSQL"
  type        = string
  default     = "ventas_sog2"
}

variable "database_user" {
  description = "Usuario de la aplicacion"
  type        = string
  default     = "sog2_app"
}

variable "database_password" {
  description = "Password del usuario PostgreSQL"
  type        = string
  sensitive   = true
}
