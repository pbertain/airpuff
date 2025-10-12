/**
 * WebSocket client for AirPuff real-time updates
 */

class AirPuffWebSocket {
    constructor(userId = null) {
        this.userId = userId;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.subscriptions = new Set();
        this.messageHandlers = new Map();
        
        // Default message handlers
        this.registerHandler('weather_update', this.handleWeatherUpdate.bind(this));
        this.registerHandler('route_alert', this.handleRouteAlert.bind(this));
        this.registerHandler('subscription_confirmed', this.handleSubscriptionConfirmed.bind(this));
        this.registerHandler('error', this.handleError.bind(this));
        this.registerHandler('pong', this.handlePong.bind(this));
    }
    
    connect() {
        try {
            const wsUrl = this.userId 
                ? `ws://localhost:8000/ws/user/${this.userId}`
                : 'ws://localhost:8000/ws';
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnectionChange(true);
                
                // Send ping to verify connection
                this.ping();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.onConnectionChange(false);
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }
    
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }
    
    subscribeToAirport(icao) {
        this.send({
            type: 'subscribe_airport',
            icao: icao.toUpperCase()
        });
        this.subscriptions.add(`airport:${icao.toUpperCase()}`);
    }
    
    subscribeToRoute(routeId) {
        this.send({
            type: 'subscribe_route',
            route_id: routeId
        });
        this.subscriptions.add(`route:${routeId}`);
    }
    
    unsubscribeFromAirport(icao) {
        this.send({
            type: 'unsubscribe_airport',
            icao: icao.toUpperCase()
        });
        this.subscriptions.delete(`airport:${icao.toUpperCase()}`);
    }
    
    unsubscribeFromRoute(routeId) {
        this.send({
            type: 'unsubscribe_route',
            route_id: routeId
        });
        this.subscriptions.delete(`route:${routeId}`);
    }
    
    ping() {
        this.send({
            type: 'ping',
            timestamp: new Date().toISOString()
        });
    }
    
    registerHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
    }
    
    handleMessage(data) {
        const handler = this.messageHandlers.get(data.type);
        if (handler) {
            handler(data);
        } else {
            console.log('Unhandled WebSocket message:', data);
        }
    }
    
    handleWeatherUpdate(data) {
        console.log('Weather update received:', data);
        
        // Update weather display
        this.updateWeatherDisplay(data.airport, data.data);
        
        // Show notification
        this.showNotification(`Weather update for ${data.airport}`, 'info');
    }
    
    handleRouteAlert(data) {
        console.log('Route alert received:', data);
        
        // Show alert notification
        const alertLevels = {
            1: { class: 'warning', icon: '⚠️' },
            2: { class: 'danger', icon: '🚨' },
            3: { class: 'critical', icon: '🔥' }
        };
        
        const alert = alertLevels[data.alert_level] || { class: 'info', icon: 'ℹ️' };
        
        this.showNotification(
            `${alert.icon} ${data.message}`,
            alert.class,
            10000 // Show for 10 seconds
        );
        
        // Update route display if visible
        this.updateRouteDisplay(data.route_id, data);
    }
    
    handleSubscriptionConfirmed(data) {
        console.log('Subscription confirmed:', data);
        this.showNotification(data.message, 'success', 3000);
    }
    
    handleError(data) {
        console.error('WebSocket error:', data.message);
        this.showNotification(`Error: ${data.message}`, 'danger');
    }
    
    handlePong(data) {
        console.log('Pong received:', data.timestamp);
    }
    
    updateWeatherDisplay(icao, weatherData) {
        // Find weather elements for this airport
        const weatherElements = document.querySelectorAll(`[data-airport="${icao}"]`);
        
        weatherElements.forEach(element => {
            // Update flight category
            const categoryElement = element.querySelector('.flight-category');
            if (categoryElement && weatherData.flight_category) {
                categoryElement.textContent = weatherData.flight_category;
                categoryElement.className = `flight-category badge ${this.getCategoryClass(weatherData.flight_category)}`;
            }
            
            // Update temperature
            const tempElement = element.querySelector('.temperature');
            if (tempElement && weatherData.temp_c !== null) {
                tempElement.textContent = `${weatherData.temp_c}°C`;
            }
            
            // Update wind
            const windElement = element.querySelector('.wind');
            if (windElement && weatherData.wind_dir_degrees !== null && weatherData.wind_speed_kt !== null) {
                windElement.textContent = `${weatherData.wind_dir_degrees}°@${weatherData.wind_speed_kt}kt`;
            }
            
            // Update visibility
            const visElement = element.querySelector('.visibility');
            if (visElement && weatherData.visibility_mi !== null) {
                visElement.textContent = `${weatherData.visibility_mi}SM`;
            }
            
            // Add update timestamp
            const timestampElement = element.querySelector('.update-time');
            if (timestampElement) {
                timestampElement.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
            }
        });
    }
    
    updateRouteDisplay(routeId, alertData) {
        // Find route elements
        const routeElements = document.querySelectorAll(`[data-route-id="${routeId}"]`);
        
        routeElements.forEach(element => {
            // Add alert indicator
            const alertElement = element.querySelector('.route-alert');
            if (alertElement) {
                alertElement.innerHTML = `
                    <span class="badge bg-danger">
                        🚨 Alert: ${alertData.airport} - ${alertData.weather_data.flight_category}
                    </span>
                `;
            }
        });
    }
    
    getCategoryClass(category) {
        const classes = {
            'VFR': 'bg-success',
            'MVFR': 'bg-warning',
            'IFR': 'bg-danger',
            'LIFR': 'bg-dark'
        };
        return classes[category] || 'bg-secondary';
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        }
    }
    
    onConnectionChange(connected) {
        // Override this method to handle connection state changes
        console.log(`WebSocket ${connected ? 'connected' : 'disconnected'}`);
        
        // Update connection indicator if it exists
        const indicator = document.getElementById('ws-connection-indicator');
        if (indicator) {
            indicator.className = `badge ${connected ? 'bg-success' : 'bg-danger'}`;
            indicator.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }
    
    getConnectionStatus() {
        return {
            connected: this.isConnected,
            subscriptions: Array.from(this.subscriptions),
            reconnectAttempts: this.reconnectAttempts
        };
    }
}

// Global WebSocket instance
let airpuffWS = null;

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get user ID from localStorage or page data
    const token = localStorage.getItem('airpuff_token');
    let userId = null;
    
    if (token) {
        // In a real app, you'd decode the JWT to get user ID
        // For now, we'll use a placeholder
        userId = 1; // This should be extracted from the token
    }
    
    // Initialize WebSocket
    airpuffWS = new AirPuffWebSocket(userId);
    airpuffWS.connect();
    
    // Add connection indicator to page
    addConnectionIndicator();
    
    // Auto-subscribe to visible airports
    autoSubscribeToAirports();
});

function addConnectionIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'ws-connection-indicator';
    indicator.className = 'badge bg-danger';
    indicator.textContent = 'Disconnected';
    indicator.style.cssText = 'position: fixed; top: 10px; left: 10px; z-index: 9999;';
    document.body.appendChild(indicator);
}

function autoSubscribeToAirports() {
    // Subscribe to all visible airports
    const airportElements = document.querySelectorAll('[data-airport]');
    airportElements.forEach(element => {
        const icao = element.getAttribute('data-airport');
        if (icao && airpuffWS) {
            airpuffWS.subscribeToAirport(icao);
        }
    });
}

// Export for use in other scripts
window.AirPuffWebSocket = AirPuffWebSocket;
window.airpuffWS = airpuffWS;
