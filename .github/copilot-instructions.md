# Copilot Instructions for F1 Analytics Workshop

## Repository Purpose

This repository is dedicated to Formula 1 statistical analysis using the Ergast F1 API (https://api.jolpi.ca/ergast/). The primary goal is to build comprehensive data analysis tools and insights for Formula 1 racing data.

## Context for AI Assistants

### Project Domain
- **Sport**: Formula 1 Racing
- **Data Source**: Ergast F1 API (comprehensive F1 database from 1950-present)
- **Focus**: Statistical analysis, data visualization, and predictive modeling
- **Language Preference**: Python for data analysis, but open to other languages as appropriate

### Key Data Entities
- **Races**: Events in the F1 calendar with results, lap times, and qualifying data
- **Drivers**: Individual racers with career statistics and performance metrics
- **Constructors**: Racing teams/manufacturers (e.g., Ferrari, Mercedes, Red Bull)
- **Circuits**: Racing tracks with characteristics and historical data
- **Seasons**: Annual championships with standings and results

### API Endpoints to Know
```
Base URL: https://api.jolpi.ca/ergast/f1/

Key endpoints:
- /seasons.json - All F1 seasons
- /{year}/races.json - Races for specific year
- /{year}/{round}/results.json - Race results
- /{year}/driverStandings.json - Driver standings
- /{year}/constructorStandings.json - Constructor standings
- /drivers.json - All drivers
- /constructors.json - All constructors
- /circuits.json - All circuits
```

### Statistical Analysis Goals

#### Performance Analytics
- Lap time analysis and sector comparisons
- Qualifying vs race performance correlation
- Weather impact assessment
- Tire strategy effectiveness analysis
- DNF (Did Not Finish) rate analysis

#### Predictive Modeling
- Race outcome prediction based on qualifying
- Championship probability calculations
- Performance trend forecasting
- Reliability prediction models

#### Historical Analysis
- Era comparisons (regulation changes impact)
- Driver career trajectory analysis
- Constructor dominance periods
- Circuit evolution and performance changes

### Coding Guidelines

#### Data Handling
- Always respect API rate limits (200 requests/hour, 4 requests/second)
- Cache API responses when possible to avoid redundant calls
- Handle missing data gracefully (not all historical data is complete)
- Use appropriate data structures for time series analysis

#### Code Style
- Follow Python PEP 8 for Python code
- Use meaningful variable names that reflect F1 terminology
- Add docstrings explaining statistical methods and assumptions
- Include data source references in analysis

#### Analysis Standards
- Always include confidence intervals for statistical estimates
- Document data preprocessing steps
- Validate assumptions before applying statistical tests
- Consider seasonal effects and regulation changes in analysis

### Common F1 Terms and Concepts

#### Racing Terms
- **Pole Position**: First place on the starting grid (fastest qualifier)
- **DNF**: Did Not Finish
- **DNS**: Did Not Start
- **DSQ**: Disqualified
- **Fastest Lap**: Quickest lap time during the race
- **Grid Position**: Starting position based on qualifying results

#### Technical Terms
- **Power Unit**: Engine and energy recovery systems
- **DRS**: Drag Reduction System (overtaking aid)
- **Tire Compounds**: Different tire types (Soft, Medium, Hard)
- **Sectors**: Track divided into 3 timing sections
- **Parc Fermé**: Restricted car modifications period

#### Championship System
- **Points System**: 25-18-15-12-10-8-6-4-2-1 for top 10 finishers
- **Constructors Championship**: Team-based championship
- **Drivers Championship**: Individual driver championship

### Data Analysis Patterns

#### Time Series Analysis
- Race results over seasons
- Performance trends within seasons
- Career progression analysis
- Technology development impact

#### Comparative Analysis
- Driver vs driver performance
- Constructor vs constructor comparison
- Circuit performance variations
- Era-to-era comparisons

#### Statistical Modeling
- Regression analysis for performance prediction
- Clustering for driver/constructor grouping
- Classification for race outcome prediction
- Survival analysis for reliability studies

### Best Practices for AI Assistance

1. **Context Awareness**: Always consider the F1 domain when suggesting solutions
2. **Data Validation**: Verify data makes sense in F1 context (e.g., lap times should be reasonable)
3. **Historical Context**: Account for regulation changes when analyzing historical trends
4. **Performance Focus**: Prioritize meaningful F1 performance metrics over generic statistics
5. **Visualization**: Suggest F1-appropriate visualizations (race progression charts, championship standings, etc.)

### Example Analysis Questions to Address

- Which drivers perform best in wet weather conditions?
- How does qualifying position correlate with race finish position at different circuits?
- What factors contribute most to championship success?
- How has the performance gap between top teams evolved over time?
- Which circuits favor certain driving styles or car characteristics?
- How effective are different tire strategies across various track types?

### File Organization Suggestions

```
data/
├── raw/           # Direct API responses
├── processed/     # Cleaned and transformed data
└── cache/         # Cached API responses

src/
├── api/           # API interaction modules
├── analysis/      # Statistical analysis functions
├── visualization/ # Plotting and charting utilities
└── models/        # Predictive models

notebooks/
├── exploratory/   # Initial data exploration
├── analysis/      # Detailed analysis notebooks
└── reports/       # Final analysis reports
```

### Common Pitfalls to Avoid

1. **Regulation Changes**: Don't compare across major regulation changes without context
2. **Missing Data**: Historical data may be incomplete, especially pre-1980s
3. **API Limits**: Respect rate limits to avoid getting blocked
4. **Context Sensitivity**: F1 performance is highly context-dependent (weather, track, car setup)
5. **Sample Size**: Some drivers/constructors have limited data for statistical significance

### Useful Libraries and Tools

#### Python
- `requests` - API calls
- `pandas` - Data manipulation
- `numpy` - Numerical analysis
- `matplotlib/seaborn` - Visualization
- `scikit-learn` - Machine learning
- `statsmodels` - Statistical analysis
- `plotly` - Interactive visualizations

#### Suggested Workflow
1. Define clear analytical question
2. Identify required data from Ergast API
3. Implement efficient data collection with caching
4. Clean and validate data
5. Perform exploratory data analysis
6. Apply appropriate statistical methods
7. Visualize results clearly
8. Document findings and methodology

This repository aims to provide valuable insights into Formula 1 performance through rigorous statistical analysis and data-driven approaches.