# AirPuff Ansible Deployment Guide

This guide covers the complete Ansible-based deployment system for AirPuff, designed for bare metal deployment without NGINX, UFW, or Mac-side iMessage services.

## Overview

The AirPuff Ansible deployment system provides:

- **Complete Infrastructure**: System setup, Python, PostgreSQL, Redis, Docker, Grafana
- **Application Deployment**: FastAPI app with all services and systemd integration
- **Environment Management**: Development, staging, and production configurations
- **Security**: Fail2ban, system limits, kernel tuning
- **Monitoring**: Log rotation, system monitoring, health checks
- **Backup**: Automated backup system (production only)

## Architecture

### Components Deployed

1. **System Layer**
   - Ubuntu/Debian system optimization
   - NTP time synchronization
   - Fail2ban security
   - System limits and kernel tuning
   - Log rotation

2. **Database Layer**
   - PostgreSQL 15 with TimescaleDB extension
   - Optimized configuration for time-series data
   - Automated hypertable creation
   - Data retention policies

3. **Cache Layer**
   - Redis 7.0 for caching and sessions
   - Optimized configuration

4. **Application Layer**
   - Python 3.11 with virtual environment
   - FastAPI application with all services
   - Systemd services and timers
   - WebSocket support

5. **Visualization Layer**
   - Grafana 10.2.0 with TimescaleDB integration
   - Pre-configured dashboards
   - Weather data visualization

6. **Container Layer**
   - Docker 24.0 for containerized services
   - Docker Compose 2.21.0 for orchestration

## Quick Start

### Prerequisites

- **Control Machine**: Ubuntu/Debian with Ansible installed
- **Target Machines**: Ubuntu 20.04+ or Debian 11+
- **SSH Access**: Key-based authentication to target machines
- **Sudo Access**: Deploy user with sudo privileges

### Installation

1. **Install Ansible**:
   ```bash
   sudo apt update
   sudo apt install ansible
   ```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/your-org/airpuff.git
   cd airpuff
   ```

3. **Configure Inventory**:
   ```bash
   # Edit ansible/inventory/hosts.yml
   # Update IP addresses and SSH keys
   ```

4. **Deploy**:
   ```bash
   ./deploy.sh -t airpuff_dev -e dev
   ```

## Configuration

### Inventory Configuration

Edit `ansible/inventory/hosts.yml`:

```yaml
all:
  children:
    airpuff_dev:
      hosts:
        airpuff-dev:
          ansible_host: 192.168.1.100
          ansible_user: deploy
          ansible_ssh_private_key_file: ~/.ssh/airpuff_dev_key
          environment: development
          domain: dev.airpuff.local
```

### Environment Variables

#### Development (`ansible/group_vars/airpuff_dev.yml`)
```yaml
environment: "development"
debug: true
log_level: "DEBUG"
airpuff_secret_key: "dev-secret-key-change-in-production"
```

#### Production (`ansible/group_vars/airpuff_prod.yml`)
```yaml
environment: "production"
debug: false
log_level: "INFO"
airpuff_secret_key: "{{ vault_airpuff_secret_key }}"
```

### Vault Configuration

For production secrets, use Ansible Vault:

```bash
# Create vault file
ansible-vault create ansible/group_vars/airpuff_prod/vault.yml

# Edit vault file
ansible-vault edit ansible/group_vars/airpuff_prod/vault.yml
```

Example vault content:
```yaml
vault_airpuff_secret_key: "your-production-secret-key"
vault_postgresql_password: "your-db-password"
vault_grafana_password: "your-grafana-password"
vault_fli_rite_api_key: "your-fli-rite-api-key"
vault_google_client_id: "your-google-client-id"
vault_google_client_secret: "your-google-client-secret"
```

## Deployment Commands

### Basic Deployment

```bash
# Development
./deploy.sh -t airpuff_dev -e dev

# Production
./deploy.sh -t airpuff_prod -e prod -p "vault-password"

# Staging
./deploy.sh -t airpuff_staging -e staging
```

### Advanced Options

```bash
# Dry run (check mode)
./deploy.sh -t airpuff_prod -e prod -d

# Verbose output
./deploy.sh -t airpuff_dev -e dev -v

# Skip specific tags
./deploy.sh -t airpuff_prod -e prod -s "backup,monitoring"

# Only run specific tags
./deploy.sh -t airpuff_dev -e dev -o "system,setup"
```

### Manual Ansible Commands

```bash
# Run specific playbook
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -t airpuff_dev

# Run with vault password
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml \
  --vault-password-file <(echo "vault-password") -t airpuff_prod

# Check mode
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml \
  --check -t airpuff_dev
