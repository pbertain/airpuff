# cURL API Endpoints

The cURL API provides clean, clear-text output for easy command-line usage. All endpoints return plain text instead of JSON, making them perfect for shell scripts and quick data retrieval.

## Base URL

```
http://localhost:8000/curl/v1/
```

## Airports

### List Airports
```bash
curl http://localhost:8000/curl/v1/airports
curl http://localhost:8000/curl/v1/airports?search=KSFO
curl http://localhost:8000/curl/v1/airports?limit=50
```

### Get Airport Details
```bash
curl http://localhost:8000/curl/v1/airports/KSFO
```

### Create Airport
```bash
curl -X POST http://localhost:8000/curl/v1/airports \
  -H "Content-Type: application/json" \
  -d '{
    "icao": "KSFO",
    "name": "San Francisco International",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "latitude": 37.6213,
    "longitude": -122.3790,
    "elevation_ft": 13,
    "atis_phone": "650-821-7731"
  }'
```

### Update Airport
```bash
curl -X PUT http://localhost:8000/curl/v1/airports/KSFO \
  -H "Content-Type: application/json" \
  -d '{
    "name": "San Francisco International Airport",
    "atis_phone": "650-821-7731"
  }'
```

### Delete Airport
```bash
curl -X DELETE http://localhost:8000/curl/v1/airports/KSFO
```

## Weather

### Current Weather
```bash
curl http://localhost:8000/curl/v1/weather/KSFO
```

### Weather History
```bash
curl http://localhost:8000/curl/v1/weather/KSFO/history
curl http://localhost:8000/curl/v1/weather/KSFO/history?hours=48
```

### Multiple Airports
```bash
curl "http://localhost:8000/curl/v1/weather?icaos=KSFO,KLAX,KJFK"
```

## Routes

### List Routes
```bash
curl http://localhost:8000/curl/v1/routes
curl http://localhost:8000/curl/v1/routes?user_id=1
curl http://localhost:8000/curl/v1/routes?public_only=true
```

### Get Route Details
```bash
curl http://localhost:8000/curl/v1/routes/1
```

### Create Route
```bash
curl -X POST http://localhost:8000/curl/v1/routes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "West Coast Commute",
    "description": "Regular flight route along the west coast",
    "airport_icaos": ["KSFO", "KLAX", "KSEA"],
    "is_public": false,
    "is_favorite": true
  }'
```

### Update Route
```bash
curl -X PUT http://localhost:8000/curl/v1/routes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated West Coast Route",
    "airport_icaos": ["KSFO", "KLAX", "KSEA", "KPDX"]
  }'
```

### Delete Route
```bash
curl -X DELETE http://localhost:8000/curl/v1/routes/1
```

## Example Output

### Airport Details
```
ICAO: KSFO
Name: San Francisco International Airport
Location: San Francisco, CA, USA
Coordinates: 37.6213, -122.3790
Elevation: 13 ft
ATIS Phone: 650-821-7731
Tower Phone: 650-821-7732
---
```

### Weather Data
```
Airport: KSFO - San Francisco International Airport
Observation Time: 2024-01-15 14:30:00 UTC
Raw METAR: KSFO 151430Z 28015G25KT 10SM FEW250 15/08 A2992

Current Conditions:
  Flight Category: VFR
  Temperature: 59°F (15°C)
  Dewpoint: 46°F (8°C)
  Temp-Dewpoint Spread: 13°F
  Wind: 280° @ 15 kts (17 mph)
  Wind Gust: 25 kts
  Visibility: 10.0 SM (16093 m)
  Ceiling: 25000 ft AGL (FEW)
  Altimeter: 29.92" Hg (1013.2 mb)
  Wind Chill: N/A°F
  Heat Index: N/A°F
  METAR Type: METAR
  Auto Station: AUTO
---
```

### Route Summary
```
Route: West Coast Commute
Description: Regular flight route along the west coast
User ID: 1
Public: No
Favorite: Yes
Created: 2024-01-15 10:00:00 UTC
Updated: 2024-01-15 10:00:00 UTC

Airports:
  1. KSFO - San Francisco International Airport
     San Francisco, CA USA
  2. KLAX - Los Angeles International Airport
     Los Angeles, CA USA
  3. KSEA - Seattle-Tacoma International Airport
     Seattle, WA USA
---
```

## Error Handling

All endpoints return appropriate HTTP status codes and clear error messages:

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error messages are returned in plain text format for easy parsing in shell scripts.
