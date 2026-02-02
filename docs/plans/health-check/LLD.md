# Low-Level Design: aiworkshop

**Created:** 2026-02-02T11:00:48Z
**Status:** Draft

## 1. Implementation Overview

<!-- AI: Brief summary of implementation approach -->

This implementation adds a health check endpoint to the existing FastAPI application in `src/api/main.py`. The health check will provide system status information including API availability, dependency status, and basic system metrics. The implementation follows REST API best practices with proper status codes, JSON response format, and comprehensive test coverage. No database changes are required as this is a stateless endpoint that reports real-time system health.

---

## 2. File Structure

<!-- AI: List all new and modified files with descriptions -->

### Modified Files

- **`src/api/main.py`** - Add health check endpoint `/health` with GET method handler
- **`test_api.py`** - Add comprehensive unit tests for health check endpoint
- **`requirements.txt`** - Add `psutil>=5.9.0` for system metrics collection (CPU, memory)
- **`README.md`** - Update API documentation to include health check endpoint details

### New Files

- **`src/api/health.py`** - Health check service module containing health status logic and response models
- **`tests/test_health.py`** - Dedicated test suite for health check functionality

---

## 3. Detailed Component Designs

<!-- AI: For each major component from HLD, provide detailed design -->

### 3.1 Health Check Service (`src/api/health.py`)

**Purpose:** Encapsulate health check logic and provide reusable health status checks

**Classes:**

```python
class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: HealthStatus
    timestamp: datetime
    version: str
    checks: Dict[str, Any]
    
class HealthChecker:
    """Main health check service class"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    async def check_system_health(self) -> HealthCheckResponse:
        """Perform all health checks and aggregate results"""
        pass
    
    def _check_api_status(self) -> Dict[str, Any]:
        """Check API availability"""
        pass
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check CPU and memory usage"""
        pass
    
    def _calculate_uptime(self) -> float:
        """Calculate service uptime in seconds"""
        pass
    
    def _determine_overall_status(self, checks: Dict) -> HealthStatus:
        """Determine overall health status from individual checks"""
        pass
```

### 3.2 API Endpoint Handler (`src/api/main.py`)

**Purpose:** Expose health check via REST API endpoint

**Implementation Details:**
- Route: `GET /health`
- Response Code: 200 (healthy), 503 (unhealthy)
- Response Format: JSON with health status details
- No authentication required (public endpoint)
- Response time target: < 100ms

**Integration:**
```python
from src.api.health import HealthChecker, HealthCheckResponse

health_checker = HealthChecker()

@app.get("/health", response_model=HealthCheckResponse, tags=["monitoring"])
async def health_check():
    """Health check endpoint"""
    response = await health_checker.check_system_health()
    status_code = 200 if response.status == "healthy" else 503
    return JSONResponse(content=response.dict(), status_code=status_code)
```

---

## 4. Database Schema Changes

<!-- AI: SQL/migration scripts for schema changes -->

**No database schema changes required.**

This feature is stateless and does not require persistent storage. All health check data is computed in real-time and returned in the API response.

---

## 5. API Implementation Details

<!-- AI: For each API endpoint, specify handler logic, validation, error handling -->

### Endpoint: `GET /health`

**Description:** Returns the current health status of the application

**Request:**
- Method: GET
- Path: `/health`
- Query Parameters: None
- Headers: None (publicly accessible)
- Body: None

**Response (200 OK - Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T11:00:48.123Z",
  "version": "1.0.0",
  "checks": {
    "api": {
      "status": "healthy",
      "response_time_ms": 1.23
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 25.5,
      "memory_percent": 45.2,
      "uptime_seconds": 3600.5
    }
  }
}
```

**Response (503 Service Unavailable - Unhealthy):**
```json
{
  "status": "unhealthy",
  "timestamp": "2026-02-02T11:00:48.123Z",
  "version": "1.0.0",
  "checks": {
    "api": {
      "status": "unhealthy",
      "error": "Internal error occurred"
    },
    "system": {
      "status": "degraded",
      "cpu_percent": 95.5,
      "memory_percent": 92.1,
      "uptime_seconds": 3600.5
    }
  }
}
```

**Handler Logic:**
1. Initialize health checker instance at application startup
2. On request, execute all health check functions concurrently
3. Aggregate results into response model
4. Determine HTTP status code based on overall health
5. Return JSON response with appropriate status code

**Validation:**
- No input validation required (no request parameters)
- Response validation via Pydantic models

**Error Handling:**
- Wrap individual check failures in try-except blocks
- Mark failed checks as "unhealthy" with error message
- Never return 500 errors - always return structured health response
- Log errors internally but don't expose sensitive details in response

---

## 6. Function Signatures

<!-- AI: Key function/method signatures with parameters and return types -->

### `src/api/health.py`

```python
from typing import Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheckResponse(BaseModel):
    status: HealthStatus
    timestamp: datetime
    version: str
    checks: Dict[str, Any]

