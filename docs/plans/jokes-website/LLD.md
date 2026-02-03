# Low-Level Design: aiworkshop

**Created:** 2026-02-03T11:01:15Z
**Status:** Draft

## 1. Implementation Overview

<!-- AI: Brief summary of implementation approach -->

This implementation will create a new React-based static website within the existing repository structure. The jokes website will be built as a standalone frontend application under a new `jokes-website/` directory in the project root. The implementation follows these key steps:

1. **Project Setup**: Initialize a new Vite-based React application with modern tooling (ESLint, Prettier) in `jokes-website/`
2. **Component Development**: Build reusable React components following atomic design principles with functional components and hooks
3. **Static Data Integration**: Create a structured JSON data file containing 20-50 jokes with categories and metadata
4. **Client-Side Routing**: Implement React Router v6 for navigation between home, joke listing, individual jokes, and category views
5. **Responsive Styling**: Use CSS Modules for component-scoped styling with mobile-first responsive design
6. **Build Optimization**: Configure Vite for optimal production builds with code splitting, tree shaking, and asset optimization
7. **S3 Deployment**: Create deployment scripts and GitHub Actions workflow for automated deployment to S3
8. **Testing**: Implement unit tests with Vitest and React Testing Library, plus E2E tests with Playwright

The application will be completely self-contained with no external dependencies beyond the React ecosystem. All jokes data will be embedded in the build, eliminating runtime dependencies. The architecture leverages React's component model for maintainability while keeping the implementation simple and focused on the core requirements.

---

## 2. File Structure

<!-- AI: List all new and modified files with descriptions -->

```
jokes-website/                          # New React application root
├── public/                             # Static assets served as-is
│   ├── favicon.ico                     # Website favicon
│   ├── robots.txt                      # SEO crawler instructions
│   └── site.webmanifest               # PWA manifest (optional)
├── src/                                # Source code directory
│   ├── components/                     # React components
│   │   ├── layout/                     # Layout components
│   │   │   ├── Header.jsx              # Site header with navigation
│   │   │   ├── Header.module.css       # Header styles
│   │   │   ├── Footer.jsx              # Site footer
│   │   │   ├── Footer.module.css       # Footer styles
│   │   │   ├── Layout.jsx              # Main layout wrapper
│   │   │   └── Layout.module.css       # Layout styles
│   │   ├── jokes/                      # Joke-related components
│   │   │   ├── JokeCard.jsx            # Individual joke display card
│   │   │   ├── JokeCard.module.css     # Joke card styles
│   │   │   ├── JokeList.jsx            # List of jokes in grid/list view
│   │   │   ├── JokeList.module.css     # Joke list styles
│   │   │   ├── JokeNavigation.jsx      # Next/Previous/Random navigation
│   │   │   └── JokeNavigation.module.css # Navigation styles
│   │   ├── categories/                 # Category-related components
│   │   │   ├── CategoryCard.jsx        # Category display card
│   │   │   ├── CategoryCard.module.css # Category card styles
│   │   │   ├── CategoryList.jsx        # Grid of category cards
│   │   │   └── CategoryList.module.css # Category list styles
│   │   └── common/                     # Shared/common components
│   │       ├── ErrorBoundary.jsx       # React error boundary
│   │       ├── NotFound.jsx            # 404 page component
│   │       └── NotFound.module.css     # 404 page styles
│   ├── pages/                          # Page-level components
│   │   ├── HomePage.jsx                # Home/landing page
│   │   ├── HomePage.module.css         # Home page styles
│   │   ├── JokePage.jsx                # Individual joke view page
│   │   ├── JokePage.module.css         # Joke page styles
│   │   ├── BrowsePage.jsx              # Browse all jokes page
│   │   ├── BrowsePage.module.css       # Browse page styles
│   │   ├── CategoryPage.jsx            # Jokes by category page
│   │   └── CategoryPage.module.css     # Category page styles
│   ├── data/                           # Static data files
│   │   ├── jokes.json                  # Main jokes data (20-50 jokes)
│   │   └── categories.json             # Category metadata
│   ├── hooks/                          # Custom React hooks
│   │   ├── useJokes.js                 # Hook for accessing joke data
│   │   └── useCategories.js            # Hook for category operations
│   ├── utils/                          # Utility functions
│   │   ├── jokeHelpers.js              # Joke filtering and sorting
│   │   └── navigation.js               # Navigation helper functions
│   ├── styles/                         # Global styles
│   │   ├── global.css                  # Global CSS reset and variables
│   │   └── variables.css               # CSS custom properties
│   ├── App.jsx                         # Root application component
│   ├── App.css                         # Root application styles
│   ├── main.jsx                        # Application entry point
│   └── router.jsx                      # React Router configuration
├── tests/                              # Test files
│   ├── unit/                           # Unit tests
│   │   ├── components/                 # Component unit tests
│   │   │   ├── JokeCard.test.jsx       # JokeCard component tests
│   │   │   ├── JokeList.test.jsx       # JokeList component tests
│   │   │   └── CategoryCard.test.jsx   # CategoryCard component tests
│   │   ├── hooks/                      # Hook unit tests
│   │   │   └── useJokes.test.js        # useJokes hook tests
│   │   └── utils/                      # Utility function tests
│   │       └── jokeHelpers.test.js     # Joke helper tests
│   ├── integration/                    # Integration tests
│   │   └── navigation.test.jsx         # Route navigation tests
│   └── e2e/                            # End-to-end tests
│       ├── homepage.spec.js            # Home page E2E tests
│       ├── browsing.spec.js            # Joke browsing E2E tests
│       └── categories.spec.js          # Category filtering E2E tests
├── .github/                            # GitHub configuration
│   └── workflows/                      # GitHub Actions workflows
│       └── deploy.yml                  # S3 deployment workflow
├── scripts/                            # Build and deployment scripts
│   ├── deploy-s3.sh                    # S3 deployment script
│   └── build-prod.sh                   # Production build script
├── .gitignore                          # Git ignore file
├── package.json                        # NPM dependencies and scripts
├── package-lock.json                   # NPM dependency lock file
├── vite.config.js                      # Vite build configuration
├── vitest.config.js                    # Vitest test configuration
├── playwright.config.js                # Playwright E2E test config
├── .eslintrc.json                      # ESLint configuration
├── .prettierrc                         # Prettier configuration
└── README.md                           # Project documentation

docs/plans/jokes-website/               # Existing documentation (modified)
├── HLD.md                              # High-level design (existing)
├── LLD.md                              # This file
├── PRD.md                              # Product requirements (existing)
├── ROAM.md                             # ROAM document (existing)
├── IMPLEMENTATION.md                   # New: Implementation guide
└── DEPLOYMENT.md                       # New: Deployment instructions

README.md                               # Root README (modified)
└── Add link to jokes-website project
```

**Key Files Summary:**

**New Directories:**
- `jokes-website/`: Complete React application for the jokes website
- `jokes-website/src/components/`: Reusable UI components
- `jokes-website/src/pages/`: Page-level route components
- `jokes-website/src/data/`: Static JSON data files
- `jokes-website/tests/`: Comprehensive test suite

**Modified Files:**
- `README.md`: Add section about jokes-website subproject
- `docs/plans/jokes-website/LLD.md`: This document

**Configuration Files:**
- `vite.config.js`: Vite bundler configuration with optimizations
- `vitest.config.js`: Unit test runner configuration
- `playwright.config.js`: E2E test framework configuration
- `.eslintrc.json`: Code quality rules
- `.prettierrc`: Code formatting rules

---

## 3. Detailed Component Designs

<!-- AI: For each major component from HLD, provide detailed design -->

### 3.1 Layout Components

#### **Header Component** (`src/components/layout/Header.jsx`)

```jsx
/**
 * Header component with site branding and navigation
 * Responsive with hamburger menu on mobile
 */
import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);
  const closeMobileMenu = () => setMobileMenuOpen(false);

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          😂 JokesHub
        </Link>
        
        <button 
          className={styles.hamburger}
          onClick={toggleMobileMenu}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <nav className={`${styles.nav} ${mobileMenuOpen ? styles.open : ''}`}>
          <NavLink to="/" onClick={closeMobileMenu}>Home</NavLink>
          <NavLink to="/browse" onClick={closeMobileMenu}>Browse</NavLink>
          <NavLink to="/categories" onClick={closeMobileMenu}>Categories</NavLink>
        </nav>
      </div>
    </header>
  );
}
```

**Styling** (`Header.module.css`):
- Mobile-first responsive design
- Hamburger menu for screens < 768px
- Smooth transitions for menu open/close
- Active link highlighting with NavLink

---

#### **Layout Component** (`src/components/layout/Layout.jsx`)

```jsx
/**
 * Main layout wrapper for all pages
 * Includes header, footer, and content area with error boundary
 */
import Header from './Header';
import Footer from './Footer';
import ErrorBoundary from '../common/ErrorBoundary';
import styles from './Layout.module.css';

export default function Layout({ children }) {
  return (
    <div className={styles.layout}>
      <Header />
      <ErrorBoundary>
        <main className={styles.main}>
          {children}
        </main>
      </ErrorBoundary>
      <Footer />
    </div>
  );
}
```

**Features:**
- Flexbox sticky footer layout
- Error boundary wraps main content
- Consistent spacing and max-width container
- Semantic HTML5 structure

---

### 3.2 Joke Display Components

#### **JokeCard Component** (`src/components/jokes/JokeCard.jsx`)

```jsx
/**
 * Displays a single joke with setup/punchline formatting
 * Props: joke object, variant (compact, full, featured)
 */
import { Link } from 'react-router-dom';
import styles from './JokeCard.module.css';

export default function JokeCard({ joke, variant = 'full', showLink = true }) {
  const { id, setup, punchline, category } = joke;

  return (
    <article className={`${styles.card} ${styles[variant]}`}>
      <div className={styles.content}>
        <p className={styles.setup}>{setup}</p>
        <p className={styles.punchline}>{punchline}</p>
      </div>
      
      <div className={styles.meta}>
        <span className={styles.category}>{category}</span>
        {showLink && (
          <Link to={`/jokes/${id}`} className={styles.link}>
            View →
          </Link>
        )}
      </div>
    </article>
  );
}
```

**Props Interface:**
- `joke`: Object { id, setup, punchline, category, tags?, dateAdded? }
- `variant`: String enum ['compact', 'full', 'featured']
- `showLink`: Boolean (default true)

**Variants:**
- `compact`: Smaller card for grid layouts
- `full`: Standard card with all details
- `featured`: Hero-style card for homepage

---

#### **JokeList Component** (`src/components/jokes/JokeList.jsx`)

```jsx
/**
 * Displays a grid or list of joke cards
 * Supports filtering and sorting
 */
import JokeCard from './JokeCard';
import styles from './JokeList.module.css';

export default function JokeList({ 
  jokes, 
  variant = 'compact', 
  layout = 'grid',
  emptyMessage = 'No jokes found.'
}) {
  if (!jokes || jokes.length === 0) {
    return <p className={styles.empty}>{emptyMessage}</p>;
  }

  return (
    <div className={`${styles.list} ${styles[layout]}`}>
      {jokes.map(joke => (
        <JokeCard 
          key={joke.id} 
          joke={joke} 
          variant={variant}
        />
      ))}
    </div>
  );
}
```

