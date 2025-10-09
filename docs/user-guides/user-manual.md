# AirPuff User Guide

Complete user guide for AirPuff 2.0, covering all features and functionality.

## Table of Contents

- [Getting Started](#getting-started)
- [Web Interface](#web-interface)
- [Airport Management](#airport-management)
- [Weather Data](#weather-data)
- [Route Planning](#route-planning)
- [User Account](#user-account)
- [Real-time Updates](#real-time-updates)
- [iMessage Integration](#imessage-integration)
- [Data Migration](#data-migration)
- [Troubleshooting](#troubleshooting)

## Getting Started

### First Visit

1. **Open AirPuff**: Navigate to `http://localhost:8000` in your web browser
2. **Explore the Interface**: Familiarize yourself with the main navigation
3. **View Airports**: Click "Airports" to see available airports
4. **Check Weather**: Click on any airport to view current weather conditions

### Account Setup

1. **Sign In**: Click "Login" in the top navigation
2. **Choose Provider**: Select Google or Apple for authentication
3. **Authorize**: Complete the OAuth flow
4. **Welcome**: You'll be redirected to your dashboard

### Navigation Overview

- **🏠 Home**: Main dashboard with weather overview
- **✈️ Airports**: Browse and search airports
- **🗺️ Route Planner**: Create and manage flight routes
- **📊 Dashboard**: Personal dashboard with saved routes
- **📈 Grafana**: Advanced data visualization
- **💬 iMessage**: Weather alerts and messaging
- **🔄 Migration**: Legacy data migration tools
- **📚 API**: API documentation and testing

## Web Interface

### Main Dashboard

The main dashboard provides an overview of weather conditions and system status.

**Key Features:**
- **Weather Summary**: Current conditions for major airports
- **Quick Access**: Direct links to common functions
- **System Status**: Health indicators and service status
- **Recent Activity**: Latest weather updates and alerts

### Airport List

Browse and search through available airports.

**Features:**
- **Search**: Find airports by ICAO code, name, city, or state
- **Filter**: Filter by country or region
- **Sort**: Sort by name, ICAO code, or location
- **Details**: Click any airport for detailed information

**Search Examples:**
- `KSFO` - Find San Francisco International
- `San Francisco` - Find airports in San Francisco
- `CA` - Find airports in California
- `USA` - Find airports in the United States

### Airport Details

View comprehensive information for any airport.

**Information Displayed:**
- **Basic Info**: ICAO code, name, location, elevation
- **Current Weather**: Latest METAR data
- **Weather History**: Historical weather trends
- **Charts**: Visual weather data representation
- **Raw Data**: Complete METAR text

## Airport Management

### Adding Airports

Add new airports to the system for weather monitoring.

1. **Navigate**: Go to "Airports" → "Add Airport"
2. **Enter Details**:
   - ICAO Code (e.g., `KSFO`)
   - Airport Name
   - City and State
   - Country
   - Coordinates (latitude/longitude)
   - Elevation
3. **Save**: Click "Add Airport" to save

**Required Fields:**
- ICAO Code (4 characters)
- Airport Name
- City
- Country
- Coordinates

### Airport Information

**ICAO Code Format:**
- 4 characters (e.g., `KSFO`, `KSEA`, `KLAX`)
- First character: Country/region identifier
- Remaining characters: Airport identifier

**Coordinate Format:**
- Latitude: Decimal degrees (-90 to +90)
- Longitude: Decimal degrees (-180 to +180)
- Example: `37.6213, -122.3790`

## Weather Data

### Understanding Weather Information

**Flight Categories:**
- **VFR**: Visual Flight Rules (good weather)
- **MVFR**: Marginal VFR (fair weather)
- **IFR**: Instrument Flight Rules (poor weather)
- **LIFR**: Low IFR (very poor weather)

**Weather Elements:**
- **Temperature**: Air temperature in Celsius and Fahrenheit
- **Dewpoint**: Temperature at which condensation occurs
- **Wind**: Direction (degrees) and speed (knots)
- **Visibility**: Horizontal visibility in statute miles
- **Altimeter**: Barometric pressure in inches of mercury
- **Ceiling**: Height of lowest cloud layer

### Weather Charts

View historical weather data in graphical format.

**Chart Types:**
- **Temperature Trends**: Temperature over time
- **Wind Patterns**: Wind direction and speed
- **Visibility**: Visibility changes
- **Pressure**: Barometric pressure trends
- **Flight Categories**: Weather category changes

**Time Ranges:**
- Last 24 hours
- Last 7 days
- Last 30 days
- Last year
- Custom range

### Weather Alerts

Receive notifications for weather changes.

**Alert Types:**
- **Category Changes**: VFR to IFR transitions
- **Wind Changes**: Significant wind shifts
- **Visibility Changes**: Visibility drops
- **Temperature Extremes**: Very hot or cold conditions

**Alert Settings:**
- Enable/disable specific alert types
- Set thresholds for alerts
- Choose notification methods (web, email, iMessage)

## Route Planning

### Creating Routes

Plan flight routes with weather integration.

1. **Start Planning**: Click "Route Planner" in navigation
2. **Add Airports**: Search and add airports to your route
3. **Set Order**: Arrange airports in flight order
4. **Add Details**: Name and describe your route
5. **Save Route**: Save for future reference

**Route Features:**
- **Weather Integration**: Current weather for each airport
- **Flight Categories**: Visual indication of weather conditions
- **Distance Calculation**: Approximate distances between airports
- **Weather Trends**: Historical weather patterns

### Route Management

**Saved Routes:**
- **Personal Routes**: Routes saved to your account
- **Shared Routes**: Routes shared with other users
- **Public Routes**: Routes available to all users

**Route Actions:**
- **Edit**: Modify route details and airports
- **Duplicate**: Create a copy of existing route
- **Share**: Share route with other users
- **Delete**: Remove route from your account

### Route Weather

View weather conditions for all airports in a route.

**Weather Display:**
- **Summary View**: Quick weather overview
- **Detailed View**: Complete weather information
- **Chart View**: Weather trends and patterns
- **Alert View**: Weather warnings and advisories

**Weather Updates:**
- **Real-time**: Live weather updates
- **Scheduled**: Regular weather refreshes
- **On-demand**: Manual weather updates

## User Account

### Account Settings

Manage your user account and preferences.

**Profile Information:**
- **Username**: Your unique username
- **Email**: Contact email address
- **Full Name**: Display name
- **Avatar**: Profile picture

**Preferences:**
- **Units**: Metric or Imperial units
- **Timezone**: Local timezone
- **Language**: Interface language
- **Notifications**: Alert preferences

### Authentication

**Supported Providers:**
- **Google**: Sign in with Google account
- **Apple**: Sign in with Apple ID

**Account Security:**
- **OAuth 2.0**: Secure authentication protocol
- **PKCE**: Enhanced security for mobile apps
- **Session Management**: Automatic session handling
- **Logout**: Secure session termination

### Data Management

**Personal Data:**
- **Routes**: Your saved flight routes
- **Preferences**: Account settings and preferences
- **Activity**: Login history and activity logs
- **Privacy**: Data sharing and privacy settings

## Real-time Updates

### WebSocket Connection

Receive real-time weather updates through WebSocket connection.

**Connection Types:**
- **Public**: General weather updates
- **User-specific**: Updates for your saved routes
- **Airport-specific**: Updates for specific airports

**Update Types:**
- **Weather Changes**: New weather observations
- **Route Updates**: Changes to saved routes
- **System Alerts**: System notifications
- **User Messages**: Personal notifications

### Notification Settings

Configure how you receive real-time updates.

**Notification Methods:**
- **Browser Notifications**: Desktop notifications
- **Sound Alerts**: Audio notifications
- **Visual Indicators**: On-screen indicators
- **Email Notifications**: Email alerts

**Filtering Options:**
- **Airport Filters**: Specific airports only
- **Weather Filters**: Specific weather conditions
- **Time Filters**: Time-based filtering
- **Category Filters**: Flight category changes

## iMessage Integration

### Setting Up iMessage

Configure iMessage integration for weather alerts.

1. **Access Settings**: Go to "iMessage" in navigation
2. **Configure Bridge**: Set up iMessage bridge connection
3. **Test Connection**: Verify iMessage connectivity
4. **Set Preferences**: Configure alert preferences

### Weather Alerts

Receive weather information via iMessage.

**Alert Types:**
- **Route Summaries**: Weather for saved routes
- **Airport Weather**: Weather for specific airports
- **Weather Changes**: Alerts for weather changes
- **Custom Messages**: Personalized weather messages

**Message Format:**
```
KSFO-VFR-20.0°C-270@10-10.0mi-CLR|12000ft
KSEA-MVFR-18.0°C-280@15-8.0mi-BKN|3000ft
```

### Bi-directional Communication

Send requests and receive responses via iMessage.

**Request Format:**
- **Single Airport**: `KSFO`
- **Multiple Airports**: `KSFO KSEA KLAX`
- **Route Request**: `route:1` (route ID)

**Response Format:**
- **Weather Data**: Formatted weather information
- **Route Summary**: Complete route weather
- **Error Messages**: Error notifications
- **Help Text**: Usage instructions

## Data Migration

### RRD Data Import

Import legacy RRD weather data into the new system.

1. **Access Migration**: Go to "Migration" in navigation
2. **Check RRD Files**: Verify RRD data availability
3. **Start Migration**: Begin data import process
4. **Monitor Progress**: Track migration progress
5. **Validate Data**: Verify imported data integrity

### Migration Process

**Discovery Phase:**
- Scan RRD directory for airport files
- Identify available weather data
- Check data file integrity

**Import Phase:**
- Extract data from RRD files
- Transform data to new format
- Import data into TimescaleDB
- Update airport information

**Validation Phase:**
- Compare imported data with source
- Verify data completeness
- Check data accuracy
- Generate migration report

### Migration Monitoring

**Progress Tracking:**
- **Airports Processed**: Number of airports migrated
- **Records Migrated**: Number of weather observations
- **Errors Encountered**: Migration errors and issues
- **Time Elapsed**: Migration duration

**Error Handling:**
- **Automatic Recovery**: Resume from failures
- **Error Logging**: Detailed error information
- **Data Validation**: Verify data integrity
- **Manual Intervention**: Handle complex errors

## Troubleshooting

### Common Issues

**Weather Data Not Loading:**
1. Check internet connection
2. Verify airport ICAO code
3. Check weather service status
4. Refresh the page

**Login Problems:**
1. Clear browser cache and cookies
2. Check OAuth provider status
3. Verify account permissions
4. Try different browser

**Route Planning Issues:**
1. Verify airport codes
2. Check airport availability
3. Ensure proper authentication
4. Clear browser cache

### Error Messages

**Common Error Codes:**
- `AIRPORT_NOT_FOUND`: Airport doesn't exist
- `WEATHER_UNAVAILABLE`: Weather data not available
- `AUTHENTICATION_REQUIRED`: Login required
- `RATE_LIMIT_EXCEEDED`: Too many requests

**Error Resolution:**
1. Read error message carefully
2. Check error code reference
3. Follow suggested actions
4. Contact support if needed

### Performance Issues

**Slow Loading:**
1. Check internet connection speed
2. Clear browser cache
3. Disable browser extensions
4. Try different browser

**Real-time Updates Not Working:**
1. Check WebSocket connection
2. Verify firewall settings
3. Check browser WebSocket support
4. Refresh the page

### Getting Help

**Support Resources:**
- **Documentation**: Complete user guides
- **API Reference**: Technical documentation
- **FAQ**: Frequently asked questions
- **Community**: User forums and discussions

**Contact Support:**
- **Email**: support@airpuff.com
- **GitHub Issues**: Technical issues
- **Discussions**: General questions
- **Feature Requests**: New feature suggestions

## Tips and Best Practices

### Efficient Usage

**Navigation Tips:**
- Use keyboard shortcuts for common actions
- Bookmark frequently used pages
- Use search functionality for quick access
- Enable browser notifications for alerts

**Weather Monitoring:**
- Set up alerts for important airports
- Use route planning for trip preparation
- Check weather trends before flights
- Monitor weather changes during trips

**Data Management:**
- Regularly update saved routes
- Clean up unused routes
- Export important data
- Backup personal settings

### Security Best Practices

**Account Security:**
- Use strong passwords
- Enable two-factor authentication
- Log out from shared computers
- Monitor account activity

**Data Privacy:**
- Review privacy settings
- Control data sharing
- Understand data usage
- Report privacy concerns

This comprehensive user guide covers all aspects of using AirPuff 2.0. For additional help or specific questions, refer to the troubleshooting section or contact support.
