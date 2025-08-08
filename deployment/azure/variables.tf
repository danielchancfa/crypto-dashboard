variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "db_username" {
  description = "PostgreSQL database administrator username"
  type        = string
  default     = "crypto_admin"
}

variable "db_password" {
  description = "PostgreSQL database administrator password"
  type        = string
  sensitive   = true
}

variable "binance_api_key" {
  description = "Binance API key"
  type        = string
  sensitive   = true
}

variable "binance_secret_key" {
  description = "Binance secret key"
  type        = string
  sensitive   = true
}

variable "coinbase_api_key" {
  description = "Coinbase API key"
  type        = string
  sensitive   = true
}

variable "coinbase_secret_key" {
  description = "Coinbase secret key"
  type        = string
  sensitive   = true
}

variable "coingecko_api_key" {
  description = "CoinGecko API key"
  type        = string
  sensitive   = true
}

variable "app_service_plan_sku" {
  description = "App Service Plan SKU"
  type        = string
  default     = "P1v2"
}

variable "postgresql_sku" {
  description = "PostgreSQL Flexible Server SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "redis_sku" {
  description = "Redis Cache SKU"
  type        = string
  default     = "Basic"
}

variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "container_registry_sku" {
  description = "Container Registry SKU"
  type        = string
  default     = "Basic"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "crypto-dashboard"
    Owner       = "data-analytics-team"
    CostCenter  = "trading-operations"
    Compliance  = "financial-data"
  }
} 