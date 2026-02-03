# High-Level Design: aiworkshop

**Created:** 2026-02-03T13:18:00Z
**Status:** Draft

## 1. Architecture Overview

<!-- AI: Describe the overall system architecture (microservices, monolith, serverless, etc.) -->

The system follows a **Static Site Architecture** (also known as Jamstack architecture) with a client-side Single Page Application (SPA) approach. The entire application is built as a static React application that runs entirely in the user's browser, with no backend server infrastructure.

**Key Architectural Characteristics:**
- **Fully Static:** All HTML, CSS, and JavaScript are pre-built and served as static files from AWS S3
- **Client-Side Only:** All business logic, data processing, search, filtering, and recommendations run in the browser
- **API-First Data Sourcing:** Book catalog data is sourced from third-party APIs (Google Books API or Open Library API) during build time or on-demand client-side
- **Local Storage Persistence:** User-generated data (reviews, ratings, reading lists) is stored in browser local storage
- **CDN-Accelerated Delivery:** CloudFront CDN distributes static assets globally for optimal performance
- **Serverless Compute:** No traditional servers; all compute happens client-side in the browser

**Architecture Benefits:**
- Minimal infrastructure costs (only S3 storage and CloudFront CDN)
- Infinite horizontal scalability (static files can serve unlimited concurrent users)
- High reliability (leveraging S3's 99.99% durability)
- Fast global performance through CDN edge locations
- Zero server maintenance overhead

---

## 2. System Components

<!-- AI: List major components/services with brief descriptions -->

### Core Frontend Components

**1. Book Catalog Service**
- Manages the book catalog data structure
- Handles book retrieval, indexing for search, and filtering logic
- Provides book detail views with metadata (title, author, synopsis, cover, etc.)
- Implements pagination for large catalog browsing

**2. Search & Filter Engine**
- Client-side full-text search using Lunr.js or similar inverted index library
- Multi-criteria filtering (genre, rating, publication year, author)
- Real-time search with debouncing for performance
- Search result ranking and relevance scoring

**3. Review & Rating Manager**
- User review submission and validation
- Star rating input (1-5 scale)
- Review text sanitization to prevent XSS
- Average rating calculation and aggregation
- Review display with user attribution and timestamps

**4. Reading List Manager**
- CRUD operations for user-created reading lists
- Book addition/removal from lists
- List categorization (To Read, Currently Reading, Favorites, custom)
- Export functionality (JSON/CSV format)
- Reading progress tracking

**5. Recommendation Engine**
- Collaborative filtering algorithm (user-based similarity)
- Content-based filtering (genre, author preferences)
- Hybrid recommendation approach combining both methods
- Minimum threshold enforcement (5 rated books)
- Dynamic adaptation based on user interactions

**6. Author Profile Service**
- Author detail page rendering
- Bibliography aggregation from catalog
- Author metadata display (bio, photo, social links)
- Book grouping by author

**7. User Preference Manager**
- Manages user settings and preferences
- Genre preference tracking
- Reading history maintenance
- Local storage synchronization
- Data export/import functionality

**8. State Management Layer**
- Centralized application state (Redux or Zustand)
- State persistence to local storage
- State hydration on application load
- Action dispatchers for state mutations

**9. UI Component Library**
- Reusable React components (buttons, cards, modals, forms)
- Responsive layout components
- Loading states and skeletons
- Error boundaries and fallback UI

**10. Data Hydration Service**
- Fetches book catalog data from third-party APIs at build time
- Generates static JSON data files for client consumption
- Handles API rate limiting and caching during build
- Fallback data loading strategies

---

## 3. Data Model

<!-- AI: High-level data entities and relationships -->

### Core Entities

**Book**
```
{
  id: string (ISBN or API-provided unique ID)
  title: string
  author: string[]
  authorId: string[]
  genre: string[]
  publicationDate: date
  synopsis: string
  coverImageUrl: string
  pageCount: number
  publisher: string
  language: string
  isbn10: string
  isbn13: string
  averageRating: number (calculated)
  reviewCount: number (calculated)
}
```

**Author**
```
{
  id: string
  name: string
  biography: string
  photoUrl: string
  birthDate: date
  nationality: string
  website: string
  books: string[] (array of book IDs)
}
```

**Review** (stored in local storage)
```
{
  id: string (UUID)
  bookId: string
  userId: string (anonymous UUID stored locally)
  rating: number (1-5)
  reviewText: string
  timestamp: date
  helpful: number (future enhancement)
}
```

**ReadingList** (stored in local storage)
```
{
  id: string (UUID)
  name: string
  description: string
  bookIds: string[]
  createdAt: date
  updatedAt: date
  isPublic: boolean
}
```

**UserProfile** (stored in local storage)
```
{
  userId: string (anonymous UUID)
  preferences: {
    favoriteGenres: string[]
    readingGoal: number
  }
  readingHistory: string[] (book IDs)
  reviews: string[] (review IDs)
  readingLists: string[] (list IDs)
  ratings: Map<bookId, rating>
}
```

**SearchIndex** (generated at build time)
```
{
  index: Lunr.Index (serialized)
  documentStore: {
    bookId: {
      title, author, genre, synopsis (tokenized)
    }
  }
}
```

### Data Relationships

- **Book → Author:** Many-to-Many (books can have multiple authors, authors write multiple books)
- **Book → Review:** One-to-Many (each book has multiple reviews)
- **User → Review:** One-to-Many (user can write multiple reviews)
- **User → ReadingList:** One-to-Many (user has multiple lists)
- **ReadingList → Book:** Many-to-Many (lists contain multiple books, books can be in multiple lists)

### Data Storage Strategy

**Static JSON Files (deployed to S3):**
- `books.json` - Complete book catalog (paginated into chunks for large catalogs)
- `authors.json` - Author profiles and metadata
- `search-index.json` - Pre-built Lunr.js search index
- `featured-books.json` - Curated lists for homepage

**Local Storage (browser-side):**
- `userProfile` - User preferences and metadata
- `reviews` - All user-submitted reviews
- `readingLists` - User's reading lists
- `ratings` - User's book ratings

---

## 4. API Contracts

<!-- AI: Define key API endpoints, request/response formats -->

### External Third-Party API Integration

**Google Books API v1**

```
GET https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40
Response:
{
  "items": [
    {
      "id": "string",
      "volumeInfo": {
        "title": "string",
        "authors": ["string"],
        "publishedDate": "string",
        "description": "string",
        "imageLinks": {
          "thumbnail": "string"
        },
        "industryIdentifiers": [...]
      }
    }
  ]
}
```

### Internal Client-Side API (Service Layer)

**BookService**

```javascript
// Get all books with pagination
getBooks(page: number, limit: number): Promise<Book[]>

// Get single book details
getBookById(id: string): Promise<Book>

// Search books
searchBooks(query: string, filters?: FilterOptions): Promise<Book[]>

// Get books by author
getBooksByAuthor(authorId: string): Promise<Book[]>

// Get featured/trending books
getFeaturedBooks(): Promise<Book[]>
```

**ReviewService**

```javascript
// Submit a review
createReview(bookId: string, rating: number, reviewText: string): Promise<Review>

// Get reviews for a book
getReviewsByBook(bookId: string): Promise<Review[]>

// Get user's reviews
getUserReviews(userId: string): Promise<Review[]>

// Update a review
updateReview(reviewId: string, updates: Partial<Review>): Promise<Review>

// Delete a review
deleteReview(reviewId: string): Promise<void>
```

**ReadingListService**

```javascript
// Create reading list
createReadingList(name: string, description?: string): Promise<ReadingList>

// Get all user lists
getReadingLists(): Promise<ReadingList[]>

// Add book to list
addBookToList(listId: string, bookId: string): Promise<void>

// Remove book from list
removeBookFromList(listId: string, bookId: string): Promise<void>

// Delete reading list
deleteReadingList(listId: string): Promise<void>

// Export list
exportReadingList(listId: string, format: 'json' | 'csv'): Promise<Blob>
```

**RecommendationService**

```javascript
// Get personalized recommendations
getRecommendations(userId: string, count?: number): Promise<Book[]>

// Refresh recommendations based on new interactions
refreshRecommendations(userId: string): Promise<Book[]>
```

**SearchService**

```javascript
// Full-text search with filters
search(query: string, filters?: {
  genre?: string[],
  rating?: [number, number],
  publicationYear?: [number, number],
  author?: string
}): Promise<SearchResult[]>

// Get search suggestions
getSuggestions(query: string): Promise<string[]>
```

**StorageService**

```javascript
// Generic local storage operations
set(key: string, value: any): void
get(key: string): any
remove(key: string): void
clear(): void
getStorageUsage(): { used: number, quota: number }
```

---

## 5. Technology Stack

### Backend
**N/A - No Backend**

This is a fully static site with no traditional backend infrastructure. All data processing and business logic occurs client-side.

**Build-Time Data Processing:**
- Node.js scripts for fetching and processing book data from APIs during build
- Data transformation scripts to generate static JSON files
- Search index generation using Lunr.js

### Frontend
**Core Framework:**
- React 18.2+ (UI library)
- React Router v6 (client-side routing)
- TypeScript 5+ (type safety)

**State Management:**
- Redux Toolkit 2.0+ or Zustand 4+ (application state)
- React Query / TanStack Query (data fetching and caching)
- Context API (theme, locale, user preferences)

**UI Components & Styling:**
- Material-UI (MUI) v5 or Ant Design v5 (component library)
- Emotion or Styled Components (CSS-in-JS)
- Tailwind CSS (utility-first styling, optional)
- Responsive design with CSS Grid and Flexbox

**Search & Data Processing:**
- Lunr.js 2.3+ (client-side full-text search)
- Fuse.js (fuzzy search alternative)
- date-fns (date manipulation)
- lodash-es (utility functions)

**Forms & Validation:**
- React Hook Form (form management)
- Zod or Yup (schema validation)

**Data Visualization:**
- Recharts or Chart.js (rating distributions, reading stats)

**Performance Optimization:**
- React.lazy() and Suspense (code splitting)
- React Window or Virtuoso (list virtualization)
- Intersection Observer API (lazy loading images)

### Infrastructure
**Hosting & CDN:**
- AWS S3 (static site hosting)
- AWS CloudFront (CDN for global distribution)
- Route 53 (DNS management)

**CI/CD:**
- GitHub Actions (build and deployment pipeline)
- AWS CLI (S3 sync and CloudFront invalidation)

**Build Tools:**
- Vite 5+ (fast build tool and dev server)
- ESBuild (JavaScript bundler)
- PostCSS (CSS processing)
- Terser (JavaScript minification)
- ImageOptim or Sharp (image optimization)

**Development Tools:**
- ESLint + Prettier (code quality)
- Husky + lint-staged (pre-commit hooks)
- Jest + React Testing Library (unit testing)
- Playwright or Cypress (E2E testing)

### Data Storage
**Client-Side Storage:**
- Local Storage API (user data persistence up to 5-10MB)
- IndexedDB (fallback for larger datasets, if needed)

**Static Data Files:**
- JSON files hosted on S3
- Pre-generated search indexes
- Compressed book catalog data

**Caching Strategy:**
- Service Workers (offline caching via Workbox)
- HTTP caching headers on S3/CloudFront
- Browser cache for static assets (images, fonts)

---

## 6. Integration Points

<!-- AI: External systems, APIs, webhooks -->

### Third-Party APIs

**1. Google Books API**
- **Purpose:** Source book metadata, cover images, author information
- **Usage:** Build-time data fetching and optional client-side on-demand lookups
- **Rate Limits:** 1,000 requests/day (free tier), 10 requests/second
- **Endpoint:** `https://www.googleapis.com/books/v1/volumes`
- **Authentication:** API key (stored in build environment)
- **Data Fields Used:** title, authors, publishedDate, description, imageLinks, industryIdentifiers, categories

**2. Open Library API (Alternative/Fallback)**
- **Purpose:** Backup data source for book metadata
- **Usage:** Supplement Google Books data or serve as fallback
- **Rate Limits:** No official limit, but throttled
- **Endpoint:** `https://openlibrary.org/api/books`
- **Authentication:** None required
- **Data Fields Used:** title, authors, publish_date, description, cover URLs

**3. Covers CDN**
- **Purpose:** High-quality book cover images
- **Options:** 
  - Open Library Covers: `https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg`
  - Google Books covers from API responses
- **Fallback:** Default placeholder image for missing covers

### Build-Time Integration

**Data Pipeline Script (Node.js):**
```
fetch-books.js → Transform data → Generate JSON files → Upload to S3
```

**Process:**
1. Fetch book data from Google Books API (paginated requests)
2. Transform and normalize data structure
3. Fetch author metadata and link to books
4. Generate search index using Lunr.js
5. Create featured/curated book lists
6. Output static JSON files to `/public/data` directory
7. Deploy to S3 during build

### Client-Side Integration

**Static Data Loading:**
- Fetch JSON files from S3/CloudFront on application load
- Use React Query for caching and background updates
- Implement progressive loading for large catalogs

**No External Webhooks:**
- No real-time integrations required (static site)
- No server-side event processing

### Analytics & Monitoring Integration

**Google Analytics 4:**
- Track page views, user interactions, search queries
- Custom events for book views, reviews submitted, lists created
- Performance metrics (Core Web Vitals)

**Sentry (Optional):**
- Client-side error tracking
- Performance monitoring
- User session replay for debugging

---

## 7. Security Architecture

<!-- AI: Authentication, authorization, encryption, secrets management -->

### Authentication & Authorization

**No Traditional Authentication:**
- No user accounts, passwords, or login system
- Anonymous user identification via locally-generated UUID
- User data tied to browser local storage (device-specific)

**Future Enhancement Path:**
- Could add optional OAuth (Google, GitHub) for cross-device sync
- User data export/import for manual device migration

### Data Security

**Client-Side Data Protection:**
- All user data (reviews, lists) stored exclusively in browser local storage
- No transmission of user data to external servers
- Data remains within user's control on their device

**Input Sanitization:**
- DOMPurify library for sanitizing user-generated content (reviews, list names)
- Prevents XSS attacks through malicious review text
- Strict validation of rating inputs (1-5 range enforcement)

**Content Security Policy (CSP):**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' https://covers.openlibrary.org https://books.google.com data:;
  font-src 'self' data:;
  connect-src 'self' https://www.googleapis.com https://openlibrary.org;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

**HTTPS Enforcement:**
- All resources loaded over HTTPS only
- S3 bucket configured for HTTPS-only access
- CloudFront configured with TLS 1.2+ minimum
- HTTP Strict Transport Security (HSTS) header enabled

### Infrastructure Security

**S3 Bucket Security:**
- Public read access for static files only
- Write access restricted to CI/CD IAM role
- Bucket versioning enabled for rollback capability
- Server-side encryption at rest (S3-SSE)
- CORS policy restricts access to authorized domains

**CORS Configuration:**
```json
{
  "AllowedOrigins": ["https://bookreviews.example.com"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "MaxAgeSeconds": 3600
}
```

**CloudFront Security:**
- Origin Access Identity (OAI) for S3 access
- Custom SSL certificate (ACM)
- Geo-restriction (optional)
- AWS WAF integration (optional for DDoS protection)
- Signed URLs for sensitive content (not required for this use case)

### Secrets Management

**Build-Time Secrets:**
- Google Books API key stored in GitHub Secrets
- Accessed via environment variables during CI/CD
- Never committed to source code
- Rotated periodically

**No Runtime Secrets:**
- Application has no sensitive credentials at runtime
- API keys not exposed in client-side code
- Book data is public information

### Data Privacy

**GDPR Compliance:**
- No personal data collected server-side
- User data stored locally gives user full control
- Clear privacy policy explaining local storage usage
- Data export functionality for data portability
- Data deletion via browser clear storage

**Local Storage Limitations:**
- 5-10MB storage limit per domain
- User notified when approaching quota
- Graceful degradation if storage unavailable

---

## 8. Deployment Architecture

<!-- AI: How components are deployed (K8s, containers, serverless) -->

### Deployment Model: Static Site with CDN

**Infrastructure Components:**

1. **AWS S3 Bucket (Origin Server)**
   - Static website hosting enabled
   - Bucket name: `book-reviews-app`
   - Index document: `index.html`
   - Error document: `index.html` (for SPA routing)
   - All compiled assets (HTML, JS, CSS, images, JSON data)

2. **AWS CloudFront CDN (Distribution Layer)**
   - Global edge locations (200+ locations)
   - Origin: S3 bucket
   - Default root object: `index.html`
   - Custom error responses (redirect 404 to index.html)
   - Cache behaviors optimized per content type
   - Compression enabled (Gzip/Brotli)

3. **AWS Route 53 (DNS)**
   - Domain management
   - Alias record pointing to CloudFront distribution
   - Health checks and failover (optional)

### Deployment Pipeline

**CI/CD Flow (GitHub Actions):**

```
Developer Push → GitHub → GitHub Actions → Build → Test → Deploy → Invalidate
```

**Pipeline Steps:**

1. **Trigger:** Push to `main` branch or manual workflow dispatch
2. **Build Environment Setup:**
   - Checkout repository
   - Install Node.js 20.x
   - Install dependencies (`npm ci`)
3. **Data Fetching (Build-Time):**
   - Run `npm run fetch-books` script
   - Fetch book data from Google Books API
   - Generate search indexes
   - Create static JSON files
4. **Application Build:**
   - Run `npm run build` (Vite production build)
   - TypeScript compilation
   - Code minification and tree-shaking
   - Asset optimization (images, fonts)
   - Generate source maps
5. **Testing:**
   - Run unit tests (`npm run test`)
   - Run E2E tests (`npm run test:e2e`)
   - Lighthouse CI performance audit
6. **Deployment:**
   - AWS CLI S3 sync (`aws s3 sync ./dist s3://book-reviews-app --delete`)
   - Set cache-control headers per file type
   - Verify upload success
7. **Cache Invalidation:**
   - Create CloudFront invalidation (`aws cloudfront create-invalidation`)
   - Invalidate paths: `/*` or specific changed files
8. **Verification:**
   - Smoke tests against production URL
   - Health check endpoint verification
   - Rollback on failure

**GitHub Actions Workflow Example:**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run fetch-books
        env:
          GOOGLE_BOOKS_API_KEY: ${{ secrets.GOOGLE_BOOKS_API_KEY }}
      - run: npm run build
      - run: npm test
      - run: aws s3 sync ./dist s3://book-reviews-app --delete
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      - run: aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
```

### Environment Configuration

**Environments:**
- **Development:** Local dev server (Vite)
- **Staging:** Separate S3 bucket + CloudFront (optional)
- **Production:** Primary S3 bucket + CloudFront

**Environment Variables:**
- `VITE_API_BASE_URL` - Base URL for data files
- `VITE_GOOGLE_BOOKS_API_KEY` - API key for build-time fetching
- `VITE_GA_TRACKING_ID` - Google Analytics tracking ID
- `VITE_SENTRY_DSN` - Sentry error tracking DSN

### Rollback Strategy

**Version Control:**
- S3 bucket versioning enabled
- Each deployment tagged with git commit SHA
- CloudFront serves from specific S3 version

**Rollback Process:**
1. Identify last known good deployment (git tag)
2. Re-run deployment pipeline from that commit
3. Or manually restore S3 bucket objects from previous version
4. Create CloudFront invalidation

**Automated Rollback:**
- Monitor error rates via Sentry
- Automated rollback if error rate exceeds threshold (future enhancement)

### Blue-Green Deployment (Optional)

**For zero-downtime updates:**
- Two S3 buckets (blue and green)
- CloudFront origin switching
- Deploy to inactive bucket, test, switch origin
- Instant rollback by switching origin back

---

## 9. Scalability Strategy

<!-- AI: How the system scales (horizontal, vertical, auto-scaling) -->

### Scalability Characteristics

**Inherent Infinite Horizontal Scale:**
- Static sites have no compute bottlenecks
- S3 and CloudFront automatically scale to handle unlimited concurrent users
- No server-side resource contention
- No database connection limits

### Traffic Scaling

**CloudFront CDN Scaling:**
- Automatic distribution across 200+ global edge locations
- Request routing to nearest edge location
- Origin shield to reduce load on S3
- Handles traffic spikes automatically (e.g., viral book trends)
- No manual intervention required

**Expected Traffic Patterns:**
- Steady-state: 1,000-10,000 daily active users
- Peak capacity: 100,000+ concurrent users (no degradation)
- Regional traffic distribution via edge locations

### Data Scaling

**Book Catalog Size:**
- **Current Target:** 5,000-10,000 books
- **Maximum Efficient Size:** 50,000 books without architecture changes

**Scaling Strategies per Data Size:**

**Up to 10,000 books:**
- Single JSON file with all book data (~10-20MB compressed)
- Loaded on initial page load
- In-memory search and filtering

**10,000-50,000 books:**
- Split catalog into paginated chunks (e.g., 1,000 books per file)
- Lazy load book data on-demand
- Keep search index in memory (Lunr.js supports 50K+ documents)
- Use IndexedDB for client-side caching of loaded chunks

**Beyond 50,000 books (future):**
- Introduce backend API for search and filtering
- Transition from static to hybrid architecture
- Maintain static frontend with dynamic data API

### Search Performance Scaling

**Lunr.js Index Optimization:**
- Pre-built serialized index (generated at build time)
- Index loaded once on application start
- In-memory search operations (<100ms for 10K books)
- Incremental index loading for large catalogs

**Search Algorithm Scaling:**
- Debounced search input (300ms delay)
- Result limiting (show first 100 results)
- Pagination for large result sets
- Web Workers for search processing (offload main thread)

### Client-Side Performance Scaling

**Code Splitting:**
- Route-based code splitting (separate bundles per page)
- Lazy loading for recommendation engine
- Dynamic imports for heavy libraries (charts, export)

**Asset Optimization:**
- Image lazy loading (Intersection Observer)
- Responsive images (srcset for different screen sizes)
- WebP format with JPEG fallback
- Thumbnail images for catalog browsing

**Rendering Optimization:**
- List virtualization (React Window) for large catalogs
- Memoization of expensive computations (React.memo)
- Debounced filter updates
- Pagination over infinite scroll

### Storage Scaling

**Local Storage Limitations:**
- 5-10MB per domain (browser-dependent)
- Monitor storage usage and notify users
- Implement data pruning strategies (old reviews archived)
- Offer data export before cleanup

**Mitigation Strategies:**
- IndexedDB fallback for larger datasets (50MB+)
- Compress data before storing (LZ-string)
- Store only essential data (IDs instead of full objects)

### Geographic Scaling

**Multi-Region CDN:**
- CloudFront automatically serves from nearest edge
- Low latency worldwide (<50ms for static assets)
- No regional deployment configuration needed

**Future Multi-Language Support:**
- Separate book catalogs per language
- Locale-based routing in CloudFront
- Minimal overhead (additional JSON files)

### Cost Scaling

**Cost Model:**
- S3 storage: ~$0.023/GB/month (minimal for static files)
- CloudFront data transfer: $0.085-$0.250/GB (first 10TB)
- Requests: $0.0075 per 10,000 HTTPS requests
- **Estimated cost for 10K daily users:** $50-100/month
- **Linear scaling:** Doubling users approximately doubles costs
- No sudden cost spikes (unlike compute-based architectures)

### Monitoring for Scale

**Performance Metrics:**
- Lighthouse CI scores in pipeline
- Real User Monitoring (RUM) via Google Analytics
- CloudFront cache hit ratio (target: >90%)
- S3 request metrics
- Client-side error rates (Sentry)

**Alerting Thresholds:**
- Cache hit ratio drops below 80%
- 5xx error rate exceeds 0.1%
- Average page load time exceeds 3 seconds
- Local storage quota warnings

---

## 10. Monitoring & Observability

<!-- AI: Logging, metrics, tracing, alerting strategy -->

### Client-Side Monitoring

**Google Analytics 4 (GA4):**

**Standard Metrics:**
- Page views and unique visitors
- Session duration and bounce rate
- Device types and screen resolutions
- Geographic distribution
- Traffic sources and referrers

**Custom Events:**
- `search_query` - Track search terms and result counts
- `book_view` - Book detail page visits
- `review_submit` - Review creation events
- `reading_list_create` - List creation
- `book_add_to_list` - Book additions to lists
- `recommendation_click` - Recommendation engagement
- `export_list` - Data export events
- `filter_apply` - Filter usage patterns

**Core Web Vitals:**
- Largest Contentful Paint (LCP) - target: <2.5s
- First Input Delay (FID) - target: <100ms
- Cumulative Layout Shift (CLS) - target: <0.1
- Time to First Byte (TTFB) - target: <600ms

**User Flow Analysis:**
- Funnel analysis (search → book view → review submit)
- Abandoned reading list creation
- Recommendation click-through rates

### Error Tracking & Debugging

**Sentry Integration:**

**Error Monitoring:**
- Unhandled JavaScript exceptions
- Promise rejections
- React component errors (error boundaries)
- Network request failures
- Local storage quota exceeded errors

**Performance Monitoring:**
- Transaction tracing for key user flows
- Component render performance
- API call durations (Google Books)
- Search query performance

**Session Replay:**
- Visual reproduction of user sessions with errors
- User interaction timeline
- Console logs and network activity
- Privacy-sensitive data redaction

**Error Enrichment:**
- User context (anonymous ID, reading lists count)
- Device and browser information
- App version and deployment ID
- Local storage usage statistics

### Infrastructure Monitoring

**AWS CloudWatch:**

**CloudFront Metrics:**
- Requests count
- Bytes downloaded
- Error rate (4xx, 5xx)
- Cache hit ratio
- Origin latency

**S3 Metrics:**
- Bucket size
- Request count (GET, PUT)
- 4xx/5xx errors
- First byte latency

**Alarms:**
- CloudFront 5xx error rate > 1% (5 min window)
- Cache hit ratio < 80% (sustained 15 min)
- S3 4xx errors > 100/min (data access issues)

### Synthetic Monitoring

**Lighthouse CI:**
- Automated performance audits on every deployment
- Performance budget enforcement
- Accessibility checks (WCAG 2.1 AA compliance)
- SEO validation
- Best practices verification

**Fail Deployment If:**
- Performance score < 85 (desktop)
- Performance score < 75 (mobile)
- Accessibility score < 90
- Bundle size increases >20%

**Uptime Monitoring (Pingdom/UptimeRobot):**
- HTTP checks every 5 minutes
- Multi-location availability testing
- Alert on downtime (email, SMS, Slack)
- Status page for users

### Logging Strategy

**Client-Side Logging:**

**Development:**
- Console logging with log levels (debug, info, warn, error)
- Redux DevTools for state inspection
- React DevTools for component profiling

**Production:**
- Minimal console logging (errors only)
- Structured logging to Sentry
- User actions logged to GA4 as events

**No Server-Side Logs:**
- S3 and CloudFront access logs (optional, for forensics)
- Not actively monitored (static site has no runtime logs)

### Dashboards

**Operational Dashboard (CloudWatch):**
- Real-time traffic volume
- Error rates over time
- Cache performance
- Geographic distribution

**User Engagement Dashboard (GA4):**
- Active users (DAU, WAU, MAU)
- Top searched books and authors
- Most reviewed books
- Reading list adoption rate
- Feature usage heatmap

**Performance Dashboard (Grafana/DataDog - Optional):**
- Page load time percentiles (p50, p95, p99)
- Search performance over time
- Client-side error trends
- Browser/device performance comparison

### Alerting Strategy

**Critical Alerts (PagerDuty/Slack):**
- Site down (CloudFront 5xx > 5%)
- Deployment failure
- Sentry error spike (>100 errors/min)

**Warning Alerts (Slack/Email):**
- Performance degradation (Lighthouse score drop >10 points)
- Cache hit ratio decline
- Elevated client-side error rate

**Informational Notifications (Email):**
- Successful deployments
- Weekly performance reports
- Monthly usage statistics

### Continuous Improvement

**A/B Testing (Optional):**
- Test different recommendation algorithms
- UI/UX variations
- Search relevance improvements

**Performance Optimization Cycle:**
1. Monitor Core Web Vitals and Lighthouse scores
2. Identify bottlenecks (large bundles, slow components)
3. Optimize and deploy
4. Validate improvements with RUM data
5. Repeat

**User Feedback Loop:**
- In-app feedback widget
- Error reports with user context
- Feature request tracking

---

## 11. Architectural Decisions (ADRs)

<!-- AI: Key architectural decisions with rationale -->

### ADR-001: Static Site Architecture with No Backend

**Status:** Accepted

**Context:**
The PRD specifies "Static site hosted on S3 (React frontend, no backend database needed)." We need to decide whether to implement a traditional client-server architecture or a fully static site.

**Decision:**
Implement a fully static site (Jamstack architecture) with all business logic client-side and user data stored in browser local storage.

**Rationale:**
- **Cost Efficiency:** Eliminates server infrastructure costs (no EC2, RDS, or Lambda)
- **Infinite Scalability:** Static files can serve unlimited concurrent users via CDN
- **Simplified Operations:** No server maintenance, patching, or scaling concerns
- **Performance:** CDN edge caching provides <50ms response times globally
- **Reliability:** S3 offers 99.99% availability with no operational overhead
- **Alignment with PRD:** Explicitly requested static hosting

**Consequences:**
- **Positive:** Low cost, high performance, simple deployment
- **Negative:** No centralized user data (device-specific), limited cross-device sync
- **Trade-off:** User reviews/lists not shared across browsers/devices (acceptable for MVP)

**Alternatives Considered:**
- Serverless backend (Lambda + DynamoDB): Added complexity and cost
- Traditional backend (Node.js + PostgreSQL): High operational overhead

---

### ADR-002: Client-Side Search with Lunr.js

**Status:** Accepted

**Context:**
Search and filtering must work on up to 50,000 books with <500ms response time per NFRs. We need to decide between client-side and server-side search.

**Decision:**
Implement client-side full-text search using Lunr.js with pre-built indexes generated at build time.

**Rationale:**
- **No Backend:** Aligns with static site architecture (ADR-001)
- **Performance:** In-memory search delivers <100ms results for 10K books
- **Offline Capable:** Works without network after initial load
- **Cost:** Zero ongoing search infrastructure costs
- **User Experience:** Instant results with no network latency

**Consequences:**
- **Positive:** Fast search, no backend complexity, works offline
- **Negative:** Index download overhead (~2-5MB), limited to ~50K books efficiently
- **Limitation:** Cannot implement advanced features like typo tolerance easily

**Alternatives Considered:**
- Algolia/Elasticsearch: Added cost ($1/1000 requests) and external dependency
- Backend search API: Requires backend infrastructure (violates ADR-001)

---

### ADR-003: Local Storage for User Data Persistence

**Status:** Accepted

**Context:**
User reviews, ratings, and reading lists must persist across sessions. We need to choose a storage mechanism.

**Decision:**
Use browser Local Storage API for all user-generated data with IndexedDB as fallback for quota limits.

**Rationale:**
- **No Backend:** Consistent with static architecture (ADR-001)
- **Privacy:** User data never leaves their device
- **Simplicity:** Native browser API, no external dependencies
- **Sufficient Capacity:** 5-10MB handles hundreds of reviews and lists
- **Fast Access:** Synchronous API with instant read/write

**Consequences:**
- **Positive:** Zero backend cost, user data privacy, simple implementation
- **Negative:** Data lost if user clears browser data, no cross-device sync
- **Limitation:** Users must export data to transfer between devices

**Mitigation:**
- Implement data export/import functionality (JSON/CSV)
- Provide clear messaging about data storage location
- Future enhancement: Optional OAuth sync via third-party service

**Alternatives Considered:**
- Backend database: Requires authentication and server infrastructure
- Cloud storage sync: Complex implementation, ongoing costs

---

### ADR-004: React 18 with TypeScript

**Status:** Accepted

**Context:**
Need to select frontend framework and type system for a complex SPA with state management needs.

**Decision:**
Use React 18+ with TypeScript 5+ as the primary frontend framework.

**Rationale:**
- **Ecosystem:** Largest component library ecosystem (MUI, Ant Design)
- **Performance:** React 18 concurrent rendering and automatic batching
- **Type Safety:** TypeScript prevents runtime errors and improves DX
- **Team Familiarity:** Most widely-used frontend framework (easy hiring)
- **Longevity:** Strong backing from Meta and community

**Consequences:**
- **Positive:** Rich ecosystem, strong typing, excellent tooling
- **Negative:** Bundle size larger than alternatives (mitigated by code splitting)
- **Trade-off:** Learning curve for TypeScript (acceptable for improved quality)

**Alternatives Considered:**
- Vue 3: Smaller ecosystem, less team familiarity
- Svelte: Better performance but smaller ecosystem and tooling
- Vanilla JS: No framework overhead but slower development

---

### ADR-005: Vite Build Tool

**Status:** Accepted

**Context:**
Need fast build times and optimized production bundles for a React application.

**Decision:**
Use Vite 5+ as the build tool and development server.

**Rationale:**
- **Development Speed:** Instant server start, <50ms HMR
- **Optimized Builds:** ESBuild produces smaller bundles than Webpack
- **Modern Defaults:** ES modules, tree-shaking, code splitting out-of-box
- **Simple Configuration:** Minimal config compared to Webpack
- **React Support:** First-class React plugin with Fast Refresh

**Consequences:**
- **Positive:** Faster development cycle, smaller bundles, better DX
- **Negative:** Newer tool with smaller ecosystem than Webpack
- **Trade-off:** Some advanced Webpack plugins unavailable (not needed)

**Alternatives Considered:**
- Create React App: Outdated, slow builds
- Webpack: Complex configuration, slower build times
- Parcel: Less control over optimization

---

### ADR-006: Redux Toolkit for State Management

**Status:** Accepted

**Context:**
Complex state including book catalog, user reviews, reading lists, and recommendation data needs centralized management.

**Decision:**
Use Redux Toolkit (RTK) for global state management with React Context for theme/locale.

**Rationale:**
- **Complexity:** App state is complex with many interdependencies
- **Persistence:** RTK integrates easily with local storage middleware
- **DevTools:** Redux DevTools provide excellent debugging experience
- **Predictability:** Unidirectional data flow prevents state bugs
- **Scalability:** Proven for large applications

**Consequences:**
- **Positive:** Predictable state updates, great debugging, persistence integration
- **Negative:** Boilerplate (mitigated by RTK), learning curve
- **Trade-off:** Overhead acceptable given state complexity

**Alternatives Considered:**
- Zustand: Simpler but less tooling and middleware
- React Context only: Performance issues with frequent updates
- MobX: Less predictable, smaller ecosystem

---

### ADR-007: Google Books API for Book Data

**Status:** Accepted

**Context:**
Need comprehensive book metadata including covers, descriptions, authors for 5,000+ books.

**Decision:**
Use Google Books API as primary data source with Open Library API as fallback.

**Rationale:**
- **Data Quality:** High-quality metadata with cover images
- **Coverage:** 40+ million books available
- **Free Tier:** 1,000 requests/day sufficient for build-time fetching
- **No Authentication:** API key only (no OAuth complexity)
- **Reliability:** Google infrastructure guarantees uptime

**Consequences:**
- **Positive:** Rich data, free tier sufficient, reliable
- **Negative:** Rate limits require build-time caching strategy
- **Limitation:** Cannot fetch data client-side at scale (mitigated by build-time)

**Mitigation:**
- Fetch all book data during build process
- Cache data as static JSON files
- Use Open Library as fallback for missing data

**Alternatives Considered:**
- Open Library API: Lower quality data, less reliable
- Commercial APIs (Book API, Goodreads): Costly or deprecated
- Scraping: Legal and reliability concerns

---

### ADR-008: CloudFront CDN for Global Distribution

**Status:** Accepted

**Context:**
Users worldwide need <2 second page load times with 99.9% uptime per NFRs.

**Decision:**
Use AWS CloudFront CDN in front of S3 for global content delivery.

**Rationale:**
- **Performance:** 200+ edge locations provide <50ms latency globally
- **Cost-Effective:** $0.085/GB for first 10TB (S3 alone: $0.09/GB egress)
- **Integration:** Native integration with S3 and Route53
- **Caching:** Intelligent caching reduces origin load
- **Security:** DDoS protection, WAF integration, HTTPS at edge

**Consequences:**
- **Positive:** Global low latency, improved reliability, better security
- **Negative:** Added complexity (cache invalidation), minimal additional cost
- **Trade-off:** Cache invalidation delays (<5 min) acceptable for static content

**Alternatives Considered:**
- S3 alone: Higher latency, no edge caching
- Cloudflare: Vendor lock-in concerns, less AWS integration
- Fastly: Higher cost for similar features

---

### ADR-009: No User Authentication System

**Status:** Accepted

**Context:**
PRD non-goals explicitly exclude user authentication. Need to handle user identity for reviews and lists.

**Decision:**
Use anonymous UUID stored in local storage to identify users across sessions. No passwords or email collection.

**Rationale:**
- **Simplicity:** Eliminates authentication infrastructure completely
- **Privacy:** No personal data collection or storage
- **Alignment:** PRD explicitly excludes authentication
- **Cost:** Zero authentication infrastructure costs
- **User Friction:** No sign-up barriers to engagement

**Consequences:**
- **Positive:** Simple implementation, maximum privacy, zero friction
- **Negative:** No cross-device sync, no user recovery mechanism
- **Limitation:** Reviews tied to browser, not portable

**Future Enhancement:**
- Optional OAuth (Google, GitHub) for cross-device sync
- Anonymous user can "claim" their data by authenticating
- Maintains simplicity while enabling power user features

**Alternatives Considered:**
- Email/password auth: Violates PRD non-goals
- Social OAuth only: Still requires backend session management
- No user identity: Cannot attribute reviews or maintain lists

---

### ADR-010: Client-Side Recommendation Engine

**Status:** Accepted

**Context:**
FR-007 requires personalized recommendations based on user ratings and preferences without backend infrastructure.

**Decision:**
Implement a hybrid recommendation algorithm (collaborative + content-based filtering) running entirely client-side.

**Rationale:**
- **No Backend:** Consistent with static architecture (ADR-001)
- **Privacy:** User data stays local, no tracking
- **Feasibility:** Algorithms can run in-browser for 10K books
- **Quality:** Hybrid approach provides better results than single method
- **Real-time:** Recommendations update instantly with new ratings

**Algorithm Details:**
- **Content-Based:** Genre, author similarity using TF-IDF
- **Collaborative:** User-based similarity with rating correlation
- **Hybrid:** Weighted combination (70% content, 30% collaborative)
- **Minimum Data:** Requires 5 rated books per PRD

**Consequences:**
- **Positive:** Works offline, private, instant updates, no cost
- **Negative:** Limited to local user data (no global collaborative filtering)
- **Limitation:** Cold start problem for new users (mitigated by trending books)

**Performance:**
- Web Worker to avoid blocking main thread
- Memoized calculations (recompute only on new ratings)
- Recommendation caching in state

**Alternatives Considered:**
- Backend recommendation API: Requires infrastructure, violates ADR-001
- No recommendations: Violates FR-007
- Simple genre matching: Poor quality, doesn't meet "personalized" requirement

---

### ADR-011: DOMPurify for XSS Prevention

**Status:** Accepted

**Context:**
Users can submit review text (FR-003) which could contain malicious scripts. Security NFR requires XSS prevention.

**Decision:**
Use DOMPurify library to sanitize all user-generated content before rendering and before storing in local storage.

**Rationale:**
- **Security:** Industry-standard library for HTML sanitization
- **Comprehensive:** Handles all known XSS vectors
- **Maintained:** Actively maintained with security updates
- **Lightweight:** 20KB gzipped
- **Configurable:** Whitelist allowed HTML tags if needed

**Implementation:**
```typescript
import DOMPurify from 'dompurify';

const sanitizeReview = (text: string): string => {
  return DOMPurify.sanitize(text, { ALLOWED_TAGS: [] }); // Strip all HTML
};
```

**Consequences:**
- **Positive:** Robust XSS protection, minimal performance impact
- **Negative:** 20KB bundle size increase (acceptable)
- **Trade-off:** Users cannot use HTML formatting in reviews (acceptable for security)

**Additional Security Measures:**
- CSP headers prevent inline scripts
- Validate rating inputs (1-5 range)
- Character limits on review text (2000 chars per FR-003)

**Alternatives Considered:**
- Manual regex sanitization: Error-prone, incomplete coverage
- No sanitization: Unacceptable security risk
- Backend sanitization: No backend available

---

## Appendix: PRD Reference

# Product Requirements Document: Create a modern book review and catalog website for adult readers. Features include:
- Book catalog with search and filtering
- User reviews and ratings
- Personal reading lists
- Book recommendations based on preferences
- Author profiles
- Static site hosted on S3 (React frontend, no backend database needed)


**Created:** 2026-02-03T13:06:50Z
**Status:** Draft

## 1. Overview

**Concept:** Create a modern book review and catalog website for adult readers. Features include:
- Book catalog with search and filtering
- User reviews and ratings
- Personal reading lists
- Book recommendations based on preferences
- Author profiles
- Static site hosted on S3 (React frontend, no backend database needed)


**Description:** Create a modern book review and catalog website for adult readers. Features include:
- Book catalog with search and filtering
- User reviews and ratings
- Personal reading lists
- Book recommendations based on preferences
- Author profiles
- Static site hosted on S3 (React frontend, no backend database needed)


---

## 2. Goals

- Provide adult readers with a comprehensive, searchable catalog of books with filtering capabilities by genre, author, publication date, and rating
- Enable users to discover new books through personalized recommendations based on their reading preferences and history
- Create an engaging community platform where users can share reviews, ratings, and curated reading lists
- Deliver a fast, responsive static website experience with minimal infrastructure costs through S3 hosting
- Offer detailed author profiles that help readers explore works by their favorite writers

---

## 3. Non-Goals

- Building a backend database or server infrastructure (static site only with client-side data management)
- Implementing real-time user-to-user messaging or social networking features
- Creating an e-commerce platform for purchasing books
- Developing native mobile applications (web-only responsive design)
- Supporting multimedia content like video reviews or podcasts

---

## 4. User Stories

- As an avid reader, I want to search for books by title, author, or genre so that I can quickly find books I'm interested in
- As a user, I want to filter books by multiple criteria (genre, rating, publication year) so that I can discover books that match my preferences
- As a reader, I want to write and publish reviews with ratings so that I can share my opinions with other readers
- As a user, I want to create and manage personal reading lists (e.g., "To Read", "Currently Reading", "Favorites") so that I can organize my reading goals
- As a book enthusiast, I want to receive personalized book recommendations based on my reading history and preferences so that I can discover new books I'll enjoy
- As a reader, I want to view detailed author profiles with their bibliography and bio so that I can explore more works by authors I like
- As a user, I want to browse other users' public reading lists so that I can get inspiration for my next read
- As a casual browser, I want to see top-rated books and trending reviews on the homepage so that I can quickly find popular and well-reviewed books
- As a returning visitor, I want my reading lists and preferences saved locally so that I can continue where I left off
- As a mobile user, I want a responsive design that works seamlessly on my phone or tablet so that I can browse books on any device

---

## 5. Acceptance Criteria

**Book Search and Filtering:**
- Given I am on the catalog page, when I enter a search term in the search bar, then I see results that match the book title, author name, or keywords
- Given I am viewing search results, when I apply filters for genre, rating range, or publication date, then the results update to show only books matching all selected criteria
- Given I have applied multiple filters, when I clear filters, then all books are displayed again

**User Reviews and Ratings:**
- Given I am viewing a book detail page, when I submit a review with a star rating (1-5) and text comment, then my review is saved and displayed on the book page
- Given I have submitted a review, when I return to the book page, then I see my review marked as "My Review"
- Given a book has multiple reviews, when I view the book details, then I see the average rating calculated from all reviews

**Personal Reading Lists:**
- Given I am viewing a book, when I add it to a reading list (e.g., "To Read", "Favorites"), then the book appears in that list on my profile
- Given I have books in my reading lists, when I navigate to my lists page, then I see all my lists with their respective books
- Given I am on my reading list, when I remove a book or delete a list, then the changes persist across sessions

**Book Recommendations:**
- Given I have rated at least 5 books, when I visit the recommendations page, then I see personalized book suggestions based on my preferences
- Given I interact with recommended books (view, rate, or add to list), when I refresh recommendations, then the suggestions adapt to my latest activity

**Author Profiles:**
- Given I click on an author's name, when the author page loads, then I see their biography, photo, and complete list of books in the catalog
- Given I am on an author profile, when I click on a book, then I navigate to that book's detail page

---

## 6. Functional Requirements

**FR-001:** The system shall provide a searchable book catalog with real-time text search across titles, authors, and descriptions

**FR-002:** The system shall support multi-criteria filtering including genre, rating (1-5 stars), publication year, and author

**FR-003:** The system shall allow users to submit reviews consisting of a star rating (1-5) and text commentary (minimum 10 characters, maximum 2000 characters)

**FR-004:** The system shall calculate and display average ratings for each book based on all submitted user reviews

**FR-005:** The system shall enable users to create, name, and manage multiple reading lists (e.g., "To Read", "Currently Reading", "Favorites")

**FR-006:** The system shall allow users to add and remove books from their reading lists

**FR-007:** The system shall generate personalized book recommendations using a client-side algorithm based on user ratings, reading history, and genre preferences

**FR-008:** The system shall display detailed author profiles including biography, photo, and a complete list of their cataloged works

**FR-009:** The system shall persist user data (reviews, ratings, reading lists, preferences) using browser local storage

**FR-010:** The system shall display book details including cover image, title, author, publication date, genre, synopsis, and user reviews

**FR-011:** The system shall provide a responsive design that adapts to desktop, tablet, and mobile screen sizes

**FR-012:** The system shall allow users to export their reading lists in JSON or CSV format

**FR-013:** The system shall display trending books and top-rated books on the homepage

---

## 7. Non-Functional Requirements

### Performance
- Page load time shall not exceed 2 seconds on standard broadband connections (10 Mbps+)
- Search and filter operations shall return results within 500ms for catalogs containing up to 10,000 books
- The application shall achieve a Lighthouse performance score of 90+ for desktop and 80+ for mobile
- Static assets (images, CSS, JS) shall be optimized and compressed to minimize bundle size
- The application shall lazy-load book cover images to improve initial page load performance

### Security
- All user data shall be stored exclusively in browser local storage with no server-side transmission
- The application shall sanitize all user-generated content (reviews, list names) to prevent XSS attacks
- Book cover images and external resources shall be loaded over HTTPS only
- The S3 bucket shall be configured with appropriate CORS policies to restrict access to authorized domains
- The application shall implement Content Security Policy (CSP) headers to prevent unauthorized script execution

### Scalability
- The application architecture shall support static catalogs of up to 50,000 books without performance degradation
- The client-side search and filtering algorithms shall efficiently handle datasets of 10,000+ books using indexing techniques
- The static site shall leverage CloudFront CDN for global distribution and reduced latency
- The application shall support concurrent access by unlimited users without server-side bottlenecks

### Reliability
- The static site shall achieve 99.9% uptime leveraging S3's built-in reliability
- The application shall gracefully handle local storage quota limits with user notifications
- The application shall implement error boundaries to prevent complete application crashes from component failures
- The application shall provide fallback UI states when book cover images fail to load
- The application shall include automated deployment pipelines with rollback capabilities

---

## 8. Dependencies

- **React 18+:** Frontend framework for building the user interface
- **React Router:** Client-side routing for navigation between pages
- **Book Data API:** Third-party API (e.g., Google Books API, Open Library API) for initial book catalog data
- **Lunr.js or similar:** Client-side search library for full-text search functionality
- **Local Storage API:** Browser API for persisting user data (reviews, lists, preferences)
- **AWS S3:** Static website hosting platform
- **AWS CloudFront (optional):** CDN for improved global performance
- **Build Tools:** Webpack, Vite, or similar for bundling and optimization
- **UI Component Library:** Material-UI, Ant Design, or similar for consistent design components
- **State Management:** Redux, Zustand, or React Context for managing application state
- **Book Cover Images:** Third-party image hosting or CDN for book cover artwork

---

## 9. Out of Scope

- Backend server infrastructure, databases, or API development
- User authentication and account management with passwords
- Real-time chat, forums, or social networking features between users
- E-commerce functionality including book purchasing, shopping carts, or payment processing
- Integration with e-readers or e-book platforms
- Native iOS or Android mobile applications
- Content moderation tools or administrative dashboards for managing reviews
- Multi-language support or internationalization (English only in initial version)
- Email notifications or newsletter functionality
- Advanced analytics or user behavior tracking beyond basic client-side metrics
- Book lending or sharing features between users

---

## 10. Success Metrics

- **Catalog Completeness:** Maintain a catalog of at least 5,000 books across diverse genres within 3 months of launch
- **User Engagement:** Achieve an average session duration of 5+ minutes per visit
- **Review Activity:** Generate at least 500 user reviews within the first 6 months
- **Reading List Adoption:** 60% of returning users create at least one reading list
- **Performance:** Maintain average page load times under 2 seconds as measured by Google Analytics
- **Mobile Usage:** Achieve 40%+ of traffic from mobile devices with equivalent engagement metrics
- **Recommendation Effectiveness:** 30% of recommended books are added to user reading lists or receive ratings
- **Return Visits:** Achieve a 30-day user retention rate of 25% or higher
- **Search Utilization:** 70% of users perform at least one search during their session
- **Site Reliability:** Maintain 99.9% uptime with zero critical incidents affecting user data

---

## Appendix: Clarification Q&A

### Clarification Questions & Answers
