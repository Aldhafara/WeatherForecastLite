from datetime import datetime, timedelta

def get_night_hours():
    return list(range(21, 24)) + list(range(0, 7))

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