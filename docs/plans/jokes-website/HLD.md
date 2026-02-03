# High-Level Design: aiworkshop

**Created:** 2026-02-03T08:26:10Z
**Status:** Draft

## 1. Architecture Overview

<!-- AI: Describe the overall system architecture (microservices, monolith, serverless, etc.) -->

This is a **client-side only, static single-page application (SPA)** architecture designed for deployment on AWS S3 static hosting. The system follows a JAMstack approach with no backend servers or databases.

**Architecture Pattern:** Static SPA with client-side rendering

**Key Characteristics:**
- All application logic runs entirely in the browser
- Jokes data is bundled as static JSON assets at build time
- React-based frontend compiled to static HTML, CSS, and JavaScript
- Client-side routing handled by React Router with HTML5 history API
- No server-side processing or API calls required
- Content delivery through S3 static hosting with optional CloudFront CDN

**Request Flow:**
1. User requests website URL
2. S3 serves index.html
3. Browser downloads JavaScript bundle and assets
4. React application hydrates and renders
5. All navigation and interactions happen client-side
6. Joke data loaded from bundled JSON files

---

## 2. System Components

<!-- AI: List major components/services with brief descriptions -->

### Frontend Application Components

**1. React Application Shell**
- Entry point and root component
- Manages global state and routing configuration
- Handles error boundaries and fallback UI

**2. Routing Module**
- React Router integration for SPA navigation
- Route definitions for home, categories, individual jokes
- 404 handling and redirects

**3. Joke Display Component**
- Renders individual joke content
- Handles setup/punchline formatting
- Supports different joke types (one-liners, Q&A, knock-knock)

**4. Navigation Component**
- Next/previous controls
- Category filters and selection
- Home/back navigation

**5. Category Browser**
- Lists available joke categories
- Filters jokes by selected category
- Updates URL with category selection

**6. Landing Page**
- Welcome screen with site introduction
- Featured or random joke display
- Call-to-action to browse categories

**7. Joke Data Manager**
- Loads and parses static JSON joke data
- Implements search and filter logic
- Manages joke indexing for navigation

**8. Layout Components**
- Responsive header/footer
- Mobile-friendly navigation drawer
- Consistent page layout structure

### Static Assets

**9. Joke Data Store (JSON)**
- jokes.json: Array of joke objects with metadata
- Categorized and indexed for efficient access
- Includes joke ID, text, category, tags

**10. Build Output**
- Compiled JavaScript bundles
- CSS stylesheets
- Static HTML shell (index.html)
- Asset manifest for cache busting

---

## 3. Data Model

<!-- AI: High-level data entities and relationships -->

### Joke Entity
```
Joke {
  id: string (unique identifier, e.g., "joke-001")
  type: enum ["one-liner", "qa", "knock-knock", "story"]
  category: string (e.g., "puns", "dad-jokes", "knock-knock")
  setup: string (question or setup text, optional for one-liners)
  punchline: string (answer or punchline)
  tags: array<string> (optional keywords for future search)
  dateAdded: ISO8601 timestamp
}
```

### Category Entity
```
Category {
  id: string (e.g., "dad-jokes")
  name: string (display name, e.g., "Dad Jokes")
  description: string
  jokeCount: number (calculated at build time)
  icon: string (optional emoji or icon identifier)
}
```

### Application State (Client-Side)
```
AppState {
  jokes: array<Joke> (loaded from JSON)
  categories: array<Category> (derived from jokes)
  currentJoke: Joke | null
  currentCategory: string | null
  viewHistory: array<string> (joke IDs for back navigation)
  filters: {
    category: string | null
    searchTerm: string | null
  }
}
```

### Data Storage Structure
```
/public/data/
  jokes.json          # Main joke dataset
  categories.json     # Category metadata (optional)
```

**Relationships:**
- One Category → Many Jokes (one-to-many)
- Jokes are self-contained with no foreign key relationships
- All relationships resolved client-side through filtering

---

## 4. API Contracts

<!-- AI: Define key API endpoints, request/response formats -->

**Note:** This application has no backend APIs. All data access is through static JSON files loaded at runtime.

### Static Data Contracts