```

## Roles Overview

### System Setup (`system_setup`)
- Package installation and updates
- User and directory creation
- NTP configuration
- Fail2ban security
- System limits and kernel tuning
- Log rotation

### Python Setup (`python_setup`)
- Python 3.11 installation
- Virtual environment creation
- Package installation
- Requirements management

### PostgreSQL Setup (`postgresql_setup`)
- PostgreSQL 15 installation
- TimescaleDB extension
- Database and user creation
- Configuration optimization
- Hypertable setup

### Redis Setup (`redis_setup`)
- Redis 7.0 installation
- Configuration optimization
- Service management

### Docker Setup (`docker_setup`)
- Docker 24.0 installation
- Docker Compose 2.21.0
- Service configuration

### Grafana Setup (`grafana_setup`)
- Grafana 10.2.0 installation
- TimescaleDB datasource configuration
- Dashboard provisioning
- User management

### AirPuff App (`airpuff_app`)
- Application deployment
- Configuration management
- Database migrations
- Systemd services
- Static files

### SystemD Services (`systemd_services`)
- Application service
- Weather data timer
- iMessage timer
- Service management

### Monitoring Setup (`monitoring_setup`)
- System monitoring
- Log management
- Health checks
- Performance monitoring

### Backup Setup (`backup_setup`)
- Automated backups
- Database dumps
- File system backups
- S3 integration (production)

## Service Management

### Systemd Services

```bash
# Application service
sudo systemctl status airpuff-app
sudo systemctl restart airpuff-app
sudo systemctl logs airpuff-app

# Weather data timer
sudo systemctl status airpuff-weather.timer
sudo systemctl list-timers airpuff-weather.timer

# iMessage timer
sudo systemctl status airpuff-imessage.timer
sudo systemctl list-timers airpuff-imessage.timer
```

### Service URLs

- **Application**: `http://domain:8000`
- **Grafana**: `http://domain:3000`
- **API Documentation**: `http://domain:8000/api/docs`
- **Health Check**: `http://domain:8000/health`

### Log Locations

- **Application**: `/var/log/airpuff/`
- **System**: `/var/log/syslog`
- **PostgreSQL**: `/var/log/postgresql/`
- **Grafana**: `/var/log/grafana/`

## Security Considerations

### What's NOT Configured

As requested, the following are **NOT** configured by this playbook:

1. **NGINX**: Reverse proxy configuration (managed separately)
2. **UFW**: Firewall configuration (not enabled)
3. **Mac iMessage Service**: Client-side service (installed separately)

### Security Features Included

1. **Fail2ban**: Intrusion prevention
2. **System Limits**: Resource protection
3. **User Isolation**: Non-root application user
4. **Service Security**: systemd security settings
5. **Log Rotation**: Disk space management

### Production Security

For production deployments:

1. **Use Vault**: Encrypt sensitive variables
2. **SSH Keys**: Key-based authentication only
3. **Regular Updates**: Keep system packages updated
4. **Monitor Logs**: Regular log analysis
5. **Backup Verification**: Test backup restoration

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Test SSH connection
   ssh -i ~/.ssh/airpuff_dev_key deploy@192.168.1.100
   
   # Check SSH key permissions
   chmod 600 ~/.ssh/airpuff_dev_key
   ```

2. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check database connectivity
   psql -h localhost -U airpuff -d airpuff
   ```

3. **Application Not Starting**
   ```bash
   # Check application logs
   sudo journalctl -u airpuff-app -f
   
   # Check service status
   sudo systemctl status airpuff-app
   ```

4. **Grafana Not Accessible**
   ```bash
   # Check Grafana status
   sudo systemctl status grafana-server
   
   # Check port accessibility
   netstat -tlnp | grep 3000
   ```

### Debug Commands

```bash
# Run with verbose output
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -vvv

# Check specific host
ansible airpuff-dev -i ansible/inventory/hosts.yml -m ping

# Run specific task
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml \
  --tags "postgresql" --limit airpuff-dev
```

## Maintenance

### Regular Tasks

1. **System Updates**:
   ```bash
   ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/update.yml
   ```

2. **Backup Verification**:
   ```bash
   ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/backup-test.yml
   ```

3. **Log Rotation**:
   ```bash
   sudo logrotate -f /etc/logrotate.d/airpuff
   ```

### Monitoring

1. **Service Health**:
   ```bash
   curl http://domain:8000/health
   curl http://domain:8000/api/v1/health
   ```

2. **Database Health**:
   ```bash
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

3. **System Resources**:
   ```bash
   htop
   df -h
   free -h
   ```

## Customization

### Adding New Roles

1. Create role directory:
   ```bash
   mkdir -p ansible/roles/new_role/{tasks,handlers,templates,files,vars,defaults,meta}
   ```

2. Add to playbook:
   ```yaml
   roles:
     - role: new_role
       tags: [new_role]
   ```

### Custom Variables

Add to `ansible/group_vars/all.yml`:
```yaml
custom_variable: "value"
```

### Custom Templates

Create templates in `ansible/roles/role_name/templates/`:
```jinja2
# Custom template
{{ custom_variable }}
```

## Support

For issues or questions:

1. Check the logs first
2. Review the Ansible output
3. Test individual components
4. Check the troubleshooting section
5. Contact the development team

The Ansible deployment system provides a robust, automated way to deploy AirPuff across different environments while maintaining consistency and reliability.
