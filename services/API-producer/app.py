import os, json, uuid, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from confluent_kafka import Producer

# Topic Kafka:
BOOT = os.getenv("KAFKA_BOOTSTRAP", "kafka-1:9093")
TOPIC = os.getenv("TOPIC_EVENTS", "weather.telemetry")

app = FastAPI(title="Weather API Producer")

class WeatherData(BaseModel):
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: float = Field(default_factory=lambda: time.time())
    
    city: str
    temperature: float
    windspeed: float
    is_day: int
    weathercode: int
    precipitation: float
    rain: float
    cloud_cover: float
    surface_pressure: float
    sunshine_duration: float

def kafka_ssl_base():
    cfg = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP"),
        "security.protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL"),
        "ssl.ca.location": os.getenv("KAFKA_SSL_CA_LOCATION"),
        "ssl.certificate.location": os.getenv("KAFKA_SSL_CERTIFICATE_LOCATION"),
        "ssl.key.location": os.getenv("KAFKA_SSL_KEY_LOCATION"),
        "acks": "all",
        "enable.idempotence": True,
        "max.in.flight.requests.per.connection": 1,
        "retries": 2147483647,
        "message.timeout.ms": 120000,
        "request.timeout.ms": 40000
    }
    return cfg

producer = Producer(kafka_ssl_base())

@app.get("/healthz")
def health():
    return {"ok": True, "status": "Weather API Producer is running"}

@app.post("/weather")
def produce_weather(data: WeatherData):
    payload_str = data.model_dump_json()
    
    try:
        producer.produce(TOPIC, value=payload_str)
        producer.poll(0)
        
        return {
            "status": "ok", 
            "eventId": data.eventId, 
            "city": data.city, 
            "message": "Dato meteo inviato a Kafka con successo"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))