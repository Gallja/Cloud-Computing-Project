import requests
import time

API_PRODUCER_URL = "http://127.0.0.1:8000/weather"

CITIES = {
    "Milano": {"lat": 45.46427, "lon": 9.18951},
    "Torino": {"lat": 45.07049, "lon": 7.68682},
    "Verona": {"lat": 45.4299, "lon": 10.9844},
    "Firenze": {"lat": 43.77925, "lon": 11.24626},
    "Roma": {"lat": 41.89193, "lon": 12.51133},
    "Napoli": {"lat": 40.85631, "lon": 14.24641}
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
                    print(f"Inviato dato per {city_name} - Status API: {post_response.status_code}")
                    # print(f"Dato estratto per {city_name}: {payload}")
                    
            except Exception as e:
                print(f"Errore durante l'elaborazione di {city_name}: {e}")
            
            time.sleep(2)
            
        print("Ciclo completato.")
        time.sleep(2)

if __name__ == "__main__":
    fetch_and_send_weather()