# Contributing to AirPuff

Thank you for your interest in contributing to AirPuff! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. By participating in this project, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully
- Help create a positive environment for everyone

### Unacceptable Behavior

The following behaviors are considered unacceptable:

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Public or private harassment
- Publishing private information without permission
- Any conduct that could reasonably be considered inappropriate

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11+ installed
- Git installed and configured
- A GitHub account
- Basic knowledge of Python, FastAPI, and web development

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/airpuff.git
   cd airpuff
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/your-org/airpuff.git
   ```

### Development Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**:
   ```bash
   # Install PostgreSQL and TimescaleDB
   sudo apt install postgresql postgresql-contrib
   sudo apt install timescaledb-2-postgresql-15
   
   # Create database
   sudo -u postgres createdb airpuff
   sudo -u postgres psql -d airpuff -c "CREATE EXTENSION timescaledb;"
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start Redis**:
   ```bash
   sudo systemctl start redis-server
   ```

6. **Run the application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Contributing Process

### 1. Choose an Issue

- Browse [open issues](https://github.com/your-org/airpuff/issues)
- Look for issues labeled `good first issue` for beginners
- Comment on the issue to express interest
- Wait for maintainer approval before starting work

### 2. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-documentation-update
```

### 3. Make Changes

- Write clean, readable code
- Follow the coding standards
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Run linting
flake8 backend/
black backend/

# Run type checking
mypy backend/app/

# Run security scan
bandit -r backend/app/
```

### 5. Commit Changes

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "Add feature: brief description

- Detailed description of changes
- Any additional context
- Reference to issue number"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Code Standards

### Python Code Style

**Follow PEP 8:**
- Use 4 spaces for indentation
- Maximum line length of 88 characters
- Use meaningful variable and function names
- Add docstrings for all functions and classes

**Example:**
```python
def get_weather_data(icao: str, hours: int = 24) -> Dict[str, Any]:
    """
    Retrieve weather data for a specific airport.
    
    Args:
        icao: ICAO airport code
        hours: Number of hours of data to retrieve
        
    Returns:
        Dictionary containing weather data
        
    Raises:
        AirportNotFoundError: If airport doesn't exist
        WeatherDataUnavailableError: If weather data unavailable
    """
    # Implementation here
    pass
```

### Import Organization

```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Third-party imports
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from ..database import get_db
from ..models.weather import WeatherObservation
from ..services.weather_service import WeatherService
```

### Error Handling

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    raise HTTPException(status_code=400, detail="User-friendly message")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

## Testing

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── unit/                # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/         # Integration tests
│   ├── test_api.py
│   └── test_database.py
├── api/                 # API tests
│   ├── test_endpoints.py
│   └── test_authentication.py
└── performance/         # Performance tests
    └── test_load.py
```

### Writing Tests

**Unit Test Example:**
```python
import pytest
from app.models.weather import WeatherObservation
from app.services.weather_service import WeatherService

class TestWeatherService:
    def test_get_weather_success(self, weather_service, sample_weather_data):
        """Test successful weather retrieval."""
        result = weather_service.get_weather("KSFO")
        
        assert result is not None
        assert result["icao"] == "KSFO"
        assert "temperature_c" in result
    
    def test_get_weather_airport_not_found(self, weather_service):
        """Test weather retrieval for non-existent airport."""
        with pytest.raises(AirportNotFoundError):
            weather_service.get_weather("INVALID")
    
    def test_get_weather_data_unavailable(self, weather_service, mock_no_data):
        """Test weather retrieval when data unavailable."""
        with pytest.raises(WeatherDataUnavailableError):
            weather_service.get_weather("KSFO")
```

**API Test Example:**
```python
import pytest
from fastapi.testclient import TestClient

class TestWeatherAPI:
    def test_get_weather_endpoint(self, client: TestClient):
        """Test weather endpoint returns valid data."""
        response = client.get("/api/v1/weather/KSFO/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["icao"] == "KSFO"
        assert "temperature_c" in data
    
    def test_get_weather_invalid_airport(self, client: TestClient):
        """Test weather endpoint with invalid airport."""
        response = client.get("/api/v1/weather/INVALID/latest")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
```

### Test Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_models.py -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Run tests in parallel
pytest tests/ -n auto

# Run only failed tests
pytest tests/ --lf
```

## Documentation

### Code Documentation

**Function Documentation:**
```python
def calculate_flight_category(visibility: float, ceiling: float, wind_speed: float) -> str:
    """
    Calculate flight category based on weather conditions.
    
    Args:
        visibility: Visibility in statute miles
        ceiling: Ceiling height in feet
        wind_speed: Wind speed in knots
        
    Returns:
        Flight category: VFR, MVFR, IFR, or LIFR
        
    Example:
        >>> calculate_flight_category(10.0, 12000, 5)
        'VFR'
    """
    # Implementation here
    pass
```

**Class Documentation:**
```python
class WeatherService:
    """
    Service for retrieving and processing weather data.
    
    This service handles weather data retrieval from external APIs,
    data processing, and storage in the database.
    
    Attributes:
        api_client: Client for external weather APIs
        db_session: Database session for data storage
        
    Example:
        >>> service = WeatherService(api_client, db_session)
        >>> weather = service.get_weather("KSFO")
    """
    
    def __init__(self, api_client, db_session):
        """Initialize weather service."""
        self.api_client = api_client
        self.db_session = db_session
```

### API Documentation

**Endpoint Documentation:**
```python
@router.get("/weather/{icao}/latest", response_model=WeatherResponse)
async def get_latest_weather(
    icao: str = Path(..., description="ICAO airport code", example="KSFO"),
    db: Session = Depends(get_db)
):
    """
    Get the latest weather data for an airport.
    
    This endpoint retrieves the most recent weather observation
    for the specified airport.
    
    Args:
        icao: 4-character ICAO airport code
        db: Database session
        
    Returns:
        Latest weather data for the airport
        
    Raises:
        HTTPException: 404 if airport not found
        HTTPException: 500 if weather data unavailable
        
    Example:
        GET /api/v1/weather/KSFO/latest
    """
    # Implementation here
    pass
```

### README Updates

When adding new features, update the README:

```markdown
## New Feature

### Feature Name
Brief description of the feature.

**Usage:**
```bash
# Example command
curl http://localhost:8000/api/v1/new-feature
```

**Configuration:**
```bash
# Environment variable
NEW_FEATURE_ENABLED=true
```
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   pytest tests/ -v
   ```

2. **Check code quality**:
   ```bash
   flake8 backend/
   black backend/
   mypy backend/app/
   ```

3. **Update documentation**:
   - Update README if needed
   - Add/update API documentation
   - Update user guides if applicable

4. **Test manually**:
   - Test the feature in browser
   - Test API endpoints
   - Verify error handling

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: Maintainers review code quality and functionality
3. **Testing**: Reviewers test the changes
4. **Approval**: Maintainer approves and merges

### After Merge

1. **Delete branch**: Delete feature branch after merge
2. **Update local**: Update your local main branch
3. **Celebrate**: You've contributed to AirPuff! 🎉

## Issue Reporting

### Bug Reports

**Use the bug report template:**

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.11.0]
- AirPuff Version: [e.g., 2.0.0]

## Additional Context
Any other context about the problem.
```

### Feature Requests

**Use the feature request template:**

```markdown
## Feature Description
Clear description of the feature.

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered.

## Additional Context
Any other context about the feature request.
```

### Good First Issues

Issues labeled `good first issue` are perfect for new contributors:

- Clear scope and requirements
- Well-documented
- Not too complex
- Have maintainer support

## Community Guidelines

### Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Discord**: Join our Discord server
- **Email**: Contact maintainers directly

### Communication

- **Be respectful**: Treat everyone with respect
- **Be patient**: Maintainers are volunteers
- **Be constructive**: Provide helpful feedback
- **Be inclusive**: Welcome newcomers

### Recognition

Contributors are recognized in:

- **Contributors list**: GitHub contributors page
- **Release notes**: Mentioned in release notes
- **Documentation**: Listed in contributors section
- **Community**: Appreciated by the community

## Development Workflow

### Daily Development

1. **Start day**: `git pull upstream main`
2. **Create branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Write code, tests, docs
4. **Test changes**: Run tests and manual testing
5. **Commit changes**: `git commit -m "Add feature: description"`
6. **Push changes**: `git push origin feature/new-feature`
7. **Create PR**: Open pull request on GitHub

### Weekly Maintenance

1. **Update dependencies**: Check for updates
2. **Run full test suite**: Ensure all tests pass
3. **Update documentation**: Keep docs current
4. **Review issues**: Help with community issues
5. **Plan next week**: Identify priorities

### Release Process

1. **Feature freeze**: Stop adding new features
2. **Bug fixes only**: Focus on stability
3. **Testing**: Comprehensive testing
4. **Documentation**: Update all docs
5. **Release**: Tag and release new version

## Resources

### Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Python Best Practices](https://docs.python.org/3/tutorial/)

### Tools

- **Code Editor**: VS Code with Python extension
- **Database**: pgAdmin for PostgreSQL
- **API Testing**: Postman or Insomnia
- **Version Control**: Git with GitHub Desktop

### Community

- **GitHub**: [AirPuff Repository](https://github.com/your-org/airpuff)
- **Discord**: [AirPuff Community](https://discord.gg/airpuff)
- **Twitter**: [@AirPuffApp](https://twitter.com/AirPuffApp)
- **Email**: [contributors@airpuff.com](mailto:contributors@airpuff.com)

Thank you for contributing to AirPuff! Your contributions help make aviation weather information more accessible and useful for everyone. 🚀✈️
