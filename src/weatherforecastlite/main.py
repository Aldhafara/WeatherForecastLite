from datetime import datetime, timedelta
from typing import List, Dict

import requests
from fastapi import FastAPI

app = FastAPI()

def get_night_hours():
    return list(range(21, 24)) + list(range(0, 7))

def fetch_weather_data(lat, lon, timezone):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=cloudcover,temperature_2m"
        f"&timezone={timezone}"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def add_unix_timestamp(hour_str, date_str):
    dt_str = f"{date_str}T{hour_str}:00"
    dt = datetime.fromisoformat(dt_str)
    return int(dt.timestamp())

def get_period(dt):
    if dt.hour >= 21:
        start = dt.date()
        end = (dt + timedelta(days=1)).date()
    else:
        start = (dt - timedelta(days=1)).date()
        end = dt.date()
    return f"{start}/{end}"

def parse_night_data(raw_data) -> List[Dict]:
    hours = raw_data["hourly"]["time"]
    clouds = raw_data["hourly"]["cloudcover"]
    temps = raw_data["hourly"]["temperature_2m"]
    night_hours = get_night_hours()
    grouped = {}
    for i, hour_str in enumerate(hours):
        dt = datetime.fromisoformat(hour_str)
        if dt.hour in night_hours:
            period = get_period(dt)
            grouped.setdefault(period, []).append({
                "timestamp":add_unix_timestamp(dt.strftime("%H:%M"), dt.date()),
                "hour": dt.strftime("%H:%M"),
                "temperature": temps[i],
                "cloudcover": clouds[i]
            })
    return [
        {"period": period, "hours": hours}
        for period, hours in grouped.items()
    ]

@app.get("/forecast")
def forecast(
    latitude: float = 52.232222,
    longitude: float = 21.008333,
    timezone: str = "Europe/Warsaw"
):
    raw = fetch_weather_data(latitude, longitude, timezone)
    night_data = parse_night_data(raw)
    result = {
        "latitude": latitude,
        "longitude": longitude,
        "generationtime_ms": raw.get("generationtime_ms"),
        "utc_offset_seconds": raw.get("utc_offset_seconds"),
        "timezone": raw.get("timezone"),
        "timezone_abbreviation": raw.get("timezone_abbreviation"),
        "elevation": raw.get("elevation"),
        "hourly_units": raw.get("hourly_units"),
        "data": night_data
    }
    return result
