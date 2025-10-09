# GitHub Actions CI/CD Pipeline

This document describes the complete GitHub Actions CI/CD pipeline for AirPuff, providing automated testing, security scanning, and deployment across all environments.

## Overview

The AirPuff CI/CD pipeline provides:

- **Automated Testing**: Backend, frontend, API, and integration tests
- **Code Quality**: Linting, formatting, type checking, and security scanning
- **Deployment Automation**: Automated deployments to dev, staging, and production
- **Monitoring**: Health checks, performance monitoring, and alerting
- **Database Management**: Automated migrations, backups, and data management
- **Emergency Procedures**: Emergency deployment and rollback capabilities

## Workflow Structure

### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to `main` or `dev` branches
- Pull requests to `main` or `dev` branches
- Manual workflow dispatch

**Jobs:**
- **Code Quality & Security**: Black, Flake8, MyPy, Bandit, Safety
- **Backend Tests**: Unit tests with PostgreSQL and Redis
- **Ansible Tests**: Playbook syntax and linting
- **Deploy Dev**: Automatic deployment to development
- **Deploy Staging**: Automatic deployment to staging
- **Deploy Prod**: Manual deployment to production

### 2. Emergency Deployment (`.github/workflows/emergency.yml`)

**Purpose:** Emergency deployments with minimal testing

**Features:**
- Skip all tests for emergency situations
- Direct deployment to any environment
- Emergency notifications
- Reason tracking for audit purposes

### 3. Scheduled Maintenance (`.github/workflows/maintenance.yml`)

**Schedule:** Every Sunday at 2 AM UTC

**Maintenance Types:**
- **Security Updates**: System and package security updates
- **Dependency Updates**: Python package updates
- **System Updates**: OS and system package updates
- **Backup Verification**: Backup integrity checks
- **Performance Check**: Performance monitoring and optimization

### 4. Database Management (`.github/workflows/database.yml`)

**Operations:**
- **Migrate**: Database schema migrations
- **Backup**: Database backup creation
- **Restore**: Database restoration from backups
- **Seed Data**: Initial data population
- **Cleanup**: Old data and log cleanup

### 5. Monitoring & Alerting (`.github/workflows/monitoring.yml`)

**Schedule:** Every 5 minutes

**Monitoring Types:**
- **Health Check**: Service availability monitoring
- **Performance Check**: Response time monitoring
- **Security Check**: Security header and HTTPS verification
- **Backup Check**: Backup status monitoring
- **Log Analysis**: Error pattern analysis

## Environment Configuration

### Development Environment
- **Branch**: `dev`
- **URL**: `http://dev.airpuff.local:8000`
- **Auto-deploy**: Yes (on push)
- **Tests**: Full test suite
- **Security**: Relaxed for development

### Staging Environment
- **Branch**: `main`
- **URL**: `https://staging.airpuff.com:8000`
- **Auto-deploy**: Yes (on push to main)
- **Tests**: Full test suite + security scans
- **Security**: Production-like

### Production Environment
- **Branch**: `main`
- **URL**: `https://airpuff.com:8000`
- **Auto-deploy**: Manual only
- **Tests**: Full test suite + security + performance
- **Security**: Maximum security

## Required Secrets

Configure these secrets in GitHub repository settings:

### Deployment Secrets
- `VAULT_PASSWORD`: Ansible vault password for production
- `SSH_PRIVATE_KEY`: SSH private key for server access
- `ANSIBLE_HOST_KEY_CHECKING`: Set to "False"

### Notification Secrets
- `SLACK_WEBHOOK`: Slack webhook URL for notifications
- `SLACK_CHANNEL`: Default Slack channel for notifications

### API Keys (Optional)
- `FLI_RITE_API_KEY`: Fli-Rite API key
- `CHECKWX_API_KEY`: CheckWX API key
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

## Workflow Usage

### Automatic Deployments

**Development:**
```bash
# Push to dev branch triggers automatic deployment
git push origin dev
```

**Staging:**
```bash
# Push to main branch triggers automatic deployment
git push origin main
```

### Manual Deployments

**Production:**
1. Go to GitHub Actions tab
2. Select "AirPuff CI/CD Pipeline"
3. Click "Run workflow"
4. Select environment: "prod"
5. Click "Run workflow"

**Emergency Deployment:**
1. Go to GitHub Actions tab
2. Select "Emergency Deployment"
3. Click "Run workflow"
4. Select environment and provide reason
5. Click "Run workflow"

### Database Operations

**Migration:**
1. Go to GitHub Actions tab
2. Select "Database Management"
3. Click "Run workflow"
4. Select operation: "migrate"
5. Select environment
6. Click "Run workflow"

