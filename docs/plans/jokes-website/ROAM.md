# ROAM Analysis: jokes-website

**Feature Count:** 15
**Created:** 2026-02-03T11:08:39Z

## Risks

<!-- AI: Identify 5-10 project risks with severity (High/Medium/Low) -->

### 1. **Static Data Maintenance Overhead** (Medium)
Static JSON jokes embedded in the codebase require rebuild and redeploy for every content update. With 20-50 jokes initially, content updates could become frequent as the site grows, leading to deployment fatigue and potential errors from manual JSON editing.

### 2. **S3 Bucket Misconfiguration** (High)
Incorrect S3 bucket policies or permissions could expose the site to security vulnerabilities (overly permissive access) or make it inaccessible (overly restrictive access). The requirement for public read access while preventing bucket listing and maintaining secure configuration is critical.

### 3. **Client-Side Routing with S3/CloudFront** (Medium)
React Router requires all routes to serve `index.html`, but S3's default 404 behavior and CloudFront's error handling need custom configuration. Misconfiguration will break deep linking and cause 404 errors when users refresh on non-root routes.

### 4. **Bundle Size Creep** (Medium)
The 500KB gzipped bundle size requirement is achievable initially, but as features are added or dependencies updated, bundle size can grow quickly. Without strict monitoring and enforcement, performance targets may be missed.

### 5. **Joke Data Quality and Schema Validation** (Low)
Manual creation of 20-50 jokes in JSON format risks typos, missing fields, inconsistent categorization, or malformed data. Invalid data could cause runtime errors or display issues despite the static nature of the site.

### 6. **Limited Testing Coverage for Static Data** (Low)
While component and integration tests are planned, validating that all 20-50 jokes render correctly and that no joke has malformed data requires extensive testing. Test data may not match production data exactly.

### 7. **CloudFront Cache Invalidation Costs and Delays** (Low)
CloudFront cache invalidations have a cost (first 1,000/month free, then $0.005 per path) and take 5-15 minutes to propagate. Frequent deployments with full-site invalidations (`/*`) could lead to unexpected costs and deployment delays.

---

## Obstacles

<!-- AI: Current blockers or challenges (technical, resource, dependency) -->

- **AWS Account and Permissions Setup**: Deployment requires AWS account with S3, CloudFront, and optionally Route 53 access. GitHub Actions needs AWS credentials configured as secrets. If AWS account is not yet set up or IAM permissions are not configured, deployment will be blocked.

- **Joke Content Creation**: Writing 20-50 original, categorized jokes with proper setup/punchline structure is time-consuming and non-technical work. This content creation task is a prerequisite for the data layer implementation and testing.

- **React Router v6 SPA Configuration on S3**: Configuring S3 and CloudFront to properly handle client-side routing (404 → index.html) requires specific error document settings and CloudFront custom error responses. Documentation is available but requires careful implementation to avoid breaking deep links.

- **Lighthouse Performance Score Validation**: Achieving 90+ Lighthouse score requires testing in production-like environment (S3/CloudFront) rather than local dev server. Performance validation is blocked until deployment infrastructure is ready.

---

## Assumptions

<!-- AI: Key assumptions the plan depends on -->

### 1. **AWS S3 and CloudFront are approved and available**
The plan assumes that S3 static hosting and optional CloudFront CDN are approved infrastructure choices and that AWS account access can be provisioned. If organizational constraints prevent AWS usage, an alternative hosting solution (Netlify, Vercel, GitHub Pages) would require architecture changes.

**Validation**: Confirm AWS access and budget approval before Phase 6 (Deployment Setup).

### 2. **20-50 jokes are sufficient for initial release**
The plan assumes that 20-50 jokes provide enough content for a viable initial release and that users will find value in browsing this collection. If user research indicates a need for 100+ jokes for credibility, content creation timelines will extend significantly.

**Validation**: Review PRD success metrics (minimum 20 jokes) and consider user feedback mechanisms post-launch.

### 3. **No backend or dynamic features will be needed**
The architecture assumes that all requirements can be met with static data and client-side logic. If future requirements emerge (user submissions, comments, ratings, analytics beyond basic web analytics), a significant architecture change would be required.

**Validation**: Confirm with stakeholders that feature scope is locked and no user-generated content or interactivity is planned for v1.

### 4. **Vite build tooling is compatible with deployment target**
The plan assumes Vite-generated static assets will work seamlessly with S3/CloudFront without requiring custom server-side rendering or special configuration beyond standard SPA setup.

**Validation**: Test production build deployment to S3 in Phase 6 before finalizing deployment scripts.

