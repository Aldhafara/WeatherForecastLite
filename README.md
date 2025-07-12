# WeatherForecastLite

![Build Status](https://github.com/Aldhafara/WeatherForecastLite/actions/workflows/python-tests.yml/badge.svg)

Minimalist service for fetching nighttime cloud cover and temperature forecasts. Created as a lightweight helper for
AstroSpotFinder - just the essentials for planning stargazing sessions.

## Table of Contents

- [Features](#features)
- [How to run](#how-to-run)
- [Project status](#project-status)
- [API - Request Parameters](#api-request-parameters)
- [API Response Format](#api-response-format)
- [Example Usage](#example-usage)
- [How to test](#how-to-test)
- [License](#license)

## Features

- Fetches cloud cover (%) and temperature for nighttime hours
- Fast, simple API
- Easy to extend - no feature bloat

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

## Project status

- [x] Initial skeleton

- [x] Basic weather fetcher

- [x] Nighttime data parser

- [x] Simple API (Flask/FastAPI)

- [x] Tests

## API Request Parameters

| Parameter | Type  | Description                    | Default      |
|-----------|--------|---------------------------------------------------|--------------------|
| latitude | float | Latitude for forecast location          | 52.232222 (Warsaw) |
| longitude | float | Longitude for forecast location          | 21.008333 (Warsaw) |
| timezone | string | Timezone (e.g. Europe/Warsaw, UTC, Europe/London) | Europe/Warsaw   |

- **All parameters are optional.** If not provided, Warsaw and Europe/Warsaw timezone are used.

**Example requests:**

```
GET /forecast
GET /forecast?latitude=50.06143&longitude=19.93658&timezone=Europe/Krakow
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

---  `timezone`: full timezone name (e.g., `Europe/Warsaw`)

---  `timezone_abbreviation`: abbreviated timezone (e.g., `GMT+2`)

---  `utc_offset_seconds`: offset from UTC in seconds

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

## Example Usage

```bash
curl "http://localhost:8000/forecast?latitude=50.06143&longitude=19.93658&timezone=Europe/Krakow"
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