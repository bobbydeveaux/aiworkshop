Based on my exploration of the codebase, I now understand that this is an F1 Analytics Workshop project with an existing health check endpoint. Let me create a comprehensive HLD that enhances the current basic health check with more sophisticated monitoring and observability capabilities.

# High-Level Design: aiworkshop

**Created:** 2026-02-02T10:56:47Z
**Status:** Draft

## 1. Architecture Overview

The F1 Analytics Workshop follows a **layered monolithic architecture** with clear separation of concerns:

- **Presentation Layer**: FastAPI-based REST API exposing F1 analytics endpoints
- **Service Layer**: Business logic and external API integration (F1APIService)
- **Data Layer**: External API integration (Ergast F1 API) with future support for caching and database persistence

The health check enhancement will adopt a **hierarchical health monitoring pattern** where the system provides:
- **Liveness probes**: Basic "is the service running?" checks
- **Readiness probes**: Comprehensive dependency health validation
- **Deep health checks**: Detailed component-level diagnostics with metrics

The architecture supports both synchronous REST endpoints and asynchronous background health monitoring for proactive alerting.

---

## 2. System Components

### Core API Server (`src/api/main.py`)
- FastAPI application handling HTTP requests
- CORS middleware for cross-origin support
- OpenAPI documentation auto-generation
- Current health check endpoint at `/health`

### Health Check Service (`src/services/health_service.py`) - **NEW**
- Centralized health monitoring orchestration
- Dependency health checkers (pluggable architecture)
- Health state aggregation and reporting
- Circuit breaker pattern for failing dependencies

### Dependency Health Checkers - **NEW**
- **ExternalAPIHealthChecker**: Monitors Ergast F1 API connectivity and latency
- **CacheHealthChecker**: Validates cache layer availability (future: Redis/memcached)
- **DatabaseHealthChecker**: Monitors database connection pool (future: PostgreSQL/MySQL)
- **SystemResourceChecker**: CPU, memory, disk usage monitoring

### F1 API Service (`src/api/main.py:F1APIService`)
- Existing service for Ergast F1 API integration
- HTTP client with retry logic and timeout handling
- Session management with custom User-Agent

### Metrics & Observability Layer - **NEW**
- Health check metrics collection
- Dependency response time tracking
- Error rate monitoring
- Integration with monitoring systems (Prometheus, CloudWatch, etc.)

---

## 3. Data Model

### HealthCheckResponse
```python
{
  "status": str,              # "healthy" | "degraded" | "unhealthy"
  "timestamp": str,            # ISO-8601 format
  "service": str,              # Service identifier
  "version": str,              # API version
  "uptime_seconds": int,       # Service uptime
  "checks": {
    "ergast_api": HealthCheckDetail,
    "cache": HealthCheckDetail,
    "database": HealthCheckDetail,
    "system_resources": HealthCheckDetail
  }
}
```

### HealthCheckDetail
```python
{
  "status": str,               # "healthy" | "degraded" | "unhealthy"
  "response_time_ms": float,   # Check execution time
  "last_check_time": str,      # ISO-8601 timestamp
  "message": str,              # Human-readable status
  "details": dict              # Component-specific metadata
}
```

### HealthCheckConfig
```python
{
  "timeout_seconds": int,      # Per-check timeout
  "check_interval_seconds": int, # Background check frequency
  "cache_ttl_seconds": int,    # Health status cache duration
  "thresholds": {
    "response_time_warning_ms": float,
    "response_time_critical_ms": float,
    "memory_usage_warning_percent": float,
    "memory_usage_critical_percent": float
  }
}
```

### MetricsData
```python
{
  "total_checks": int,
  "successful_checks": int,
  "failed_checks": int,
  "average_response_time_ms": float,
  "error_rate_percent": float,
  "check_history": List[HealthCheckSnapshot]
}
```

---

## 4. API Contracts