**Props Interface:**
- `jokes`: Array of joke objects
- `variant`: String enum ['compact', 'full']
- `layout`: String enum ['grid', 'list']
- `emptyMessage`: String (default shown)

**CSS Grid Layout:**
- Grid: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)
- List: Single column with wider cards
- Gap spacing: 1.5rem

---

#### **JokeNavigation Component** (`src/components/jokes/JokeNavigation.jsx`)

```jsx
/**
 * Navigation controls for browsing jokes
 * Next, Previous, and Random buttons
 */
import { useNavigate } from 'react-router-dom';
import { getNextJoke, getPreviousJoke, getRandomJoke } from '../../utils/jokeHelpers';
import styles from './JokeNavigation.module.css';

export default function JokeNavigation({ currentJokeId, jokes }) {
  const navigate = useNavigate();

  const handleNext = () => {
    const nextJoke = getNextJoke(currentJokeId, jokes);
    if (nextJoke) navigate(`/jokes/${nextJoke.id}`);
  };

  const handlePrevious = () => {
    const prevJoke = getPreviousJoke(currentJokeId, jokes);
    if (prevJoke) navigate(`/jokes/${prevJoke.id}`);
  };

  const handleRandom = () => {
    const randomJoke = getRandomJoke(jokes, currentJokeId);
    if (randomJoke) navigate(`/jokes/${randomJoke.id}`);
  };

  return (
    <nav className={styles.navigation}>
      <button onClick={handlePrevious} className={styles.button}>
        ← Previous
      </button>
      <button onClick={handleRandom} className={styles.buttonRandom}>
        🎲 Random
      </button>
      <button onClick={handleNext} className={styles.button}>
        Next →
      </button>
    </nav>
  );
}
```

**Features:**
- Circular navigation (wraps around)
- Random joke excludes current joke
- Keyboard navigation support (arrow keys)
- Disabled state for single joke scenario

---

### 3.3 Category Components

#### **CategoryCard Component** (`src/components/categories/CategoryCard.jsx`)

```jsx
/**
 * Displays a category with joke count and description
 */
import { Link } from 'react-router-dom';
import styles from './CategoryCard.module.css';

export default function CategoryCard({ category }) {
  const { id, name, description, jokeCount } = category;

  return (
    <Link to={`/categories/${id}`} className={styles.card}>
      <h3 className={styles.name}>{name}</h3>
      <p className={styles.description}>{description}</p>
      <span className={styles.count}>{jokeCount} jokes</span>
    </Link>
  );
}
```

**Features:**
- Entire card is clickable link
- Hover state with transform effect
- Badge showing joke count
- Accessible with keyboard focus styles

---

#### **CategoryList Component** (`src/components/categories/CategoryList.jsx`)

```jsx
/**
 * Grid of category cards
 */
import CategoryCard from './CategoryCard';
import styles from './CategoryList.module.css';

export default function CategoryList({ categories }) {
  return (
    <div className={styles.grid}>
      {categories.map(category => (
        <CategoryCard key={category.id} category={category} />
      ))}
    </div>
  );
}
```

**CSS Grid:**
- 1 column (mobile)
- 2 columns (tablet, ≥ 640px)
- 3 columns (desktop, ≥ 1024px)
- Equal height cards with flexbox

---

### 3.4 Page Components

#### **HomePage Component** (`src/pages/HomePage.jsx`)

```jsx
/**
 * Landing page with featured joke and category overview
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import JokeCard from '../components/jokes/JokeCard';
import CategoryList from '../components/categories/CategoryList';
import { useJokes } from '../hooks/useJokes';
import { useCategories } from '../hooks/useCategories';
import { getRandomJoke } from '../utils/jokeHelpers';
import styles from './HomePage.module.css';

export default function HomePage() {
  const { jokes } = useJokes();
  const { categories } = useCategories();
  const [featuredJoke, setFeaturedJoke] = useState(null);

  useEffect(() => {
    if (jokes.length > 0) {
      setFeaturedJoke(getRandomJoke(jokes));
    }
  }, [jokes]);

  const handleNewJoke = () => {
    setFeaturedJoke(getRandomJoke(jokes, featuredJoke?.id));
  };

  return (
    <div className={styles.home}>
      <section className={styles.hero}>
        <h1>Welcome to JokesHub</h1>
        <p className={styles.tagline}>
          Your daily dose of laughter, one joke at a time
        </p>
      </section>

      {featuredJoke && (
        <section className={styles.featured}>
          <h2>Joke of the Moment</h2>
          <JokeCard joke={featuredJoke} variant="featured" showLink={false} />
          <button onClick={handleNewJoke} className={styles.refreshButton}>
            Show Another
          </button>
        </section>
      )}

      <section className={styles.categories}>
        <h2>Browse by Category</h2>
        <CategoryList categories={categories} />
      </section>

      <section className={styles.cta}>
        <Link to="/browse" className={styles.ctaButton}>
          Browse All Jokes →
        </Link>
      </section>
    </div>
  );
}
```

---

#### **JokePage Component** (`src/pages/JokePage.jsx`)

```jsx
/**
 * Individual joke view page with navigation
 */
import { useParams } from 'react-router-dom';
import JokeCard from '../components/jokes/JokeCard';
import JokeNavigation from '../components/jokes/JokeNavigation';
import NotFound from '../components/common/NotFound';
import { useJokes } from '../hooks/useJokes';
import styles from './JokePage.module.css';

export default function JokePage() {
  const { id } = useParams();
  const { jokes, getJokeById } = useJokes();
  const joke = getJokeById(id);

  if (!joke) {
    return <NotFound message="Joke not found" />;
  }

  return (
    <div className={styles.page}>
      <JokeCard joke={joke} variant="full" showLink={false} />
      <JokeNavigation currentJokeId={id} jokes={jokes} />
    </div>
  );
}
```

---

#### **BrowsePage Component** (`src/pages/BrowsePage.jsx`)

```jsx
/**
 * Browse all jokes with filtering and sorting
 */
import { useState } from 'react';
import JokeList from '../components/jokes/JokeList';
import { useJokes } from '../hooks/useJokes';
import { useCategories } from '../hooks/useCategories';
import styles from './BrowsePage.module.css';

export default function BrowsePage() {
  const { jokes } = useJokes();
  const { categories } = useCategories();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredJokes = selectedCategory === 'all' 
    ? jokes 
    : jokes.filter(j => j.category === selectedCategory);

  return (
    <div className={styles.page}>
      <h1>Browse All Jokes</h1>
      
      <div className={styles.filters}>
        <label htmlFor="category-filter">Filter by category:</label>
        <select 
          id="category-filter"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className={styles.select}
        >
          <option value="all">All Categories</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name} ({cat.jokeCount})
            </option>
          ))}
        </select>
      </div>

      <p className={styles.count}>
        Showing {filteredJokes.length} joke{filteredJokes.length !== 1 ? 's' : ''}
      </p>

      <JokeList jokes={filteredJokes} layout="grid" />
    </div>
  );
}
```

---

#### **CategoryPage Component** (`src/pages/CategoryPage.jsx`)

```jsx
/**
 * Jokes filtered by specific category
 */
import { useParams } from 'react-router-dom';
import JokeList from '../components/jokes/JokeList';
import NotFound from '../components/common/NotFound';
import { useJokes } from '../hooks/useJokes';
import { useCategories } from '../hooks/useCategories';
import styles from './CategoryPage.module.css';

export default function CategoryPage() {
  const { categoryId } = useParams();
  const { jokes } = useJokes();
  const { getCategoryById } = useCategories();
  
  const category = getCategoryById(categoryId);
  const categoryJokes = jokes.filter(j => j.category === categoryId);

  if (!category) {
    return <NotFound message="Category not found" />;
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>{category.name}</h1>
        <p>{category.description}</p>
        <span className={styles.count}>{categoryJokes.length} jokes</span>
      </header>

      <JokeList jokes={categoryJokes} layout="grid" />
    </div>
  );
}
```

---

### 3.5 Common Components

#### **ErrorBoundary Component** (`src/components/common/ErrorBoundary.jsx`)

```jsx
/**
 * React error boundary to catch and display errors gracefully
 */
import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Oops! Something went wrong.</h2>
          <p>We're sorry for the inconvenience. Please refresh the page.</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

#### **NotFound Component** (`src/components/common/NotFound.jsx`)

```jsx
/**
 * 404 Not Found page
 */
import { Link } from 'react-router-dom';
import styles from './NotFound.module.css';

export default function NotFound({ message = 'Page not found' }) {
  return (
    <div className={styles.notFound}>
      <h1>404</h1>
      <p>{message}</p>
      <Link to="/" className={styles.homeLink}>
        Go Back Home
      </Link>
    </div>
  );
}
```

---

## 4. Database Schema Changes

<!-- AI: SQL/migration scripts for schema changes -->

**N/A - No Database Required**

This application is a static frontend with no database. All data is stored as JSON files and embedded in the JavaScript bundle at build time.

### Data Storage Approach

Instead of database tables, we use structured JSON files:

**File: `src/data/jokes.json`**
```json
[
  {
    "id": "joke-001",
    "setup": "Why don't scientists trust atoms?",
    "punchline": "Because they make up everything!",
    "category": "science",
    "tags": ["science", "chemistry", "puns"],
    "dateAdded": "2026-01-15"
  },
  {
    "id": "joke-002",
    "setup": "What do you call a bear with no teeth?",
    "punchline": "A gummy bear!",
    "category": "animals",
    "tags": ["animals", "wordplay"],
    "dateAdded": "2026-01-16"
  }
  // ... 18-48 more jokes
]
```

**File: `src/data/categories.json`**
```json
[
  {
    "id": "dad-jokes",
    "name": "Dad Jokes",
    "description": "Classic groan-worthy jokes your dad would tell"
  },
  {
    "id": "puns",
    "name": "Puns",
    "description": "Clever wordplay that will make you smile (or groan)"
  },
  {
    "id": "one-liners",
    "name": "One-Liners",
    "description": "Quick jokes that pack a punch"
  },
  {
    "id": "science",
    "name": "Science Jokes",
    "description": "Jokes for the scientifically inclined"
  },
  {
    "id": "animals",
    "name": "Animal Jokes",
    "description": "Jokes about our furry, feathered, and scaly friends"
  }
]
```

### Data Validation Schema

While not a database, we can define TypeScript interfaces (if using TypeScript) or JSDoc types for validation:

```javascript
/**
 * @typedef {Object} Joke
 * @property {string} id - Unique identifier (format: "joke-XXX")
 * @property {string} setup - Joke setup or question
 * @property {string} punchline - Joke punchline or answer
 * @property {string} category - Category ID (must match categories.json)
 * @property {string[]} [tags] - Optional array of tags
 * @property {string} dateAdded - ISO date string (YYYY-MM-DD)
 */

/**
 * @typedef {Object} Category
 * @property {string} id - Category identifier (kebab-case)
 * @property {string} name - Display name
 * @property {string} description - Brief description
 */
