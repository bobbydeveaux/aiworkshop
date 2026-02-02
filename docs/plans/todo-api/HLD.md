Based on my understanding of the existing F1 Analytics Workshop system, I can now create a comprehensive HLD for a Todo API feature. Since the PRD for the todo-api doesn't exist yet, I'll create an HLD that adds a Todo API feature to this existing F1 analytics system, following the architecture patterns already established and based on the health-check reference.

# High-Level Design: aiworkshop

**Created:** 2026-02-02T15:36:58Z
**Status:** Draft

## 1. Architecture Overview

The Todo API will be implemented as a RESTful microservice within the existing F1 Analytics Workshop monolithic FastAPI application. The architecture follows a layered approach:

- **Presentation Layer:** FastAPI REST endpoints for todo operations
- **Business Logic Layer:** Todo service layer handling CRUD operations and validation
- **Data Access Layer:** Repository pattern with SQLAlchemy ORM for database operations
- **Data Storage Layer:** PostgreSQL database for persistent todo storage

The todo functionality will be self-contained with its own database schema, models, and endpoints, while sharing the existing FastAPI infrastructure, middleware, and deployment configuration. This approach maintains separation of concerns while leveraging the established application framework.

The system will support both synchronous REST operations and eventual integration with the existing F1 analytics features, allowing users to create todos related to F1 data analysis tasks.

---

## 2. System Components

### 2.1 Todo API Service
RESTful API service exposing endpoints for creating, reading, updating, and deleting todo items. Implements standard CRUD operations with filtering, pagination, and search capabilities.

### 2.2 Todo Business Logic Layer
Service layer containing todo validation rules, business logic for status transitions, priority management, and deadline handling. Enforces data consistency and business constraints.

### 2.3 Todo Repository Layer
Data access layer implementing the repository pattern with SQLAlchemy ORM. Handles database operations, query construction, and transaction management.

### 2.4 Todo Data Models
SQLAlchemy models defining the todo entity schema, relationships, and database constraints. Includes Pydantic schemas for request/response validation.

### 2.5 Database Migration System
Alembic-based migration system for managing todo table schema changes, indexes, and database version control.

### 2.6 Todo Authentication Middleware
Middleware component for authenticating todo requests and associating todos with users. Integrates with the existing application authentication strategy.

---

## 3. Data Model

### 3.1 Todo Entity

```
Todo
├── id: UUID (primary key)
├── title: String(200) (required, indexed)
├── description: Text (optional)
├── status: Enum ['pending', 'in_progress', 'completed', 'archived'] (default: 'pending', indexed)
├── priority: Enum ['low', 'medium', 'high', 'urgent'] (default: 'medium')
├── due_date: DateTime (optional, indexed)
├── tags: Array[String] (optional, indexed with GIN)
├── user_id: UUID (foreign key, indexed)
├── created_at: DateTime (auto-generated, indexed)
├── updated_at: DateTime (auto-updated)
├── completed_at: DateTime (optional)
└── metadata: JSONB (flexible key-value storage)
```

### 3.2 Relationships and Constraints
- Unique constraint on (user_id, title) to prevent duplicate todos per user
- Cascade delete on user deletion
- Check constraint: completed_at must be set when status is 'completed'
- Check constraint: due_date must be in the future on creation

### 3.3 Indexes
- Composite index on (user_id, status, created_at) for efficient filtering
- Composite index on (user_id, due_date) for deadline queries
- GIN index on tags for array search operations
- Full-text search index on (title, description) for search functionality

---

## 4. API Contracts