### GET /health (Enhanced - existing endpoint)
**Purpose**: Quick liveness probe for load balancers and orchestrators

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T10:56:47Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0"
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2026-02-02T10:56:47Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0",
  "error": "Critical dependencies unavailable"
}
```

### GET /health/ready - **NEW**
**Purpose**: Readiness probe with comprehensive dependency validation

**Query Parameters**:
- `detailed` (boolean, default: false): Include detailed check results
- `include_metrics` (boolean, default: false): Include historical metrics

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T10:56:47Z",
  "service": "F1 Analytics Workshop API",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "checks": {
    "ergast_api": {
      "status": "healthy",
      "response_time_ms": 45.3,
      "last_check_time": "2026-02-02T10:56:47Z",
      "message": "Ergast F1 API responding normally",
      "details": {
        "url": "https://api.jolpi.ca/ergast/f1",
        "rate_limit_remaining": 195
      }
    }
  }
}
```

**Response** (503 Service Unavailable): Similar structure with `status: "unhealthy"` or `"degraded"`

### GET /health/live - **NEW**
**Purpose**: Kubernetes-style liveness probe (minimal overhead)

**Response** (200 OK):
```json
{
  "alive": true,
  "timestamp": "2026-02-02T10:56:47Z"
}
```

### GET /health/metrics - **NEW**
**Purpose**: Prometheus-compatible metrics endpoint

**Response** (200 OK, text/plain):
```
# HELP health_check_total Total number of health checks performed
# TYPE health_check_total counter
health_check_total{component="ergast_api"} 1234

# HELP health_check_duration_seconds Health check duration in seconds
# TYPE health_check_duration_seconds histogram
health_check_duration_seconds_bucket{component="ergast_api",le="0.1"} 1000
```

---

## 5. Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ (async-capable, high-performance Python web framework)
- **ASGI Server**: Uvicorn (production-grade async server)
- **HTTP Client**: httpx 0.25+ (async HTTP client replacing requests for health checks)
- **Async Runtime**: asyncio (native Python async/await support)
- **Dependency Injection**: FastAPI's built-in DI system
- **Python Version**: 3.8+ (with type hints)

### Frontend
- **API Documentation**: OpenAPI/Swagger UI (auto-generated by FastAPI)
- **Redoc**: Alternative API documentation interface
- **No dedicated frontend**: This is a backend API service

### Infrastructure
- **Containerization**: Docker (multi-stage builds for optimization)
- **Orchestration**: Kubernetes (health probes integration)
- **Configuration Management**: Environment variables with pydantic Settings
- **Secrets Management**: Kubernetes Secrets / AWS Secrets Manager / HashiCorp Vault
- **Reverse Proxy**: Nginx / AWS ALB / GCP Load Balancer
- **Container Registry**: Docker Hub / AWS ECR / GCP Artifact Registry

### Data Storage
- **Primary Data Source**: Ergast F1 API (external REST API)
- **Cache Layer** (future): Redis 7+ or Memcached (for API response caching)
- **Metrics Storage**: Prometheus (time-series metrics database)
- **Database** (future): PostgreSQL 14+ (for analytics persistence, user data)
- **Log Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch Logs

---

## 6. Integration Points

### External Systems

**Ergast F1 API** (Primary Dependency)
- **URL**: https://api.jolpi.ca/ergast/f1
- **Protocol**: REST over HTTPS
- **Rate Limits**: 200 requests/hour, 4 requests/second
- **Health Check Method**: Lightweight `/seasons.json?limit=1` endpoint
- **Timeout**: 30 seconds
- **Retry Strategy**: 3 attempts with exponential backoff

**Monitoring & Observability Platforms** (Future)
- **Prometheus**: Metrics scraping via `/health/metrics` endpoint
- **Grafana**: Dashboard visualization of health metrics
- **PagerDuty / Opsgenie**: Alerting integration for health failures
- **AWS CloudWatch**: CloudWatch Logs and CloudWatch Metrics integration
- **Datadog / New Relic**: APM and infrastructure monitoring

**Load Balancers / API Gateways**
- **Health Check Endpoint**: `/health/live` for liveness probes
- **Readiness Endpoint**: `/health/ready` for traffic routing decisions
- **Expected Response**: HTTP 200 for healthy, 503 for unhealthy
- **Check Interval**: Configurable (recommended: 10-30 seconds)

