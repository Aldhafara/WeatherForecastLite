# WeatherForecastLite

![Build Status](https://github.com/Aldhafara/WeatherForecastLite/actions/workflows/python-tests.yml/badge.svg)

Minimalist service for fetching nighttime cloud cover and temperature forecasts. Created as a lightweight helper for
[AstroSpotFinder](https://github.com/Aldhafara/AstroSpotFinder) - just the essentials for planning stargazing sessions.

## Table of Contents

- [Features](#features)
- [How to run](#how-to-run)
- [Docker](#docker)
- [API - Request Parameters](#api-request-parameters)
- [API Response Format](#api-response-format)
- [Caching](#caching)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Example Usage](#example-usage)
- [How to test](#how-to-test)
- [License](#license)

## Features

- Fetches cloud cover (%) and temperature for nighttime hours
- Fast, simple API
- Easy to extend - no feature bloat
- Due to occasional SSL certificate issues with the FarmSense API, a smart fallback mechanism was added.
- Requests try HTTPS by default, but on SSL errors the system automatically switches to HTTP for a 10-minute cache duration.
- This improves reliability and reduces potential downtime caused by external SSL problems.

## How to run

1. Clone the repo:

```bash
git clone https://github.com/Aldhafara/WeatherForecastLite.git
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

### Windows:

```powershell
venv\Scripts\activate
```

### Git Bash/Mac/Linux:

```bash
source venv/Scripts/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the script:

```bash
python src/weatherforecastlite/main.py
```

## Docker

1. Build the image:

```bash
docker build -t weatherforecastlite .
```

2. Run the container:

```bash
docker run -p 8000:8000 weatherforecastlite
```

To run with live code reload (dev only), use:

```bash
docker run -p 8000:8000 -v $(pwd)/src:/app/src weatherforecastlite
```

## API Request Parameters

| Parameter | Type    | Description                                                                                       | Default            |
|-----------|---------|---------------------------------------------------------------------------------------------------|--------------------|
| latitude  | float   | Latitude for forecast location                                                                    | 52.232222 (Warsaw) |
| longitude | float   | Longitude for forecast location                                                                   | 21.008333 (Warsaw) |
| timezone  | string  | Timezone (IANA tz database name, e.g. Europe/Warsaw, UTC, America/New_York). See [full list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) | Europe/Warsaw      |
| moon_info | boolean | Include moon illumination data in the forecast. Optional; defaults to false.                      | False              |

- **All parameters are optional.** If not provided, Warsaw and Europe/Warsaw timezone are used.

**Example requests:**

```
GET /forecast
GET /forecast?latitude=50.06143&longitude=19.93658&timezone=Europe/Krakow
GET /forecast?latitude=50.06143&longitude=19.93658&timezone=Europe/Krakow&moon_info=true
```

## API Response Format

```json
{
 "latitude": 52.232222,
 "longitude": 21.008333,
 "generationtime_ms": 0.09,
 "utc_offset_seconds": 7200,
 "timezone": "Europe/Warsaw",
 "timezone_abbreviation": "GMT+2",
 "elevation": 113,
 "hourly_units": {
  "time": "iso8601",
  "cloudcover": "%",
  "temperature_2m": "°C",
  "visibility": "m",
  "windspeed_10m": "m/s",
  "windgusts_10m": "m/s"
 },
 "data": [
  {
   "period": "2025-07-11/2025-07-12",
   "moon_illumination":0.41,
   "hours": [
    {
     "timestamp": 1752267600,
     "hour": "21:00",
     "temperature": 14.9,
     "cloudcover": 3,
     "visibility": 16720.0,
     "windspeed": 4.7,
     "windgust": 8.9
    }
    // other hours...
   ]
  }
  // other periods...
 ]
}
```

**Description of key fields:**

- `latitude`, `longitude` - geographic coordinates of the forecast location (decimal degrees)

- `generationtime_ms` - time taken to generate the API response, in milliseconds

- `timezone`, `timezone_abbreviation`, `utc_offset_seconds` - timezone information for the forecast:

  -  `timezone`: full timezone name (e.g., `Europe/Warsaw`)

  -  `timezone_abbreviation`: abbreviated timezone (e.g., `GMT+2`)

  -  `utc_offset_seconds`: offset from UTC in seconds

- `elevation` - elevation of the forecast location above sea level (meters)

- `hourly_units` - dictionary specifying the units for each weather parameter (e.g., `"temperature_2m": "°C"`,
 `"windspeed_10m": "m/s"`)

- `data` - an array of objects, each representing a single night (from sunset to sunrise)

  - `period` - date range for the night, formatted as `"YYYY-MM-DD/YYYY-MM-DD"` (e.g., `"2025-07-11/2025-07-12"`)

  - `moon_illumination` - fraction of the Moon’s disk illuminated (value between 0 and 1, where 0 means new moon and 1 means full moon), value is calculated for 01:00 each night period

  - `hours` - array of hourly forecast entries for the night. Each entry contains:

    - `timestamp` - timestamp (Unix)

    - `hour` - hour as HH:MM (24-hour format)

    - `temperature` - air temperature at 2 meters above ground (unit: °C)

    - `cloudcover` - cloud cover[%]

    - `visibility` - widoczność [m]

    - `windspeed` - wind speed at 10 meters above ground (unit: m/s)

    - `windgust` - wind gust speed at 10 meters above ground (unit: m/s)

## Caching

- Weather data: cached for 1 hour per location.
- Moon illumination: cached for 24 hours per night period.
- First request may be slower (data fetched from external APIs), subsequent requests are instant (served from cache).

## Rate Limiting

To protect the API and external resources, requests to `/forecast` are limited to 20 per minute per IP (HTTP 429 on limit exceeded).

## Error Handling

- Returns `503` if external weather or moon phase API is unavailable.
- Returns `422` for invalid input parameters (latitude, longitude).
- All errors are returned as JSON with a clear message, for example:
```json
{
  "detail": {
    "message": "Weather data unavailable. External weather API did not respond.",
    "error": "ConnectionError: ..."
  }
}
```
## Example Usage

```bash
curl "http://localhost:8000/forecast?latitude=50.06143&longitude=19.93658&timezone=Europe/Warsaw"
```

## How to test

1. Install dev dependencies:

```
pip install -r requirements.txt
```

2. Run tests:

```
pytest
```

## License

MIT