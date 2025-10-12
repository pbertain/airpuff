# AirPuff Examples

Practical examples and use cases for AirPuff 2.0 API and features.

## Table of Contents

- [API Examples](#api-examples)
- [WebSocket Examples](#websocket-examples)
- [cURL Examples](#curl-examples)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [Integration Examples](#integration-examples)
- [Automation Examples](#automation-examples)

## API Examples

### Basic Weather Queries

**Get Latest Weather:**
```bash
curl -X GET "http://localhost:8000/api/v1/weather/KSFO/latest" \
     -H "Accept: application/json"
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

**Get Historical Weather:**
```bash
curl -X GET "http://localhost:8000/api/v1/weather/KSFO/history?start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z&limit=100" \
     -H "Accept: application/json"
```

**Get Multiple Airports:**
```bash
curl -X GET "http://localhost:8000/api/v1/weather/batch" \
     -H "Content-Type: application/json" \
     -d '{"airports": ["KSFO", "KSEA", "KLAX"]}'
```

### Airport Management

**List Airports:**
```bash
curl -X GET "http://localhost:8000/api/v1/airports/?limit=50&search=San Francisco" \
     -H "Accept: application/json"
```

**Add New Airport:**
```bash
curl -X POST "http://localhost:8000/api/v1/airports/" \
     -H "Content-Type: application/json" \
     -d '{
       "icao": "KSFO",
       "name": "San Francisco International Airport",
       "city": "San Francisco",
       "state": "CA",
       "country": "USA",
       "latitude": 37.6213,
       "longitude": -122.3790,
       "elevation_ft": 13
     }'
```

**Get Airport Details:**
```bash
curl -X GET "http://localhost:8000/api/v1/airports/KSFO" \
     -H "Accept: application/json"
```

### Route Management

**Create Route:**
```bash
curl -X POST "http://localhost:8000/api/v1/routes/" \
     -H "Authorization: Bearer your-access-token" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "West Coast Route",
       "description": "Major West Coast airports",
       "airport_codes": ["KSFO", "KSEA", "KLAX", "KPDX"]
     }'
```

**Get Route with Weather:**
```bash
curl -X GET "http://localhost:8000/api/v1/routes/1" \
     -H "Authorization: Bearer your-access-token" \
     -H "Accept: application/json"
```

**Update Route:**
```bash
curl -X PUT "http://localhost:8000/api/v1/routes/1" \
     -H "Authorization: Bearer your-access-token" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated West Coast Route",
       "description": "Updated description",
       "airport_codes": ["KSFO", "KSEA", "KLAX", "KPDX", "KSAN"]
     }'
```

## WebSocket Examples

### Basic WebSocket Connection

**JavaScript Client:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to AirPuff WebSocket');
    
    // Subscribe to weather updates for specific airport
    ws.send(JSON.stringify({
        type: 'subscribe',
        airport: 'KSFO'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    if (data.type === 'weather_update') {
        console.log(`Weather update for ${data.icao}:`);
        console.log(`Temperature: ${data.data.temperature_c}°C`);
        console.log(`Wind: ${data.data.wind_dir_deg}° @ ${data.data.wind_speed_kts} kts`);
    }
};

ws.onclose = () => {
    console.log('Disconnected from AirPuff WebSocket');
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

**Python Client:**
```python
import asyncio
import websockets
import json

async def weather_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to weather updates
        await websocket.send(json.dumps({
            "type": "subscribe",
            "airport": "KSFO"
        }))
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'weather_update':
                print(f"Weather update for {data['icao']}:")
                print(f"Temperature: {data['data']['temperature_c']}°C")
                print(f"Wind: {data['data']['wind_dir_deg']}° @ {data['data']['wind_speed_kts']} kts")

asyncio.run(weather_client())
```

### Advanced WebSocket Usage

**Subscribe to Multiple Airports:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    // Subscribe to multiple airports
    ws.send(JSON.stringify({
        type: 'subscribe',
        airports: ['KSFO', 'KSEA', 'KLAX']
    }));
    
    // Subscribe to route updates
    ws.send(JSON.stringify({
        type: 'subscribe_route',
        route_id: 1
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'weather_update':
            updateWeatherDisplay(data);
            break;
        case 'route_update':
            updateRouteDisplay(data);
            break;
        case 'system_alert':
            showSystemAlert(data);
            break;
    }
};
```

## cURL Examples

### Weather Data

**Get Weather in Plain Text:**
```bash
curl http://localhost:8000/curl/v1/weather/KSFO
```

**Output:**
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

**Get Multiple Airports:**
```bash
curl "http://localhost:8000/curl/v1/weather/KSFO,KSEA,KLAX"
```

**Get Route Weather:**
```bash
curl http://localhost:8000/curl/v1/routes/1
```

### Airport Information

**List Airports:**
```bash
curl http://localhost:8000/curl/v1/airports/
```

**Get Airport Details:**
```bash
curl http://localhost:8000/curl/v1/airports/KSFO
```

### Authentication

**Get User Routes:**
```bash
curl -H "Authorization: Bearer your-access-token" \
     http://localhost:8000/curl/v1/routes/
```

## Python Examples

### Basic API Client

```python
import requests
import json
from datetime import datetime, timedelta

class AirPuffClient:
    def __init__(self, base_url="http://localhost:8000", access_token=None):
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"
    
    def get_weather(self, icao):
        """Get latest weather for airport."""
        response = requests.get(
            f"{self.base_url}/api/v1/weather/{icao}/latest",
            headers=self.headers
        )
        return response.json()
    
    def get_historical_weather(self, icao, start_time, end_time, limit=1000):
        """Get historical weather data."""
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": limit
        }
        response = requests.get(
            f"{self.base_url}/api/v1/weather/{icao}/history",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def get_airports(self, search=None, limit=100):
        """Get list of airports."""
        params = {"limit": limit}
        if search:
            params["search"] = search
        
        response = requests.get(
            f"{self.base_url}/api/v1/airports/",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def create_route(self, name, description, airport_codes):
        """Create a new route."""
        data = {
            "name": name,
            "description": description,
            "airport_codes": airport_codes
        }
        response = requests.post(
            f"{self.base_url}/api/v1/routes/",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_route(self, route_id):
        """Get route details with weather."""
        response = requests.get(
            f"{self.base_url}/api/v1/routes/{route_id}",
            headers=self.headers
        )
        return response.json()

# Usage examples
client = AirPuffClient()

# Get weather for San Francisco
weather = client.get_weather("KSFO")
print(f"Temperature: {weather['temperature_c']}°C")

# Get historical weather for last 24 hours
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=24)
historical = client.get_historical_weather("KSFO", start_time, end_time)
print(f"Found {len(historical['observations'])} observations")

# Search for airports
airports = client.get_airports(search="San Francisco")
for airport in airports['airports']:
    print(f"{airport['icao']} - {airport['name']}")

# Create a route
route = client.create_route(
    name="West Coast Route",
    description="Major West Coast airports",
    airport_codes=["KSFO", "KSEA", "KLAX"]
)
print(f"Created route: {route['name']}")
```

### Weather Analysis

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def analyze_weather_trends(icao, days=7):
    """Analyze weather trends for an airport."""
    client = AirPuffClient()
    
    # Get historical data
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    data = client.get_historical_weather(icao, start_time, end_time)
    
    # Convert to DataFrame
    df = pd.DataFrame(data['observations'])
    df['time'] = pd.to_datetime(df['time'])
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Temperature trend
    axes[0, 0].plot(df['time'], df['temperature_c'])
    axes[0, 0].set_title('Temperature Trend')
    axes[0, 0].set_ylabel('Temperature (°C)')
    
    # Wind speed trend
    axes[0, 1].plot(df['time'], df['wind_speed_kts'])
    axes[0, 1].set_title('Wind Speed Trend')
    axes[0, 1].set_ylabel('Wind Speed (kts)')
    
    # Visibility trend
    axes[1, 0].plot(df['time'], df['visibility_mi'])
    axes[1, 0].set_title('Visibility Trend')
    axes[1, 0].set_ylabel('Visibility (mi)')
    
    # Altimeter trend
    axes[1, 1].plot(df['time'], df['altimeter_hg'])
    axes[1, 1].set_title('Altimeter Trend')
    axes[1, 1].set_ylabel('Altimeter (inHg)')
    
    plt.tight_layout()
    plt.show()
    
    return df

# Analyze weather trends for San Francisco
df = analyze_weather_trends("KSFO", days=7)
print(f"Average temperature: {df['temperature_c'].mean():.1f}°C")
print(f"Average wind speed: {df['wind_speed_kts'].mean():.1f} kts")
```

### Route Planning

```python
def plan_flight_route(airports, check_weather=True):
    """Plan a flight route with weather information."""
    client = AirPuffClient()
    
    route_data = {
        "name": f"Route: {' -> '.join(airports)}",
        "description": f"Flight route through {len(airports)} airports",
        "airport_codes": airports
    }
    
    # Create route
    route = client.create_route(**route_data)
    print(f"Created route: {route['name']}")
    
    if check_weather:
        # Get weather for each airport
        for airport in route['airports']:
            weather = client.get_weather(airport['icao'])
            print(f"\n{airport['icao']} - {airport['name']}:")
            print(f"  Flight Category: {weather['flight_category']}")
            print(f"  Temperature: {weather['temperature_c']}°C")
            print(f"  Wind: {weather['wind_dir_deg']}° @ {weather['wind_speed_kts']} kts")
            print(f"  Visibility: {weather['visibility_mi']} mi")
            print(f"  Ceiling: {weather['ceiling_code']}")
    
    return route

# Plan a route from San Francisco to Seattle
route = plan_flight_route(["KSFO", "KSEA", "KLAX"])
```

## JavaScript Examples

### Weather Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>AirPuff Weather Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>AirPuff Weather Dashboard</h1>
    
    <div id="weather-container">
        <div id="current-weather"></div>
        <canvas id="weather-chart" width="400" height="200"></canvas>
    </div>
    
    <script>
        class AirPuffDashboard {
            constructor(baseUrl = 'http://localhost:8000') {
                this.baseUrl = baseUrl;
                this.chart = null;
                this.initChart();
            }
            
            async getWeather(icao) {
                const response = await fetch(`${this.baseUrl}/api/v1/weather/${icao}/latest`);
                return await response.json();
            }
            
            async getHistoricalWeather(icao, hours = 24) {
                const endTime = new Date();
                const startTime = new Date(endTime.getTime() - hours * 60 * 60 * 1000);
                
                const response = await fetch(
                    `${this.baseUrl}/api/v1/weather/${icao}/history?start_time=${startTime.toISOString()}&end_time=${endTime.toISOString()}&limit=1000`
                );
                return await response.json();
            }
            
            displayCurrentWeather(weather) {
                const container = document.getElementById('current-weather');
                container.innerHTML = `
                    <h2>${weather.icao} - Current Weather</h2>
                    <p><strong>Time:</strong> ${new Date(weather.time).toLocaleString()}</p>
                    <p><strong>Flight Category:</strong> ${weather.flight_category}</p>
                    <p><strong>Temperature:</strong> ${weather.temperature_c}°C (${weather.temperature_f}°F)</p>
                    <p><strong>Wind:</strong> ${weather.wind_dir_deg}° @ ${weather.wind_speed_kts} kts</p>
                    <p><strong>Visibility:</strong> ${weather.visibility_mi} mi</p>
                    <p><strong>Altimeter:</strong> ${weather.altimeter_hg} inHg</p>
                    <p><strong>Ceiling:</strong> ${weather.ceiling_code}</p>
                `;
            }
            
            initChart() {
                const ctx = document.getElementById('weather-chart').getContext('2d');
                this.chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: [],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: false
                            }
                        }
                    }
                });
            }
            
            updateChart(historicalData) {
                const labels = historicalData.observations.map(obs => 
                    new Date(obs.time).toLocaleTimeString()
                );
                const temperatures = historicalData.observations.map(obs => obs.temperature_c);
                
                this.chart.data.labels = labels;
                this.chart.data.datasets[0].data = temperatures;
                this.chart.update();
            }
            
            async loadWeather(icao) {
                try {
                    // Get current weather
                    const currentWeather = await this.getWeather(icao);
                    this.displayCurrentWeather(currentWeather);
                    
                    // Get historical weather
                    const historicalWeather = await this.getHistoricalWeather(icao);
                    this.updateChart(historicalWeather);
                    
                } catch (error) {
                    console.error('Error loading weather:', error);
                }
            }
        }
        
        // Initialize dashboard
        const dashboard = new AirPuffDashboard();
        
        // Load weather for San Francisco
        dashboard.loadWeather('KSFO');
        
        // Update every 5 minutes
        setInterval(() => {
            dashboard.loadWeather('KSFO');
        }, 5 * 60 * 1000);
    </script>
</body>
</html>
```

### Real-time Weather Updates

```javascript
class RealTimeWeather {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.ws = null;
        this.subscriptions = new Set();
    }
    
    connect() {
        this.ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws`);
        
        this.ws.onopen = () => {
            console.log('Connected to AirPuff WebSocket');
            this.resubscribe();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from AirPuff WebSocket');
            // Reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    subscribe(airport) {
        this.subscriptions.add(airport);
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'subscribe',
                airport: airport
            }));
        }
    }
    
    unsubscribe(airport) {
        this.subscriptions.delete(airport);
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'unsubscribe',
                airport: airport
            }));
        }
    }
    
    resubscribe() {
        for (const airport of this.subscriptions) {
            this.ws.send(JSON.stringify({
                type: 'subscribe',
                airport: airport
            }));
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'weather_update':
                this.onWeatherUpdate(data);
                break;
            case 'route_update':
                this.onRouteUpdate(data);
                break;
            case 'system_alert':
                this.onSystemAlert(data);
                break;
        }
    }
    
    onWeatherUpdate(data) {
        console.log(`Weather update for ${data.icao}:`);
        console.log(`Temperature: ${data.data.temperature_c}°C`);
        console.log(`Wind: ${data.data.wind_dir_deg}° @ ${data.data.wind_speed_kts} kts`);
        
        // Update UI
        this.updateWeatherDisplay(data);
    }
    
    onRouteUpdate(data) {
        console.log(`Route update for route ${data.route_id}`);
        this.updateRouteDisplay(data);
    }
    
    onSystemAlert(data) {
        console.log(`System alert: ${data.message}`);
        this.showAlert(data);
    }
    
    updateWeatherDisplay(data) {
        // Update weather display in UI
        const element = document.getElementById(`weather-${data.icao}`);
        if (element) {
            element.innerHTML = `
                <div class="weather-card">
                    <h3>${data.icao}</h3>
                    <p>Temperature: ${data.data.temperature_c}°C</p>
                    <p>Wind: ${data.data.wind_dir_deg}° @ ${data.data.wind_speed_kts} kts</p>
                    <p>Visibility: ${data.data.visibility_mi} mi</p>
                    <p>Category: ${data.data.flight_category}</p>
                </div>
            `;
        }
    }
    
    updateRouteDisplay(data) {
        // Update route display in UI
        const element = document.getElementById(`route-${data.route_id}`);
        if (element) {
            element.innerHTML = this.formatRouteData(data.data);
        }
    }
    
    showAlert(data) {
        // Show system alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning';
        alert.textContent = data.message;
        document.body.appendChild(alert);
        
        // Remove alert after 5 seconds
        setTimeout(() => {
            document.body.removeChild(alert);
        }, 5000);
    }
    
    formatRouteData(routeData) {
        let html = `<h3>${routeData.name}</h3>`;
        html += `<p>${routeData.description}</p>`;
        html += '<ul>';
        
        for (const airport of routeData.airports) {
            html += `<li>${airport.icao} - ${airport.name}</li>`;
            if (airport.weather) {
                html += `<ul><li>Category: ${airport.weather.flight_category}</li></ul>`;
            }
        }
        
        html += '</ul>';
        return html;
    }
}

