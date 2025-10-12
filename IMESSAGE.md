# AirPuff iMessage Integration

This document describes the bi-directional iMessage integration for AirPuff's weather data system.

## Overview

AirPuff's iMessage integration provides two powerful features:

1. **Scheduled Route Summaries**: Automatically send weather updates for saved routes at specified times
2. **On-Demand Weather Requests**: Send airport codes or route names via iMessage to get instant weather data

## Features

### 📱 **Bi-Directional Communication**
- **Server → Client**: Scheduled route weather summaries
- **Client → Server**: On-demand weather requests
- **Real-time Processing**: Instant responses to weather queries

### 🛩️ **Airport Weather Requests**
Send airport codes to get instant weather:
```
Client: KSFO KLAX KJFK
Server: AirPuff:
KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft
KLAX-MVFR-29.92-180@12-6.0mi-SCT|4000ft
KJFK-IFR-30.15-360@15-2.0mi-OVC|1000ft
```

### 🗺️ **Route Weather Requests**
Get weather for saved routes:
```
Client: ROUTE MyCommute
Server: AirPuff Route: MyCommute
1. KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft
2. KLAX-MVFR-29.92-180@12-6.0mi-SCT|4000ft
3. KJFK-IFR-30.15-360@15-2.0mi-OVC|1000ft
```

### ⏰ **Scheduled Messages**
- **Daily**: Send at specific times (e.g., 7:00 AM, 5:00 PM)
- **Hourly**: Send every hour
- **On-Demand**: Manual sending only
- **Smart Scheduling**: Avoid duplicate sends

## Message Format

### Weather Response Format
```
ICAO-CATEGORY-ALTIMETER-WIND-VISIBILITY-SKY|CEILING
```

**Example:**
```
KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft
```

**Breakdown:**
- **KSFO**: Airport ICAO code
- **VFR**: Flight category (VFR/MVFR/IFR/LIFR)
- **29.95**: Altimeter setting (inHg)
- **270@8**: Wind direction and speed (degrees@knots)
- **10.0mi**: Visibility (statute miles)
- **CLR|12000ft**: Sky cover and ceiling

### Wind Format
- **Calm**: No wind (0 kts)
- **270@8**: Wind from 270° at 8 knots
- **Variable**: VRB@5 (variable wind)

### Sky Cover Codes
- **CLR**: Clear sky (ceiling 12,000+ ft)
- **FEW**: Few clouds (ceiling 3,000 ft)
- **SCT**: Scattered clouds (ceiling 4,000 ft)
- **BKN**: Broken clouds (ceiling 2,000 ft)
- **OVC**: Overcast (ceiling 1,000 ft)

## Available Commands

### Airport Weather
```
KSFO KLAX KJFK          # Get weather for specific airports
KEDU KCCR KHWD KPAO     # Multiple airports (max 10)
```

### Route Weather
```
ROUTE MyCommute          # Get weather for named route
ROUTE                    # Get weather for favorite route
ROUTES                   # List available routes
```

### System Commands
```
STATUS                   # Check AirPuff service status
HELP                     # Show help message
PING                     # Test connectivity
```

## API Endpoints

### Message Processing
- `POST /api/v1/imessage/process` - Process incoming iMessage
- `POST /api/v1/imessage/send` - Send iMessage to recipient
- `GET /api/v1/imessage/test` - Test message formatting

### Scheduled Messages
- `GET /api/v1/imessage/schedule` - List user's scheduled messages
- `POST /api/v1/imessage/schedule` - Create scheduled message
- `PUT /api/v1/imessage/schedule/{id}` - Update scheduled message
- `DELETE /api/v1/imessage/schedule/{id}` - Delete scheduled message
- `POST /api/v1/imessage/schedule/{id}/send` - Send scheduled message now

### System Management
- `GET /api/v1/imessage/commands` - Get available commands
- `POST /api/v1/imessage/process-scheduled` - Process all due messages

## Setup Instructions

### Prerequisites
- AirPuff backend running
- iMessage bridge service (optional for development)
- User account with saved routes

### Configuration

**Environment Variables:**
```bash
# iMessage Bridge (optional)
IMESSAGE_BRIDGE_URL=http://localhost:8080
IMESSAGE_API_KEY=your-api-key

# Service Settings
IMESSAGE_MAX_AIRPORTS=10
IMESSAGE_TIMEOUT=30
```

### Development Mode
Without an iMessage bridge, the service will:
- Log messages instead of sending them
- Process requests normally
- Return formatted responses

## Usage Examples

### 1. Airport Weather Request
**Send:** `KSFO KLAX KJFK`
**Receive:**
```
AirPuff:
KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft
KLAX-MVFR-29.92-180@12-6.0mi-SCT|4000ft
KJFK-IFR-30.15-360@15-2.0mi-OVC|1000ft
```

