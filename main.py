from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY")

class WeatherInput(BaseModel):
    city: str

@app.get("/")
def home():
    return {"message": "KrishiMitra Weather API is running"}

@app.post("/get-weather")
def get_weather(data: WeatherInput):
    # Current weather
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={data.city}&appid={OPENWEATHER_KEY}&units=metric"
    current_resp = requests.get(current_url).json()

    if current_resp.get("cod") != 200:
        return {"error": "City not found or API error", "details": current_resp.get("message", "")}

    current = {
        "city": current_resp["name"],
        "temperature": current_resp["main"]["temp"],
        "humidity": current_resp["main"]["humidity"],
        "condition": current_resp["weather"][0]["main"],
        "description": current_resp["weather"][0]["description"],
        "rain_chance": current_resp.get("rain", {}).get("1h", 0)
    }

    # 7-day forecast (using 5-day/3-hour forecast API, grouped by day)
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={data.city}&appid={OPENWEATHER_KEY}&units=metric"
    forecast_resp = requests.get(forecast_url).json()

    daily_forecast = []
    seen_dates = set()
    for entry in forecast_resp.get("list", []):
        date = entry["dt_txt"].split(" ")[0]
        if date not in seen_dates and "12:00:00" in entry["dt_txt"]:
            seen_dates.add(date)
            daily_forecast.append({
                "date": date,
                "temp_max": entry["main"]["temp_max"],
                "temp_min": entry["main"]["temp_min"],
                "condition": entry["weather"][0]["main"],
                "rain_chance": int(entry.get("pop", 0) * 100)
            })

    return {
        "current": current,
        "forecast": daily_forecast
    }