**GET /data/jokes.json**
```json
{
  "version": "1.0",
  "lastUpdated": "2026-02-03T08:00:00Z",
  "jokes": [
    {
      "id": "joke-001",
      "type": "qa",
      "category": "puns",
      "setup": "Why don't scientists trust atoms?",
      "punchline": "Because they make up everything!",
      "tags": ["science", "wordplay"],
      "dateAdded": "2026-01-15T10:00:00Z"
    }
  ]
}
```

**GET /data/categories.json** (Optional)
```json
{
  "categories": [
    {
      "id": "puns",
      "name": "Puns",
      "description": "Clever wordplay and puns",
      "icon": "🎭"
    }
  ]
}
```

### Client-Side Routing URLs

| Route | Purpose | Parameters |
|-------|---------|------------|
| `/` | Home/landing page | None |
| `/jokes` | Browse all jokes | `?category=<id>` (optional filter) |
| `/jokes/:id` | View specific joke | `:id` - joke identifier |
| `/categories` | List all categories | None |
| `/categories/:category` | Jokes by category | `:category` - category ID |
| `*` | 404 fallback | None |

**URL Query Parameters:**
- `category`: Filter jokes by category (e.g., `?category=puns`)
- `page`: Pagination (future enhancement)

---

## 5. Technology Stack

### Backend
**Not Applicable** - This is a static frontend-only application with no backend services.

### Frontend
- **React 18+**: UI framework for component-based architecture
- **React Router v6**: Client-side routing and navigation
- **JavaScript (ES6+)**: Primary programming language
- **CSS3 / CSS Modules**: Styling with scoped component styles
- **Vite**: Build tool and development server (fast HMR, optimized builds)
  - Alternative: Create React App (CRA) if preferred
- **ESLint + Prettier**: Code quality and formatting
- **Jest + React Testing Library**: Unit and component testing (optional)

### Infrastructure
- **AWS S3**: Static website hosting (primary hosting platform)
- **AWS CloudFront**: CDN for global content delivery (optional but recommended)
- **AWS Route 53**: DNS management (if custom domain required)
- **AWS Certificate Manager**: SSL/TLS certificates for HTTPS
- **GitHub Actions / AWS CodePipeline**: CI/CD for automated deployment

### Data Storage
**Client-Side Storage Only:**
- **Static JSON Files**: Joke data embedded in build artifacts
- **Browser LocalStorage**: Optional for user preferences (theme, favorites)
- **Browser SessionStorage**: Temporary navigation state
- **No Database**: All data is static and bundled at build time

---

## 6. Integration Points

<!-- AI: External systems, APIs, webhooks -->

**This application has minimal external integrations as it is entirely self-contained.**

### Optional Third-Party Integrations

**1. Analytics (Optional)**
- **Google Analytics 4** or **Plausible Analytics**: Track page views and user behavior
- Integration: Client-side JavaScript snippet in index.html
- Data sent: Page views, navigation events, category selections
- Privacy: Comply with minimal data collection practices

**2. Social Sharing**
- **Native Web Share API**: Browser-native sharing for mobile devices
- **Open Graph Meta Tags**: Rich previews when sharing joke URLs
- **Twitter Card Meta Tags**: Enhanced Twitter sharing experience
- No external API calls required - metadata embedded in HTML

**3. CDN (AWS CloudFront)**
- Distributes static assets globally
- Integration: S3 bucket configured as CloudFront origin
- Improves load times for international users

**4. Error Tracking (Optional)**
- **Sentry** or **LogRocket**: Client-side error monitoring
- Captures JavaScript errors and performance issues
- Integration: JavaScript SDK loaded asynchronously

### Build-Time Integrations

**1. Node Package Registry (npm)**
- Fetch React and dependency packages during build
- No runtime dependency

**2. CI/CD Pipeline**
- GitHub → GitHub Actions → AWS S3
- Automated build and deployment on git push

**No webhooks, no real-time integrations, no external API dependencies for core functionality.**

---

## 7. Security Architecture

<!-- AI: Authentication, authorization, encryption, secrets management -->

### Security Principles

This static application has a minimal security surface area. Security focuses on secure delivery, content integrity, and preventing XSS vulnerabilities.

**1. Transport Security**
- **HTTPS Only**: All content served over TLS 1.2+ via CloudFront/S3
- **HSTS Headers**: Force HTTPS with Strict-Transport-Security headers
- **SSL/TLS Certificates**: Managed via AWS Certificate Manager

