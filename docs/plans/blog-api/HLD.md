Now I'll generate the HLD document based on the PRD:

# High-Level Design: aiworkshop

**Created:** 2026-02-02T15:47:43Z
**Status:** Draft

## 1. Architecture Overview

<!-- AI: Describe the overall system architecture (microservices, monolith, serverless, etc.) -->

The system follows a **three-tier monolithic architecture** with clear separation of concerns:

- **Presentation Layer (API Layer):** RESTful HTTP API endpoints handling client requests and responses
- **Business Logic Layer (Service Layer):** Core application logic for user management, post management, and comment management
- **Data Access Layer (Repository/DAO Layer):** Abstraction over database operations with ORM/ODM

**Architecture Pattern:** MVC (Model-View-Controller) adapted for API development where controllers handle HTTP concerns, services contain business logic, and models represent data entities.

**Communication:** Synchronous HTTP/HTTPS request-response pattern. The API is stateless to enable horizontal scalability.

**Rationale:** A monolithic architecture is appropriate for this MVP blogging platform as it:
- Simplifies deployment and development for a small-to-medium scale application
- Reduces operational complexity compared to microservices
- Provides sufficient scalability for initial requirements (100 concurrent users)
- Allows faster time-to-market with simpler debugging and testing

---

## 2. System Components

<!-- AI: List major components/services with brief descriptions -->

### Core API Server
Central application server exposing RESTful endpoints for all operations.

### Authentication Module
- **JWT Token Manager:** Generates, validates, and refreshes JWT tokens
- **Password Manager:** Handles password hashing (bcrypt) and verification
- **Auth Middleware:** Intercepts requests to validate authentication tokens

### User Service
- Handles user registration, profile management, and retrieval
- Enforces email/username uniqueness validation
- Manages user data integrity

### Post Service
- Manages blog post CRUD operations
- Enforces authorization (users can only modify their own posts)
- Handles post-author relationships and timestamps

### Comment Service
- Manages comment CRUD operations on blog posts
- Enforces authorization (users can only modify their own comments)
- Maintains post-comment relationships

### Validation Layer
- Input validation middleware for request payloads
- Schema validation for user, post, and comment data
- Sanitization to prevent injection attacks

### Error Handler
- Centralized error handling and logging
- Consistent error response formatting
- HTTP status code mapping

### Database Connection Manager
- Connection pooling for database efficiency
- Transaction management for data consistency
- Database health monitoring

---

## 3. Data Model

<!-- AI: High-level data entities and relationships -->

### User Entity
```
User {
  id: UUID/Integer (PK)
  username: String (unique, indexed)
  email: String (unique, indexed)
  passwordHash: String
  createdAt: Timestamp
  updatedAt: Timestamp
}
```

### Post Entity
```
Post {
  id: UUID/Integer (PK)
  title: String (indexed)
  content: Text
  authorId: UUID/Integer (FK -> User.id, indexed)
  createdAt: Timestamp (indexed)
  updatedAt: Timestamp
}
```

### Comment Entity
```
Comment {
  id: UUID/Integer (PK)
  content: Text
  postId: UUID/Integer (FK -> Post.id, indexed)
  authorId: UUID/Integer (FK -> User.id, indexed)
  createdAt: Timestamp (indexed)
  updatedAt: Timestamp
}
```

### Relationships
- **User → Post:** One-to-Many (one user can author many posts)
- **User → Comment:** One-to-Many (one user can author many comments)
- **Post → Comment:** One-to-Many (one post can have many comments)

### Indexes
- Primary keys on all entities
- Unique indexes on User.username and User.email
- Foreign key indexes on Post.authorId, Comment.postId, Comment.authorId
- Composite index on (Comment.postId, Comment.createdAt) for efficient comment retrieval

---

## 4. API Contracts

<!-- AI: Define key API endpoints, request/response formats -->

### Authentication Endpoints

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123",
    "username": "johndoe",
    "email": "user@example.com"
  }
}
```

### User Endpoints

**POST /api/users** (Register)
```json
Request:
{
  "username": "johndoe",
  "email": "user@example.com",
  "password": "securePassword123"
}

