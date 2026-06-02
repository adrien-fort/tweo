# Key Vault stores the DATABASE_ENCRYPTION_KEY and DB credentials.
# AKS Managed Identity is granted Get/List secret access at deploy time.

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project"              { type = string }
variable "environment"          { type = string }
variable "aks_principal_id"     { type = string }
variable "tags"                 { type = map(string) }

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = "${var.project}-${var.environment}-kv"
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  soft_delete_retention_days = 7
  purge_protection_enabled   = true

  tags = var.tags
}

# Grant AKS Managed Identity read access to secrets
resource "azurerm_key_vault_access_policy" "aks" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.aks_principal_id

  secret_permissions = ["Get", "List"]
}

output "vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}
