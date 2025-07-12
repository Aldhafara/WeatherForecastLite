from fastapi.testclient import TestClient
from unittest.mock import patch
from weatherforecastlite.main import app

MOCK_WEATHER_RESPONSE = {
        "generationtime_ms": 0.1,
        "utc_offset_seconds": 7200,
        "timezone": "Europe/Warsaw",
        "timezone_abbreviation": "GMT+2",
        "elevation": 100,
        "hourly_units": {
            "time": "iso8601",
            "cloudcover": "%",
            "temperature_2m": "°C",
            "visibility":"m",
            "windspeed_10m":"m/s",
            "windgusts_10m":"m/s"
        },
        "hourly": {
            "time": ["2025-07-11T21:00"],
            "cloudcover": [10],
            "temperature_2m": [15.0],
            "visibility":[16720.0],
            "windspeed_10m":[4.7],
            "windgusts_10m":[8.9]
        }
    }

client = TestClient(app)

@patch("weatherforecastlite.main.fetch_weather_data")
def test_forecast_endpoint(mock_fetch):
    mock_response = MOCK_WEATHER_RESPONSE
    mock_fetch.return_value = mock_response

    response = client.get("/forecast")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 52.232222
    assert data["longitude"] == 21.008333
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["period"] == "2025-07-11/2025-07-12"

@patch("weatherforecastlite.main.fetch_weather_data", side_effect=Exception("Weather API error"))
def test_forecast_endpoint_error(mock_fetch):
    response = client.get("/forecast")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["message"] == "Weather data unavailable. External weather API did not respond."

@patch("weatherforecastlite.main.get_moon_illumination", side_effect=Exception("Moon API error"))
@patch("weatherforecastlite.main.fetch_weather_data")
def test_forecast_moon_api_error(mock_fetch, mock_moon):
    mock_fetch.return_value = MOCK_WEATHER_RESPONSE
    response = client.get("/forecast")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["message"] == "Night data unavailable. External moon phase API did not respond or data parsing failed."