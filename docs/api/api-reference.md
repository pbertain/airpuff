# AirPuff API Reference

Complete API documentation for AirPuff 2.0, including all endpoints, authentication, and examples.

## Table of Contents

- [Authentication](#authentication)
- [Core API Endpoints](#core-api-endpoints)
- [cURL-Friendly Endpoints](#curl-friendly-endpoints)
- [WebSocket API](#websocket-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Authentication

### OAuth 2.0 Flow

AirPuff uses OAuth 2.0 with PKCE for secure authentication.

**Supported Providers:**
- Google OAuth 2.0
- Apple Sign-In

### Authentication Endpoints

```http
# Get authorization URL
GET /api/v1/auth/authorize/{provider}
```

**Parameters:**
- `provider`: `google` or `apple`

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/oauth/authorize?...",
  "state": "random-state-string",
  "code_verifier": "code-verifier-string"
}
```

```http
# Exchange authorization code for tokens
POST /api/v1/auth/token
```

**Request Body:**
```json
{
  "provider": "google",
  "code": "authorization-code",
  "state": "state-string",
  "code_verifier": "code-verifier-string"
}
```

**Response:**
```json
{
  "access_token": "jwt-access-token",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh-token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "is_active": true
  }
}
```

### Using Access Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer your-access-token
```

## Core API Endpoints

### Health & Status

#### Application Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "2.0.0",
  "environment": "production"
}
```

#### API Health
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "healthy"
  },
  "version": "2.0.0"
}
```

### Airports

#### List Airports
```http
GET /api/v1/airports/
```

**Query Parameters:**
- `limit`: Number of airports to return (default: 100)
- `offset`: Number of airports to skip (default: 0)
- `search`: Search by ICAO code, name, city, or state
- `country`: Filter by country code

**Response:**
```json
{
  "airports": [
    {
      "id": 1,
      "icao": "KSFO",
      "name": "San Francisco International Airport",
      "city": "San Francisco",
      "state": "CA",
      "country": "USA",
      "latitude": 37.6213,
      "longitude": -122.3790,
      "elevation_ft": 13,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

#### Get Airport by ICAO
```http
GET /api/v1/airports/{icao}
```

**Response:**
```json
{
  "id": 1,
  "icao": "KSFO",
  "name": "San Francisco International Airport",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA",
  "latitude": 37.6213,
  "longitude": -122.3790,
  "elevation_ft": 13,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Add Airport
```http
POST /api/v1/airports/
```

**Request Body:**
```json
{
  "icao": "KSFO",
  "name": "San Francisco International Airport",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA",
  "latitude": 37.6213,
  "longitude": -122.3790,
  "elevation_ft": 13
}
```

**Response:**
```json
{
  "id": 1,
  "icao": "KSFO",
  "name": "San Francisco International Airport",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA",
  "latitude": 37.6213,
  "longitude": -122.3790,
  "elevation_ft": 13,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Weather Data

#### Latest Weather
```http
GET /api/v1/weather/{icao}/latest
```

**Response:**
```json
{
  "airport_id": 1,
  "icao": "KSFO",
  "time": "2024-01-01T12:00:00Z",
  "flight_category": "VFR",
  "temperature_c": 20.0,
  "dewpoint_c": 15.0,
  "wind_dir_deg": 270,
  "wind_speed_kts": 10,
  "visibility_mi": 10.0,
  "altimeter_hg": 29.92,
  "ceiling_code": "CLR",
  "raw_metar": "KSFO 011200Z 27010KT 10SM CLR 20/15 A2992"
}
```

#### Historical Weather
```http
GET /api/v1/weather/{icao}/history
```

**Query Parameters:**
- `start_time`: Start time (ISO 8601 format)
- `end_time`: End time (ISO 8601 format)
- `limit`: Number of records to return (default: 1000)

**Response:**
```json
{
  "airport_id": 1,
  "icao": "KSFO",
  "observations": [
    {
      "time": "2024-01-01T12:00:00Z",
      "flight_category": "VFR",
      "temperature_c": 20.0,
      "dewpoint_c": 15.0,
      "wind_dir_deg": 270,
      "wind_speed_kts": 10,
      "visibility_mi": 10.0,
      "altimeter_hg": 29.92,
      "ceiling_code": "CLR",
      "raw_metar": "KSFO 011200Z 27010KT 10SM CLR 20/15 A2992"
    }
  ],
  "total": 1,
  "start_time": "2024-01-01T12:00:00Z",
  "end_time": "2024-01-01T12:00:00Z"
}
```

### Routes

#### List Routes
```http
GET /api/v1/routes/
```

**Headers:**
```
Authorization: Bearer your-access-token
```

**Response:**
```json
{
  "routes": [
    {
      "id": 1,
      "name": "Sac Valley Route",
      "description": "Sacramento Valley airports",
      "airports": [
        {
          "id": 1,
          "icao": "KSAC",
          "name": "Sacramento Executive Airport",
          "sequence": 1
        }
      ],
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1
}
```

#### Create Route
```http
POST /api/v1/routes/
```

**Headers:**
```
Authorization: Bearer your-access-token
```

**Request Body:**
```json
{
  "name": "Sac Valley Route",
  "description": "Sacramento Valley airports",
  "airport_codes": ["KSAC", "KDWA", "KWLW"]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Sac Valley Route",
  "description": "Sacramento Valley airports",
  "airports": [
    {
      "id": 1,
      "icao": "KSAC",
      "name": "Sacramento Executive Airport",
      "sequence": 1
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Get Route Details
```http
GET /api/v1/routes/{id}
```

**Headers:**
```
Authorization: Bearer your-access-token
```

**Response:**
```json
{
  "id": 1,
  "name": "Sac Valley Route",
  "description": "Sacramento Valley airports",
  "airports": [
    {
      "id": 1,
      "icao": "KSAC",
      "name": "Sacramento Executive Airport",
      "sequence": 1,
      "weather": {
        "time": "2024-01-01T12:00:00Z",
        "flight_category": "VFR",
        "temperature_c": 20.0,
        "dewpoint_c": 15.0,
        "wind_dir_deg": 270,
        "wind_speed_kts": 10,
        "visibility_mi": 10.0,
        "altimeter_hg": 29.92,
        "ceiling_code": "CLR"
      }
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Real-time Updates

#### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to AirPuff WebSocket');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Weather update:', data);
};

ws.onclose = () => {
    console.log('Disconnected from AirPuff WebSocket');
};
```

#### WebSocket Message Types

**Weather Update:**
```json
{
  "type": "weather_update",
  "airport_id": 1,
  "icao": "KSFO",
  "data": {
    "time": "2024-01-01T12:00:00Z",
    "flight_category": "VFR",
    "temperature_c": 20.0,
    "dewpoint_c": 15.0,
    "wind_dir_deg": 270,
    "wind_speed_kts": 10,
    "visibility_mi": 10.0,
    "altimeter_hg": 29.92,
    "ceiling_code": "CLR"
  }
}
```

**Route Update:**
```json
{
  "type": "route_update",
  "route_id": 1,
  "data": {
    "name": "Sac Valley Route",
    "airports": [
      {
        "icao": "KSAC",
        "weather": {
          "flight_category": "VFR",
          "temperature_c": 20.0
        }
      }
    ]
  }
}
```

## cURL-Friendly Endpoints

AirPuff provides plain-text endpoints for command-line usage and scripting.

### Airport Endpoints

#### List Airports
```bash
curl http://localhost:8000/curl/v1/airports/
```

**Response:**
```
KSFO - San Francisco International Airport (San Francisco, CA, USA)
KSEA - Seattle-Tacoma International Airport (Seattle, WA, USA)
KLAX - Los Angeles International Airport (Los Angeles, CA, USA)
```

#### Get Airport Details
```bash
curl http://localhost:8000/curl/v1/airports/KSFO
```

**Response:**
```
KSFO - San Francisco International Airport
Location: San Francisco, CA, USA
Coordinates: 37.6213°N, 122.3790°W
Elevation: 13 ft
```

### Weather Endpoints

#### Get Weather
```bash
curl http://localhost:8000/curl/v1/weather/KSFO
```

**Response:**
```
KSFO - San Francisco International Airport
Time: 2024-01-01T12:00:00Z
Flight Category: VFR
Temperature: 20.0°C (68.0°F)
Dewpoint: 15.0°C (59.0°F)
Wind: 270° @ 10 kts
Visibility: 10.0 mi
Altimeter: 29.92 inHg
Ceiling: Clear
Raw METAR: KSFO 011200Z 27010KT 10SM CLR 20/15 A2992
```

#### Get Route Weather
```bash
curl http://localhost:8000/curl/v1/routes/1
```

**Response:**
```
Sac Valley Route
Description: Sacramento Valley airports

KSAC - Sacramento Executive Airport
VFR - 20.0°C - 270°@10 - 10.0mi - CLR - 29.92

KDWA - Yolo County Airport
VFR - 22.0°C - 280°@8 - 10.0mi - CLR - 29.90

KWLW - Willows-Glenn County Airport
VFR - 25.0°C - 270°@12 - 10.0mi - CLR - 29.88
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "request-id"
}
```

### Common Error Codes

- `AIRPORT_NOT_FOUND`: Airport with specified ICAO code not found
- `INVALID_ICAO_CODE`: Invalid ICAO code format
- `WEATHER_DATA_UNAVAILABLE`: Weather data not available for airport
- `ROUTE_NOT_FOUND`: Route with specified ID not found
- `UNAUTHORIZED`: Authentication required
- `RATE_LIMIT_EXCEEDED`: Too many requests

## Rate Limiting

### Limits

- **Unauthenticated**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **WebSocket**: 10 connections per IP

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Exceeded Limit Response

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3600
}
```

## Examples

### Python Examples

#### Basic API Usage
```python
import requests

# Get latest weather
response = requests.get('http://localhost:8000/api/v1/weather/KSFO/latest')
weather = response.json()
print(f"Temperature: {weather['temperature_c']}°C")

# Get airport list
response = requests.get('http://localhost:8000/api/v1/airports/')
airports = response.json()
for airport in airports['airports']:
    print(f"{airport['icao']} - {airport['name']}")
```

#### Authenticated Requests
```python
import requests

# Authenticate
auth_response = requests.post('http://localhost:8000/api/v1/auth/token', json={
    'provider': 'google',
    'code': 'authorization-code',
    'state': 'state-string',
    'code_verifier': 'code-verifier-string'
})
tokens = auth_response.json()
access_token = tokens['access_token']

# Use access token
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/routes/', headers=headers)
routes = response.json()
```

#### WebSocket Client
```python
import asyncio
import websockets
import json

async def weather_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data['type'] == 'weather_update':
                print(f"Weather update for {data['icao']}: {data['data']['temperature_c']}°C")

asyncio.run(weather_client())
```

### JavaScript Examples

#### Fetch API
```javascript
// Get latest weather
fetch('http://localhost:8000/api/v1/weather/KSFO/latest')
    .then(response => response.json())
    .then(weather => {
        console.log(`Temperature: ${weather.temperature_c}°C`);
    });

// Get airport list
fetch('http://localhost:8000/api/v1/airports/')
    .then(response => response.json())
    .then(data => {
        data.airports.forEach(airport => {
            console.log(`${airport.icao} - ${airport.name}`);
        });
    });
```

#### WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to AirPuff WebSocket');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'weather_update') {
        console.log(`Weather update for ${data.icao}: ${data.data.temperature_c}°C`);
    }
};

ws.onclose = () => {
    console.log('Disconnected from AirPuff WebSocket');
};
```

### cURL Examples

#### Basic Requests
```bash
# Get health status
curl http://localhost:8000/health

# Get airport list
curl http://localhost:8000/api/v1/airports/

# Get weather for specific airport
curl http://localhost:8000/api/v1/weather/KSFO/latest

# Get weather in plain text
curl http://localhost:8000/curl/v1/weather/KSFO
```

#### Authenticated Requests
```bash
# Get user routes
curl -H "Authorization: Bearer your-access-token" \
     http://localhost:8000/api/v1/routes/

# Create new route
curl -X POST \
     -H "Authorization: Bearer your-access-token" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Route", "airport_codes": ["KSFO", "KSEA"]}' \
     http://localhost:8000/api/v1/routes/
```

## Advanced Features

### Data Migration

#### RRD Data Migration
```bash
# Start migration
curl -X POST http://localhost:8000/api/v1/migration/rrd/migrate \
     -H "Content-Type: application/json" \
     -d '{"rrd_path": "/var/airpuff/rrd-data"}'

# Check migration status
curl http://localhost:8000/api/v1/migration/rrd/status

# Get RRD airports
curl http://localhost:8000/api/v1/migration/rrd/airports
```

### Grafana Integration

#### Dashboard Access
```bash
# Get Grafana status
curl http://localhost:8000/api/v1/grafana/status

# Get dashboard URLs
curl http://localhost:8000/api/v1/grafana/dashboards
```

### iMessage Integration

#### Process iMessage
```bash
# Process incoming iMessage
curl -X POST http://localhost:8000/api/v1/imessage/process \
     -H "Content-Type: application/json" \
     -d '{"message": "KSFO KSEA KLAX"}'

# Test weather format
curl http://localhost:8000/api/v1/imessage/test-format/KSFO
```

This comprehensive API reference covers all aspects of the AirPuff API, from basic usage to advanced features. For more detailed examples and use cases, see the [Examples](docs/examples/) directory.