Response (201 Created):
{
  "id": "123",
  "username": "johndoe",
  "email": "user@example.com",
  "createdAt": "2026-02-02T15:47:43Z"
}
```

**GET /api/users/:id** (Get User Profile)
```json
Response (200 OK):
{
  "id": "123",
  "username": "johndoe",
  "email": "user@example.com",
  "createdAt": "2026-02-02T15:47:43Z"
}
```

**PUT /api/users/:id** (Update Profile - Authenticated)
```json
Request:
{
  "username": "johndoe_updated",
  "email": "newemail@example.com"
}

Response (200 OK):
{
  "id": "123",
  "username": "johndoe_updated",
  "email": "newemail@example.com",
  "updatedAt": "2026-02-02T16:00:00Z"
}
```

### Post Endpoints

**GET /api/posts** (List Posts)
```json
Query params: ?page=1&limit=20

Response (200 OK):
{
  "data": [
    {
      "id": "456",
      "title": "My First Blog Post",
      "content": "This is the content...",
      "author": {
        "id": "123",
        "username": "johndoe"
      },
      "createdAt": "2026-02-02T15:47:43Z",
      "updatedAt": "2026-02-02T15:47:43Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

**GET /api/posts/:id** (Get Single Post)
```json
Response (200 OK):
{
  "id": "456",
  "title": "My First Blog Post",
  "content": "This is the content...",
  "author": {
    "id": "123",
    "username": "johndoe"
  },
  "createdAt": "2026-02-02T15:47:43Z",
  "updatedAt": "2026-02-02T15:47:43Z"
}
```

**POST /api/posts** (Create Post - Authenticated)
```json
Request:
{
  "title": "My First Blog Post",
  "content": "This is the content..."
}

Response (201 Created):
{
  "id": "456",
  "title": "My First Blog Post",
  "content": "This is the content...",
  "authorId": "123",
  "createdAt": "2026-02-02T15:47:43Z",
  "updatedAt": "2026-02-02T15:47:43Z"
}
```

**PUT /api/posts/:id** (Update Post - Authenticated, Author Only)
```json
Request:
{
  "title": "Updated Title",
  "content": "Updated content..."
}

Response (200 OK):
{
  "id": "456",
  "title": "Updated Title",
  "content": "Updated content...",
  "authorId": "123",
  "updatedAt": "2026-02-02T16:00:00Z"
}
```

**DELETE /api/posts/:id** (Delete Post - Authenticated, Author Only)
```json
Response (204 No Content)
```

### Comment Endpoints

**GET /api/posts/:postId/comments** (List Comments for Post)
```json
Response (200 OK):
{
  "data": [
    {
      "id": "789",
      "content": "Great post!",
      "author": {
        "id": "124",
        "username": "janedoe"
      },
      "postId": "456",
      "createdAt": "2026-02-02T16:00:00Z",
      "updatedAt": "2026-02-02T16:00:00Z"
    }
  ]
}
```

**POST /api/posts/:postId/comments** (Create Comment - Authenticated)
```json
Request:
{
  "content": "Great post!"
}

Response (201 Created):
{
  "id": "789",
  "content": "Great post!",
  "authorId": "124",
  "postId": "456",
  "createdAt": "2026-02-02T16:00:00Z"
}
```

**PUT /api/comments/:id** (Update Comment - Authenticated, Author Only)
```json
Request:
{
  "content": "Updated comment!"
}

Response (200 OK):
{
  "id": "789",
  "content": "Updated comment!",
  "updatedAt": "2026-02-02T16:30:00Z"
}
```

**DELETE /api/comments/:id** (Delete Comment - Authenticated, Author Only)
```json
Response (204 No Content)
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Email format is invalid"
      }
    ]
  }
}
```

---

## 5. Technology Stack

### Backend
- **Runtime:** Node.js 20 LTS (or Python 3.11+ / Java 17+)
- **Framework:** Express.js 4.x (or FastAPI / Spring Boot)
- **Language:** TypeScript 5.x (or Python / Java)
- **Authentication:** jsonwebtoken library for JWT
- **Password Hashing:** bcrypt (10+ salt rounds)
- **Validation:** Joi / express-validator (or Pydantic / Hibernate Validator)
- **ORM/ODM:** Sequelize / TypeORM (SQL) or Mongoose (MongoDB)
- **HTTP Client:** axios (for potential external integrations)

### Frontend
N/A - API-only (out of scope per PRD NG-001)

### Infrastructure
- **Containerization:** Docker for consistent deployment environments
- **Process Manager:** PM2 (Node.js) or systemd
- **Web Server:** Nginx as reverse proxy for load balancing and SSL termination
- **Environment Management:** dotenv for configuration management
- **API Documentation:** Swagger/OpenAPI 3.0 for API specification

### Data Storage
- **Primary Database:** PostgreSQL 15+ (recommended) or MySQL 8.0+
  - Rationale: ACID compliance, robust relational model for user-post-comment relationships, proven scalability
  - Alternative: MongoDB 6.0+ if document flexibility is prioritized
- **Connection Pooling:** pg-pool (PostgreSQL) or native pool configuration
- **Caching (Future):** Redis 7.x for session storage and query caching (not in MVP scope)

---

## 6. Integration Points

<!-- AI: External systems, APIs, webhooks -->

### Current Integrations
**None** - The system is self-contained for MVP as per PRD non-goals.

### Future Integration Considerations (Out of Scope for MVP)
- **Email Service:** SendGrid / AWS SES for user notifications and password reset
- **OAuth Providers:** Google, GitHub, Facebook for third-party authentication
- **CDN:** CloudFlare / AWS CloudFront for static asset delivery
- **Storage Service:** AWS S3 / Cloudinary for media uploads (images, videos)
- **Search Engine:** Elasticsearch for full-text search functionality
- **Analytics:** Google Analytics API for usage tracking

### External Dependencies (Non-Integration)
- **NPM Registry / PyPI:** Package dependency management
- **GitHub:** Source code repository and CI/CD triggers

---

## 7. Security Architecture

<!-- AI: Authentication, authorization, encryption, secrets management -->

### Authentication
- **Method:** JWT (JSON Web Tokens) with HS256 signing algorithm
- **Token Expiration:** 24 hours (configurable via environment variables)
- **Token Storage:** Client-side storage (not server-side sessions) for stateless architecture
- **Login Flow:** POST /api/auth/login validates credentials, returns JWT token
- **Password Requirements:** Minimum 8 characters (enforced at validation layer)

### Authorization
- **Middleware-Based:** Auth middleware validates JWT on protected routes
- **Resource Ownership:** Service layer validates that users can only modify/delete their own posts and comments
- **Access Control:**
  - Public endpoints: GET /api/posts, GET /api/posts/:id, GET /api/posts/:postId/comments, GET /api/users/:id
  - Authenticated endpoints: All POST, PUT, DELETE operations
  - Ownership validation: PUT/DELETE on posts and comments verify authorId matches authenticated user

### Password Security
- **Hashing Algorithm:** bcrypt with 10 salt rounds (configurable, minimum 10)
- **Storage:** Never store plaintext passwords; only store password hashes
- **Transmission:** Passwords transmitted over HTTPS only (enforced at deployment level)

### Data Protection
- **Encryption in Transit:** HTTPS/TLS 1.3 enforced via Nginx reverse proxy
- **Encryption at Rest:** Database-level encryption (PostgreSQL transparent data encryption)
- **Sensitive Data Handling:**
  - Password hashes never returned in API responses
  - JWT tokens never logged
  - User email addresses not exposed in post/comment public responses

### Input Validation & Sanitization
- **Request Validation:** All inputs validated against schemas (Joi/Pydantic)
- **SQL Injection Prevention:** Parameterized queries via ORM (no raw SQL)
- **XSS Prevention:** Input sanitization and output encoding
- **CSRF Protection:** Not applicable for stateless JWT authentication

### Secrets Management
- **Environment Variables:** All secrets stored in .env files (excluded from git)
- **Secret Types:**
  - JWT_SECRET: Random 256-bit key for token signing
  - DATABASE_URL: Database connection string with credentials
  - PORT, NODE_ENV, BCRYPT_ROUNDS: Configuration values
- **Production:** Use managed secret services (AWS Secrets Manager, HashiCorp Vault)

### API Security Headers
- **CORS:** Configured to allow specific origins (wildcard for development, restricted for production)
- **Rate Limiting:** (Future enhancement) 100 requests per minute per IP
- **Security Headers:** Helmet.js middleware (X-Content-Type-Options, X-Frame-Options, etc.)

### Logging & Auditing
- **Access Logs:** All API requests logged with timestamp, endpoint, user ID, status code
- **Sensitive Data Exclusion:** Never log passwords, tokens, or full request bodies with sensitive data
- **Audit Trail:** User actions (create, update, delete) logged for security monitoring

---

## 8. Deployment Architecture

<!-- AI: How components are deployed (K8s, containers, serverless) -->

### Deployment Model: Containerized Application with Reverse Proxy

### Component Deployment

**Application Container (Docker)**
- **Image:** Custom Node.js/Python/Java Docker image with application code
- **Base Image:** node:20-alpine / python:3.11-slim / openjdk:17-slim
- **Exposed Port:** 3000 (internal)
- **Environment:** Production environment variables injected at runtime
- **Health Check:** HTTP GET /api/health endpoint

**Database**
- **Deployment:** Managed PostgreSQL service (AWS RDS, DigitalOcean Managed Database)
- **Alternative:** Self-hosted PostgreSQL in separate container with persistent volume
- **Backup:** Automated daily backups with 7-day retention

**Reverse Proxy (Nginx)**
- **Container/VM:** Nginx container or standalone VM
- **Configuration:**
  - SSL/TLS termination with Let's Encrypt certificates
  - Proxy requests to application container on port 3000
  - Static file serving (if needed for API documentation)
  - Load balancing across multiple application instances

### Deployment Topology

```
Internet
   |
   v
[Nginx Reverse Proxy] (Port 443 HTTPS)
   |
   v
[Application Container(s)] (Port 3000)
   |
   v
[PostgreSQL Database] (Port 5432)
```

### Environment Configuration

**Development**
- Single application container
- Local PostgreSQL instance or Docker container
- No SSL (HTTP only)

**Staging**
- Single application container
- Shared managed database
- SSL enabled with staging certificates

**Production**
- Multiple application containers (2-3 instances) behind Nginx load balancer
- Managed PostgreSQL with read replicas (future)
- SSL enabled with production certificates
- Environment variable injection via Docker secrets or orchestration platform

### Deployment Strategy
- **Blue-Green Deployment:** Maintain two identical environments, switch traffic after validation
- **Rollback Plan:** Keep previous container version for quick rollback
- **Database Migrations:** Run migrations before deploying new application version
- **Zero-Downtime:** Rolling updates with health checks before routing traffic

### Infrastructure Options

**Option 1: Cloud VMs (AWS EC2, DigitalOcean Droplets)**
- Docker Compose for container orchestration
- Manual scaling by launching additional VMs

**Option 2: Container Orchestration (AWS ECS, DigitalOcean App Platform)**
- Managed container orchestration
- Automated scaling and health monitoring

**Option 3: Platform-as-a-Service (Heroku, Railway, Render)**
- Simplified deployment with git push
- Built-in PostgreSQL addon
- Limited customization but faster setup

**Recommended for MVP:** Option 3 (PaaS) for rapid deployment, migrate to Option 2 for production scale.

---

## 9. Scalability Strategy

<!-- AI: How the system scales (horizontal, vertical, auto-scaling) -->

### Horizontal Scaling (Primary Strategy)

**Application Tier**
- **Stateless Design:** No server-side sessions; JWT tokens enable any instance to handle requests
- **Load Balancing:** Nginx distributes requests across multiple application containers using round-robin or least-connections algorithm
- **Instance Scaling:** Add/remove application containers based on CPU/memory metrics
- **Target:** Scale from 1 to 5 instances to handle 100-500 concurrent users

**Implementation:**
- Docker Compose `replicas` configuration or orchestration platform (ECS, Kubernetes) scaling policies
- Auto-scaling triggers: CPU > 70% for 5 minutes, scale up; CPU < 30% for 10 minutes, scale down

### Database Scaling

**Read Scaling (Future Enhancement)**
- **Read Replicas:** PostgreSQL read replicas for GET requests (read-heavy workload)
- **Connection Pooling:** Max 100 connections per instance, pooled across replicas
- **Query Optimization:** Indexes on frequently queried fields (authorId, postId, createdAt)

**Write Scaling (Future Enhancement)**
- **Sharding:** Shard by user ID or post ID for horizontal database scaling (beyond 100K users)
- **Partitioning:** Table partitioning by date for posts/comments (archive old data)

### Vertical Scaling (Short-Term Strategy)
- **Initial Setup:** 2 vCPU, 4GB RAM for application container
- **Scale-Up Path:** Increase to 4 vCPU, 8GB RAM if single instance reaches capacity
- **Database:** Start with db.t3.medium (2 vCPU, 4GB), scale to db.t3.large (2 vCPU, 8GB)

### Caching Strategy (Future Enhancement)
- **Redis Cache:** Cache frequently accessed posts and user profiles
- **Cache Invalidation:** Invalidate on update/delete operations
- **TTL:** 5-minute TTL for post lists, 1-hour TTL for user profiles

### Content Delivery Optimization
- **Pagination:** Default 20 items per page, maximum 100 items per request
- **Lazy Loading:** Fetch comments only when post detail is accessed (not in list view)
- **Field Selection:** Support query parameters to return partial data (future enhancement)

### Performance Targets
- **Current Load:** 100 concurrent users, 50 requests per second
- **Scaling Target:** 500 concurrent users, 250 requests per second
- **Database Capacity:** 100,000 posts, 1,000,000 comments (per NFR-SC-001)

### Bottleneck Identification
- **Monitoring:** Track response times per endpoint to identify slow queries
- **Database Query Analysis:** EXPLAIN ANALYZE for slow queries, add indexes as needed
- **Connection Pool Monitoring:** Alert when pool exhaustion occurs

---

## 10. Monitoring & Observability

<!-- AI: Logging, metrics, tracing, alerting strategy -->

### Logging Strategy

**Application Logs**
- **Framework:** Winston (Node.js) / Python logging / Logback (Java)
- **Log Levels:**
  - ERROR: Application errors, unhandled exceptions, authentication failures
  - WARN: Validation failures, authorization denials, deprecated API usage
  - INFO: Request/response logs (endpoint, status code, user ID, duration)
  - DEBUG: Detailed debugging info (development only)
- **Log Format:** Structured JSON logs with timestamp, level, message, context (userId, requestId)
- **Sensitive Data:** Never log passwords, tokens, or full request bodies with PII

**Access Logs**
- **Nginx Access Logs:** HTTP request logs (IP, method, endpoint, status, response time)
- **Format:** JSON format for easy parsing and analysis

**Log Aggregation**
- **Development:** Console output and local file rotation
- **Production:** Centralized logging via CloudWatch Logs (AWS), Papertrail, or ELK Stack
- **Retention:** 30 days for INFO logs, 90 days for ERROR logs

### Metrics & Monitoring

**Application Metrics**
- **Response Time:** 95th and 99th percentile latency per endpoint
- **Request Rate:** Requests per second, broken down by endpoint
- **Error Rate:** 4xx and 5xx errors per minute
- **Active Users:** Concurrent authenticated sessions (approximation via request patterns)

**System Metrics**
- **CPU Utilization:** Per container/instance
- **Memory Usage:** Heap usage, RSS, garbage collection frequency
- **Network I/O:** Inbound/outbound traffic

**Database Metrics**
- **Connection Pool:** Active/idle/waiting connections
- **Query Performance:** Slow query log (queries > 100ms)
- **Database Size:** Table sizes, index sizes, growth rate
- **Replication Lag:** If read replicas are used

**Monitoring Tools**
- **APM:** New Relic, Datadog, or Prometheus + Grafana
- **Database Monitoring:** PostgreSQL pg_stat_statements, AWS RDS Performance Insights
- **Uptime Monitoring:** Uptime Robot, Pingdom for endpoint availability checks

### Health Checks

**Liveness Probe:** `GET /api/health`
```json
Response (200 OK):
{
  "status": "healthy",
  "timestamp": "2026-02-02T15:47:43Z"
}
```

**Readiness Probe:** `GET /api/health/ready`
```json
Response (200 OK):
{
  "status": "ready",
  "database": "connected",
  "timestamp": "2026-02-02T15:47:43Z"
}
```

### Alerting Strategy

**Critical Alerts (Page On-Call)**
- Application error rate > 5% for 5 minutes
- Database connection failures
- API downtime > 1 minute (uptime monitor failure)
- Disk space > 90% full

**Warning Alerts (Slack/Email)**
- Response time 95th percentile > 500ms for 10 minutes
- CPU utilization > 80% for 10 minutes
- Memory usage > 85% for 10 minutes
- Error rate > 1% for 10 minutes

**Alerting Channels**
- **Critical:** PagerDuty or OpsGenie for on-call rotation
- **Warning:** Slack channel, email notifications

### Distributed Tracing (Future Enhancement)
- **Trace Context:** Request ID propagated through all log entries
- **Tracing System:** Jaeger or AWS X-Ray for end-to-end request tracing
- **Trace Key Operations:** Database queries, external API calls

### Dashboards
- **Operations Dashboard:** Response times, error rates, request volume, system health
- **Business Dashboard:** User registrations, post/comment creation rates, active users
- **Database Dashboard:** Query performance, connection pool status, table sizes

---

## 11. Architectural Decisions (ADRs)

<!-- AI: Key architectural decisions with rationale -->

### ADR-001: Monolithic Architecture Over Microservices
**Decision:** Implement as a single monolithic application rather than microservices.

**Rationale:**
- MVP scope is small and well-defined with three core entities (users, posts, comments)
- Deployment and operational complexity of microservices unnecessary for initial scale
- Shared data model (users referenced by posts and comments) simplifies transactional consistency
- Team size and development velocity favor simpler architecture
- Can refactor to microservices later if specific components require independent scaling

**Consequences:**
- Faster initial development and deployment
- Easier debugging and testing
- Entire application must be deployed as a unit (no independent service deployments)
- All components share same runtime and resources

---

### ADR-002: JWT Authentication Over Session-Based Authentication
**Decision:** Use JWT tokens for authentication instead of server-side sessions.

**Rationale:**
- Stateless authentication enables horizontal scaling without session store (NFR-SC-002)
- No need for Redis or session database, reducing infrastructure complexity
- Tokens can be verified by any application instance without shared state
- Aligns with modern API authentication best practices

**Consequences:**
- Token revocation requires additional mechanism (not in MVP scope)
- Token size larger than session IDs (increased network overhead)
- Expiration-based logout (cannot invalidate tokens server-side in MVP)

---

### ADR-003: PostgreSQL as Primary Database
**Decision:** Use PostgreSQL as the primary database over MongoDB or other NoSQL options.

**Rationale:**
- Relational model naturally fits user-post-comment relationships with foreign keys
- ACID compliance ensures data consistency for transactional operations
- Strong query capabilities for filtering, sorting, and pagination
- Proven scalability path with read replicas and sharding
- Rich ecosystem of tools, ORMs, and monitoring solutions

**Consequences:**
- Schema migrations required for data model changes
- Less flexible for unstructured data (not a requirement for this project)
- Vertical scaling limits higher than horizontal, but read replicas available for scaling

---

### ADR-004: RESTful API Over GraphQL
**Decision:** Implement REST API following standard HTTP conventions rather than GraphQL.

**Rationale:**
- REST aligns with PRD requirements and acceptance criteria (FR-020, FR-021)
- Simpler learning curve for API consumers
- Well-defined CRUD operations map cleanly to HTTP methods
- Tooling and caching infrastructure mature for REST
- GraphQL over-engineering for simple resource-based API

**Consequences:**
- Multiple requests required for nested data (e.g., post + comments requires 2 requests)
- Over-fetching or under-fetching data compared to GraphQL's field selection
- Simpler client implementation and API documentation

---

### ADR-005: bcrypt for Password Hashing
**Decision:** Use bcrypt with 10 salt rounds for password hashing.

**Rationale:**
- Industry-standard algorithm designed for password hashing (NFR-S-001)
- Adaptive hashing automatically slows brute-force attacks
- Well-tested libraries available in all major languages
- Configurable work factor (salt rounds) allows tuning security vs performance

**Consequences:**
- Slower than SHA-256 (intentional for security)
- Higher CPU usage during login/registration (acceptable for use case)
- Future migration to Argon2 possible if security requirements increase

---

### ADR-006: Pagination Required for List Endpoints
**Decision:** Implement pagination for GET /api/posts and GET /api/posts/:postId/comments endpoints.

**Rationale:**
- Prevents unbounded response sizes as data grows (NFR-P-003, NFR-SC-001)
- Improves API response times by limiting query result set
- Standard practice for scalable APIs
- Aligns with performance requirements (<200ms response time)

**Consequences:**
- Clients must handle pagination logic
- Default page size of 20 items balances performance and usability
- Requires total count queries for accurate pagination metadata (potential performance impact)

---

### ADR-007: Authorization via Ownership Model
**Decision:** Implement authorization based on resource ownership (users can modify only their own posts/comments).

**Rationale:**
- PRD does not specify role-based access control (out of scope per OOS-008)
- Ownership model sufficient for MVP requirements (FR-011, FR-012, FR-017, FR-018)
- Simpler implementation than RBAC (no roles table or permission checks)
- Aligns with acceptance criteria (US-004, US-007)

**Consequences:**
- No admin or moderator roles in MVP
- Content moderation requires manual database operations or future enhancement
- Easier to extend to RBAC later by adding role checks on top of ownership

---

### ADR-008: Docker for Deployment Packaging
**Decision:** Package application as Docker container for deployment.

**Rationale:**
- Consistent deployment environment across development, staging, and production
- Simplified dependency management (all dependencies in container image)
- Portable across cloud providers and local environments
- Enables horizontal scaling via container orchestration

**Consequences:**
- Requires Docker knowledge for deployment operations
- Container image build time added to CI/CD pipeline
- Increased complexity compared to bare-metal or PaaS deployments (mitigated by PaaS Docker support)

---

### ADR-009: Nginx as Reverse Proxy
**Decision:** Use Nginx as reverse proxy in front of application containers.

**Rationale:**
- SSL/TLS termination offloaded from application layer
- Load balancing across multiple application instances
- Static file serving for API documentation (future)
- Industry-standard solution with mature tooling
- Better performance than application-level HTTPS

**Consequences:**
- Additional component to configure and monitor
- Network hop adds minimal latency (<5ms)
- Simplifies application code (no HTTPS handling)

---

### ADR-010: No Real-Time Features in MVP
**Decision:** Exclude WebSocket or real-time update mechanisms from MVP.

**Rationale:**
- Explicitly out of scope per PRD (NG-002, OOS-003)
- Increases architectural complexity (stateful connections, scaling challenges)
- Polling or refresh sufficient for blogging platform use case
- Can be added later if user demand justifies complexity

**Consequences:**
- Clients must poll or refresh to see new posts/comments
- Simplified architecture with stateless HTTP-only communication
- Lower infrastructure costs without persistent connection management

---

## Appendix: PRD Reference

PRD reference: docs/plans/blog-api/PRD.md (file not yet committed)