### 4.1 Create Todo
```
POST /api/v1/todos
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "title": "Analyze 2024 Monaco GP performance",
  "description": "Compare lap times between top 3 drivers",
  "priority": "high",
  "due_date": "2026-02-15T00:00:00Z",
  "tags": ["analysis", "monaco", "performance"]
}

Response (201):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Analyze 2024 Monaco GP performance",
  "description": "Compare lap times between top 3 drivers",
  "status": "pending",
  "priority": "high",
  "due_date": "2026-02-15T00:00:00Z",
  "tags": ["analysis", "monaco", "performance"],
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2026-02-02T15:36:58Z",
  "updated_at": "2026-02-02T15:36:58Z",
  "completed_at": null,
  "metadata": {}
}
```

### 4.2 List Todos
```
GET /api/v1/todos?status=pending&priority=high&limit=20&offset=0&sort_by=due_date&order=asc
Authorization: Bearer <token>

Response (200):
{
  "items": [...],
  "total": 45,
  "limit": 20,
  "offset": 0,
  "has_next": true
}
```

### 4.3 Get Todo by ID
```
GET /api/v1/todos/{todo_id}
Authorization: Bearer <token>

Response (200): {Todo Object}
```

### 4.4 Update Todo
```
PATCH /api/v1/todos/{todo_id}
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "status": "completed",
  "completed_at": "2026-02-03T10:30:00Z"
}

Response (200): {Updated Todo Object}
```

### 4.5 Delete Todo
```
DELETE /api/v1/todos/{todo_id}
Authorization: Bearer <token>

Response (204): No Content
```

### 4.6 Search Todos
```
GET /api/v1/todos/search?q=analysis&tags=monaco,performance
Authorization: Bearer <token>

Response (200): {Paginated Todo List}
```

### 4.7 Bulk Operations
```
POST /api/v1/todos/bulk/complete
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "todo_ids": ["uuid1", "uuid2", "uuid3"]
}

Response (200):
{
  "updated": 3,
  "failed": []
}
```

---

## 5. Technology Stack

### Backend
- **Framework:** FastAPI 0.104+ (existing framework)
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0+ with async support
- **Validation:** Pydantic v2 for request/response schemas
- **Database Migrations:** Alembic 1.12+
- **Authentication:** JWT tokens with PyJWT library
- **Task Queue:** Celery 5.3+ (for async operations like bulk updates)
- **Caching:** Redis 7.0+ for query result caching

### Frontend
- **Not in scope for initial implementation** - API-first approach
- Future consideration: React/Vue.js SPA for todo management UI
- Swagger UI and ReDoc for API documentation and testing

### Infrastructure
- **Container Runtime:** Docker 24.0+
- **Container Orchestration:** Kubernetes 1.28+ (for production) or Docker Compose (for development)
- **API Gateway:** NGINX or Traefik for routing and load balancing
- **Service Mesh:** Istio (optional, for advanced traffic management)

### Data Storage
- **Primary Database:** PostgreSQL 15+ with JSONB support for metadata
- **Cache Layer:** Redis 7.0+ for:
  - Query result caching (TTL: 5 minutes)
  - Session storage
  - Rate limiting data
- **Backup Strategy:** 
  - Continuous WAL archiving to S3/GCS
  - Daily full backups with 30-day retention
  - Point-in-time recovery capability

---

## 6. Integration Points

### 6.1 Authentication Service
Integration with existing or new JWT-based authentication service for user identity management. Todos are scoped to authenticated users.

### 6.2 F1 Analytics Integration (Future)
- Ability to create todos linked to specific F1 races, drivers, or analysis tasks
- Webhook notifications when F1 data updates complete
- Auto-generate todos for scheduled analysis tasks

### 6.3 Notification Service (Future)
- Email notifications for approaching due dates
- Webhook endpoints for external task management systems
- Push notifications for mobile clients

### 6.4 Monitoring and Observability
- Integration with Prometheus for metrics collection
- OpenTelemetry for distributed tracing
- Structured logging to centralized log aggregation system

### 6.5 External Calendar Integration (Future)
- iCal export for todo due dates
- Google Calendar / Outlook Calendar sync

---

## 7. Security Architecture