**Container Orchestrators (Kubernetes)**
- **Liveness Probe**: `httpGet` on `/health/live`
- **Readiness Probe**: `httpGet` on `/health/ready`
- **Startup Probe**: `httpGet` on `/health/live` with longer timeout
- **Probe Configuration**: initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold

### Internal Integrations

**Cache Layer** (Future)
- **Technology**: Redis/Memcached
- **Health Check**: PING command or GET on sentinel key
- **Purpose**: Cache F1 API responses to reduce external API calls

**Database** (Future)
- **Technology**: PostgreSQL
- **Health Check**: Simple SELECT 1 query with connection pool validation
- **Purpose**: Store analytics results, user preferences, cached data

---

## 7. Security Architecture

### Authentication & Authorization
- **Current State**: Open API (no authentication)
- **Future**: API key-based authentication via headers (`X-API-Key`)
- **Health Endpoints**: Liveness probe (`/health/live`) remains public; detailed endpoints (`/health/ready`, `/health/metrics`) restricted to internal networks or authenticated monitoring systems

### Network Security
- **CORS Policy**: Currently allows all origins (`*`); production should whitelist specific domains
- **TLS/SSL**: HTTPS enforced in production via reverse proxy (Nginx/ALB)
- **Internal Network**: Health check endpoints accessible from monitoring systems within VPC/private network
- **Rate Limiting**: Implement rate limiting on public endpoints to prevent abuse

### Secrets Management
- **API Keys**: External API keys (future) stored in environment variables, loaded from secure vaults
- **Database Credentials**: Stored in Kubernetes Secrets / AWS Secrets Manager
- **Configuration**: Sensitive configuration never committed to version control
- **Credential Rotation**: Support for dynamic credential updates without service restart

### Data Protection
- **In-Transit Encryption**: HTTPS/TLS 1.2+ for all external communication
- **At-Rest Encryption**: Encrypted storage volumes for databases (future)
- **PII Handling**: No personally identifiable information currently stored; F1 data is public
- **Audit Logging**: Log all health check failures and access to sensitive endpoints

### Dependency Security
- **External API**: Validate SSL certificates for Ergast F1 API calls
- **Timeout Protection**: 30-second timeouts prevent hanging connections
- **Input Validation**: Validate all external API responses before processing
- **Dependency Scanning**: Regular security audits of Python dependencies (Dependabot/Snyk)

---

## 8. Deployment Architecture

### Containerization Strategy
**Docker Multi-Stage Build**:
1. **Builder Stage**: Install dependencies, compile if needed
2. **Runtime Stage**: Minimal Python slim image with only runtime dependencies
3. **Image Size**: Optimized <200MB

**Dockerfile Structure**:
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ /app/src/
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

**Deployment Manifest**:
- **Replicas**: 3 (minimum for high availability)
- **Rolling Update Strategy**: MaxSurge=1, MaxUnavailable=0 (zero-downtime)
- **Resource Requests**: CPU 100m, Memory 256Mi
- **Resource Limits**: CPU 500m, Memory 512Mi

**Health Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Service Configuration**:
- **Type**: ClusterIP (internal) or LoadBalancer (external)
- **Port**: 8000 (HTTP)
- **Session Affinity**: None (stateless service)

### Environment Configuration

**Configuration Layers**:
1. **Default Values**: Hardcoded sensible defaults in code
2. **Environment Variables**: Override via `ENV` in Kubernetes ConfigMap
3. **Secrets**: Sensitive values injected via Kubernetes Secrets

**Key Environment Variables**:
- `API_VERSION`: 1.0.0
- `LOG_LEVEL`: INFO (DEBUG for dev, ERROR for production)
- `ERGAST_API_URL`: https://api.jolpi.ca/ergast/f1
- `HEALTH_CHECK_TIMEOUT`: 30
- `HEALTH_CHECK_CACHE_TTL`: 30
- `CORS_ALLOWED_ORIGINS`: Comma-separated list

### Deployment Environments

**Development**:
- Local Docker Compose setup
- Hot-reload enabled (Uvicorn `--reload`)
- Detailed logging and error traces
- CORS allows all origins

**Staging**:
- Kubernetes cluster (separate namespace)
- Mirrors production configuration
- Integration testing environment
- Monitoring and alerting enabled

