import requests
import time

API_PRODUCER_URL = "http://127.0.0.1:8000/weather"

CITIES = {
    "Milan": {"lat": 45.46427, "lon": 9.18951},
    "Turin": {"lat": 45.07049, "lon": 7.68682},
    "Verona": {"lat": 45.4299, "lon": 10.9844},
    "Florence": {"lat": 43.77925, "lon": 11.24626},
    "Rome": {"lat": 41.89193, "lon": 12.51133},
    "Naples": {"lat": 40.85631, "lon": 14.24641}
}

def fetch_and_send_weather():
    print("Weather data polling...")
    
    current_vars = "temperature_2m,wind_speed_10m,is_day,weather_code,precipitation,rain,cloud_cover,surface_pressure"

    while True:
        for city_name, coords in CITIES.items():
            meteo_url = (f"https://api.open-meteo.com/v1/forecast?"
                         f"latitude={coords['lat']}&longitude={coords['lon']}"
                         f"&current={current_vars}"
                         f"&daily=sunshine_duration"
                         f"&timezone=auto")
            
            try:
                response = requests.get(meteo_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()

                    current = data.get("current", {})
                    daily = data.get("daily", {})

                    sunshine_today = 0
                    if "sunshine_duration" in daily and len(daily["sunshine_duration"]) > 0:
                        sunshine_today = daily["sunshine_duration"][0]
                    
                    payload = {
                        "city": city_name,
                        "temperature": current.get("temperature_2m"),
                        "windspeed": current.get("wind_speed_10m"),
                        "is_day": current.get("is_day"),
                        "weathercode": current.get("weather_code"),
                        "precipitation": current.get("precipitation"),
                        "rain": current.get("rain"),
                        "cloud_cover": current.get("cloud_cover"),
                        "surface_pressure": current.get("surface_pressure"),
                        "sunshine_duration": sunshine_today
                    }
                    
                    post_response = requests.post(API_PRODUCER_URL, json=payload, timeout=4)
                    print(f"Data sended for {city_name} - Status API: {post_response.status_code}")
                    # print(f"Data extracted for {city_name}: {payload}")
                    
            except Exception as e:
                print(f"Error during elaboration - {city_name}: {e}")
            
            time.sleep(2)
            
        print("Cycle completed.")
        time.sleep(2)

if __name__ == "__main__":
    fetch_and_send_weather()