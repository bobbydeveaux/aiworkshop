# ROAM Analysis: jokes-website

**Feature Count:** 14
**Created:** 2026-02-03T08:35:28Z

## Risks

<!-- AI: Identify 5-10 project risks with severity (High/Medium/Low) -->

1. **Bundle Size Exceeding 500KB Limit** (Medium): The PRD requires JavaScript bundle size under 500KB gzipped. With React, React Router, and jokes data included, there's risk of exceeding this limit as the joke dataset grows. Initial estimates show 200KB for core app, but adding 50+ jokes with rich metadata could push toward the limit.

2. **S3 SPA Routing Configuration Failure** (High): Client-side routing requires S3 error document redirect to index.html. Misconfiguration will result in 404 errors when users directly access routes like /jokes/joke-001 or refresh pages. This is a critical blocker for production launch.

3. **Lighthouse Performance Score Regression** (Medium): The PRD mandates Lighthouse score >90. Performance can degrade due to unoptimized images, excessive re-renders, large CSS bundles, or inefficient React hooks. Without continuous monitoring, scores may drop below threshold.

4. **JSON Data Loading Race Conditions** (Low): The useJokes hook loads data on mount. If multiple components call this hook simultaneously before data loads, it could trigger multiple fetch requests. While unlikely to break functionality, it wastes bandwidth and could slow initial load.

5. **Joke Dataset Quality and Curation** (Medium): The project requires 50+ jokes across multiple categories. Curating, formatting, and validating this content is non-trivial. Poor joke quality, offensive content, or inconsistent categorization could impact user experience and require rework.

6. **CloudFront Cache Invalidation Delays** (Low): After deployment, CloudFront cache invalidation can take 5-15 minutes to propagate globally. Users may see stale content during this window, particularly problematic if fixing critical bugs.

7. **No Rollback Testing in Staging** (Medium): The LLD defines rollback procedures but doesn't mandate testing them before production launch. Untested rollback processes may fail during actual incidents, extending downtime.

---

## Obstacles

<!-- AI: Current blockers or challenges (technical, resource, dependency) -->

- **No Joke Dataset Exists Yet**: The project requires 50+ jokes formatted as JSON with proper categorization, IDs, and metadata. This content creation task is not assigned and could delay Phase 2 development if not started immediately.

- **AWS Account and Credentials Setup Required**: Deployment requires AWS S3 bucket, CloudFront distribution, IAM credentials, and GitHub Secrets configuration. If AWS account setup is pending or requires approval, it blocks Phase 4 deployment testing.

- **Vite and React Router v6 Learning Curve**: If the development team is unfamiliar with Vite (vs. Create React App) or React Router v6 (major API changes from v5), implementation time may increase. The LLD assumes familiarity with these tools.

- **No Design Mockups or Style Guide**: The LLD specifies CSS Modules and responsive design but provides no visual design, color scheme, or typography guidelines. Without design direction, styling could require multiple iterations and delay completion.

---

## Assumptions

<!-- AI: Key assumptions the plan depends on -->

1. **Single Developer or Small Team**: The 8-day migration timeline assumes dedicated developer(s) working full-time on this project with no context-switching. If developers are split across multiple projects, timeline extends significantly. *Validation: Confirm team allocation and availability before starting Phase 1.*

2. **AWS Services Available in Target Region**: The plan assumes AWS S3, CloudFront, and Route 53 are available and performant in the chosen deployment region (likely us-east-1). *Validation: Verify AWS service availability and pricing in target region before infrastructure setup.*

3. **Modern Browser Support Only**: The design assumes users access the site via modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions). No IE11 or legacy browser support is planned. *Validation: Confirm with stakeholders that <5% of users are on legacy browsers.*

4. **Static Joke Dataset Acceptable**: The plan assumes jokes are curated at build time and deployed statically - no user-generated content, no admin panel for adding jokes. Changes require redeployment. *Validation: Confirm with stakeholders that manual joke updates are acceptable for v1.*

5. **No SEO Requirements**: The architecture uses client-side rendering with no SSR/SSG. This limits SEO effectiveness (search engines may not index joke detail pages well). *Validation: Confirm that organic search traffic is not a primary success metric for v1.*

---

## Mitigations

<!-- AI: For each risk, propose mitigation strategies -->

### Risk 1: Bundle Size Exceeding 500KB Limit

**Mitigation Actions:**
- **Action 1.1**: Implement bundle size monitoring in CI/CD. Add webpack-bundle-analyzer or vite-plugin-bundle-analyzer to visualize bundle composition. Fail builds if total gzipped size exceeds 450KB (10% buffer).
- **Action 1.2**: Keep jokes.json as separate lazy-loaded asset (not bundled). Use fetch() in useJokes hook rather than import statement. This excludes joke data from initial bundle.
- **Action 1.3**: Implement route-based code splitting with React.lazy() for all page components (Home, JokesList, JokeDetail, Categories). This defers loading non-critical code until needed.
- **Action 1.4**: If joke dataset grows beyond 500 jokes, split jokes.json into category-specific files (jokes-puns.json, jokes-dad-jokes.json) and lazy-load on category selection.

