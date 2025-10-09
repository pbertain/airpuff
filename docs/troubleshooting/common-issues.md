# AirPuff Troubleshooting Guide

Comprehensive troubleshooting guide for AirPuff 2.0, covering common issues, error codes, and resolution procedures.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
- [Error Codes](#error-codes)
- [Performance Issues](#performance-issues)
- [Database Issues](#database-issues)
- [Network Issues](#network-issues)
- [Authentication Issues](#authentication-issues)
- [Deployment Issues](#deployment-issues)
- [Recovery Procedures](#recovery-procedures)
- [Getting Help](#getting-help)

## Quick Diagnostics

### Health Check Commands

**Application Health:**
```bash
# Check application status
curl http://localhost:8000/health

# Check API health
curl http://localhost:8000/api/v1/health

# Check service status
sudo systemctl status airpuff-app
```

**Database Health:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U airpuff -d airpuff -c "SELECT 1;"

# Check TimescaleDB
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM pg_extension WHERE extname = 'timescaledb';"
```

**Redis Health:**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connectivity
redis-cli ping
```

**System Resources:**
```bash
# Check CPU and memory
htop

# Check disk usage
df -h

# Check network connectivity
netstat -tlnp
```

### Log Locations

**Application Logs:**
- `/var/log/airpuff/` - Application logs
- `sudo journalctl -u airpuff-app -f` - Systemd logs

**System Logs:**
- `/var/log/syslog` - System logs
- `/var/log/auth.log` - Authentication logs
- `/var/log/nginx/` - Web server logs

**Database Logs:**
- `/var/log/postgresql/` - PostgreSQL logs
- `sudo journalctl -u postgresql -f` - PostgreSQL systemd logs

## Common Issues

### Application Won't Start

**Symptoms:**
- Service fails to start
- Application crashes on startup
- Port 8000 not accessible

**Diagnosis:**
```bash
# Check service status
sudo systemctl status airpuff-app

# Check logs
sudo journalctl -u airpuff-app -f

# Check port availability
netstat -tlnp | grep 8000
```

**Common Causes:**
1. **Configuration Issues**: Invalid environment variables
2. **Database Connection**: Database not accessible
3. **Port Conflicts**: Port 8000 already in use
4. **Dependencies**: Missing Python packages
5. **Permissions**: Incorrect file permissions

**Resolution:**
```bash
# Check configuration
cat /opt/airpuff/backend/.env

# Test database connection
psql -h localhost -U airpuff -d airpuff -c "SELECT 1;"

# Check Python environment
cd /opt/airpuff/backend
source venv/bin/activate
python -c "import app.main; print('Import successful')"

# Restart service
sudo systemctl restart airpuff-app
```

### Weather Data Not Loading

**Symptoms:**
- Weather data shows "No data available"
- API returns 404 errors
- Weather charts are empty

**Diagnosis:**
```bash
# Check weather API
curl http://localhost:8000/api/v1/weather/KSFO/latest

# Check external API connectivity
curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=KSFO"

# Check database for weather data
psql -h localhost -U airpuff -d airpuff -c "SELECT COUNT(*) FROM weather_observations;"
```

**Common Causes:**
1. **External API Issues**: Fli-Rite or CheckWX API down
2. **Database Issues**: No weather data in database
3. **Airport Issues**: Airport not found in database
4. **Network Issues**: Internet connectivity problems
5. **API Keys**: Invalid or expired API keys

**Resolution:**
```bash
# Check external API status
curl -I https://www.aviationweather.gov/adds/dataserver_current/

# Verify airport exists
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM airports WHERE icao = 'KSFO';"

# Check API keys
grep -E "(FLI_RITE_API_KEY|CHECKWX_API_KEY)" /opt/airpuff/backend/.env

# Restart weather service
sudo systemctl restart airpuff-weather.timer
```

### Login Problems

**Symptoms:**
- OAuth login fails
- "Authentication required" errors
- User sessions not persisting

**Diagnosis:**
```bash
# Check OAuth configuration
grep -E "(GOOGLE_CLIENT_ID|APPLE_CLIENT_ID)" /opt/airpuff/backend/.env

# Check Redis connectivity
redis-cli ping

# Check session storage
redis-cli keys "*session*"
```

**Common Causes:**
1. **OAuth Configuration**: Invalid client IDs or secrets
2. **Redis Issues**: Session storage not working
3. **Network Issues**: OAuth provider connectivity
4. **SSL Issues**: HTTPS configuration problems
5. **Cookie Issues**: Browser cookie settings

**Resolution:**
```bash
# Verify OAuth configuration
curl -X POST http://localhost:8000/api/v1/auth/authorize/google

# Check Redis
redis-cli ping
redis-cli info

# Clear Redis sessions
redis-cli flushdb

# Check SSL configuration
openssl s_client -connect your-domain.com:443
```

### Route Planning Issues

**Symptoms:**
- Routes not saving
- Airport search not working
- Route weather not loading

**Diagnosis:**
```bash
# Check route API
curl -H "Authorization: Bearer your-token" http://localhost:8000/api/v1/routes/

# Check airport search
curl "http://localhost:8000/api/v1/airports/?search=KSFO"

# Check database
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM routes;"
```

**Common Causes:**
1. **Authentication Issues**: Invalid or expired tokens
2. **Database Issues**: Route data not saving
3. **Airport Issues**: Airport not found
4. **Permission Issues**: User not authorized
5. **API Issues**: Route API not responding

**Resolution:**
```bash
# Check authentication
curl -H "Authorization: Bearer your-token" http://localhost:8000/api/v1/users/me

# Verify airport exists
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM airports WHERE icao = 'KSFO';"

# Check user permissions
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM users WHERE id = 1;"
```

## Error Codes

### HTTP Status Codes

**200 OK**: Request successful
**201 Created**: Resource created successfully
**400 Bad Request**: Invalid request data
**401 Unauthorized**: Authentication required
**403 Forbidden**: Access denied
**404 Not Found**: Resource not found
**422 Unprocessable Entity**: Validation error
**429 Too Many Requests**: Rate limit exceeded
**500 Internal Server Error**: Server error

### Application Error Codes

**AIRPORT_NOT_FOUND**: Airport with specified ICAO code not found
```bash
# Resolution: Check if airport exists
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM airports WHERE icao = 'KSFO';"
```

**WEATHER_DATA_UNAVAILABLE**: Weather data not available for airport
```bash
# Resolution: Check weather data
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM weather_observations WHERE airport_id = 1 ORDER BY time DESC LIMIT 5;"
```

**INVALID_ICAO_CODE**: Invalid ICAO code format
```bash
# Resolution: Use valid 4-character ICAO code
# Valid: KSFO, KSEA, KLAX
# Invalid: KSF, KSFOO, 1234
```

**ROUTE_NOT_FOUND**: Route with specified ID not found
```bash
# Resolution: Check if route exists
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM routes WHERE id = 1;"
```

**UNAUTHORIZED**: Authentication required
```bash
# Resolution: Check authentication
curl -H "Authorization: Bearer your-token" http://localhost:8000/api/v1/users/me
```

**RATE_LIMIT_EXCEEDED**: Too many requests
```bash
# Resolution: Wait for rate limit reset
curl -I http://localhost:8000/api/v1/weather/KSFO/latest
```

### Database Error Codes

**CONNECTION_REFUSED**: Database connection failed
```bash
# Resolution: Check PostgreSQL status
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**AUTHENTICATION_FAILED**: Database authentication failed
```bash
# Resolution: Check database credentials
psql -h localhost -U airpuff -d airpuff -c "SELECT 1;"
```

**DATABASE_DOES_NOT_EXIST**: Database not found
```bash
# Resolution: Create database
sudo -u postgres createdb airpuff
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
```

**TIMESCALEDB_NOT_INSTALLED**: TimescaleDB extension not available
```bash
# Resolution: Install TimescaleDB
sudo apt install timescaledb-2-postgresql-15
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
```

## Performance Issues

### Slow Response Times

**Symptoms:**
- API responses take >2 seconds
- Web interface loads slowly
- Database queries timeout

**Diagnosis:**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check system resources
htop
free -h
df -h

# Check database performance
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM pg_stat_activity;"
```

**Common Causes:**
1. **High CPU Usage**: System overloaded
2. **Memory Issues**: Insufficient RAM
3. **Disk I/O**: Slow disk performance
4. **Database Issues**: Slow queries
5. **Network Issues**: Network latency

**Resolution:**
```bash
# Check system resources
htop
iotop
nethogs

# Optimize database
psql -h localhost -U airpuff -d airpuff -c "VACUUM ANALYZE;"

# Check database configuration
psql -h localhost -U airpuff -d airpuff -c "SHOW shared_buffers;"
psql -h localhost -U airpuff -d airpuff -c "SHOW work_mem;"

# Restart services
sudo systemctl restart airpuff-app
sudo systemctl restart postgresql
```

### High Memory Usage

**Symptoms:**
- System running out of memory
- Application crashes
- Slow performance

**Diagnosis:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check application memory
ps aux | grep airpuff
ps aux | grep postgres
```

**Resolution:**
```bash
# Restart services
sudo systemctl restart airpuff-app
sudo systemctl restart postgresql

# Check for memory leaks
sudo journalctl -u airpuff-app | grep -i memory

# Optimize database
psql -h localhost -U airpuff -d airpuff -c "VACUUM ANALYZE;"
```

### Database Performance Issues

**Symptoms:**
- Slow database queries
- Database timeouts
- High CPU usage

**Diagnosis:**
```bash
# Check active queries
psql -h localhost -U airpuff -d airpuff -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
psql -h localhost -U airpuff -d airpuff -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check database size
psql -h localhost -U airpuff -d airpuff -c "SELECT pg_size_pretty(pg_database_size('airpuff'));"
```

**Resolution:**
```bash
# Analyze tables
psql -h localhost -U airpuff -d airpuff -c "ANALYZE;"

# Vacuum database
psql -h localhost -U airpuff -d airpuff -c "VACUUM ANALYZE;"

# Check indexes
psql -h localhost -U airpuff -d airpuff -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE tablename = 'weather_observations';"

# Reindex if needed
psql -h localhost -U airpuff -d airpuff -c "REINDEX DATABASE airpuff;"
```

## Database Issues

### Connection Issues

**Symptoms:**
- "Connection refused" errors
- Database timeout errors
- Authentication failures

**Diagnosis:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check port availability
netstat -tlnp | grep 5432

# Test connection
psql -h localhost -U airpuff -d airpuff -c "SELECT 1;"
```

**Resolution:**
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check configuration
sudo -u postgres psql -c "SHOW listen_addresses;"
sudo -u postgres psql -c "SHOW port;"

# Check authentication
sudo -u postgres psql -c "SELECT * FROM pg_hba.conf;"
```

### Data Corruption

**Symptoms:**
- Inconsistent data
- Missing records
- Database errors

**Diagnosis:**
```bash
# Check database integrity
psql -h localhost -U airpuff -d airpuff -c "VACUUM ANALYZE;"

# Check for errors
sudo journalctl -u postgresql | grep -i error

# Check table sizes
psql -h localhost -U airpuff -d airpuff -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname = 'public';"
```

**Resolution:**
```bash
# Backup database
sudo -u postgres pg_dump airpuff > backup.sql

# Rebuild database
sudo -u postgres dropdb airpuff
sudo -u postgres createdb airpuff
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
sudo -u postgres psql -d airpuff < backup.sql

# Run migrations
cd /opt/airpuff/backend
alembic upgrade head
```

### Migration Issues

**Symptoms:**
- Migration failures
- Schema errors
- Data type mismatches

**Diagnosis:**
```bash
# Check migration status
alembic current
alembic history

# Check database schema
psql -h localhost -U airpuff -d airpuff -c "\dt"
psql -h localhost -U airpuff -d airpuff -c "\d weather_observations"
```

**Resolution:**
```bash
# Check migration files
ls -la alembic/versions/

# Run specific migration
alembic upgrade +1

# Downgrade if needed
alembic downgrade -1

# Check for conflicts
alembic merge -m "merge migrations"
```

## Network Issues

### Connectivity Problems

**Symptoms:**
- External API calls failing
- Weather data not updating
- OAuth authentication failing

**Diagnosis:**
```bash
# Check internet connectivity
ping -c 4 8.8.8.8
ping -c 4 google.com

# Check DNS resolution
nslookup google.com
nslookup www.aviationweather.gov

# Check external API connectivity
curl -I https://www.aviationweather.gov/adds/dataserver_current/
```

**Resolution:**
```bash
# Check firewall
sudo ufw status
sudo iptables -L

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test specific endpoints
curl -v https://www.aviationweather.gov/adds/dataserver_current/
curl -v https://accounts.google.com/.well-known/openid_configuration
```

### Port Issues

**Symptoms:**
- Services not accessible
- Connection refused errors
- Port conflicts

**Diagnosis:**
```bash
# Check port usage
netstat -tlnp | grep 8000
netstat -tlnp | grep 5432
netstat -tlnp | grep 6379

# Check service status
sudo systemctl status airpuff-app
sudo systemctl status postgresql
sudo systemctl status redis-server
```

**Resolution:**
```bash
# Kill conflicting processes
sudo lsof -ti:8000 | xargs sudo kill -9

# Restart services
sudo systemctl restart airpuff-app
sudo systemctl restart postgresql
sudo systemctl restart redis-server

# Check firewall
sudo ufw allow 8000
sudo ufw allow 5432
sudo ufw allow 6379
```

## Authentication Issues

### OAuth Problems

**Symptoms:**
- OAuth login fails
- "Invalid client" errors
- Redirect URI mismatches

**Diagnosis:**
```bash
# Check OAuth configuration
grep -E "(GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET)" /opt/airpuff/backend/.env

# Test OAuth endpoints
curl -X POST http://localhost:8000/api/v1/auth/authorize/google

# Check OAuth provider status
curl -I https://accounts.google.com/.well-known/openid_configuration
```

**Resolution:**
```bash
# Verify OAuth configuration
# Check client ID and secret
# Verify redirect URI
# Check OAuth provider settings

# Test OAuth flow
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"provider": "google", "code": "test-code", "state": "test-state", "code_verifier": "test-verifier"}'
```

### Session Issues

**Symptoms:**
- User sessions not persisting
- Frequent logouts
- Session data lost

**Diagnosis:**
```bash
# Check Redis connectivity
redis-cli ping

# Check session storage
redis-cli keys "*session*"

# Check Redis configuration
redis-cli config get "*"
```

**Resolution:**
```bash
# Restart Redis
sudo systemctl restart redis-server

# Clear Redis data
redis-cli flushdb

# Check Redis logs
sudo journalctl -u redis-server -f
```

## Deployment Issues

### Ansible Deployment Failures

**Symptoms:**
- Ansible playbook failures
- Deployment errors
- Service not starting

**Diagnosis:**
```bash
# Check Ansible syntax
ansible-playbook ansible/playbooks/deploy.yml --syntax-check

# Run in check mode
ansible-playbook ansible/playbooks/deploy.yml --check

# Check inventory
ansible-inventory -i ansible/inventory/hosts.yml --list
```

**Resolution:**
```bash
# Fix Ansible issues
ansible-playbook ansible/playbooks/deploy.yml --check --diff

# Run specific tasks
ansible-playbook ansible/playbooks/deploy.yml --tags "app"

# Check connectivity
ansible all -i ansible/inventory/hosts.yml -m ping
```

### Docker Deployment Issues

**Symptoms:**
- Docker containers not starting
- Container crashes
- Port conflicts

**Diagnosis:**
```bash
# Check Docker status
docker ps -a
docker-compose ps

# Check container logs
docker-compose logs airpuff-app
docker-compose logs postgres

# Check Docker resources
docker system df
docker system prune
```

**Resolution:**
```bash
# Restart containers
docker-compose down
docker-compose up -d

# Check container health
docker-compose exec airpuff-app curl http://localhost:8000/health

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

## Recovery Procedures

### Database Recovery

**Full Database Restore:**
```bash
# Stop application
sudo systemctl stop airpuff-app

# Backup current database
sudo -u postgres pg_dump airpuff > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore from backup
sudo -u postgres dropdb airpuff
sudo -u postgres createdb airpuff
sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
sudo -u postgres psql -d airpuff < backup.sql

# Start application
sudo systemctl start airpuff-app
```

**Partial Data Recovery:**
```bash
# Restore specific table
sudo -u postgres psql -d airpuff -c "TRUNCATE TABLE weather_observations;"
sudo -u postgres psql -d airpuff -c "COPY weather_observations FROM '/path/to/backup.csv' WITH CSV HEADER;"
```

### Application Recovery

**Complete Application Restore:**
```bash
# Stop services
sudo systemctl stop airpuff-app

# Backup current installation
sudo cp -r /opt/airpuff /opt/airpuff-backup-$(date +%Y%m%d-%H%M%S)

# Restore from backup
sudo rm -rf /opt/airpuff
sudo cp -r /opt/airpuff-backup /opt/airpuff

# Restart services
sudo systemctl start airpuff-app
```

**Configuration Recovery:**
```bash
# Restore configuration
sudo cp /opt/airpuff-backup/backend/.env /opt/airpuff/backend/.env

# Restart services
sudo systemctl restart airpuff-app
```

### System Recovery

**Complete System Recovery:**
```bash
# Stop all services
sudo systemctl stop airpuff-app
sudo systemctl stop postgresql
sudo systemctl stop redis-server

# Restore system from backup
sudo tar -xzf system-backup.tar.gz -C /

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl start airpuff-app
```

## Getting Help

### Support Resources

**Documentation:**
- [User Guide](docs/user-guides/user-manual.md)
- [API Reference](docs/api/api-reference.md)
- [Deployment Guide](docs/deployment/production.md)

**Community:**
- [GitHub Issues](https://github.com/your-org/airpuff/issues)
- [GitHub Discussions](https://github.com/your-org/airpuff/discussions)
- [Community Forum](https://community.airpuff.com)

**Professional Support:**
- Email: support@airpuff.com
- Phone: +1-555-AIRPUFF
- Enterprise: enterprise@airpuff.com

### Reporting Issues

**Before Reporting:**
1. Check this troubleshooting guide
2. Search existing issues
3. Gather relevant information
4. Test with minimal configuration

**Information to Include:**
- AirPuff version
- Operating system
- Error messages
- Log files
- Steps to reproduce
- Expected vs actual behavior

**Log Collection:**
```bash
# Collect system logs
sudo journalctl -u airpuff-app --since "1 hour ago" > airpuff-app.log
sudo journalctl -u postgresql --since "1 hour ago" > postgresql.log
sudo journalctl -u redis-server --since "1 hour ago" > redis-server.log

# Collect application logs
sudo cp -r /var/log/airpuff/ ./airpuff-logs/

# Collect system information
uname -a > system-info.txt
free -h >> system-info.txt
df -h >> system-info.txt
```

This comprehensive troubleshooting guide covers all common issues and provides step-by-step resolution procedures. For additional help or specific issues not covered here, please contact support.