```

### Data Management

**Adding New Jokes:**
1. Edit `src/data/jokes.json`
2. Add new joke object with sequential ID
3. Ensure category exists in `categories.json`
4. Rebuild and redeploy application

**No Migration Scripts Needed:**
- Data is statically imported at build time
- No versioning or migration logic required
- Changes require full rebuild and deployment

---

## 5. API Implementation Details

<!-- AI: For each API endpoint, specify handler logic, validation, error handling -->

**N/A - No Backend API**

This is a purely static frontend application with no backend API endpoints. However, the application defines internal data access patterns through custom React hooks that serve as the "API" layer for components.

### Internal Data Access Layer

#### **useJokes Hook** (`src/hooks/useJokes.js`)

This hook serves as the primary interface for accessing joke data throughout the application.

```javascript
/**
 * Custom hook for accessing and manipulating joke data
 * Returns jokes array and utility functions
 */
import { useMemo } from 'react';
import jokesData from '../data/jokes.json';

export function useJokes() {
  const jokes = useMemo(() => jokesData, []);

  const getJokeById = (id) => {
    return jokes.find(joke => joke.id === id) || null;
  };

  const getJokesByCategory = (categoryId) => {
    return jokes.filter(joke => joke.category === categoryId);
  };

  const getJokesByTag = (tag) => {
    return jokes.filter(joke => joke.tags?.includes(tag));
  };

  const searchJokes = (query) => {
    const lowerQuery = query.toLowerCase();
    return jokes.filter(joke => 
      joke.setup.toLowerCase().includes(lowerQuery) ||
      joke.punchline.toLowerCase().includes(lowerQuery)
    );
  };

  return {
    jokes,
    getJokeById,
    getJokesByCategory,
    getJokesByTag,
    searchJokes,
    totalCount: jokes.length
  };
}
```

**Return Interface:**
- `jokes`: Array<Joke> - All jokes
- `getJokeById(id)`: Joke | null
- `getJokesByCategory(categoryId)`: Array<Joke>
- `getJokesByTag(tag)`: Array<Joke>
- `searchJokes(query)`: Array<Joke>
- `totalCount`: number

**Error Handling:**
- Returns `null` for missing jokes
- Returns empty array for no matches
- Handles malformed JSON gracefully (try-catch in import)

---

#### **useCategories Hook** (`src/hooks/useCategories.js`)

```javascript
/**
 * Custom hook for accessing category data and computing counts
 */
import { useMemo } from 'react';
import categoriesData from '../data/categories.json';
import jokesData from '../data/jokes.json';

export function useCategories() {
  const categories = useMemo(() => {
    // Compute joke counts for each category
    return categoriesData.map(category => ({
      ...category,
      jokeCount: jokesData.filter(j => j.category === category.id).length
    }));
  }, []);

  const getCategoryById = (id) => {
    return categories.find(cat => cat.id === id) || null;
  };

  const getCategoryByName = (name) => {
    return categories.find(cat => 
      cat.name.toLowerCase() === name.toLowerCase()
    ) || null;
  };

  return {
    categories,
    getCategoryById,
    getCategoryByName,
    totalCount: categories.length
  };
}
```

**Return Interface:**
- `categories`: Array<CategoryWithCount>
- `getCategoryById(id)`: Category | null
- `getCategoryByName(name)`: Category | null
- `totalCount`: number

---

### Client-Side Routing (Internal "Endpoints")

#### **Router Configuration** (`src/router.jsx`)

```javascript
import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import BrowsePage from './pages/BrowsePage';
import JokePage from './pages/JokePage';
import CategoryPage from './pages/CategoryPage';
import NotFound from './components/common/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <Layout><NotFound /></Layout>,
    children: [
      {
        index: true,
        element: <HomePage />
      },
      {
        path: 'browse',
        element: <BrowsePage />
      },
      {
        path: 'jokes/:id',
        element: <JokePage />
      },
      {
        path: 'categories',
        element: <CategoryList />
      },
      {
        path: 'categories/:categoryId',
        element: <CategoryPage />
      },
      {
        path: '*',
        element: <NotFound />
      }
    ]
  }
]);
```

**Route Definitions:**
- `GET /` → HomePage (featured joke, category overview)
- `GET /browse` → BrowsePage (all jokes with filters)
- `GET /jokes/:id` → JokePage (individual joke detail)
- `GET /categories` → Categories listing
- `GET /categories/:categoryId` → CategoryPage (jokes by category)
- `GET /*` → NotFound (404 page)

**Error Handling:**
- Invalid joke IDs render NotFound component
- Invalid category IDs render NotFound component
- React Router catches all routing errors
- ErrorBoundary catches component render errors

---

## 6. Function Signatures

<!-- AI: Key function/method signatures with parameters and return types -->

### Utility Functions

#### **jokeHelpers.js** (`src/utils/jokeHelpers.js`)

```javascript
/**
 * Get the next joke in the array (circular)
 * @param {string} currentId - Current joke ID
 * @param {Array<Joke>} jokes - Array of all jokes
 * @returns {Joke|null} Next joke or null if jokes array empty
 */
export function getNextJoke(currentId, jokes) {
  if (!jokes || jokes.length === 0) return null;
  const currentIndex = jokes.findIndex(j => j.id === currentId);
  const nextIndex = (currentIndex + 1) % jokes.length;
  return jokes[nextIndex];
}

/**
 * Get the previous joke in the array (circular)
 * @param {string} currentId - Current joke ID
 * @param {Array<Joke>} jokes - Array of all jokes
 * @returns {Joke|null} Previous joke or null if jokes array empty
 */
export function getPreviousJoke(currentId, jokes) {
  if (!jokes || jokes.length === 0) return null;
  const currentIndex = jokes.findIndex(j => j.id === currentId);
  const prevIndex = currentIndex === 0 ? jokes.length - 1 : currentIndex - 1;
  return jokes[prevIndex];
}

/**
 * Get a random joke, optionally excluding current joke
 * @param {Array<Joke>} jokes - Array of all jokes
 * @param {string} [excludeId] - Optional joke ID to exclude
 * @returns {Joke|null} Random joke or null if no valid jokes
 */
export function getRandomJoke(jokes, excludeId = null) {
  if (!jokes || jokes.length === 0) return null;
  
  const availableJokes = excludeId 
    ? jokes.filter(j => j.id !== excludeId)
    : jokes;
  
  if (availableJokes.length === 0) return jokes[0]; // Fallback
  
  const randomIndex = Math.floor(Math.random() * availableJokes.length);
  return availableJokes[randomIndex];
}

/**
 * Sort jokes by date added (newest first)
 * @param {Array<Joke>} jokes - Array of jokes to sort
 * @returns {Array<Joke>} Sorted array
 */
export function sortJokesByDate(jokes) {
  return [...jokes].sort((a, b) => 
    new Date(b.dateAdded) - new Date(a.dateAdded)
  );
}

/**
 * Filter jokes by search query
 * @param {Array<Joke>} jokes - Array of jokes
 * @param {string} query - Search query string
 * @returns {Array<Joke>} Filtered jokes
 */
export function filterJokesByQuery(jokes, query) {
  if (!query) return jokes;
  const lowerQuery = query.toLowerCase().trim();
  return jokes.filter(joke =>
    joke.setup.toLowerCase().includes(lowerQuery) ||
    joke.punchline.toLowerCase().includes(lowerQuery) ||
    joke.category.toLowerCase().includes(lowerQuery) ||
    joke.tags?.some(tag => tag.toLowerCase().includes(lowerQuery))
  );
}

/**
 * Group jokes by category
 * @param {Array<Joke>} jokes - Array of jokes
 * @returns {Object<string, Array<Joke>>} Object with category keys
 */
export function groupJokesByCategory(jokes) {
  return jokes.reduce((acc, joke) => {
    if (!acc[joke.category]) {
      acc[joke.category] = [];
    }
    acc[joke.category].push(joke);
    return acc;
  }, {});
}
```

---

#### **navigation.js** (`src/utils/navigation.js`)

```javascript
/**
 * Build URL for joke page
 * @param {string} jokeId - Joke ID
 * @returns {string} URL path
 */
export function getJokeUrl(jokeId) {
  return `/jokes/${jokeId}`;
}

/**
 * Build URL for category page
 * @param {string} categoryId - Category ID
 * @returns {string} URL path
 */
export function getCategoryUrl(categoryId) {
  return `/categories/${categoryId}`;
}

/**
 * Extract joke ID from pathname
 * @param {string} pathname - Current URL pathname
 * @returns {string|null} Joke ID or null
 */
export function extractJokeIdFromPath(pathname) {
  const match = pathname.match(/^\/jokes\/(.+)$/);
  return match ? match[1] : null;
}

/**
 * Extract category ID from pathname
 * @param {string} pathname - Current URL pathname
 * @returns {string|null} Category ID or null
 */
export function extractCategoryIdFromPath(pathname) {
  const match = pathname.match(/^\/categories\/(.+)$/);
  return match ? match[1] : null;
}
```

---

### Component Props Interfaces

```javascript
/**
 * JokeCard Props
 * @typedef {Object} JokeCardProps
 * @property {Joke} joke - Joke object to display
 * @property {'compact'|'full'|'featured'} [variant='full'] - Display variant
 * @property {boolean} [showLink=true] - Show link to joke page
 */

/**
 * JokeList Props
 * @typedef {Object} JokeListProps
 * @property {Array<Joke>} jokes - Array of jokes to display
 * @property {'compact'|'full'} [variant='compact'] - Card variant
 * @property {'grid'|'list'} [layout='grid'] - Layout mode
 * @property {string} [emptyMessage='No jokes found.'] - Message when empty
 */

/**
 * JokeNavigation Props
 * @typedef {Object} JokeNavigationProps
 * @property {string} currentJokeId - Current joke ID
 * @property {Array<Joke>} jokes - All jokes for navigation
 */

/**
 * CategoryCard Props
 * @typedef {Object} CategoryCardProps
 * @property {Category} category - Category object with jokeCount
 */

/**
 * CategoryList Props
 * @typedef {Object} CategoryListProps
 * @property {Array<Category>} categories - Array of categories
 */
```

---

### Custom Hook Return Types

```javascript
/**
 * useJokes Hook Return
 * @typedef {Object} UseJokesReturn
 * @property {Array<Joke>} jokes - All jokes
 * @property {function(string): Joke|null} getJokeById - Get joke by ID
 * @property {function(string): Array<Joke>} getJokesByCategory - Get jokes by category
 * @property {function(string): Array<Joke>} getJokesByTag - Get jokes by tag
 * @property {function(string): Array<Joke>} searchJokes - Search jokes
 * @property {number} totalCount - Total number of jokes
 */

/**
 * useCategories Hook Return
 * @typedef {Object} UseCategoriesReturn
 * @property {Array<Category>} categories - All categories with counts
 * @property {function(string): Category|null} getCategoryById - Get category by ID
 * @property {function(string): Category|null} getCategoryByName - Get by name
 * @property {number} totalCount - Total number of categories
 */
```

---

## 7. State Management

<!-- AI: How application state is managed (Redux, Context, database) -->

### State Management Strategy

This application uses **React's built-in state management** without external libraries like Redux or Zustand. The state architecture is simple and leverages:

1. **Custom Hooks** for data access (useJokes, useCategories)
2. **Component-level state** with `useState` for UI state
3. **URL state** via React Router for navigation state
4. **No global state** needed (all data is static and immutable)

---

### State Categories

#### **1. Static Data State (Immutable)**

Managed by custom hooks that import JSON data:

```javascript
// src/hooks/useJokes.js
import jokesData from '../data/jokes.json';

