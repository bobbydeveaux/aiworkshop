# ROAM Analysis: test-website

**Feature Count:** 15
**Created:** 2026-02-02T23:43:21Z

## Risks

<!-- AI: Identify 5-10 project risks with severity (High/Medium/Low) -->

1. **Build Time Scalability** (High): With 10,000+ pages of content, static site generation build times may exceed acceptable limits (target: <15 minutes). Next.js builds can become slow with large page counts, potentially impacting content deployment velocity and developer experience. This directly conflicts with the requirement to support 50+ new articles per month.

2. **Third-Party Service Dependencies** (High): The architecture relies heavily on external services (Algolia for search, Cloudinary for images, Vercel for hosting, Strapi/Contentful for CMS). Any service outage, API changes, or pricing model shifts could significantly impact the site. The 99.5% uptime SLA depends on the combined reliability of all these services.

3. **Strapi CMS Complexity** (Medium): Self-hosted Strapi requires managing PostgreSQL database, handling migrations, implementing backup strategies, and maintaining infrastructure. The team needs DevOps expertise for database scaling, security patches, and disaster recovery. Alternative managed CMS (Contentful) has cost implications at scale.

4. **Search Service Cost Scaling** (Medium): Algolia's pricing is based on search operations and records. With success metrics targeting 5,000+ monthly visitors and 20% search usage, costs could grow rapidly (1,000+ searches/day = 30k+ searches/month, approaching paid tier limits). Search is critical functionality with no easy migration path.

5. **Content Migration and Initial Seeding** (Medium): The project requires 50+ comprehensive articles at launch to meet "Content Coverage" success metrics. Content creation, migration, and structuring into the CMS schema (Article, PenModel, Brand, GlossaryTerm entities) is time-consuming and requires subject matter expertise about pens.

6. **Image Optimization Pipeline Complexity** (Low): Integration between Strapi CMS, Cloudinary CDN, and Next.js Image component requires careful configuration. Image URLs must flow correctly from CMS → Cloudinary → Frontend, with proper transformations and lazy loading. Misconfiguration could impact page load time targets (<2s).

7. **Webhook Reliability and Build Triggers** (Medium): Content updates depend on webhooks from Strapi → Vercel to trigger rebuilds. Webhook failures, network issues, or build queue delays could create content publication gaps. No built-in retry mechanism in standard webhook implementations.

---

## Obstacles

<!-- AI: Current blockers or challenges (technical, resource, dependency) -->

- **No Existing Content Repository**: The project lacks initial content about pens. Meeting the 50+ article requirement for launch requires either content creation from scratch or sourcing/licensing content from pen enthusiasts, which is outside the technical scope but blocks launch readiness.

- **Complex Content Modeling Requirements**: The data model includes 9+ entities (Article, PenModel, Brand, Category, Tag, PenType, GlossaryTerm, Media, ComparisonSet) with multiple relationships. Defining accurate content types in Strapi, implementing validation rules, and creating editorial workflows requires significant upfront effort before development can begin.

- **External Service Account Setup**: The architecture requires accounts and configuration for 5+ external services (Vercel, Cloudinary, Algolia, PostgreSQL hosting, analytics service, Sentry). Each requires signup, billing configuration, API key generation, and integration testing, creating sequential dependencies that block parallel development.

- **Comparison Tool Feature Complexity**: The pen comparison tool (FR-006) requires dynamic data fetching, client-side state management for multiple selected pens, and side-by-side specification display. This is marked as "high complexity" in the epic and requires significant frontend engineering that could delay the feature set.

---

## Assumptions

<!-- AI: Key assumptions the plan depends on -->

1. **Content Team Availability and Expertise**: Assumes access to writers/editors with pen domain knowledge who can create 50+ comprehensive articles covering fountain pens, ballpoint pens, brands, models, and specifications. Validation: Confirm content team capacity and pen expertise before sprint planning.

2. **PostgreSQL Database Availability**: Assumes PostgreSQL database can be provisioned with sufficient capacity (storage for 10,000+ pages, connection pooling for 500+ connections). Validation: Provision staging database early and load test with representative content volume.

3. **Algolia Free Tier Sufficiency for MVP**: Assumes Algolia's free tier (10k searches/month, 10k records) covers initial launch phase. Validation: Calculate expected search volume from traffic projections (5,000 monthly visitors × 20% search usage × 3 searches/session = 3,000 searches/month - within limits).

4. **Next.js ISR Handles Content Update Latency**: Assumes 1-5 minute delay for content updates (build time + cache invalidation) is acceptable to editors and users. Validation: Confirm with stakeholders that "publish" doesn't mean "immediately live" and 5-minute SLA is acceptable.

5. **No Mobile App Requirements in V1**: Assumes headless CMS architecture provides sufficient future-proofing for potential mobile apps without immediate implementation. Validation: Explicitly confirmed in PRD non-goals section.

6. **Team TypeScript and React Proficiency**: Assumes development team has experience with Next.js 14+, TypeScript, React 18+, and Jamstack architecture. Validation: Assess team skills and plan for training/ramp-up time if needed.

---

## Mitigations

<!-- AI: For each risk, propose mitigation strategies -->

### Risk 1: Build Time Scalability

**Mitigation Strategies:**
- **Implement Incremental Static Regeneration (ISR)** from day one: Configure `revalidate` parameter on all dynamic pages to regenerate on-demand rather than rebuilding entire site. Target: only rebuild changed pages + homepage.
- **Use Next.js Parallel Builds**: Configure `experimental.workerThreads: true` and `cpus: 4` in next.config.js to parallelize page generation (already specified in LLD Section 12.5).
- **Establish Build Time Monitoring**: Add CI/CD job that tracks build duration per commit. Alert if build time exceeds 10 minutes, escalate at 15 minutes. Monitor page count vs build time ratio.
- **Optimize Content Fetching**: Batch CMS API requests during build (fetch all articles in 100-item pages rather than individual queries). Cache CMS responses during build process.
- **Contingency Plan**: If builds exceed 15 minutes consistently, implement on-demand ISR exclusively for article pages and switch to scheduled nightly full rebuilds for non-critical pages.

### Risk 2: Third-Party Service Dependencies

**Mitigation Strategies:**
- **Abstract Service Interfaces**: Create wrapper functions for Algolia search (`src/lib/algolia.ts`), Cloudinary images (`src/lib/cloudinary.ts`), and Strapi CMS (`src/lib/strapi.ts`). This enables swapping providers without rewriting application code.
- **Implement Health Check Endpoints**: Create `/api/health` endpoint that tests connectivity to all critical services (CMS, search, database). Monitor every 5 minutes with uptime service.
- **Set Up Service Status Monitoring**: Subscribe to status pages for Vercel, Algolia, Cloudinary. Configure Slack/email alerts for service degradation notifications.
- **Document Migration Procedures**: Create runbooks for migrating from Algolia → MeiliSearch (self-hosted) and Contentful → Strapi if pricing/terms become unfavorable. Test migration in staging annually.
- **Negotiate SLAs with Paid Tiers**: Once traffic grows, upgrade to paid tiers with SLA guarantees (e.g., Algolia Premium with 99.9% uptime SLA).

### Risk 3: Strapi CMS Complexity

**Mitigation Strategies:**
- **Consider Contentful for MVP**: Evaluate using managed Contentful CMS for initial launch to eliminate database management, backup, and scaling concerns. Defer self-hosted Strapi decision until traffic/cost justifies complexity.
- **If Using Strapi, Use Managed Database**: Deploy PostgreSQL on managed service (AWS RDS, DigitalOcean Managed Database, Railway) rather than self-managing. Enable automated backups (daily snapshots, 30-day retention).
- **Infrastructure as Code**: Use Docker Compose for local development and production deployment (cms.Dockerfile already specified in LLD Section 10.1). Version control all infrastructure configuration.
- **Database Migration Testing**: Establish staging environment that mirrors production. Test all Strapi upgrades and database migrations in staging 1 week before production deployment.
- **Implement Database Monitoring**: Set up alerts for connection pool exhaustion (>80% utilization), slow queries (>1s), and storage capacity (>75% used). Use DataDog or AWS CloudWatch.

### Risk 4: Search Service Cost Scaling

**Mitigation Strategies:**
- **Monitor Search Usage Proactively**: Implement analytics on search query volume, queries per user, and zero-result searches. Set up alerts at 7,500 searches/month (75% of free tier).
- **Optimize Search Index Size**: Use `filterOnly` attributes for facets not displayed to users (reduces index size). Limit searchable content to title, excerpt, tags (exclude full article body from search index to reduce operations).
- **Implement Search Result Caching**: Cache popular search queries (e.g., "fountain pen", "best ballpoint") in CDN or Redis with 15-minute TTL. This reduces Algolia API calls for common searches.
- **Self-hosted Fallback Plan**: Prepare MeiliSearch self-hosted alternative. Estimate infrastructure costs (MeiliSearch on $20/month VPS vs Algolia at $1/1000 searches). Have migration script ready if costs exceed threshold.
- **Rate Limit Search API**: Implement client-side debouncing (300ms) on search input to reduce queries-per-keystroke. Limit search queries to 20/minute per IP address.

### Risk 5: Content Migration and Initial Seeding

**Mitigation Strategies:**
- **Create Content Templates**: Build Strapi content type schemas first, then generate CSV templates for bulk content import. Provide editors with structured templates (fields: title, excerpt, content, category, tags).
- **Phased Content Launch**: Launch with minimum 20 high-quality articles across core categories (5 fountain pen articles, 5 ballpoint, 5 brand profiles, 5 buying guides). Add remaining 30 articles over 8 weeks post-launch.
- **Hire Freelance Content Writers**: Budget for 3-5 freelance writers with pen expertise. Provide style guide, content templates, and editorial review process. Estimate 2-3 articles per writer per week.
- **Source Public Domain Content**: Research Creative Commons or public domain pen resources (Wikipedia, pen enthusiast blogs with CC licenses) for initial content base. Always verify licensing and attribute properly.
- **Build Sample Content for Development**: Create 10 realistic sample articles during development phase for testing search, navigation, and performance. Use Lorem Ipsum with real pen terminology.

### Risk 6: Image Optimization Pipeline Complexity

**Mitigation Strategies:**
- **Use Cloudinary Strapi Plugin**: Install `@strapi/provider-upload-cloudinary` plugin for seamless integration. Configure in `cms/config/plugins.js` with upload preset for automatic transformations.
- **Standardize Image URLs**: Configure Cloudinary to return consistent URL format that Next.js Image component accepts. Test image loading during development setup phase.
- **Create Image Upload Guidelines**: Document image requirements for content editors (minimum 1200px width, JPEG/PNG only, <5MB file size). Provide image optimization checklist.
- **Implement Fallback Images**: Configure Next.js Image component with placeholder blur images and fallback behavior if Cloudinary is unreachable. Use local placeholder images for development.
- **Test Image Performance Early**: Add image-heavy test pages during development. Measure LCP (target <2.5s) with real image assets to validate optimization pipeline works.

