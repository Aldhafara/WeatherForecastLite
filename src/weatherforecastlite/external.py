import requests
import time
from fastapi import Query
from cachetools import TTLCache, cached
from .logging_config import logger
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

weather_cache = TTLCache(maxsize=128, ttl=3600)  # 1h
moon_phase_cache = TTLCache(maxsize=128, ttl=86400)  # 24h
moon_phase_protocol_cache = TTLCache(maxsize=1, ttl=600)  # 10 min

def log_cache(cache, name="cache"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = args if args else tuple(kwargs.items())
            if key in cache:
                logger.info(f"Cache HIT ({name}): {key}")
            else:
                logger.info(f"Cache MISS ({name}): {key}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_moon_api_protocol():
    return moon_phase_protocol_cache.get("proto", "https")

def set_moon_api_protocol(proto):
    moon_phase_protocol_cache["proto"] = proto

def fetch_moon_phase_data(timestamp, protocol):
    url = f"{protocol}://api.farmsense.net/v1/moonphases/?d={timestamp}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return data

@log_cache(moon_phase_cache, name="moon_illumination")
@cached(moon_phase_cache)
def get_moon_illumination(
    timestamp: int = Query(..., description="Unix timestamp (required)")
):
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        logger.error(f"Invalid timestamp type: {timestamp}")
        raise ValueError("Timestamp must be an integer.")
    if ts < 0:
        logger.error(f"Negative timestamp: {timestamp}")
        raise ValueError("Timestamp must be a positive integer.")
    now = int(time.time())
    if ts > now + 10 * 365 * 24 * 3600:
        logger.warning(f"Timestamp out of reasonable range: {timestamp}")
        raise ValueError(f"Timestamp out of reasonable range: {timestamp}")

    protocol = get_moon_api_protocol()
    try:
        data = fetch_moon_phase_data(timestamp, protocol)
        return data[0]["Illumination"]
    except requests.exceptions.SSLError as ssl_exc:
        if protocol == "https":
            logger.warning("Moonphases API SSL error – switching to HTTP")
            set_moon_api_protocol("http")
            try:
                data = fetch_moon_phase_data(timestamp, "http")
                return data[0]["Illumination"]
            except Exception as e2:
                logger.error(f"Moonphases API HTTP fetch fail with SSL: {e2}")
                raise
        logger.error(f"Moonphases API SSL error with HTTP – something is seriously wrong: {ssl_exc}")
        raise
    except Exception as e:
        logger.error(f"Error fetching moon illumination: {e}")
        raise

@log_cache(weather_cache, name="weather_cache")
@cached(weather_cache)
def fetch_weather_data(lat, lon, timezone):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=cloudcover,temperature_2m,visibility,windspeed_10m,windgusts_10m"
        f"&windspeed_unit=ms"
        f"&timezone={timezone}"
    )
    start = time.time()
    response = requests.get(url)
    duration = time.time() - start
    logger.info(f"Open-Meteo API call took {duration:.3f}s")
    response.raise_for_status()
    return response.json()

def batch_get_moon_illumination(timestamps):
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(get_moon_illumination, timestamps))
    return results
