Now I have the PRD. Let me fill in the HLD template based on this PRD content.

# High-Level Design: aiworkshop

**Created:** 2026-02-02T12:05:49Z
**Status:** Draft

## 1. Architecture Overview

The F1 Analytics Workshop follows a **layered monolithic architecture** with clear separation of concerns. For the health check enhancement, we adopt a **lightweight monitoring pattern** that integrates seamlessly with existing FastAPI infrastructure:

- **Presentation Layer**: FastAPI REST API with dedicated health endpoint at `/health`
- **Service Layer**: Health check orchestration logic that validates service readiness
- **Integration Layer**: External dependency validation (Ergast F1 API connectivity checks)

The health check implementation follows a **stateless, non-blocking design** optimized for high-frequency polling by load balancers and orchestration platforms. The endpoint operates independently of application state, ensuring availability even during partial service degradation.

**Architecture Pattern**: Single unified health endpoint initially, with future extensibility for separate liveness/readiness probes following Kubernetes conventions.

---

## 2. System Components

### Core API Server (`src/api/main.py`)
- FastAPI application serving all HTTP endpoints
- CORS middleware for cross-origin support
- OpenAPI/Swagger documentation generation
- Entry point for the new `/health` endpoint

### Health Check Handler (`src/api/main.py` - new route)
- Lightweight HTTP GET endpoint at `/health`
- Returns JSON response with health status
- Performs basic service readiness validation
- Response time target: <500ms (99th percentile)

### Health Validation Service (`src/services/health_service.py` - NEW)
- Centralizes health check logic
- Validates critical dependencies (Ergast F1 API connectivity)
- Aggregates health status into unified response
- Implements timeout protection (1 second max)

### Ergast F1 API Validator
- Performs lightweight connectivity check to external F1 data API
- Uses minimal request (e.g., HEAD request or `/seasons.json?limit=1`)
- Implements 5-second timeout to prevent slow responses blocking health checks
- Returns degraded status on timeout rather than complete failure

### Response Builder
- Constructs standardized JSON health response
- Includes status, timestamp, and optional metadata
- Ensures consistent response format across all scenarios
- Sanitizes error messages to avoid exposing sensitive information

---

## 3. Data Model

### HealthCheckResponse
```python
{
  "status": str,              # "healthy" | "unhealthy"
  "timestamp": str,            # ISO-8601 format (e.g., "2026-02-02T12:05:49Z")
  "service": str,              # Service identifier (e.g., "F1 Analytics Workshop API")
  "version": str               # API version (e.g., "1.0.0")
}
```

**Healthy Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T12:05:49Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0"
}
```

**Unhealthy Response Example**:
```json
{
  "status": "unhealthy",
  "timestamp": "2026-02-02T12:05:49Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0"
}
```

### HealthCheckStatus (Internal Enum)
```python
class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
```

### DependencyCheckResult (Internal Model)
```python
{
  "name": str,                 # Dependency identifier
  "available": bool,           # Is dependency reachable
  "response_time_ms": float,   # Check duration
  "error": Optional[str]       # Error message if check failed
}
```

---

## 4. API Contracts

### GET /health

**Purpose**: Health check endpoint for monitoring systems, load balancers, and orchestration platforms.

**Request**:
- Method: `GET`
- Path: `/health`
- Headers: None required
- Body: None
- Query Parameters: None

**Response - Healthy (200 OK)**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "timestamp": "2026-02-02T12:05:49Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0"
}
```

