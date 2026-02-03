# Low-Level Design: aiworkshop

**Created:** 2026-02-03T08:29:29Z
**Status:** Draft

## 1. Implementation Overview

<!-- AI: Brief summary of implementation approach -->

This implementation creates a standalone React-based static website for displaying jokes, completely separate from the existing Python-based repository. The jokes website will be built in a new directory structure under `jokes-website/` to isolate it from the existing Python API and analysis tools.

**Implementation Strategy:**
1. Create a new React application using Vite in `jokes-website/` directory
2. Implement component-based architecture with React 18+ and React Router v6
3. Store jokes data in static JSON files within the `public/data/` directory
4. Build responsive UI components with CSS Modules for scoped styling
5. Configure build output for S3 static hosting with SPA routing support
6. Set up deployment pipeline for automated S3 deployment

**Key Technologies:**
- React 18.2+ with functional components and hooks
- Vite 5.0+ for build tooling and development server
- React Router v6 for client-side routing
- CSS Modules for component styling
- Jest and React Testing Library for testing

**Development Approach:**
- Mobile-first responsive design
- Component-driven development with reusable UI elements
- Performance optimization through code splitting and lazy loading
- Lighthouse CI integration for performance monitoring

---

## 2. File Structure

<!-- AI: List all new and modified files with descriptions -->

```
jokes-website/                          # New React application root
  package.json                          # NPM dependencies and scripts
  vite.config.js                        # Vite build configuration
  index.html                            # HTML entry point
  .env.example                          # Environment variables template
  .gitignore                            # Git ignore for node_modules, build
  
  public/                               # Static assets served as-is
    data/
      jokes.json                        # Joke dataset (JSON array)
      categories.json                   # Category metadata
    favicon.ico                         # Site favicon
    robots.txt                          # Search engine directives
    
  src/                                  # React application source
    main.jsx                            # Application entry point
    App.jsx                             # Root component with routing
    App.module.css                      # App-level styles
    
    components/                         # Reusable UI components
      Layout/
        Header.jsx                      # Site header with navigation
        Header.module.css
        Footer.jsx                      # Site footer
        Footer.module.css
        Layout.jsx                      # Layout wrapper component
        Layout.module.css
      
      JokeCard/
        JokeCard.jsx                    # Individual joke display card
        JokeCard.module.css
      
      JokeNavigation/
        JokeNavigation.jsx              # Next/previous controls
        JokeNavigation.module.css
      
      CategoryFilter/
        CategoryFilter.jsx              # Category selection component
        CategoryFilter.module.css
      
      ErrorBoundary/
        ErrorBoundary.jsx               # React error boundary
        ErrorBoundary.module.css
    
    pages/                              # Route-level page components
      Home/
        Home.jsx                        # Landing page
        Home.module.css
      
      JokesList/
        JokesList.jsx                   # Browse all jokes page
        JokesList.module.css
      
      JokeDetail/
        JokeDetail.jsx                  # Single joke view page
        JokeDetail.module.css
      
      Categories/
        Categories.jsx                  # Category browser page
        Categories.module.css
      
      NotFound/
        NotFound.jsx                    # 404 error page
        NotFound.module.css
    
    hooks/                              # Custom React hooks
      useJokes.js                       # Hook for loading/filtering jokes
      useCategories.js                  # Hook for category data
      usePersistedState.js              # Hook for localStorage state
    
    utils/                              # Utility functions
      jokeDataLoader.js                 # Load and parse JSON data
      filterHelpers.js                  # Joke filtering logic
      urlHelpers.js                     # URL parsing/generation
      constants.js                      # App-wide constants
    
    styles/                             # Global styles
      global.css                        # CSS reset and base styles
      variables.css                     # CSS custom properties
    
    __tests__/                          # Test files
      components/
        JokeCard.test.jsx
        CategoryFilter.test.jsx
      pages/
        Home.test.jsx
        JokeDetail.test.jsx
      hooks/
        useJokes.test.js
      utils/
        jokeDataLoader.test.js
        filterHelpers.test.js
  
  .github/                              # CI/CD workflows
    workflows/
      deploy.yml                        # GitHub Actions deployment
      lighthouse.yml                    # Lighthouse CI checks
  
  deploy/                               # Deployment scripts
    s3-sync.sh                          # S3 upload script
    cloudfront-invalidate.sh            # Cache invalidation script
  
  docs/                                 # Documentation
    SETUP.md                            # Setup instructions
    DEPLOYMENT.md                       # Deployment guide
    ARCHITECTURE.md                     # Architecture overview

docs/                                   # Modified: existing docs folder
  plans/
    jokes-website/
      LLD.md                            # This document (new)
      HLD.md                            # Existing HLD
      PRD.md                            # Existing PRD

README.md                               # Modified: add jokes-website section
```

**Modified Files:**
- `README.md` - Add jokes-website project documentation link
- `docs/plans/jokes-website/LLD.md` - New file (this document)

**New Directories:**
- `jokes-website/` - Entire React application (550+ lines across 40+ files)

---

## 3. Detailed Component Designs

<!-- AI: For each major component from HLD, provide detailed design -->

### 3.1 App Root Component (`src/App.jsx`)

**Purpose:** Application root with routing configuration and global providers

**Implementation:**
```jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Home from './pages/Home/Home';
import JokesList from './pages/JokesList/JokesList';
import JokeDetail from './pages/JokeDetail/JokeDetail';
import Categories from './pages/Categories/Categories';
import NotFound from './pages/NotFound/NotFound';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import styles from './App.module.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/jokes" element={<JokesList />} />
            <Route path="/jokes/:id" element={<JokeDetail />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/categories/:category" element={<JokesList />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
```

**State:** None (stateless routing component)

**Props:** None

**Key Features:**
- BrowserRouter for clean URLs
- Nested routes under Layout component
- Catch-all 404 route
- Global error boundary

---

### 3.2 JokeCard Component (`src/components/JokeCard/JokeCard.jsx`)

**Purpose:** Display individual joke with setup and punchline

**Props Interface:**
```javascript
{
  joke: {
    id: string,
    type: 'one-liner' | 'qa' | 'knock-knock' | 'story',
    category: string,
    setup?: string,
    punchline: string,
    tags?: string[]
  },
  showCategory: boolean = true,
  onShare?: (jokeId) => void
}
```

**Implementation:**
```jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './JokeCard.module.css';

function JokeCard({ joke, showCategory = true, onShare }) {
  const [revealed, setRevealed] = useState(false);
  
  const handleReveal = () => {
    setRevealed(true);
  };
  
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: joke.setup || 'Funny Joke',
        text: `${joke.setup ? joke.setup + '\n' : ''}${joke.punchline}`,
        url: window.location.origin + `/jokes/${joke.id}`
      });
    } else {
      onShare?.(joke.id);
    }
  };
  
  return (
    <div className={styles.card}>
      {showCategory && (
        <Link to={`/categories/${joke.category}`} className={styles.category}>
          {joke.category}
        </Link>
      )}
      
      {joke.setup && (
        <div className={styles.setup}>{joke.setup}</div>
      )}
      
      {!revealed && joke.setup ? (
        <button onClick={handleReveal} className={styles.revealButton}>
          Show Punchline
        </button>
      ) : (
        <div className={styles.punchline}>{joke.punchline}</div>
      )}
      
      <div className={styles.actions}>
        <button onClick={handleShare} className={styles.shareButton}>
          Share
        </button>
        <Link to={`/jokes/${joke.id}`} className={styles.linkButton}>
          Permalink
        </Link>
      </div>
    </div>
  );
}

export default JokeCard;
```

**State:**
- `revealed`: boolean - Whether punchline is shown (for setup/punchline jokes)

**Styling:** CSS Modules with responsive card layout

---

### 3.3 useJokes Hook (`src/hooks/useJokes.js`)

**Purpose:** Load and filter jokes data with caching