### 2. Route Weather Request
**Send:** `ROUTE MyCommute`
**Receive:**
```
AirPuff Route: MyCommute
1. KSFO-VFR-29.95-270@8-10.0mi-CLR|12000ft
2. KLAX-MVFR-29.92-180@12-6.0mi-SCT|4000ft
3. KJFK-IFR-30.15-360@15-2.0mi-OVC|1000ft
```

### 3. Help Request
**Send:** `HELP`
**Receive:**
```
AirPuff iMessage Commands:

AIRPORT CODES: Send airport codes (e.g., KSFO KLAX KJFK)
ROUTE [name]: Get weather for a named route
ROUTES: List your available routes
STATUS: Check AirPuff service status
HELP: Show this help message

Examples:
• KSFO KLAX KJFK
• ROUTE MyCommute
• ROUTE (uses favorite route)

Maximum 10 airports per request.
```

### 4. Status Request
**Send:** `STATUS`
**Receive:**
```
AirPuff Status: Online
Time: 2025-10-09 20:18:10 UTC
Service: Active
```

## Scheduled Message Management

### Creating Scheduled Messages
1. **Via Web Interface**: `/imessage` page
2. **Via API**: `POST /api/v1/imessage/schedule`

**Schedule Options:**
- `daily 07:00` - Daily at 7:00 AM
- `daily 12:00` - Daily at 12:00 PM
- `daily 17:00` - Daily at 5:00 PM
- `hourly` - Every hour
- `on-demand` - Manual sending only

### Managing Scheduled Messages
- **View**: List all scheduled messages
- **Edit**: Modify schedule or recipient
- **Send Now**: Trigger immediate sending
- **Delete**: Remove scheduled message

## System Integration

### WebSocket Integration
- Real-time updates for scheduled messages
- Live status monitoring
- Connection management

### Database Integration
- User route storage
- Scheduled message persistence
- Weather data caching

### External Services
- **Fli-Rite API**: Weather data source
- **iMessage Bridge**: Message delivery
- **TimescaleDB**: Historical data

## Error Handling

### Common Errors
- **No Weather Data**: "No weather data available for the requested airports"
- **Route Not Found**: "Route 'MyRoute' not found"
- **Too Many Airports**: "Too many airports requested. Maximum 10 airports per request"
- **Unknown Command**: "Unknown command. Send 'HELP' for available commands"

### Fallback Behavior
- Database weather data preferred
- Fli-Rite API fallback
- Graceful error messages
- Service status reporting

## Security Considerations

### Authentication
- User-based route access
- API key validation
- Phone number verification

### Rate Limiting
- Maximum 10 airports per request
- Message length limits
- Request frequency controls

### Data Privacy
- User data isolation
- Secure message transmission
- Audit logging

## Monitoring and Logging

### Service Monitoring
- Connection status
- Message processing rates
- Error tracking
- Performance metrics

### Logging
- Incoming message processing
- Scheduled message delivery
- Error conditions
- User activity

## Troubleshooting

### Common Issues

**1. No Weather Data**
- Check database connectivity
- Verify Fli-Rite API access
- Check airport code validity

**2. Scheduled Messages Not Sending**
- Verify systemd timer status
- Check message configuration
- Review service logs

**3. iMessage Bridge Issues**
- Test bridge connectivity
- Verify API credentials
- Check message format

### Debug Commands
```bash
# Check service status
curl http://localhost:8000/api/v1/imessage/commands

# Test message processing
curl -X POST http://localhost:8000/api/v1/imessage/process \
  -H "Content-Type: application/json" \
  -d '{"sender": "+1234567890", "message": "KSFO KLAX"}'

# Test formatting
curl http://localhost:8000/api/v1/imessage/test
```

## Production Deployment

### Systemd Services
```bash
# Enable scheduled message processing
sudo systemctl enable airpuff-imessage.timer
sudo systemctl start airpuff-imessage.timer

# Check status
sudo systemctl status airpuff-imessage.timer
```

### Monitoring
- Service health checks
- Message delivery tracking
- Performance monitoring
- Error alerting

### Scaling
- Multiple iMessage bridge instances
- Load balancing
- Database optimization
- Caching strategies

## Future Enhancements

### Planned Features
- **Voice Integration**: Siri shortcuts
- **Group Messages**: Multiple recipients
- **Custom Formats**: User-defined output formats
- **Weather Alerts**: Threshold-based notifications
- **Route Optimization**: Weather-based routing suggestions

### Integration Opportunities
- **Apple Watch**: Quick weather checks
- **CarPlay**: In-flight weather updates
- **HomeKit**: Smart home integration
- **Shortcuts**: iOS automation

## Support

For issues or questions:
- Check the logs first
- Review the API documentation
- Test individual components
- Contact the development team

The iMessage integration provides a powerful, user-friendly way to access AirPuff's weather data directly from your phone, making it perfect for pilots who need quick weather updates while on the go.