**Response - Unhealthy (503 Service Unavailable)**:
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "status": "unhealthy",
  "timestamp": "2026-02-02T12:05:49Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0"
}
```

**Response Codes**:
- `200 OK`: Service is healthy and ready to handle requests
- `503 Service Unavailable`: Service is unhealthy or critical dependencies are unavailable
- `500 Internal Server Error`: Health check endpoint itself encountered an error

**Performance SLA**:
- Response time: <500ms (99th percentile), <1 second maximum
- Throughput: Supports 100+ requests/second
- Resource usage: <1% CPU/memory overhead

**Security**:
- No authentication required (publicly accessible for monitoring)
- Rate limiting: 100 requests/minute per IP address
- No sensitive information exposed in responses

---

## 5. Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ (async-capable Python web framework)
- **ASGI Server**: Uvicorn (production-grade async server)
- **HTTP Client**: httpx 0.25+ (async HTTP client for dependency checks)
- **Async Runtime**: asyncio (native Python async/await for non-blocking I/O)
- **Validation**: Pydantic v2 (data validation and settings management)
- **Python Version**: 3.8+ (with type hints and async support)

### Frontend
- **API Documentation**: OpenAPI/Swagger UI (auto-generated by FastAPI at `/docs`)
- **Redoc**: Alternative documentation interface at `/redoc`
- **No dedicated frontend UI**: Health endpoint is machine-readable JSON for monitoring systems

### Infrastructure
- **Containerization**: Docker (multi-stage builds for optimized images)
- **Orchestration**: Kubernetes (health probe integration via livenessProbe/readinessProbe)
- **Configuration**: Environment variables with Pydantic Settings
- **Secrets Management**: Kubernetes Secrets, AWS Secrets Manager, or environment variables
- **Reverse Proxy**: Nginx, AWS ALB, or GCP Load Balancer
- **Container Registry**: Docker Hub, AWS ECR, or GCP Artifact Registry

### Data Storage
- **External API**: Ergast F1 API (https://api.jolpi.ca/ergast/f1) - primary data source
- **No database required**: Health check is stateless and requires no persistent storage
- **Future caching**: Redis or in-memory cache for health check result caching (optional optimization)

---

## 6. Integration Points

### External Systems

**Ergast F1 API** (Dependency Validation)
- **URL**: https://api.jolpi.ca/ergast/f1
- **Protocol**: HTTPS REST API
- **Health Check Method**: Lightweight GET request to `/seasons.json?limit=1` or HEAD request to base URL
- **Timeout**: 5 seconds (prevents slow external API from blocking health checks)
- **Purpose**: Validates that the primary data source is accessible
- **Failure Handling**: Returns unhealthy status if unreachable or timeout exceeded

**Load Balancers / API Gateways**
- **Integration Type**: HTTP health probe
- **Check Endpoint**: `GET /health`
- **Expected Response**: HTTP 200 for healthy, 503 for unhealthy
- **Check Interval**: Configurable (typical: 10-30 seconds)
- **Failure Threshold**: 2-3 consecutive failures before removing from rotation
- **Examples**: AWS Application Load Balancer, GCP Load Balancer, Nginx upstream health checks

**Container Orchestrators (Kubernetes)**
- **Liveness Probe**: `httpGet` on `/health` (detects if pod is alive and should be restarted)
- **Readiness Probe**: `httpGet` on `/health` (detects if pod is ready to receive traffic)
- **Probe Configuration**:
  - `initialDelaySeconds: 15` (allow service startup time)
  - `periodSeconds: 10` (check every 10 seconds)
  - `timeoutSeconds: 5` (fail if health check takes >5 seconds)
  - `failureThreshold: 3` (restart/mark unready after 3 failures)
  - `successThreshold: 1` (mark ready after 1 success)

**Monitoring Systems**
- **Prometheus**: Can scrape `/health` and convert to metrics (up/down status)
- **Datadog / New Relic**: HTTP check monitors for uptime tracking
- **CloudWatch**: Health check via Route 53 health checks or custom Lambda monitors
- **PagerDuty / Opsgenie**: Alerting integration when health checks fail consistently

### Internal Integrations

**FastAPI Application**
- Health endpoint registered as standard FastAPI route
- Shares same server instance and port (8000)
- Uses FastAPI dependency injection for health service

**Logging System**
- Health check failures logged at WARNING or ERROR level
- Successful checks not logged (avoid log spam)
- Includes error details for debugging without exposing sensitive data

---

## 7. Security Architecture

### Authentication & Authorization
- **Public Access**: `/health` endpoint is publicly accessible without authentication
- **Rationale**: Monitoring systems, load balancers, and orchestrators need unauthenticated access
- **No credentials required**: Ensures simplicity and compatibility with all monitoring tools

### Rate Limiting
- **Limit**: 100 requests per minute per IP address
- **Implementation**: FastAPI middleware or reverse proxy (Nginx `limit_req`)
- **Purpose**: Prevent DoS attacks or accidental request storms
- **Behavior**: Return HTTP 429 (Too Many Requests) when limit exceeded

### Information Disclosure Protection
- **No sensitive data**: Response excludes credentials, API keys, internal IPs, stack traces
- **Error sanitization**: Generic "unhealthy" status without detailed error messages in production
- **No system details**: Avoid exposing OS version, Python version, internal architecture
- **Version information**: Service version included (e.g., "1.0.0") but not library versions

### Network Security
- **CORS**: Health endpoint exempt from CORS restrictions (monitoring systems need cross-origin access)
- **HTTPS**: Enforce TLS 1.2+ in production via reverse proxy
- **Internal network access**: No firewall restrictions; must be accessible from load balancers and monitoring systems
- **DDoS mitigation**: Rate limiting + reverse proxy DDoS protection (Cloudflare, AWS Shield)

### Input Validation
- **No parameters**: Endpoint accepts no query parameters, headers, or body (minimal attack surface)
- **HTTP method restriction**: Only GET method allowed (405 Method Not Allowed for POST/PUT/DELETE)

### Logging & Auditing
- **Health check failures logged**: Includes timestamp, error type, dependency status
- **No PII logging**: No user-identifiable information in health check logs
- **Audit trail**: Failed health checks trigger alerts for investigation

---

## 8. Deployment Architecture

### Containerization

**Dockerfile Strategy** (Multi-stage build):
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ /app/src/
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Image Characteristics**:
- Base image: `python:3.11-slim` (minimal Debian-based image)
- Size: ~150-200MB (optimized multi-stage build)
- Health check: Built-in Docker `HEALTHCHECK` using the `/health` endpoint

### Kubernetes Deployment

**Deployment Manifest** (`k8s/deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: f1-analytics-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: f1-analytics-api
  template:
    metadata:
      labels:
        app: f1-analytics-api
    spec:
      containers:
      - name: api
        image: f1-analytics-api:1.0.0
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        env:
        - name: API_VERSION
          value: "1.0.0"
        - name: LOG_LEVEL
          value: "INFO"
