from fastapi.testclient import TestClient
from unittest.mock import patch
from weatherforecastlite.main import app

client = TestClient(app)

@patch("weatherforecastlite.main.fetch_weather_data")
def test_forecast_endpoint(mock_fetch):
    mock_response = {
        "generationtime_ms": 0.1,
        "utc_offset_seconds": 7200,
        "timezone": "Europe/Warsaw",
        "timezone_abbreviation": "GMT+2",
        "elevation": 100,
        "hourly_units": {
            "time": "iso8601",
            "cloudcover": "%",
            "temperature_2m": "°C"
        },
        "hourly": {
            "time": ["2025-07-11T21:00"],
            "cloudcover": [10],
            "temperature_2m": [15.0]
        }
    }
    mock_fetch.return_value = mock_response

    response = client.get("/forecast")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 52.232222
    assert data["longitude"] == 21.008333
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["period"] == "2025-07-11/2025-07-12"

@patch("weatherforecastlite.main.fetch_weather_data", side_effect=Exception("API error"))
def test_forecast_endpoint_error(mock_fetch):
    response = client.get("/forecast")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["message"] == "Weather data unavailable. External API did not respond."