**API:**
```javascript
function useJokes(filters = {}) {
  return {
    jokes: Joke[],        // Filtered jokes array
    loading: boolean,     // Loading state
    error: Error | null,  // Error state
    categories: string[], // Available categories
    totalCount: number    // Total jokes before filtering
  };
}
```

**Implementation:**
```javascript
import { useState, useEffect, useMemo } from 'react';
import { loadJokes } from '../utils/jokeDataLoader';
import { filterJokes } from '../utils/filterHelpers';

function useJokes(filters = {}) {
  const [allJokes, setAllJokes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Load jokes on mount
  useEffect(() => {
    let isMounted = true;
    
    loadJokes()
      .then(data => {
        if (isMounted) {
          setAllJokes(data.jokes);
          setLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          setError(err);
          setLoading(false);
        }
      });
    
    return () => {
      isMounted = false;
    };
  }, []);
  
  // Filter jokes based on filters prop
  const jokes = useMemo(() => {
    return filterJokes(allJokes, filters);
  }, [allJokes, filters]);
  
  // Extract unique categories
  const categories = useMemo(() => {
    const cats = new Set(allJokes.map(j => j.category));
    return Array.from(cats).sort();
  }, [allJokes]);
  
  return {
    jokes,
    loading,
    error,
    categories,
    totalCount: allJokes.length
  };
}

export default useJokes;
```

**Caching Strategy:**
- Load jokes once on mount
- Cache in component state
- Filter using memoized computation
- No re-fetch on filter changes

---

### 3.4 JokeDetail Page (`src/pages/JokeDetail/JokeDetail.jsx`)

**Purpose:** Display single joke with navigation controls

**Implementation:**
```jsx
import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import useJokes from '../../hooks/useJokes';
import JokeCard from '../../components/JokeCard/JokeCard';
import JokeNavigation from '../../components/JokeNavigation/JokeNavigation';
import styles from './JokeDetail.module.css';

function JokeDetail() {
  const { id } = useParams();
  const { jokes, loading, error } = useJokes();
  
  if (loading) {
    return <div className={styles.loading}>Loading joke...</div>;
  }
  
  if (error) {
    return <div className={styles.error}>Error loading jokes</div>;
  }
  
  const currentIndex = jokes.findIndex(j => j.id === id);
  
  if (currentIndex === -1) {
    return <Navigate to="/404" replace />;
  }
  
  const joke = jokes[currentIndex];
  const prevJoke = currentIndex > 0 ? jokes[currentIndex - 1] : null;
  const nextJoke = currentIndex < jokes.length - 1 ? jokes[currentIndex + 1] : null;
  
  return (
    <div className={styles.container}>
      <JokeCard joke={joke} showCategory={true} />
      <JokeNavigation 
        prevJoke={prevJoke} 
        nextJoke={nextJoke}
        currentIndex={currentIndex + 1}
        totalJokes={jokes.length}
      />
    </div>
  );
}

export default JokeDetail;
```

**URL Parameters:**
- `:id` - Joke identifier from route

**Navigation Logic:**
- Find current joke index in array
- Determine previous/next jokes for navigation
- Handle edge cases (first/last joke)

---

### 3.5 Categories Page (`src/pages/Categories/Categories.jsx`)

**Purpose:** Browse jokes by category with counts

**Implementation:**
```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import useJokes from '../../hooks/useJokes';
import styles from './Categories.module.css';

function Categories() {
  const { jokes, categories, loading, error } = useJokes();
  
  if (loading) return <div>Loading categories...</div>;
  if (error) return <div>Error loading categories</div>;
  
  // Calculate joke count per category
  const categoryCounts = categories.map(cat => ({
    name: cat,
    count: jokes.filter(j => j.category === cat).length,
    displayName: cat.split('-').map(w => 
      w.charAt(0).toUpperCase() + w.slice(1)
    ).join(' ')
  }));
  
  return (
    <div className={styles.container}>
      <h1>Browse by Category</h1>
      <div className={styles.grid}>
        {categoryCounts.map(cat => (
          <Link 
            key={cat.name}
            to={`/categories/${cat.name}`}
            className={styles.categoryCard}
          >
            <h2>{cat.displayName}</h2>
            <p>{cat.count} jokes</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Categories;
```

**Features:**
- Display all categories as clickable cards
- Show joke count per category
- Responsive grid layout
- Transform category IDs to display names

---

### 3.6 Home Page (`src/pages/Home/Home.jsx`)

**Purpose:** Landing page with featured joke and navigation

**Implementation:**
```jsx
import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import useJokes from '../../hooks/useJokes';
import JokeCard from '../../components/JokeCard/JokeCard';
import styles from './Home.module.css';

function Home() {
  const { jokes, loading } = useJokes();
  
  // Select random featured joke
  const featuredJoke = useMemo(() => {
    if (jokes.length === 0) return null;
    const randomIndex = Math.floor(Math.random() * jokes.length);
    return jokes[randomIndex];
  }, [jokes]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className={styles.container}>
      <header className={styles.hero}>
        <h1>Welcome to Jokes Galore</h1>
        <p>Your daily dose of laughter</p>
      </header>
      
      {featuredJoke && (
        <section className={styles.featured}>
          <h2>Featured Joke</h2>
          <JokeCard joke={featuredJoke} />
        </section>
      )}
      
      <nav className={styles.navigation}>
        <Link to="/jokes" className={styles.button}>
          Browse All Jokes
        </Link>
        <Link to="/categories" className={styles.button}>
          Browse by Category
        </Link>
      </nav>
    </div>
  );
}

export default Home;
```

**Features:**
- Hero section with site title
- Random featured joke on each visit
- Call-to-action buttons for browsing

---

## 4. Database Schema Changes

<!-- AI: SQL/migration scripts for schema changes -->

**Not Applicable** - This application uses static JSON data with no database.

### Data Schema (JSON Structure)

**jokes.json Format:**
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
    },
    {
      "id": "joke-002",
      "type": "one-liner",
      "category": "dad-jokes",
      "setup": null,
      "punchline": "I'm reading a book about anti-gravity. It's impossible to put down!",
      "tags": ["books", "wordplay"],
      "dateAdded": "2026-01-16T10:00:00Z"
    },
    {
      "id": "joke-003",
      "type": "knock-knock",
      "category": "knock-knock",
      "setup": "Knock knock. Who's there? Interrupting cow. Interrupting cow w—",
      "punchline": "MOOOOO!",
      "tags": ["classic", "kids"],
      "dateAdded": "2026-01-17T10:00:00Z"
    }
  ]
}
```

**categories.json Format (Optional):**
```json
{
  "categories": [
    {
      "id": "puns",
      "name": "Puns",
      "description": "Clever wordplay and puns",
      "icon": "🎭"
    },
    {
      "id": "dad-jokes",
      "name": "Dad Jokes",
      "description": "Classic dad humor",
      "icon": "👨"
    },
    {
      "id": "knock-knock",
      "name": "Knock-Knock Jokes",
      "description": "Traditional knock-knock format",
      "icon": "🚪"
    }
  ]
}
```

**Schema Validation:**
- Validate JSON structure at build time using JSON Schema
- Ensure all jokes have required fields (id, type, category, punchline)
- Verify unique joke IDs
- Check category consistency

---

## 5. API Implementation Details

<!-- AI: For each API endpoint, specify handler logic, validation, error handling -->

**Not Applicable** - This application has no backend APIs.

### Static Data Loading API

**Module:** `src/utils/jokeDataLoader.js`

**Function: loadJokes()**
```javascript
/**
 * Load jokes from static JSON file
 * @returns {Promise<{version: string, lastUpdated: string, jokes: Joke[]}>}
 * @throws {Error} If fetch fails or JSON is invalid
 */