**2. Content Security Policy (CSP)**
- Strict CSP headers configured in S3 bucket metadata or CloudFront
- Example policy:
  ```
  Content-Security-Policy: 
    default-src 'self'; 
    script-src 'self'; 
    style-src 'self' 'unsafe-inline'; 
    img-src 'self' data:; 
    font-src 'self';
  ```
- Prevents XSS by restricting script sources

**3. Input Sanitization**
- No user input accepted (read-only application)
- Joke data sanitized at build time to prevent stored XSS
- React's built-in XSS protection via JSX escaping

**4. Dependency Security**
- Regular `npm audit` to check for vulnerable packages
- Automated dependency updates via Dependabot
- Pin major versions to prevent breaking changes

**5. S3 Bucket Security**
- **Public read access** for website hosting (required)
- **Block public write access** (no uploads allowed)
- **Bucket policies**: Restrict access to CloudFront only (if using CDN)
- **Versioning disabled**: Not needed for static assets
- **Server-side encryption**: Enable S3-SSE for data at rest

**6. Secrets Management**
- **No secrets in frontend code** (public JavaScript bundle)
- Build/deploy credentials stored in GitHub Secrets or AWS Secrets Manager
- No API keys or sensitive data in application

**7. CORS Configuration**
- Not required (all resources served from same origin)
- If using separate CDN domain, configure CORS on S3 bucket

**8. Subresource Integrity (SRI)**
- Consider SRI hashes for CDN-loaded libraries (if any)
- Build tool can generate SRI hashes automatically

**Authentication/Authorization:** Not applicable - public website with no restricted content.

---

## 8. Deployment Architecture

<!-- AI: How components are deployed (K8s, containers, serverless) -->

### Deployment Model: Static S3 Hosting

**Architecture:** Serverless static hosting with optional CDN

```
[Developer] → [Git Push] → [CI/CD Pipeline] → [Build Process] → [S3 Bucket] → [CloudFront CDN] → [Users]
```

### Infrastructure Components

**1. S3 Static Website Hosting**
- **Bucket Configuration:**
  - Enable static website hosting
  - Set index.html as index document
  - Set index.html as error document (for SPA routing)
  - Configure CORS if needed
  - Set appropriate cache-control headers
- **Bucket Policy:** Allow public read access
- **Region:** Choose region closest to primary user base

**2. CloudFront Distribution (Optional but Recommended)**
- **Origin:** S3 bucket configured as origin
- **Cache Behavior:**
  - Cache HTML files with short TTL (5-10 minutes)
  - Cache JS/CSS/images with long TTL (1 year)
  - Use query string cache keys for versioning
- **Custom Domain:** Configure CNAME for custom domain
- **SSL Certificate:** Attach ACM certificate for HTTPS
- **Compression:** Enable Gzip/Brotli compression
- **Error Pages:** Redirect 403/404 to index.html for SPA routing

**3. Route 53 (If Custom Domain)**
- **A Record (Alias):** Points to CloudFront distribution
- **AAAA Record:** IPv6 support
- **Health Checks:** Optional CloudWatch alarms

### CI/CD Pipeline

**Build Pipeline (GitHub Actions Example):**

```yaml
Trigger: Push to main branch
Steps:
  1. Checkout code
  2. Install Node.js dependencies (npm ci)
  3. Run tests (npm test)
  4. Build production bundle (npm run build)
  5. Sync build output to S3 (aws s3 sync)
  6. Invalidate CloudFront cache (aws cloudfront create-invalidation)
```

**Deployment Environments:**
- **Production:** main branch → S3 production bucket
- **Staging (Optional):** develop branch → S3 staging bucket
- **Preview (Optional):** Pull requests → temporary S3 prefix

### Rollback Strategy

- **S3 Versioning:** Enable to keep previous builds
- **CloudFront Invalidation:** Clear cache to revert
- **Git Revert:** Rollback code and redeploy
- **Blue-Green:** Maintain two S3 buckets and swap CloudFront origin

### Deployment Checklist

1. Configure S3 bucket for static hosting
2. Upload build artifacts
3. Set cache-control headers on objects
4. Configure CloudFront distribution
5. Set up custom domain and SSL
6. Test all routes and ensure SPA routing works
7. Verify cache behavior and invalidation
8. Set up monitoring and alarms