### 7.1 Authentication
- **JWT Bearer Tokens:** All todo endpoints require valid JWT tokens in Authorization header
- **Token Validation:** Verify signature, expiration, and issuer on every request
- **Token Refresh:** Implement refresh token mechanism for long-lived sessions
- **User Context:** Extract user_id from token claims to scope all operations

### 7.2 Authorization
- **Row-Level Security:** Users can only access their own todos
- **Role-Based Access Control (RBAC):** Support for admin role with cross-user access
- **Operation Permissions:** Fine-grained permissions for create, read, update, delete operations

### 7.3 Data Protection
- **Encryption at Rest:** PostgreSQL transparent data encryption (TDE) for database files
- **Encryption in Transit:** TLS 1.3 for all API communications
- **Secrets Management:** HashiCorp Vault or AWS Secrets Manager for database credentials and JWT signing keys
- **Input Validation:** Strict Pydantic schema validation to prevent injection attacks

### 7.4 API Security
- **Rate Limiting:** 100 requests/minute per user, 1000 requests/minute per IP
- **CORS Policy:** Configurable allowed origins, strict in production
- **SQL Injection Prevention:** Parameterized queries via SQLAlchemy ORM
- **XSS Prevention:** Content-Type validation, no HTML rendering
- **CSRF Protection:** Not required for stateless JWT-based API

### 7.5 Audit and Compliance
- **Audit Logging:** Log all create, update, delete operations with user_id and timestamp
- **Data Retention:** Configurable soft-delete with 90-day retention before permanent deletion
- **GDPR Compliance:** User data export and right-to-be-forgotten endpoints

---

## 8. Deployment Architecture

### 8.1 Container Strategy
- **Docker Images:** Multi-stage builds with Python 3.11-slim base image
- **Image Registry:** Private container registry (Docker Hub, AWS ECR, or GCR)
- **Image Tagging:** Semantic versioning with git commit SHA for traceability

### 8.2 Kubernetes Deployment (Production)
```
Kubernetes Cluster
├── Namespace: f1-analytics-prod
│   ├── Deployment: fastapi-app (3 replicas)
│   │   ├── Container: fastapi-server (port 8000)
│   │   ├── Resources: 500m CPU, 1Gi memory (requests), 1 CPU, 2Gi memory (limits)
│   │   └── Health Probes: liveness (/health), readiness (/health)
│   ├── Service: fastapi-service (ClusterIP)
│   ├── Ingress: api-ingress (HTTPS with TLS)
│   ├── StatefulSet: postgresql-db (1 replica)
│   │   ├── PersistentVolume: 100Gi SSD
│   │   └── Resources: 1 CPU, 4Gi memory
│   ├── Deployment: redis-cache (1 replica)
│   │   └── Resources: 250m CPU, 512Mi memory
│   ├── ConfigMap: app-config (environment variables)
│   └── Secret: app-secrets (database credentials, JWT keys)
```

### 8.3 Development Environment
- **Docker Compose:** Single-file orchestration for local development
- **Hot Reload:** Volume mounts for live code updates
- **Local Database:** PostgreSQL container with persistent volume

### 8.4 CI/CD Pipeline
- **Source Control:** Git with feature branch workflow
- **CI:** GitHub Actions or GitLab CI
  - Linting (flake8, pylint)
  - Unit tests with coverage (pytest, 80% threshold)
  - Integration tests against test database
  - Container image build and push
- **CD:** Automated deployment to staging, manual approval for production
- **Rollback Strategy:** Kubernetes deployment rollback or blue-green deployment

---

## 9. Scalability Strategy

### 9.1 Horizontal Scaling
- **Stateless API:** FastAPI application is fully stateless, enabling unlimited horizontal scaling
- **Kubernetes HPA:** Horizontal Pod Autoscaler targeting 70% CPU utilization
- **Scale Range:** 3-20 pods based on traffic demand
- **Load Balancing:** Kubernetes Service with round-robin distribution