### Risk 7: Webhook Reliability and Build Triggers

**Mitigation Strategies:**
- **Implement Webhook Retry Logic**: Use webhook service with built-in retries (e.g., Hookdeck, Svix) or implement custom retry queue with exponential backoff (3 retries over 15 minutes).
- **Add Webhook Status Monitoring**: Log all webhook events in Strapi and Vercel. Create dashboard showing webhook delivery success rate (target: >99%). Alert on failures >5% over 1 hour.
- **Provide Manual Build Trigger**: Add "Rebuild Site" button in Strapi admin panel that directly calls Vercel deployment API. Document for editors to use if webhook fails.
- **Implement Build Queue Visibility**: Show editors the build status (queued, building, deployed, failed) in Strapi admin interface using Vercel API. Provide transparency into deployment process.
- **Use On-Demand ISR as Backup**: Configure `revalidate` API routes that editors can manually call to refresh specific pages without full site rebuild. Document as webhook failure workaround.

---

## Appendix: Plan Documents

### PRD
# Product Requirements Document: I want a website all about Pens

**Created:** 2026-02-02T23:28:53Z
**Status:** Draft

## 1. Overview

**Concept:** I want a website all about Pens

**Description:** I want a website all about Pens

---

## 2. Goals

<!-- AI: Based on the concept and clarification Q&A, list 3-5 primary goals. Each goal should be specific and measurable. -->

- Create a comprehensive information hub about pens, covering different types, brands, and uses
- Provide educational content to help users understand pen mechanics, materials, and history
- Build an engaging platform where pen enthusiasts can discover and learn about writing instruments
- Establish a resource library with detailed guides, comparisons, and reviews of various pen types
- Foster user engagement through informative content that drives repeat visits

---

## 3. Non-Goals

<!-- AI: List 3-5 explicit non-goals to set boundaries. -->

- E-commerce functionality or direct pen sales
- User authentication or account management systems
- Social networking features (user profiles, messaging, following)
- Mobile application development (initial version)
- Integration with third-party inventory or shopping platforms

---

## 4. User Stories

<!-- AI: Generate 5-10 user stories in the format: "As a [user type], I want [goal] so that [benefit]" -->

- As a pen enthusiast, I want to browse different categories of pens so that I can learn about types I'm unfamiliar with
- As a beginner, I want to read introductory guides about pens so that I can understand the basics of writing instruments
- As a collector, I want to view detailed specifications and history of specific pen models so that I can make informed decisions
- As a student, I want to compare different pen types (ballpoint, rollerball, fountain) so that I can choose the best pen for my needs
- As a professional, I want to learn about luxury and business pens so that I can find appropriate writing instruments for my work
- As a casual visitor, I want to search for specific pen brands or models so that I can quickly find relevant information
- As an artist, I want to discover specialty pens and their applications so that I can expand my creative toolkit
- As a history buff, I want to read about the evolution of pens so that I can appreciate their cultural significance
- As a researcher, I want to access organized content by categories so that I can efficiently navigate the site

---

## 5. Acceptance Criteria

<!-- AI: For each major user story, define acceptance criteria in Given/When/Then format -->

**Browse Pen Categories:**
- Given I am on the homepage, When I click on a category (e.g., "Fountain Pens"), Then I should see a list of relevant articles and guides
- Given I am viewing a category, When the page loads, Then I should see at least 5-10 items organized clearly
- Given I am browsing categories, When I select a subcategory, Then the content should filter appropriately

**Read Educational Content:**
- Given I am viewing an article, When the page loads, Then I should see well-formatted text with headings, images, and structured content
- Given I am reading a guide, When I scroll through the content, Then images and diagrams should load properly
- Given I am on a guide page, When I finish reading, Then I should see related articles or suggested next reads

**Search Functionality:**
- Given I am on any page, When I enter a search term in the search box, Then I should see relevant results within 2 seconds
- Given I have searched for a term, When results are displayed, Then they should be ranked by relevance
- Given I search for a specific brand or model, When matches exist, Then they should appear at the top of results

**Compare Pen Types:**
- Given I want to compare pens, When I access the comparison section, Then I should see side-by-side specifications
- Given I am viewing a comparison, When the data loads, Then key differences should be clearly highlighted
- Given I am comparing items, When I select different pens, Then the comparison should update dynamically

---

## 6. Functional Requirements

<!-- AI: List specific functional requirements (FR-001, FR-002, etc.) -->

**FR-001:** The website shall display a homepage with featured pen content and category navigation
**FR-002:** The system shall provide categorized browsing by pen type (fountain, ballpoint, rollerball, gel, specialty)
**FR-003:** The website shall include detailed article pages with text, images, and specifications
**FR-004:** The system shall implement a search function that queries across all content
**FR-005:** The website shall display brand profiles with history and notable models
**FR-006:** The system shall provide comparison pages showing specifications side-by-side
**FR-007:** The website shall include a glossary of pen-related terminology
**FR-008:** The system shall organize content with tags and categories for easy navigation
**FR-009:** The website shall display high-quality images of pens with zoom capability
**FR-010:** The system shall provide internal linking between related articles and topics
**FR-011:** The website shall include a navigation menu accessible from all pages
**FR-012:** The system shall display breadcrumb navigation showing the user's current location

---

## 7. Non-Functional Requirements

### Performance
- Page load time shall not exceed 2 seconds on standard broadband connections
- Images shall be optimized to load within 1 second without sacrificing quality
- Search results shall return within 2 seconds for any query
- The website shall support at least 1,000 concurrent users without performance degradation
- Static assets shall be cached to improve repeat visit performance

### Security
- All pages shall be served over HTTPS
- The website shall implement basic security headers (CSP, X-Frame-Options, etc.)
- User input in search functionality shall be sanitized to prevent XSS attacks
- The system shall protect against common web vulnerabilities (OWASP Top 10)
- Regular security updates shall be applied to all dependencies and frameworks

### Scalability
- The website architecture shall support scaling to 10,000+ pages of content
- The system shall handle traffic spikes of up to 10x normal load
- Content management shall support addition of 50+ new articles per month
- The database structure shall accommodate growing content without performance loss

### Reliability
- The website shall maintain 99.5% uptime
- The system shall implement automated backups daily
- Error pages shall provide helpful information and navigation options
- The website shall gracefully handle missing images or broken links
- Monitoring shall alert administrators of critical failures within 5 minutes

---

## 8. Dependencies

<!-- AI: List external systems, APIs, libraries this project depends on -->

- **Web Hosting Service:** Cloud hosting platform (e.g., AWS, Netlify, Vercel) for deploying the website
- **Content Management System:** CMS platform (e.g., WordPress, Strapi, or static site generator like Hugo/Jekyll)
- **Image Optimization Service:** CDN or image optimization service for efficient media delivery
- **Search Engine:** Search library or service (e.g., Algolia, ElasticSearch, or built-in CMS search)
- **Domain Registration:** Domain registrar for website URL
- **Analytics Platform:** Web analytics tool (e.g., Google Analytics, Plausible) for tracking usage
- **SSL Certificate:** SSL/TLS certificate provider for HTTPS encryption
- **Frontend Framework:** Modern web framework (React, Vue, or vanilla HTML/CSS/JS)

---

## 9. Out of Scope

<!-- AI: Based on non-goals and clarification, explicitly state what is NOT included -->

- Online shopping cart or checkout functionality
- User registration, login, or personalized accounts
- Community features such as forums, comments, or user-generated content
- Social media integration beyond basic share buttons
- Newsletter subscription or email marketing automation
- Mobile native applications (iOS/Android)
- Real-time inventory tracking or price monitoring
- Affiliate marketing links or monetization features
- Multi-language support (initial version will be English-only)
- Interactive tools like pen customization or design simulators
- Video hosting or streaming content
- Integration with retail point-of-sale systems

---

## 10. Success Metrics

<!-- AI: Define measurable success criteria -->

- **Traffic:** Achieve 5,000 unique monthly visitors within 6 months of launch
- **Engagement:** Average session duration of at least 3 minutes
- **Content Coverage:** Publish at least 50 comprehensive articles across all major pen categories
- **Search Effectiveness:** Search feature used by at least 20% of visitors
- **Bounce Rate:** Maintain bounce rate below 60%
- **Page Views:** Average 3+ pages per session
- **Return Visitors:** Achieve 30% returning visitor rate within 1 year
- **Load Performance:** 95% of pages load within 2 seconds
- **Content Quality:** Maintain average page read depth of 50% or higher
- **SEO Performance:** Rank in top 10 Google results for at least 10 pen-related keywords within 1 year

---

## Appendix: Clarification Q&A

### Clarification Questions & Answers


### HLD
# High-Level Design: aiworkshop

**Created:** 2026-02-02T23:29:44Z
**Status:** Draft

## 1. Architecture Overview

<!-- AI: Describe the overall system architecture (microservices, monolith, serverless, etc.) -->

The system will use a **Jamstack architecture** with a static site generator approach, optimized for content-heavy websites with minimal dynamic functionality. This architecture separates content management from content delivery, providing excellent performance, security, and scalability for an informational website.

**Core Architecture Pattern:**
- **Static Site Generation (SSG):** Pre-rendered HTML pages generated at build time
- **Headless CMS:** Decoupled content management system for editorial workflows
- **CDN-First Delivery:** Global content delivery network for static assets and pages
- **API Layer:** Serverless functions for dynamic features (search, comparisons)

**Rationale:**
This architecture is ideal for content-focused websites because:
- Serves pre-rendered HTML for sub-second page loads
- Eliminates server-side processing for most requests, reducing costs and improving reliability
- Provides excellent SEO through server-side rendering
- Scales automatically through CDN distribution
- Maintains high security posture with minimal attack surface
- Supports content editor workflows through headless CMS

---

## 2. System Components

<!-- AI: List major components/services with brief descriptions -->

### 2.1 Content Management Layer
**Headless CMS (Strapi/Contentful)**
- Content authoring interface for editors and administrators
- Content modeling for articles, brands, pen types, specifications
- Media asset management for pen images and diagrams
- Workflow management for content approval and publishing
- Version control and content scheduling

### 2.2 Build & Generation Layer
**Static Site Generator (Next.js/Gatsby)**
- Fetches content from headless CMS during build
- Generates static HTML pages for all routes
- Optimizes images and assets automatically
- Implements incremental static regeneration for updates
- Handles routing and navigation structure

### 2.3 Presentation Layer
**Frontend Application**
- React-based UI components for content display
- Responsive layouts for desktop, tablet, and mobile
- Interactive comparison tool interface
- Image gallery with zoom functionality
- Navigation menus, breadcrumbs, and site structure
- Client-side routing for smooth navigation

### 2.4 Search Service
**Search API (Algolia/MeiliSearch)**
- Full-text search across all content
- Real-time search indexing on content updates
- Faceted search with filters by category, brand, type
- Search analytics and query optimization
- Typo tolerance and synonym handling

### 2.5 CDN & Edge Network
**Content Delivery Network (Cloudflare/Vercel)**
- Global distribution of static assets
- Edge caching for optimal performance
- DDoS protection and WAF capabilities
- SSL/TLS termination
- Automatic compression and optimization

### 2.6 Analytics & Monitoring
**Analytics Service (Plausible/Google Analytics)**
- Page view tracking and user behavior analysis
- Traffic source and referral tracking
- Search term analytics
- Performance metrics and Core Web Vitals monitoring

### 2.7 Media Optimization
**Image CDN (Cloudinary/imgix)**
- Automatic image optimization and compression
- Responsive image delivery with srcset
- Format conversion (WebP, AVIF)
- On-the-fly transformations and cropping
- Lazy loading support

---

## 3. Data Model

<!-- AI: High-level data entities and relationships -->

### 3.1 Core Entities

**Article**
- `id` (UUID, primary key)
- `title` (string)
- `slug` (string, unique, indexed)
- `content` (rich text/markdown)
- `excerpt` (text)
- `featuredImage` (reference to Media)
- `author` (string)
- `publishedDate` (timestamp)
- `lastModified` (timestamp)
- `category` (reference to Category)
- `tags` (array of references to Tag)
- `relatedArticles` (array of references to Article)
- `seoMetadata` (embedded object)
- `readTime` (integer, minutes)

**PenType**
- `id` (UUID, primary key)
- `name` (string, e.g., "Fountain Pen", "Ballpoint")
- `slug` (string, unique, indexed)
- `description` (text)
- `featuredImage` (reference to Media)
- `characteristics` (array of strings)
- `articles` (array of references to Article)
- `brands` (array of references to Brand)

**Brand**
- `id` (UUID, primary key)
- `name` (string)
- `slug` (string, unique, indexed)
- `logo` (reference to Media)
- `history` (rich text)
- `foundedYear` (integer)
- `country` (string)
- `website` (URL)
- `notableModels` (array of references to PenModel)
- `articles` (array of references to Article)

**PenModel**
- `id` (UUID, primary key)
- `name` (string)
- `slug` (string, unique, indexed)
- `brand` (reference to Brand)
- `penType` (reference to PenType)
- `description` (rich text)
- `images` (array of references to Media)
- `specifications` (embedded object)
- `price` (decimal, optional)
- `releaseYear` (integer)
- `discontinued` (boolean)
- `relatedModels` (array of references to PenModel)

**Category**
- `id` (UUID, primary key)
- `name` (string)
- `slug` (string, unique, indexed)
- `description` (text)
- `parentCategory` (reference to Category, nullable)
- `icon` (reference to Media, optional)
- `sortOrder` (integer)

**Tag**
- `id` (UUID, primary key)
- `name` (string)
- `slug` (string, unique, indexed)
- `usage_count` (integer)

**Media**
- `id` (UUID, primary key)
- `filename` (string)
- `url` (URL)
- `altText` (string)
- `caption` (text, optional)
- `mimeType` (string)
- `width` (integer)
- `height` (integer)
- `fileSize` (integer, bytes)
- `uploadedAt` (timestamp)

**GlossaryTerm**
- `id` (UUID, primary key)
- `term` (string)
- `slug` (string, unique, indexed)
- `definition` (text)
- `relatedTerms` (array of references to GlossaryTerm)
- `relatedArticles` (array of references to Article)

**ComparisonSet**
- `id` (UUID, primary key)
- `title` (string)
- `slug` (string, unique, indexed)
- `description` (text)
- `penModels` (array of references to PenModel)
- `comparisonCriteria` (array of strings)
- `featuredImage` (reference to Media)

### 3.2 Relationships

- Article belongs to one Category, has many Tags
- Article can reference many related Articles
- PenType has many Articles and Brands
- Brand has many PenModels and Articles
- PenModel belongs to one Brand and one PenType
- Category can have child Categories (hierarchical)
- ComparisonSet includes multiple PenModels
- GlossaryTerm can reference related Terms and Articles

### 3.3 Search Index Structure

**SearchDocument** (denormalized for search)
- `objectID` (unique identifier)
- `type` (enum: article, brand, penModel, glossaryTerm)
- `title` (string, searchable)
- `content` (text, searchable)
- `category` (string, facet)
- `tags` (array, facets)
- `url` (string)
- `imageUrl` (string)
- `publishedDate` (timestamp, sortable)
- `relevanceScore` (integer)

---

## 4. API Contracts

<!-- AI: Define key API endpoints, request/response formats -->

### 4.1 Content API (CMS to Build Process)

**GET /api/content/articles**
```json
{
  "page": 1,
  "limit": 100,
  "filters": {
    "published": true,
    "category": "fountain-pens"
  }
}
```
Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Introduction to Fountain Pens",
      "slug": "introduction-to-fountain-pens",
      "content": "...",
      "category": { "id": "uuid", "name": "Fountain Pens" },
      "tags": [{ "id": "uuid", "name": "beginner" }],
      "publishedDate": "2026-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "pages": 2
  }
}
```

**GET /api/content/brands/{slug}**
Response:
```json
{
  "data": {
    "id": "uuid",
    "name": "Pilot",
    "slug": "pilot",
    "history": "...",
    "logo": { "url": "https://cdn.example.com/...", "altText": "Pilot Logo" },
    "notableModels": [
      { "id": "uuid", "name": "Pilot Metropolitan", "slug": "pilot-metropolitan" }
    ]
  }
}
```

### 4.2 Search API (Client to Search Service)

**POST /api/search**
Request:
```json
{
  "query": "fountain pen ink",
  "filters": {
    "category": ["fountain-pens"],
    "type": ["article", "penModel"]
  },
  "page": 1,
  "hitsPerPage": 20
}
```
Response:
```json
{
  "hits": [
    {
      "objectID": "article-uuid-123",
      "type": "article",
      "title": "Best Inks for Fountain Pens",
      "excerpt": "...",
      "url": "/articles/best-inks-for-fountain-pens",
      "imageUrl": "https://cdn.example.com/...",
      "category": "Fountain Pens",
      "tags": ["fountain pens", "ink"],
      "_highlightResult": {
        "title": "Best <em>Inks</em> for <em>Fountain</em> <em>Pens</em>"
      }
    }
  ],
  "nbHits": 47,
  "page": 1,
  "nbPages": 3,
  "processingTimeMS": 12
}
```

### 4.3 Comparison API (Client to Serverless Function)

**POST /api/compare**
Request:
```json
{
  "penModelIds": ["uuid-1", "uuid-2", "uuid-3"]
}
```
Response:
```json
{
  "data": [
    {
      "id": "uuid-1",
      "name": "Pilot Metropolitan",
      "brand": "Pilot",
      "type": "Fountain Pen",
      "specifications": {
        "nibMaterial": "Stainless Steel",
        "weight": "28g",
        "length": "143mm",
        "fillingMechanism": "Converter/Cartridge"
      },
      "price": 15.00,
      "imageUrl": "https://cdn.example.com/..."
    }
  ]
}
```

### 4.4 Analytics API (Serverless Functions)

**POST /api/analytics/pageview**
Request:
```json
{
  "url": "/articles/fountain-pen-basics",
  "referrer": "https://google.com",
  "timestamp": "2026-02-02T14:30:00Z",
  "userAgent": "Mozilla/5.0..."
}
```
Response:
```json
{
  "success": true,
  "eventId": "uuid"
}
```

### 4.5 Webhooks (CMS to Build Trigger)

**POST /api/webhooks/content-updated**
Payload:
```json
{
  "event": "entry.publish",
  "model": "article",
  "entry": {
    "id": "uuid",
    "slug": "new-article"
  },
  "timestamp": "2026-02-02T14:30:00Z"
}
```

---

## 5. Technology Stack

### Backend
- **Headless CMS:** Strapi (self-hosted) or Contentful (SaaS)
  - Rationale: Provides robust content modeling, user-friendly editorial interface, and flexible API
- **Serverless Functions:** Vercel Functions / AWS Lambda
  - Rationale: Handle dynamic operations (search, analytics) without managing servers
- **API Layer:** Node.js with Express or Next.js API Routes
  - Rationale: JavaScript consistency across stack, excellent performance for I/O operations
- **Build System:** Next.js 14+ with Static Site Generation
  - Rationale: Mature ecosystem, excellent performance, built-in optimization features

### Frontend
- **Framework:** React 18+ with Next.js 14+
  - Rationale: Industry-standard framework with excellent SSG support, large ecosystem
- **UI Library:** Tailwind CSS + Headless UI
  - Rationale: Utility-first CSS for rapid development, fully customizable, excellent performance
- **State Management:** React Context + SWR for data fetching
  - Rationale: Lightweight, sufficient for content-focused site without complex state
- **Image Optimization:** Next.js Image component
  - Rationale: Automatic optimization, lazy loading, responsive images out of the box
- **Search UI:** InstantSearch.js (if using Algolia) or custom React components
  - Rationale: Pre-built search components with excellent UX patterns

### Infrastructure
- **Hosting Platform:** Vercel or Netlify
  - Rationale: Zero-config deployments, automatic HTTPS, global CDN, serverless functions support
- **CDN:** Cloudflare or integrated CDN (Vercel Edge Network)
  - Rationale: Global distribution, DDoS protection, edge caching, excellent performance
- **Domain & DNS:** Cloudflare DNS
  - Rationale: Fast DNS resolution, integrated with CDN, excellent security features
- **CI/CD:** GitHub Actions or integrated platform CI (Vercel/Netlify)
  - Rationale: Automated builds on content changes, preview deployments, rollback capabilities

### Data Storage
- **CMS Database:** PostgreSQL (for Strapi) or managed by CMS provider (Contentful)
  - Rationale: Robust relational database, excellent for content relationships and queries
- **Search Index:** Algolia or MeiliSearch
  - Rationale: Purpose-built for search, sub-50ms response times, typo tolerance, faceting
- **Media Storage:** Cloudinary or AWS S3 + CloudFront
  - Rationale: Automatic image optimization, transformations, global CDN delivery
- **Analytics Storage:** Service-managed (Plausible/Google Analytics) or ClickHouse for self-hosted
  - Rationale: Optimized for time-series data, fast queries for dashboards

---

## 6. Integration Points

<!-- AI: External systems, APIs, webhooks -->

### 6.1 Headless CMS Integration
**Direction:** Bidirectional (Read/Write)
- **Build-time Content Fetch:** Static site generator pulls content via CMS API during builds
- **Webhook Triggers:** CMS sends webhooks to trigger rebuilds when content is published/updated
- **Media API:** CMS provides media assets through API or direct CDN links
- **Preview Mode:** Next.js preview mode connects to CMS for draft content preview

### 6.2 Search Service Integration
**Direction:** Bidirectional
- **Index Updates:** Build process pushes content updates to search index after generation
- **Query API:** Frontend queries search service directly from client-side JavaScript
- **Analytics:** Search service provides query analytics and popular search terms
- **Synchronization:** Automated sync process ensures search index matches published content

### 6.3 Image CDN Integration
**Direction:** Read-only (Frontend to CDN)
- **Image Requests:** Frontend requests optimized images with transformation parameters
- **Upload Pipeline:** CMS uploads original images to CDN during content creation
- **URL Generation:** CMS generates CDN URLs with appropriate transformations
- **Cache Invalidation:** Triggered when images are updated or replaced

### 6.4 Analytics Platform Integration
**Direction:** Write-only (Frontend to Analytics)
- **Client-side Tracking:** JavaScript snippet on all pages sends events to analytics service
- **Custom Events:** Track specific interactions (search usage, comparison views, article reads)
- **Performance Metrics:** Real User Monitoring (RUM) data sent to analytics platform
- **Server-side Events:** API routes send server-side events for specific actions

### 6.5 DNS & CDN Integration
**Direction:** Configuration
- **DNS Configuration:** Domain points to CDN/hosting platform
- **SSL/TLS:** Automatic certificate provisioning and renewal
- **Cache Control:** Headers from hosting platform instruct CDN caching behavior
- **Origin Pull:** CDN fetches content from origin (hosting platform) on cache miss

### 6.6 CI/CD Integration
**Direction:** Bidirectional
- **Git Triggers:** Commits to main branch trigger production builds
- **CMS Webhooks:** Content changes in CMS trigger rebuilds via webhook to CI/CD
- **Deployment Status:** CI/CD reports build status back to Git provider
- **Preview Deployments:** Pull requests create preview environments automatically

### 6.7 Monitoring & Alerting Integration
**Direction:** Write-only (Application to Monitoring)
- **Error Tracking:** Frontend and serverless functions send errors to Sentry or similar
- **Uptime Monitoring:** External service pings endpoints and checks availability
- **Performance Monitoring:** Real User Monitoring and synthetic checks report metrics
- **Log Aggregation:** Application logs sent to centralized logging service

---

## 7. Security Architecture

<!-- AI: Authentication, authorization, encryption, secrets management -->

### 7.1 Authentication & Authorization
**CMS Access Control:**
- Role-based access control (RBAC) within headless CMS
- User roles: Admin, Editor, Contributor
- SSO integration for team authentication (optional: Google Workspace, Okta)
- API token authentication for build process access to CMS
- Token rotation policy (90-day expiration)

**Public Website:**
- No user authentication required (public information site)
- API endpoints use CORS policies to restrict origins
- Rate limiting on public API endpoints to prevent abuse

### 7.2 Data Protection & Encryption
**In Transit:**
- TLS 1.3 for all HTTPS connections
- HSTS (HTTP Strict Transport Security) headers enforced
- Certificate pinning for critical API connections
- Secure WebSocket connections (WSS) if real-time features added

**At Rest:**
- Database encryption at rest (managed by database provider)
- Encrypted S3 buckets for media storage (AES-256)
- CMS credentials stored in encrypted environment variables
- No sensitive user data collected (no PII beyond basic analytics)

### 7.3 Input Validation & Sanitization
**Content Input:**
- HTML sanitization in CMS for rich text content (prevent stored XSS)
- File upload restrictions (type, size validation)
- Content Security Policy to prevent injection attacks

**Search Input:**
- Query parameter sanitization to prevent injection
- Rate limiting on search API (100 requests/minute per IP)
- Input length limits (max 200 characters for search queries)

### 7.4 Security Headers
**Implemented Headers:**
```
Content-Security-Policy: default-src 'self'; img-src 'self' https://cdn.example.com; script-src 'self' 'unsafe-inline' https://analytics.example.com
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 7.5 Secrets Management
**Environment Variables:**
- CMS API keys stored in Vercel/Netlify environment variables
- Search service API keys in encrypted environment variables
- Separate keys for development, staging, production environments
- Regular key rotation (quarterly)

**Build-time Secrets:**
- Read-only CMS API tokens for build process
- Write-only search API tokens for index updates
- Secrets never committed to version control (.env files in .gitignore)

### 7.6 API Security
**Rate Limiting:**
- Search API: 100 requests/minute per IP
- Comparison API: 50 requests/minute per IP
- Global rate limit: 1000 requests/minute per IP

**DDoS Protection:**
- Cloudflare DDoS protection at edge
- WAF rules to block malicious patterns
- Automatic IP blocking for suspicious activity

### 7.7 Dependency Security
**Supply Chain Security:**
- Automated dependency scanning (Dependabot, Snyk)
- Regular updates for security patches
- Lock files committed (package-lock.json, yarn.lock)
- Security audit on npm install in CI/CD pipeline

### 7.8 Compliance & Privacy
**Data Privacy:**
- Cookie consent banner for analytics (GDPR compliance)
- Privacy policy page outlining data collection
- Minimal data collection (no PII beyond IP address for analytics)
- Analytics data anonymization where possible

---

## 8. Deployment Architecture

<!-- AI: How components are deployed (K8s, containers, serverless) -->

### 8.1 Deployment Model
**Static Site:** Serverless / Edge Deployment
- Pre-rendered HTML pages deployed to global CDN edge locations
- No traditional servers or containers for frontend delivery
- Automatic deployment on git push to main branch

**Serverless Functions:** Function-as-a-Service (FaaS)
- Search API endpoints as serverless functions (Vercel Functions / AWS Lambda)
- Comparison API as serverless function
- Analytics ingestion as serverless function
- Auto-scaling based on request volume

**Headless CMS:** Managed Service or Containerized Deployment
- **Option A (Managed):** Contentful SaaS - fully managed, no deployment needed
- **Option B (Self-hosted Strapi):** Docker container on AWS ECS/Fargate or Digital Ocean App Platform

### 8.2 Deployment Environments

**Production Environment:**
- **Domain:** www.pensencyclopedia.com
- **Hosting:** Vercel production deployment
- **CMS:** Production Strapi instance or Contentful production space
- **Search:** Algolia production index
- **CDN:** Cloudflare with production cache settings (long TTL)
- **Database:** Production PostgreSQL (if self-hosted CMS)

**Staging Environment:**
- **Domain:** staging.pensencyclopedia.com
- **Hosting:** Vercel preview deployment (main staging branch)
- **CMS:** Staging CMS instance with copy of production content
- **Search:** Algolia staging index
- **CDN:** Cloudflare with short TTL for testing
- **Database:** Staging PostgreSQL with anonymized production data

**Development Environment:**
- **Domain:** localhost:3000 or dev branch preview deployments
- **Hosting:** Local development server or Vercel preview deployments per PR
- **CMS:** Shared development CMS instance or local Strapi instance
- **Search:** Development search index or mock search responses
- **Database:** Local PostgreSQL or SQLite for CMS

### 8.3 Deployment Pipeline

**Build Process:**
1. **Trigger:** Git push to main or CMS webhook on content publish
2. **Install Dependencies:** npm install with cached node_modules
3. **Fetch Content:** Query CMS API for all published content
4. **Generate Pages:** Next.js builds static HTML for all routes
5. **Optimize Assets:** Image optimization, minification, compression
6. **Update Search Index:** Push updated content to search service
7. **Deploy to CDN:** Upload static assets to edge locations
8. **Invalidate Cache:** Clear CDN cache for updated pages
9. **Health Check:** Verify deployment with smoke tests

**Deployment Workflow:**
```
[CMS Content Update] → [Webhook] → [GitHub Action Trigger]
                                           ↓
[Git Push to Main] → [Vercel Build Hook] → [Build Process]
                                           ↓
                               [Static Site Generation]
                                           ↓
                        [Deploy to Edge Network (300+ locations)]
                                           ↓
                              [Cache Invalidation]
                                           ↓
                           [Health Check & Smoke Tests]
                                           ↓
                            [Deployment Complete]
```

### 8.4 Infrastructure as Code
**Vercel Configuration (vercel.json):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1", "sfo1", "lhr1"],
  "env": {
    "CMS_API_URL": "@cms-api-url",
    "SEARCH_API_KEY": "@search-api-key"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

**Docker Configuration (if self-hosted CMS):**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
ENV NODE_ENV=production
RUN npm run build
EXPOSE 1337
CMD ["npm", "start"]
```

### 8.5 Rollback Strategy
**Instant Rollback:**
- Vercel maintains deployment history with one-click rollback
- Previous deployment versions remain available for instant reactivation
- DNS remains unchanged, only CDN origin is switched

**Content Rollback:**
- CMS maintains version history for all content
- Editors can revert to previous content versions
- Build can be triggered with specific content version snapshot

### 8.6 Blue-Green Deployment
**Not Required for Static Sites:**
- CDN edge deployment is atomic - new version replaces old instantly
- No downtime during deployments
- Preview deployments allow testing before production

---

## 9. Scalability Strategy

<!-- AI: How the system scales (horizontal, vertical, auto-scaling) -->

### 9.1 Frontend Scalability
**Static Site + CDN Architecture:**
- **Horizontal Scaling:** Automatic via CDN - content replicated to 300+ edge locations globally
- **Edge Caching:** Pages cached at edge locations closest to users (sub-50ms latency)
- **Cache Strategy:**
  - Static pages: 1 year cache with immutable assets
  - HTML pages: 1 hour cache with stale-while-revalidate
  - API responses: 5 minute cache for dynamic content
- **Performance Target:** Handle 10,000+ concurrent users without degradation
- **Traffic Spikes:** CDN automatically absorbs traffic spikes up to 100x normal load

### 9.2 Search Service Scalability
**Managed Search (Algolia):**
- **Horizontal Scaling:** Automatic scaling managed by Algolia infrastructure
- **Distributed Search:** Queries distributed across multiple search clusters
- **Index Replication:** Search index replicated across multiple regions
- **Performance:** Sub-50ms search responses regardless of index size
- **Capacity:** Supports 10,000+ search queries per second

**Self-hosted Search (MeiliSearch):**
- **Vertical Scaling:** Increase instance size (CPU/RAM) for larger indices
- **Horizontal Scaling:** Add read replicas for query distribution
- **Index Optimization:** Compression and efficient data structures for large datasets
- **Capacity:** Single instance handles 1,000+ queries/second, scales with replicas

### 9.3 Serverless Functions Scalability
**Auto-scaling Architecture:**
- **Concurrency:** Each function automatically scales to handle concurrent requests
- **Cold Start Mitigation:** Keep warm instances for frequently used functions
- **Regional Deployment:** Functions deployed in multiple regions for low latency
- **Scaling Limits:**
  - Vercel Functions: 1,000 concurrent executions (default)
  - AWS Lambda: 1,000 concurrent executions per region (adjustable to 100,000+)
- **Performance:** Each function invocation independent, no shared state

### 9.4 CMS Scalability
**Managed CMS (Contentful):**
- **Horizontal Scaling:** Fully managed by Contentful, transparent to users
- **API Rate Limits:** 
  - 78 requests/second for content delivery API
  - 10 requests/second for content management API
- **Content Delivery:** Global CDN for CMS API responses
- **Database:** Managed by Contentful, automatically scaled

**Self-hosted CMS (Strapi):**
- **Vertical Scaling:** Increase container resources (CPU/RAM) for larger content volume
- **Horizontal Scaling:** Deploy multiple Strapi instances behind load balancer
- **Database Scaling:**
  - Read replicas for content delivery API
  - Connection pooling (PgBouncer) for efficient database connections
  - Vertical scaling of PostgreSQL instance (up to 64 CPU, 256GB RAM)
- **Caching Layer:** Redis cache for frequently accessed content
- **Media Storage:** S3 handles unlimited media files with automatic scaling

### 9.5 Database Scalability
**PostgreSQL (if self-hosted CMS):**
- **Read Replicas:** 2-5 read replicas for content delivery queries
- **Write Primary:** Single primary instance for content management writes
- **Connection Pooling:** PgBouncer with 500 max connections
- **Vertical Scaling:** Scale instance up to 64 vCPU, 256GB RAM (AWS RDS)
- **Partitioning:** Table partitioning for large tables (media, content versions)
- **Archival:** Archive old content versions to reduce active dataset size

### 9.6 Media Storage Scalability
**S3 + CloudFront:**
- **Storage:** Unlimited object storage capacity
- **CDN Distribution:** CloudFront edge caching for global delivery
- **Bandwidth:** Automatically scales to handle any traffic volume
- **Optimization:** Image transformation service (Cloudinary/imgix) handles on-demand resizing

### 9.7 Content Scalability Strategy
**Growing Content Volume:**
- **10,000+ Pages:** Static site generation handles large page counts efficiently
- **Incremental Builds:** Only rebuild changed pages (Next.js ISR)
- **Build Optimization:**
  - Parallel page generation (8-16 concurrent builds)
  - Incremental static regeneration for frequently updated pages
  - On-demand revalidation for specific pages
- **Search Indexing:** Batch index updates (100 documents at a time) for efficiency

### 9.8 Scaling Thresholds & Triggers
**Monitoring Thresholds:**
- **Page Load Time > 2 seconds:** Investigate CDN cache hit rates, optimize assets
- **Search Response > 2 seconds:** Scale search service or optimize indices
- **Build Time > 10 minutes:** Implement incremental builds, optimize build process
- **Database CPU > 70%:** Add read replicas or scale instance size
- **CDN Bandwidth > 80% of limit:** Upgrade CDN plan or add additional CDN providers

**Auto-scaling Policies:**
- Serverless functions scale automatically (no manual intervention)
- CDN automatically handles traffic (no limits in typical plans)
- Database auto-scaling based on CPU/memory thresholds (if using managed database)
- Container scaling (if self-hosted CMS) based on CPU > 70% for 5 minutes

---

## 10. Monitoring & Observability

<!-- AI: Logging, metrics, tracing, alerting strategy -->

### 10.1 Application Performance Monitoring (APM)

**Frontend Monitoring:**
- **Real User Monitoring (RUM):** Vercel Analytics or New Relic Browser
  - Core Web Vitals: LCP, FID, CLS tracking
  - Page load times by route
  - JavaScript errors and stack traces
  - User session recordings (optional, Hotjar/FullStory)
- **Metrics Collected:**
  - Time to First Byte (TTFB)
  - First Contentful Paint (FCP)
  - Largest Contentful Paint (LCP) - target: < 2.5s
  - Cumulative Layout Shift (CLS) - target: < 0.1
  - Time to Interactive (TTI)

**Serverless Function Monitoring:**
- **Platform:** Vercel monitoring or AWS CloudWatch (for Lambda)
- **Metrics Collected:**
  - Function invocation count
  - Execution duration (p50, p95, p99)
  - Cold start frequency and duration
  - Error rate and types
  - Memory utilization
  - Concurrent execution count

### 10.2 Infrastructure Monitoring

**CDN Monitoring:**
- **Cloudflare Analytics or Vercel Edge Analytics:**
  - Cache hit rate (target: > 95%)
  - Bandwidth usage
  - Request rate by location
  - Status code distribution
  - Top requested URLs
  - Geographic traffic distribution

**Database Monitoring (if self-hosted):**
- **Tools:** PostgreSQL native monitoring + DataDog/CloudWatch
- **Metrics:**
  - Query performance (slow query log for queries > 1s)
  - Connection pool utilization
  - Database size and growth rate
  - Replication lag (for read replicas)
  - CPU and memory utilization

**Search Service Monitoring:**
- **Algolia Dashboard or MeiliSearch metrics:**
  - Search queries per second
  - Average search response time
  - Search success rate (queries returning results)
  - Top search queries
  - Zero-result search queries
  - Index size and update frequency

### 10.3 Logging Strategy

**Structured Logging:**
- **Format:** JSON-structured logs for machine parsing
- **Log Levels:** ERROR, WARN, INFO, DEBUG
- **Log Aggregation:** Vercel logs, AWS CloudWatch Logs, or DataDog

**Application Logs:**
- Serverless function execution logs
- CMS API request logs
- Build process logs
- Search query logs (anonymized)

**Log Retention:**
- Error logs: 90 days
- Access logs: 30 days
- Debug logs: 7 days
- Compliance/audit logs: 1 year (if required)

### 10.4 Error Tracking

**Error Monitoring Tool:** Sentry or Rollbar
- **Frontend Errors:**
  - JavaScript exceptions with stack traces
  - Network request failures
  - Resource loading errors (images, scripts)
  - Console errors and warnings
- **Backend Errors:**
  - Serverless function exceptions
  - API integration failures
  - Database connection errors
  - CMS API timeouts

**Error Context:**
- User agent and browser version
- URL and route
- User actions leading to error (breadcrumbs)
- Request payload (sanitized)
- Environment variables (non-sensitive)

### 10.5 Uptime Monitoring

**Synthetic Monitoring:** Pingdom, UptimeRobot, or Better Uptime
- **Endpoints Monitored:**
  - Homepage: www.pensencyclopedia.com (every 1 minute)
  - Key article pages (every 5 minutes)
  - Search API endpoint (every 5 minutes)
  - CMS API health check (every 5 minutes)

**Health Check Endpoints:**
- `/api/health` - returns 200 OK with system status
- `/api/search/health` - verifies search service connectivity
- CMS admin health endpoint

**SLA Targets:**
- Uptime: 99.5% (target from PRD)
- Maximum consecutive downtime: 10 minutes
- Response time: < 2 seconds for 95% of requests

### 10.6 Alerting Strategy

**Critical Alerts (Immediate Response - PagerDuty/Opsgenie):**
- Website down (returning 5xx errors) for > 2 minutes
- Build failures for > 3 consecutive attempts
- Database down or unreachable
- CDN/origin connectivity issues
- Error rate > 5% of requests for > 5 minutes

**Warning Alerts (Email/Slack - 15 minute response):**
- Page load time > 3 seconds (p95) for > 10 minutes
- Search response time > 2 seconds for > 10 minutes
- CDN cache hit rate < 90% for > 30 minutes
- Database CPU > 80% for > 15 minutes
- Build time > 15 minutes
- Disk space > 80% (if self-hosted)

**Informational Alerts (Email/Slack - next business day):**
- Daily traffic summary
- New content published
- Search zero-result rate > 20%
- Unusual traffic patterns detected
- Weekly performance report

### 10.7 Observability Dashboards

**Operations Dashboard:**
- Real-time request rate and latency
- Error rate by service
- CDN cache performance
- Active serverless function invocations
- Current uptime status

**Business Metrics Dashboard:**
- Daily/weekly/monthly traffic
- Top articles by views
- Search queries and popular terms
- User engagement metrics (session duration, pages per session)
- Geographic traffic distribution
- Traffic sources (referrals, search engines, direct)

**Performance Dashboard:**
- Core Web Vitals trends
- Page load time percentiles (p50, p75, p95)
- Build time trends
- Search performance metrics
- Database query performance

### 10.8 Distributed Tracing

**Not Required for Initial Version:**
- Static site architecture has minimal distributed transactions
- Most requests served directly from CDN
- Simple request flows don't warrant complex tracing

**Future Consideration:**
- Implement distributed tracing if adding complex serverless workflows
- Use OpenTelemetry or AWS X-Ray for request tracing
- Trace search queries through multiple services

---

## 11. Architectural Decisions (ADRs)

<!-- AI: Key architectural decisions with rationale -->

### ADR-001: Static Site Generation with Jamstack Architecture

**Status:** Accepted

**Context:**
The website is content-focused with minimal dynamic functionality, requiring excellent performance, SEO, and scalability for 10,000+ pages of content.

**Decision:**
Adopt Jamstack architecture with static site generation (Next.js SSG) and headless CMS, deployed to global CDN.

**Rationale:**
- Pre-rendered HTML provides sub-second page loads (meets < 2s requirement)
- CDN distribution scales automatically to handle traffic spikes (10x normal load)
- Minimal server infrastructure reduces costs and operational complexity
- Excellent SEO through server-side rendering
- Strong security posture with reduced attack surface (no live database queries)
- Aligns with non-functional requirement for 99.5% uptime

**Consequences:**
- Positive: Exceptional performance, automatic scaling, low operational overhead
- Positive: Strong security and reliability
- Negative: Content updates require build process (1-5 minute delay)
- Mitigation: Incremental Static Regeneration for time-sensitive updates

---

### ADR-002: Headless CMS over Traditional CMS

**Status:** Accepted

**Context:**
Need content management capabilities for editorial team without coupling content to presentation layer.

**Decision:**
Use headless CMS (Strapi or Contentful) instead of traditional CMS (WordPress with theme).

**Rationale:**
- Decouples content from presentation, allowing flexible frontend technology choices
- API-first approach enables future mobile apps or alternative frontends
- Better performance through static site generation
- Improved security (no PHP vulnerabilities, admin interface separate from public site)
- Modern editorial experience for content team
- Supports structured content modeling for complex pen specifications

**Consequences:**
- Positive: Flexibility, performance, security, modern content workflows
- Positive: Easy integration with build process and search services
- Negative: More complex initial setup than traditional CMS
- Negative: Content preview requires integration with Next.js preview mode

---

### ADR-003: Managed Search Service (Algolia) over Self-hosted

**Status:** Accepted

**Context:**
Search functionality is critical (20% of users expected to use search), requiring sub-2-second response times with typo tolerance.

**Decision:**
Use managed search service (Algolia) rather than self-hosted solution (Elasticsearch, MeiliSearch).

**Rationale:**
- Sub-50ms search response times meet performance requirements
- Typo tolerance and relevance ranking out-of-the-box
- Zero maintenance overhead (no servers to manage)
- Automatic scaling for traffic spikes
- Search analytics included
- Generous free tier (10k searches/month, suitable for MVP)

**Consequences:**
- Positive: Excellent performance, zero maintenance, quick implementation
- Positive: Advanced features (faceting, filtering, highlighting) included
- Negative: Cost scales with usage (potential future expense)
- Negative: Vendor lock-in for search infrastructure
- Mitigation: Abstract search interface to allow future migration if needed

---

### ADR-004: Next.js over Gatsby for Static Site Generation

**Status:** Accepted

**Context:**
Need robust static site generator with good performance, large ecosystem, and support for incremental adoption of dynamic features.

**Decision:**
Use Next.js 14+ with Static Site Generation over Gatsby or other SSG options.

**Rationale:**
- Hybrid rendering: SSG for most pages, ISR for time-sensitive content, SSR if needed later
- Better build performance for large sites (parallel builds, incremental compilation)
- Strong commercial backing (Vercel) ensures long-term maintenance
- Excellent image optimization built-in (Next.js Image component)
- API routes for serverless functions within same codebase
- Larger ecosystem and community support
- Easier learning curve for developers familiar with React

**Consequences:**
- Positive: Flexibility for future dynamic features without architectural changes
- Positive: Excellent developer experience and tooling
- Positive: Strong performance optimization features
- Negative: Slightly more complex than pure SSG options
- Negative: Vercel-optimized (but works with other hosts)

---

### ADR-005: Vercel for Hosting over AWS or Self-hosted

**Status:** Accepted

**Context:**
Need reliable hosting with global CDN, automatic HTTPS, CI/CD integration, and minimal operational overhead.

**Decision:**
Deploy on Vercel platform rather than AWS infrastructure or traditional hosting.

**Rationale:**
- Zero-config deployments for Next.js applications
- Global edge network (300+ locations) included
- Automatic HTTPS and SSL certificates
- Built-in preview deployments for every commit
- Serverless functions integrated seamlessly
- Generous free tier, predictable pricing
- Git integration for automatic deployments
- Meets 99.5% uptime SLA requirement

**Consequences:**
- Positive: Minimal DevOps overhead, fast deployment
- Positive: Excellent developer experience (preview deployments, instant rollbacks)
- Positive: Cost-effective for expected traffic volume
- Negative: Platform lock-in (though Next.js is portable)
- Negative: Less control over infrastructure details
- Mitigation: Next.js applications are portable; migration path exists if needed

---

### ADR-006: No User Authentication in Initial Version

**Status:** Accepted

**Context:**
PRD explicitly excludes user accounts, authentication, and personalization features.

**Decision:**
Do not implement user authentication, registration, or personalized features in initial version.

**Rationale:**
- Aligns with PRD non-goals (no user accounts, no social networking)
- Reduces complexity and security surface area
- Faster time to market
- Lower operational overhead (no user data privacy concerns)
- All content is public, no access control needed

**Consequences:**
- Positive: Simpler architecture, faster development
- Positive: No GDPR/privacy compliance for user accounts
- Positive: Lower security risk (no user credentials to protect)
- Negative: Cannot offer personalized experiences or user-generated content
- Negative: Future addition of authentication requires architectural changes
- Note: Can add authentication later if business requirements change

---

### ADR-007: Structured Content Model over Free-form CMS

**Status:** Accepted

**Context:**
Content includes complex structured data (pen specifications, comparisons, brands) requiring consistent formatting.

**Decision:**
Define strict content models in CMS for entities (Article, PenModel, Brand, etc.) rather than free-form pages.

**Rationale:**
- Ensures consistent data structure for comparison features
- Enables structured data markup for SEO (schema.org)
- Facilitates search indexing with proper faceting
- Supports data validation at entry time
- Enables reuse of content across pages (e.g., pen specs shown in multiple contexts)
- Better content governance and quality control

**Consequences:**
- Positive: Consistent data structure, better SEO, enables advanced features
- Positive: Content validation prevents errors
- Negative: Less flexibility for content editors
- Negative: Requires upfront content modeling effort
- Mitigation: Provide "flexible content" field for unstructured information where needed

---

### ADR-008: Client-side Search over Server-side Search

**Status:** Accepted

**Context:**
Search functionality needs to be fast (< 2s) and cost-effective.

**Decision:**
Implement search with client-side JavaScript calling search API directly, rather than proxying through backend.

**Rationale:**
- Reduces latency (no backend proxy hop)
- Lower costs (direct API calls to search service)
- Simpler architecture (fewer moving parts)
- Better user experience (instant search results as user types)
- Search service (Algolia) provides secure public API keys with rate limiting

**Consequences:**
- Positive: Faster search experience, lower latency
- Positive: Simpler backend (no search proxy needed)
- Negative: Search API key exposed in client code
- Mitigation: Use rate-limited public API key, monitor for abuse
- Negative: Slightly higher client-side JavaScript payload
- Mitigation: Lazy load search components on first interaction

---

### ADR-009: Image CDN for Media Optimization

**Status:** Accepted

**Context:**
Website will feature high-quality pen images requiring fast loading without sacrificing quality, with zoom functionality.

**Decision:**
Use dedicated image CDN (Cloudinary or imgix) for media storage and optimization rather than self-hosted solution.

**Rationale:**
- Automatic format conversion (WebP, AVIF) based on browser support
- On-demand image transformations (resize, crop, quality adjustment)
- Global CDN for fast delivery
- Lazy loading support
- Zoom functionality through high-resolution source images
- Reduces build time (no need to generate multiple image sizes at build)

**Consequences:**
- Positive: Excellent image performance and loading speed
- Positive: Reduces build complexity and time
- Positive: Automatic optimization for different devices
- Negative: Additional service dependency
- Negative: Cost scales with image transformations and bandwidth
- Mitigation: Generous free tiers available, cost predictable based on traffic

---

### ADR-010: No E-commerce Integration in Architecture

**Status:** Accepted

**Context:**
PRD explicitly excludes e-commerce functionality, shopping carts, and checkout processes.

**Decision:**
Do not architect for or include any e-commerce capabilities in system design.

**Rationale:**
- Aligns with PRD non-goals
- Significant complexity reduction
- No PCI compliance requirements
- No payment gateway integration needed
- No inventory management systems
- Faster time to market for information-focused site

**Consequences:**
- Positive: Much simpler architecture and development
- Positive: Lower costs (no payment processing fees, no inventory systems)
- Positive: Reduced security concerns (no payment data)
- Negative: Cannot generate revenue through direct sales
- Negative: Adding e-commerce later requires significant architectural changes
- Note: External links to retailers could be added without architectural changes

---

## Appendix: PRD Reference

# Product Requirements Document: I want a website all about Pens

**Created:** 2026-02-02T23:28:53Z
**Status:** Draft

## 1. Overview

**Concept:** I want a website all about Pens

**Description:** I want a website all about Pens

---

## 2. Goals

<!-- AI: Based on the concept and clarification Q&A, list 3-5 primary goals. Each goal should be specific and measurable. -->

- Create a comprehensive information hub about pens, covering different types, brands, and uses
- Provide educational content to help users understand pen mechanics, materials, and history
- Build an engaging platform where pen enthusiasts can discover and learn about writing instruments
- Establish a resource library with detailed guides, comparisons, and reviews of various pen types
- Foster user engagement through informative content that drives repeat visits

---

## 3. Non-Goals

<!-- AI: List 3-5 explicit non-goals to set boundaries. -->

- E-commerce functionality or direct pen sales
- User authentication or account management systems
- Social networking features (user profiles, messaging, following)
- Mobile application development (initial version)
- Integration with third-party inventory or shopping platforms

---

## 4. User Stories

<!-- AI: Generate 5-10 user stories in the format: "As a [user type], I want [goal] so that [benefit]" -->

- As a pen enthusiast, I want to browse different categories of pens so that I can learn about types I'm unfamiliar with
- As a beginner, I want to read introductory guides about pens so that I can understand the basics of writing instruments
- As a collector, I want to view detailed specifications and history of specific pen models so that I can make informed decisions
- As a student, I want to compare different pen types (ballpoint, rollerball, fountain) so that I can choose the best pen for my needs
- As a professional, I want to learn about luxury and business pens so that I can find appropriate writing instruments for my work
- As a casual visitor, I want to search for specific pen brands or models so that I can quickly find relevant information
- As an artist, I want to discover specialty pens and their applications so that I can expand my creative toolkit
- As a history buff, I want to read about the evolution of pens so that I can appreciate their cultural significance
- As a researcher, I want to access organized content by categories so that I can efficiently navigate the site

---

## 5. Acceptance Criteria

<!-- AI: For each major user story, define acceptance criteria in Given/When/Then format -->

**Browse Pen Categories:**
- Given I am on the homepage, When I click on a category (e.g., "Fountain Pens"), Then I should see a list of relevant articles and guides
- Given I am viewing a category, When the page loads, Then I should see at least 5-10 items organized clearly
- Given I am browsing categories, When I select a subcategory, Then the content should filter appropriately

**Read Educational Content:**
- Given I am viewing an article, When the page loads, Then I should see well-formatted text with headings, images, and structured content
- Given I am reading a guide, When I scroll through the content, Then images and diagrams should load properly
- Given I am on a guide page, When I finish reading, Then I should see related articles or suggested next reads

**Search Functionality:**
- Given I am on any page, When I enter a search term in the search box, Then I should see relevant results within 2 seconds
- Given I have searched for a term, When results are displayed, Then they should be ranked by relevance
- Given I search for a specific brand or model, When matches exist, Then they should appear at the top of results

**Compare Pen Types:**
- Given I want to compare pens, When I access the comparison section, Then I should see side-by-side specifications
- Given I am viewing a comparison, When the data loads, Then key differences should be clearly highlighted
- Given I am comparing items, When I select different pens, Then the comparison should update dynamically

---

## 6. Functional Requirements

<!-- AI: List specific functional requirements (FR-001, FR-002, etc.) -->

**FR-001:** The website shall display a homepage with featured pen content and category navigation
**FR-002:** The system shall provide categorized browsing by pen type (fountain, ballpoint, rollerball, gel, specialty)
**FR-003:** The website shall include detailed article pages with text, images, and specifications
**FR-004:** The system shall implement a search function that queries across all content
**FR-005:** The website shall display brand profiles with history and notable models
**FR-006:** The system shall provide comparison pages showing specifications side-by-side
**FR-007:** The website shall include a glossary of pen-related terminology
**FR-008:** The system shall organize content with tags and categories for easy navigation
**FR-009:** The website shall display high-quality images of pens with zoom capability
**FR-010:** The system shall provide internal linking between related articles and topics
**FR-011:** The website shall include a navigation menu accessible from all pages
**FR-012:** The system shall display breadcrumb navigation showing the user's current location

---

## 7. Non-Functional Requirements

### Performance
- Page load time shall not exceed 2 seconds on standard broadband connections
- Images shall be optimized to load within 1 second without sacrificing quality
- Search results shall return within 2 seconds for any query
- The website shall support at least 1,000 concurrent users without performance degradation
- Static assets shall be cached to improve repeat visit performance

### Security
- All pages shall be served over HTTPS
- The website shall implement basic security headers (CSP, X-Frame-Options, etc.)
- User input in search functionality shall be sanitized to prevent XSS attacks
- The system shall protect against common web vulnerabilities (OWASP Top 10)
- Regular security updates shall be applied to all dependencies and frameworks

### Scalability
- The website architecture shall support scaling to 10,000+ pages of content
- The system shall handle traffic spikes of up to 10x normal load
- Content management shall support addition of 50+ new articles per month
- The database structure shall accommodate growing content without performance loss

### Reliability
- The website shall maintain 99.5% uptime
- The system shall implement automated backups daily
- Error pages shall provide helpful information and navigation options
- The website shall gracefully handle missing images or broken links
- Monitoring shall alert administrators of critical failures within 5 minutes

---

## 8. Dependencies

<!-- AI: List external systems, APIs, libraries this project depends on -->

- **Web Hosting Service:** Cloud hosting platform (e.g., AWS, Netlify, Vercel) for deploying the website
- **Content Management System:** CMS platform (e.g., WordPress, Strapi, or static site generator like Hugo/Jekyll)
- **Image Optimization Service:** CDN or image optimization service for efficient media delivery
- **Search Engine:** Search library or service (e.g., Algolia, ElasticSearch, or built-in CMS search)
- **Domain Registration:** Domain registrar for website URL
- **Analytics Platform:** Web analytics tool (e.g., Google Analytics, Plausible) for tracking usage
- **SSL Certificate:** SSL/TLS certificate provider for HTTPS encryption
- **Frontend Framework:** Modern web framework (React, Vue, or vanilla HTML/CSS/JS)

---

## 9. Out of Scope

<!-- AI: Based on non-goals and clarification, explicitly state what is NOT included -->

- Online shopping cart or checkout functionality
- User registration, login, or personalized accounts
- Community features such as forums, comments, or user-generated content
- Social media integration beyond basic share buttons
- Newsletter subscription or email marketing automation
- Mobile native applications (iOS/Android)
- Real-time inventory tracking or price monitoring
- Affiliate marketing links or monetization features
- Multi-language support (initial version will be English-only)
- Interactive tools like pen customization or design simulators
- Video hosting or streaming content
- Integration with retail point-of-sale systems

---

## 10. Success Metrics

<!-- AI: Define measurable success criteria -->

- **Traffic:** Achieve 5,000 unique monthly visitors within 6 months of launch
- **Engagement:** Average session duration of at least 3 minutes
- **Content Coverage:** Publish at least 50 comprehensive articles across all major pen categories
- **Search Effectiveness:** Search feature used by at least 20% of visitors
- **Bounce Rate:** Maintain bounce rate below 60%
- **Page Views:** Average 3+ pages per session
- **Return Visitors:** Achieve 30% returning visitor rate within 1 year
- **Load Performance:** 95% of pages load within 2 seconds
- **Content Quality:** Maintain average page read depth of 50% or higher
- **SEO Performance:** Rank in top 10 Google results for at least 10 pen-related keywords within 1 year

---

## Appendix: Clarification Q&A

### Clarification Questions & Answers


### LLD
# Low-Level Design: aiworkshop (Continued)

## 10. Migration Strategy (Continued)

### 10.5 Environment Variables Migration (Continued)

**File**: `cms/.env.example`

```bash
# Database
DATABASE_CLIENT=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=strapi_cms
DATABASE_USERNAME=strapi_user
DATABASE_PASSWORD=your_password_here
DATABASE_SSL=false

# Application
HOST=0.0.0.0
PORT=1337
APP_KEYS=key1,key2,key3,key4
API_TOKEN_SALT=your_token_salt
ADMIN_JWT_SECRET=your_admin_secret
TRANSFER_TOKEN_SALT=your_transfer_salt
JWT_SECRET=your_jwt_secret

# Deployment
NODE_ENV=development

# Webhooks
VERCEL_DEPLOY_HOOK=https://api.vercel.com/v1/integrations/deploy/...
REVALIDATION_SECRET=your_secret_here

# Cloudinary (if using for CMS uploads)
CLOUDINARY_NAME=your_cloud_name
CLOUDINARY_KEY=your_api_key
CLOUDINARY_SECRET=your_api_secret
```

### 10.6 Deployment Migration Steps

**Step 1: Deploy Strapi CMS**

```bash
# Option A: Deploy to Railway/Render
# 1. Create new PostgreSQL database on platform
# 2. Set environment variables in platform dashboard
# 3. Connect GitHub repository
# 4. Deploy from cms/ directory

# Option B: Deploy to AWS ECS with Docker
cd docker
docker build -f cms.Dockerfile -t strapi-cms ../cms
docker tag strapi-cms:latest your-registry/strapi-cms:latest
docker push your-registry/strapi-cms:latest

# Deploy to ECS using AWS CLI or console
```

**Step 2: Deploy Frontend to Vercel**

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Link project
vercel link

# Set environment variables
vercel env add NEXT_PUBLIC_STRAPI_URL
vercel env add STRAPI_API_TOKEN
# ... add all environment variables

# Deploy
vercel --prod
```

**Step 3: Configure DNS**

```bash
# Point domain to Vercel
# Add CNAME record: www.pensencyclopedia.com -> cname.vercel-dns.com

# Configure SSL (automatic with Vercel)
```

### 10.7 Migration Checklist

- [ ] Create frontend and cms directories
- [ ] Initialize Next.js application
- [ ] Initialize Strapi CMS
- [ ] Set up PostgreSQL database
- [ ] Run database migrations
- [ ] Configure environment variables
- [ ] Set up Cloudinary account and integration
- [ ] Set up Algolia account and create index
- [ ] Seed sample content data
- [ ] Test local development environment
- [ ] Deploy Strapi CMS to hosting platform
- [ ] Deploy frontend to Vercel
- [ ] Configure DNS and SSL
- [ ] Set up webhooks between CMS and frontend
- [ ] Configure monitoring (Sentry, analytics)
- [ ] Run E2E tests against production
- [ ] Update repository README

---

## 11. Rollback Plan

### 11.1 Rollback Strategy Overview

**Deployment Rollback**: Instant rollback to previous version
**Database Rollback**: Restore from backup or run down migrations
**Content Rollback**: Revert to previous content version in CMS

### 11.2 Frontend Rollback

**Vercel Instant Rollback**:

```bash
# List recent deployments
vercel ls

# Promote previous deployment to production
vercel promote <deployment-url>

# Or rollback via Vercel dashboard
# 1. Go to Deployments
# 2. Find previous working deployment
# 3. Click "Promote to Production"
```

**Rollback Time**: < 1 minute

### 11.3 CMS Rollback

**Docker-based Rollback**:

```bash
# Rollback to previous Docker image
docker pull your-registry/strapi-cms:previous-tag
docker stop strapi-cms
docker rm strapi-cms
docker run -d --name strapi-cms your-registry/strapi-cms:previous-tag

# Or use orchestration platform (ECS, Kubernetes)
kubectl rollout undo deployment/strapi-cms
```

**Rollback Time**: 2-5 minutes

### 11.4 Database Rollback

**File**: `cms/database/migrations/down/001_rollback_initial.sql`

```sql
-- Rollback initial schema migration

DROP TRIGGER IF EXISTS articles_search_update ON articles;
DROP TRIGGER IF EXISTS brands_search_update ON brands;

DROP FUNCTION IF EXISTS articles_search_trigger();
DROP FUNCTION IF EXISTS brands_search_trigger();

DROP INDEX IF EXISTS idx_articles_search;
DROP INDEX IF EXISTS idx_brands_search;

DROP TABLE IF EXISTS articles_related_links;
DROP TABLE IF EXISTS articles_tags_links;
DROP TABLE IF EXISTS pen_models_related_links;
DROP TABLE IF EXISTS pen_models_images_links;
DROP TABLE IF EXISTS glossary_terms_related_links;

DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS pen_types;
DROP TABLE IF EXISTS pen_models;
DROP TABLE IF EXISTS components_pen_specifications;
DROP TABLE IF EXISTS glossary_terms;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS components_seo_metadata;
```

**Database Restore from Backup**:

```bash
# Restore from automated backup
pg_restore -U strapi_user -d strapi_cms backup_file.dump

# Or restore from specific timestamp
# (if using continuous archiving/PITR)
```

**Rollback Time**: 5-15 minutes

### 11.5 Content Rollback

**Strapi Version History**:

```javascript
// Use Strapi's version history to revert content
// 1. Navigate to Content Manager
// 2. Select content item
// 3. Click "Version History"
// 4. Select previous version
// 5. Click "Restore"
```

**Bulk Content Rollback**:

```bash
# Restore from database backup to specific point in time
pg_dump -U strapi_user strapi_cms > backup_before_changes.sql

# If changes were problematic, restore:
dropdb -U strapi_user strapi_cms
createdb -U strapi_user strapi_cms
psql -U strapi_user strapi_cms < backup_before_changes.sql
```

### 11.6 Search Index Rollback

**File**: `scripts/rollback-search-index.js`

```javascript
const { getSearchIndex } = require('../frontend/src/lib/algolia');

async function rollbackSearchIndex(backupIndexName) {
  const adminClient = algoliasearch(
    process.env.ALGOLIA_APP_ID,
    process.env.ALGOLIA_ADMIN_KEY
  );
  
  const sourceIndex = adminClient.initIndex(backupIndexName);
  const targetIndex = adminClient.initIndex(process.env.ALGOLIA_INDEX_NAME);
  
  // Copy backup index to main index
  await sourceIndex.copyTo(targetIndex.indexName, [
    'settings',
    'synonyms',
    'rules'
  ]);
  
  console.log(`Search index rolled back from ${backupIndexName}`);
}

// Usage: node scripts/rollback-search-index.js pens_backup_20260202
rollbackSearchIndex(process.argv[2]);
```

### 11.7 Rollback Decision Matrix

| Issue | Rollback Action | Estimated Time |
|-------|----------------|----------------|
| Frontend bug | Vercel instant rollback | < 1 min |
| CMS API error | Container/image rollback | 2-5 min |
| Database corruption | Restore from backup | 5-15 min |
| Bad content publish | CMS version history | 1-2 min |
| Search index issues | Rollback to backup index | 2-3 min |
| Complete system failure | Full rollback (all layers) | 10-20 min |

### 11.8 Rollback Testing

**File**: `tests/rollback/test-rollback.sh`

```bash
#!/bin/bash

# Test rollback procedures in staging environment

echo "Testing frontend rollback..."
vercel ls --scope staging
PREVIOUS_DEPLOYMENT=$(vercel ls --scope staging | sed -n '2p' | awk '{print $1}')
vercel promote $PREVIOUS_DEPLOYMENT --scope staging

echo "Testing database rollback..."
pg_dump -U strapi_user strapi_cms_staging > /tmp/test_backup.sql
# Make test changes
psql -U strapi_user strapi_cms_staging < /tmp/test_backup.sql

echo "Rollback tests completed"
```

---

## 12. Performance Considerations

### 12.1 Frontend Performance Optimizations

**Static Generation with ISR**:

```typescript
// frontend/src/app/articles/[slug]/page.tsx

// Revalidate every hour for frequently updated content
export const revalidate = 3600;

// Pre-generate top 100 articles at build time
export async function generateStaticParams() {
  const response = await getArticles({}, { page: 1, pageSize: 100 });
  return response.data.map((article) => ({ slug: article.attributes.slug }));
}
```

**Image Optimization**:

```typescript
// frontend/next.config.js

module.exports = {
  images: {
    domains: ['res.cloudinary.com', process.env.NEXT_PUBLIC_STRAPI_URL],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 31536000, // 1 year
  },
};
```

**Code Splitting**:

```typescript
// Lazy load heavy components
const ComparisonTable = dynamic(() => import('@/components/comparison/ComparisonTable'), {
  loading: () => <Spinner />,
  ssr: false, // Client-side only for interactive features
});

const ImageGallery = dynamic(() => import('@/components/content/ImageGallery'), {
  loading: () => <div className="h-96 bg-gray-100 animate-pulse" />,
});
```

**Font Optimization**:

```typescript
// frontend/src/app/layout.tsx

import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

### 12.2 Database Performance

**Indexing Strategy**:

```sql
-- Composite indexes for common queries
CREATE INDEX idx_articles_category_published 
  ON articles(category_id, published_date DESC) 
  WHERE published_at IS NOT NULL;

CREATE INDEX idx_pen_models_brand_type_price 
  ON pen_models(brand_id, pen_type_id, price) 
  WHERE published_at IS NOT NULL;

-- Partial indexes for specific queries
CREATE INDEX idx_articles_published 
  ON articles(published_date DESC) 
  WHERE published_at IS NOT NULL;

-- Full-text search indexes
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);
```

**Query Optimization**:

```javascript
// cms/src/api/article/services/article.js

module.exports = createCoreService('api::article.article', ({ strapi }) => ({
  async findWithRelations(slug) {
    // Optimized query with specific field selection
    return strapi.db.query('api::article.article').findOne({
      where: { slug },
      select: ['id', 'title', 'content', 'excerpt', 'publishedDate'],
      populate: {
        category: { select: ['id', 'name', 'slug'] },
        tags: { select: ['id', 'name', 'slug'] },
        featuredImage: { select: ['id', 'url', 'alternativeText', 'width', 'height'] },
        relatedArticles: {
          select: ['id', 'title', 'slug', 'excerpt'],
          populate: { featuredImage: true },
          limit: 3,
        },
      },
    });
  },
}));
```

**Connection Pooling**:

```javascript
// cms/config/database.js

module.exports = ({ env }) => ({
  connection: {
    client: 'postgres',
    connection: {
      host: env('DATABASE_HOST'),
      port: env.int('DATABASE_PORT'),
      database: env('DATABASE_NAME'),
      user: env('DATABASE_USERNAME'),
      password: env('DATABASE_PASSWORD'),
      ssl: env.bool('DATABASE_SSL', false),
    },
    pool: {
      min: 2,
      max: 10,
      acquireTimeoutMillis: 30000,
      idleTimeoutMillis: 30000,
    },
    debug: false,
  },
});
```

### 12.3 Caching Strategy

**Multi-layer Caching**:

```typescript
// Layer 1: CDN Edge Cache (Vercel/Cloudflare)
// - Static pages: 1 year with immutable assets
// - HTML: 1 hour with stale-while-revalidate