### 5. **React and React Router are acceptable dependencies**
The plan assumes that React 18+ and React Router v6 are approved dependencies without licensing, security, or organizational policy concerns. All dependencies are open-source (MIT license).

**Validation**: Run security audit (`npm audit`) during Phase 1 and confirm no high/critical vulnerabilities exist.

---

## Mitigations

<!-- AI: For each risk, propose mitigation strategies -->

### Risk 1: Static Data Maintenance Overhead

**Mitigation Strategies:**

1. **Implement JSON Schema Validation**: Create a JSON schema file for jokes and categories, and add a pre-commit hook or build-time validation script to catch malformed data before deployment.
   ```bash
   npm install -D ajv ajv-cli
   # Add validation script: ajv validate -s schema.json -d src/data/jokes.json
   ```

2. **Create Joke Contribution Guidelines**: Document the joke data structure with examples in `CONTRIBUTING.md` to reduce errors when adding new jokes. Include a template for joke objects.

3. **Build Simple CLI Tool for Joke Management**: Create a Node.js script that allows adding/editing jokes with prompts and validation, reducing manual JSON editing errors.
   ```bash
   # Example: npm run add-joke
   # Prompts for setup, punchline, category, tags
   # Validates and appends to jokes.json
   ```

4. **Plan for Future CMS**: Document in technical debt backlog that if content updates become frequent (>1 per week), consider migrating to a headless CMS with build-time data fetching (e.g., Contentful, Sanity).

---

### Risk 2: S3 Bucket Misconfiguration

**Mitigation Strategies:**

1. **Use Infrastructure as Code (IaC)**: Define S3 bucket and CloudFront configuration using AWS CloudFormation or Terraform templates instead of manual console configuration. Store templates in repository for version control and reproducibility.

2. **Implement Least Privilege Bucket Policy**: Use a minimal bucket policy that allows only `GetObject` for public access, explicitly blocking `ListBucket` and all write operations.
   ```json
   {
     "Effect": "Allow",
     "Principal": "*",
     "Action": "s3:GetObject",
     "Resource": "arn:aws:s3:::jokes-website-bucket/*"
   }
   ```

3. **Enable S3 Block Public Access Settings**: Configure S3 block public access at the account level to prevent accidental exposure, then explicitly allow GetObject via bucket policy.

4. **Security Audit Checklist**: Create deployment checklist that includes:
   - Verify bucket versioning enabled
   - Confirm block public ACLs is enabled
   - Test public access only allows reading objects, not listing
   - Validate no AWS credentials are in repository

5. **Automated Security Scanning**: Add AWS Security Hub or Prowler scanning to CI/CD pipeline to detect misconfigurations automatically.

---

### Risk 3: Client-Side Routing with S3/CloudFront

**Mitigation Strategies:**

1. **Document Exact Configuration Steps**: Create detailed `DEPLOYMENT.md` with step-by-step instructions for S3 error document configuration and CloudFront custom error responses.
   - S3: Set error document to `index.html`
   - CloudFront: Custom error response for 404 → 200 status code, response page `/index.html`

2. **Test Deep Linking During Deployment**: Add automated test in deployment script that:
   - Deploys to staging S3 bucket
   - Tests direct navigation to `/jokes/joke-001`, `/categories/dad-jokes`
   - Validates 200 status codes and correct page rendering
   - Only promotes to production if tests pass

3. **Create Deployment Script Template**: Provide shell script with correct AWS CLI commands for both S3 and CloudFront configuration:
   ```bash
   # Set S3 error document
   aws s3 website s3://bucket --error-document index.html
   
   # CloudFront custom error response (via distribution config update)
   # Include in CloudFormation/Terraform template
   ```

4. **Add E2E Tests for Routing**: Playwright E2E tests should explicitly test direct navigation to all route patterns (not just navigation from home page) to catch routing configuration issues.

---

### Risk 4: Bundle Size Creep

**Mitigation Strategies:**

1. **Implement Bundle Size CI Check**: Add `bundlesize` or `size-limit` package to CI/CD pipeline that fails builds if bundle exceeds thresholds.
   ```json
   // package.json
   {
     "bundlesize": [
       {"path": "dist/assets/*.js", "maxSize": "150 KB"},
       {"path": "dist/assets/*.css", "maxSize": "20 KB"}
     ]
   }
   ```

2. **Regular Bundle Analysis**: Schedule monthly bundle analysis using `rollup-plugin-visualizer` or Vite's built-in analysis to identify large dependencies.
   ```bash
   npm run build -- --report
   # Review generated stats.html for unexpected large modules
   ```