**Backup:**
1. Go to GitHub Actions tab
2. Select "Database Management"
3. Click "Run workflow"
4. Select operation: "backup"
5. Select environment
6. Click "Run workflow"

## Testing Strategy

### Code Quality Tests
- **Black**: Code formatting
- **Flake8**: Linting and style
- **MyPy**: Type checking
- **Bandit**: Security scanning
- **Safety**: Dependency vulnerability scanning

### Backend Tests
- **Unit Tests**: Individual component testing
- **Integration Tests**: Database and API integration
- **Performance Tests**: Response time and load testing
- **Security Tests**: Authentication and authorization

### Frontend Tests
- **HTML Validation**: Template validation
- **CSS Validation**: Style sheet validation
- **Accessibility Tests**: WCAG compliance
- **Browser Tests**: Cross-browser compatibility

### API Tests
- **Endpoint Tests**: All API endpoints
- **Authentication Tests**: OAuth and JWT
- **Data Validation Tests**: Request/response validation
- **Error Handling Tests**: Error scenarios

## Deployment Process

### Development Deployment
1. **Code Quality**: Run all quality checks
2. **Backend Tests**: Run unit and integration tests
3. **Ansible Tests**: Validate playbook syntax
4. **Deploy**: Run Ansible playbook
5. **Health Check**: Verify deployment success

### Staging Deployment
1. **Code Quality**: Run all quality checks
2. **Backend Tests**: Run unit and integration tests
3. **Security Scan**: Run security scans
4. **Ansible Tests**: Validate playbook syntax
5. **Deploy**: Run Ansible playbook
6. **Health Check**: Verify deployment success
7. **Smoke Tests**: Run basic functionality tests

### Production Deployment
1. **Code Quality**: Run all quality checks
2. **Backend Tests**: Run unit and integration tests
3. **Security Scan**: Run security scans
4. **Performance Tests**: Run performance tests
5. **Ansible Tests**: Validate playbook syntax
6. **Deploy**: Run Ansible playbook with vault
7. **Health Check**: Verify deployment success
8. **Smoke Tests**: Run basic functionality tests

## Monitoring and Alerting

### Health Monitoring
- **Service Availability**: HTTP status checks
- **Response Times**: Performance monitoring
- **Error Rates**: Error tracking
- **Resource Usage**: CPU, memory, disk monitoring

### Security Monitoring
- **HTTPS Verification**: SSL certificate checks
- **Security Headers**: Header validation
- **Vulnerability Scanning**: Regular security scans
- **Access Logs**: Unauthorized access detection

### Backup Monitoring
- **Backup Status**: Backup completion verification
- **Backup Integrity**: Backup file validation
- **Retention Policy**: Backup retention compliance
- **Restore Testing**: Periodic restore tests

## Troubleshooting

### Common Issues

**Deployment Failures:**
1. Check Ansible logs in GitHub Actions
2. Verify server connectivity
3. Check SSH key permissions
4. Verify vault password

**Test Failures:**
1. Check test logs in GitHub Actions
2. Verify database connectivity
3. Check environment variables
4. Verify test data

**Health Check Failures:**
1. Check service status on server
2. Verify port accessibility
3. Check firewall rules
4. Verify DNS resolution

### Debug Commands

**Local Testing:**
```bash
# Run tests locally
cd backend
pytest tests/ -v

# Run Ansible locally
ansible-playbook ansible/playbooks/deploy.yml --check

# Test deployment script
./deploy.sh -t airpuff_dev -e dev -d
```

**Server Debugging:**
```bash
# Check service status
sudo systemctl status airpuff-app

# Check logs
sudo journalctl -u airpuff-app -f

# Check database
sudo -u postgres psql -d airpuff
```

## Best Practices

### Code Quality
- Run tests locally before pushing
- Use meaningful commit messages
- Keep pull requests small and focused
- Review code thoroughly before merging

### Deployment
- Test in development first
- Use staging for final validation
- Deploy to production during low-traffic periods
- Monitor deployments closely

### Security
- Keep dependencies updated
- Use strong passwords and keys
- Enable all security features
- Monitor for vulnerabilities

### Monitoring
- Set up proper alerting
- Monitor key metrics
- Regular health checks
- Backup verification

## Support

For issues or questions:

1. Check GitHub Actions logs
2. Review the troubleshooting section
3. Check server logs and status
4. Contact the development team

The GitHub Actions CI/CD pipeline provides a robust, automated way to test, deploy, and monitor AirPuff across all environments while maintaining high quality and security standards.