export function useJokes() {
  // Data is imported once at module level
  // useMemo ensures referential stability
  const jokes = useMemo(() => jokesData, []);
  
  // All operations are pure functions, no mutations
  return { jokes, /* ...utility functions */ };
}
```

**Characteristics:**
- Data loaded once at build time
- Immutable throughout application lifecycle
- Shared across all components without prop drilling
- No re-renders caused by data changes (data never changes)

---

#### **2. UI State (Component-level)**

Managed with `useState` within individual components:

**Example: HomePage**
```javascript
export default function HomePage() {
  const { jokes } = useJokes();
  
  // Local UI state for featured joke
  const [featuredJoke, setFeaturedJoke] = useState(null);
  
  // Initialize on mount
  useEffect(() => {
    setFeaturedJoke(getRandomJoke(jokes));
  }, [jokes]);
  
  // Update local state on user action
  const handleNewJoke = () => {
    setFeaturedJoke(getRandomJoke(jokes, featuredJoke?.id));
  };
  
  return (/* JSX using featuredJoke state */);
}
```

**Example: Header Navigation**
```javascript
export default function Header() {
  // Local state for mobile menu open/close
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);
  
  return (/* JSX using mobileMenuOpen state */);
}
```

**Example: BrowsePage Filters**
```javascript
export default function BrowsePage() {
  const { jokes } = useJokes();
  
  // Local state for filter selection
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // Derived state (computed from local state)
  const filteredJokes = selectedCategory === 'all'
    ? jokes
    : jokes.filter(j => j.category === selectedCategory);
  
  return (/* JSX using filteredJokes */);
}
```

---

#### **3. Navigation State (URL-based)**

Managed by React Router through URL parameters:

```javascript
// Current joke ID stored in URL
// /jokes/joke-001
export default function JokePage() {
  const { id } = useParams(); // From React Router
  const { getJokeById } = useJokes();
  const joke = getJokeById(id);
  
  // State is derived from URL, not local useState
  return <JokeCard joke={joke} />;
}

// Current category ID stored in URL
// /categories/dad-jokes
export default function CategoryPage() {
  const { categoryId } = useParams();
  const { getJokesByCategory } = useJokes();
  const jokes = getJokesByCategory(categoryId);
  
  return <JokeList jokes={jokes} />;
}
```

**Benefits of URL State:**
- Deep linking support (users can bookmark specific jokes)
- Browser history works automatically (back/forward buttons)
- Sharable URLs
- No need for client-side state management for navigation

---

### State Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Static JSON Data                      │
│           (jokes.json, categories.json)                  │
│                  Loaded at build time                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ import
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Custom Hooks (Data Layer)                   │
│         useJokes(), useCategories()                      │
│         - Pure functions for data access                 │
│         - No mutations, immutable operations             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ hook calls
                      ▼
┌─────────────────────────────────────────────────────────┐
│                Page Components                           │
│        HomePage, BrowsePage, JokePage, etc.              │
│        - useState for local UI state                     │
│        - useParams for URL state                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ props
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Presentational Components                   │
│        JokeCard, JokeList, CategoryCard, etc.            │
│        - Stateless (props only)                          │
│        - Pure rendering logic                            │
└─────────────────────────────────────────────────────────┘
```

---

### Why No Redux/Zustand?

**Decision Rationale:**
- **Simple data model**: All data is static, no complex async operations
- **No shared mutable state**: Data never changes at runtime
- **Component tree is shallow**: No deep prop drilling issues
- **URL handles navigation state**: React Router eliminates need for route state
- **Minimal UI state**: Each component manages its own simple UI state

**When Redux/Zustand Would Be Needed:**
- User authentication state
- Shopping cart or persistent user data
- Complex async data fetching
- Deeply nested components with shared state
- Undo/redo functionality
- Real-time updates from WebSocket

**None of these apply to this jokes website.**

---

### State Management Best Practices Applied

1. **Single Source of Truth**: JSON files are the source, never duplicated
2. **Immutability**: All data operations return new arrays/objects
3. **Derived State**: Filtered/sorted data computed on-demand, not stored
4. **Local State Preference**: Keep state as local as possible to reduce complexity
5. **URL as State**: Navigation and view state stored in URL for shareability

---

### State Flow Example: Browsing Jokes

```
User visits /categories/dad-jokes
            ↓
React Router parses URL → categoryId = "dad-jokes"
            ↓
CategoryPage calls useJokes() and useCategories()
            ↓
Hooks return static data (jokes array, categories array)
            ↓
CategoryPage filters jokes by categoryId
            ↓
Filtered jokes passed to JokeList component
            ↓
JokeList maps over jokes, renders JokeCard for each
            ↓
User clicks joke card
            ↓
Navigate to /jokes/joke-005 (URL state changes)
            ↓
JokePage reads joke ID from URL params
            ↓
Calls getJokeById(id) to retrieve joke
            ↓
Renders JokeCard with joke data
```

**No global state store involved. All state is either:**
- Static (imported JSON)
- Ephemeral UI state (useState)
- Navigation state (URL parameters)

---

## 8. Error Handling Strategy

<!-- AI: Error codes, exception handling, user-facing messages -->

### Error Handling Architecture

The application uses a multi-layered error handling approach:

1. **React Error Boundaries** - Catch component rendering errors
2. **Conditional Rendering** - Handle missing data gracefully
3. **User-Friendly Messages** - Clear, actionable error messages
4. **Console Logging** - Development debugging information
5. **Fallback UI** - Always show something useful to the user

---

### 1. React Error Boundary

**Location:** `src/components/common/ErrorBoundary.jsx`

```javascript
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to console in development
    console.error('ErrorBoundary caught error:', {
      error,
      errorInfo,
      componentStack: errorInfo.componentStack
    });
    
    this.setState({ errorInfo });
    
    // Optional: Send to error tracking service in production
    // if (process.env.NODE_ENV === 'production') {
    //   logErrorToService(error, errorInfo);
    // }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Oops! Something went wrong.</h2>
          <p>
            We encountered an unexpected error. Please try refreshing the page.
          </p>
          <details style={{ marginTop: '1rem', cursor: 'pointer' }}>
            <summary>Error Details</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
          <button onClick={this.handleReset}>Try Again</button>
          <button onClick={() => window.location.href = '/'}>
            Go Home
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Usage:**
- Wraps main content area in Layout component
- Catches all rendering errors in child components
- Provides user with recovery options (retry, go home)
- Logs errors for debugging

---

### 2. Data Access Error Handling

**Custom Hooks Error Handling:**

```javascript
// src/hooks/useJokes.js
export function useJokes() {
  const [jokes, error] = useMemo(() => {
    try {
      const data = jokesData;
      
      // Validate data structure
      if (!Array.isArray(data)) {
        throw new Error('Jokes data is not an array');
      }
      
      // Validate each joke has required fields
      data.forEach((joke, index) => {
        if (!joke.id || !joke.setup || !joke.punchline || !joke.category) {
          console.error(`Invalid joke at index ${index}:`, joke);
          throw new Error(`Joke at index ${index} is missing required fields`);
        }
      });
      
      return [data, null];
    } catch (err) {
      console.error('Error loading jokes:', err);
      return [[], err];
    }
  }, []);

  const getJokeById = (id) => {
    try {
      if (!id) return null;
      return jokes.find(joke => joke.id === id) || null;
    } catch (err) {
      console.error('Error getting joke by ID:', err);
      return null;
    }
  };

  // Return error state for components to handle
  return {
    jokes,
    error,
    getJokeById,
    // ... other functions
  };
}
```

---

### 3. Component-Level Error Handling

**Example: JokePage with Missing Joke**

```javascript
// src/pages/JokePage.jsx
export default function JokePage() {
  const { id } = useParams();
  const { jokes, getJokeById, error } = useJokes();
  
  // Handle data loading error
  if (error) {
    return (
      <div className={styles.error}>
        <h2>Unable to Load Jokes</h2>
        <p>We're having trouble loading the joke data. Please try again later.</p>
        <Link to="/">Return Home</Link>
      </div>
    );
  }
  
  const joke = getJokeById(id);
  
  // Handle missing joke (404)
  if (!joke) {
    return (
      <NotFound 
        message="This joke doesn't exist or has been removed."
        showHomeLink={true}
      />
    );
  }
  
  return <JokeCard joke={joke} variant="full" />;
}
```

---

### 4. Routing Error Handling

**React Router Error Handling:**

```javascript
// src/router.jsx
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: (
      <Layout>
        <ErrorPage />
      </Layout>
    ),
    children: [
      // ... routes
      {
        path: '*',
        element: <NotFound />
      }
    ]
  }
]);

// src/components/common/ErrorPage.jsx
export default function ErrorPage() {
  const error = useRouteError();
  
  return (
    <div className={styles.errorPage}>
      <h1>Routing Error</h1>
      <p>Sorry, an unexpected error occurred.</p>
      <p>
        <i>{error.statusText || error.message}</i>
      </p>
      <Link to="/">Go Home</Link>
    </div>
  );
}
```

---

### 5. User-Facing Error Messages

**Error Message Guidelines:**

| Scenario | User Message | Recovery Action |
|----------|--------------|-----------------|
| Joke not found | "This joke doesn't exist or has been removed." | Link to home or browse page |
| Category not found | "Category not found." | Link to categories page |
| Data load failure | "We're having trouble loading the joke data." | Refresh button |
| Component crash | "Oops! Something went wrong." | Try again or go home |
| Network error (future) | "Unable to connect. Check your internet." | Retry button |
| Empty search results | "No jokes match your search." | Clear filters link |

**Implementation Example:**

```javascript
// src/components/jokes/JokeList.jsx
export default function JokeList({ jokes, emptyMessage, onReset }) {
  if (!jokes || jokes.length === 0) {
    return (
      <div className={styles.empty}>
        <p>{emptyMessage || 'No jokes found.'}</p>
        {onReset && (
          <button onClick={onReset}>Show All Jokes</button>
        )}
      </div>
    );
  }
  
  // Render joke cards...
}
```

---

### 6. Validation Error Handling

**Data Validation Functions:**

```javascript
// src/utils/validation.js

/**
 * Validate joke object structure
 * @param {Object} joke - Joke object to validate
 * @returns {Object} { valid: boolean, errors: string[] }
 */
