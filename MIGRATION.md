# AirPuff Data Migration Guide

This guide covers the complete data migration system for AirPuff, including RRD (Round Robin Database) data migration from the legacy system to the new TimescaleDB-based system.

## Overview

The AirPuff data migration system provides:

- **RRD Data Migration**: Import legacy RRD weather data into TimescaleDB
- **Data Validation**: Verify migration integrity and completeness
- **Progress Monitoring**: Real-time migration progress tracking
- **Error Handling**: Comprehensive error handling and recovery
- **Web Interface**: User-friendly migration management interface
- **API Endpoints**: Programmatic migration control

## RRD Data Structure

### Legacy RRD Files

The legacy system stores weather data in separate RRD files for each airport and data type:

**File Naming Convention:**
- `{airport_code}-temp.rrd` - Temperature data
- `{airport_code}-altimeter.rrd` - Altimeter data
- `{airport_code}-wind.rrd` - Wind data
- `{airport_code}-visibility.rrd` - Visibility data
- `{airport_code}-ceiling.rrd` - Ceiling data

**Data Sources per File:**

**Temperature (`-temp.rrd`):**
- `temp_c` - Temperature in Celsius
- `temp_f` - Temperature in Fahrenheit
- `dew_pt_c` - Dew point in Celsius
- `dew_pt_f` - Dew point in Fahrenheit
- `t_dp_spread_c` - Temperature-dewpoint spread in Celsius
- `t_dp_spread_f` - Temperature-dewpoint spread in Fahrenheit

**Altimeter (`-altimeter.rrd`):**
- `altimeter` - Altimeter setting in inches of mercury

**Wind (`-wind.rrd`):**
- `wind_dir` - Wind direction in degrees
- `wind_speed` - Wind speed in knots

**Visibility (`-visibility.rrd`):**
- `visibility` - Visibility in statute miles

**Ceiling (`-ceiling.rrd`):**
- `ceiling` - Ceiling height in feet

### Data Retention

RRD files store data at multiple resolutions:

- **1 Day**: 5-minute averages (288 data points)
- **7 Days**: 15-minute averages (672 data points)
- **30 Days**: 30-minute averages (1,440 data points)
- **365 Days**: 60-minute averages (8,760 data points)
- **10 Years**: 24-hour averages (3,650 data points)

## Migration Process

### 1. Discovery Phase

The migration service automatically discovers airports by scanning RRD files:

```python
# Scan for temperature RRD files (they all follow the same pattern)
for rrd_file in rrd_path.glob("*-temp.rrd"):
    airport_code = rrd_file.stem.replace("-temp", "").upper()
    airports.add(airport_code)
```

### 2. Airport Creation

For each discovered airport, the system ensures it exists in the database:

```python
# Check if airport already exists
airport = db.query(Airport).filter(Airport.icao == airport_code).first()

if not airport:
    # Create airport with basic info
    airport = Airport(
        icao=airport_code,
        name=f"{airport_code} Airport",
        city="Unknown",
        state="Unknown",
        country="Unknown",
        latitude=0.0,
        longitude=0.0,
        elevation_ft=0
    )
    db.add(airport)
    db.commit()
```

### 3. Data Extraction

RRD data is extracted using the `rrdtool` command-line utility:

```bash
rrdtool xport \
    --start now-10y \
    --end now \
    --json \
    --showtime \
    DEF:temp_c=/var/airpuff/rrd-data/ksfo-temp.rrd temp_c AVERAGE \
    XPORT:temp_c:temp_c
```

### 4. Data Transformation

RRD data is transformed to match the new database schema:

```python
# Transform RRD data to WeatherObservation format
observation = WeatherObservation(
    airport_id=airport_id,
    time=timestamp,
    temperature_c=values.get('temp_c'),
    dewpoint_c=values.get('dew_pt_c'),
    wind_dir_deg=values.get('wind_dir'),
    wind_speed_kts=values.get('wind_speed'),
    visibility_mi=values.get('visibility'),
    altimeter_hg=values.get('altimeter'),
    ceiling_ft=values.get('ceiling')
)
```

### 5. Data Upsertion

Data is upserted to handle duplicates and updates:

```python
# Check if observation already exists
existing = db.query(WeatherObservation).filter(
    WeatherObservation.airport_id == airport_id,
    WeatherObservation.time == timestamp
).first()

if existing:
    # Update existing observation
    for key, value in data.items():
        if hasattr(existing, key) and value is not None:
            setattr(existing, key, value)
else:
    # Create new observation
    observation = WeatherObservation(**data)
    db.add(observation)
```

## API Endpoints

### Migration Control

**Start Migration:**
```http
POST /api/v1/migration/rrd/migrate
Content-Type: application/json

{
    "rrd_path": "/var/airpuff/rrd-data"
}
```

**Get Migration Status:**
```http
GET /api/v1/migration/rrd/status
```

**Validate Migration:**
```http
POST /api/v1/migration/rrd/validate
```

### Airport Management

**List RRD Airports:**
```http
GET /api/v1/migration/rrd/airports
```

**Get Airport Info:**
```http
GET /api/v1/migration/rrd/airport/{airport_code}/info
```

**Migrate Single Airport:**
```http
POST /api/v1/migration/rrd/airport/{airport_code}/migrate
```