```

**Service Configuration** (`k8s/service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: f1-analytics-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: f1-analytics-api
```

### Environment Configuration

**Environment Variables**:
- `API_VERSION`: Service version string (e.g., "1.0.0")
- `SERVICE_NAME`: Display name for health check response (default: "F1 Analytics Workshop API")
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `HEALTH_CHECK_TIMEOUT`: Maximum time for health check execution (default: 1 second)
- `ERGAST_API_URL`: Base URL for Ergast F1 API (default: https://api.jolpi.ca/ergast/f1)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS

**Configuration Management**:
- **Development**: `.env` file or environment variables
- **Staging/Production**: Kubernetes ConfigMap for non-sensitive values, Secrets for sensitive data

### Deployment Environments

**Development**:
- Local Docker Compose or direct Python execution
- Health check enabled for testing load balancer integration
- Verbose logging (DEBUG level)

**Staging**:
- Kubernetes cluster (separate namespace)
- Mirrors production configuration
- Automated health check testing in CI/CD pipeline

**Production**:
- Kubernetes cluster with multiple replicas (3+)
- Load balancer health checks enabled
- Automated rollout with health-based readiness gates
- Blue-green or rolling deployment strategy

---

## 9. Scalability Strategy

### Horizontal Scaling
- **Stateless Design**: Health check logic contains no session state or shared memory
- **Replica Independence**: Each pod performs health checks independently without coordination
- **Kubernetes HPA**: Horizontal Pod Autoscaler based on CPU/memory usage (not health check specific)
- **Load Balancing**: Round-robin distribution with health-based routing (unhealthy pods excluded)

### Health Check Performance Optimization
- **Lightweight Checks**: Minimal external API calls (single HEAD request or cached result)
- **Timeout Protection**: 5-second timeout for external dependency checks prevents cascading delays
- **Async I/O**: Non-blocking HTTP client (httpx) for concurrent dependency validation
- **No Database Queries**: Avoids expensive I/O operations that could slow response time

### Caching Strategy (Future Optimization)
- **Health Check Result Caching**: Cache external dependency status for 30-60 seconds
- **Rationale**: Load balancers may poll every 5-10 seconds; caching reduces external API calls by 80-90%
- **Implementation**: In-memory cache with TTL (e.g., `TTLCache` or Redis)
- **Trade-off**: 30-second staleness acceptable for health monitoring vs. reduced API load

### Rate Limiting for Monitoring Systems
- **Challenge**: Multiple monitoring systems may poll health endpoint simultaneously
- **Solution**: Rate limiting (100 req/min per IP) prevents excessive load
- **Graceful Degradation**: Health check responds quickly even under rate limiting (HTTP 429)

### Resource Isolation
- **CPU/Memory Limits**: Kubernetes resource limits prevent health check from consuming excessive resources
- **Health Check Thread Pool**: Separate async task pool for health checks (future enhancement)

---

## 10. Monitoring & Observability

### Logging Strategy

**Log Levels**:
- **INFO**: Health check failures (when service transitions to unhealthy)
- **WARNING**: Slow external dependency responses (>3 seconds)
- **ERROR**: Health check endpoint errors (500 responses)
- **DEBUG**: Not used for health checks (too noisy)

**Structured Logging**:
```json
{
  "timestamp": "2026-02-02T12:05:49Z",
  "level": "WARNING",
  "service": "f1-analytics-api",
  "component": "health_check",
  "message": "Ergast API slow response",
  "duration_ms": 3200,
  "dependency": "ergast_api"
}
```

**Log Aggregation**:
- Kubernetes stdout/stderr logs collected by logging agent (Fluentd, Fluent Bit)
- Centralized storage: ELK Stack, CloudWatch Logs, or Splunk
- Retention: 30 days for INFO, 90 days for WARNING/ERROR

### Metrics Collection (Future)

**Prometheus Metrics** (optional future enhancement):
- `health_check_duration_seconds{status}`: Histogram of health check response times
- `health_check_total{status}`: Counter of health checks by status (healthy/unhealthy)
- `dependency_available{dependency}`: Gauge indicating dependency availability (1=up, 0=down)

**Metrics Endpoint** (future): `/metrics` in Prometheus text format

### Alerting Strategy

**Critical Alerts** (PagerDuty/Opsgenie):
- Health check returning 503 for >5 minutes (sustained outage)
- All replicas failing health checks (complete service unavailability)
- External dependency (Ergast API) unreachable for >10 minutes

**Warning Alerts** (Slack/Email):
- Health check response time >500ms (approaching SLA threshold)
- Single replica failing health checks (potential deployment issue)
- Rate limiting triggered frequently (monitoring system misconfiguration)

**Alert Sources**:
- **Kubernetes**: Pod restart alerts when liveness probe fails repeatedly
- **Load Balancer**: Alerts when all targets marked unhealthy
- **Monitoring System**: Direct health check polling (Datadog, Prometheus Alertmanager)

### Dashboards (Future)

**Grafana Dashboard** (example):
- Health check success rate (last 24 hours)
- Average health check response time
- External dependency availability timeline
- Kubernetes pod health status

### Health Check Monitoring Flow

1. **Load Balancer Polling**: Checks `/health` every 10 seconds
2. **Health Check Execution**: Service validates readiness and external dependencies
3. **Response**: Returns 200 (healthy) or 503 (unhealthy)
4. **Load Balancer Action**: Routes traffic only to healthy pods
5. **Logging**: Failed checks logged for investigation
6. **Alerting**: Sustained failures trigger PagerDuty incidents

---

## 11. Architectural Decisions (ADRs)

### ADR-001: Single Unified Health Endpoint Initially
**Status**: Accepted

**Context**: Kubernetes and cloud platforms support separate liveness and readiness probes, but PRD specifies single combined endpoint initially.

**Decision**: Implement single `/health` endpoint that serves as both liveness and readiness probe. Future versions can introduce `/health/live` and `/health/ready` if needed.

**Rationale**:
- Simplicity: Single endpoint easier to implement, test, and maintain
- PRD Non-Goals: Separate liveness/readiness endpoints explicitly out of scope
- Sufficient for initial use case: Load balancers and basic monitoring needs met
- Extensibility: Architecture allows easy addition of separate endpoints later

**Consequences**:
- Load balancers and Kubernetes use same endpoint for both liveness and readiness
- Cannot distinguish "service is alive but not ready" from "service is dead" initially
- Acceptable trade-off for MVP; can enhance later based on operational needs

---

### ADR-002: Minimal Dependency Health Checks
**Status**: Accepted

**Context**: Could implement comprehensive dependency checks (database, cache, external APIs), but PRD specifies initial version should be lightweight.

**Decision**: Health check validates only critical external dependency (Ergast F1 API) with lightweight connectivity check. No database or cache health checks initially.

**Rationale**:
- PRD Out of Scope: "Detailed dependency health checks" explicitly excluded from initial version
- Performance: Keeps health check response time <500ms (meeting SLA)
- Simplicity: Reduces complexity and potential failure points
- Current architecture: No database or cache in current implementation to check

**Consequences**:
- Health check only detects external API failures, not internal resource issues
- Future enhancements can add database/cache checks when those components exist
- Meets stated performance and simplicity requirements

---

### ADR-003: No Authentication for Health Endpoint
**Status**: Accepted

**Context**: Could implement API key authentication or IP whitelisting for health endpoint.

**Decision**: Health endpoint publicly accessible without authentication.

**Rationale**:
- PRD Requirement: "Implementing authentication or authorization for the health endpoint" is a non-goal
- Monitoring compatibility: Load balancers and monitoring systems need unauthenticated access
- Security: No sensitive information exposed in response (status, timestamp only)
- Industry standard: Health endpoints typically public for operational tooling

**Consequences**:
- Anyone can query health status (acceptable - no sensitive data exposed)
- Rate limiting protects against abuse
- Simplifies integration with monitoring tools

---

### ADR-004: Return 503 for Unhealthy State
**Status**: Accepted

**Context**: Could return 200 with `"status": "unhealthy"` or use different HTTP codes (503, 500).

**Decision**: Return HTTP 503 (Service Unavailable) when health check determines service is unhealthy.

**Rationale**:
- HTTP semantics: 503 indicates temporary unavailability, appropriate for health checks
- Load balancer compatibility: Most load balancers expect non-2xx status for unhealthy targets
- Kubernetes convention: Liveness/readiness probes treat non-2xx as failure
- PRD Acceptance Criteria: Explicitly requires 503 for unhealthy status

**Consequences**:
- Clear distinction between healthy (200) and unhealthy (503) for monitoring systems
- Load balancers automatically remove 503-responding pods from rotation
- Aligns with industry best practices

---

### ADR-005: Async Health Check Implementation
**Status**: Accepted

**Context**: Could implement health check as synchronous blocking code or async non-blocking code.

**Decision**: Use FastAPI's async capabilities with `async def` endpoint and `httpx.AsyncClient` for external dependency checks.

**Rationale**:
- FastAPI native support: Async endpoints are first-class in FastAPI
- Performance: Non-blocking I/O prevents external API delays from blocking other requests
- Concurrency: Allows future parallel health checks if multiple dependencies added
- Consistency: Aligns with FastAPI's async-first design philosophy

**Consequences**:
- Slightly more complex code (async/await syntax)
- Better performance under load
- Future-proof for adding multiple parallel dependency checks

---

### ADR-006: 5-Second Timeout for External Dependency Check
**Status**: Accepted

**Context**: PRD requires health check to respond within 1 second (99th percentile). External API check needs timeout to prevent hanging.

**Decision**: Set 5-second timeout for Ergast F1 API connectivity check, with 1-second overall health endpoint response target.

**Rationale**:
- PRD Performance Requirement: Health check must respond <1 second
- External API variability: Ergast API may occasionally be slow
- Fail-fast: Timeout prevents slow external API from blocking health checks indefinitely
- Balance: 5 seconds allows reasonable validation while preventing excessive delays

**Consequences**:
- Health check may timeout and return unhealthy if Ergast API is slow (>5 seconds)
- Acceptable: Slow external API means service cannot fulfill requests anyway
- Meets PRD requirement for <1 second response (most checks complete quickly; timeout prevents worst-case)

---

### ADR-007: Stateless Health Check Design
**Status**: Accepted

**Context**: Could cache health check results or maintain health state across requests.

**Decision**: Health check is fully stateless; each request performs fresh validation.

**Rationale**:
- Scalability: Stateless design allows horizontal scaling without coordination
- Accuracy: Fresh checks provide real-time health status
- Simplicity: No cache invalidation or state synchronization logic needed
- Performance: Lightweight checks (single external API HEAD request) are fast enough without caching

**Consequences**:
- Each health check independently validates dependencies (no shared state)
- Minor performance impact from repeated external API calls (mitigated by timeout and lightweight check)
- Future optimization: Can add caching layer if health check becomes performance bottleneck

---

### ADR-008: JSON Response Format with Timestamp
**Status**: Accepted

**Context**: Could return plain text ("OK"), JSON, or XML.

**Decision**: Return structured JSON response with status, timestamp, service name, and version.

**Rationale**:
- PRD Requirement: Response must include JSON body with "status" field and ISO 8601 timestamp
- Machine-readable: JSON enables programmatic parsing by monitoring systems
- Metadata: Service name and version aid debugging and multi-service monitoring
- Industry standard: JSON is universal format for REST APIs

**Consequences**:
- Slightly larger response payload than plain text (acceptable overhead)
- Easy integration with monitoring tools that parse JSON
- Extensible: Can add additional fields in future without breaking compatibility

---

## Appendix: PRD Reference

PRD reference: docs/plans/health-check/PRD.md (file not yet committed)
