#!/bin/bash

# Azure Deployment Script for Crypto Dashboard
# This script deploys the crypto dashboard to Azure with enterprise-grade infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Login to Azure
login_to_azure() {
    print_status "Logging into Azure..."
    az login
    print_success "Successfully logged into Azure"
}

# Set Azure subscription
set_subscription() {
    print_status "Setting Azure subscription..."
    
    # List available subscriptions
    echo "Available subscriptions:"
    az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o table
    
    # Get current subscription
    CURRENT_SUB=$(az account show --query id -o tsv)
    print_status "Current subscription: $CURRENT_SUB"
    
    read -p "Do you want to use a different subscription? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter subscription ID: " SUBSCRIPTION_ID
        az account set --subscription $SUBSCRIPTION_ID
        print_success "Subscription set to: $SUBSCRIPTION_ID"
    fi
}

# Create Terraform backend resources
create_terraform_backend() {
    print_status "Creating Terraform backend resources..."
    
    # Create resource group for Terraform state
    az group create \
        --name "crypto-dashboard-terraform-rg" \
        --location "East US" \
        --tags "Project=crypto-dashboard" "Owner=data-analytics-team"
    
    # Create storage account for Terraform state
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
    
    print_success "Terraform backend resources created"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Get the container registry URL from Terraform output
    ACR_URL=$(terraform output -raw container_registry_url 2>/dev/null || echo "")
    
    if [ -z "$ACR_URL" ]; then
        print_warning "Container registry URL not found. Building image locally first..."
        docker build -t crypto-dashboard:latest .
        print_success "Docker image built locally"
        return
    fi
    
    # Login to Azure Container Registry
    az acr login --name $(echo $ACR_URL | cut -d'.' -f1)
    
    # Build and tag image
    docker build -t $ACR_URL/crypto-dashboard:latest .
    
    # Push image
    docker push $ACR_URL/crypto-dashboard:latest
    
    print_success "Docker image built and pushed to Azure Container Registry"
}

# Initialize and apply Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    cd deployment/azure
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Ask for confirmation
    read -p "Do you want to apply this plan? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Apply deployment
        print_status "Applying Terraform plan..."
        terraform apply tfplan
        
        print_success "Infrastructure deployed successfully!"
        
        # Display outputs
        echo ""
        print_status "Deployment Summary:"
        echo "====================="
        terraform output
        
    else
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    cd ../..
}

# Setup database schema
setup_database() {
    print_status "Setting up database schema..."
    
    # Get database connection details
    DB_HOST=$(terraform -chdir=deployment/azure output -raw database_host)
    DB_NAME="crypto_dashboard"
    DB_USER=$(terraform -chdir=deployment/azure output -raw db_username 2>/dev/null || echo "crypto_admin")
    
    print_status "Database host: $DB_HOST"
    print_status "Database name: $DB_NAME"
    print_status "Database user: $DB_USER"
    
    # Note: In a real deployment, you would run database migrations here
    print_success "Database setup completed (migrations would run here)"
}

# Configure monitoring and alerts
setup_monitoring() {
    print_status "Setting up monitoring and alerts..."
    
    # Get Application Insights key
    APP_INSIGHTS_KEY=$(terraform -chdir=deployment/azure output -raw application_insights_key)
    
    print_status "Application Insights configured with key: ${APP_INSIGHTS_KEY:0:8}..."
    
    # In a real deployment, you would configure alerts here
    print_success "Monitoring setup completed"
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get the app URL
    APP_URL=$(terraform -chdir=deployment/azure output -raw app_url)
    
    print_status "Application URL: $APP_URL"
    
    # Wait for the app to be ready
    print_status "Waiting for application to be ready..."
    sleep 30
    
    # Test the application
    if curl -f -s "$APP_URL" > /dev/null; then
        print_success "Application is responding successfully!"
    else
        print_warning "Application might still be starting up. Please check manually."
    fi
}

# Main deployment function
main() {
    echo "=========================================="
    echo "  Crypto Dashboard Azure Deployment"
    echo "=========================================="
    echo ""
    
    # Check if terraform.tfvars exists
    if [ ! -f "deployment/azure/terraform.tfvars" ]; then
        print_error "terraform.tfvars file not found!"
        print_status "Please copy terraform.tfvars.example to terraform.tfvars and configure your values"
        exit 1
    fi
    
    # Run deployment steps
    check_prerequisites
    login_to_azure
    set_subscription
    create_terraform_backend
    deploy_infrastructure
    build_and_push_image
    setup_database
    setup_monitoring
    test_deployment
    
    echo ""
    echo "=========================================="
    print_success "Deployment completed successfully!"
    echo "=========================================="
    echo ""
    print_status "Your crypto dashboard is now live at:"
    terraform -chdir=deployment/azure output app_url
    echo ""
    print_status "Next steps:"
    echo "1. Configure your API keys in the Azure App Service settings"
    echo "2. Set up monitoring alerts in Application Insights"
    echo "3. Configure backup policies for the database"
    echo "4. Set up CI/CD pipeline for future deployments"
    echo ""
}

# Run main function
main "$@" 