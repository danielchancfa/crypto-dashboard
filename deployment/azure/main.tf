terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    resource_group_name  = "crypto-dashboard-terraform-rg"
    storage_account_name = "cryptodashboardtfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "crypto-dashboard-${var.environment}-rg"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
    Owner       = "data-analytics-team"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "crypto-dashboard-vnet"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  address_space       = ["10.0.0.0/16"]

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Subnets
resource "azurerm_subnet" "app" {
  name                 = "app-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "database" {
  name                 = "database-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
  
  service_endpoints = ["Microsoft.Sql"]
}

resource "azurerm_subnet" "redis" {
  name                 = "redis-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
}

# Network Security Groups
resource "azurerm_network_security_group" "app" {
  name                = "app-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowStreamlit"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8501"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

resource "azurerm_network_security_group" "database" {
  name                = "database-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowPostgreSQL"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "10.0.1.0/24"
    destination_address_prefix = "*"
  }

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Associate NSGs with subnets
resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = azurerm_subnet.database.id
  network_security_group_id = azurerm_network_security_group.database.id
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "crypto-dashboard-db-${var.environment}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "14"
  administrator_login    = var.db_username
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  zone                   = "1"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  depends_on = [azurerm_subnet_network_security_group_association.database]

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "crypto_dashboard"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Redis Cache
resource "azurerm_redis_cache" "main" {
  name                = "crypto-dashboard-redis-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 0
  family              = "C"
  sku_name            = "Basic"
  enable_non_ssl_port = false

  redis_configuration {
    maxmemory_reserved = 2
    maxmemory_delta    = 2
    maxmemory_policy   = "volatile-lru"
  }

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Storage Account for data and logs
resource "azurerm_storage_account" "main" {
  name                     = "cryptodashboard${var.environment}${random_string.storage.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  blob_properties {
    versioning_enabled = true
  }

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "logs" {
  name                  = "logs"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = "cryptodashboard${var.environment}${random_string.acr.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "crypto-dashboard-plan-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "P1v2"

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# App Service
resource "azurerm_linux_web_app" "main" {
  name                = "crypto-dashboard-${var.environment}-${random_string.app.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker {
        registry_url = azurerm_container_registry.main.login_server
        image_name   = "crypto-dashboard:latest"
      }
    }

    always_on = true

    application_stack {
      python_version = "3.9"
    }
  }

  app_settings = {
    "WEBSITES_PORT"                    = "8501"
    "DATABASE_URL"                     = "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/crypto_dashboard"
    "REDIS_URL"                        = "redis://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:6380/0"
    "STORAGE_ACCOUNT_NAME"             = azurerm_storage_account.main.name
    "STORAGE_ACCOUNT_KEY"              = azurerm_storage_account.main.primary_access_key
    "BINANCE_API_KEY"                  = var.binance_api_key
    "BINANCE_SECRET_KEY"               = var.binance_secret_key
    "COINBASE_API_KEY"                 = var.coinbase_api_key
    "COINBASE_SECRET_KEY"              = var.coinbase_secret_key
    "COINGECKO_API_KEY"                = var.coingecko_api_key
    "DOCKER_ENABLE_CI"                 = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "crypto-dashboard-insights-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Key Vault for secrets
resource "azurerm_key_vault" "main" {
  name                        = "crypto-dashboard-kv-${var.environment}-${random_string.kv.result}"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"

  tags = {
    Environment = var.environment
    Project     = "crypto-dashboard"
  }
}

# Random strings for unique names
resource "random_string" "storage" {
  length  = 8
  special = false
  upper   = false
}

resource "random_string" "acr" {
  length  = 8
  special = false
  upper   = false
}

resource "random_string" "app" {
  length  = 8
  special = false
  upper   = false
}

resource "random_string" "kv" {
  length  = 8
  special = false
  upper   = false
}

# Data sources
data "azurerm_client_config" "current" {}

# Outputs
output "app_url" {
  description = "URL of the deployed application"
  value       = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "database_host" {
  description = "PostgreSQL server hostname"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_host" {
  description = "Redis cache hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "container_registry_url" {
  description = "Container registry URL"
  value       = azurerm_container_registry.main.login_server
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
} 