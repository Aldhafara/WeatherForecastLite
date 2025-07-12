import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI()

def get_night_hours():
    return list(range(21, 24)) + list(range(0, 7))

def get_moon_illumination(timestamp):
    url = f"https://api.farmsense.net/v1/moonphases/?d={timestamp}"
    resp = requests.get(url)
    data = resp.json()
    return data[0]["Illumination"]

def fetch_weather_data(lat, lon, timezone):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=cloudcover,temperature_2m,visibility,windspeed_10m,windgusts_10m"
        f"&windspeed_unit=ms"
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
    try:
        hours = raw_data["hourly"]["time"]
        clouds = raw_data["hourly"]["cloudcover"]
        temps = raw_data["hourly"]["temperature_2m"]
        visibilities = raw_data["hourly"]["visibility"]
        windspeeds = raw_data["hourly"]["windspeed_10m"]
        windgusts = raw_data["hourly"]["windgusts_10m"]
    except KeyError as e:
        print(f"Data unavailable in external API: {e}")
        return []
    night_hours = get_night_hours()
    grouped = {}
    for i, hour_str in enumerate(hours):
        try:
            dt = datetime.fromisoformat(hour_str)
            temp = temps[i]
            cloud = clouds[i]
            visibility = visibilities[i]
            windspeed = windspeeds[i]
            windgust = windgusts[i]
        except (IndexError, ValueError) as e:
            print(f"Data error for hour {hour_str}: {e}")
            continue

        if dt.hour in night_hours:
            period = get_period(dt)
            grouped.setdefault(period, []).append({
                "timestamp": add_unix_timestamp(dt.strftime("%H:%M"), dt.date()),
                "hour": dt.strftime("%H:%M"),
                "temperature": temp,
                "cloudcover": cloud,
                "visibility": visibility,
                "windspeed": windspeed,
                "windgust": windgust,
            })
    result = []
    for period, hours in grouped.items():
        moon_hour = next((h for h in hours if h["hour"] == "01:00"), hours[0])
        moon_illumination = get_moon_illumination(moon_hour["timestamp"])
        result.append({
            "period": period,
            "moon_illumination": moon_illumination,
            "hours": hours
        })
    return result

@app.get("/forecast")
def forecast(
    latitude: float = 52.232222,
    longitude: float = 21.008333,
    timezone: str = "Europe/Warsaw"
):
    try:
        try:
            raw = fetch_weather_data(latitude, longitude, timezone)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Weather data unavailable. External weather API did not respond.",
                    "error": str(e)
                }
            )

        try:
            night_data = parse_night_data(raw)
        except Exception as e:
            print(f"Error fetching moon phase or parsing night data: {e}")
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Night data unavailable. External moon phase API did not respond or data parsing failed.",
                    "error": str(e)
                }
            )

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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Internal server error.",
                "error": str(e)
            }
        )
