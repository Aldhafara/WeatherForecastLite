import time
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException, Request
from typing import List, Dict
from .logging_config import logger
from .utils import get_night_hours, add_unix_timestamp, get_period
from .external import fetch_weather_data, batch_get_moon_illumination, get_moon_illumination, log_cache, weather_cache, moon_phase_cache
from .rate_limit_config import limiter, rate_limit_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(*rate_limit_handler)

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} took {duration:.3f}s")
    return response

def parse_night_data(raw_data) -> List[Dict]:
    try:
        hours = raw_data["hourly"]["time"]
        clouds = raw_data["hourly"]["cloudcover"]
        temps = raw_data["hourly"]["temperature_2m"]
        visibilities = raw_data["hourly"]["visibility"]
        windspeeds = raw_data["hourly"]["windspeed_10m"]
        windgusts = raw_data["hourly"]["windgusts_10m"]
    except KeyError as e:
        logger.warning(f"Data unavailable in external API: {e}")
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
            logger.error(f"Data error for hour {hour_str}: {e}")
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
    moon_timestamps = []
    periods = []
    for period, hours in grouped.items():
        moon_hour = next((h for h in hours if h["hour"] == "01:00"), hours[0])
        moon_timestamps.append(moon_hour["timestamp"])
        periods.append((period, hours))
    moon_illuminations = batch_get_moon_illumination(moon_timestamps)
    for (period, hours), moon_illumination in zip(periods, moon_illuminations):
        result.append({
            "period": period,
            "moon_illumination": moon_illumination,
            "hours": hours
        })
    return result

@app.get("/forecast")
@limiter.limit("20/minute")
def forecast(
    request: Request,
    latitude: float = Query(52.232222, ge=-90, le=90, description="Latitude (-90 to 90)"),
    longitude: float = Query(21.008333, ge=-180, le=180, description="Longitude (-180 to 180)"),
    timezone: str = Query("Europe/Warsaw", description="Timezone, e.g. Europe/Warsaw")
):
    try:
        try:
            raw = fetch_weather_data(latitude, longitude, timezone)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
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
            logger.error(f"Error fetching moon phase or parsing night data: {e}")
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
        logger.error(f"Internal server error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Internal server error.",
                "error": str(e)
            }
        )
