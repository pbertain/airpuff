# AirPuff Grafana Integration

This document describes the Grafana integration for AirPuff's weather data visualization.

## Overview

AirPuff includes comprehensive Grafana dashboards for real-time weather data visualization and analytics. The integration provides:

- **Real-time Weather Dashboards**: Live weather trends across all airports
- **Airport-Specific Analytics**: Detailed weather analysis for individual airports
- **Alert Management**: Weather-based alert rules and notifications
- **Embedded Dashboards**: Seamless integration with the AirPuff web interface

## Architecture

### Components

1. **TimescaleDB**: Time-series database for weather observations
2. **Grafana**: Visualization and dashboard platform
3. **Redis**: Caching and session management
4. **FastAPI Integration**: REST API for dashboard management

### Docker Services

```yaml
services:
  timescaledb:    # PostgreSQL with TimescaleDB extension
  grafana:        # Grafana visualization platform
  redis:          # Caching and session storage
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ with FastAPI
- AirPuff backend running

### Quick Start

1. **Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Access Grafana**:
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `admin`

3. **Access AirPuff**:
   - URL: http://localhost:8000/grafana
   - Integrated dashboard interface

### Manual Setup (Alternative)

If Docker Compose is not available:

1. **Install TimescaleDB**:
   ```bash
   # Using Docker
   docker run -d --name timescaledb \
     -e POSTGRES_DB=airpuff \
     -e POSTGRES_USER=airpuff \
     -e POSTGRES_PASSWORD=airpuff \
     -p 5432:5432 \
     timescale/timescaledb:latest-pg15
   ```

2. **Install Grafana**:
   ```bash
   # Using Docker
   docker run -d --name grafana \
     -e GF_SECURITY_ADMIN_PASSWORD=admin \
     -p 3000:3000 \
     grafana/grafana:latest
   ```

3. **Configure Database**:
   - Run the initialization script: `docker/timescaledb/init.sql`
   - Create TimescaleDB hypertables
   - Insert sample data

## Dashboard Features

### Weather Overview Dashboard

- **Temperature Trends**: 24-hour temperature and dewpoint trends
- **Wind Analysis**: Wind speed and direction over time
- **Visibility Monitoring**: Visibility trends and alerts
- **Altimeter Tracking**: Barometric pressure changes
- **Flight Category Distribution**: VFR/MVFR/IFR/LIFR breakdown

### Airport-Specific Dashboard

- **Current Conditions**: Real-time weather status
- **Historical Trends**: 24-hour weather patterns
- **Sky Cover Analysis**: Cloud coverage distribution
- **Flight Category History**: Weather condition trends
- **Interactive Selection**: Choose any airport from dropdown

## API Endpoints

### Grafana Management

- `GET /api/v1/grafana/status` - Service status
- `GET /api/v1/grafana/dashboards` - List dashboards
- `GET /api/v1/grafana/dashboards/{uid}` - Get specific dashboard
- `GET /api/v1/grafana/datasources` - List datasources

### Dashboard URLs

- `GET /api/v1/grafana/weather-dashboard` - Weather dashboard URL
- `GET /api/v1/grafana/airport-dashboard?airport=KSFO` - Airport dashboard URL
- `GET /api/v1/grafana/embed/weather` - Embedded weather dashboard
- `GET /api/v1/grafana/embed/airport?airport=KSFO` - Embedded airport dashboard

### Alert Management

- `GET /api/v1/grafana/alerts` - List alert rules
- `POST /api/v1/grafana/alerts/weather/{airport}` - Create weather alert

## Data Schema

### Weather Observations Table

```sql
CREATE TABLE weather_observations (
    icao_code VARCHAR(4) NOT NULL,
    observed_time TIMESTAMP WITH TIME ZONE NOT NULL,
    flight_category VARCHAR(4),
    temp_c DECIMAL(4,1),
    dewpoint_c DECIMAL(4,1),
    wind_dir_degrees INTEGER,
    wind_speed_kt INTEGER,
    visibility_mi DECIMAL(4,1),
    altimeter_in_hg DECIMAL(5,2),
    sky_cover VARCHAR(10),
    raw_text TEXT,
    PRIMARY KEY (icao_code, observed_time)
);
```

### TimescaleDB Hypertable

```sql
SELECT create_hypertable('weather_observations', 'observed_time');
```

## Configuration

### Environment Variables

```bash
# Database
TIMESCALEDB_URL=postgresql://airpuff:airpuff@localhost:5432/airpuff

# Grafana
GRAFANA_URL=http://localhost:3000
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin

# Redis
REDIS_URL=redis://localhost:6379
```

### Grafana Settings

- **Theme**: Dark mode for AirPuff integration
- **Refresh Rate**: 5 seconds for real-time updates
- **Time Range**: 24 hours default, configurable
- **Timezone**: UTC for consistency

## Troubleshooting

### Common Issues

1. **Grafana Not Connecting**:
   - Check Docker containers are running
   - Verify port 3000 is accessible
   - Check Grafana logs: `docker logs grafana`

2. **No Data in Dashboards**:
   - Verify TimescaleDB is running
   - Check database connection
   - Ensure weather data is being collected

3. **Dashboard Not Loading**:
   - Check Grafana datasource configuration
   - Verify TimescaleDB permissions
   - Check network connectivity

### Logs

```bash
# Grafana logs
docker logs grafana

# TimescaleDB logs
docker logs timescaledb

# AirPuff logs
tail -f backend/logs/airpuff.log
```

## Development

### Adding New Dashboards

1. Create dashboard JSON in `docker/grafana/dashboards/`
2. Update provisioning configuration
3. Restart Grafana container
4. Add API endpoints in `app/api/v1/grafana.py`

### Custom Queries

Example TimescaleDB query for weather trends:

```sql
SELECT 
    observed_time as time,
    temp_c as "Temperature (°C)"
FROM weather_observations
WHERE observed_time >= NOW() - INTERVAL '24 hours'
ORDER BY observed_time;
```

## Production Considerations

- **Security**: Change default passwords
- **SSL**: Enable HTTPS for Grafana
- **Backup**: Regular database backups
- **Monitoring**: Set up Grafana alerts
- **Scaling**: Consider Grafana clustering for high availability

## Support

For issues or questions:
- Check the logs first
- Review the API documentation
- Test individual components
- Contact the development team