**No containers, no Kubernetes, no VMs** - purely static asset hosting.

---

## 9. Scalability Strategy

<!-- AI: How the system scales (horizontal, vertical, auto-scaling) -->

### Scalability Characteristics

**Static websites on S3 + CloudFront are inherently highly scalable** due to the serverless nature and global CDN distribution.

**1. Horizontal Scalability**
- **S3 Auto-Scaling:** Automatic and unlimited (AWS-managed)
- **CloudFront Edge Locations:** 400+ edge locations globally
- **No server capacity planning required:** Scales automatically to millions of requests

**2. Performance Scaling**

**Content Delivery:**
- **CloudFront CDN:** Caches assets at edge locations near users
- **Cache Strategy:**
  - Static assets (JS/CSS/images): 1 year cache TTL
  - HTML files: 5-10 minute TTL or no-cache with ETag
  - Versioned filenames (hash-based) for cache busting
- **Gzip/Brotli Compression:** Reduce transfer size by 70-80%

**Bundle Optimization:**
- **Code Splitting:** Separate vendor and application bundles
- **Lazy Loading:** Load routes on demand with React.lazy()
- **Tree Shaking:** Remove unused code during build
- **Minification:** Terser for JavaScript, cssnano for CSS
- **Image Optimization:** WebP format, responsive images

**3. Data Scalability**

**Joke Data Growth:**
- **Current Design:** Single jokes.json file (supports 100-10,000 jokes)
- **Future Scaling Options:**
  - Split jokes into multiple JSON files by category (lazy load)
  - Implement pagination to load jokes in chunks
  - Use IndexedDB for client-side caching of large datasets
- **JSON File Size Guidelines:**
  - Under 1MB: Single file acceptable
  - 1-5MB: Consider splitting by category
  - Over 5MB: Implement chunking and lazy loading

**4. Traffic Scaling**

**Expected Load Handling:**
- **S3 Request Rate:** 5,500 GET requests/second per prefix (no action needed)
- **CloudFront:** Unlimited requests (AWS scales automatically)
- **Concurrent Users:** Supports millions of concurrent users with no degradation

**Cost-Based Scaling:**
- **S3 Costs:** Pay per GB stored and per request (minimal for static sites)
- **CloudFront Costs:** Pay per GB transferred (reduces S3 egress costs)
- **Cost Optimization:** Enable CloudFront compression to reduce bandwidth

**5. Availability and Reliability Scaling**

- **S3 Durability:** 99.999999999% (11 nines)
- **S3 Availability:** 99.99% SLA
- **CloudFront Availability:** 99.9% SLA
- **Multi-Region:** CloudFront automatically serves from nearest edge
- **Failover:** Not required (S3 handles redundancy automatically)

**6. Performance Monitoring and Auto-Adjustment**

- **CloudWatch Metrics:** Track request count, error rates, latency
- **CloudFront Metrics:** Monitor cache hit ratio (target >85%)
- **Real User Monitoring:** Measure actual user load times
- **Auto-Optimization:** CloudFront automatically routes to fastest edge

**No manual scaling actions required** - the architecture scales automatically.

---

## 10. Monitoring & Observability

<!-- AI: Logging, metrics, tracing, alerting strategy -->

### Monitoring Strategy

**Monitoring Goals:**
1. Ensure website availability and performance
2. Track user behavior and engagement
3. Detect errors and performance degradation
4. Monitor costs and resource usage

### 1. Infrastructure Monitoring

**AWS CloudWatch**

**S3 Metrics:**
- Bucket size and object count
- Request count (GET, PUT, DELETE)
- 4xx and 5xx error rates
- First-byte latency

**CloudFront Metrics:**
- Total requests and data transfer
- Cache hit rate (target: >85%)
- Error rate by status code (4xx, 5xx)
- Origin latency
- Requests by geography

**Alarms:**
- Alert if 5xx error rate exceeds 1%
- Alert if cache hit rate drops below 80%
- Alert if origin latency exceeds 500ms
- Budget alerts for cost overruns

### 2. Application Performance Monitoring

**Client-Side Performance Metrics:**

**Core Web Vitals (measured via browser):**
- **LCP (Largest Contentful Paint):** Target <2.5s
- **FID (First Input Delay):** Target <100ms
- **CLS (Cumulative Layout Shift):** Target <0.1