class HealthChecker:
    def __init__(self) -> None:
        """Initialize health checker with startup timestamp"""
        ...
    
    async def check_system_health(self) -> HealthCheckResponse:
        """
        Perform all health checks and return aggregated results
        
        Returns:
            HealthCheckResponse: Complete health check response with status and details
        """
        ...
    
    def _check_api_status(self) -> Dict[str, Any]:
        """
        Check API availability and response time
        
        Returns:
            Dict containing api check status and response time
        """
        ...
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage (CPU, memory)
        
        Returns:
            Dict containing system resource metrics and status
        """
        ...
    
    def _calculate_uptime(self) -> float:
        """
        Calculate service uptime since initialization
        
        Returns:
            float: Uptime in seconds
        """
        ...
    
    def _determine_overall_status(self, checks: Dict[str, Any]) -> HealthStatus:
        """
        Determine overall health status from individual check results
        
        Args:
            checks: Dictionary of individual health check results
            
        Returns:
            HealthStatus: Overall health status (healthy/degraded/unhealthy)
        """
        ...
```

### `src/api/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.api.health import HealthChecker, HealthCheckResponse

@app.get("/health", response_model=HealthCheckResponse, tags=["monitoring"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring system status
    
    Returns:
        JSONResponse: Health check response with appropriate HTTP status code
            - 200: System is healthy
            - 503: System is unhealthy or degraded
    """
    ...
```

---

## 7. State Management

<!-- AI: How application state is managed (Redux, Context, database) -->

**Application State:**

The health check feature maintains minimal stateful information:

1. **Startup Timestamp** - Stored in `HealthChecker` instance variable
   - Initialized once when the FastAPI application starts
   - Used to calculate uptime
   - Persists for the lifetime of the application process

2. **HealthChecker Instance** - Application-level singleton
   - Created at FastAPI application startup (in `main.py` module scope)
   - Reused across all health check requests
   - No per-request state

**State Flow:**
```
Application Start → Initialize HealthChecker (record start_time)
                ↓
Request /health → Execute health checks (stateless)
                ↓
            Return response (no state mutation)
```

**No External State:**
- No database persistence required
- No cache required (real-time checks)
- No shared state between requests
- Thread-safe by design (read-only operations)

---

## 8. Error Handling Strategy

<!-- AI: Error codes, exception handling, user-facing messages -->

### Error Handling Principles

1. **Never fail completely** - Always return a structured health response
2. **Isolate failures** - Individual check failures shouldn't crash the entire health check
3. **Provide context** - Include error details in response for debugging
4. **Log internally** - Log full exception details server-side
5. **Hide sensitive data** - Don't expose internal system details in public responses

### Error Handling Implementation

**Individual Check Failures:**
```python
def _check_system_resources(self) -> Dict[str, Any]:
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        return {
            "status": "healthy" if cpu < 80 and memory < 85 else "degraded",
            "cpu_percent": cpu,
            "memory_percent": memory
        }
    except Exception as e:
        logger.error(f"System resource check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": "Unable to retrieve system metrics"
        }
