from weatherforecastlite.main import parse_night_data, get_period

from datetime import datetime

def test_parse_night_data_basic():
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "2025-07-11T22:00"],
            "cloudcover": [10, 20],
            "temperature_2m": [15.0, 14.5]
        }
    }
    result = parse_night_data(sample)
    assert len(result) > 0
    assert result[0]["hours"][0]["hour"] == "21:00"
    assert "timestamp" in result[0]["hours"][0]

def test_get_period():
    dt1 = datetime.fromisoformat("2025-07-11T22:00:00")
    dt2 = datetime.fromisoformat("2025-07-12T02:00:00")
    dt3 = datetime.fromisoformat("2025-07-11T20:00:00")
    assert get_period(dt1) == "2025-07-11/2025-07-12"
    assert get_period(dt2) == "2025-07-11/2025-07-12"
    assert get_period(dt3) == "2025-07-10/2025-07-11"

def test_parse_night_data_basic():
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "2025-07-11T22:00", "2025-07-11T23:00", "2025-07-12T00:00"],
            "cloudcover": [10, 20, 30, 40],
            "temperature_2m": [15.0, 14.5, 14.0, 13.5]
        }
    }
    result = parse_night_data(sample)
    assert len(result) == 1
    assert result[0]["period"] == "2025-07-11/2025-07-12"
    assert len(result[0]["hours"]) == 4
    assert result[0]["hours"][0]["hour"] == "21:00"
    assert "timestamp" in result[0]["hours"][0]

def test_parse_night_data_missing_keys():
    sample = {"hourly": {"time": ["2025-07-11T21:00"]}}
    result = parse_night_data(sample)
    assert result == []

def test_parse_night_data_bad_data():
    sample = {
        "hourly": {
            "time": ["2025-07-11T21:00", "bad-time"],
            "cloudcover": [10],
            "temperature_2m": [15.0]
        }
    }
    result = parse_night_data(sample)
    assert len(result) == 1
    assert len(result[0]["hours"]) == 1

