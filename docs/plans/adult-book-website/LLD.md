```typescript
// src/components/book/BookCover.tsx
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';

export const BookCover: React.FC<{ src: string; alt: string }> = ({ src, alt }) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const isVisible = useIntersectionObserver(imgRef, { rootMargin: '50px' });
  const [imageSrc, setImageSrc] = useState<string>('');
  const [error, setError] = useState(false);
  
  useEffect(() => {
    if (isVisible && !imageSrc) {
      setImageSrc(src);
    }
  }, [isVisible, src, imageSrc]);
  
  return (
    <img
      ref={imgRef}
      src={error ? '/images/placeholder-book.png' : imageSrc || '/images/placeholder-book.png'}
      alt={alt}
      onError={() => setError(true)}
      loading="lazy"
    />
  );
};
```

**Data Lazy Loading:**

```typescript
// src/services/BookService.ts
public async getBooks(page: number, limit: number): Promise<Book[]> {
  const chunkNumber = Math.ceil((page * limit) / 1000);
  const chunkId = `books-${String(chunkNumber).padStart(3, '0')}`;
  
  // Only load chunk if not already loaded
  if (!this.loadedChunks.has(chunkId)) {
    const chunkData = await this.dataLoader.loadJSON<BookChunk>(
      `/data/books/${chunkId}.json`
    );
    
    chunkData.books.forEach(book => {
      this.bookCache.set(book.id, book);
    });
    
    this.loadedChunks.add(chunkId);
  }
  
  // Return requested page from cache
  const start = ((page - 1) * limit) % 1000;
  const books = Array.from(this.bookCache.values()).slice(start, start + limit);
  
  return books;
}
```

---

### Local Storage Performance

**Storage Quota Management:**

```typescript
// src/services/StorageService.ts
public getStorageUsage(): { used: number; quota: number } {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    navigator.storage.estimate().then(estimate => {
      return {
        used: estimate.usage || 0,
        quota: estimate.quota || 0
      };
    });
  }
  
  // Fallback: calculate stored data size
  let used = 0;
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      used += localStorage[key].length + key.length;
    }
  }
  
  return { used, quota: 5 * 1024 * 1024 }; // Assume 5MB quota
}

public checkQuota(): void {
  const { used, quota } = this.getStorageUsage();
  const usagePercent = (used / quota) * 100;
  
  if (usagePercent > 90) {
    throw new StorageQuotaError();
  } else if (usagePercent > 75) {
    console.warn('Local storage usage > 75%, consider exporting data');
  }
}
```

**Data Compression:**

```typescript
import LZString from 'lz-string';

export class StorageService {
  public set<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      const compressed = LZString.compress(serialized);
      localStorage.setItem(key, compressed);
    } catch (error) {
      if (error.name === 'QuotaExceededError') {
        this.handleQuotaExceeded();
      }
      throw error;
    }
  }
  
  public get<T>(key: string): T | null {
    const compressed = localStorage.getItem(key);
    if (!compressed) return null;
    
    const decompressed = LZString.decompress(compressed);
    return JSON.parse(decompressed);
  }
}
```

---

### Recommendation Engine Performance

**Web Worker for Heavy Computation:**

```typescript
// public/recommendation-worker.js
self.onmessage = function(e) {
  const { userRatings, allBooks, allReviews } = e.data;
  
  // Run recommendation algorithm in background
  const recommendations = calculateRecommendations(
    userRatings,
    allBooks,
    allReviews
  );
  
  self.postMessage({ recommendations });
};

// src/services/RecommendationService.ts
public async getRecommendations(userId: string, count: number = 10): Promise<Book[]> {
  return new Promise((resolve) => {
    const worker = new Worker('/recommendation-worker.js');
    
    worker.postMessage({
      userRatings: this.getUserRatings(userId),
      allBooks: this.getAllBooks(),
      allReviews: this.getAllReviews()
    });
    
    worker.onmessage = (e) => {
      resolve(e.data.recommendations.slice(0, count));
      worker.terminate();
    };
  });
}
```

**Caching Recommendations:**

```typescript
private recommendationCache: Map<string, { recommendations: Book[], timestamp: number }> = new Map();
private readonly CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

public async getRecommendations(userId: string, count: number = 10): Promise<Book[]> {
  const cached = this.recommendationCache.get(userId);
  
  if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
    return cached.recommendations.slice(0, count);
  }
  
  // Calculate new recommendations
  const recommendations = await this.calculateRecommendations(userId, count);
  
  this.recommendationCache.set(userId, {
    recommendations,
    timestamp: Date.now()
  });
  
  return recommendations;
}
```

---

### Performance Monitoring

**Core Web Vitals Tracking:**

```typescript
// src/utils/performance.ts
import { onLCP, onFID, onCLS } from 'web-vitals';

export const initPerformanceMonitoring = () => {
  onLCP((metric) => {
    console.log('LCP:', metric.value);
    if (window.gtag) {
      gtag('event', 'web_vitals', {
        name: 'LCP',
        value: Math.round(metric.value),
        event_category: 'Web Vitals'
      });
    }
  });
  
  onFID((metric) => {
    console.log('FID:', metric.value);
    if (window.gtag) {
      gtag('event', 'web_vitals', {
        name: 'FID',
        value: Math.round(metric.value),
        event_category: 'Web Vitals'
      });
    }
  });
  
  onCLS((metric) => {
    console.log('CLS:', metric.value);
    if (window.gtag) {
      gtag('event', 'web_vitals', {
        name: 'CLS',
        value: Math.round(metric.value * 1000),
        event_category: 'Web Vitals'
      });
    }
  });
};
```

**Performance Budget Enforcement:**

```javascript
// lighthouse-ci.config.js
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      url: ['http://localhost:3000']
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.85 }],
        'categories:accessibility': ['error', { minScore: 0.90 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }]
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};
```

---

### Performance Targets Summary

| Metric | Target | Current |
|--------|--------|---------|
| Initial Bundle Size | <200KB gzipped | TBD |
| Time to Interactive | <3s (3G) | TBD |
| Largest Contentful Paint | <2.5s | TBD |
| First Input Delay | <100ms | TBD |
| Cumulative Layout Shift | <0.1 | TBD |
| Lighthouse Performance | >85 (desktop) | TBD |
| Lighthouse Performance | >75 (mobile) | TBD |
| Search Latency | <100ms | TBD |
| CloudFront Cache Hit Ratio | >90% | TBD |

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
  plans/
    adult-book-website/
      HLD.md
      PRD.md
      LLD.md                  # [THIS DOCUMENT]
    health-check/
      HLD.md
      LLD.md
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