### Risk 2: S3 SPA Routing Configuration Failure

**Mitigation Actions:**
- **Action 2.1**: Document exact S3 configuration in deployment guide with screenshots. Set both "Index document" AND "Error document" to index.html in S3 static website hosting settings.
- **Action 2.2**: Add automated E2E test that directly accesses /jokes/joke-001 URL (not by navigation) to verify deep linking works. Fail deployment if this test fails.
- **Action 2.3**: Configure CloudFront custom error responses: 404 → index.html (200 status), 403 → index.html (200 status). This ensures both S3 and CloudFront layers handle SPA routing.
- **Action 2.4**: Test routing configuration in staging environment before production. Access multiple routes directly via URL and refresh pages to confirm no 404s.

### Risk 3: Lighthouse Performance Score Regression

**Mitigation Actions:**
- **Action 3.1**: Implement Lighthouse CI in GitHub Actions (per LLD section 12.8). Run on every PR and fail if score drops below 90. Use treosh/lighthouse-ci-action with budget.json configuration.
- **Action 3.2**: Establish performance budget: FCP <1.5s, LCP <2.5s, TTI <3s, bundle <500KB. Monitor in CI/CD and block merges that violate budget.
- **Action 3.3**: Optimize React rendering: Use React.memo for JokeCard component, useMemo for category filtering, and useCallback for event handlers. Profile with React DevTools Profiler.
- **Action 3.4**: Implement image optimization checklist: Use WebP format, add loading="lazy" to below-fold images, compress with imagemin, and add srcset for responsive images.

### Risk 4: JSON Data Loading Race Conditions

**Mitigation Actions:**
- **Action 4.1**: Implement singleton pattern in jokeDataLoader.js. Cache first fetch() promise and return same promise for subsequent calls. This prevents duplicate network requests.
  ```javascript
  let jokesPromise = null;
  export function loadJokes() {
    if (!jokesPromise) {
      jokesPromise = fetch('/data/jokes.json').then(r => r.json());
    }
    return jokesPromise;
  }
  ```
- **Action 4.2**: Add loading state deduplication in useJokes hook. Track loading state globally (using ref or context) to prevent multiple simultaneous loads.
- **Action 4.3**: Test race condition scenario: Mount multiple components using useJokes hook simultaneously and verify only one network request occurs. Check browser Network tab.

### Risk 5: Joke Dataset Quality and Curation

**Mitigation Actions:**
- **Action 5.1**: Create joke dataset specification document defining: acceptable joke types, category taxonomy (5-7 categories max), required metadata fields, and content guidelines (no offensive material).
- **Action 5.2**: Assign dedicated content curator role. Allocate 8-16 hours for joke research, curation, and formatting. Source jokes from public domain collections (e.g., /r/jokes archive, joke APIs).
- **Action 5.3**: Implement JSON schema validation in build process. Use ajv or similar to validate jokes.json structure before deployment. Fail builds on validation errors.
- **Action 5.4**: Add joke preview/review step: Build simple HTML page that displays all jokes for manual review before production deployment. Check for typos, formatting, categorization.

### Risk 6: CloudFront Cache Invalidation Delays

**Mitigation Actions:**
- **Action 6.1**: Implement versioned deployments: Deploy to /v1/, /v2/ paths instead of root. Update CloudFront origin path to switch versions. This provides instant rollback without invalidation.
- **Action 6.2**: Set short TTL (5 minutes) on index.html in CloudFront. Only invalidate index.html on critical deployments. Static assets (JS/CSS) use hashed filenames and don't need invalidation.
- **Action 6.3**: Add health check endpoint or meta tag in index.html with build timestamp. Monitor this to confirm new version deployed before announcing updates.
- **Action 6.4**: For critical hotfixes, use S3 versioning rollback (2-5 minutes) instead of waiting for invalidation. Document this as primary rollback method in runbook.

### Risk 7: No Rollback Testing in Staging

**Mitigation Actions:**
- **Action 7.1**: Add rollback testing to Phase 5 checklist (Day 8). Deploy v1.0 to staging, then v1.1 with intentional breaking change, then rollback to v1.0 using all three rollback methods (S3 versioning, Git revert, blue-green).
- **Action 7.2**: Create rollback runbook in jokes-website/docs/ROLLBACK.md with step-by-step commands for each method. Include screenshots and expected outputs.
- **Action 7.3**: Automate S3 versioning rollback with script (jokes-website/scripts/rollback.sh). Test script in staging before production launch.
- **Action 7.4**: Document rollback decision matrix (per LLD section 11) and train team on when to use each rollback method. Conduct tabletop exercise simulating production incident.

---

## Appendix: Plan Documents

### PRD
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


### HLD
[HLD content included in planning context above]

### LLD
[LLD content included in planning context above]
