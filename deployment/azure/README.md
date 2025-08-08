# Azure Deployment Guide for Crypto Dashboard

This guide will help you deploy the Crypto Dashboard to Azure with enterprise-grade infrastructure suitable for hedge fund operations.

## 🎯 Overview

This deployment creates a production-ready infrastructure with:

- **High Availability**: Multi-zone deployment with load balancing
- **Security**: Network security groups, Key Vault for secrets, encrypted storage
- **Monitoring**: Application Insights for real-time monitoring and alerting
- **Scalability**: Auto-scaling App Service with container registry
- **Data Integrity**: PostgreSQL with backup and Redis for caching
- **Compliance**: Financial-grade security and audit logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Azure Load    │    │   App Service   │    │   Container     │
│   Balancer      │───▶│   (Linux)       │───▶│   Registry      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Virtual       │
                       │   Network       │
                       │   (VNet)        │
                       └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
            ┌─────────────┐ ┌─────────┐ ┌─────────┐
            │ PostgreSQL  │ │  Redis  │ │ Storage │
            │ Flexible    │ │  Cache  │ │ Account │
            │ Server      │ │         │ │         │
            └─────────────┘ └─────────┘ └─────────┘
```

## 📋 Prerequisites

1. **Azure CLI** - [Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Terraform** - [Install Guide](https://www.terraform.io/downloads.html)
3. **Docker** - [Install Guide](https://docs.docker.com/get-docker/)
4. **Azure Subscription** - Active subscription with billing enabled

## 🚀 Quick Deployment

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/danielchancfa/crypto-dashboard.git
cd cryptoDashboard

# Copy and configure variables
cp deployment/azure/terraform.tfvars.example deployment/azure/terraform.tfvars
```

### Step 2: Configure Variables

Edit `deployment/azure/terraform.tfvars` with your values:

```hcl
environment = "prod"
location    = "East US"

# Database Configuration
db_username = "crypto_admin"
db_password = "your_secure_password_here"

# API Keys (Get these from respective exchanges)
binance_api_key    = "your_binance_api_key"
binance_secret_key = "your_binance_secret_key"
coinbase_api_key   = "your_coinbase_api_key"
coinbase_secret_key = "your_coinbase_secret_key"
coingecko_api_key  = "your_coingecko_api_key"
```

### Step 3: Run Deployment

```bash
# Make script executable (if not already)
chmod +x deployment/azure/deploy.sh

# Run deployment
./deployment/azure/deploy.sh
```

## 🔧 Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. Login to Azure

```bash
az login
az account set --subscription "your-subscription-id"
```

### 2. Create Terraform Backend

```bash
# Create resource group for Terraform state
az group create \
    --name "crypto-dashboard-terraform-rg" \
    --location "East US" \
    --tags "Project=crypto-dashboard" "Owner=data-analytics-team"

# Create storage account
az storage account create \
    --name "cryptodashboardtfstate" \
    --resource-group "crypto-dashboard-terraform-rg" \
    --location "East US" \
    --sku Standard_LRS \
    --encryption-services blob

# Create blob container
az storage container create \
    --name "tfstate" \
    --account-name "cryptodashboardtfstate"
```

### 3. Deploy Infrastructure

```bash
cd deployment/azure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply deployment
terraform apply tfplan
```

### 4. Build and Deploy Application

```bash
# Login to Azure Container Registry
az acr login --name $(terraform output -raw container_registry_url | cut -d'.' -f1)

# Build and push Docker image
docker build -t $(terraform output -raw container_registry_url)/crypto-dashboard:latest ..
docker push $(terraform output -raw container_registry_url)/crypto-dashboard:latest
```

## 🔒 Security Features

### Network Security
- **VNet Isolation**: All resources deployed in private subnets
- **NSG Rules**: Restrictive firewall rules for database access
- **Service Endpoints**: Secure database connectivity

### Data Protection
- **Encryption at Rest**: All storage and databases encrypted
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Key Vault**: Centralized secret management

### Access Control
- **RBAC**: Role-based access control for Azure resources
- **Managed Identities**: Secure service-to-service authentication
- **Audit Logging**: Comprehensive activity logging

## 📊 Monitoring and Alerting

### Application Insights
- **Real-time Monitoring**: Application performance and availability
- **Custom Metrics**: Business-specific KPIs and alerts
- **Error Tracking**: Automatic error detection and reporting

### Azure Monitor
- **Infrastructure Monitoring**: Resource health and performance
- **Log Analytics**: Centralized logging and analysis
- **Alert Rules**: Automated alerting for critical issues

## 🔄 CI/CD Pipeline

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and Push Docker Image
      run: |
        az acr login --name ${{ secrets.ACR_NAME }}
        docker build -t ${{ secrets.ACR_NAME }}.azurecr.io/crypto-dashboard:${{ github.sha }} .
        docker push ${{ secrets.ACR_NAME }}.azurecr.io/crypto-dashboard:${{ github.sha }}
    
    - name: Deploy Infrastructure
      run: |
        cd deployment/azure
        terraform init
        terraform apply -auto-approve
```

## 💰 Cost Optimization

### Resource Sizing
- **Development**: Use Basic SKUs for cost savings
- **Production**: Use Standard/Premium SKUs for performance
- **Auto-scaling**: Configure based on demand patterns

### Cost Monitoring
- **Azure Cost Management**: Track and optimize spending
- **Resource Tags**: Organize resources for cost allocation
- **Budget Alerts**: Set spending limits and notifications

## 🛠️ Troubleshooting

### Common Issues

1. **Terraform State Lock**
   ```bash
   terraform force-unlock <lock-id>
   ```

2. **Container Registry Access**
   ```bash
   az acr login --name <registry-name>
   ```

3. **Database Connection Issues**
   - Check NSG rules
   - Verify connection string format
   - Ensure SSL is enabled

### Logs and Debugging

```bash
# View App Service logs
az webapp log tail --name <app-name> --resource-group <rg-name>

# View Application Insights
az monitor app-insights query --app <app-insights-name> --analytics-query "requests | limit 10"
```

## 📈 Scaling and Performance

### Horizontal Scaling
- **App Service**: Configure auto-scaling rules
- **Database**: Use read replicas for read-heavy workloads
- **Cache**: Scale Redis based on memory requirements

### Performance Optimization
- **CDN**: Enable Azure CDN for static content
- **Caching**: Implement Redis caching strategies
- **Database**: Optimize queries and indexes

## 🔄 Backup and Disaster Recovery

### Backup Strategy
- **Database**: Automated daily backups with 7-day retention
- **Application**: Container images stored in ACR
- **Configuration**: Terraform state and variables versioned

### Disaster Recovery
- **Multi-region**: Deploy to secondary region for RTO/RPO
- **Data Replication**: Configure cross-region replication
- **Failover**: Automated failover procedures

## 📞 Support

For deployment issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Azure documentation for specific services
3. Open an issue in the GitHub repository

## 📝 License

This deployment configuration is part of the Crypto Dashboard project and follows the same MIT license. 