### 9.2 Database Scaling
- **Read Replicas:** PostgreSQL read replicas for query load distribution
- **Connection Pooling:** PgBouncer for efficient connection management (max 100 connections per pod)
- **Query Optimization:** Proper indexing strategy, query plan analysis
- **Partitioning:** Table partitioning by user_id for large-scale deployments (>10M todos)

### 9.3 Caching Strategy
- **Redis Cache:** Cache frequently accessed todo lists with 5-minute TTL
- **Cache Invalidation:** Invalidate user-specific cache on write operations
- **Cache Warming:** Pre-populate cache for common queries on deployment
- **Cache Stampede Prevention:** Distributed locks for cache regeneration

### 9.4 Performance Optimization
- **Database Indexes:** Composite indexes on common query patterns
- **Pagination:** Cursor-based pagination for large result sets
- **Async I/O:** SQLAlchemy async mode for non-blocking database operations
- **Request Batching:** Bulk operations for creating/updating multiple todos

### 9.5 Auto-Scaling Metrics
- **CPU Utilization:** Scale at 70% average CPU
- **Memory Utilization:** Scale at 80% average memory
- **Request Rate:** Scale at 1000 requests/second per pod
- **Response Time:** Scale when p95 latency exceeds 500ms

---

## 10. Monitoring & Observability

### 10.1 Metrics Collection
- **Prometheus Metrics:**
  - Request rate, latency, error rate (RED metrics)
  - Database connection pool utilization
  - Cache hit/miss ratio
  - Todo creation/completion rate
  - API endpoint-specific metrics
- **Custom Metrics:**
  - Todo status distribution
  - Average completion time
  - User activity metrics

### 10.2 Distributed Tracing
- **OpenTelemetry:** Instrument all API endpoints and database queries
- **Trace Context Propagation:** W3C Trace Context standard
- **Jaeger/Tempo:** Trace collection and visualization backend
- **Trace Sampling:** 10% sampling in production, 100% in staging

### 10.3 Logging Strategy
- **Structured Logging:** JSON-formatted logs with consistent schema
- **Log Levels:** DEBUG (development), INFO (production), ERROR (always)
- **Log Aggregation:** ELK Stack (Elasticsearch, Logstash, Kibana) or Loki
- **Log Retention:** 30 days for application logs, 90 days for audit logs
- **Key Log Events:**
  - Todo CRUD operations with user_id
  - Authentication failures
  - Database errors
  - External API failures

### 10.4 Alerting
- **Alert Manager:** Prometheus AlertManager for alert routing
- **Alert Channels:** PagerDuty (critical), Slack (warning), Email (info)
- **Key Alerts:**
  - API error rate > 5% (critical)
  - p95 latency > 1 second (warning)
  - Database connection pool exhausted (critical)
  - Pod crash loop (critical)
  - Cache unavailable (warning)

### 10.5 Dashboards
- **Grafana Dashboards:**
  - Service overview (requests, errors, latency)
  - Database performance (query time, connection count)
  - User activity (active users, todo creation rate)
  - Infrastructure health (CPU, memory, network)

### 10.6 Health Checks
- **Liveness Probe:** GET /health (checks service is running)
- **Readiness Probe:** GET /health (checks database connectivity)
- **Startup Probe:** GET /health (allows slow startup)
- **Probe Configuration:** 
  - Initial delay: 10s
  - Period: 10s
  - Timeout: 5s
  - Failure threshold: 3

---

## 11. Architectural Decisions (ADRs)

### ADR-001: Use PostgreSQL over NoSQL Database
**Decision:** Use PostgreSQL as the primary database for todo storage.

**Rationale:**
- Strong ACID guarantees ensure data consistency for todo operations
- JSONB support provides flexibility for metadata while maintaining structure
- Excellent indexing capabilities including GIN indexes for array/JSONB queries
- Mature ecosystem with proven reliability and tooling
- Aligns with relational requirements (user relationships, referential integrity)
- Full-text search capabilities without additional infrastructure

