import os, json, threading, queue, time, random
from urllib import response
import requests
from flask import Flask, Response, render_template, jsonify
from confluent_kafka import Consumer

BOOT = os.getenv("KAFKA_BOOTSTRAP", "kafka-1:9093")
TOPIC = os.getenv("TOPIC_NOTIFICATIONS", "weather.telemetry")
GROUP = os.getenv("DASHBOARD_GROUP_ID", f"dashboard-ui-{int(time.time())}")
API_BASE = os.getenv("API_BASE", "http://api-producer:8000")

webapp = Flask(__name__, static_folder="static", template_folder="template")

state_lock = threading.Lock()
state = {}
output_queue = queue.Queue()
started = False

def kafka_ssl_base():
    return {
        "bootstrap.servers": BOOT,
        "security.protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL"),
        "ssl.ca.location": os.getenv("KAFKA_SSL_CA_LOCATION", "/app/security/ca.crt"),
        "ssl.certificate.location": os.getenv("KAFKA_SSL_CERTIFICATE_LOCATION", "/app/security/client.pem"),
        "ssl.key.location": os.getenv("KAFKA_SSL_KEY_LOCATION", "/app/security/client.key"),
        "group.id": GROUP,
        "auto.offset.reset": "latest"
    }

def kafa_background_loop():
    consumer = Consumer(kafka_ssl_base())
    consumer.subscribe([TOPIC])
    
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Errore Kafka: {msg.error()}")
            continue
        
        try:
            data = json.loads(msg.value().decode("utf-8"))
            city = data.get("city", "Unknown")
            temperature = data.get("temperature", "N/A")
            windspeed = data.get("windspeed", "N/A")
            is_day = data.get("is_day", 0)
            weathercode = data.get("weathercode", -1)
            
            with state_lock:
                state[city] = {
                    "temperature": temperature,
                    "windspeed": windspeed,
                    "is_day": is_day,
                    "weathercode": weathercode
                }
            
            output_queue.put(json.dumps({"city": city, "temperature": temperature, "windspeed": windspeed, "is_day": is_day, "weathercode": weathercode}))
        
        except Exception as e:
            print(f"Errore di lettura: {e}")

def stress_test(n=200, delay=0.1):
    CITIES = ["Milano", "Torino", "Verona", "Firenze", "Roma", "Napoli"]

    for _ in range(n):
        city = random.choice(CITIES)
        payload = {
            "city": city,
            "temperature": round(random.uniform(-10, 35), 2),
            "windspeed": round(random.uniform(0, 20), 2),
            "is_day": random.choice([0, 1]),
            "weathercode": random.randint(0, 100)
        }
        try:
            response = requests.post(f"{API_BASE}/weather", json=payload, timeout=5)

            if response.status_code != 200:
                print(f"Errore API: {response.status_code} - Motivo: {response.text}")
        except Exception as e:
            print(f"Errore durante lo stress test: {e}")
        time.sleep(delay)

def start_kafka_thread():
    global started
    if not started:
        threading.Thread(target=kafa_background_loop, daemon=True).start()
        started = True

@webapp.before_request
def before():
    start_kafka_thread()

@webapp.get("/healthz")
def health():
    return {"ok": True, "bootstrap": BOOT, "topic": TOPIC, "group": GROUP, "api": API_BASE}

@webapp.get("/stream")
def stream():
    def event_stream():
        while True:
            data = output_queue.get()
            yield f"data: {data}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

@webapp.get("/")
def index():
    return render_template("index.html")

@webapp.post("/admin/stress")
def admin_stress():
    threading.Thread(target=stress_test, daemon=True).start()
    return jsonify({"status": "Stress test avviato", "message": "Verranno inviati 200 dati casuali con un intervallo di 0.1 secondi"})

if __name__ == "__main__":
    webapp.run(host="0.0.0.0", port=8500, debug=True)