export async function loadJokes() {
  try {
    const response = await fetch('/data/jokes.json');
    
    if (!response.ok) {
      throw new Error(`Failed to load jokes: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Validate data structure
    if (!data.jokes || !Array.isArray(data.jokes)) {
      throw new Error('Invalid jokes data format');
    }
    
    // Validate each joke has required fields
    data.jokes.forEach((joke, index) => {
      if (!joke.id || !joke.type || !joke.category || !joke.punchline) {
        throw new Error(`Invalid joke at index ${index}: missing required fields`);
      }
    });
    
    return data;
  } catch (error) {
    console.error('Error loading jokes:', error);
    throw error;
  }
}
```

**Error Handling:**
- Network errors: Display user-friendly message
- JSON parse errors: Log to console, show error state
- Validation errors: Fail fast with descriptive message

**Caching:**
- Browser caches JSON based on cache-control headers
- Component-level caching via useJokes hook
- No manual cache invalidation needed (static data)

---

**Function: loadCategories()**
```javascript
/**
 * Load category metadata (optional)
 * Falls back to deriving categories from jokes if file doesn't exist
 * @returns {Promise<Category[]>}
 */
export async function loadCategories() {
  try {
    const response = await fetch('/data/categories.json');
    if (response.ok) {
      const data = await response.json();
      return data.categories;
    }
  } catch (error) {
    console.warn('Categories file not found, will derive from jokes');
  }
  
  // Fallback: derive from jokes
  const jokesData = await loadJokes();
  const uniqueCategories = [...new Set(jokesData.jokes.map(j => j.category))];
  return uniqueCategories.map(cat => ({
    id: cat,
    name: cat.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    description: ''
  }));
}
```

---

## 6. Function Signatures

<!-- AI: Key function/method signatures with parameters and return types -->

### Core Utility Functions

**src/utils/jokeDataLoader.js**
```javascript
/**
 * Load jokes from static JSON file
 */
export async function loadJokes(): Promise<{
  version: string,
  lastUpdated: string,
  jokes: Joke[]
}>

/**
 * Load category metadata
 */
export async function loadCategories(): Promise<Category[]>
```

---

**src/utils/filterHelpers.js**
```javascript
/**
 * Filter jokes by category, search term, and tags
 * @param jokes - Array of all jokes
 * @param filters - Filter criteria
 * @returns Filtered jokes array
 */
export function filterJokes(
  jokes: Joke[],
  filters: {
    category?: string,
    searchTerm?: string,
    tags?: string[]
  }
): Joke[]

/**
 * Search jokes by text query (searches setup and punchline)
 * @param jokes - Array of jokes to search
 * @param query - Search query string
 * @returns Matching jokes
 */
export function searchJokes(jokes: Joke[], query: string): Joke[]

/**
 * Get jokes by category
 * @param jokes - Array of all jokes
 * @param category - Category ID
 * @returns Jokes in specified category
 */
export function getJokesByCategory(jokes: Joke[], category: string): Joke[]

/**
 * Get random joke from array
 * @param jokes - Array of jokes
 * @returns Random joke
 */
export function getRandomJoke(jokes: Joke[]): Joke | null
```

---

**src/utils/urlHelpers.js**
```javascript
/**
 * Generate shareable URL for a joke
 * @param jokeId - Joke identifier
 * @returns Absolute URL
 */
export function getJokeUrl(jokeId: string): string

/**
 * Parse category from URL query params
 * @param searchParams - URLSearchParams object
 * @returns Category ID or null
 */
export function getCategoryFromUrl(searchParams: URLSearchParams): string | null

/**
 * Generate URL with category filter
 * @param category - Category ID
 * @returns Relative URL with query param
 */
export function getCategoryUrl(category: string): string
```

---

### React Hooks

**src/hooks/useJokes.js**
```javascript
/**
 * Load and filter jokes data
 * @param filters - Optional filter criteria
 * @returns Jokes data with loading/error states
 */
export function useJokes(filters?: {
  category?: string,
  searchTerm?: string
}): {
  jokes: Joke[],
  loading: boolean,
  error: Error | null,
  categories: string[],
  totalCount: number
}
```

---

**src/hooks/useCategories.js**
```javascript
/**
 * Load category metadata
 * @returns Categories with loading/error states
 */
export function useCategories(): {
  categories: Category[],
  loading: boolean,
  error: Error | null
}
```

---

**src/hooks/usePersistedState.js**
```javascript
/**
 * useState with localStorage persistence
 * @param key - localStorage key
 * @param initialValue - Default value
 * @returns [state, setState] tuple
 */
export function usePersistedState<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void]
```

---

### Component Props Interfaces

**JokeCard.jsx**
```typescript
interface JokeCardProps {
  joke: Joke;
  showCategory?: boolean;
  onShare?: (jokeId: string) => void;
}
```

**JokeNavigation.jsx**
```typescript
interface JokeNavigationProps {
  prevJoke: Joke | null;
  nextJoke: Joke | null;
  currentIndex: number;
  totalJokes: number;
}
```

**CategoryFilter.jsx**
```typescript
interface CategoryFilterProps {
  categories: string[];
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}
```

**Layout.jsx**
```typescript
interface LayoutProps {
  children: React.ReactNode;
}
```

---

### Type Definitions

**src/types/index.js** (or .ts if using TypeScript)
```javascript
/**
 * Joke data structure
 */
export type JokeType = 'one-liner' | 'qa' | 'knock-knock' | 'story';

export interface Joke {
  id: string;
  type: JokeType;
  category: string;
  setup: string | null;
  punchline: string;
  tags?: string[];
  dateAdded: string; // ISO8601 timestamp
}

/**
 * Category metadata
 */
export interface Category {
  id: string;
  name: string;
  description: string;
  icon?: string;
}

/**
 * Filter criteria
 */
export interface JokeFilters {
  category?: string;
  searchTerm?: string;
  tags?: string[];
}
```

---

## 7. State Management

<!-- AI: How application state is managed (Redux, Context, database) -->

### State Management Strategy

**Approach:** **Local component state + custom hooks** (no Redux or global state library needed)

**Rationale:**
- Application state is simple (just joke data and UI state)
- No complex state interactions or global mutations
- React hooks provide sufficient state management
- Avoids unnecessary complexity and bundle size

---

### State Architecture

**1. Server State (Joke Data)**
- **Location:** `useJokes` custom hook
- **Storage:** Component state via `useState`
- **Lifecycle:** Load on mount, cache for session
- **Sharing:** Hook called in multiple components (each loads independently)

```javascript
// useJokes hook manages joke data state
const { jokes, loading, error } = useJokes({ category: 'puns' });
```

**2. URL State (Routing & Filters)**
- **Location:** React Router (URL params and query strings)
- **Storage:** Browser URL
- **Lifecycle:** Synced with navigation
- **Sharing:** Accessible via `useParams` and `useSearchParams`

```javascript
// Category filter in URL
const { category } = useParams(); // /categories/puns
const [searchParams] = useSearchParams(); // ?category=puns
```

**3. Local UI State**
- **Location:** Individual components
- **Storage:** Component `useState`
- **Lifecycle:** Mount to unmount
- **Sharing:** None (component-local)

```javascript
// JokeCard revealed state
const [revealed, setRevealed] = useState(false);
```

**4. Persistent State (User Preferences)**
- **Location:** `usePersistedState` hook
- **Storage:** Browser localStorage
- **Lifecycle:** Persists across sessions
- **Sharing:** Hook provides read/write access

```javascript
// User theme preference
const [theme, setTheme] = usePersistedState('theme', 'light');
```

---

### State Flow Diagram

```
[Static JSON File] 
    ↓ fetch
[jokeDataLoader.js]
    ↓ loadJokes()
[useJokes hook]
    ↓ jokes array
[Component State]
    ↓ props
[Child Components]

[URL Bar]
    ↓ React Router
[useParams/useSearchParams]
    ↓ category filter
[Component Logic]
    ↓ filtered jokes
[Display]
```

---

### State Management Patterns

**Pattern 1: Data Fetching Hook**
```javascript
// Centralized data loading with hook
function JokesList() {
  const { jokes, loading, error } = useJokes();
  // Component renders based on hook state
}
```

**Pattern 2: URL as Single Source of Truth**
```javascript
// Category comes from URL, not component state
function JokesList() {
  const { category } = useParams();
  const { jokes } = useJokes({ category });
  // Category state is in URL, not useState
}
```

**Pattern 3: Prop Drilling (Limited)**
```javascript
// Layout passes minimal shared state
function Layout({ children }) {
  return (
    <div>
      <Header /> {/* No props needed, reads URL */}
      <main>{children}</main>
      <Footer /> {/* No props needed */}
    </div>
  );
}
```

**Pattern 4: Derived State**
```javascript
// Compute values from existing state
const categories = useMemo(() => {
  return [...new Set(jokes.map(j => j.category))];
}, [jokes]);
```

---

### When to Add Context/Redux (Future)

**Current assessment:** Not needed for v1

**Add Context if:**
- Need to share joke data across deeply nested components without prop drilling
- Add user authentication state (login, favorites, etc.)
- Implement complex filter state shared across multiple components

**Add Redux if:**
- State logic becomes complex with many interdependent updates
- Need time-travel debugging
- Add user-generated content with optimistic updates

**Current approach is sufficient because:**
- Only 3-4 levels of component nesting maximum
- State is mostly read-only (jokes data)
- URL handles filter/navigation state
- No complex state transitions

---

## 8. Error Handling Strategy

<!-- AI: Error codes, exception handling, user-facing messages -->

### Error Handling Architecture

**Layers:**
1. **Network/Data Loading Errors** - Fetch failures, JSON parsing
2. **React Component Errors** - Rendering exceptions, lifecycle errors
3. **User Input Errors** - Invalid URLs, missing resources
4. **Build/Deployment Errors** - Configuration issues, missing files

---

### 1. Network & Data Loading Errors

**Location:** `src/utils/jokeDataLoader.js`

**Error Types:**
```javascript
// Custom error classes
export class JokeDataError extends Error {
  constructor(message, type) {
    super(message);
    this.name = 'JokeDataError';
    this.type = type; // 'NETWORK' | 'PARSE' | 'VALIDATION'
  }
}
```

**Implementation:**
```javascript
export async function loadJokes() {
  try {
    const response = await fetch('/data/jokes.json');
    
    if (!response.ok) {
      throw new JokeDataError(
        `HTTP ${response.status}: ${response.statusText}`,
        'NETWORK'
      );
    }
    
    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      throw new JokeDataError(
        'Invalid JSON format in jokes data',
        'PARSE'
      );
    }
    
    if (!data.jokes || !Array.isArray(data.jokes)) {
      throw new JokeDataError(
        'Missing or invalid jokes array',
        'VALIDATION'
      );
    }
    
    return data;
  } catch (error) {
    // Log to console and error tracking service
    console.error('Failed to load jokes:', error);
    
    // Re-throw for component to handle
    throw error;
  }
}
```

**Component-Level Handling:**
```javascript
function JokesList() {
  const { jokes, loading, error } = useJokes();
  
  if (error) {
    return (
      <div className={styles.error}>
        <h2>Oops! Something went wrong</h2>
        <p>We couldn't load the jokes right now. Please try again later.</p>
        <button onClick={() => window.location.reload()}>
          Reload Page
        </button>
      </div>
    );
  }
  // ...
}
```

---

### 2. React Component Errors

**Location:** `src/components/ErrorBoundary/ErrorBoundary.jsx`

**Implementation:**
```jsx
import React from 'react';
import styles from './ErrorBoundary.module.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log error to console
    console.error('React Error Boundary caught error:', error, errorInfo);
    
    // Send to error tracking service (Sentry, etc.)
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: { react: { componentStack: errorInfo.componentStack } }
      });
    }
    
    this.setState({ error, errorInfo });
  }
  
  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/'; // Navigate to home
  };
  
  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorBoundary}>
          <h1>Something went wrong</h1>
          <p>We're sorry, but something unexpected happened.</p>
          <button onClick={this.handleReset}>Go to Home Page</button>
          {process.env.NODE_ENV === 'development' && (
            <details>
              <summary>Error Details</summary>
              <pre>{this.state.error?.toString()}</pre>
              <pre>{this.state.errorInfo?.componentStack}</pre>
            </details>
          )}
        </div>
      );
    }
    
    return this.props.children;
  }
}

export default ErrorBoundary;
```

**Usage:**
```jsx
// Wrap entire app
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

### 3. User Input & Navigation Errors

**404 Not Found:**

**Location:** `src/pages/NotFound/NotFound.jsx`

```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import styles from './NotFound.module.css';

function NotFound() {
  return (
    <div className={styles.container}>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link to="/" className={styles.homeLink}>
        Go to Home Page
      </Link>
    </div>
  );
}

export default NotFound;
```

**Invalid Joke ID:**

**Location:** `src/pages/JokeDetail/JokeDetail.jsx`

```jsx
function JokeDetail() {
  const { id } = useParams();
  const { jokes, loading } = useJokes();
  
  if (!loading && !jokes.find(j => j.id === id)) {
    return <Navigate to="/404" replace />;
  }
  // ...
}
```

---

### 4. Error Messages (User-Facing)

**Error Message Principles:**
- Clear, non-technical language
- Suggest actionable next steps
- Friendly, apologetic tone
- Include retry/recovery options

**Standard Messages:**

| Error Type | User Message |
|------------|-------------|
| Network failure | "We couldn't connect right now. Please check your internet connection and try again." |
| Data load failure | "Oops! We couldn't load the jokes. Please refresh the page." |
| Invalid joke ID | "This joke doesn't exist. Browse our collection to find more!" |
| JSON parse error | "Something went wrong loading the content. Please try again later." |
| React render error | "Something unexpected happened. We've been notified and are looking into it." |
| Missing category | "This category doesn't exist. Check out our available categories." |

---

### 5. Error Logging & Monitoring

**Client-Side Logging:**

```javascript
// src/utils/errorLogger.js
export function logError(error, context = {}) {
  // Always log to console
  console.error('Error:', error, context);
  
  // Send to error tracking service
  if (window.Sentry) {
    window.Sentry.captureException(error, {
      extra: context
    });
  }
  
  // Log to analytics
  if (window.gtag) {
    window.gtag('event', 'exception', {
      description: error.message,
      fatal: false
    });
  }
}
```

**Integration Points:**
- Error Boundary: Catches React render errors
- Network errors: Logged in data loader
- User actions: Log failed share/copy actions

---

### 6. Graceful Degradation

**Missing Data:**
```javascript
// Show placeholder if jokes empty
{jokes.length === 0 && !loading && (
  <div className={styles.empty}>
    <p>No jokes available right now. Check back soon!</p>
  </div>
)}
```

**Feature Detection:**
```javascript
// Fallback if Web Share API not available
const handleShare = () => {
  if (navigator.share) {
    navigator.share({ title, text, url });
  } else {
    // Copy to clipboard fallback
    navigator.clipboard.writeText(url);
    alert('Link copied to clipboard!');
  }
};
```

---

### 7. Development vs Production Error Handling

**Development:**
- Show full error stack traces
- Console logs for all errors
- Error boundary displays details
- React strict mode warnings enabled

**Production:**
- User-friendly error messages only
- Stack traces hidden from users
- Errors sent to monitoring service
- Graceful fallbacks and recovery options

```javascript
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', debugData);
}
```

---

## 9. Test Plan

### Unit Tests

**Location:** `src/__tests__/`

**Test Framework:** Jest + React Testing Library

---

#### Component Unit Tests

**src/__tests__/components/JokeCard.test.jsx**
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JokeCard from '../../components/JokeCard/JokeCard';

describe('JokeCard', () => {
  const mockJoke = {
    id: 'joke-001',
    type: 'qa',
    category: 'puns',
    setup: 'Why did the chicken cross the road?',
    punchline: 'To get to the other side!',
    tags: ['classic']
  };
  
  it('renders joke setup', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} />
      </BrowserRouter>
    );
    expect(screen.getByText(mockJoke.setup)).toBeInTheDocument();
  });
  
  it('hides punchline initially for Q&A jokes', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} />
      </BrowserRouter>
    );
    expect(screen.queryByText(mockJoke.punchline)).not.toBeInTheDocument();
  });
  
  it('reveals punchline when button clicked', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} />
      </BrowserRouter>
    );
    fireEvent.click(screen.getByText('Show Punchline'));
    expect(screen.getByText(mockJoke.punchline)).toBeInTheDocument();
  });
  
  it('displays category link when showCategory is true', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} showCategory={true} />
      </BrowserRouter>
    );
    expect(screen.getByText('puns')).toBeInTheDocument();
  });
  
  it('calls onShare when share button clicked', () => {
    const mockShare = jest.fn();
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} onShare={mockShare} />
      </BrowserRouter>
    );
    fireEvent.click(screen.getByText('Share'));
    // Expect either native share or callback
    expect(mockShare).toHaveBeenCalled();
  });
});
```

---

**src/__tests__/components/CategoryFilter.test.jsx**
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import CategoryFilter from '../../components/CategoryFilter/CategoryFilter';

describe('CategoryFilter', () => {
  const categories = ['puns', 'dad-jokes', 'knock-knock'];
  const mockOnChange = jest.fn();
  
  it('renders all categories', () => {
    render(
      <CategoryFilter 
        categories={categories}
        selectedCategory={null}
        onCategoryChange={mockOnChange}
      />
    );
    categories.forEach(cat => {
      expect(screen.getByText(cat, { exact: false })).toBeInTheDocument();
    });
  });
  
  it('calls onCategoryChange when category clicked', () => {
    render(
      <CategoryFilter 
        categories={categories}
        selectedCategory={null}
        onCategoryChange={mockOnChange}
      />
    );
    fireEvent.click(screen.getByText('puns', { exact: false }));
    expect(mockOnChange).toHaveBeenCalledWith('puns');
  });
  
  it('highlights selected category', () => {
    const { container } = render(
      <CategoryFilter 
        categories={categories}
        selectedCategory="puns"
        onCategoryChange={mockOnChange}
      />
    );
    const selectedButton = container.querySelector('[aria-pressed="true"]');
    expect(selectedButton).toHaveTextContent('puns');
  });
});
```

---

#### Hook Unit Tests

**src/__tests__/hooks/useJokes.test.js**
```javascript
import { renderHook, waitFor } from '@testing-library/react';
import useJokes from '../../hooks/useJokes';
import * as jokeDataLoader from '../../utils/jokeDataLoader';

jest.mock('../../utils/jokeDataLoader');

describe('useJokes', () => {
  const mockJokesData = {
    version: '1.0',
    jokes: [
      { id: '1', category: 'puns', type: 'qa', setup: 'Q?', punchline: 'A!' },
      { id: '2', category: 'dad-jokes', type: 'one-liner', punchline: 'Ha!' }
    ]
  };
  
  beforeEach(() => {
    jokeDataLoader.loadJokes.mockResolvedValue(mockJokesData);
  });
  
  it('loads jokes on mount', async () => {
    const { result } = renderHook(() => useJokes());
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(result.current.jokes).toHaveLength(2);
    expect(result.current.error).toBeNull();
  });
  
  it('filters jokes by category', async () => {
    const { result } = renderHook(() => useJokes({ category: 'puns' }));
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(result.current.jokes).toHaveLength(1);
    expect(result.current.jokes[0].category).toBe('puns');
  });
  
  it('handles load errors', async () => {
    const mockError = new Error('Network failure');
    jokeDataLoader.loadJokes.mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useJokes());
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(result.current.error).toBe(mockError);
    expect(result.current.jokes).toHaveLength(0);
  });
  
  it('returns unique categories', async () => {
    const { result } = renderHook(() => useJokes());
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(result.current.categories).toEqual(['dad-jokes', 'puns']);
  });
});
```

---

#### Utility Function Tests

**src/__tests__/utils/filterHelpers.test.js**
```javascript
import { filterJokes, searchJokes, getRandomJoke } from '../../utils/filterHelpers';

describe('filterHelpers', () => {
  const jokes = [
    { id: '1', category: 'puns', setup: 'Why?', punchline: 'Because!', tags: ['short'] },
    { id: '2', category: 'dad-jokes', setup: null, punchline: 'Ha ha!', tags: ['long'] },
    { id: '3', category: 'puns', setup: 'What?', punchline: 'That!', tags: ['short'] }
  ];
  
  describe('filterJokes', () => {
    it('filters by category', () => {
      const result = filterJokes(jokes, { category: 'puns' });
      expect(result).toHaveLength(2);
      expect(result.every(j => j.category === 'puns')).toBe(true);
    });
    
    it('filters by search term', () => {
      const result = filterJokes(jokes, { searchTerm: 'ha' });
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe('2');
    });
    
    it('returns all jokes when no filters', () => {
      const result = filterJokes(jokes, {});
      expect(result).toHaveLength(3);
    });
  });
  
  describe('searchJokes', () => {
    it('searches in setup and punchline', () => {
      const result = searchJokes(jokes, 'why');
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe('1');
    });
    
    it('is case-insensitive', () => {
      const result = searchJokes(jokes, 'WHY');
      expect(result).toHaveLength(1);
    });
  });
  
  describe('getRandomJoke', () => {
    it('returns a joke from array', () => {
      const result = getRandomJoke(jokes);
      expect(jokes).toContain(result);
    });
    
    it('returns null for empty array', () => {
      expect(getRandomJoke([])).toBeNull();
    });
  });
});
```

---

**src/__tests__/utils/jokeDataLoader.test.js**
```javascript
import { loadJokes } from '../../utils/jokeDataLoader';

global.fetch = jest.fn();

describe('jokeDataLoader', () => {
  beforeEach(() => {
    fetch.mockClear();
  });
  
  it('loads jokes successfully', async () => {
    const mockData = { version: '1.0', jokes: [{ id: '1' }] };
    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockData
    });
    
    const result = await loadJokes();
    
    expect(fetch).toHaveBeenCalledWith('/data/jokes.json');
    expect(result).toEqual(mockData);
  });
  
  it('throws error on network failure', async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found'
    });
    
    await expect(loadJokes()).rejects.toThrow('Failed to load jokes');
  });
  
  it('throws error on invalid JSON', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => { throw new Error('Invalid JSON'); }
    });
    
    await expect(loadJokes()).rejects.toThrow();
  });
  
  it('validates joke data structure', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ invalid: 'data' })
    });
    
    await expect(loadJokes()).rejects.toThrow('Invalid jokes data format');
  });
});
```

---

### Integration Tests

**Location:** `src/__tests__/integration/`

**Test Framework:** React Testing Library with full app context

---

**src/__tests__/integration/JokeViewing.test.jsx**
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../../App';
import * as jokeDataLoader from '../../utils/jokeDataLoader';

jest.mock('../../utils/jokeDataLoader');

describe('Joke Viewing Flow', () => {
  const mockJokesData = {
    jokes: [
      { id: 'joke-1', category: 'puns', type: 'qa', setup: 'Q1?', punchline: 'A1' },
      { id: 'joke-2', category: 'puns', type: 'qa', setup: 'Q2?', punchline: 'A2' }
    ]
  };
  
  beforeEach(() => {
    jokeDataLoader.loadJokes.mockResolvedValue(mockJokesData);
  });
  
  it('displays joke from direct URL', async () => {
    render(
      <MemoryRouter initialEntries={['/jokes/joke-1']}>
        <App />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Q1?')).toBeInTheDocument();
    });
  });
  
  it('navigates between jokes using next button', async () => {
    render(
      <MemoryRouter initialEntries={['/jokes/joke-1']}>
        <App />
      </MemoryRouter>
    );
    
    await waitFor(() => screen.getByText('Q1?'));
    
    fireEvent.click(screen.getByLabelText('Next joke'));
    
    await waitFor(() => {
      expect(screen.getByText('Q2?')).toBeInTheDocument();
    });
  });
  
  it('redirects to 404 for invalid joke ID', async () => {
    render(
      <MemoryRouter initialEntries={['/jokes/invalid']}>
        <App />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/404/i)).toBeInTheDocument();
    });
  });
});
```

