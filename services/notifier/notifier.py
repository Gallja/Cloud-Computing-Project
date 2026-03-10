import os, json, sys, re, time
from confluent_kafka import Consumer, Producer

BOOT = os.getenv("KAFKA_BOOTSTRAP", "kafka-1:9093")
TOPIC_IN = os.getenv("TOPIC_TELEMETRY", "weather.telemetry")
TOPIC_OUT = os.getenv("TOPIC_NOTIFICATIONS", "weather.alerts")
GROUP_ID = os.getenv("GROUP_ID", "notifier-group")

def kafka_ssl_base():
    return {
        "bootstrap.servers": BOOT,
        "security.protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL"),
        "ssl.ca.location": os.getenv("KAFKA_SSL_CA_LOCATION", "/app/security/ca.crt"),
        "ssl.certificate.location": os.getenv("KAFKA_SSL_CERTIFICATE_LOCATION", "/app/security/client.pem"),
        "ssl.key.location": os.getenv("KAFKA_SSL_KEY_LOCATION", "/app/security/client.key"),
    }

cons = Consumer({
    **kafka_ssl_base(),
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})

prod = Producer({
    **kafka_ssl_base(),
    "acks": "all",
    "enable.idempotence": True,
    "max.in.flight.requests.per.connection": 1,
    "retries": 5,
    "request.timeout.ms": 30000
})

cons.subscribe([TOPIC_IN])

try:
    while True:
        msg = cons.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue
        
        try:
            data = json.loads(msg.value().decode("utf-8"))
            city = data.get("city", "Unknown")
            temperature = data.get("temperature", 0.0)
            precipitation = data.get("precipitation", 0.0)
            
            alert = None
            if temperature > 30.0:
                alert = f"High temperature alert for {city}: {temperature}°C"
            elif temperature < 0.0:
                alert = f"Low temperature alert for {city}: {temperature}°C"
            elif precipitation > 40.0:
                alert = f"Heavy rain alert for {city}: {precipitation}mm"
            
            if alert:
                prod.produce(TOPIC_OUT, json.dumps({"city": city, "alert": alert}).encode("utf-8"))
                prod.poll(1.0)
                print(f"Sent alert: {alert}")
            
            cons.commit(asynchronous=False)
        except Exception as e:
            print(f"Error processing message: {e}")
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    try:
        prod.flush(5)
    except:
        pass
    cons.close()