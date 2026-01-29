"""
Test suite for F1 Analytics Workshop API

Tests for health check endpoint and other API functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.main import app, F1APIService


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_f1_service():
    """Create a mock F1APIService for testing"""
    return Mock(spec=F1APIService)


class TestHealthEndpoint:
    """Test cases for the health check endpoint"""

    def test_health_check_success(self, client):
        """Test health check endpoint returns success when external API is accessible"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            # Mock successful external API call
            mock_service = Mock()
            mock_service.make_request.return_value = {"MRData": {"SeasonTable": {"Seasons": []}}}
            mock_get_service.return_value = mock_service

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            # Verify basic health check structure
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert data["service"] == "F1 Analytics Workshop API"
            assert data["version"] == "1.0.0"

            # Verify external API check
            assert "external_api" in data
            assert data["external_api"]["ergast_f1_api"] == "healthy"
            assert "url" in data["external_api"]

    def test_health_check_external_api_failure(self, client):
        """Test health check endpoint when external API is not accessible"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            # Mock external API failure
            mock_service = Mock()
            mock_service.make_request.side_effect = Exception("API connection failed")
            mock_get_service.return_value = mock_service

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            # Verify unhealthy status when external API fails
            assert data["status"] == "unhealthy"
            assert "timestamp" in data
            assert data["service"] == "F1 Analytics Workshop API"

            # Verify external API error is recorded
            assert "external_api" in data
            assert data["external_api"]["ergast_f1_api"] == "unhealthy"
            assert "error" in data["external_api"]

    def test_health_check_response_structure(self, client):
        """Test that health check response has all required fields"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_service.make_request.return_value = {"MRData": {}}
            mock_get_service.return_value = mock_service

            response = client.get("/health")
            data = response.json()

            # Required fields
            required_fields = ["status", "timestamp", "service", "version", "external_api"]
            for field in required_fields:
                assert field in data

            # Timestamp format check (ISO 8601 with Z suffix)
            assert data["timestamp"].endswith("Z")
            assert "T" in data["timestamp"]


class TestRootEndpoint:
    """Test cases for the root endpoint"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns basic API information"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "F1 Analytics Workshop API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestF1APIEndpoints:
    """Test cases for F1 API endpoints"""

    def test_get_seasons(self, client):
        """Test seasons endpoint"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_seasons_data = {
                "MRData": {
                    "SeasonTable": {
                        "Seasons": [
                            {"season": "2023", "url": "http://example.com/2023"},
                            {"season": "2022", "url": "http://example.com/2022"}
                        ]
                    }
                }
            }
            mock_service.make_request.return_value = mock_seasons_data
            mock_get_service.return_value = mock_service

            response = client.get("/seasons")

            assert response.status_code == 200
            data = response.json()
            assert data == mock_seasons_data

    def test_get_seasons_with_params(self, client):
        """Test seasons endpoint with limit and offset parameters"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_service.make_request.return_value = {"MRData": {}}
            mock_get_service.return_value = mock_service

            response = client.get("/seasons?limit=5&offset=10")

            assert response.status_code == 200
            # Verify the correct endpoint was called with parameters
            mock_service.make_request.assert_called_once_with("seasons.json?limit=5&offset=10")

    def test_get_races_for_season(self, client):
        """Test races endpoint for a specific season"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_races_data = {
                "MRData": {
                    "RaceTable": {
                        "season": "2023",
                        "Races": [
                            {"round": "1", "raceName": "Bahrain Grand Prix"},
                            {"round": "2", "raceName": "Saudi Arabian Grand Prix"}
                        ]
                    }
                }
            }
            mock_service.make_request.return_value = mock_races_data
            mock_get_service.return_value = mock_service

            response = client.get("/seasons/2023/races")

            assert response.status_code == 200
            data = response.json()
            assert data == mock_races_data
            mock_service.make_request.assert_called_once_with("2023/races.json")

    def test_get_driver_standings(self, client):
        """Test driver standings endpoint"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_standings_data = {
                "MRData": {
                    "StandingsTable": {
                        "season": "2023",
                        "StandingsLists": [
                            {
                                "DriverStandings": [
                                    {"position": "1", "Driver": {"givenName": "Max", "familyName": "Verstappen"}}
                                ]
                            }
                        ]
                    }
                }
            }
            mock_service.make_request.return_value = mock_standings_data
            mock_get_service.return_value = mock_service

            response = client.get("/seasons/2023/standings/drivers")

            assert response.status_code == 200
            data = response.json()
            assert data == mock_standings_data

    def test_get_race_results(self, client):
        """Test race results endpoint"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            mock_service = Mock()
            mock_results_data = {
                "MRData": {
                    "RaceTable": {
                        "season": "2023",
                        "round": "1",
                        "Races": [
                            {
                                "Results": [
                                    {"position": "1", "Driver": {"givenName": "Max", "familyName": "Verstappen"}}
                                ]
                            }
                        ]
                    }
                }
            }
            mock_service.make_request.return_value = mock_results_data
            mock_get_service.return_value = mock_service

            response = client.get("/seasons/2023/1/results")

            assert response.status_code == 200
            data = response.json()
            assert data == mock_results_data
            mock_service.make_request.assert_called_once_with("2023/1/results.json")


class TestF1APIService:
    """Test cases for the F1APIService class"""

    @patch('requests.Session')
    def test_f1_api_service_initialization(self, mock_session_class):
        """Test F1APIService initializes correctly"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        service = F1APIService()

        assert service.base_url == "https://api.jolpi.ca/ergast/f1"
        assert service.session == mock_session
        mock_session.headers.update.assert_called_once_with({
            'User-Agent': 'F1-Analytics-Workshop/1.0.0'
        })

    @patch('requests.Session')
    def test_make_request_success(self, mock_session_class):
        """Test successful API request"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"test": "data"}
        mock_session.get.return_value = mock_response

        service = F1APIService()
        result = service.make_request("seasons.json")

        assert result == {"test": "data"}
        expected_url = "https://api.jolpi.ca/ergast/f1/seasons.json"
        mock_session.get.assert_called_once_with(expected_url, timeout=30)

    @patch('requests.Session')
    def test_make_request_http_error(self, mock_session_class):
        """Test API request with HTTP error"""
        from fastapi import HTTPException
        import requests

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock HTTP error
        mock_session.get.side_effect = requests.RequestException("Connection failed")

        service = F1APIService()

        with pytest.raises(HTTPException) as exc_info:
            service.make_request("seasons.json")

        assert exc_info.value.status_code == 503
        assert "Error accessing Ergast F1 API" in str(exc_info.value.detail)


class TestErrorHandling:
    """Test cases for error handling scenarios"""

    def test_external_api_service_error(self, client):
        """Test handling when external API service fails"""
        with patch('src.api.main.get_f1_service') as mock_get_service:
            from fastapi import HTTPException
            mock_service = Mock()
            mock_service.make_request.side_effect = HTTPException(
                status_code=503,
                detail="External API error"
            )
            mock_get_service.return_value = mock_service

            response = client.get("/seasons")

            assert response.status_code == 503
            data = response.json()
            assert "External API error" in data["detail"]


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])