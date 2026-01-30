"""
F1 Analytics Workshop API Server

A FastAPI-based web server that provides health check endpoints and F1 data analysis APIs
using the Ergast F1 API as the data source.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

app = FastAPI(
    title="F1 Analytics Workshop API",
    description="A comprehensive API for Formula 1 statistical analysis using the Ergast F1 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ergast F1 API base URL
ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

# API rate limiting configuration
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


class F1APIService:
    """Service class for interacting with the Ergast F1 API"""

    def __init__(self):
        self.base_url = ERGAST_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'F1-Analytics-Workshop/1.0.0'
        })

    def make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a request to the Ergast API with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error accessing Ergast F1 API: {str(e)}"
            )


# Dependency to get F1 API service instance
def get_f1_service() -> F1APIService:
    return F1APIService()


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint that verifies the API server is running
    and can access the external Ergast F1 API.

    Returns:
        Dict containing health status, timestamp, and external API status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "F1 Analytics Workshop API",
        "version": "1.0.0"
    }

    # Check connectivity to external Ergast API
    try:
        f1_service = get_f1_service()
        # Make a lightweight request to check API availability
        f1_service.make_request("seasons.json?limit=1")
        health_status["external_api"] = {
            "ergast_f1_api": "healthy",
            "url": ERGAST_BASE_URL
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["external_api"] = {
            "ergast_f1_api": "unhealthy",
            "error": str(e),
            "url": ERGAST_BASE_URL
        }

    return health_status


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint providing basic API information"""
    return {
        "message": "F1 Analytics Workshop API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/seasons")
async def get_seasons(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get list of all F1 seasons

    Args:
        limit: Maximum number of results to return
        offset: Number of results to skip

    Returns:
        Dict containing seasons data from Ergast API
    """
    endpoint = "seasons.json"

    # Add query parameters if provided
    params = []
    if limit is not None:
        params.append(f"limit={limit}")
    if offset is not None:
        params.append(f"offset={offset}")

    if params:
        endpoint += "?" + "&".join(params)

    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/races")
async def get_races(
    year: int,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get all races for a specific season

    Args:
        year: The F1 season year

    Returns:
        Dict containing race data for the specified year
    """
    endpoint = f"{year}/races.json"
    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/drivers")
async def get_season_drivers(
    year: int,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get all drivers for a specific season

    Args:
        year: The F1 season year

    Returns:
        Dict containing driver data for the specified year
    """
    endpoint = f"{year}/drivers.json"
    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/constructors")
async def get_season_constructors(
    year: int,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get all constructors for a specific season

    Args:
        year: The F1 season year

    Returns:
        Dict containing constructor data for the specified year
    """
    endpoint = f"{year}/constructors.json"
    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/standings/drivers")
async def get_driver_standings(
    year: int,
    round_num: Optional[int] = None,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get driver championship standings for a specific season

    Args:
        year: The F1 season year
        round_num: Optional specific round number

    Returns:
        Dict containing driver standings data
    """
    if round_num is not None:
        endpoint = f"{year}/{round_num}/driverStandings.json"
    else:
        endpoint = f"{year}/driverStandings.json"

    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/standings/constructors")
async def get_constructor_standings(
    year: int,
    round_num: Optional[int] = None,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get constructor championship standings for a specific season

    Args:
        year: The F1 season year
        round_num: Optional specific round number

    Returns:
        Dict containing constructor standings data
    """
    if round_num is not None:
        endpoint = f"{year}/{round_num}/constructorStandings.json"
    else:
        endpoint = f"{year}/constructorStandings.json"

    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/{round_num}/results")
async def get_race_results(
    year: int,
    round_num: int,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get race results for a specific race

    Args:
        year: The F1 season year
        round_num: The race round number in the season

    Returns:
        Dict containing race results data
    """
    endpoint = f"{year}/{round_num}/results.json"
    return f1_service.make_request(endpoint)


@app.get("/seasons/{year}/{round_num}/qualifying")
async def get_qualifying_results(
    year: int,
    round_num: int,
    f1_service: F1APIService = Depends(get_f1_service)
) -> Dict[str, Any]:
    """
    Get qualifying results for a specific race

    Args:
        year: The F1 season year
        round_num: The race round number in the season

    Returns:
        Dict containing qualifying results data
    """
    endpoint = f"{year}/{round_num}/qualifying.json"
    return f1_service.make_request(endpoint)


if __name__ == "__main__":
    # Run the server when executed directly
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )