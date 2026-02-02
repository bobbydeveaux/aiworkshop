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