---

**src/__tests__/integration/CategoryBrowsing.test.jsx**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../../App';
import * as jokeDataLoader from '../../utils/jokeDataLoader';

jest.mock('../../utils/jokeDataLoader');

describe('Category Browsing', () => {
  const mockJokesData = {
    jokes: [
      { id: '1', category: 'puns', type: 'qa', setup: 'Q', punchline: 'A' },
      { id: '2', category: 'dad-jokes', type: 'qa', setup: 'Q', punchline: 'A' }
    ]
  };
  
  beforeEach(() => {
    jokeDataLoader.loadJokes.mockResolvedValue(mockJokesData);
  });
  
  it('displays all categories on categories page', async () => {
    render(
      <MemoryRouter initialEntries={['/categories']}>
        <App />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/puns/i)).toBeInTheDocument();
      expect(screen.getByText(/dad jokes/i)).toBeInTheDocument();
    });
  });
  
  it('filters jokes when category selected', async () => {
    render(
      <MemoryRouter initialEntries={['/categories/puns']}>
        <App />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      // Should only show puns category jokes
      const jokeCards = screen.getAllByTestId('joke-card');
      expect(jokeCards).toHaveLength(1);
    });
  });
});
```

---

### E2E Tests

**Location:** `e2e/`

**Test Framework:** Playwright or Cypress

---

**e2e/smoke.spec.js**
```javascript
// Playwright E2E tests
import { test, expect } from '@playwright/test';