**Production**:
- Kubernetes cluster with auto-scaling
- Multiple availability zones
- Strict CORS policy
- Comprehensive monitoring and alerting
- Blue-green deployment strategy

---

## 9. Scalability Strategy

### Horizontal Scaling
- **Stateless Design**: No session state stored in application memory
- **Kubernetes HPA (Horizontal Pod Autoscaler)**:
  - Target Metric: CPU utilization > 70%
  - Min Replicas: 3
  - Max Replicas: 10
  - Scale-up: Add pods when CPU exceeds threshold for 2 minutes
  - Scale-down: Remove pods when CPU below threshold for 5 minutes

### Vertical Scaling
- **Resource Limits**: Adjust CPU/memory requests based on observed usage
- **Current Baseline**: 100m CPU, 256Mi memory (requests)
- **Monitoring**: Track actual resource usage and adjust limits proactively
- **Headroom**: 2x resource limits for burst capacity

### Caching Strategy (Future)
- **Redis Cache Layer**:
  - Cache F1 API responses (TTL: 1 hour for historical data, 5 minutes for current season)
  - Reduce external API calls by 80-90%
  - Handle Ergast API rate limits gracefully
- **Application-Level Caching**:
  - In-memory LRU cache for frequently accessed data
  - Cache health check results (TTL: 30 seconds) to reduce check overhead

### Database Scaling (Future)
- **Read Replicas**: PostgreSQL read replicas for analytics queries
- **Connection Pooling**: PgBouncer or SQLAlchemy connection pool (10-20 connections per pod)
- **Query Optimization**: Indexes on frequently queried columns, materialized views for complex analytics

### Load Balancing
- **Layer 7 Load Balancer**: AWS ALB, GCP Load Balancer, or Nginx
- **Routing Strategy**: Round-robin with health check validation
- **Session Affinity**: Not required (stateless service)
- **Failover**: Automatic removal of unhealthy pods from rotation

### Rate Limiting & Throttling
- **External API Protection**:
  - Respect Ergast API limits (200 req/hour, 4 req/sec)
  - Implement token bucket algorithm for outgoing requests
  - Queue requests during rate limit periods
- **API Gateway Rate Limiting** (Future):
  - Per-client rate limits (1000 req/hour)
  - Burst allowance for legitimate traffic spikes

### Performance Optimization
- **Async I/O**: FastAPI + asyncio for non-blocking external API calls
- **HTTP Connection Pooling**: Reuse connections to Ergast API (httpx.AsyncClient)
- **Response Compression**: Gzip compression for large JSON responses
- **Lazy Loading**: Load dependency health checks in parallel (asyncio.gather)

---

## 10. Monitoring & Observability

### Logging Strategy

**Log Levels**:
- **DEBUG**: Development only (detailed request/response data)
- **INFO**: Standard operation logs (startup, health checks, API calls)
- **WARNING**: Degraded performance (slow external API, approaching rate limits)
- **ERROR**: Failures (external API errors, timeout exceptions)
- **CRITICAL**: Service unavailable (all dependencies down, unrecoverable errors)

**Structured Logging**:
- **Format**: JSON logs for machine parsing
- **Fields**: timestamp, level, service, version, request_id, component, message, metadata
- **Correlation IDs**: Track requests across services (X-Request-ID header)

**Log Aggregation**:
- **Stdout/Stderr**: Logs to console (captured by Kubernetes)
- **Centralized Storage**: ELK Stack, CloudWatch Logs, or Datadog
- **Retention**: 30 days for INFO, 90 days for ERROR/CRITICAL

### Metrics Collection

**Health Check Metrics**:
- `health_check_total{component, status}`: Counter of health checks
- `health_check_duration_seconds{component}`: Histogram of check latency
- `health_check_last_success_timestamp{component}`: Gauge of last successful check
- `dependency_status{component}`: Gauge (1=healthy, 0=unhealthy)

**API Metrics**:
- `http_requests_total{method, endpoint, status_code}`: Request counter
- `http_request_duration_seconds{method, endpoint}`: Request latency histogram
- `ergast_api_calls_total{status}`: External API call counter
- `ergast_api_rate_limit_remaining`: Current rate limit headroom

