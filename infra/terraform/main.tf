resource "google_project_service" "sqladmin" {
  project = var.project_id
  service = "sqladmin.googleapis.com"

  disable_on_destroy = false
}

resource "google_sql_database_instance" "postgres" {
  name             = var.instance_name
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_15"

  deletion_protection = false

  settings {
    tier              = "db-f1-micro"
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"

    disk_type       = "PD_HDD"
    disk_size       = 10
    disk_autoresize = false

    ip_configuration {
      ipv4_enabled = true
    }

    backup_configuration {
      enabled = false
    }

    user_labels = {
      proyecto = "sog2"
      practica = "pra1"
      grupo    = "grupo1"
    }
  }

  depends_on = [
    google_project_service.sqladmin
  ]
}

resource "google_sql_database" "ventas" {
  name     = var.database_name
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app" {
  name     = var.database_user
  project  = var.project_id
  instance = google_sql_database_instance.postgres.name
  password = var.database_password
}