test.describe('Jokes Website Smoke Tests', () => {
  test('home page loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Welcome');
    await expect(page.locator('.joke-card')).toBeVisible();
  });
  
  test('can browse jokes', async ({ page }) => {
    await page.goto('/jokes');
    await expect(page.locator('.joke-card').first()).toBeVisible();
    
    const jokeCount = await page.locator('.joke-card').count();
    expect(jokeCount).toBeGreaterThan(0);
  });
  
  test('can view individual joke', async ({ page }) => {
    await page.goto('/jokes');
    await page.locator('.joke-card').first().click();
    
    await expect(page).toHaveURL(/\/jokes\/joke-\d+/);
    await expect(page.locator('.joke-card')).toBeVisible();
  });
  
  test('can navigate between jokes', async ({ page }) => {
    await page.goto('/jokes/joke-001');
    
    await page.locator('[aria-label="Next joke"]').click();
    await expect(page).toHaveURL(/\/jokes\/joke-\d+/);
  });
  
  test('category filtering works', async ({ page }) => {
    await page.goto('/categories');
    await page.locator('text=Puns').click();
    
    await expect(page).toHaveURL(/\/categories\/puns/);
    await expect(page.locator('.joke-card')).toBeVisible();
  });
  
  test('404 page for invalid routes', async ({ page }) => {
    await page.goto('/invalid-page');
    await expect(page.locator('text=/404/i')).toBeVisible();
  });
  
  test('mobile responsive layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.joke-card')).toBeVisible();
  });
});
```

---

**e2e/performance.spec.js**
```javascript
import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('initial page load under 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(2000);
  });
  
  test('lighthouse performance score above 90', async ({ page }) => {
    await page.goto('/');
    
    const lighthouse = await page.evaluate(() => {
      return new Promise((resolve) => {
        // Trigger lighthouse audit via Chrome DevTools Protocol
        // This is a simplified example
        resolve({ performanceScore: 95 });
      });
    });
    
    expect(lighthouse.performanceScore).toBeGreaterThan(90);
  });
});
```

---

**Test Coverage Goals:**
- Unit tests: >80% coverage for utils and hooks
- Component tests: All major components tested
- Integration tests: Critical user flows covered
- E2E tests: Smoke tests for all pages
- Performance tests: Lighthouse CI on every build

---

## 10. Migration Strategy

<!-- AI: How to migrate from current state to new implementation -->

### Migration Overview

**Current State:** Empty repository with Python-based projects

**Target State:** Add standalone React jokes website in `jokes-website/` directory

**Migration Type:** **Greenfield addition** (no existing code to migrate)

---

### Migration Steps

#### Phase 1: Project Setup (Day 1)

**Step 1.1: Create React Application**
```bash
cd /path/to/repo
npm create vite@latest jokes-website -- --template react
cd jokes-website
npm install
```

**Step 1.2: Install Dependencies**
```bash
npm install react-router-dom
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev jest jest-environment-jsdom
npm install --save-dev eslint eslint-plugin-react
npm install --save-dev @playwright/test
```

**Step 1.3: Configure Vite for S3 Hosting**

Edit `jokes-website/vite.config.js`:
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom']
        }
      }
    }
  },
  server: {
    port: 3000
  }
});
```

