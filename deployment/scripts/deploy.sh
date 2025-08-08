#!/bin/bash

# Crypto Dashboard Deployment Script
# This script deploys the crypto dashboard to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="crypto-dashboard"
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="crypto-dashboard"
CLUSTER_NAME="crypto-dashboard-cluster"
SERVICE_NAME="crypto-dashboard-service"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists terraform; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Build and push Docker image
build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"
    
    # Login to ECR
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}
    
    # Build Docker image
    docker build -t ${ECR_REPOSITORY_NAME} .
    
    # Tag image
    docker tag ${ECR_REPOSITORY_NAME}:latest ${ECR_REPOSITORY_URI}:latest
    
    # Push image
    docker push ${ECR_REPOSITORY_URI}:latest
    
    print_success "Docker image built and pushed successfully"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    cd deployment/terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -out=tfplan
    
    # Apply deployment
    terraform apply tfplan
    
    # Get outputs
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    ECR_REPOSITORY_URL=$(terraform output -raw ecr_repository_url)
    
    cd ../..
    
    print_success "Infrastructure deployed successfully"
    print_status "Load Balancer DNS: ${ALB_DNS_NAME}"
    print_status "Database Endpoint: ${DATABASE_ENDPOINT}"
    print_status "Redis Endpoint: ${REDIS_ENDPOINT}"
    print_status "ECR Repository: ${ECR_REPOSITORY_URL}"
}

# Update ECS service
update_ecs_service() {
    print_status "Updating ECS service..."
    
    # Force new deployment
    aws ecs update-service \
        --cluster ${CLUSTER_NAME} \
        --service ${SERVICE_NAME} \
        --force-new-deployment \
        --region ${AWS_REGION}
    
    # Wait for service to be stable
    print_status "Waiting for service to be stable..."
    aws ecs wait services-stable \
        --cluster ${CLUSTER_NAME} \
        --services ${SERVICE_NAME} \
        --region ${AWS_REGION}
    
    print_success "ECS service updated successfully"
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Get ALB DNS name
    ALB_DNS_NAME=$(cd deployment/terraform && terraform output -raw alb_dns_name && cd ../..)
    
    # Wait for ALB to be ready
    print_status "Waiting for load balancer to be ready..."
    sleep 30
    
    # Test health endpoint
    HEALTH_URL="http://${ALB_DNS_NAME}/_stcore/health"
    
    for i in {1..10}; do
        if curl -f -s ${HEALTH_URL} >/dev/null; then
            print_success "Health check passed"
            return 0
        else
            print_warning "Health check attempt ${i} failed, retrying..."
            sleep 10
        fi
    done
    
    print_error "Health checks failed after 10 attempts"
    return 1
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create CloudWatch dashboard
    aws cloudwatch put-dashboard \
        --dashboard-name "CryptoDashboard" \
        --dashboard-body file://deployment/cloudwatch-dashboard.json \
        --region ${AWS_REGION}
    
    # Create CloudWatch alarms
    aws cloudwatch put-metric-alarm \
        --alarm-name "CryptoDashboard-HighCPU" \
        --alarm-description "High CPU utilization" \
        --metric-name CPUUtilization \
        --namespace AWS/ECS \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --region ${AWS_REGION}
    
    print_success "Monitoring setup completed"
}

# Main deployment function
main() {
    print_status "Starting deployment of Crypto Dashboard..."
    
    # Check prerequisites
    check_prerequisites
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Build and push Docker image
    build_and_push_image
    
    # Update ECS service
    update_ecs_service
    
    # Run health checks
    if run_health_checks; then
        print_success "Deployment completed successfully!"
        
        # Setup monitoring
        setup_monitoring
        
        # Get final URL
        ALB_DNS_NAME=$(cd deployment/terraform && terraform output -raw alb_dns_name && cd ../..)
        print_success "Application is available at: http://${ALB_DNS_NAME}"
    else
        print_error "Deployment failed health checks"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up deployment artifacts..."
    
    # Remove Terraform plan file
    rm -f deployment/terraform/tfplan
    
    print_success "Cleanup completed"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        cleanup
        ;;
    "destroy")
        print_status "Destroying infrastructure..."
        cd deployment/terraform
        terraform destroy -auto-approve
        cd ../..
        print_success "Infrastructure destroyed"
        ;;
    "plan")
        print_status "Planning Terraform deployment..."
        cd deployment/terraform
        terraform plan
        cd ../..
        ;;
    "status")
        print_status "Checking deployment status..."
        aws ecs describe-services \
            --cluster ${CLUSTER_NAME} \
            --services ${SERVICE_NAME} \
            --region ${AWS_REGION} \
            --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}'
        ;;
    *)
        echo "Usage: $0 {deploy|destroy|plan|status}"
        echo "  deploy  - Deploy the application (default)"
        echo "  destroy - Destroy the infrastructure"
        echo "  plan    - Plan Terraform deployment"
        echo "  status  - Check deployment status"
        exit 1
        ;;
esac 