```

### HTTP Status Codes

| Status Code | Condition | Description |
|-------------|-----------|-------------|
| 200 | status == "healthy" | All checks passed, system operating normally |
| 503 | status == "degraded" or "unhealthy" | One or more checks failed or degraded |

### Error Response Format

```json
{
  "status": "unhealthy",
  "timestamp": "2026-02-02T11:00:48.123Z",
  "version": "1.0.0",
  "checks": {
    "api": {
      "status": "unhealthy",
      "error": "Service unavailable"
    },
    "system": {
      "status": "unhealthy",
      "error": "Unable to retrieve system metrics"
    }
  }
}
```

### Logging Strategy

- **ERROR level**: Individual check failures with full stack traces
- **WARNING level**: Degraded status conditions (high CPU/memory)
- **INFO level**: Health check requests (for monitoring)
- **DEBUG level**: Detailed check results for troubleshooting

---

## 9. Test Plan

### Unit Tests

**File:** `tests/test_health.py`

```python
# Test Cases:

def test_health_checker_initialization():
    """Test HealthChecker initializes with start time"""
    # Verify start_time is set on initialization

def test_calculate_uptime():
    """Test uptime calculation accuracy"""
    # Mock start_time, verify uptime calculation

def test_check_api_status_success():
    """Test API status check returns healthy"""
    # Verify API check returns healthy status

def test_check_system_resources_success():
    """Test system resource check with normal usage"""
    # Mock psutil to return normal CPU/memory values
    # Verify healthy status returned

def test_check_system_resources_degraded():
    """Test system resource check with high usage"""
    # Mock psutil to return high CPU/memory values (>80%)
    # Verify degraded status returned

def test_check_system_resources_failure():
    """Test system resource check handles psutil errors"""
    # Mock psutil to raise exception
    # Verify unhealthy status with error message

def test_determine_overall_status_healthy():
    """Test overall status is healthy when all checks pass"""
    # Provide all healthy checks
    # Verify overall status is healthy

def test_determine_overall_status_degraded():
    """Test overall status is degraded when one check is degraded"""
    # Provide one degraded check
    # Verify overall status is degraded

def test_determine_overall_status_unhealthy():
    """Test overall status is unhealthy when any check fails"""
    # Provide one unhealthy check
    # Verify overall status is unhealthy

async def test_check_system_health_integration():
    """Test complete health check execution"""
    # Execute full health check
    # Verify response structure and data types
```

**File:** `test_api.py` (additions)

```python
async def test_health_endpoint_returns_200_when_healthy(client):
    """Test /health endpoint returns 200 for healthy system"""
    # Make GET request to /health
    # Assert status code 200
    # Assert response contains required fields

async def test_health_endpoint_returns_503_when_unhealthy(client):
    """Test /health endpoint returns 503 for unhealthy system"""
    # Mock system checks to return unhealthy
    # Make GET request to /health
    # Assert status code 503
    # Assert response indicates unhealthy status

async def test_health_endpoint_response_structure(client):
    """Test /health response has correct structure"""
    # Make GET request to /health
    # Assert all required fields present
    # Assert field types are correct

async def test_health_endpoint_no_auth_required(client):
    """Test /health is publicly accessible"""
    # Make GET request without authentication
    # Assert request succeeds
```

### Integration Tests

**File:** `tests/integration/test_health_integration.py` (new)

```python
async def test_health_check_with_real_system_metrics():
    """Test health check with actual system metrics"""
    # Start FastAPI test server
    # Make real HTTP request to /health
    # Verify response contains real CPU/memory data
    # Verify response time < 100ms

async def test_health_check_concurrent_requests():
    """Test health check handles concurrent requests"""
    # Send 10 concurrent requests to /health
    # Verify all return successful responses
    # Verify no race conditions or errors

async def test_health_check_uptime_accuracy():
    """Test uptime increases over time"""
    # Make first health check request, record uptime
    # Wait 5 seconds
    # Make second health check request, record uptime
    # Verify second uptime is ~5 seconds greater
```

### E2E Tests

**File:** `tests/e2e/test_monitoring.py` (new)

```python
def test_health_endpoint_accessible_from_external_client():
    """Test /health endpoint accessible via HTTP"""
    # Start application server
    # Make HTTP request from external client (requests library)
    # Verify 200 response
    # Verify valid JSON response

def test_health_check_in_deployment_pipeline():
    """Test health check works in CI/CD pipeline"""
    # Deploy application to test environment
    # Poll /health endpoint until healthy (max 30 seconds)
    # Verify deployment successful based on health status