// Layer 2: Next.js Data Cache
export async function getArticleBySlug(slug: string) {
  return fetchFromStrapi({
    endpoint: 'articles',
    query: { filters: { slug: { $eq: slug } } },
    next: {
      revalidate: 3600, // 1 hour cache
      tags: [`article-${slug}`], // For targeted revalidation
    },
  });
}

// Layer 3: Strapi Response Cache (Redis)
// cms/config/plugins.js
module.exports = {
  'rest-cache': {
    enabled: true,
    config: {
      provider: {
        name: 'redis',
        options: {
          max: 32767,
          connection: process.env.REDIS_URL,
        },
      },
      strategy: {
        contentTypes: [
          {
            contentType: 'api::article.article',
            maxAge: 3600000, // 1 hour
          },
        ],
      },
    },
  },
};
```

**Cache Headers**:

```typescript
// frontend/src/middleware.ts

import { NextResponse } from 'next/server';

export function middleware(request) {
  const response = NextResponse.next();
  
  // Static assets - long cache
  if (request.nextUrl.pathname.startsWith('/_next/static')) {
    response.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
  }
  
  // HTML pages - short cache with revalidation
  else if (!request.nextUrl.pathname.startsWith('/api')) {
    response.headers.set(
      'Cache-Control',
      'public, s-maxage=3600, stale-while-revalidate=86400'
    );
  }
  
  return response;
}
```

### 12.4 Search Performance

**Search Index Optimization**:

```javascript
// scripts/optimize-search-index.js