export function validateJoke(joke) {
  const errors = [];
  
  if (!joke) {
    return { valid: false, errors: ['Joke is null or undefined'] };
  }
  
  if (!joke.id || typeof joke.id !== 'string') {
    errors.push('Invalid or missing joke ID');
  }
  
  if (!joke.setup || typeof joke.setup !== 'string') {
    errors.push('Invalid or missing setup');
  }
  
  if (!joke.punchline || typeof joke.punchline !== 'string') {
    errors.push('Invalid or missing punchline');
  }
  
  if (!joke.category || typeof joke.category !== 'string') {
    errors.push('Invalid or missing category');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate jokes array
 * @param {Array} jokes - Array of jokes
 * @returns {Object} { valid: boolean, invalidJokes: Array }
 */
export function validateJokesArray(jokes) {
  if (!Array.isArray(jokes)) {
    return { valid: false, invalidJokes: [] };
  }
  
  const invalidJokes = [];
  
  jokes.forEach((joke, index) => {
    const validation = validateJoke(joke);
    if (!validation.valid) {
      invalidJokes.push({ index, joke, errors: validation.errors });
    }
  });
  
  return {
    valid: invalidJokes.length === 0,
    invalidJokes
  };
}
```

---

### 7. Console Logging Strategy

**Development vs Production:**

```javascript
// src/utils/logger.js

const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
  error: (message, ...args) => {
    console.error(`[ERROR] ${message}`, ...args);
  },
  
  warn: (message, ...args) => {
    if (isDevelopment) {
      console.warn(`[WARN] ${message}`, ...args);
    }
  },
  
  info: (message, ...args) => {
    if (isDevelopment) {
      console.info(`[INFO] ${message}`, ...args);
    }
  },
  
  debug: (message, ...args) => {
    if (isDevelopment) {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  }
};

// Usage in components:
import { logger } from '../utils/logger';

export function useJokes() {
  // ...
  if (error) {
    logger.error('Failed to load jokes:', error);
  }
}
```

---

### 8. Graceful Degradation

**Progressive Enhancement Strategy:**

```javascript
// Handle missing features gracefully
export default function HomePage() {
  const { jokes, error } = useJokes();
  const [featuredJoke, setFeaturedJoke] = useState(null);
  
  useEffect(() => {
    if (jokes.length > 0) {
      setFeaturedJoke(getRandomJoke(jokes));
    }
  }, [jokes]);
  
  // If data fails to load, still show UI with message
  if (error || jokes.length === 0) {
    return (
      <div className={styles.home}>
        <h1>Welcome to JokesHub</h1>
        <div className={styles.error}>
          {error ? (
            <p>We're having trouble loading jokes. Please refresh the page.</p>
          ) : (
            <p>No jokes available yet. Check back soon!</p>
          )}
        </div>
      </div>
    );
  }
  
  // Normal rendering when data loads successfully
  return (/* full homepage */);
}
```

---

### Error Handling Checklist

✅ **React Error Boundaries** wrap main content
✅ **Null checks** before rendering data-dependent components
✅ **Fallback UI** for empty states and missing data
✅ **User-friendly messages** avoid technical jargon
✅ **Recovery actions** (buttons, links) always provided
✅ **Console logging** for debugging (dev only)
✅ **Validation** at data import time catches issues early
✅ **404 handling** for invalid routes and missing resources
✅ **Graceful degradation** - always show something useful

---

## 9. Test Plan

### Unit Tests

**Testing Framework:** Vitest + React Testing Library

**Location:** `jokes-website/tests/unit/`

---

#### **Component Unit Tests**

**File:** `tests/unit/components/JokeCard.test.jsx`

```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import JokeCard from '../../../src/components/jokes/JokeCard';

describe('JokeCard', () => {
  const mockJoke = {
    id: 'joke-001',
    setup: 'Why did the chicken cross the road?',
    punchline: 'To get to the other side!',
    category: 'classic'
  };

  it('renders joke setup and punchline', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} />
      </BrowserRouter>
    );
    
    expect(screen.getByText(mockJoke.setup)).toBeInTheDocument();
    expect(screen.getByText(mockJoke.punchline)).toBeInTheDocument();
  });

  it('displays category', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('classic')).toBeInTheDocument();
  });

  it('renders link when showLink is true', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} showLink={true} />
      </BrowserRouter>
    );
    
    const link = screen.getByRole('link', { name: /view/i });
    expect(link).toHaveAttribute('href', '/jokes/joke-001');
  });

  it('does not render link when showLink is false', () => {
    render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} showLink={false} />
      </BrowserRouter>
    );
    
    const link = screen.queryByRole('link', { name: /view/i });
    expect(link).not.toBeInTheDocument();
  });

  it('applies correct variant class', () => {
    const { container } = render(
      <BrowserRouter>
        <JokeCard joke={mockJoke} variant="featured" />
      </BrowserRouter>
    );
    
    expect(container.querySelector('.featured')).toBeInTheDocument();
  });
});
```

---

**File:** `tests/unit/components/JokeList.test.jsx`

```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import JokeList from '../../../src/components/jokes/JokeList';