**Step 1.4: Update Repository README**

Add section to root `README.md`:
```markdown
## Jokes Website

A static React-based website for browsing jokes, deployed to AWS S3.

- **Location:** `jokes-website/`
- **Documentation:** See [jokes-website/docs/](jokes-website/docs/)
- **Tech Stack:** React, Vite, React Router
- **Deployment:** AWS S3 + CloudFront

### Quick Start
```bash
cd jokes-website
npm install
npm run dev
```
```

---

#### Phase 2: Core Development (Days 2-5)

**Step 2.1: Create Joke Dataset**

Create `jokes-website/public/data/jokes.json` with initial 50+ jokes:
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
    // ... 49 more jokes
  ]
}
```

**Step 2.2: Implement Components**

Follow the file structure defined in section 2, implementing:
1. Layout components (Header, Footer, Layout)
2. JokeCard component
3. Navigation components
4. Page components (Home, JokesList, JokeDetail, Categories)

**Step 2.3: Implement Hooks and Utils**

Implement:
- `useJokes` hook for data loading
- `jokeDataLoader.js` for JSON fetching
- `filterHelpers.js` for filtering logic

**Step 2.4: Add Styling**

Create CSS Modules for each component with mobile-first responsive design.

---

#### Phase 3: Testing (Day 6)

**Step 3.1: Write Unit Tests**

Implement tests as defined in section 9:
- Component tests for JokeCard, CategoryFilter
- Hook tests for useJokes
- Utility tests for filterHelpers, jokeDataLoader

**Step 3.2: Write Integration Tests**

Test critical user flows:
- Joke viewing flow
- Category browsing
- Navigation between jokes

**Step 3.3: Configure Jest**

Create `jokes-website/jest.config.js`:
```javascript
export default {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  }
};
```

---

#### Phase 4: Deployment Setup (Day 7)

**Step 4.1: Create S3 Bucket**

```bash
aws s3 mb s3://jokes-website-prod
aws s3 website s3://jokes-website-prod \
  --index-document index.html \
  --error-document index.html
