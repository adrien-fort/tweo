# Azure Database for PostgreSQL Flexible Server — Burstable B1ms SKU
# Provides transparent AES-256 disk encryption by default.
# Customer-managed keys can be enabled via Key Vault when compliance requires it.

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project"              { type = string }
variable "environment"          { type = string }
variable "tags"                 { type = map(string) }

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project}-${var.environment}-pg"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  administrator_login    = "tweo_admin"
  administrator_password = var.db_admin_password

  sku_name   = "B_Standard_B1ms"   # cheapest burstable tier (~$12-15/month)
  storage_mb = 32768

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false  # enable for prod if budget allows

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "tweo"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

variable "db_admin_password" {
  description = "PostgreSQL admin password. Supply via TF_VAR or Key Vault."
  type        = string
  sensitive   = true
}

output "server_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}