**Alternatives Considered:**
- MongoDB: Lacks strong consistency guarantees, complex transaction handling
- DynamoDB: Higher operational cost, limited query flexibility
- SQLite: Insufficient for multi-user concurrent access

### ADR-002: Implement Repository Pattern with SQLAlchemy
**Decision:** Use SQLAlchemy ORM with repository pattern for data access.

**Rationale:**
- Abstraction layer enables easier testing with mock repositories
- Async support improves concurrency and throughput
- Type safety with SQLAlchemy 2.0 type annotations
- Migration support via Alembic
- Protection against SQL injection through parameterized queries

**Alternatives Considered:**
- Raw SQL: Less maintainable, more error-prone
- Django ORM: Requires full Django framework
- Tortoise ORM: Less mature ecosystem

### ADR-003: JWT-Based Authentication
**Decision:** Use JWT bearer tokens for API authentication.

**Rationale:**
- Stateless authentication enables horizontal scaling without session storage
- Standard protocol with broad library support
- Can embed user context (user_id, roles) in token claims
- No database lookup required for authentication on every request
- Suitable for API-first architecture

**Alternatives Considered:**
- Session-based auth: Requires sticky sessions or shared session store
- OAuth2: Over-engineered for internal API
- API keys: Less flexible for user context

### ADR-004: Monolithic FastAPI Application Over Microservices
**Decision:** Implement todo functionality within the existing FastAPI monolith.

**Rationale:**
- Simpler deployment and operations for current scale
- Reduced network latency (no inter-service calls)
- Easier debugging and development
- Shared infrastructure (middleware, logging, monitoring)
- Can extract to microservice later if needed

**Alternatives Considered:**
- Separate microservice: Added complexity without clear benefits at current scale
- Serverless functions: Cold start latency, state management challenges

### ADR-005: Redis for Caching Layer
**Decision:** Use Redis for query result caching and rate limiting.

**Rationale:**
- In-memory performance for sub-millisecond cache access
- Rich data structures (strings, lists, sets, sorted sets)
- Built-in TTL support for automatic cache expiration
- Pub/sub capabilities for future real-time features
- Battle-tested reliability and extensive tooling

**Alternatives Considered:**
- Memcached: Limited data structures, no persistence
- Application memory: Not shared across pods, lost on restart

### ADR-006: Cursor-Based Pagination for List Endpoints
**Decision:** Implement cursor-based pagination instead of offset-based.

**Rationale:**
- Consistent results when data changes between requests
- Better performance for large offsets (no need to skip N rows)
- Prevents duplicate or missing items during pagination
- Scalable to millions of records

**Alternatives Considered:**
- Offset-based: Simple but inconsistent and slow for large offsets
- GraphQL Relay: Over-engineered for REST API

### ADR-007: Soft Delete with Retention Policy
**Decision:** Implement soft delete with 90-day retention before permanent deletion.

**Rationale:**
- Enables undo functionality for accidentally deleted todos
- Supports audit requirements and compliance
- Allows data recovery during incident response
- Minimal storage overhead with archive status

**Alternatives Considered:**
- Hard delete: No recovery option, fails compliance requirements
- Indefinite retention: Storage cost grows unbounded

### ADR-008: API Versioning in URL Path
**Decision:** Version the API using URL path prefix (/api/v1/todos).

**Rationale:**
- Clear and explicit versioning visible in URLs
- Supports parallel version deployment
- Easy to route at load balancer/gateway level
- Industry standard practice

**Alternatives Considered:**
- Header-based versioning: Less discoverable, harder to test
- Query parameter: Non-standard, poor caching behavior

---

## Appendix: PRD Reference

PRD reference: docs/plans/todo-api/PRD.md (file not yet committed)
