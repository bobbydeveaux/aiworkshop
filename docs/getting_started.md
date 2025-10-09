# F1 Analytics Workshop - Getting Started

## Quick Setup Guide

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv f1_analytics
source f1_analytics/bin/activate  # On Windows: f1_analytics\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. First Data Analysis
Create your first analysis by exploring recent race results:

```python
import requests
import pandas as pd

# Get latest race results
url = "https://api.jolpi.ca/ergast/f1/current/last/results.json"
response = requests.get(url)
data = response.json()

# Extract and analyze data
race_data = data['MRData']['RaceTable']['Races'][0]
results = race_data['Results']

# Create DataFrame
df = pd.DataFrame([
    {
        'Position': int(result['position']),
        'Driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
        'Constructor': result['Constructor']['name'],
        'Points': float(result['points']) if result['points'] else 0
    }
    for result in results
])

print(df)
```

### 3. API Exploration Examples

#### Get All Seasons
```python
seasons_url = "https://api.jolpi.ca/ergast/f1/seasons.json"
seasons = requests.get(seasons_url).json()
```

#### Get Driver Standings
```python
standings_url = "https://api.jolpi.ca/ergast/f1/2023/driverStandings.json"
standings = requests.get(standings_url).json()
```

#### Get Circuit Information
```python
circuits_url = "https://api.jolpi.ca/ergast/f1/circuits.json"
circuits = requests.get(circuits_url).json()
```

### 4. Common Analysis Patterns

#### Race Results Analysis
```python
def analyze_race_results(year, round_num):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/{round_num}/results.json"
    data = requests.get(url).json()
    # Process results...
    return processed_data
```

#### Performance Trend Analysis
```python
def driver_performance_trend(driver_id, seasons):
    results = []
    for season in seasons:
        # Fetch season data for driver
        url = f"https://api.jolpi.ca/ergast/f1/{season}/drivers/{driver_id}/results.json"
        # Process and accumulate results...
    return trend_data
```

### 5. Visualization Examples

#### Championship Standings Plot
```python
import matplotlib.pyplot as plt

def plot_championship_standings(year):
    # Fetch standings data
    # Create visualization
    plt.figure(figsize=(12, 8))
    # Plot data...
    plt.title(f'F1 {year} Championship Standings')
    plt.show()
```

### 6. Project Development Workflow

1. **Data Collection**: Use API to gather relevant F1 data
2. **Data Cleaning**: Handle missing values and inconsistencies
3. **Exploratory Analysis**: Understand data patterns and distributions
4. **Statistical Analysis**: Apply appropriate statistical methods
5. **Visualization**: Create clear and informative charts
6. **Documentation**: Document findings and methodology

### 7. Best Practices

- Always cache API responses to avoid hitting rate limits
- Validate data ranges and check for outliers
- Consider regulation changes when comparing across years
- Use meaningful variable names related to F1 terminology
- Document your analysis assumptions and limitations

## Next Steps

1. Explore the `/notebooks/exploratory/` directory for example analyses
2. Check `/src/api/` for API wrapper functions
3. Review `/src/analysis/` for statistical analysis utilities
4. Look at `/docs/` for detailed documentation

Happy analyzing! 🏎️