**System Metrics**:
- CPU usage, memory usage, disk I/O
- Network throughput, connection counts
- Python GC metrics (via prometheus_client)

**Metrics Exposure**:
- **Endpoint**: `/health/metrics` (Prometheus format)
- **Scrape Interval**: 30 seconds (Prometheus scraper)
- **Retention**: 15 days in Prometheus, long-term in Thanos/Cortex

### Distributed Tracing

**Future Implementation**:
- **Technology**: OpenTelemetry + Jaeger/Zipkin
- **Trace Spans**: HTTP request → F1 API call → health check execution
- **Context Propagation**: W3C Trace Context headers
- **Sampling**: 10% in production, 100% in staging

### Alerting Strategy

**Critical Alerts** (PagerDuty/Opsgenie):
- All health check dependencies unhealthy for >5 minutes
- Service unavailable (returning 503) for >3 minutes
- Error rate >10% sustained for 5 minutes
- External API timeout rate >50%

**Warning Alerts** (Slack/Email):
- Health check degraded state (slow responses)
- External API rate limit approaching (>80% consumed)
- Memory usage >80% sustained for 10 minutes
- Response time p95 >1 second

**Alert Routing**:
- Critical: 24/7 on-call engineer
- Warning: Team channel notification
- Informational: Dashboard visibility only

### Dashboards

**Grafana Dashboards**:
1. **Service Health Overview**:
   - Real-time health status for all dependencies
   - Health check success rate (24h)
   - Average response times per component
   - Error rate trends

2. **API Performance**:
   - Request rate (requests/minute)
   - Latency percentiles (p50, p95, p99)
   - Error rate by endpoint
   - External API call statistics

3. **Infrastructure**:
   - Pod count and CPU/memory usage
   - Kubernetes health probe success rate
   - Network I/O and connection counts
   - Container restart count

### Health Check Monitoring Flow

1. **Continuous Background Checks**: Health service runs checks every 30 seconds
2. **Metrics Emission**: Results published to Prometheus
3. **Dashboard Update**: Grafana displays real-time health status
4. **Alert Evaluation**: Prometheus Alertmanager evaluates rules
5. **Notification**: Critical alerts trigger PagerDuty incidents
6. **Incident Response**: On-call engineer investigates via dashboards and logs

---

## 11. Architectural Decisions (ADRs)

### ADR-001: Use FastAPI for REST API Framework
**Status**: Accepted (Already Implemented)

**Context**: Need a modern Python web framework for F1 analytics API with automatic documentation and high performance.

**Decision**: Use FastAPI with Uvicorn ASGI server.

**Rationale**:
- Native async/await support for non-blocking I/O
- Automatic OpenAPI documentation generation
- Built-in request validation with Pydantic
- High performance (comparable to Node.js and Go)
- Type hints for better code quality

**Consequences**:
- Requires Python 3.8+ for async features
- Team needs familiarity with async programming patterns
- Excellent developer experience and productivity

---

### ADR-002: Implement Hierarchical Health Check Pattern
**Status**: Proposed

**Context**: Current health check is basic (single endpoint). Need comprehensive dependency monitoring for production reliability.

**Decision**: Implement three-tier health check system:
1. Liveness probe (`/health/live`): Minimal overhead, just process alive check
2. Basic health (`/health`): Quick check with external API validation
3. Readiness probe (`/health/ready`): Comprehensive dependency validation

**Rationale**:
- Kubernetes best practices distinguish liveness vs readiness
- Liveness prevents unnecessary pod restarts (quick check)
- Readiness ensures traffic only routes to fully-ready pods
- Detailed endpoint provides diagnostics without affecting load balancer behavior

**Consequences**:
- Three endpoints to maintain instead of one
- Clear separation of concerns improves reliability
- Supports gradual rollout with readiness-based traffic shifting

---

### ADR-003: Use Circuit Breaker Pattern for External Dependencies
**Status**: Proposed

**Context**: Ergast F1 API has rate limits and may become temporarily unavailable. Repeated failing health checks waste resources.

