import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from weatherforecastlite.main import app
from weatherforecastlite.external import get_moon_illumination

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

client = TestClient(app, raise_server_exceptions=False)

@patch("weatherforecastlite.external.get_moon_illumination")
@patch("weatherforecastlite.main.fetch_weather_data")
def test_forecast_endpoint(mock_fetch, mock_moon):
    mock_response = MOCK_WEATHER_RESPONSE
    mock_fetch.return_value = mock_response
    mock_moon.return_value = 0.5

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

@patch("weatherforecastlite.external.get_moon_illumination", side_effect=Exception("Moon API error"))
@patch("weatherforecastlite.main.fetch_weather_data")
def test_forecast_moon_api_error(mock_fetch, mock_moon):
    mock_fetch.return_value = MOCK_WEATHER_RESPONSE
    response = client.get("/forecast?moon_info=true")
    assert response.status_code == 503
    data = response.json()
    assert data["detail"]["message"] == "Night data unavailable. External moon phase API did not respond or data parsing failed."

def test_forecast_latitude_out_of_range():
    response = client.get("/forecast?latitude=100.0&longitude=19.0")
    assert response.status_code == 422
    data = response.json()
    error = data["detail"][0]
    assert "Input should be less than or equal to 90" in error["msg"]

def test_forecast_longitude_out_of_range():
    response = client.get("/forecast?latitude=50.0&longitude=200.0")
    assert response.status_code == 422
    data = response.json()
    error = data["detail"][0]
    assert "Input should be less than or equal to 180" in error["msg"]

def test_forecast_invalid_latitude_type():
    response = client.get("/forecast?latitude=foo&longitude=19.0")
    assert response.status_code == 422
    data = response.json()
    error = data["detail"][0]
    assert "Input should be a valid number, unable to parse string as a number" in error["msg"]

def test_get_moon_illumination_negative_timestamp():
    with pytest.raises(ValueError, match="Timestamp must be a positive integer"):
        get_moon_illumination(-123)

def test_get_moon_illumination_timestamp_from_far_future():
    with pytest.raises(ValueError, match=r"Timestamp out of reasonable range.*9999"):
        get_moon_illumination(9999999999999999)
