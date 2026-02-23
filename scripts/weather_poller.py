import requests
import time

API_PRODUCER_URL = "http://127.0.0.1:8000/event"

CITIES = {
    "Milano": {"lat": 45.4642, "lon": 9.1900},
    "Torino": {"lat": 45.0703, "lon": 7.6869},
    "Verona": {"lat": 45.4384, "lon": 10.9916},
    "Firenze": {"lat": 43.7696, "lon": 11.2558},
    "Roma": {"lat": 41.9028, "lon": 12.4964},
    "Napoli": {"lat": 40.8518, "lon": 14.2681}
}

def fetch_and_send_weather():
    print("Raccolta dati meteo...")
    
    while True:
        for city_name, coords in CITIES.items():
            meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
            
            try:
                response = requests.get(meteo_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_weather", {})
                    
                    payload = {
                        "city": city_name,
                        "temperature": current.get("temperature"),
                        "windspeed": current.get("windspeed"),
                        "is_day": current.get("is_day"),
                        "weathercode": current.get("weathercode")
                    }
                    
                    post_response = requests.post(API_PRODUCER_URL, json=payload, timeout=4)
                    print(f"Inviato dato per {city_name}: {payload['temperature']}°C - Status API: {post_response.status_code}")
                    
            except Exception as e:
                print(f"Errore durante l'elaborazione di {city_name}: {e}")
            
            time.sleep(2)
            
        print("Ciclo completato.")
        time.sleep(15)

if __name__ == "__main__":
    fetch_and_send_weather()