```

**Step 4.2: Configure Bucket Policy**

Create `deploy/bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::jokes-website-prod/*"
    }
  ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
  --bucket jokes-website-prod \
  --policy file://deploy/bucket-policy.json
```

**Step 4.3: Create CloudFront Distribution**

```bash
aws cloudfront create-distribution \
  --origin-domain-name jokes-website-prod.s3.amazonaws.com \
  --default-root-object index.html
```

**Step 4.4: Set Up GitHub Actions**

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to S3

on:
  push:
    branches: [main]
    paths:
      - 'jokes-website/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: jokes-website/package-lock.json
      
      - name: Install dependencies
        working-directory: jokes-website
        run: npm ci
      
      - name: Run tests
        working-directory: jokes-website
        run: npm test
      
      - name: Build
        working-directory: jokes-website
        run: npm run build
      
      - name: Deploy to S3
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Sync to S3
        working-directory: jokes-website
        run: aws s3 sync dist/ s3://jokes-website-prod --delete
      
      - name: Invalidate CloudFront
        run: aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} --paths "/*"
```

---

#### Phase 5: Launch (Day 8)

**Step 5.1: Final Testing**

- Run E2E tests against staging environment
- Run Lighthouse CI checks
- Test on multiple devices and browsers

**Step 5.2: Deploy to Production**

```bash
cd jokes-website
npm run build
aws s3 sync dist/ s3://jokes-website-prod --delete
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/*"
```

**Step 5.3: Verify Deployment**

- Check website loads at CloudFront URL
- Test all routes and navigation
- Verify Lighthouse score >90
- Confirm load time <2s

---

### Data Migration

**No data migration required** - starting with fresh joke dataset.

**Initial Joke Dataset Creation:**
1. Curate 50+ jokes across 5-7 categories
2. Format as JSON following schema
3. Validate JSON structure
4. Commit to repository in `jokes-website/public/data/`

---

### Configuration Migration

**No existing configuration to migrate.**

**New Configuration Files:**
- `jokes-website/vite.config.js` - Build configuration
- `jokes-website/jest.config.js` - Test configuration
- `.github/workflows/deploy.yml` - CI/CD pipeline
- `deploy/bucket-policy.json` - S3 permissions

---

### User Impact

**No existing users** - this is a new application.

**Launch Communication:**
- Update repository README with jokes-website section
- Add documentation in `jokes-website/docs/`
- Create CHANGELOG.md for future updates

---

## 11. Rollback Plan

<!-- AI: How to rollback if deployment fails -->

### Rollback Strategy

**Objective:** Quickly restore previous working version if deployment issues occur.

---

### Rollback Triggers

**Initiate rollback if:**
1. Critical errors in production (500 errors, site down)
2. Lighthouse performance score drops below 70
3. >10% of users experience load failures
4. Major functionality broken (navigation, joke display)
5. Security vulnerability discovered

---

### Rollback Methods

#### Method 1: S3 Versioning Rollback (Recommended)

**Prerequisites:**
- Enable S3 bucket versioning before first deployment

**Enable Versioning:**
```bash
aws s3api put-bucket-versioning \
  --bucket jokes-website-prod \
  --versioning-configuration Status=Enabled
```

**Rollback Process:**

**Step 1: Identify Previous Version**
```bash
# List object versions
aws s3api list-object-versions \
  --bucket jokes-website-prod \
  --prefix index.html
```

**Step 2: Restore Previous Version**
```bash
# Copy previous version to current
aws s3api copy-object \
  --bucket jokes-website-prod \
  --copy-source jokes-website-prod/index.html?versionId=PREVIOUS_VERSION_ID \
  --key index.html
```

**Step 3: Sync Full Previous Build**
```bash
# If full rollback needed, restore from backup
aws s3 sync s3://jokes-website-backup/build-<timestamp>/ \
  s3://jokes-website-prod/ --delete
```

**Step 4: Invalidate CloudFront Cache**
```bash
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

**Time to Rollback:** 2-5 minutes

---

#### Method 2: Git Revert + Redeploy

**When to Use:** For issues discovered after some time, or when S3 versioning not available.

**Rollback Process:**

**Step 1: Identify Working Commit**
```bash
git log --oneline jokes-website/
# Find last known good commit
```

**Step 2: Revert Code**
```bash
git revert <bad-commit-hash>
# Or
git reset --hard <good-commit-hash>
git push --force origin main
```

**Step 3: Trigger CI/CD Pipeline**
- GitHub Actions will automatically rebuild and deploy
- Or manually trigger workflow

**Time to Rollback:** 5-10 minutes (includes rebuild)

---

#### Method 3: Blue-Green Deployment Rollback

**Setup (before deployment):**

Create two S3 buckets:
- `jokes-website-blue` (current production)
- `jokes-website-green` (new deployment)

CloudFront origin points to blue bucket initially.

**Deployment Process:**
1. Deploy new version to green bucket
2. Test green bucket URL directly
3. If tests pass, switch CloudFront origin to green
4. Blue bucket remains as instant rollback option

**Rollback Process:**

**Step 1: Switch CloudFront Origin**
```bash
aws cloudfront update-distribution \
  --id $DIST_ID \
  --distribution-config file://cloudfront-config-blue.json
```

**Step 2: Invalidate Cache**
```bash
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

**Time to Rollback:** 1-2 minutes (instant origin swap)

---

### Rollback Testing

**Before Production Deployment:**

1. **Test Rollback in Staging:**
   - Deploy v2 to staging
   - Rollback to v1
   - Verify v1 functionality restored

2. **Document Rollback Procedures:**
   - Create runbook with exact commands
   - Store in `jokes-website/docs/ROLLBACK.md`
   - Include credentials/permissions needed

3. **Automate Rollback:**
   ```bash
   # jokes-website/scripts/rollback.sh
   #!/bin/bash
   PREVIOUS_VERSION=$1
   aws s3 sync s3://jokes-website-backup/build-$PREVIOUS_VERSION/ \
     s3://jokes-website-prod/ --delete
   aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
   ```

---

### Monitoring During Rollback

**Key Metrics to Watch:**

1. **CloudFront Error Rate:**
   - Should drop to 0% after rollback
   - Monitor for 5 minutes post-rollback

2. **Cache Hit Rate:**
   - May drop temporarily due to invalidation
   - Should recover to 80%+ within 10 minutes

3. **User Load Times:**
   - Verify <2s load times restored
   - Check from multiple geographic locations

4. **Error Logs:**
   - Monitor browser console errors
   - Check CloudWatch logs for S3 access errors

---

### Communication Plan

**Internal Notification:**
1. Alert team in Slack/Teams: "Rollback initiated"
2. Create incident ticket with details
3. Document rollback reason and steps taken

**User Communication:**
- If site was down <5 minutes: No user notification needed
- If downtime >5 minutes: Post status update on social media
- If data affected: Email affected users (N/A for this static site)

---

### Post-Rollback Actions

**Step 1: Root Cause Analysis**
- Review deployment logs
- Identify what caused the issue
- Document findings in post-mortem

**Step 2: Fix Issues**
- Create hotfix branch
- Implement fixes
- Add tests to prevent regression

**Step 3: Safe Redeployment**
- Deploy fix to staging
- Run full test suite
- Verify Lighthouse scores
- Deploy to production with monitoring

**Step 4: Update Runbooks**
- Document new failure modes
- Update rollback procedures if needed
- Share lessons learned with team

---

### Rollback Decision Matrix

| Issue Severity | Rollback Decision | Timeline |
|----------------|------------------|----------|
| Site completely down | Immediate rollback | <2 min |
| Critical feature broken | Immediate rollback | <5 min |
| Performance degraded (Lighthouse <70) | Rollback recommended | <10 min |
| Minor UI bug | Fix forward, no rollback | N/A |
| Analytics not tracking | Fix forward, no rollback | N/A |
| One joke rendering incorrectly | Fix forward, no rollback | N/A |

---

## 12. Performance Considerations

<!-- AI: Performance optimizations, caching, indexing -->

### Performance Goals

**Targets (from PRD & HLD):**
- Initial page load: <2 seconds on 3G
- Lighthouse performance score: >90
- JavaScript bundle: <500KB gzipped
- Time to Interactive: <3 seconds
- First Contentful Paint: <1.5 seconds

---

### 1. Bundle Size Optimization

**Code Splitting:**

**Implementation in `vite.config.js`:**
```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'router': ['react-router-dom']
        }
      }
    }
  }
});
```

**Route-Based Lazy Loading:**

```jsx
// src/App.jsx
import { lazy, Suspense } from 'react';

const Home = lazy(() => import('./pages/Home/Home'));
const JokesList = lazy(() => import('./pages/JokesList/JokesList'));
const JokeDetail = lazy(() => import('./pages/JokeDetail/JokeDetail'));
const Categories = lazy(() => import('./pages/Categories/Categories'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jokes" element={<JokesList />} />
        {/* ... */}
      </Routes>
    </Suspense>
  );
}
```

**Expected Bundle Sizes:**
- Vendor chunk: ~150KB gzipped
- App code: ~50KB gzipped
- Each route: ~10-20KB gzipped
- Total initial load: ~200KB gzipped

---

### 2. Asset Optimization

**Image Optimization:**
- Use WebP format for all images
- Implement responsive images with srcset
- Lazy load images below fold

```jsx
<img 
  src="icon.webp" 
  loading="lazy"
  srcset="icon-320.webp 320w, icon-640.webp 640w"
  sizes="(max-width: 600px) 320px, 640px"
  alt="Icon"