// Usage
const realTimeWeather = new RealTimeWeather();
realTimeWeather.connect();

// Subscribe to weather updates for specific airports
realTimeWeather.subscribe('KSFO');
realTimeWeather.subscribe('KSEA');
realTimeWeather.subscribe('KLAX');
```

## Integration Examples

### Slack Integration

```python
import requests
import json
from datetime import datetime

class AirPuffSlackBot:
    def __init__(self, airpuff_url, slack_webhook_url):
        self.airpuff_url = airpuff_url
        self.slack_webhook_url = slack_webhook_url
    
    def get_weather(self, icao):
        response = requests.get(f"{self.airpuff_url}/api/v1/weather/{icao}/latest")
        return response.json()
    
    def send_slack_message(self, message):
        payload = {"text": message}
        response = requests.post(self.slack_webhook_url, json=payload)
        return response.status_code == 200
    
    def format_weather_message(self, weather):
        message = f"🌤️ *Weather Update for {weather['icao']}*\n"
        message += f"⏰ Time: {datetime.fromisoformat(weather['time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M UTC')}\n"
        message += f"✈️ Flight Category: {weather['flight_category']}\n"
        message += f"🌡️ Temperature: {weather['temperature_c']}°C ({weather['temperature_f']}°F)\n"
        message += f"💨 Wind: {weather['wind_dir_deg']}° @ {weather['wind_speed_kts']} kts\n"
        message += f"👁️ Visibility: {weather['visibility_mi']} mi\n"
        message += f"📊 Altimeter: {weather['altimeter_hg']} inHg\n"
        message += f"☁️ Ceiling: {weather['ceiling_code']}\n"
        return message
    
    def send_weather_alert(self, icao):
        weather = self.get_weather(icao)
        message = self.format_weather_message(weather)
        return self.send_slack_message(message)