def test_load_balancer_health_check_integration():
    """Test health endpoint works with load balancer"""
    # Configure load balancer to use /health endpoint
    # Verify load balancer correctly routes traffic when healthy
    # Simulate unhealthy state
    # Verify load balancer removes instance from pool
```

**Test Coverage Target:** 95%+ for health check module

**Test Execution:**
```bash
# Run all tests
pytest tests/ -v

# Run only health tests
pytest tests/test_health.py -v

# Run with coverage
pytest tests/ --cov=src/api/health --cov-report=html
```

---

## 10. Migration Strategy

<!-- AI: How to migrate from current state to new implementation -->

### Migration Steps

**Phase 1: Code Implementation (Day 1)**
1. Create `src/api/health.py` with health check logic
2. Add `psutil` dependency to `requirements.txt`
3. Modify `src/api/main.py` to add `/health` endpoint
4. Create test files and implement test suite

**Phase 2: Local Testing (Day 1)**
1. Install updated dependencies: `pip install -r requirements.txt`
2. Run unit tests: `pytest tests/test_health.py -v`
3. Run integration tests: `pytest tests/integration/ -v`
4. Start local server: `uvicorn src.api.main:app --reload`
5. Manually test endpoint: `curl http://localhost:8000/health`
6. Verify response structure and status codes

**Phase 3: Staging Deployment (Day 2)**
1. Deploy code to staging environment
2. Run smoke tests against staging `/health` endpoint
3. Configure monitoring system to poll `/health` endpoint
4. Monitor for 24 hours to verify stability
5. Load test with 100 concurrent requests

**Phase 4: Production Deployment (Day 3)**
1. Deploy to production during maintenance window
2. Verify `/health` endpoint responds successfully
3. Configure production monitoring and alerting
4. Update load balancer health check configuration
5. Update API documentation with new endpoint

**Phase 5: Integration (Day 4)**
1. Configure Kubernetes liveness/readiness probes
2. Set up external uptime monitoring (Pingdom, StatusPage)
3. Add /health checks to CI/CD pipeline
4. Update runbooks and incident response procedures

### Backward Compatibility

- **No breaking changes** - This is a new endpoint, existing functionality unchanged
- **No API version bump required** - Additive change only
- **No database migrations** - No schema changes
- **No configuration changes required** - Works with existing setup

### Validation Criteria

✅ All tests pass (unit, integration, e2e)
✅ `/health` endpoint returns 200 status code
✅ Response contains all required fields
✅ Response time < 100ms (p99)
✅ No errors in application logs
✅ Monitoring system successfully polls endpoint

---

## 11. Rollback Plan

<!-- AI: How to rollback if deployment fails -->

### Rollback Triggers

Initiate rollback if any of the following occur within 1 hour of deployment:

- `/health` endpoint returns 500 errors
- Application fails to start due to new code
- Response time > 500ms consistently
- System resource usage increases significantly (>20%)
- Other API endpoints affected negatively
- Critical errors in application logs

### Rollback Procedure

**Option 1: Git Revert (Preferred)**
```bash
# Identify commit hash that introduced health check
git log --oneline

# Revert the health check changes
git revert <commit-hash>

# Push revert commit
git push origin main

# Redeploy application
./deploy.sh production
```

**Option 2: Deployment Rollback**
```bash
# Roll back to previous deployment version
kubectl rollout undo deployment/aiworkshop-api

# Verify previous version is running
kubectl rollout status deployment/aiworkshop-api
```

**Option 3: Feature Flag (If Implemented)**
```python
# In src/api/main.py, add conditional registration
if os.getenv("ENABLE_HEALTH_CHECK", "true") == "true":
    @app.get("/health")
    async def health_check():
        ...
```
```bash
# Disable health check via environment variable
export ENABLE_HEALTH_CHECK=false

# Restart application
systemctl restart aiworkshop-api
```

### Post-Rollback Actions

1. **Verify Rollback Success**
   - Confirm `/health` endpoint no longer accessible (404 expected)
   - Verify existing API endpoints functioning normally
   - Check application logs for errors

2. **Update Monitoring**
   - Disable health check monitoring alerts
   - Remove load balancer health check configuration
   - Update status page if health status published

3. **Root Cause Analysis**
   - Review application logs for errors
   - Analyze performance metrics
   - Identify what caused the rollback
   - Document findings in incident report