describe('JokeList', () => {
  const mockJokes = [
    { id: 'joke-001', setup: 'Setup 1', punchline: 'Punchline 1', category: 'cat1' },
    { id: 'joke-002', setup: 'Setup 2', punchline: 'Punchline 2', category: 'cat2' }
  ];

  it('renders all jokes', () => {
    render(
      <BrowserRouter>
        <JokeList jokes={mockJokes} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Setup 1')).toBeInTheDocument();
    expect(screen.getByText('Setup 2')).toBeInTheDocument();
  });

  it('shows empty message when jokes array is empty', () => {
    render(
      <BrowserRouter>
        <JokeList jokes={[]} emptyMessage="No jokes here!" />
      </BrowserRouter>
    );
    
    expect(screen.getByText('No jokes here!')).toBeInTheDocument();
  });

  it('applies grid layout by default', () => {
    const { container } = render(
      <BrowserRouter>
        <JokeList jokes={mockJokes} />
      </BrowserRouter>
    );
    
    expect(container.querySelector('.grid')).toBeInTheDocument();
  });

  it('applies list layout when specified', () => {
    const { container } = render(
      <BrowserRouter>
        <JokeList jokes={mockJokes} layout="list" />
      </BrowserRouter>
    );
    
    expect(container.querySelector('.list')).toBeInTheDocument();
  });
});
```

---

**File:** `tests/unit/components/CategoryCard.test.jsx`

```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import CategoryCard from '../../../src/components/categories/CategoryCard';

describe('CategoryCard', () => {
  const mockCategory = {
    id: 'dad-jokes',
    name: 'Dad Jokes',
    description: 'Classic groan-worthy jokes',
    jokeCount: 15
  };

  it('renders category name and description', () => {
    render(
      <BrowserRouter>
        <CategoryCard category={mockCategory} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Dad Jokes')).toBeInTheDocument();
    expect(screen.getByText('Classic groan-worthy jokes')).toBeInTheDocument();
  });

  it('displays joke count', () => {
    render(
      <BrowserRouter>
        <CategoryCard category={mockCategory} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('15 jokes')).toBeInTheDocument();
  });

  it('links to category page', () => {
    render(
      <BrowserRouter>
        <CategoryCard category={mockCategory} />
      </BrowserRouter>
    );
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/categories/dad-jokes');
  });
});
```

---

#### **Hook Unit Tests**

**File:** `tests/unit/hooks/useJokes.test.js`

```javascript
import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useJokes } from '../../../src/hooks/useJokes';

describe('useJokes', () => {
  it('returns array of jokes', () => {
    const { result } = renderHook(() => useJokes());
    
    expect(Array.isArray(result.current.jokes)).toBe(true);
    expect(result.current.jokes.length).toBeGreaterThan(0);
  });

  it('getJokeById returns correct joke', () => {
    const { result } = renderHook(() => useJokes());
    const firstJoke = result.current.jokes[0];
    
    const joke = result.current.getJokeById(firstJoke.id);
    
    expect(joke).toEqual(firstJoke);
  });

  it('getJokeById returns null for invalid id', () => {
    const { result } = renderHook(() => useJokes());
    
    const joke = result.current.getJokeById('invalid-id-999');
    
    expect(joke).toBeNull();
  });

  it('getJokesByCategory filters correctly', () => {
    const { result } = renderHook(() => useJokes());
    const category = result.current.jokes[0].category;
    
    const filtered = result.current.getJokesByCategory(category);
    
    expect(filtered.every(j => j.category === category)).toBe(true);
  });

  it('searchJokes finds jokes by setup text', () => {
    const { result } = renderHook(() => useJokes());
    const searchTerm = result.current.jokes[0].setup.split(' ')[0];
    
    const results = result.current.searchJokes(searchTerm);
    
    expect(results.length).toBeGreaterThan(0);
  });
});
```

---

#### **Utility Function Tests**

**File:** `tests/unit/utils/jokeHelpers.test.js`

```javascript
import { describe, it, expect } from 'vitest';
import {
  getNextJoke,
  getPreviousJoke,
  getRandomJoke,
  sortJokesByDate,
  filterJokesByQuery
} from '../../../src/utils/jokeHelpers';

describe('jokeHelpers', () => {
  const mockJokes = [
    { id: 'joke-001', setup: 'Setup 1', punchline: 'P1', category: 'cat1', dateAdded: '2026-01-01' },
    { id: 'joke-002', setup: 'Setup 2', punchline: 'P2', category: 'cat2', dateAdded: '2026-01-02' },
    { id: 'joke-003', setup: 'Setup 3', punchline: 'P3', category: 'cat1', dateAdded: '2026-01-03' }
  ];

  describe('getNextJoke', () => {
    it('returns next joke in array', () => {
      const next = getNextJoke('joke-001', mockJokes);
      expect(next.id).toBe('joke-002');
    });

    it('wraps around to first joke at end', () => {
      const next = getNextJoke('joke-003', mockJokes);
      expect(next.id).toBe('joke-001');
    });

    it('returns null for empty array', () => {
      const next = getNextJoke('joke-001', []);
      expect(next).toBeNull();
    });
  });

  describe('getPreviousJoke', () => {
    it('returns previous joke in array', () => {
      const prev = getPreviousJoke('joke-002', mockJokes);
      expect(prev.id).toBe('joke-001');
    });

    it('wraps around to last joke at beginning', () => {
      const prev = getPreviousJoke('joke-001', mockJokes);
      expect(prev.id).toBe('joke-003');
    });
  });

  describe('getRandomJoke', () => {
    it('returns a joke from the array', () => {
      const random = getRandomJoke(mockJokes);
      expect(mockJokes).toContain(random);
    });

    it('excludes specified joke', () => {
      const random = getRandomJoke(mockJokes, 'joke-001');
      expect(random.id).not.toBe('joke-001');
    });

    it('returns null for empty array', () => {
      const random = getRandomJoke([]);
      expect(random).toBeNull();
    });
  });

  describe('sortJokesByDate', () => {
    it('sorts jokes by date descending', () => {
      const sorted = sortJokesByDate(mockJokes);
      expect(sorted[0].id).toBe('joke-003');
      expect(sorted[2].id).toBe('joke-001');
    });
  });

  describe('filterJokesByQuery', () => {
    it('filters jokes by setup text', () => {
      const filtered = filterJokesByQuery(mockJokes, 'Setup 1');
      expect(filtered.length).toBe(1);
      expect(filtered[0].id).toBe('joke-001');
    });

    it('filters jokes by category', () => {
      const filtered = filterJokesByQuery(mockJokes, 'cat1');
      expect(filtered.length).toBe(2);
    });

    it('returns all jokes for empty query', () => {
      const filtered = filterJokesByQuery(mockJokes, '');
      expect(filtered.length).toBe(mockJokes.length);
    });
  });
});
```

---

### Integration Tests

**Location:** `jokes-website/tests/integration/`

---

**File:** `tests/integration/navigation.test.jsx`

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { routes } from '../../src/router';

describe('Navigation Integration', () => {
  it('navigates from home to browse page', async () => {
    const router = createMemoryRouter(routes, {
      initialEntries: ['/']
    });
    
    render(<RouterProvider router={router} />);
    
    const browseLink = screen.getByRole('link', { name: /browse/i });
    await userEvent.click(browseLink);
    
    await waitFor(() => {
      expect(screen.getByText(/browse all jokes/i)).toBeInTheDocument();
    });
  });

  it('navigates to individual joke page', async () => {
    const router = createMemoryRouter(routes, {
      initialEntries: ['/browse']
    });
    
    render(<RouterProvider router={router} />);
    
    const viewLinks = screen.getAllByRole('link', { name: /view/i });
    await userEvent.click(viewLinks[0]);
    
    await waitFor(() => {
      expect(window.location.pathname).toMatch(/^\/jokes\/.+/);
    });
  });

  it('navigates between jokes using next/previous', async () => {
    const router = createMemoryRouter(routes, {
      initialEntries: ['/jokes/joke-001']
    });
    
    render(<RouterProvider router={router} />);
    
    const nextButton = screen.getByRole('button', { name: /next/i });
    await userEvent.click(nextButton);
    
    await waitFor(() => {
      expect(window.location.pathname).toBe('/jokes/joke-002');
    });
  });

  it('shows 404 page for invalid route', async () => {
    const router = createMemoryRouter(routes, {
      initialEntries: ['/invalid-route']
    });
    
    render(<RouterProvider router={router} />);
    
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    expect(screen.getByText(/not found/i)).toBeInTheDocument();
  });
});
```

---

**File:** `tests/integration/filtering.test.jsx`

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import BrowsePage from '../../src/pages/BrowsePage';

describe('Joke Filtering Integration', () => {
  it('filters jokes by category', async () => {
    render(
      <BrowserRouter>
        <BrowsePage />
      </BrowserRouter>
    );
    
    const initialCount = screen.getByText(/showing \d+ jokes?/i);
    const select = screen.getByLabelText(/filter by category/i);
    
    await userEvent.selectOptions(select, 'dad-jokes');
    
    await waitFor(() => {
      const newCount = screen.getByText(/showing \d+ jokes?/i);
      expect(newCount).not.toBe(initialCount);
    });
  });

  it('shows all jokes when "All Categories" selected', async () => {
    render(
      <BrowserRouter>
        <BrowsePage />
      </BrowserRouter>
    );
    
    const select = screen.getByLabelText(/filter by category/i);
    
    // First filter
    await userEvent.selectOptions(select, 'dad-jokes');
    
    // Then show all
    await userEvent.selectOptions(select, 'all');
    
    await waitFor(() => {
      const jokes = screen.getAllByRole('article');
      expect(jokes.length).toBeGreaterThan(0);
    });
  });
});
```

---

### E2E Tests

**Testing Framework:** Playwright

**Location:** `jokes-website/tests/e2e/`

---

**File:** `tests/e2e/homepage.spec.js`

```javascript
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('loads successfully', async ({ page }) => {
    await page.goto('/');
    
    await expect(page).toHaveTitle(/JokesHub/i);
    await expect(page.locator('h1')).toContainText('Welcome to JokesHub');
  });

  test('displays featured joke', async ({ page }) => {
    await page.goto('/');
    
    const jokeCard = page.locator('article').first();
    await expect(jokeCard).toBeVisible();
  });

  test('shows category cards', async ({ page }) => {
    await page.goto('/');
    
    const categoryCards = page.locator('a[href^="/categories/"]');
    await expect(categoryCards.first()).toBeVisible();
    
    const count = await categoryCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('navigates to browse page via CTA button', async ({ page }) => {
    await page.goto('/');
    
    await page.click('text=Browse All Jokes');
    
    await expect(page).toHaveURL(/\/browse/);
    await expect(page.locator('h1')).toContainText('Browse All Jokes');
  });

  test('refreshes featured joke on button click', async ({ page }) => {
    await page.goto('/');
    
    const firstJokeText = await page.locator('article p').first().textContent();
    
    await page.click('text=Show Another');
    
    // Wait for new joke to render
    await page.waitForTimeout(100);
    
    const secondJokeText = await page.locator('article p').first().textContent();
    
    // May be the same joke by chance, but button should work
    expect(secondJokeText).toBeTruthy();
  });
});
```

---

**File:** `tests/e2e/browsing.spec.js`

```javascript
import { test, expect } from '@playwright/test';

test.describe('Joke Browsing', () => {
  test('browse page displays jokes grid', async ({ page }) => {
    await page.goto('/browse');
    
    const jokes = page.locator('article');
    const count = await jokes.count();
    
    expect(count).toBeGreaterThan(0);
  });

  test('filters jokes by category', async ({ page }) => {
    await page.goto('/browse');
    
    const initialCount = await page.locator('article').count();
    
    await page.selectOption('select#category-filter', 'dad-jokes');
    
    await page.waitForTimeout(100);
    
    const filteredCount = await page.locator('article').count();
    
    // Filtered count should be different (assuming multiple categories exist)
    expect(filteredCount).toBeGreaterThan(0);
  });

  test('navigates to individual joke', async ({ page }) => {
    await page.goto('/browse');
    
    const firstJoke = page.locator('article').first();
    await firstJoke.locator('a:has-text("View")').click();
    
    await expect(page).toHaveURL(/\/jokes\/.+/);
  });

  test('individual joke page shows navigation', async ({ page }) => {
    await page.goto('/browse');
    
    await page.locator('article').first().locator('a:has-text("View")').click();
    
    await expect(page.locator('button:has-text("Next")')).toBeVisible();
    await expect(page.locator('button:has-text("Previous")')).toBeVisible();
    await expect(page.locator('button:has-text("Random")')).toBeVisible();
  });

  test('next/previous navigation works', async ({ page }) => {
    await page.goto('/browse');
    await page.locator('article').first().locator('a:has-text("View")').click();
    
    const firstUrl = page.url();
    
    await page.click('button:has-text("Next")');
    
    const secondUrl = page.url();
    expect(secondUrl).not.toBe(firstUrl);
    
    await page.click('button:has-text("Previous")');
    
    await expect(page).toHaveURL(firstUrl);
  });
});
```

---

**File:** `tests/e2e/categories.spec.js`

```javascript
import { test, expect } from '@playwright/test';

test.describe('Category Navigation', () => {
  test('displays all categories on homepage', async ({ page }) => {
    await page.goto('/');
    
    const categoryCards = page.locator('a[href^="/categories/"]');
    const count = await categoryCards.count();
    
    expect(count).toBeGreaterThan(0);
  });

  test('navigates to category page', async ({ page }) => {
    await page.goto('/');
    
    const firstCategory = page.locator('a[href^="/categories/"]').first();
    await firstCategory.click();
    
    await expect(page).toHaveURL(/\/categories\/.+/);
  });

  test('category page shows filtered jokes', async ({ page }) => {
    await page.goto('/categories/dad-jokes');
    
    await expect(page.locator('h1')).toContainText('Dad Jokes');
    
    const jokes = page.locator('article');
    const count = await jokes.count();
    
    expect(count).toBeGreaterThan(0);
  });

  test('shows 404 for invalid category', async ({ page }) => {
    await page.goto('/categories/invalid-category-xyz');
    
    await expect(page.locator('text=404')).toBeVisible();
    await expect(page.locator('text=/not found/i')).toBeVisible();
  });
});
```

---

**File:** `tests/e2e/mobile.spec.js`

```javascript
import { test, expect, devices } from '@playwright/test';

test.use(devices['iPhone 12']);

test.describe('Mobile Responsiveness', () => {
  test('homepage is mobile-friendly', async ({ page }) => {
    await page.goto('/');
    
    await expect(page.locator('h1')).toBeVisible();
    
    // Check hamburger menu exists
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    await expect(hamburger).toBeVisible();
  });

  test('mobile menu opens and closes', async ({ page }) => {
    await page.goto('/');
    
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    await hamburger.click();
    
    const nav = page.locator('nav');
    await expect(nav).toHaveClass(/open/);
    
    await hamburger.click();
    await expect(nav).not.toHaveClass(/open/);
  });

  test('jokes are readable on mobile', async ({ page }) => {
    await page.goto('/browse');
    
    const jokeCard = page.locator('article').first();
    await expect(jokeCard).toBeVisible();
    
    const boundingBox = await jokeCard.boundingBox();
    expect(boundingBox.width).toBeLessThanOrEqual(400); // Mobile viewport
  });
});
```

---

### Test Coverage Goals

**Target Coverage:**
- Unit tests: > 80% code coverage
- Integration tests: All critical user flows
- E2E tests: Core user journeys

**Coverage Report Command:**
```bash
npm run test:coverage
```

---

## 10. Migration Strategy

<!-- AI: How to migrate from current state to new implementation -->

### Migration Overview

This is a **greenfield implementation** - no existing jokes website to migrate from. The migration strategy focuses on setting up the new application within the existing repository structure without disrupting current projects.

---

### Phase 1: Repository Setup

**Objective:** Set up the jokes-website directory structure without affecting existing code.

**Steps:**

1. **Create jokes-website directory**
   ```bash
   mkdir -p jokes-website
   cd jokes-website
   ```

2. **Initialize Vite React project**
   ```bash
   npm create vite@latest . -- --template react
   ```

3. **Install dependencies**
   ```bash
   npm install react-router-dom
   npm install -D vitest @testing-library/react @testing-library/jest-dom
   npm install -D @testing-library/user-event
   npm install -D @playwright/test
   npm install -D eslint prettier
   ```

4. **Update root .gitignore** (if needed)
   ```
   # Add to existing .gitignore
   jokes-website/node_modules/
   jokes-website/dist/
   jokes-website/.env
   ```

5. **Update root README.md**
   Add section documenting the jokes-website subproject:
   ```markdown
   ## Jokes Website
   
   A static React-based jokes website hosted on S3.
   
   Location: `jokes-website/`
   
   See [jokes-website/README.md](jokes-website/README.md) for details.
   ```

**Validation:**
- Verify `npm run dev` works in jokes-website directory
- Confirm existing projects (src/, notebooks/) are unaffected
- Check git status shows no unwanted changes

---

### Phase 2: Core Implementation

**Objective:** Build the React application with all components and data.

**Steps:**

1. **Create directory structure**
   ```bash
   mkdir -p src/components/{layout,jokes,categories,common}
   mkdir -p src/pages
   mkdir -p src/data
   mkdir -p src/hooks
   mkdir -p src/utils
   mkdir -p src/styles
   mkdir -p tests/{unit,integration,e2e}
   ```

2. **Add joke data**
   - Create `src/data/jokes.json` with 20-50 jokes
   - Create `src/data/categories.json` with category metadata
   - Validate JSON structure

3. **Implement components** (in order)
   - Common: ErrorBoundary, NotFound
   - Layout: Header, Footer, Layout
   - Jokes: JokeCard, JokeList, JokeNavigation
   - Categories: CategoryCard, CategoryList
   - Pages: HomePage, BrowsePage, JokePage, CategoryPage

4. **Implement routing**
   - Configure React Router in `src/router.jsx`
   - Set up App.jsx with RouterProvider
   - Test all routes

5. **Add styles**
   - Global styles in `src/styles/`
   - Component CSS Modules
   - Responsive breakpoints

6. **Implement custom hooks**
   - useJokes in `src/hooks/useJokes.js`
   - useCategories in `src/hooks/useCategories.js`

7. **Add utility functions**
   - jokeHelpers.js for joke operations
   - navigation.js for URL helpers
   - validation.js for data validation

**Validation:**
- Test all pages in development mode
- Verify responsive design on mobile/desktop
- Check all navigation flows work
- Validate data loading and error handling

---

### Phase 3: Testing Implementation

**Objective:** Implement comprehensive test suite.

**Steps:**

1. **Configure test frameworks**
   - Create `vitest.config.js` for unit tests
   - Create `playwright.config.js` for E2E tests
   - Add test scripts to package.json

2. **Write unit tests**
   - Component tests (JokeCard, JokeList, etc.)
   - Hook tests (useJokes, useCategories)
   - Utility function tests

3. **Write integration tests**
   - Navigation flows
   - Filtering and sorting

4. **Write E2E tests**
   - Homepage journey
   - Browsing jokes
   - Category filtering
   - Mobile responsiveness

5. **Run test suite and achieve coverage goals**
   ```bash
   npm run test:unit
   npm run test:integration
   npm run test:e2e
   npm run test:coverage
   ```

**Validation:**
- All tests pass
- Coverage > 80% for unit tests
- E2E tests cover critical paths

---

### Phase 4: Build Optimization

**Objective:** Optimize production build for performance.

**Steps:**

1. **Configure Vite for optimization**
   ```javascript
   // vite.config.js
   export default {
     build: {
       target: 'es2015',
       minify: 'terser',
       rollupOptions: {
         output: {
           manualChunks: {
             vendor: ['react', 'react-dom', 'react-router-dom']
           }
         }
       }
     }
   };
   ```

2. **Add compression**
   ```bash
   npm install -D vite-plugin-compression
   ```

3. **Optimize images** (if any)
   - Compress favicon and any graphics
   - Use appropriate formats (WebP, SVG)

4. **Test production build**
   ```bash
   npm run build
   npm run preview
   ```

5. **Analyze bundle size**
   ```bash
   npm run build -- --report
   ```

**Validation:**
- Bundle size < 500KB (gzipped)
- Lighthouse performance score > 90
- All assets load correctly in preview

---

### Phase 5: Documentation

**Objective:** Create comprehensive documentation.

**Steps:**

1. **Create jokes-website/README.md**
   - Project overview
   - Local development setup
   - Available scripts
   - Project structure
   - Testing guide

2. **Update docs/plans/jokes-website/ documentation**
   - Create IMPLEMENTATION.md (detailed setup guide)
   - Create DEPLOYMENT.md (S3 deployment instructions)

3. **Add inline code comments**
   - Document complex functions
   - Add JSDoc comments for public APIs

4. **Create CONTRIBUTING.md** (if accepting contributions)
   - Code style guide
   - PR process
   - Testing requirements

**Validation:**
- New developer can follow README and run project
- All documentation is accurate and up-to-date

---

### Phase 6: Deployment Setup

**Objective:** Configure S3 hosting and CI/CD pipeline.

**Steps:**

1. **Create S3 bucket**
   ```bash
   aws s3 mb s3://jokes-website-bucket
   aws s3 website s3://jokes-website-bucket \
     --index-document index.html \
     --error-document index.html
   ```

2. **Configure bucket policy for public access**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::jokes-website-bucket/*"
     }]
   }
   ```

3. **Create deployment script**
   - `scripts/deploy-s3.sh`
   - Test manual deployment

4. **Set up GitHub Actions**
   - Create `.github/workflows/deploy.yml`
   - Configure AWS credentials in GitHub Secrets
   - Test automated deployment

5. **(Optional) Set up CloudFront**
   - Create CloudFront distribution
   - Configure SSL certificate
   - Update deployment script to invalidate cache

**Validation:**
- Manual deployment works
- CI/CD pipeline deploys on push to main
- Website is accessible via S3 URL

---

### Migration Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Repository Setup | 1 day | Directory structure, dependencies |
| Phase 2: Core Implementation | 3-5 days | All components, pages, routing |
| Phase 3: Testing | 2-3 days | Complete test suite |
| Phase 4: Build Optimization | 1 day | Optimized production build |
| Phase 5: Documentation | 1 day | Complete documentation |
| Phase 6: Deployment | 1-2 days | S3 hosting, CI/CD |
| **Total** | **9-13 days** | Production-ready website |

---

### Risk Mitigation

**Risk: Breaking existing repository code**
- Mitigation: jokes-website is isolated directory, no shared dependencies

**Risk: Data structure issues**
- Mitigation: Validate JSON schema before implementation, add validation tests

**Risk: S3 configuration errors**
- Mitigation: Test with manual deployment before automating, document rollback

**Risk: Build failures in CI/CD**
- Mitigation: Test build locally, use GitHub Actions cache, add build validation

---

### Success Criteria

✅ Jokes website runs independently in jokes-website/ directory
✅ Existing repository projects are unaffected
✅ All tests pass with > 80% coverage
✅ Production build is optimized (< 500KB gzipped)
✅ Website is deployed and accessible via S3
✅ CI/CD pipeline deploys automatically on merge to main
✅ Documentation is complete and accurate

---

## 11. Rollback Plan

<!-- AI: How to rollback if deployment fails -->

### Rollback Strategy

Since this is a static website hosted on S3, rollback is straightforward and fast. The strategy includes automated rollback mechanisms and manual procedures.

---

### 1. S3 Versioning Rollback

**Setup: Enable S3 Versioning**

```bash
aws s3api put-bucket-versioning \
  --bucket jokes-website-bucket \
  --versioning-configuration Status=Enabled
```

**Rollback Procedure:**

1. **List recent versions of index.html**
   ```bash
   aws s3api list-object-versions \
     --bucket jokes-website-bucket \
     --prefix index.html \
     --max-items 10
   ```

2. **Identify previous working version ID**
   - Note the VersionId of the previous deployment

3. **Restore previous version**
   ```bash
   aws s3api copy-object \
     --bucket jokes-website-bucket \
     --copy-source jokes-website-bucket/index.html?versionId=PREVIOUS_VERSION_ID \
     --key index.html
   ```

4. **Invalidate CloudFront cache** (if using CDN)
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id DISTRIBUTION_ID \
     --paths "/*"
   ```

**Time to Rollback:** < 2 minutes

---

### 2. Deployment Artifact Rollback

**Setup: Keep Previous Build Artifacts**

Store each deployment build with timestamp:

```bash
# In deployment script
BUILD_ID=$(date +%Y%m%d-%H%M%S)
tar -czf "builds/jokes-website-${BUILD_ID}.tar.gz" dist/
```

**Rollback Procedure:**

1. **List available builds**
   ```bash
   ls -lt builds/
   ```

2. **Extract previous build**
   ```bash
   tar -xzf builds/jokes-website-PREVIOUS_TIMESTAMP.tar.gz
   ```

3. **Deploy previous build to S3**
   ```bash
   aws s3 sync dist/ s3://jokes-website-bucket --delete
   ```

4. **Invalidate CloudFront cache**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id DISTRIBUTION_ID \
     --paths "/*"
   ```

**Time to Rollback:** < 5 minutes

---

### 3. Git-Based Rollback

**Rollback to Previous Git Commit:**

1. **Identify last working commit**
   ```bash
   git log --oneline jokes-website/ -10
   ```

2. **Create rollback branch**
   ```bash
   git checkout -b rollback/jokes-website-YYYYMMDD COMMIT_SHA
   ```

3. **Trigger CI/CD deployment**
   ```bash
   git push origin rollback/jokes-website-YYYYMMDD
   ```
   
   Or manually deploy:
   ```bash
   cd jokes-website
   npm run build
   ./scripts/deploy-s3.sh
   ```

**Time to Rollback:** 5-10 minutes (includes build time)

---

### 4. Emergency S3 Bucket Replacement

**Setup: Maintain Backup Bucket**

Keep a mirror of last known good deployment:

```bash
aws s3 sync s3://jokes-website-bucket s3://jokes-website-backup \
  --delete
```

**Rollback Procedure:**

1. **Sync backup bucket to production**
   ```bash
   aws s3 sync s3://jokes-website-backup s3://jokes-website-bucket \
     --delete
   ```

2. **Invalidate CloudFront cache**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id DISTRIBUTION_ID \
     --paths "/*"
   ```

**Time to Rollback:** < 2 minutes

---

### 5. Automated Rollback in CI/CD

**GitHub Actions Workflow with Rollback:**

```yaml
# .github/workflows/deploy.yml
name: Deploy to S3

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Backup current S3 state
        run: |
          aws s3 sync s3://jokes-website-bucket s3://jokes-website-backup --delete
      
      - name: Build
        working-directory: jokes-website
        run: |
          npm ci
          npm run build
      
      - name: Deploy to S3
        run: |
          aws s3 sync jokes-website/dist/ s3://jokes-website-bucket --delete
        id: deploy
      
      - name: Health Check
        id: health
        run: |
          RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://jokes-website.example.com)
          if [ $RESPONSE -ne 200 ]; then
            echo "Health check failed with status $RESPONSE"
            exit 1
          fi
      
      - name: Rollback on Failure
        if: failure()
        run: |
          echo "Deployment failed, rolling back..."
          aws s3 sync s3://jokes-website-backup s3://jokes-website-bucket --delete
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CF_DISTRIBUTION_ID }} --paths "/*"
```

---

### 6. Rollback Decision Matrix

| Scenario | Recommended Rollback Method | Estimated Time |
|----------|----------------------------|----------------|
| Build artifact corrupted | S3 Versioning Rollback | < 2 min |
| New feature breaks UI | Git-Based Rollback | 5-10 min |
| Data file error (jokes.json) | Deployment Artifact Rollback | < 5 min |
| Complete site failure | Emergency S3 Bucket Replacement | < 2 min |
| Routing issues | Git-Based Rollback | 5-10 min |
| CI/CD pipeline failure | Automated Rollback (built-in) | Automatic |

---

### 7. Rollback Validation Checklist

After performing rollback, validate:

- ✅ Website loads at S3/CloudFront URL
- ✅ All pages are accessible (home, browse, jokes, categories)
- ✅ Navigation works correctly
- ✅ Jokes display properly
- ✅ No console errors in browser
- ✅ Lighthouse performance score > 85
- ✅ Mobile responsiveness intact

**Validation Script:**

```bash
#!/bin/bash
# scripts/validate-deployment.sh

SITE_URL="https://jokes-website.example.com"

echo "Validating deployment..."

# Check homepage
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $SITE_URL)
if [ $HTTP_CODE -ne 200 ]; then
  echo "❌ Homepage failed: HTTP $HTTP_CODE"
  exit 1
fi
echo "✅ Homepage OK"

# Check joke page
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $SITE_URL/jokes/joke-001)
if [ $HTTP_CODE -ne 200 ]; then
  echo "❌ Joke page failed: HTTP $HTTP_CODE"
  exit 1
fi
echo "✅ Joke page OK"

# Check category page
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $SITE_URL/categories/dad-jokes)
if [ $HTTP_CODE -ne 200 ]; then
  echo "❌ Category page failed: HTTP $HTTP_CODE"
  exit 1
fi
echo "✅ Category page OK"

echo "✅ All checks passed"
```

---

### 8. Post-Rollback Actions

1. **Notify team** of rollback via Slack/email
2. **Document incident** in incident log
3. **Create bug ticket** for the issue that caused rollback
4. **Review logs** to identify root cause
5. **Update tests** to prevent similar issues
6. **Plan fix and redeploy** after thorough testing

---

### 9. Prevention Measures

**To minimize need for rollbacks:**

1. **Staging Environment** - Test deployments in staging S3 bucket first
2. **Pre-deployment Checks** - Run full test suite before deploy
3. **Smoke Tests** - Automated health checks post-deployment
4. **Progressive Rollout** - Deploy to subset of users first (if using CloudFront with Lambda@Edge)
5. **Monitoring** - Set up CloudWatch alarms for 4xx/5xx errors
6. **Blue-Green Deployment** - Maintain two S3 buckets, switch DNS on success

---

### 10. Rollback Contact and Escalation

**Primary Contact:** DevOps Lead
**Secondary Contact:** Project Owner
**Escalation Path:** CTO → VP Engineering

**Emergency Rollback Authority:**
- Any team member can initiate rollback if site is down
- Document decision and notify team immediately
- Post-mortem required within 24 hours

---

### Rollback Runbook Summary

**Quick Rollback Commands:**

```bash
# 1. Rollback using S3 sync from backup (fastest)
aws s3 sync s3://jokes-website-backup s3://jokes-website-bucket --delete
aws cloudfront create-invalidation --distribution-id XYZ --paths "/*"

