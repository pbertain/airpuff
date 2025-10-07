# AirPuff - Modern Aviation Weather System

A complete rewrite of the legacy AirPuff system, built with modern Python technologies and designed for scalability and maintainability.

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: TimescaleDB (PostgreSQL extension) for time-series data
- **Frontend**: Jinja2 templates with HTMX for dynamic updates
- **Charts**: Grafana for historical data visualization
- **Real-time**: WebSocket connections for live updates
- **Authentication**: OAuth 2.0 (Google/Apple) with future Keycloak support
- **Deployment**: Docker containers with Ansible automation

## Features

### Current Implementation (Phase 1-2)
- ✅ TimescaleDB schema with hypertables
- ✅ FastAPI application with database models
- ✅ REST API endpoints for airports and weather
- ✅ WebSocket support for real-time updates
- ✅ systemd timer service for data fetching
- ✅ Docker containerization
- ✅ Basic frontend templates

### Planned Features
- 🔄 Fli-Rite API integration
- 🔄 OAuth authentication
- 🔄 Route planning with interactive maps
- 🔄 Grafana dashboards
- 🔄 iMessage/SMS notifications
- 🔄 Automated deployment

## Quick Start

### Development with Docker

1. Clone the repository:
```bash
git clone https://github.com/pbertain/airpuff.git
cd airpuff
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the application:
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3000 (admin/admin)

### Manual Setup

1. Install TimescaleDB:
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo apt install timescaledb-2-postgresql-15

# macOS
brew install timescaledb
```

2. Create database:
```bash
sudo -u postgres createdb airpuff
sudo -u postgres psql airpuff -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
```

3. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Airports
- `GET /api/v1/airports` - List airports
- `GET /api/v1/airports/{icao}` - Get airport details
- `POST /api/v1/airports` - Create airport
- `PUT /api/v1/airports/{icao}` - Update airport
- `DELETE /api/v1/airports/{icao}` - Delete airport

### Weather
- `GET /api/v1/weather/{icao}` - Current weather
- `GET /api/v1/weather/{icao}/history` - Weather history
- `GET /api/v1/weather?icaos=KSFO,KLAX` - Multiple airports

### Routes
- `GET /api/v1/routes` - List routes
- `GET /api/v1/routes/{id}` - Get route details
- `POST /api/v1/routes` - Create route
- `PUT /api/v1/routes/{id}` - Update route
- `DELETE /api/v1/routes/{id}` - Delete route

### Authentication
- `POST /api/v1/auth/google` - Google OAuth
- `POST /api/v1/auth/apple` - Apple OAuth
- `GET /api/v1/auth/me` - Current user

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://airpuff:airpuff@localhost:5432/airpuff

# API Keys
FLI_RITE_API_KEY=your_key_here
CHECKWX_API_KEY=your_key_here

# OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

## Development

### Project Structure
```
airpuff/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── templates/      # Jinja2 templates
│   │   └── static/         # CSS, JS, images
│   ├── systemd/            # systemd service files
│   └── alembic/            # Database migrations
├── grafana/                # Grafana configuration
├── deployment/             # Ansible playbooks
└── docker-compose.yml      # Docker services
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Bare Metal with Ansible
```bash
# Deploy to dev
ansible-playbook deployment/ansible/playbook.yml -i deployment/ansible/inventory/dev.yml

# Deploy to prod
ansible-playbook deployment/ansible/playbook.yml -i deployment/ansible/inventory/prod.yml
```

### GitHub Actions
- Push to `dev` branch → automatic dev deployment
- Push to `main` branch → automatic prod deployment

## Migration from Legacy

The legacy system in `src/` is preserved for reference. The new system will:

1. Import existing airport data
2. Migrate historical weather data
3. Provide API compatibility where possible
4. Gradually replace legacy functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

See LICENSE file for details.

## Support

- Issues: GitHub Issues
- Documentation: [Wiki](https://github.com/pbertain/airpuff/wiki)
- API Docs: `/docs` endpoint when running
