import requests

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.23&longitude=21.01&hourly=cloudcover,temperature_2m&timezone=Europe/Warsaw"
    response = requests.get(url)
    data = response.json()
    print(data)

if __name__ == "__main__":
    fetch_weather()
