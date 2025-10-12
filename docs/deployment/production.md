# AirPuff Deployment Guide

Complete deployment guide for AirPuff 2.0, covering development, staging, and production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Ansible Deployment](#ansible-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Overview

AirPuff 2.0 supports multiple deployment methods:

- **Development**: Local development environment
- **Docker**: Containerized deployment
- **Ansible**: Infrastructure as Code deployment
- **Production**: Bare metal production deployment
- **CI/CD**: Automated deployment pipeline

### Architecture Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Application   │
│   (NGINX)       │────│   (NGINX)       │────│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
          ┌───────────────────────────────────────────┼───────────────────────────────────────────┐
          │                                           │                                           │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│   TimescaleDB   │    │     Redis       │    │   Grafana       │    │   External APIs │
│   (Database)    │    │   (Cache)       │    │ (Monitoring)    │    │  (Fli-Rite, etc)│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **CPU**: 2 cores, 2.4 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 100 Mbps

**Recommended Requirements:**
- **CPU**: 4 cores, 3.0 GHz
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **Network**: 1 Gbps

### Software Requirements

**Operating System:**
- Ubuntu 20.04+ LTS
- Debian 11+
- CentOS 8+ / RHEL 8+
- macOS 10.15+ (development only)

**Required Software:**
- Python 3.11+
- PostgreSQL 15+ with TimescaleDB
- Redis 7.0+
- Docker 24.0+ (optional)
- Docker Compose 2.21+ (optional)
- Ansible 7.4+ (deployment)

**Development Tools:**
- Git 2.30+
- Node.js 18+ (frontend tools)
- curl (testing)
- jq (JSON processing)

## Development Deployment

### Local Development Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/your-org/airpuff.git
   cd airpuff
   ```

2. **Set Up Python Environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set Up Database:**
   ```bash
   # Install PostgreSQL and TimescaleDB
   sudo apt install postgresql postgresql-contrib
   sudo apt install timescaledb-2-postgresql-15
   
   # Create database
   sudo -u postgres createdb airpuff
   sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
   
   # Run migrations
   alembic upgrade head
   ```

5. **Set Up Redis:**
   ```bash
   sudo apt install redis-server
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

6. **Start Application:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Verify Installation:**
   ```bash
   curl http://localhost:8000/health
   ```

### Development Configuration

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/airpuff
TIMESCALEDB_URL=postgresql://user:password@localhost:5432/airpuff

# Redis
REDIS_URL=redis://localhost:6379

# Application
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# API Keys
FLI_RITE_API_KEY=your-fli-rite-api-key
CHECKWX_API_KEY=your-checkwx-api-key

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret
```

### Development Tools

**Code Quality:**
```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/app/

# Security scan
bandit -r backend/app/
```

**Testing:**
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_models.py -v
```

## Production Deployment

### Bare Metal Deployment

**System Preparation:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql-15 postgresql-client-15
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y fail2ban
sudo apt install -y ufw
```

**Database Setup:**
```bash
# Install TimescaleDB
sudo apt install -y timescaledb-2-postgresql-15

# Configure PostgreSQL
sudo -u postgres createuser airpuff
sudo -u postgres createdb airpuff
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
sudo -u postgres psql -d airpuff -c "GRANT ALL PRIVILEGES ON DATABASE airpuff TO airpuff;"
```

**Application Deployment:**
```bash
# Create application user
sudo useradd -m -s /bin/bash airpuff
sudo mkdir -p /opt/airpuff
sudo chown airpuff:airpuff /opt/airpuff

# Deploy application
sudo -u airpuff git clone https://github.com/your-org/airpuff.git /opt/airpuff
cd /opt/airpuff/backend
sudo -u airpuff python3.11 -m venv venv
sudo -u airpuff ./venv/bin/pip install -r requirements.txt

# Configure application
sudo -u airpuff cp .env.example .env
# Edit .env with production values

# Run migrations
sudo -u airpuff ./venv/bin/alembic upgrade head
```

**Service Configuration:**
```bash
# Create systemd service
sudo cp systemd/airpuff-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable airpuff-app
sudo systemctl start airpuff-app
```

**NGINX Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/airpuff/backend/app/static/;
    }
}
```

### Production Configuration

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://airpuff:secure-password@localhost:5432/airpuff
TIMESCALEDB_URL=postgresql://airpuff:secure-password@localhost:5432/airpuff

# Redis
REDIS_URL=redis://localhost:6379

# Application
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

**Security Configuration:**
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Configure fail2ban
sudo cp fail2ban/jail.local /etc/fail2ban/
sudo systemctl restart fail2ban
```

## Docker Deployment

### Docker Compose Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:2.13.0-pg15
    environment:
      POSTGRES_DB: airpuff
      POSTGRES_USER: airpuff
      POSTGRES_PASSWORD: airpuff_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/timescaledb/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.2.0
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/provisioning:/etc/grafana/provisioning
      - ./docker/grafana/dashboards:/var/lib/grafana/dashboards
    ports:
      - "3000:3000"
    restart: unless-stopped

  airpuff-app:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://airpuff:airpuff_password@postgres:5432/airpuff
      REDIS_URL: redis://redis:6379
      SECRET_KEY: your-secret-key
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 airpuff && chown -R airpuff:airpuff /app
USER airpuff

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Commands

**Start Services:**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f airpuff-app
```

**Database Operations:**
```bash
# Run migrations
docker-compose exec airpuff-app alembic upgrade head

# Access database
docker-compose exec postgres psql -U airpuff -d airpuff
```

**Backup and Restore:**
```bash
# Backup database
docker-compose exec postgres pg_dump -U airpuff airpuff > backup.sql

# Restore database
docker-compose exec -T postgres psql -U airpuff -d airpuff < backup.sql
```

## Ansible Deployment

### Inventory Configuration

**ansible/inventory/hosts.yml:**
```yaml
all:
  children:
    airpuff_prod:
      hosts:
        airpuff-prod:
          ansible_host: 192.168.1.200
          ansible_user: deploy
          ansible_ssh_private_key_file: ~/.ssh/airpuff_prod_key
          environment: production
          domain: airpuff.com
          ssl_enabled: true
      vars:
        app_port: 8000
        grafana_port: 3000
        timescaledb_port: 5432
        redis_port: 6379
```

### Deployment Commands

**Deploy to Production:**
```bash
# Deploy with Ansible
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -t airpuff_prod

# Deploy with custom script
./deploy.sh -t airpuff_prod -e prod -p "vault-password"
```

**Deploy Specific Components:**
```bash
# Deploy only application
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -t airpuff_prod --tags "app"

# Deploy only database
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -t airpuff_prod --tags "database"

# Deploy only monitoring
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -t airpuff_prod --tags "monitoring"
```

### Ansible Roles

**Available Roles:**
- `system_setup`: System configuration and security
- `python_setup`: Python environment setup
- `postgresql_setup`: Database configuration
- `redis_setup`: Redis configuration
- `docker_setup`: Docker installation
- `grafana_setup`: Grafana configuration
- `airpuff_app`: Application deployment
- `systemd_services`: Service management
- `monitoring_setup`: Monitoring configuration
- `backup_setup`: Backup system setup

## CI/CD Pipeline

### GitHub Actions Workflow

**Automated Deployment:**
- **Development**: Auto-deploy on push to `dev` branch
- **Staging**: Auto-deploy on push to `main` branch
- **Production**: Manual deploy with approval

**Pipeline Stages:**
1. **Code Quality**: Linting, formatting, type checking
2. **Testing**: Unit, integration, and API tests
3. **Security**: Vulnerability scanning
4. **Build**: Docker image creation
5. **Deploy**: Automated deployment
6. **Health Check**: Post-deployment verification

### Deployment Commands

**Manual Deployment:**
```bash
# Deploy to development
gh workflow run "AirPuff CI/CD Pipeline" -f environment=dev

# Deploy to staging
gh workflow run "AirPuff CI/CD Pipeline" -f environment=staging

# Deploy to production
gh workflow run "AirPuff CI/CD Pipeline" -f environment=prod
```

**Emergency Deployment:**
```bash
# Emergency deploy (skip tests)
gh workflow run "Emergency Deployment" -f environment=prod -f reason="Critical bug fix"
```

## Monitoring

### Health Monitoring

**Health Endpoints:**
```bash
# Application health
curl http://localhost:8000/health

# API health with service status
curl http://localhost:8000/api/v1/health

# Database health
curl http://localhost:8000/api/v1/health | jq '.services.database'
```

**Service Monitoring:**
```bash
# Check service status
sudo systemctl status airpuff-app
sudo systemctl status postgresql
sudo systemctl status redis-server

# Check service logs
sudo journalctl -u airpuff-app -f
sudo journalctl -u postgresql -f
```

### Grafana Dashboards

**Access Grafana:**
- URL: `http://localhost:3000`
- Username: `admin`
- Password: `admin` (change in production)

**Available Dashboards:**
- **Weather Overview**: Real-time weather conditions
- **Airport Analytics**: Airport-specific metrics
- **System Performance**: Application performance
- **Database Metrics**: Database performance
- **User Activity**: User engagement metrics

### Log Management

**Log Locations:**
- **Application**: `/var/log/airpuff/`
- **System**: `/var/log/syslog`
- **PostgreSQL**: `/var/log/postgresql/`
- **NGINX**: `/var/log/nginx/`

**Log Rotation:**
```bash
# Check logrotate configuration
sudo logrotate -d /etc/logrotate.d/airpuff

# Force log rotation
sudo logrotate -f /etc/logrotate.d/airpuff
```

## Security

### SSL/TLS Configuration

**Let's Encrypt Setup:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**NGINX SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Hardening

**Firewall Configuration:**
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp
sudo ufw deny 6379/tcp
```

**Fail2ban Configuration:**
```bash
# Configure fail2ban
sudo cp fail2ban/jail.local /etc/fail2ban/
sudo systemctl restart fail2ban

# Check fail2ban status
sudo fail2ban-client status
```

**System Hardening:**
```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Enable automatic updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## Troubleshooting

### Common Issues

**Application Won't Start:**
1. Check service status: `sudo systemctl status airpuff-app`
2. Check logs: `sudo journalctl -u airpuff-app -f`
3. Verify configuration: Check `.env` file
4. Check dependencies: Verify database and Redis connectivity

**Database Connection Issues:**
1. Check PostgreSQL status: `sudo systemctl status postgresql`
2. Verify database exists: `sudo -u postgres psql -l`
3. Check connection: `psql -h localhost -U airpuff -d airpuff`
4. Verify TimescaleDB: `sudo -u postgres psql -d airpuff -c "SELECT * FROM pg_extension;"`

**Performance Issues:**
1. Check system resources: `htop`, `df -h`, `free -h`
2. Check database performance: `sudo -u postgres psql -d airpuff -c "SELECT * FROM pg_stat_activity;"`
3. Check application logs for errors
4. Monitor response times: `curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health`

### Debug Commands

**Application Debugging:**
```bash
# Run in debug mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Check database migrations
alembic current
alembic history

# Test database connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

**System Debugging:**
```bash
# Check system resources
htop
iotop
nethogs

# Check network connectivity
netstat -tlnp
ss -tlnp

# Check disk usage
df -h
du -sh /opt/airpuff/*
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore from backup
sudo -u postgres psql -d airpuff < backup.sql

# Recreate database
sudo -u postgres dropdb airpuff
sudo -u postgres createdb airpuff
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
alembic upgrade head
```

**Application Recovery:**
```bash
# Restart services
sudo systemctl restart airpuff-app
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# Check service status
sudo systemctl status airpuff-app postgresql redis-server
```

This comprehensive deployment guide covers all aspects of deploying AirPuff 2.0 across different environments. For additional help or specific deployment scenarios, refer to the troubleshooting section or contact support.