**Get Sample Data:**
```http
GET /api/v1/migration/rrd/sample/{airport_code}?file_type=temperature&limit=10
```

### Migration Summary

**Get Migration Summary:**
```http
GET /api/v1/migration/summary
```

## Web Interface

### Migration Dashboard

The web interface provides a comprehensive migration dashboard:

- **Status Overview**: Migration progress and statistics
- **Airport List**: List of airports with RRD data
- **Progress Tracking**: Real-time migration progress
- **Log Viewer**: Migration logs and error messages
- **Airport Details**: Sample data preview for each airport

### Features

- **Real-time Updates**: Live progress tracking
- **Error Handling**: Comprehensive error reporting
- **Data Preview**: Sample data viewing before migration
- **Validation**: Post-migration data validation
- **Logging**: Detailed migration logs

## Usage Examples

### Command Line Migration

```bash
# Start migration via API
curl -X POST "http://localhost:8000/api/v1/migration/rrd/migrate" \
     -H "Content-Type: application/json" \
     -d '{"rrd_path": "/var/airpuff/rrd-data"}'

# Check migration status
curl "http://localhost:8000/api/v1/migration/rrd/status"

# Get list of RRD airports
curl "http://localhost:8000/api/v1/migration/rrd/airports"
```

### Python Migration

```python
import asyncio
from app.services.migration.rrd_migration_service import rrd_migration_service
from app.database import get_db

async def migrate_data():
    db = next(get_db())
    stats = await rrd_migration_service.migrate_all_rrd_data(db)
    print(f"Migration completed: {stats}")

# Run migration
asyncio.run(migrate_data())
```

### Web Interface

1. Navigate to `/migration` in your browser
2. Click "Start Migration" to begin the process
3. Monitor progress in real-time
4. Use "Validate" to verify migration integrity
5. View sample data for each airport

## Migration Statistics

The migration service tracks comprehensive statistics:

```python
migration_stats = {
    'airports_processed': 0,      # Number of airports processed
    'records_migrated': 0,        # Number of weather records migrated
    'errors': 0,                  # Number of errors encountered
    'start_time': None,           # Migration start time
    'end_time': None              # Migration end time
}
```

## Error Handling

### Common Issues

**RRD File Not Found:**
- Check RRD file path and permissions
- Verify airport code format
- Ensure RRD files exist

**Database Connection Issues:**
- Verify database connectivity
- Check database credentials
- Ensure TimescaleDB is running

**Data Validation Errors:**
- Check data format and ranges
- Verify timestamp formats
- Validate numeric values

### Recovery Procedures

**Resume Migration:**
- Migration can be resumed from where it left off
- Duplicate data is handled via upsert operations
- Error recovery is automatic

**Data Validation:**
- Use validation endpoint to check data integrity
- Compare RRD data with database data
- Identify and fix discrepancies

## Performance Considerations

### Optimization

- **Batch Processing**: Process airports in batches
- **Parallel Processing**: Use async/await for concurrent operations
- **Memory Management**: Process data in chunks to avoid memory issues
- **Database Optimization**: Use bulk operations where possible

### Monitoring

- **Progress Tracking**: Real-time progress monitoring
- **Performance Metrics**: Track migration speed and efficiency
- **Resource Usage**: Monitor CPU, memory, and disk usage
- **Error Rates**: Track and analyze error patterns

## Troubleshooting

### Common Problems

**Migration Stuck:**
- Check for database locks
- Verify RRD file accessibility
- Check system resources

**Data Inconsistencies:**
- Run validation checks
- Compare RRD and database data
- Check for timezone issues

**Performance Issues:**
- Monitor system resources
- Check database performance
- Optimize batch sizes

### Debug Commands

```bash
# Check RRD file info
rrdtool info /var/airpuff/rrd-data/ksfo-temp.rrd

# Export sample data
rrdtool xport --start now-1d --end now \
    DEF:temp_c=/var/airpuff/rrd-data/ksfo-temp.rrd temp_c AVERAGE \
    XPORT:temp_c:temp_c

# Check database records
psql -d airpuff -c "SELECT COUNT(*) FROM weather_observations WHERE airport_id = 1;"
```

## Best Practices

### Migration Planning

- **Backup Data**: Always backup existing data before migration
- **Test Migration**: Test migration on a subset of data first
- **Monitor Resources**: Ensure adequate system resources
- **Plan Downtime**: Schedule migration during low-traffic periods

### Data Quality

- **Validate Data**: Run validation checks after migration
- **Check Completeness**: Verify all data was migrated
- **Monitor Errors**: Track and resolve migration errors
- **Document Issues**: Keep records of migration issues

### Performance

- **Batch Processing**: Process data in manageable batches
- **Resource Monitoring**: Monitor system resources during migration
- **Error Recovery**: Implement robust error recovery procedures
- **Progress Tracking**: Provide clear progress indicators

## Support

For migration issues or questions:

1. Check the migration logs for error details
2. Verify RRD file accessibility and format
3. Check database connectivity and permissions
4. Review system resources and performance
5. Contact the development team for assistance

The data migration system provides a robust, automated way to migrate legacy RRD data to the new TimescaleDB-based system while maintaining data integrity and providing comprehensive monitoring and error handling capabilities.