# 2. Rollback to previous git commit and redeploy
cd jokes-website
git checkout PREVIOUS_COMMIT_SHA
npm run build
./scripts/deploy-s3.sh

# 3. Restore from build artifact
tar -xzf builds/jokes-website-TIMESTAMP.tar.gz
aws s3 sync dist/ s3://jokes-website-bucket --delete
```

---

## 12. Performance Considerations

<!-- AI: Performance optimizations, caching, indexing -->

### Performance Strategy

The jokes website will be optimized for fast load times, minimal bundle size, and excellent user experience metrics. Target performance metrics:

- **First Contentful Paint (FCP):** < 1.5s
- **Largest Contentful Paint (LCP):** < 2.5s
- **Time to Interactive (TTI):** < 3.5s
- **Cumulative Layout Shift (CLS):** < 0.1
- **First Input Delay (FID):** < 100ms
- **Lighthouse Performance Score:** > 90

---

### 1. Bundle Size Optimization

#### **Code Splitting**

**Vite Configuration** (`vite.config.js`):

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunk
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom']
        }
      }
    },
    chunkSizeWarningLimit: 500 // Warn if chunk > 500KB
  }
});
```

**Route-Based Code Splitting:**

```javascript
// src/router.jsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';

// Lazy load page components
const HomePage = lazy(() => import('./pages/HomePage'));
const BrowsePage = lazy(() => import('./pages/BrowsePage'));
const JokePage = lazy(() => import('./pages/JokePage'));
const CategoryPage = lazy(() => import('./pages/CategoryPage'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<div>Loading...</div>}>
            <HomePage />
          </Suspense>
        )
      },
      {
        path: 'browse',
        element: (
          <Suspense fallback={<div>Loading...</div>}>
            <BrowsePage />
          </Suspense>
        )
      }
      // ... other routes
    ]
  }
]);
```

**Expected Results:**
- Initial bundle: ~80-120 KB (gzipped)
- Vendor chunk: ~40-50 KB (gzipped)
- Route chunks: ~10-20 KB each (gzipped)
- Total page load: < 150 KB (gzipped)

---

### 2. Asset Optimization

#### **Image Optimization**

```bash
# Optimize favicon and any images
npm install -D vite-plugin-imagemin

# Configure in vite.config.js
import viteImagemin from 'vite-plugin-imagemin';

export default defineConfig({
  plugins: [
    viteImagemin({
      gifsicle: { optimizationLevel: 7 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      svgo: {
        plugins: [
          { removeViewBox: false },
          { removeEmptyAttrs: false }
        ]
      }
    })
  ]
});
```

#### **Font Optimization**

```css
/* Use system font stack for instant rendering */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 
               'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
               sans-serif;
}

/* If using web fonts, preload critical fonts */
/* <link rel="preload" href="/fonts/font.woff2" as="font" crossorigin> */
```

---

### 3. Caching Strategy

#### **S3 Cache Headers**

```bash
# Deploy script with cache headers
aws s3 sync dist/ s3://jokes-website-bucket \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html" \
  --exclude "*.json"

# HTML files: short cache (use ETags for validation)
aws s3 cp dist/index.html s3://jokes-website-bucket/index.html \
  --cache-control "public, max-age=300, must-revalidate" \
  --content-type "text/html"
```

**Cache Strategy:**
- **Hashed Assets** (JS, CSS): 1 year cache, immutable
- **HTML Files**: 5 minutes cache, must-revalidate
- **JSON Data** (if external): 1 hour cache, stale-while-revalidate
- **Favicon**: 7 days cache

#### **CloudFront Caching**

```json
{
  "DefaultCacheBehavior": {
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "Compress": true,
    "ViewerProtocolPolicy": "redirect-to-https"
  },
  "CacheBehaviors": [
    {
      "PathPattern": "*.js",
      "MinTTL": 31536000,
      "DefaultTTL": 31536000,
      "Compress": true
    },
    {
      "PathPattern": "*.css",
      "MinTTL": 31536000,
      "DefaultTTL": 31536000,
      "Compress": true
    },
    {
      "PathPattern": "index.html",
      "MinTTL": 0,
      "DefaultTTL": 300,
      "MaxTTL": 3600,
      "Compress": true
    }
  ]
}
```

---

### 4. React Performance Optimizations

#### **Memoization**

```javascript
// src/components/jokes/JokeList.jsx
import { memo } from 'react';

// Memoize expensive list rendering
const JokeList = memo(({ jokes, variant, layout }) => {
  return (
    <div className={`${styles.list} ${styles[layout]}`}>
      {jokes.map(joke => (
        <JokeCard key={joke.id} joke={joke} variant={variant} />
      ))}
    </div>
  );
});

export default JokeList;
```

#### **useMemo for Expensive Computations**

```javascript
// src/pages/BrowsePage.jsx
import { useMemo } from 'react';

export default function BrowsePage() {
  const { jokes } = useJokes();
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Memoize filtered jokes (only recompute when dependencies change)
  const filteredJokes = useMemo(() => {
    return selectedCategory === 'all'
      ? jokes
      : jokes.filter(j => j.category === selectedCategory);
  }, [jokes, selectedCategory]);

  return <JokeList jokes={filteredJokes} />;
}
```

#### **Virtual Scrolling** (if joke count grows significantly)

```bash
npm install react-window
```

```javascript
// Only implement if > 100 jokes
import { FixedSizeList } from 'react-window';

export default function VirtualJokeList({ jokes }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <JokeCard joke={jokes[index]} variant="compact" />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={jokes.length}
      itemSize={200}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

---

### 5. CSS Performance

#### **Critical CSS Inlining**

```javascript
// vite.config.js - Extract critical CSS
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    cssCodeSplit: true, // Split CSS by route
    assetsInlineLimit: 4096 // Inline small assets < 4KB
  }
});
```

#### **CSS Optimization**

```css
/* Use CSS containment for better paint performance */
.joke-card {
  contain: layout style paint;
}

/* Use will-change sparingly for animations */
.hamburger:active {
  will-change: transform;
}

/* Avoid expensive properties */
/* Bad: box-shadow on scroll */
/* Good: Add shadow only on hover */
.card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
```

---

### 6. Data Loading Optimization

#### **Static Data Optimization**

```javascript
// src/data/jokes.json
// Keep JSON minified in production (Vite does this automatically)
// Validate data structure at build time

// src/hooks/useJokes.js
import { useMemo } from 'react';
import jokesData from '../data/jokes.json';

export function useJokes() {
  // Memoize to prevent re-parsing on every render
  const jokes = useMemo(() => jokesData, []);
  
  // Lazy compute categories only when needed
  const categories = useMemo(() => {
    const categorySet = new Set(jokes.map(j => j.category));
    return Array.from(categorySet);
  }, [jokes]);

  return { jokes, categories };
}
```

#### **Avoid Unnecessary Re-renders**

```javascript
// src/components/jokes/JokeCard.jsx
import { memo } from 'react';

// Memoize component - only re-render if props change
export default memo(function JokeCard({ joke, variant, showLink }) {
  return (/* JSX */);
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if joke ID changes
  return prevProps.joke.id === nextProps.joke.id &&
         prevProps.variant === nextProps.variant &&
         prevProps.showLink === nextProps.showLink;
});
```

---

### 7. Network Performance

#### **Compression**

```bash
npm install -D vite-plugin-compression
```

```javascript
// vite.config.js
import viteCompression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz'
    }),
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ]
});
```

**S3 Configuration:**
```bash
# Serve .br files with correct headers
aws s3 cp dist/assets/*.br s3://jokes-website-bucket/assets/ \
  --content-encoding "br" \
  --recursive
```

#### **Preconnect and DNS Prefetch**

```html
<!-- index.html -->
<head>
  <!-- Preconnect to CDN if using external resources -->
  <link rel="preconnect" href="https://cdn.example.com">
  <link rel="dns-prefetch" href="https://cdn.example.com">
</head>
```

---

### 8. Rendering Performance

#### **Reduce Layout Shifts**

```css
/* Reserve space for images to prevent CLS */
.joke-card img {
  aspect-ratio: 16 / 9;
  width: 100%;
  height: auto;
}

/* Use min-height for dynamic content areas */
.joke-list {
  min-height: 400px;
}
```

#### **Optimize Animations**

```css
/* Use transform and opacity for smooth animations */
.joke-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

/* Avoid animating layout properties */
/* Bad: transition: width 0.3s; */
/* Good: transition: transform 0.3s; */
```

---

### 9. Monitoring and Measurement

#### **Performance Monitoring Setup**

```javascript
// src/utils/performance.js
export function reportWebVitals(onPerfEntry) {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
}

// Usage in main.jsx
import { reportWebVitals } from './utils/performance';

reportWebVitals((metric) => {
  console.log(metric);
  // Send to analytics service in production
});
```

#### **Lighthouse CI in GitHub Actions**

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://jokes-website.example.com
            https://jokes-website.example.com/browse
          uploadArtifacts: true
          temporaryPublicStorage: true
```

---

### 10. Performance Budget

**Enforce budgets in Vite:**

```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Create separate chunks
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  }
});

// Add build size check
// package.json
{
  "scripts": {
    "build": "vite build",
    "build:check": "vite build && npm run size-limit"
  },
  "size-limit": [
    {
      "path": "dist/assets/*.js",
      "limit": "150 KB"
    }
  ]
}
```

---

### Performance Checklist

✅ Bundle size < 500 KB (gzipped)
✅ Code splitting by route
✅ Image optimization
✅ Aggressive caching strategy (S3 + CloudFront)
✅ React component memoization
✅ useMemo for expensive computations
✅ CSS containment for layout optimization
✅ Gzip/Brotli compression
✅ Web Vitals monitoring
✅ Lighthouse CI in pipeline
✅ Performance budget enforcement

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
      LLD.md
      PRD.md
      ROAM.md
      epic.yaml
      slices.yaml
      tasks.yaml
      timeline.md
      timeline.yaml
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
