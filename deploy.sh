#!/bin/bash
# AirPuff Ansible Deployment Script
# This script automates the deployment of AirPuff using Ansible

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TARGET="airpuff_dev"
ENVIRONMENT="dev"
VERBOSE=""
DRY_RUN=""
VAULT_PASSWORD=""
SKIP_TAGS=""
ONLY_TAGS=""

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

# Function to show usage
show_usage() {
    cat << EOF
AirPuff Ansible Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --target TARGET        Target environment (airpuff_dev, airpuff_prod, airpuff_staging)
    -e, --environment ENV     Environment name (dev, prod, staging)
    -v, --verbose             Enable verbose output
    -d, --dry-run             Perform a dry run (check mode)
    -p, --vault-password      Vault password for encrypted variables
    -s, --skip-tags TAGS      Skip specified tags (comma-separated)
    -o, --only-tags TAGS      Only run specified tags (comma-separated)
    -h, --help                Show this help message

EXAMPLES:
    # Deploy to development
    $0 -t airpuff_dev -e dev

    # Deploy to production with vault password
    $0 -t airpuff_prod -e prod -p "myvaultpassword"

    # Dry run deployment
    $0 -t airpuff_prod -e prod -d

    # Deploy only system setup
    $0 -t airpuff_dev -e dev -o "system,setup"

    # Skip database setup
    $0 -t airpuff_prod -e prod -s "database,postgresql"

ENVIRONMENTS:
    airpuff_dev      Development environment
    airpuff_prod     Production environment  
    airpuff_staging  Staging environment

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -d|--dry-run)
            DRY_RUN="--check"
            shift
            ;;
        -p|--vault-password)
            VAULT_PASSWORD="$2"
            shift 2
            ;;
        -s|--skip-tags)
            SKIP_TAGS="--skip-tags $2"
            shift 2
            ;;
        -o|--only-tags)
            ONLY_TAGS="--tags $2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate target
case $TARGET in
    airpuff_dev|airpuff_prod|airpuff_staging)
        ;;
    *)
        print_error "Invalid target: $TARGET"
        print_error "Valid targets: airpuff_dev, airpuff_prod, airpuff_staging"
        exit 1
        ;;
esac

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    print_error "Ansible is not installed. Please install Ansible first."
    exit 1
fi

# Check if inventory file exists
INVENTORY_FILE="ansible/inventory/hosts.yml"
if [[ ! -f "$INVENTORY_FILE" ]]; then
    print_error "Inventory file not found: $INVENTORY_FILE"
    exit 1
fi

# Check if playbook exists
PLAYBOOK_FILE="ansible/playbooks/deploy.yml"
if [[ ! -f "$PLAYBOOK_FILE" ]]; then
    print_error "Playbook file not found: $PLAYBOOK_FILE"
    exit 1
fi

# Build Ansible command
ANSIBLE_CMD="ansible-playbook"
ANSIBLE_CMD="$ANSIBLE_CMD -i $INVENTORY_FILE"
ANSIBLE_CMD="$ANSIBLE_CMD $PLAYBOOK_FILE"
ANSIBLE_CMD="$ANSIBLE_CMD -e target=$TARGET"
ANSIBLE_CMD="$ANSIBLE_CMD -e environment=$ENVIRONMENT"

if [[ -n "$VERBOSE" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD $VERBOSE"
fi

if [[ -n "$DRY_RUN" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD $DRY_RUN"
fi

if [[ -n "$VAULT_PASSWORD" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD --vault-password-file <(echo '$VAULT_PASSWORD')"
fi

if [[ -n "$SKIP_TAGS" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD $SKIP_TAGS"
fi

if [[ -n "$ONLY_TAGS" ]]; then
    ANSIBLE_CMD="$ANSIBLE_CMD $ONLY_TAGS"
fi

# Display deployment information
print_status "Starting AirPuff deployment..."
print_status "Target: $TARGET"
print_status "Environment: $ENVIRONMENT"
print_status "Inventory: $INVENTORY_FILE"
print_status "Playbook: $PLAYBOOK_FILE"

if [[ -n "$DRY_RUN" ]]; then
    print_warning "DRY RUN MODE - No changes will be made"
fi

if [[ -n "$VERBOSE" ]]; then
    print_status "Verbose mode enabled"
fi

if [[ -n "$SKIP_TAGS" ]]; then
    print_status "Skipping tags: $SKIP_TAGS"
fi

if [[ -n "$ONLY_TAGS" ]]; then
    print_status "Only running tags: $ONLY_TAGS"
fi

# Confirm deployment
if [[ "$TARGET" == "airpuff_prod" && -z "$DRY_RUN" ]]; then
    print_warning "You are about to deploy to PRODUCTION!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        print_error "Deployment cancelled"
        exit 1
    fi
fi

# Run the deployment
print_status "Executing Ansible playbook..."
print_status "Command: $ANSIBLE_CMD"

if eval "$ANSIBLE_CMD"; then
    print_success "AirPuff deployment completed successfully!"
    print_success "Target: $TARGET"
    print_success "Environment: $ENVIRONMENT"
    
    # Display service URLs
    case $TARGET in
        airpuff_dev)
            print_status "Application URL: http://dev.airpuff.local:8000"
            print_status "Grafana URL: http://dev.airpuff.local:3000"
            ;;
        airpuff_prod)
            print_status "Application URL: https://airpuff.com:8000"
            print_status "Grafana URL: https://airpuff.com:3000"
            ;;
        airpuff_staging)
            print_status "Application URL: https://staging.airpuff.com:8000"
            print_status "Grafana URL: https://staging.airpuff.com:3000"
            ;;
    esac
    
    print_status "Logs: /var/log/airpuff/"
    print_status "Configuration: /opt/airpuff/"
    
else
    print_error "AirPuff deployment failed!"
    print_error "Check the Ansible output above for details"
    exit 1
fi
