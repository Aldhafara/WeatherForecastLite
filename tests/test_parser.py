from unittest.mock import patch
from weatherforecastlite.main import parse_night_data, get_period

from datetime import datetime

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_minimal(mock_logger):
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "2025-07-11T22:00"],
            "cloudcover": [10, 20],
            "temperature_2m": [15.0, 14.5]
        }
    }
    result = parse_night_data(sample)
    assert result == []
    mock_logger.warning.assert_called_with("Data unavailable in external API: 'visibility'")

def test_get_period():
    dt1 = datetime.fromisoformat("2025-07-11T22:00:00")
    dt2 = datetime.fromisoformat("2025-07-12T02:00:00")
    dt3 = datetime.fromisoformat("2025-07-11T20:00:00")
    assert get_period(dt1) == "2025-07-11/2025-07-12"
    assert get_period(dt2) == "2025-07-11/2025-07-12"
    assert get_period(dt3) == "2025-07-10/2025-07-11"

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_full(mock_logger):
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "2025-07-11T22:00", "2025-07-11T23:00", "2025-07-12T00:00"],
            "cloudcover": [10, 20, 30, 40],
            "temperature_2m": [15.0, 14.5, 14.0, 13.5],
            "visibility":[16720.0, 15670.0, 14560.0, 14000.0],
            "windspeed_10m":[4.7, 5.1, 4.2, 3.4],
            "windgusts_10m":[8.9, 9.2, 8.0, 7.5]
        }
    }
    result = parse_night_data(sample)
    assert len(result) == 1
    assert result[0]["period"] == "2025-07-11/2025-07-12"
    assert len(result[0]["hours"]) == 4
    assert result[0]["hours"][0]["hour"] == "21:00"
    assert "timestamp" in result[0]["hours"][0]

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_missing_keys(mock_logger):
    sample = {"hourly": {"time": ["2025-07-11T21:00"]}}
    result = parse_night_data(sample)
    assert result == []
    mock_logger.warning.assert_called()

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_bad_data(mock_logger):
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "bad-time"],
            "cloudcover": [10, 11],
            "temperature_2m": [15.0, 14.5],
            "visibility":[16720.0, 15670.0],
            "windspeed_10m":[4.7, 5.1],
            "windgusts_10m":[8.9, 9.2]
        }
    }
    result = parse_night_data(sample)
    assert len(result) == 1
    assert len(result[0]["hours"]) == 1
    assert mock_logger.error.call_count >= 1

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_data_error_message(mock_logger):
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "bad-time"],
            "cloudcover": [10, 11],
            "temperature_2m": [15.0, 14.5],
            "visibility":[16720.0, 15670.0],
            "windspeed_10m":[4.7, 5.1],
            "windgusts_10m":[8.9, 9.2]
        }
    }
    result = parse_night_data(sample)
    assert len(result) == 1
    error_logs = [call[0][0] for call in mock_logger.error.call_args_list]
    assert any("Data error for hour bad-time:" in msg for msg in error_logs)

@patch('weatherforecastlite.main.logger')
def test_parse_night_data_empty_lists(mock_logger):
    sample = {
        "hourly": {
            "time": [],
            "cloudcover": [],
            "temperature_2m": [],
            "visibility": [],
            "windspeed_10m": [],
            "windgusts_10m": []
        }
    }
    result = parse_night_data(sample)
    assert result == []