# Usage
bot = AirPuffSlackBot(
    airpuff_url="http://localhost:8000",
    slack_webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
)

# Send weather alert for San Francisco
bot.send_weather_alert("KSFO")
```

### Discord Integration

```python
import requests
import json
from datetime import datetime

class AirPuffDiscordBot:
    def __init__(self, airpuff_url, discord_webhook_url):
        self.airpuff_url = airpuff_url
        self.discord_webhook_url = discord_webhook_url
    
    def get_weather(self, icao):
        response = requests.get(f"{self.airpuff_url}/api/v1/weather/{icao}/latest")
        return response.json()
    
    def send_discord_message(self, message, embeds=None):
        payload = {"content": message}
        if embeds:
            payload["embeds"] = embeds
        
        response = requests.post(self.discord_webhook_url, json=payload)
        return response.status_code == 204
    
    def create_weather_embed(self, weather):
        embed = {
            "title": f"Weather Update for {weather['icao']}",
            "color": 0x00ff00 if weather['flight_category'] == 'VFR' else 0xff0000,
            "fields": [
                {"name": "Time", "value": datetime.fromisoformat(weather['time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M UTC'), "inline": True},
                {"name": "Flight Category", "value": weather['flight_category'], "inline": True},
                {"name": "Temperature", "value": f"{weather['temperature_c']}°C ({weather['temperature_f']}°F)", "inline": True},
                {"name": "Wind", "value": f"{weather['wind_dir_deg']}° @ {weather['wind_speed_kts']} kts", "inline": True},
                {"name": "Visibility", "value": f"{weather['visibility_mi']} mi", "inline": True},
                {"name": "Altimeter", "value": f"{weather['altimeter_hg']} inHg", "inline": True}
            ],
            "footer": {"text": "AirPuff Weather System"},
            "timestamp": weather['time']
        }
        return embed
    
    def send_weather_alert(self, icao):
        weather = self.get_weather(icao)
        embed = self.create_weather_embed(weather)
        return self.send_discord_message("", [embed])

# Usage
bot = AirPuffDiscordBot(
    airpuff_url="http://localhost:8000",
    discord_webhook_url="https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
)

# Send weather alert for San Francisco
bot.send_weather_alert("KSFO")
```

## Automation Examples

### Weather Monitoring Script

```python
#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class WeatherMonitor:
    def __init__(self, airpuff_url, email_config):
        self.airpuff_url = airpuff_url
        self.email_config = email_config
        self.last_weather = {}
    
    def get_weather(self, icao):
        response = requests.get(f"{self.airpuff_url}/api/v1/weather/{icao}/latest")
        return response.json()
    
    def check_weather_changes(self, icao):
        current_weather = self.get_weather(icao)
        
        if icao in self.last_weather:
            last_weather = self.last_weather[icao]
            
            # Check for significant changes
            changes = []
            
            if current_weather['flight_category'] != last_weather['flight_category']:
                changes.append(f"Flight category changed from {last_weather['flight_category']} to {current_weather['flight_category']}")
            
            if abs(current_weather['temperature_c'] - last_weather['temperature_c']) > 5:
                changes.append(f"Temperature changed by {current_weather['temperature_c'] - last_weather['temperature_c']:.1f}°C")
            
            if abs(current_weather['wind_speed_kts'] - last_weather['wind_speed_kts']) > 10:
                changes.append(f"Wind speed changed by {current_weather['wind_speed_kts'] - last_weather['wind_speed_kts']:.1f} kts")
            
            if abs(current_weather['visibility_mi'] - last_weather['visibility_mi']) > 2:
                changes.append(f"Visibility changed by {current_weather['visibility_mi'] - last_weather['visibility_mi']:.1f} mi")
            
            if changes:
                self.send_alert(icao, current_weather, changes)
        
        self.last_weather[icao] = current_weather
    
    def send_alert(self, icao, weather, changes):
        subject = f"Weather Alert for {icao}"
        body = f"Weather changes detected for {icao}:\n\n"
        
        for change in changes:
            body += f"• {change}\n"
        
        body += f"\nCurrent Weather:\n"
        body += f"• Flight Category: {weather['flight_category']}\n"
        body += f"• Temperature: {weather['temperature_c']}°C\n"
        body += f"• Wind: {weather['wind_dir_deg']}° @ {weather['wind_speed_kts']} kts\n"
        body += f"• Visibility: {weather['visibility_mi']} mi\n"
        body += f"• Altimeter: {weather['altimeter_hg']} inHg\n"
        
        self.send_email(subject, body)
    
    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['username'], self.email_config['password'])
        text = msg.as_string()
        server.sendmail(self.email_config['from'], self.email_config['to'], text)
        server.quit()
    
    def monitor_airports(self, airports, interval=300):
        """Monitor airports for weather changes."""
        print(f"Starting weather monitoring for {airports}")
        print(f"Check interval: {interval} seconds")
        
        while True:
            for icao in airports:
                try:
                    self.check_weather_changes(icao)
                    print(f"Checked weather for {icao} at {datetime.now()}")
                except Exception as e:
                    print(f"Error checking weather for {icao}: {e}")
            
            time.sleep(interval)

