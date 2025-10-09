# F1 Analytics Workshop

A comprehensive repository for Formula 1 statistical analysis using the Ergast F1 API. This project focuses on building data-driven insights and analytics for Formula 1 racing data.

## Overview

This repository provides tools and analysis capabilities for Formula 1 data using the [Ergast F1 API](https://api.jolpi.ca/ergast/). The Ergast API offers comprehensive historical F1 data including:

- Race results and standings
- Driver and constructor information
- Circuit details and lap times
- Qualifying results and practice sessions
- Historical data from 1950 to present

## Project Goals

- **Statistical Analysis**: Build comprehensive statistical models for F1 performance analysis
- **Data Visualization**: Create insightful visualizations of F1 trends and patterns
- **Predictive Modeling**: Develop models to predict race outcomes and championship standings
- **Historical Analysis**: Analyze historical trends in F1 performance and technology evolution

## API Endpoints

The Ergast F1 API provides various endpoints for different types of data:

### Base URL
```
https://api.jolpi.ca/ergast/
```

### Key Endpoints
- `/f1/seasons.json` - List of all F1 seasons
- `/f1/{year}/races.json` - Races for a specific year
- `/f1/{year}/{round}/results.json` - Race results
- `/f1/{year}/driverStandings.json` - Driver championship standings
- `/f1/{year}/constructorStandings.json` - Constructor championship standings
- `/f1/drivers.json` - All drivers information
- `/f1/constructors.json` - All constructors information
- `/f1/circuits.json` - All circuits information

### Example Usage
```bash
# Get all races for 2023 season
curl "https://api.jolpi.ca/ergast/f1/2023/races.json"

# Get race results for Monaco GP 2023
curl "https://api.jolpi.ca/ergast/f1/2023/6/results.json"

# Get current driver standings
curl "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
```

## Project Structure

```
aiworkshop/
├── README.md                 # This file
├── .github/
│   └── copilot-instructions.md  # AI assistant guidelines
├── data/                     # Raw and processed F1 data
├── src/                      # Source code for analysis tools
├── notebooks/                # Jupyter notebooks for analysis
├── visualizations/           # Generated charts and graphs
├── models/                   # Statistical and ML models
└── docs/                     # Additional documentation
```

## Getting Started

### Prerequisites
- Python 3.8+ or Node.js 16+
- Internet connection for API access
- Git for version control

### Installation
```bash
# Clone the repository
git clone https://github.com/bobbydeveaux/aiworkshop.git
cd aiworkshop

# Install dependencies (Python example)
pip install -r requirements.txt

# Or for Node.js
npm install
```

### Quick Start
```python
# Example: Get latest race results
import requests

url = "https://api.jolpi.ca/ergast/f1/current/last/results.json"
response = requests.get(url)
data = response.json()

# Extract race results
race_results = data['MRData']['RaceTable']['Races'][0]['Results']
for result in race_results:
    driver = result['Driver']
    position = result['position']
    print(f"{position}: {driver['givenName']} {driver['familyName']}")
```

## Statistical Analysis Areas

### Performance Analytics
- Lap time analysis and trends
- Qualifying vs race performance correlation
- Weather impact on performance
- Tire strategy effectiveness

### Driver Analytics
- Career progression analysis
- Head-to-head comparisons
- Consistency metrics
- Championship probability models

### Constructor Analytics
- Technical development trends
- Reliability analysis
- Resource allocation effectiveness
- Power unit performance comparison

### Circuit Analytics
- Track characteristics analysis
- Overtaking opportunity assessment
- Weather pattern impact
- Historical performance trends

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-analysis`)
3. Commit your changes (`git commit -m 'Add amazing F1 analysis'`)
4. Push to the branch (`git push origin feature/amazing-analysis`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new analysis functions
- Document new features and API usage
- Include data sources and methodology in analysis

## API Rate Limits

The Ergast API has the following limits:
- 200 requests per hour per IP
- 4 requests per second
- Be respectful with API usage

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [Ergast F1 API Documentation](http://ergast.com/mrd/)
- [Formula 1 Official Website](https://www.formula1.com/)
- [F1 Technical Regulations](https://www.fia.com/regulation/category/110)

## Acknowledgments

- Ergast for providing the comprehensive F1 API
- The Formula 1 community for data insights and analysis inspiration