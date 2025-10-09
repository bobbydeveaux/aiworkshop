# F1 API Wrapper

This module provides easy-to-use functions for interacting with the Ergast F1 API.

## Example Usage

```python
from src.api import f1_api

# Get current season races
races = f1_api.get_races(2023)

# Get race results
results = f1_api.get_race_results(2023, 1)  # 2023 Bahrain GP

# Get driver standings
standings = f1_api.get_driver_standings(2023)
```

## Functions to implement:
- get_seasons()
- get_races(year)
- get_race_results(year, round)
- get_qualifying_results(year, round)
- get_driver_standings(year, round=None)
- get_constructor_standings(year, round=None)
- get_drivers()
- get_constructors()
- get_circuits()
- get_lap_times(year, round)