# Usage
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'from': 'your-email@gmail.com',
    'to': 'recipient@example.com'
}

monitor = WeatherMonitor("http://localhost:8000", email_config)
monitor.monitor_airports(["KSFO", "KSEA", "KLAX"], interval=300)  # Check every 5 minutes
```

### Automated Route Planning

```python
#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timedelta

class AutomatedRoutePlanner:
    def __init__(self, airpuff_url, access_token):
        self.airpuff_url = airpuff_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_weather(self, icao):
        response = requests.get(f"{self.airpuff_url}/api/v1/weather/{icao}/latest")
        return response.json()
    
    def evaluate_weather_conditions(self, weather):
        """Evaluate weather conditions for flight planning."""
        score = 100  # Start with perfect score
        
        # Flight category scoring
        if weather['flight_category'] == 'VFR':
            score -= 0
        elif weather['flight_category'] == 'MVFR':
            score -= 20
        elif weather['flight_category'] == 'IFR':
            score -= 50
        elif weather['flight_category'] == 'LIFR':
            score -= 80
        
        # Wind scoring
        if weather['wind_speed_kts'] > 20:
            score -= 30
        elif weather['wind_speed_kts'] > 15:
            score -= 20
        elif weather['wind_speed_kts'] > 10:
            score -= 10
        
        # Visibility scoring
        if weather['visibility_mi'] < 3:
            score -= 40
        elif weather['visibility_mi'] < 5:
            score -= 20
        elif weather['visibility_mi'] < 10:
            score -= 10
        
        return max(0, score)
    
    def plan_route(self, airports, departure_time=None):
        """Plan a route with weather evaluation."""
        if departure_time is None:
            departure_time = datetime.utcnow() + timedelta(hours=1)
        
        route_evaluation = {
            "airports": [],
            "total_score": 0,
            "recommendation": "",
            "departure_time": departure_time.isoformat()
        }
        
        for icao in airports:
            weather = self.get_weather(icao)
            score = self.evaluate_weather_conditions(weather)
            
            airport_eval = {
                "icao": icao,
                "weather": weather,
                "score": score,
                "recommendation": self.get_recommendation(score)
            }
            
            route_evaluation["airports"].append(airport_eval)
            route_evaluation["total_score"] += score
        
        route_evaluation["total_score"] /= len(airports)
        route_evaluation["recommendation"] = self.get_route_recommendation(route_evaluation["total_score"])
        
        return route_evaluation
    
    def get_recommendation(self, score):
        """Get recommendation based on weather score."""
        if score >= 80:
            return "Excellent conditions"
        elif score >= 60:
            return "Good conditions"
        elif score >= 40:
            return "Marginal conditions"
        else:
            return "Poor conditions"
    
    def get_route_recommendation(self, total_score):
        """Get route recommendation based on total score."""
        if total_score >= 80:
            return "Route recommended - excellent weather conditions"
        elif total_score >= 60:
            return "Route acceptable - good weather conditions"
        elif total_score >= 40:
            return "Route marginal - consider alternatives"
        else:
            return "Route not recommended - poor weather conditions"
    
    def create_route(self, name, airports):
        """Create a route in AirPuff."""
        data = {
            "name": name,
            "description": f"Automated route planning for {', '.join(airports)}",
            "airport_codes": airports
        }
        
        response = requests.post(f"{self.airpuff_url}/api/v1/routes/", headers=self.headers, json=data)
        return response.json()

# Usage
planner = AutomatedRoutePlanner("http://localhost:8000", "your-access-token")

# Plan a route
route_eval = planner.plan_route(["KSFO", "KSEA", "KLAX"])
print(f"Route Score: {route_eval['total_score']:.1f}")
print(f"Recommendation: {route_eval['recommendation']}")

for airport in route_eval["airports"]:
    print(f"{airport['icao']}: {airport['score']:.1f} - {airport['recommendation']}")

# Create route if conditions are good
if route_eval["total_score"] >= 60:
    route = planner.create_route("West Coast Route", ["KSFO", "KSEA", "KLAX"])
    print(f"Created route: {route['name']}")
```

These examples demonstrate the full range of AirPuff 2.0 capabilities, from basic API usage to advanced integrations and automation. Each example includes complete, working code that can be adapted for specific use cases.