const { getSearchIndex } = require('../frontend/src/lib/algolia');

async function optimizeSearchIndex() {
  const index = getSearchIndex();
  
  await index.setSettings({
    // Optimize searchable attributes
    searchableAttributes: [
      'unordered(title)',     // Exact matches in title boost ranking
      'unordered(tags)',
      'unordered(category)',
      'content',              // Lower priority for content text
    ],
    
    // Custom ranking for relevance
    customRanking: [
      'desc(publishedDate)',
      'desc(relevanceScore)',
    ],
    
    // Faceting for filters
    attributesForFaceting: [
      'filterOnly(type)',     // Use filterOnly for non-displayed facets
      'searchable(category)', // Allow searching within facets
      'searchable(tags)',
      'brand',
    ],
    
    // Optimize for typos
    typoTolerance: true,
    minWordSizefor1Typo: 4,
    minWordSizefor2Typos: 8,
    
    // Highlighting
    attributesToHighlight: ['title', 'excerpt'],
    highlightPreTag: '<mark>',
    highlightPostTag: '</mark>',
    
    // Pagination
    hitsPerPage: 20,
    maxValuesPerFacet: 100,
    
    // Performance
    removeWordsIfNoResults: 'lastWords',
  });
}
```

### 12.5 Build Performance

**Parallel Static Generation**:

```javascript
// frontend/next.config.js

module.exports = {
  // Experimental features for build performance
  experimental: {
    workerThreads: true,
    cpus: 4, // Use 4 CPU cores for parallel builds
  },
  
  // Optimize build output
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Webpack optimizations
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
        },
      };
    }
    return config;
  },
};
```

**Incremental Builds**:

```yaml
# .github/workflows/deploy-frontend.yml

name: Deploy Frontend
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
        env:
          NEXT_PUBLIC_STRAPI_URL: ${{ secrets.STRAPI_URL }}
          # Enable experimental build cache
          NEXT_EXPERIMENTAL_BUILD_CACHE: 1
```

### 12.6 Runtime Performance Monitoring

**File**: `frontend/src/lib/performance.ts`

```typescript
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

export function reportWebVitals() {
  onCLS((metric) => sendToAnalytics('CLS', metric.value));
  onFID((metric) => sendToAnalytics('FID', metric.value));
  onLCP((metric) => sendToAnalytics('LCP', metric.value));
  onFCP((metric) => sendToAnalytics('FCP', metric.value));
  onTTFB((metric) => sendToAnalytics('TTFB', metric.value));
}

function sendToAnalytics(metric: string, value: number) {
  // Send to analytics service
  if (window.gtag) {
    window.gtag('event', metric, {
      value: Math.round(metric === 'CLS' ? value * 1000 : value),
      event_category: 'Web Vitals',
      non_interaction: true,
    });
  }
  
  // Also send to custom monitoring
  fetch('/api/analytics/web-vitals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metric, value }),
  });
}
```

### 12.7 Performance Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| First Contentful Paint (FCP) | < 1.0s | TBD |
| Largest Contentful Paint (LCP) | < 2.5s | TBD |
| Time to Interactive (TTI) | < 3.0s | TBD |
| Cumulative Layout Shift (CLS) | < 0.1 | TBD |
| First Input Delay (FID) | < 100ms | TBD |
| Total Blocking Time (TBT) | < 200ms | TBD |
| Build Time (10,000 pages) | < 15 min | TBD |
| Search Response Time (p95) | < 200ms | TBD |
| API Response Time (p95) | < 500ms | TBD |

---

## Appendix: Existing Repository Structure

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
  plans/
    health-check/
      HLD.md
      LLD.md
      PRD.md
    test-website/
      HLD.md
      PRD.md
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