4. **Fix and Redeploy**
   - Address root cause in separate branch
   - Re-run full test suite
   - Deploy to staging and re-validate
   - Schedule new production deployment

### Rollback Time Target

- **Detection:** < 5 minutes (via monitoring alerts)
- **Decision:** < 5 minutes (based on defined triggers)
- **Execution:** < 10 minutes (automated deployment rollback)
- **Verification:** < 5 minutes (confirm system stable)
- **Total:** < 25 minutes from issue detection to stable state

---

## 12. Performance Considerations

<!-- AI: Performance optimizations, caching, indexing -->

### Response Time Optimization

**Target:** < 100ms (p99), < 50ms (p50)

**Optimizations:**
1. **Async Operations** - Use `async/await` for concurrent check execution
2. **Short CPU Interval** - Use `psutil.cpu_percent(interval=0.1)` for fast CPU sampling
3. **In-Memory Only** - No database queries or external API calls
4. **Minimal Dependencies** - Only import required modules
5. **Connection Pooling** - Reuse HealthChecker instance across requests

### Resource Usage

**Memory:**
- HealthChecker instance: ~1KB
- Per-request overhead: ~10KB (response object)
- psutil library: ~5MB (one-time import cost)
- **Total Impact:** Negligible (<0.1% of typical API memory)

**CPU:**
- Health check execution: ~5-10ms CPU time
- psutil.cpu_percent(): ~1-2ms
- Response serialization: ~1ms
- **Total Impact:** <0.5% CPU under normal load (10 req/sec)

### Scalability

**Request Rate Handling:**
- No state synchronization required (thread-safe reads)
- Can handle 1000+ req/sec on single core
- Linear scaling with horizontal scaling
- No bottlenecks or locks

**Concurrent Request Handling:**
```python
# Each request runs independently
async def health_check():
    # No shared mutable state
    response = await health_checker.check_system_health()
    return response
```

### Caching Strategy

**Not Recommended for Health Checks:**
- Health data must be real-time for accurate monitoring
- Caching defeats purpose of liveness/readiness checks
- Response generation is already fast (<50ms)

**If Caching Required (edge case):**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class HealthChecker:
    def __init__(self):
        self._cache_timestamp = None
        self._cached_response = None
        self._cache_ttl = 5  # seconds
    
    async def check_system_health(self):
        now = datetime.utcnow()
        if (self._cached_response and self._cache_timestamp and 
            (now - self._cache_timestamp).total_seconds() < self._cache_ttl):
            return self._cached_response
        
        # Perform actual health checks
        response = await self._perform_checks()
        self._cached_response = response
        self._cache_timestamp = now
        return response
```

### Monitoring Recommendations

**Metrics to Track:**
- `/health` endpoint response time (p50, p95, p99)
- `/health` request rate (req/sec)
- `/health` error rate
- System CPU/memory reported in health checks

**Alerting Thresholds:**
- Response time p99 > 200ms: Warning
- Response time p99 > 500ms: Critical
- Error rate > 1%: Critical
- Endpoint returning 503 status: Critical

### Database Impact

**N/A** - No database queries in health check implementation

### Network Optimization

- Response payload size: ~500 bytes (gzip: ~200 bytes)
- Enable gzip compression in FastAPI:
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500)
```

### Load Testing Results (Expected)

**Test Configuration:**
- Tool: Apache Bench (ab)
- Concurrency: 100
- Total Requests: 10,000
- Command: `ab -n 10000 -c 100 http://localhost:8000/health`

**Expected Results:**
- Requests per second: 2000-5000
- Mean response time: 20-50ms
- 99th percentile: <100ms
- No failed requests

---

## Appendix: Existing Repository Structure

## Repository File Structure

```
.claude-output.json
.claude-plan.json
.claude-resolution.json
.conflict-info.json
.git
.gitignore
.pr-number
CONTRIBUTING.md
LICENSE
README.md
docs/
  getting_started.md
notebooks/
  README.md
random_colors.py
random_words.py
requirements.txt
src/
  analysis/
    README.md
  api/
    README.md
    __init__.py
    main.py
  models/
    README.md
  random_words.py
  visualization/
    README.md
test_api.py
test_random_colors.py
test_random_words.py
```
