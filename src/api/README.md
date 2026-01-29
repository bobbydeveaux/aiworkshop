# F1 Analytics Workshop API

A FastAPI-based web server that provides health check endpoints and F1 data analysis APIs using the Ergast F1 API as the data source.

## Features

### Health Check Endpoint

The API includes a comprehensive health check endpoint at `/health` that:

- Verifies the API server is running correctly
- Checks connectivity to the external Ergast F1 API
- Returns detailed status information including timestamps
- Provides both healthy and unhealthy status reporting

**Endpoint:** `GET /health`

**Response Example (Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-29T12:00:00Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0",
  "external_api": {
    "ergast_f1_api": "healthy",
    "url": "https://api.jolpi.ca/ergast/f1"
  }
}
```

**Response Example (Unhealthy):**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-29T12:00:00Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0",
  "external_api": {
    "ergast_f1_api": "unhealthy",
    "error": "Connection timeout",
    "url": "https://api.jolpi.ca/ergast/f1"
  }
}
```

### F1 Data Endpoints

The API provides comprehensive F1 data endpoints that mirror the Ergast F1 API:

#### Seasons
- `GET /seasons` - Get list of all F1 seasons
- `GET /seasons?limit=10&offset=0` - Get seasons with pagination

#### Races and Results
- `GET /seasons/{year}/races` - Get all races for a specific season
- `GET /seasons/{year}/{round}/results` - Get race results
- `GET /seasons/{year}/{round}/qualifying` - Get qualifying results

#### Drivers and Constructors
- `GET /seasons/{year}/drivers` - Get all drivers for a season
- `GET /seasons/{year}/constructors` - Get all constructors for a season

#### Championships
- `GET /seasons/{year}/standings/drivers` - Get driver championship standings
- `GET /seasons/{year}/standings/constructors` - Get constructor championship standings
- `GET /seasons/{year}/{round}/standings/drivers` - Get standings after specific round

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
cd src/api
python main.py
```

Or using uvicorn directly:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
- Root endpoint: http://localhost:8000/

## Testing

Run the test suite:
```bash
python -m pytest test_api.py -v
```

## Configuration

The API is configured with:

- **Base URL:** Configurable Ergast F1 API base URL
- **Request Timeout:** 30 seconds for external API calls
- **CORS:** Enabled for all origins (configure for production)
- **Rate Limiting:** Respects Ergast API limits (200 requests/hour, 4 requests/second)

## Error Handling

The API includes comprehensive error handling:

- External API failures are caught and reported in health checks
- HTTP errors are properly mapped to appropriate status codes
- Request timeouts are handled gracefully
- All errors include detailed error messages

## Architecture

The API follows a clean architecture with:

- **FastAPI Framework:** Modern, fast Python web framework
- **Service Layer:** `F1APIService` class for external API interactions
- **Dependency Injection:** Proper dependency management for testing
- **Error Handling:** Comprehensive error handling throughout
- **Documentation:** Auto-generated OpenAPI documentation

## External Dependencies

- **Ergast F1 API:** Primary data source at https://api.jolpi.ca/ergast/f1
- **FastAPI:** Web framework
- **Uvicorn:** ASGI server
- **Requests:** HTTP client for external API calls

## Development

### Code Structure

```
src/api/
├── __init__.py          # Package initialization
├── main.py              # Main FastAPI application
└── README.md            # This documentation

test_api.py              # Comprehensive test suite
```

### Adding New Endpoints

To add new F1 data endpoints:

1. Add the endpoint function to `main.py`
2. Use the `F1APIService` dependency
3. Add appropriate tests to `test_api.py`
4. Update this documentation

### Testing Strategy

The test suite includes:

- **Health Check Tests:** Verify healthy and unhealthy states
- **API Endpoint Tests:** Test all F1 data endpoints
- **Service Layer Tests:** Test the F1APIService class
- **Error Handling Tests:** Verify proper error responses
- **Mocking:** External API calls are mocked for reliable testing