/>
```

**Font Optimization:**
- Use system fonts (no web fonts initially)
- If custom fonts needed, use font-display: swap
- Subset fonts to include only used characters

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}
```

**CSS Optimization:**
- CSS Modules for automatic tree-shaking
- Minify and compress CSS
- Inline critical CSS (Vite handles automatically)

---

### 3. Data Loading Optimization

**JSON Data Strategy:**

**Option A: Bundle jokes data (for <1MB)**
```javascript
// Import directly in build
import jokesData from '../data/jokes.json';
```
- Pros: No network request, instant availability
- Cons: Increases initial bundle size

**Option B: Lazy load JSON (recommended for >500KB)**
```javascript
// Fetch on demand
fetch('/data/jokes.json')
  .then(res => res.json())
  .then(data => setJokes(data.jokes));
```
- Pros: Smaller initial bundle, progressive loading
- Cons: Additional network request

**Recommendation:** Use Option B with aggressive caching

**Data Pagination (if joke count exceeds 1000):**
```javascript
// Load jokes in chunks
async function loadJokesPage(page = 1, pageSize = 100) {
  const response = await fetch(`/data/jokes-page-${page}.json`);
  return response.json();
}
```

---

### 4. Caching Strategy

**S3 Cache-Control Headers:**

```bash
# Set cache headers during deployment
aws s3 sync dist/ s3://jokes-website-prod \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html"

# index.html with short cache
aws s3 cp dist/index.html s3://jokes-website-prod/index.html \
  --cache-control "public, max-age=300, must-revalidate"
```

**Cache Strategy:**
| File Type | Cache Duration | Rationale |
|-----------|----------------|-----------|
| JS/CSS (hashed) | 1 year | Immutable, hash changes on update |
| Images | 1 year | Static, rarely change |
| index.html | 5 minutes | Entry point, needs fresh version |
| jokes.json | 1 hour | Data file, updates occasionally |

**CloudFront Caching:**
- Enable compression (Gzip + Brotli)
- Cache based on query strings for filtered views
- Set appropriate TTL per file type

**Browser Caching:**
```javascript
// Service worker for offline support (future enhancement)
// Cache jokes data in browser for offline viewing
```

---

### 5. React Performance Optimization

**Memoization:**

```jsx
import { memo, useMemo, useCallback } from 'react';

// Memoize expensive components
const JokeCard = memo(({ joke }) => {
  return <div>{joke.punchline}</div>;
});

// Memoize computed values
function JokesList({ jokes }) {
  const sortedJokes = useMemo(() => {
    return jokes.sort((a, b) => a.id.localeCompare(b.id));
  }, [jokes]);
  
  const handleClick = useCallback((id) => {
    navigate(`/jokes/${id}`);
  }, [navigate]);
  
  return <div>{/* ... */}</div>;
}
```

**Virtual Scrolling (if >500 jokes displayed):**
```jsx
import { FixedSizeList } from 'react-window';

function JokesList({ jokes }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={jokes.length}
      itemSize={200}
    >
      {({ index, style }) => (
        <div style={style}>
          <JokeCard joke={jokes[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

**Avoid Unnecessary Re-renders:**
- Use `React.memo` for pure components
- Keep state as local as possible
- Use `useCallback` for event handlers passed as props

---

### 6. Network Optimization

**HTTP/2 & Compression:**
- CloudFront supports HTTP/2 automatically
- Enable Brotli compression (better than Gzip)

**Resource Hints:**
```html
<!-- index.html -->
<link rel="dns-prefetch" href="//jokes-website-prod.s3.amazonaws.com">
<link rel="preconnect" href="https://cloudfront.net">
<link rel="preload" href="/data/jokes.json" as="fetch" crossorigin>
```

**Reduce Request Count:**
- Bundle CSS into single file per route
- Inline small critical CSS
- Use SVG sprites instead of multiple icon files

---

### 7. Rendering Optimization

**Minimize Layout Thrashing:**
```javascript
// Bad: Forces layout recalculation in loop
jokes.forEach(joke => {
  element.style.height = element.offsetHeight + 10 + 'px';
});

// Good: Batch DOM reads and writes
const heights = jokes.map(joke => element.offsetHeight);
heights.forEach((height, i) => {
  elements[i].style.height = height + 10 + 'px';
});
```

**CSS Containment:**
```css
.joke-card {
  contain: content; /* Isolate layout/paint/style */
}
```

**Avoid Expensive CSS:**
- Minimize box-shadow (performance-intensive)
- Use transform/opacity for animations (GPU-accelerated)
- Avoid complex selectors

```css
/* Good: GPU-accelerated */
.fade-enter {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s, transform 0.3s;
}

/* Avoid: Forces repaints */
.fade-enter {
  height: 0;
  margin-top: -100px;
  transition: height 0.3s, margin 0.3s;
}
```

---

### 8. Performance Monitoring

**Lighthouse CI Integration:**

`.github/workflows/lighthouse.yml`:
```yaml
name: Lighthouse CI

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://staging.jokes-website.com
            https://staging.jokes-website.com/jokes
          uploadArtifacts: true
          temporaryPublicStorage: true
```

**Real User Monitoring:**

```javascript
// src/utils/analytics.js
export function reportWebVitals(metric) {
  // Send to analytics endpoint
  if (window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.value),
      metric_id: metric.id,
      metric_value: metric.value,
      metric_delta: metric.delta
    });
  }
}
```

```jsx
// src/main.jsx
import { reportWebVitals } from './utils/analytics';
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(reportWebVitals);
getFID(reportWebVitals);
getLCP(reportWebVitals);
```

**Performance Budget:**

`jokes-website/budget.json`:
```json
{
  "timings": [
    {
      "metric": "first-contentful-paint",
      "budget": 1500
    },
    {
      "metric": "interactive",
      "budget": 3000
    }
  ],
  "resourceSizes": [
    {
      "resourceType": "script",
      "budget": 500
    },
    {
      "resourceType": "total",
      "budget": 1000
    }
  ]
}
```

---

### 9. Performance Checklist

**Build-Time Optimizations:**
- ✅ Code splitting by route
- ✅ Minify JavaScript and CSS
- ✅ Tree-shake unused code
- ✅ Compress images
- ✅ Generate source maps for debugging only
- ✅ Hash filenames for cache busting

**Runtime Optimizations:**
- ✅ Lazy load routes with React.lazy
- ✅ Memoize expensive computations
- ✅ Use React.memo for pure components
- ✅ Debounce search inputs
- ✅ Virtual scrolling for long lists
- ✅ Optimize images with loading="lazy"

**Network Optimizations:**
- ✅ Enable HTTP/2 and compression
- ✅ Set appropriate cache headers
- ✅ Use CDN (CloudFront)
- ✅ Minimize number of requests
- ✅ Preload critical resources

**Monitoring:**
- ✅ Lighthouse CI in pipeline
- ✅ Real User Monitoring (RUM)
- ✅ Performance budget enforcement
- ✅ CloudWatch metrics for S3/CloudFront

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
    health-check/
      HLD.md
      LLD.md
      PRD.md
    jokes-website/
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
