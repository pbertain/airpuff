# AirPuff Production Deployment Guide

Complete guide for deploying AirPuff 2.0 to production with proper port configuration and RRD data handling.

## Overview

This guide covers:
- **Port Configuration**: Production (25080) and Development (25081)
- **GitHub Actions**: Automated deployment to dev and prod environments
- **RRD Data Handling**: Upload and migration of legacy RRD data
- **Environment Separation**: Proper dev/prod environment isolation

## Port Configuration

### Production Environment
- **Port**: 25080
- **Hostname**: www.airpuff.info
- **Directory**: /opt/airpuff
- **Database**: airpuff
- **Redis DB**: 0

### Development Environment
- **Port**: 25081
- **Hostname**: dev.airpuff.info
- **Directory**: /opt/airpuff-dev
- **Database**: airpuff_dev
- **Redis DB**: 1

## GitHub Actions Setup

### Required Secrets

Add these secrets to your GitHub repository:

**Development Secrets:**
- `DEV_SSH_PRIVATE_KEY`: SSH private key for dev deployment

**Production Secrets:**
- `PROD_SSH_PRIVATE_KEY`: SSH private key for prod deployment
- `vault_postgresql_password`: Production database password
- `vault_redis_password`: Production Redis password
- `vault_secret_key`: Production secret key
- `vault_fli_rite_api_key`: Fli-Rite API key
- `vault_checkwx_api_key`: CheckWX API key
- `vault_google_client_id`: Google OAuth client ID
- `vault_google_client_secret`: Google OAuth client secret
- `vault_apple_client_id`: Apple OAuth client ID
- `vault_apple_client_secret`: Apple OAuth client secret
- `vault_imessage_bridge_url`: iMessage bridge URL
- `vault_imessage_api_key`: iMessage API key
- `vault_grafana_password`: Grafana admin password

### Deployment Triggers

**Development Deployment:**
- **Trigger**: Push to `dev` branch
- **Target**: host74.nird.club (web_dev group)
- **Port**: 25081
- **URL**: http://dev.airpuff.info:25081

**Production Deployment:**
- **Trigger**: Push to `main` branch
- **Target**: host74.nird.club (web_prod group)
- **Port**: 25080
- **URL**: http://www.airpuff.info:25080

### Workflow Steps

1. **Code Quality**: Linting, type checking, security scan
2. **Testing**: Unit tests, integration tests, API tests
3. **Deployment**: Ansible deployment to target environment
4. **Health Check**: Verify deployment success
5. **Database Migration**: Run migrations (production only)

## RRD Data Handling

### Option 1: Manual Upload (Recommended)

**Step 1: Upload RRD Data**
```bash
# Use the provided script
./scripts/upload-rrd-data.sh

# Or manually with rsync
rsync -avz --progress /var/airpuff/rrd-data/ deploy@host74.nird.club:/opt/airpuff/rrd-data/
```

**Step 2: Run Migration**
```bash
# Via API
curl -X POST http://www.airpuff.info:25080/api/v1/migration/rrd/migrate

# Via Web Interface
http://www.airpuff.info:25080/migration
```

### Option 2: Ansible Upload

**Enable RRD Data Upload in Ansible:**
```bash
# Deploy with RRD data upload
ansible-playbook -i inventory/prod-hosts.yml playbooks/deploy.yml \
  -e "rrd_data_enabled=true" \
  -e "rrd_data_source_path=/var/airpuff/rrd-data"
```

### RRD Data Structure

The migration system expects RRD files in this structure:
```
/opt/airpuff/rrd-data/
├── ksfo-temp.rrd
├── ksfo-altimeter.rrd
├── ksfo-wind.rrd
├── ksfo-visibility.rrd
├── ksfo-ceiling.rrd
├── ksea-temp.rrd
├── ksea-altimeter.rrd
└── ...
```

## Environment Configuration

### Development Environment

**File**: `ansible/group_vars/web_dev.yml`
```yaml
# Development overrides
airpuff_app_home: "/opt/airpuff-dev"
airpuff_app_port: 25081
airpuff_app_hostname: "dev.airpuff.info"
postgresql_db_name: "airpuff_dev"
environment: "development"
debug: true
monitoring_enabled: false
```

### Production Environment

**File**: `ansible/group_vars/web_prod.yml`
```yaml
# Production overrides
airpuff_app_home: "/opt/airpuff"
airpuff_app_port: 25080
airpuff_app_hostname: "www.airpuff.info"
postgresql_db_name: "airpuff"
environment: "production"
debug: false
monitoring_enabled: true
```

## Deployment Commands

### Manual Deployment

**Development:**
```bash
ansible-playbook -i inventory/dev-hosts.yml playbooks/deploy.yml \
  -e "environment=dev" \
  -e "app_port=25081" \
  -e "app_hostname=dev.airpuff.info" \
  -e "app_directory=/opt/airpuff-dev"
```

