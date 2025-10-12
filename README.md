# AirPuff 2.0 - Modern Aviation Weather System

<div align="center">

![AirPuff Logo](backend/app/static/images/airpuff-logo.png)

**Modern, scalable aviation weather information system with real-time data, advanced analytics, and comprehensive integration capabilities.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-2.13+-orange.svg)](https://timescale.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🚀 Quick Start](#quick-start) • [📚 Documentation](#documentation) • [🔧 API Reference](#api-reference) • [🤝 Contributing](#contributing)

</div>

## 🌟 Features

### Core Functionality
- **Real-time Weather Data**: Live METAR and TAF data from multiple sources
- **Historical Analytics**: 10+ years of weather data with advanced time-series analysis
- **Interactive Dashboards**: Beautiful, responsive web interface with real-time updates
- **Route Planning**: Intelligent flight route planning with weather integration
- **User Management**: OAuth 2.0 authentication with Google and Apple
- **API-First Design**: Comprehensive REST API with cURL-friendly endpoints

### Advanced Features
- **WebSocket Integration**: Real-time weather updates and notifications
- **Grafana Dashboards**: Professional data visualization and monitoring
- **iMessage Integration**: Bi-directional weather alerts and route summaries
- **Legacy Data Migration**: Import RRD data from legacy systems
- **Docker Support**: Containerized deployment with Docker Compose
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

### Enterprise Features
- **Ansible Automation**: Infrastructure as Code for bare metal deployment
- **Security Hardening**: Production-ready security with fail2ban and monitoring
- **Backup & Recovery**: Automated backup system with S3 integration
- **Performance Monitoring**: Comprehensive monitoring and alerting
- **Scalable Architecture**: Microservices-ready with horizontal scaling

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ with TimescaleDB extension
- Redis 7.0+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/airpuff.git
   cd airpuff
   ```

2. **Set up the environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the database:**
   ```bash
   # Set environment variables
   export DATABASE_URL="postgresql://user:password@localhost:5432/airpuff"
   export REDIS_URL="redis://localhost:6379"
   export SECRET_KEY="your-secret-key"
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start the application:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health

### Docker Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f airpuff-app
```

## 📚 Documentation

### User Guides
- [Getting Started Guide](docs/user-guides/getting-started.md)
- [User Manual](docs/user-guides/user-manual.md)
- [Route Planning Guide](docs/user-guides/route-planning.md)
- [Dashboard Guide](docs/user-guides/dashboard.md)
- [iMessage Integration](docs/user-guides/imessage-integration.md)

### API Documentation
- [API Reference](docs/api/api-reference.md)
- [Authentication Guide](docs/api/authentication.md)
- [WebSocket API](docs/api/websocket-api.md)
- [cURL Endpoints](docs/api/curl-endpoints.md)
- [Rate Limiting](docs/api/rate-limiting.md)

### Deployment Guides
- [Development Setup](docs/deployment/development.md)
- [Production Deployment](docs/deployment/production.md)
- [Docker Deployment](docs/deployment/docker.md)
- [Ansible Deployment](docs/deployment/ansible.md)
- [GitHub Actions CI/CD](docs/deployment/ci-cd.md)

### Advanced Topics
- [Data Migration](docs/migration.md)
- [Grafana Integration](docs/grafana.md)
- [Performance Tuning](docs/deployment/performance-tuning.md)
- [Security Hardening](docs/deployment/security.md)
- [Monitoring & Alerting](docs/deployment/monitoring.md)

### Troubleshooting
- [Common Issues](docs/troubleshooting/common-issues.md)
- [Error Codes](docs/troubleshooting/error-codes.md)
- [Performance Issues](docs/troubleshooting/performance.md)
- [Database Issues](docs/troubleshooting/database.md)
- [Network Issues](docs/troubleshooting/network.md)

## 🔧 API Reference

### Core Endpoints

**Health & Status:**
```http
GET /health                    # Application health
GET /api/v1/health            # API health with service status
```

**Airports:**
```http
GET /api/v1/airports/          # List all airports
POST /api/v1/airports/         # Add new airport
GET /api/v1/airports/{icao}   # Get airport by ICAO code
```

**Weather Data:**
```http
GET /api/v1/weather/{icao}/latest    # Latest weather for airport
GET /api/v1/weather/{icao}/history   # Historical weather data
GET /api/v1/weather/{icao}/forecast  # Weather forecast
```

**Routes:**
```http
GET /api/v1/routes/           # List user routes
POST /api/v1/routes/          # Create new route
GET /api/v1/routes/{id}       # Get route details
PUT /api/v1/routes/{id}       # Update route
DELETE /api/v1/routes/{id}    # Delete route
```

### cURL-Friendly Endpoints

**Plain Text Output:**
```bash
# Get airport list
curl http://localhost:8000/curl/v1/airports/

# Get weather for specific airport
curl http://localhost:8000/curl/v1/weather/KSFO

# Get route information
curl http://localhost:8000/curl/v1/routes/
```

### WebSocket API

**Real-time Updates:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Weather update:', data);
};
```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App    │    │   API Client    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      FastAPI Server       │
                    │   (Port 8000)             │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│   TimescaleDB   │    │     Redis       │    │   External APIs │
│   (Port 5432)   │    │   (Port 6379)   │    │  (Fli-Rite, etc)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Python ORM with async support
- **Alembic**: Database migrations
- **TimescaleDB**: Time-series database
- **Redis**: Caching and session storage
- **WebSockets**: Real-time communication

**Frontend:**
- **Jinja2**: Server-side templating
- **HTMX**: Dynamic web interactions
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Data visualization

**Infrastructure:**
- **Docker**: Containerization
- **Ansible**: Infrastructure automation
- **GitHub Actions**: CI/CD pipeline
- **Grafana**: Monitoring and dashboards
- **systemd**: Service management

## 🔒 Security

### Authentication & Authorization
- **OAuth 2.0**: Google and Apple authentication
- **JWT Tokens**: Secure API access tokens
- **PKCE**: Enhanced OAuth security
- **Rate Limiting**: API rate limiting and throttling

### Security Features
- **HTTPS**: SSL/TLS encryption
- **CORS**: Cross-origin resource sharing
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Cross-site scripting prevention

### Production Security
- **Fail2ban**: Intrusion prevention
- **Firewall**: Network security
- **Security Headers**: HTTP security headers
- **Audit Logging**: Security event logging
- **Backup Encryption**: Encrypted backups

## 📊 Monitoring & Analytics

### Grafana Dashboards
- **Weather Overview**: Real-time weather conditions
- **Airport Analytics**: Airport-specific metrics
- **System Performance**: Application performance metrics
- **User Activity**: User engagement analytics

### Monitoring Stack
- **Health Checks**: Application health monitoring
- **Performance Metrics**: Response time and throughput
- **Error Tracking**: Error rate and debugging
- **Resource Usage**: CPU, memory, and disk monitoring

### Alerting
- **Service Down**: Application availability alerts
- **Performance Issues**: Response time alerts
- **Error Rates**: High error rate notifications
- **Resource Usage**: Resource threshold alerts

## 🚀 Deployment

### Development
```bash
# Local development
uvicorn app.main:app --reload

# With Docker
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
# Ansible deployment
./deploy.sh -t airpuff_prod -e prod -p "vault-password"

# Docker deployment
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline
- **Automated Testing**: Unit, integration, and API tests
- **Security Scanning**: Vulnerability and security checks
- **Performance Testing**: Load and stress testing
- **Automated Deployment**: Dev, staging, and production deployments

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Testing**: Maintain 90%+ test coverage
- **Documentation**: Update docs for new features
- **Security**: Follow security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Fli-Rite**: Weather data provider
- **CheckWX**: Additional weather data source
- **TimescaleDB**: Time-series database
- **FastAPI**: Web framework
- **Open Source Community**: All contributors and supporters

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/airpuff/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/airpuff/discussions)
- **Email**: support@airpuff.com

---

<div align="center">

**Built with ❤️ for the aviation community**

[⭐ Star us on GitHub](https://github.com/your-org/airpuff) • [🐛 Report Issues](https://github.com/your-org/airpuff/issues) • [💬 Join Discussions](https://github.com/your-org/airpuff/discussions)

</div># Deployment trigger - Thu Oct  9 15:46:45 PDT 2025
# Dev deployment trigger - Sun Oct 12 13:29:18 PDT 2025
