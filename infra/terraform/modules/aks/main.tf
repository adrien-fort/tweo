# AKS cluster — single node pool to start, autoscale enabled.
# Uses system-assigned Managed Identity so Ansible/Key Vault access
# is granted without storing credentials.

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project"              { type = string }
variable "environment"          { type = string }
variable "tags"                 { type = map(string) }

resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project}-${var.environment}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project}-${var.environment}"

  default_node_pool {
    name                = "system"
    node_count          = 1
    vm_size             = "Standard_B2s"
    enable_auto_scaling = true
    min_count           = 1
    max_count           = 3
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

output "principal_id" {
  value = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}