3. **Dependency Audit Process**: Before adding any new npm dependency, require:
   - Check package size on Bundlephobia (https://bundlephobia.com)
   - Evaluate if functionality can be implemented with existing dependencies
   - Document decision in ADR if adding package >10KB

4. **Tree Shaking Verification**: Ensure all imports use named imports (not `import *`) to maximize tree shaking. Configure ESLint rule to warn on default imports from large libraries.

5. **Consider Dynamic Imports for Large Features**: If future features add significant code, use React.lazy() and Suspense for route-based code splitting already planned in LLD.

---

### Risk 5: Joke Data Quality and Schema Validation

**Mitigation Strategies:**

1. **JSON Schema with Build-Time Validation**: Define JSON Schema for jokes and categories, add validation as npm script that runs before build.
   ```bash
   npm run validate-data  # Runs before npm run build
   # Fails build if data doesn't match schema
   ```

2. **Unit Tests for Data Integrity**: Add specific unit tests that:
   - Validate all jokes have required fields (id, setup, punchline, category)
   - Check no duplicate joke IDs
   - Verify all joke categories exist in categories.json
   - Confirm dateAdded fields are valid ISO dates

3. **Manual Review Checklist**: Create content review checklist for joke additions:
   - Setup and punchline are both present and non-empty
   - Category exists and is spelled consistently
   - No offensive or inappropriate content
   - Joke ID follows pattern (joke-XXX with sequential number)

4. **Linting for Common Errors**: Add custom ESLint or markdownlint rules to check for common mistakes (e.g., trailing commas in JSON, inconsistent quote styles).

---

### Risk 6: Limited Testing Coverage for Static Data

**Mitigation Strategies:**

1. **Snapshot Testing for All Jokes**: Use Jest/Vitest snapshot testing to render every joke and detect unexpected rendering changes.
   ```javascript
   test('all jokes render without errors', () => {
     jokes.forEach(joke => {
       const { container } = render(<JokeCard joke={joke} />);
       expect(container).toMatchSnapshot();
     });
   });
   ```

2. **Parameterized Tests**: Use test.each() to run component tests against all real production jokes, not just mock data.
   ```javascript
   test.each(jokes)('joke $id displays correctly', (joke) => {
     render(<JokeCard joke={joke} />);
     expect(screen.getByText(joke.setup)).toBeInTheDocument();
   });
   ```

3. **Visual Regression Testing**: Add Percy, Chromatic, or similar visual regression testing to E2E suite to catch rendering issues across all joke cards.

4. **Production Smoke Tests**: After deployment, run automated smoke tests that randomly sample 10 jokes and verify they load without console errors.

---

### Risk 7: CloudFront Cache Invalidation Costs and Delays

**Mitigation Strategies:**

1. **Invalidate Only Changed Paths**: Instead of invalidating entire distribution (`/*`), track changed files during deployment and invalidate only affected paths.
   ```bash
   # Compare previous build manifest to current, invalidate only changed files
   aws cloudfront create-invalidation --paths /index.html /assets/app.abc123.js
   ```

2. **Use Cache-Busting for Assets**: Ensure all JS/CSS assets use content hashing in filename (Vite does this by default). This allows long cache times without requiring invalidation since new deployments create new filenames.

3. **Short TTL for index.html**: Set index.html cache to 5 minutes so most users get fresh content without requiring invalidation. Balance between freshness and reduced invalidation needs.

4. **Deployment Throttling**: Limit deployments to production to once per day or on-demand for critical fixes. Use staging environment for testing to reduce production invalidations.

5. **Monitor Invalidation Costs**: Set up AWS Budgets alert if CloudFront invalidation costs exceed $5/month threshold, indicating too-frequent deployments.

6. **Document Invalidation Strategy**: Add to `DEPLOYMENT.md`:
   - First 1,000 invalidation paths/month are free
   - Full site invalidation (`/*`) counts as 1 path
   - Prefer targeted invalidations for large deployments
   - Consider if immediate cache clear is necessary or if 5-15 min delay is acceptable

---

## Appendix: Plan Documents

### PRD
# Product Requirements Document: Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

**Created:** 2026-02-03T10:57:56Z
**Status:** Draft

## 1. Overview

**Concept:** Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

**Description:** Make a website full of jokes - it only needs to run on s3 static hosting so no need for a database or servers - just build the react frontend

---

## 2. Goals

- Build a static React-based website that displays jokes to users
- Deploy the application to S3 static hosting with no server-side dependencies
- Provide an engaging and responsive user interface for browsing jokes
- Include a collection of jokes embedded within the frontend application
- Ensure the website works seamlessly across desktop and mobile devices

---

## 3. Non-Goals

- Implementing user authentication or user accounts
- Building a backend API or database infrastructure
- Creating admin tools for content management
- Implementing user-generated content or joke submissions
- Supporting real-time features or WebSocket connections

---

## 4. User Stories

- As a visitor, I want to view jokes on the homepage so that I can be entertained
- As a user, I want to browse through multiple jokes so that I can find ones I enjoy
- As a mobile user, I want the website to work well on my phone so that I can read jokes on the go
- As a user, I want to navigate between different jokes easily so that I can quickly find new content
- As a user, I want the website to load quickly so that I don't have to wait to see jokes
- As a visitor, I want to see different categories of jokes so that I can find the type of humor I prefer
- As a user, I want the website to have a clean, readable design so that jokes are easy to read
- As a repeat visitor, I want to see a variety of jokes so that I don't see the same content every time

---

## 5. Acceptance Criteria

**Story: View jokes on the homepage**
- Given I visit the website
- When the page loads
- Then I should see at least one joke displayed on screen

**Story: Browse through multiple jokes**
- Given I am on the website
- When I click a "Next" or navigation button
- Then I should see a different joke displayed

**Story: Mobile responsiveness**
- Given I access the website on a mobile device
- When the page renders
- Then the layout should adapt to my screen size and text should be readable without zooming

**Story: Navigate between jokes**
- Given I am viewing a joke
- When I use navigation controls
- Then I should be able to move forward and backward through jokes

**Story: Fast loading**
- Given I visit the website URL
- When the page loads
- Then the initial content should be visible within 2 seconds on a standard connection

---

## 6. Functional Requirements

- **FR-001**: The application shall be built using React framework
- **FR-002**: The application shall store jokes as static data within the frontend codebase
- **FR-003**: The application shall display individual jokes with readable formatting
- **FR-004**: The application shall provide navigation controls to move between jokes
- **FR-005**: The application shall be deployable to AWS S3 as a static website
- **FR-006**: The application shall include at least 20-50 jokes in the initial release
- **FR-007**: The application shall have a responsive layout that works on mobile and desktop
- **FR-008**: The application shall support client-side routing for different views
- **FR-009**: The application shall include a home page that serves as the main entry point
- **FR-010**: The application shall display jokes in a clear, easy-to-read format

---

## 7. Non-Functional Requirements

### Performance
- Initial page load time should be under 2 seconds on 3G connection
- Time to Interactive (TTI) should be under 3 seconds
- Bundle size should be optimized and kept under 500KB (gzipped)
- Images and assets should be optimized for web delivery

### Security
- All resources should be served over HTTPS
- No sensitive data or API keys should be embedded in the frontend code
- Content Security Policy headers should be configured in S3
- Cross-Origin Resource Sharing (CORS) should be properly configured

### Scalability
- Static hosting on S3 should handle high traffic volumes without degradation
- CloudFront CDN can be added for global distribution if needed
- Application should work without any server-side scaling concerns

### Reliability
- Website should have 99.9% uptime leveraging S3's infrastructure
- Application should gracefully handle missing or malformed joke data
- Errors should be handled to prevent blank screens or crashes

---

## 8. Dependencies

- **React**: Frontend framework for building the user interface
- **React Router**: For client-side routing between pages/views
- **Node.js & npm**: For build tooling and dependency management
- **Create React App or Vite**: Build toolchain for React application
- **AWS S3**: Static hosting platform for deployment
- **AWS CLI or S3 deployment tools**: For deploying built assets to S3

---

## 9. Out of Scope

- Backend server or API development
- Database setup or management
- User authentication and authorization
- Content Management System (CMS) for joke administration
- User comments or social features
- Dynamic joke loading from external APIs
- Analytics or tracking beyond basic static website analytics
- Joke submission forms or user-generated content
- Payment processing or monetization features
- Email notifications or subscriptions

---

## 10. Success Metrics

- Successfully deploy the React application to S3 static hosting
- Achieve page load time of under 2 seconds
- Display minimum of 20 jokes accessible through the interface
- Pass responsive design testing on mobile devices (320px width minimum)
- Achieve Lighthouse performance score of 90+ for performance
- Zero critical console errors in production build
- Successful navigation between all routes without errors

---

## Appendix: Clarification Q&A

### Clarification Questions & Answers


### HLD
[Previous HLD content remains the same]

### LLD
[Previous LLD content remains the same]