**Custom Performance Metrics:**
- Time to Interactive (TTI)
- First Contentful Paint (FCP)
- JavaScript bundle load time
- Joke data load time

**Tools:**
- **Lighthouse CI:** Run automated performance audits in CI/CD
- **Google PageSpeed Insights:** Manual performance testing
- **WebPageTest:** Detailed waterfall analysis

### 3. Error Tracking

**Client-Side Error Monitoring:**

**Sentry (Recommended) or Similar:**
- Capture JavaScript errors and unhandled promise rejections
- Track error frequency and affected users
- Provide stack traces and breadcrumbs
- Integrate with React error boundaries

**Custom Error Logging:**
- Log errors to browser console
- Track error events in analytics
- Report critical errors via CloudWatch (if using Lambda@Edge)

**Error Categories to Monitor:**
- JSON parsing errors (malformed joke data)
- Routing errors (404s, invalid routes)
- Network errors (failed asset loads)
- React rendering errors

### 4. User Analytics

**Google Analytics 4 or Plausible:**

**Page Views:**
- Track all route changes (SPA routing events)
- Monitor most visited jokes and categories
- Measure session duration and bounce rate

**User Interactions:**
- Click events: next/previous buttons, category filters
- Share button usage
- External link clicks

**User Segmentation:**
- Device type (mobile, tablet, desktop)
- Browser and OS
- Geographic location
- New vs returning visitors

**Privacy Considerations:**
- Anonymize IP addresses
- No personally identifiable information (PII) collected
- Comply with GDPR/CCPA by providing opt-out

### 5. Logging

**S3 Access Logs:**
- Enable S3 server access logging to separate bucket
- Log all requests (timestamp, IP, user-agent, status code)
- Use for security auditing and traffic analysis

**CloudFront Access Logs:**
- Enable standard logging or real-time logs (Kinesis)
- Contains detailed request/response data
- Use for debugging and analytics

**Log Retention:**
- Retain logs for 90 days minimum
- Archive to S3 Glacier for long-term storage

### 6. Alerting Strategy

**Critical Alerts (Immediate Response):**
- Website down (5xx error rate >5% for 5 minutes)
- CloudFront distribution disabled
- SSL certificate expiration within 7 days

**Warning Alerts (Review Within 24 Hours):**
- Cache hit rate below 80% for 1 hour
- 4xx error rate above 10%
- Performance degradation (LCP >4s for 50% of users)

**Informational Alerts:**
- Monthly cost exceeds budget threshold
- New version deployed successfully
- Weekly performance report

**Alert Channels:**
- Email for critical alerts
- Slack/Teams integration for warnings
- Dashboard for informational metrics

### 7. Dashboards

**CloudWatch Dashboard:**
- S3 and CloudFront metrics overview
- Request volume and error rates
- Performance trends over time

**Grafana or Custom Dashboard (Optional):**
- Combine CloudWatch, Sentry, and GA data
- Real-time user activity visualization
- Cost tracking and forecasting

### 8. Health Checks

**Route 53 Health Checks (If Using):**
- Monitor website availability from multiple regions
- Check HTTP 200 response on root URL
- Failover to backup (not needed for S3, but useful for custom domains)

**Synthetic Monitoring:**
- Run automated Lighthouse audits daily
- Test critical user flows (view joke, navigate categories)
- Alert on performance regressions

---

## 11. Architectural Decisions (ADRs)

<!-- AI: Key architectural decisions with rationale -->

### ADR-001: Static SPA with Client-Side Rendering

**Status:** Accepted

**Context:**
The PRD explicitly requires a static website hosted on S3 with no backend servers or databases.

**Decision:**
Build a React-based single-page application (SPA) that runs entirely in the browser with all joke data bundled as static JSON.

**Rationale:**
- Meets PRD requirement for S3 static hosting
- No infrastructure costs beyond storage and bandwidth
- Simplest deployment model (just upload files)
- Infinite scalability via CDN
- Fast development with React ecosystem

**Consequences:**
- All jokes must be known at build time (no dynamic content)
- Initial bundle size includes all joke data
- SEO may be limited without server-side rendering (acceptable for joke site)
- Cannot add user-generated content without backend

**Alternatives Considered:**
- Server-side rendering (SSR): Rejected - requires servers
- Static site generator (SSG): Possible but unnecessary complexity for SPA use case

