# AirPuff Test Suite

This directory contains the complete test suite for AirPuff, supporting the CI/CD pipeline with comprehensive testing across all components.

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for database and services
├── api/           # API endpoint tests
├── performance/   # Performance and load tests
└── conftest.py    # Pytest configuration and fixtures
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Models**: Database model testing
- **Services**: Business logic testing
- **Utils**: Utility function testing
- **Auth**: Authentication and authorization testing

### Integration Tests (`tests/integration/`)
- **Database**: Database integration testing
- **Redis**: Cache integration testing
- **External APIs**: Fli-Rite and CheckWX API testing
- **WebSockets**: Real-time communication testing

### API Tests (`tests/api/`)
- **Endpoints**: All API endpoint testing
- **Authentication**: OAuth and JWT testing
- **Data Validation**: Request/response validation
- **Error Handling**: Error scenario testing

### Performance Tests (`tests/performance/`)
- **Load Testing**: High-load scenario testing
- **Stress Testing**: System limits testing
- **Response Time**: Performance benchmarking
- **Resource Usage**: Memory and CPU monitoring

## Running Tests

### Local Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/api/ -v
pytest tests/performance/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v
```

### CI/CD Testing
Tests are automatically run in GitHub Actions:
- **Code Quality**: Linting, formatting, type checking
- **Backend Tests**: Unit and integration tests
- **API Tests**: Endpoint and integration tests
- **Performance Tests**: Load and stress testing

## Test Configuration

### Environment Variables
```bash
# Test database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/airpuff_test

# Test Redis
REDIS_URL=redis://localhost:6379

# Test configuration
SECRET_KEY=test-secret-key
ENVIRONMENT=testing
DEBUG=true
```

### Test Data
- **Airports**: Sample airport data for testing
- **Weather**: Mock weather data for testing
- **Users**: Test user accounts for authentication
- **Routes**: Sample flight routes for testing

## Test Fixtures

### Database Fixtures
- **Test Database**: Isolated test database
- **Sample Data**: Pre-populated test data
- **Cleanup**: Automatic cleanup after tests

### API Fixtures
- **Test Client**: HTTP client for API testing
- **Authentication**: Test user authentication
- **Headers**: Common request headers

### Service Fixtures
- **Mock Services**: Mocked external services
- **Test Configuration**: Test-specific configuration
- **Cleanup**: Service cleanup after tests

## Test Coverage

### Coverage Goals
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **API Tests**: 95%+ coverage
- **Performance Tests**: 70%+ coverage

### Coverage Reports
- **HTML Reports**: Detailed coverage reports
- **XML Reports**: CI/CD integration
- **Console Output**: Real-time coverage feedback

## Test Data Management

### Test Database
- **Isolation**: Each test gets isolated database
- **Cleanup**: Automatic cleanup after tests
- **Migrations**: Automatic schema migrations
- **Seeding**: Test data seeding

### Mock Data
- **Weather Data**: Mock weather observations
- **Airport Data**: Sample airport information
- **User Data**: Test user accounts
- **Route Data**: Sample flight routes

## Performance Testing

### Load Testing
- **Concurrent Users**: Multiple simultaneous users
- **Request Volume**: High request volume testing
- **Response Time**: Performance benchmarking
- **Resource Usage**: Memory and CPU monitoring

### Stress Testing
- **System Limits**: Testing system boundaries
- **Error Handling**: Error scenario testing
- **Recovery**: System recovery testing
- **Stability**: Long-running stability tests

## Test Automation

### GitHub Actions Integration
- **Automatic Testing**: Tests run on every push
- **Parallel Execution**: Tests run in parallel
- **Environment Isolation**: Isolated test environments
- **Result Reporting**: Test result reporting

### Continuous Testing
- **Real-time Feedback**: Immediate test feedback
- **Quality Gates**: Quality checkpoints
- **Deployment Gates**: Deployment quality checks
- **Monitoring**: Test result monitoring

## Best Practices

### Test Writing
- **Clear Names**: Descriptive test names
- **Single Responsibility**: One test per scenario
- **Independence**: Tests should be independent
- **Cleanup**: Proper test cleanup

### Test Data
- **Realistic Data**: Use realistic test data
- **Edge Cases**: Test edge cases and boundaries
- **Error Scenarios**: Test error conditions
- **Performance**: Test performance scenarios

### Test Maintenance
- **Regular Updates**: Keep tests updated
- **Refactoring**: Refactor tests with code
- **Documentation**: Document test scenarios
- **Review**: Regular test review

## Troubleshooting

### Common Issues
- **Database Connection**: Check database connectivity
- **Test Data**: Verify test data setup
- **Environment Variables**: Check environment configuration
- **Dependencies**: Verify test dependencies

### Debug Commands
```bash
# Run tests with debug output
pytest tests/ -v -s

# Run specific test with debug
pytest tests/unit/test_models.py::test_airport_creation -v -s

# Check test coverage
pytest tests/ --cov=app --cov-report=term-missing
```

## Support

For test-related issues:
1. Check test logs and output
2. Verify test data and configuration
3. Review test documentation
4. Contact the development team

The test suite provides comprehensive coverage of all AirPuff components, ensuring high quality and reliability across all environments.