**Production:**
```bash
ansible-playbook -i inventory/prod-hosts.yml playbooks/deploy.yml \
  -e "environment=prod" \
  -e "app_port=25080" \
  -e "app_hostname=www.airpuff.info" \
  -e "app_directory=/opt/airpuff"
```

### Using Deploy Script

**Development:**
```bash
./deploy.sh -t web_dev -e dev
```

**Production:**
```bash
./deploy.sh -t web_prod -e prod
```

## Service Configuration

### Systemd Services

**Development Service**: `airpuff-dev-app.service`
```ini
[Unit]
Description=AirPuff Development Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=airpuff
Group=airpuff
WorkingDirectory=/opt/airpuff-dev/backend
ExecStart=/opt/airpuff-dev/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 25081 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Production Service**: `airpuff-app.service`
```ini
[Unit]
Description=AirPuff Production Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=airpuff
Group=airpuff
WorkingDirectory=/opt/airpuff/backend
ExecStart=/opt/airpuff/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 25080 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Database Configuration

### Development Database
```sql
-- Development database
CREATE DATABASE airpuff_dev;
CREATE USER airpuff_dev WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE airpuff_dev TO airpuff_dev;
```

### Production Database
```sql
-- Production database
CREATE DATABASE airpuff;
CREATE USER airpuff WITH PASSWORD 'secure_production_password';
GRANT ALL PRIVILEGES ON DATABASE airpuff TO airpuff;
```

## Monitoring and Health Checks

### Health Endpoints

**Development:**
- Health: http://dev.airpuff.info:25081/health
- API Health: http://dev.airpuff.info:25081/api/v1/health
- Migration: http://dev.airpuff.info:25081/migration

**Production:**
- Health: http://www.airpuff.info:25080/health
- API Health: http://www.airpuff.info:25080/api/v1/health
- Migration: http://www.airpuff.info:25080/migration

### Service Status

```bash
# Check service status
sudo systemctl status airpuff-app
sudo systemctl status airpuff-dev-app

# Check logs
sudo journalctl -u airpuff-app -f
sudo journalctl -u airpuff-dev-app -f

# Check ports
sudo netstat -tlnp | grep 25080
sudo netstat -tlnp | grep 25081
```

## Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Check if ports are in use
sudo lsof -i :25080
sudo lsof -i :25081

# Kill conflicting processes
sudo kill -9 <PID>
```

**Service Won't Start:**
```bash
# Check service logs
sudo journalctl -u airpuff-app -f

# Check configuration
sudo systemctl cat airpuff-app

# Restart service
sudo systemctl restart airpuff-app
```

**Database Connection Issues:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
psql -h localhost -U airpuff -d airpuff -c "SELECT 1;"

# Check database exists
sudo -u postgres psql -l | grep airpuff
```

### Log Locations

**Application Logs:**
- Development: `/var/log/airpuff-dev/`
- Production: `/var/log/airpuff/`

**System Logs:**
- Service logs: `sudo journalctl -u airpuff-app`
- System logs: `/var/log/syslog`

## Security Considerations

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 25080/tcp # Production
sudo ufw allow 25081/tcp # Development
sudo ufw deny 5432/tcp   # PostgreSQL (internal only)
sudo ufw deny 6379/tcp   # Redis (internal only)
```

### SSL/TLS Configuration

**Production SSL:**
```nginx
server {
    listen 443 ssl http2;
    server_name www.airpuff.info;
    
    ssl_certificate /etc/letsencrypt/live/www.airpuff.info/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.airpuff.info/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:25080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup and Recovery

### Database Backup

```bash
# Backup production database
sudo -u postgres pg_dump airpuff > /var/backups/airpuff/airpuff-$(date +%Y%m%d-%H%M%S).sql

# Backup development database
sudo -u postgres pg_dump airpuff_dev > /var/backups/airpuff-dev/airpuff-dev-$(date +%Y%m%d-%H%M%S).sql
```

### RRD Data Backup

```bash
# Backup RRD data
tar -czf /var/backups/airpuff/rrd-data-$(date +%Y%m%d-%H%M%S).tar.gz /opt/airpuff/rrd-data/
```

## Next Steps

1. **Set up GitHub Secrets**: Add all required secrets to your repository
2. **Configure DNS**: Point dev.airpuff.info and www.airpuff.info to host74.nird.club
3. **Upload RRD Data**: Use the upload script to transfer your RRD data
4. **Test Deployment**: Push to dev branch to test development deployment
5. **Production Deployment**: Push to main branch for production deployment
6. **Run Migration**: Use the web interface to migrate RRD data
7. **Monitor**: Check health endpoints and logs

## Support

For issues or questions:
- Check logs: `sudo journalctl -u airpuff-app -f`
- Health check: `curl http://www.airpuff.info:25080/health`
- GitHub Issues: Create an issue in the repository
- Documentation: Check the troubleshooting guide

This deployment guide ensures proper separation between development and production environments while maintaining security and reliability.