---

### ADR-002: Vite as Build Tool

**Status:** Accepted

**Context:**
Need a modern build tool for React development with fast builds and optimized production output.

**Decision:**
Use Vite as the primary build tool and development server.

**Rationale:**
- Extremely fast HMR (Hot Module Replacement) during development
- Optimized production builds with Rollup
- Built-in code splitting and tree shaking
- Smaller and faster than Create React App
- Modern ESM-based approach

**Consequences:**
- Learning curve for developers familiar with Webpack
- Smaller community than CRA but growing rapidly
- Excellent build performance and DX

**Alternatives Considered:**
- Create React App: More mature but slower builds
- Webpack custom config: Too much configuration overhead
- Parcel: Less ecosystem support for React

---

### ADR-003: Client-Side Routing with React Router

**Status:** Accepted

**Context:**
Need to support multiple views (home, categories, individual jokes) with shareable URLs.

**Decision:**
Use React Router v6 with BrowserRouter for client-side routing.

**Rationale:**
- Standard solution for React SPAs
- Supports clean URLs (no hash routing)
- Enables deep linking to specific jokes
- Works with S3 static hosting via error document redirect

**Consequences:**
- Requires S3 error document configuration (all errors redirect to index.html)
- Client-side routing can cause 404s if not configured properly
- SEO requires proper meta tags for each route

