# WeatherForecastLite

Minimalist service for fetching nighttime cloud cover and temperature forecasts. Created as a lightweight helper for AstroSpotFinder – just the essentials for planning stargazing sessions.

## Features
 - Fetches cloud cover (%) and temperature for nighttime hours
 - Fast, simple API (in progress)
 - Easy to extend – no feature bloat

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
 - [ ]  Nighttime data parser
 - [ ] Simple API (Flask/FastAPI)
 - [ ] Tests
 
 ## License
 MIT