**Decision**: Implement circuit breaker pattern for external API health checks:
- **Closed**: Normal operation, all checks execute
- **Open**: Repeated failures trigger fast-fail (skip actual check)
- **Half-Open**: Periodic retry to test if service recovered

**Rationale**:
- Prevents cascading failures and resource exhaustion
- Reduces load on failing external services
- Faster health check response when dependency is known to be down
- Aligns with resilience engineering best practices

**Consequences**:
- Adds complexity to health check logic
- Need to tune thresholds (failure count, timeout, recovery interval)
- Improved overall system resilience

---

### ADR-004: Cache Health Check Results
**Status**: Proposed

**Context**: Health checks are expensive (external API calls, network I/O). Frequent checks by multiple load balancers multiply the cost.

**Decision**: Cache health check results with 30-second TTL. Background task refreshes cache proactively.

**Rationale**:
- Load balancers may check every 5-10 seconds
- Uncached: 100 req/minute to external API (hits rate limits)
- Cached (30s TTL): 2 req/minute to external API (sustainable)
- 30-second staleness acceptable for health monitoring
- Background refresh ensures cache never fully expires

**Consequences**:
- Health status may be stale for up to 30 seconds
- Requires thread-safe cache implementation (asyncio.Lock)
- Significantly reduces external API load

---

### ADR-005: Expose Prometheus Metrics Endpoint
**Status**: Proposed

**Context**: Need production observability into health check performance and dependency status.

**Decision**: Expose `/health/metrics` endpoint in Prometheus text format. Use `prometheus_client` Python library.

**Rationale**:
- Industry-standard metrics format
- Native Prometheus integration (no agent required)
- Rich metric types (counter, gauge, histogram, summary)
- Time-series data enables trend analysis and alerting

**Consequences**:
- Additional dependency (`prometheus_client`)
- Metrics endpoint should be secured (internal network only)
- Requires Prometheus server deployment

---

### ADR-006: Use Async HTTP Client (httpx) for Health Checks
**Status**: Proposed

**Context**: Current implementation uses `requests` library (synchronous). Health checks for multiple dependencies should run in parallel.

**Decision**: Migrate from `requests` to `httpx` with async support. Use `asyncio.gather()` for parallel checks.

**Rationale**:
- Async I/O reduces check latency (parallel vs sequential)
- Sequential: 3 dependencies × 100ms = 300ms total
- Parallel: max(100ms, 100ms, 100ms) = 100ms total
- `httpx` API similar to `requests` (easy migration)
- FastAPI is already async-native

**Consequences**:
- Need to refactor existing synchronous `requests` code
- All health check functions must be async (`async def`)
- Improved performance justifies migration effort

---

### ADR-007: Degraded State for Partial Failures
**Status**: Proposed

**Context**: Binary healthy/unhealthy doesn't capture partial failures. Service may be usable even if one non-critical dependency is down.

**Decision**: Introduce "degraded" health status:
- **Healthy**: All dependencies operational
- **Degraded**: Some non-critical dependencies failing (e.g., cache down but API functional)
- **Unhealthy**: Critical dependencies failing (e.g., external API unreachable)

**Rationale**:
- More nuanced status reporting
- Load balancers can still route to degraded instances if needed
- Alerts can distinguish critical vs warning scenarios
- Better reflects real-world failure modes

**Consequences**:
- Need to classify dependencies as critical vs non-critical
- Load balancer configuration must handle 3 states (not just 2)
- More complex alerting logic

---

### ADR-008: Environment-Based Configuration with Defaults
**Status**: Proposed

**Context**: Health check behavior needs to vary by environment (dev, staging, production). Avoid hardcoded values.

**Decision**: Use Pydantic Settings for configuration management:
- Default values in code (sensible for most environments)
- Override via environment variables
- Validation and type checking via Pydantic

**Rationale**:
- Environment variables are 12-factor app best practice
- Pydantic provides type safety and validation
- Easy to test with different configurations
- No secret values in code (loaded from environment)

**Consequences**:
- Configuration class to maintain
- Must document all environment variables
- Better configuration management overall

---

## Appendix: PRD Reference

PRD reference: docs/plans/health-check/PRD.md (file not yet committed)