**Alternatives Considered:**
- Hash routing (#/jokes/123): Works without configuration but ugly URLs
- No routing: Single page only - doesn't meet requirements

---

### ADR-004: Jokes Stored in Static JSON

**Status:** Accepted

**Context:**
Need to store joke data without a database, accessible to the frontend.

**Decision:**
Store all jokes in a JSON file (jokes.json) bundled with the application or loaded as a static asset.

**Rationale:**
- Simplest approach for static hosting
- No API calls or network requests needed (or lazy load if needed)
- Enables offline-first architecture
- Easy to update (just modify JSON and redeploy)
- Supports up to ~10,000 jokes in single file (<1MB)

**Consequences:**
- Adding new jokes requires rebuild and redeployment
- All users download entire joke dataset (can optimize with lazy loading)
- No real-time updates
- Version control tracks joke changes

**Alternatives Considered:**
- External API: Requires backend infrastructure (out of scope)
- Multiple JSON files: Adds complexity, defer until needed
- IndexedDB: Unnecessary for initial version

---

### ADR-005: CloudFront CDN for Global Distribution

**Status:** Accepted

**Context:**
Users may access the website from anywhere in the world, and performance requirements demand <2s load times.

**Decision:**
Use AWS CloudFront CDN in front of S3 bucket for content delivery.

**Rationale:**
- Dramatically improves load times for global users
- Reduces S3 egress costs
- Provides SSL/TLS termination
- Enables cache optimization strategies
- Improves availability and DDoS protection

**Consequences:**
- Additional cost (~$0.085/GB, cheaper than S3 egress)
- Cache invalidation required on deployments
- Additional configuration complexity
- Slightly more complex debugging

**Alternatives Considered:**
- Direct S3 hosting: Slower for global users, higher egress costs
- Third-party CDN (Cloudflare, Fastly): Increases vendor dependencies

---

### ADR-006: No Backend or Database

**Status:** Accepted

**Context:**
PRD explicitly states "no need for a database or servers - just build the react frontend."

**Decision:**
Build a 100% frontend application with no backend services or database.

**Rationale:**
- Meets explicit PRD requirement
- Minimizes infrastructure costs and complexity
- Eliminates server maintenance and scaling concerns
- Fastest development path
- Sufficient for read-only joke website

**Consequences:**
- Cannot support user accounts, comments, or voting
- Cannot add new jokes without redeployment
- No analytics backend (use third-party like GA)
- Cannot track individual user preferences persistently across devices

**Alternatives Considered:**
- Lightweight backend (Lambda + DynamoDB): Out of scope per PRD
- Firebase/Supabase: Adds external dependency and cost

---

### ADR-007: Responsive Design with CSS (No UI Framework)

**Status:** Accepted

**Context:**
Application must work on devices from 320px to 1920px width.

**Decision:**
Implement responsive design using plain CSS (or CSS Modules) with media queries, without a heavy UI framework.

**Rationale:**
- Maximum control over styling and performance
- Smaller bundle size (no framework overhead)
- Custom design tailored to joke display use case
- Modern CSS features (Grid, Flexbox) are sufficient

**Consequences:**
- More manual styling work compared to component libraries
- Need to ensure cross-browser compatibility
- Requires design skills or simple, clean aesthetic

**Alternatives Considered:**
- Material-UI, Ant Design: Too heavy for simple joke site
- Tailwind CSS: Possible but adds build complexity
- Bootstrap: Outdated approach, large bundle size

---

### ADR-008: Lighthouse Performance as Quality Gate

**Status:** Accepted

**Context:**
PRD requires Lighthouse score of 90+ and <2s load times.

**Decision:**
Integrate Lighthouse CI into build pipeline as a quality gate; fail builds if score drops below 90.

**Rationale:**
- Enforces performance requirements automatically
- Prevents performance regressions
- Provides objective metrics
- Standard industry benchmark

**Consequences:**
- Failed builds if performance degrades
- Requires performance budget discipline
- May need to optimize aggressively to maintain scores

**Alternatives Considered:**
- Manual testing: Not scalable or reliable
- Custom performance metrics: Reinventing the wheel

---

### ADR-009: Minimal Analytics with Privacy Focus

**Status:** Accepted

**Context:**
Need to track success metrics (load time, navigation, user engagement) but respect user privacy.

**Decision:**
Use privacy-focused analytics (Plausible or GA4 with minimal tracking) with IP anonymization and no PII collection.

**Rationale:**
- Balances data needs with user privacy
- Complies with GDPR/CCPA without complex consent flows
- Sufficient for tracking success metrics
- Lightweight impact on performance

**Consequences:**
- Limited user-level tracking
- Cannot track individual user journeys
- Acceptable trade-off for public joke website

**Alternatives Considered:**
- Google Analytics (full tracking): Privacy concerns
- No analytics: Cannot measure success metrics
- Self-hosted analytics: Additional infrastructure overhead

---

### ADR-010: GitHub Actions for CI/CD

**Status:** Accepted

**Context:**
Need automated build and deployment pipeline.

**Decision:**
Use GitHub Actions for CI/CD with automated deployments to S3 on push to main branch.

**Rationale:**
- Native integration with GitHub repository
- Free for public repositories, affordable for private
- Easy to configure and maintain
- Supports testing, building, and AWS deployments
- Secrets management built-in

**Consequences:**
- Tied to GitHub as code hosting platform
- Requires AWS credentials stored in GitHub Secrets
- Build minutes count toward GitHub quota

**Alternatives Considered:**
- AWS CodePipeline: More complex setup
- CircleCI/Travis CI: Additional vendor dependency
- Manual deployment: Not scalable or reliable

---

## Appendix: PRD Reference

# Product Requirements Document: Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

**Created:** 2026-02-03T08:25:23Z
**Status:** Draft

## 1. Overview

**Concept:** Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

**Description:** Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

---

## 2. Goals

- Create a static React-based website that displays jokes to users without requiring backend infrastructure
- Deploy the application to S3 static hosting with appropriate configuration for single-page application routing
- Provide an engaging, responsive user interface that works across desktop and mobile devices
- Implement joke browsing and viewing functionality using client-side data management
- Ensure fast load times and smooth user experience through optimized static asset delivery

---

## 3. Non-Goals

- Building any backend API or server infrastructure
- Implementing user authentication or user accounts
- Creating a database or persistent storage solution
- Developing joke submission or user-generated content features
- Implementing real-time features or WebSocket connections
- Supporting server-side rendering or dynamic content generation

---

## 4. User Stories

- As a visitor, I want to see jokes immediately when I load the website so that I can be entertained without delay
- As a mobile user, I want the website to display properly on my phone so that I can read jokes on the go
- As a user, I want to browse through different jokes so that I can find ones that make me laugh
- As a user, I want to navigate between different categories or types of jokes so that I can find content that matches my sense of humor
- As a user, I want the website to load quickly so that I don't lose interest while waiting
- As a visitor, I want a clean and simple interface so that I can focus on the jokes without distractions
- As a user, I want to share jokes with friends so that I can spread the humor
- As a returning visitor, I want the website to be consistently available so that I can access it whenever I want entertainment

---

## 5. Acceptance Criteria

**Joke Display**
- Given I am a visitor
- When I load the website
- Then I should see at least one joke displayed on the screen within 2 seconds

**Navigation**
- Given I am viewing a joke
- When I click the next/previous button
- Then I should see a different joke displayed
- And the transition should be smooth without page reload

**Responsive Design**
- Given I am accessing the website from any device
- When I view the website on screens from 320px to 1920px width
- Then the layout should adapt appropriately and remain readable

**Category Browsing**
- Given I want to find specific types of jokes
- When I select a category filter
- Then I should see only jokes from that category
- And the URL should update to reflect the current filter

**Static Hosting Compatibility**
- Given the application is deployed to S3
- When I navigate to any route directly via URL
- Then the application should load correctly without 404 errors

---

## 6. Functional Requirements

- **FR-001**: The application must be built using React framework and compile to static HTML, CSS, and JavaScript files
- **FR-002**: Jokes must be stored in JSON format within the application bundle or loaded from a static JSON file
- **FR-003**: The website must display jokes with readable typography and appropriate spacing
- **FR-004**: Users must be able to navigate between different jokes using next/previous controls
- **FR-005**: The application must support client-side routing for different views (e.g., home, categories, individual jokes)
- **FR-006**: Jokes must be organized into categories (e.g., puns, one-liners, dad jokes, knock-knock jokes)
- **FR-007**: Users must be able to filter or browse jokes by category
- **FR-008**: The application must include a home/landing page that introduces the site
- **FR-009**: Each joke must be displayable on its own route/URL for sharing purposes
- **FR-010**: The application must implement a responsive layout that works on mobile, tablet, and desktop devices
- **FR-011**: The build output must be optimized for S3 static hosting with appropriate file structure

---

## 7. Non-Functional Requirements

### Performance
- Initial page load time must be under 2 seconds on 3G connections
- JavaScript bundle size must not exceed 500KB (gzipped)
- Images and assets must be optimized and lazy-loaded where appropriate
- The application must achieve a Lighthouse performance score of 90 or above

### Security
- All assets must be served over HTTPS when deployed
- The application must not contain any hardcoded secrets or sensitive information
- Content Security Policy headers should be configured appropriately in S3
- Dependencies must be kept up to date to avoid known vulnerabilities

### Scalability
- Static files must be configured with appropriate cache headers for CDN compatibility
- The architecture must support serving thousands of concurrent users without degradation
- Joke data structure must allow for easy addition of new jokes without code changes

### Reliability
- The application must handle missing or malformed joke data gracefully
- Client-side routing must include fallback handling for unmatched routes
- The application must work consistently across modern browsers (Chrome, Firefox, Safari, Edge)
- S3 bucket must be configured for 99.9% uptime availability

---

## 8. Dependencies

- **React** (v18+): Core framework for building the user interface
- **React Router**: Client-side routing for single-page application navigation
- **Build Tool**: Vite or Create React App for bundling and development server
- **AWS S3**: Static hosting platform for deployment
- **CloudFront (optional)**: CDN for improved global performance
- **Node.js/npm**: Development environment and package management
- **Joke Dataset**: Pre-existing joke collection in JSON format or will be manually curated

---

## 9. Out of Scope

- Backend API development or server-side logic
- Database design or implementation
- User authentication, registration, or login functionality
- User-generated content submission or moderation
- Comment systems or social features
- Admin panels or content management systems
- Real-time updates or live data synchronization
- Email notifications or any communication features
- Analytics beyond basic static website tracking
- Payment or monetization features
- Internationalization or multi-language support
- Accessibility features beyond basic WCAG compliance
- Advanced search functionality with filters and sorting

---

## 10. Success Metrics

- **Deployment Success**: Application successfully builds and deploys to S3 without errors
- **Load Time**: 95% of page loads complete within 2 seconds
- **Browser Compatibility**: Website functions correctly on 95%+ of modern browser versions
- **Mobile Responsiveness**: Layout renders correctly on devices from 320px to 1920px width
- **Joke Accessibility**: Users can access and view at least 50 different jokes
- **Navigation Success Rate**: 99% of navigation actions result in expected view changes
- **Build Size**: Total bundle size remains under 500KB gzipped
- **Zero Critical Errors**: No console errors or broken functionality in production

---

## Appendix: Clarification Q&A

### Clarification Questions & Answers
