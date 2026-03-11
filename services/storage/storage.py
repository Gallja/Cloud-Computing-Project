import os, json
from confluent_kafka import Consumer
from pymongo import MongoClient

BOOT = os.getenv("KAFKA_BOOTSTRAP", "kafka-1:9093")
TOPIC = os.getenv("TOPIC_TELEMETRY", "weather.telemetry")
GROUP_ID = os.getenv("GROUP_ID", "storage-group")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")

def kafka_ssl_base():
    return {
        "bootstrap.servers": BOOT,
        "security.protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "SSL"),
        "ssl.ca.location": os.getenv("KAFKA_SSL_CA_LOCATION", "/app/security/ca.crt"),
        "ssl.certificate.location": os.getenv("KAFKA_SSL_CERTIFICATE_LOCATION", "/app/security/client-creds/kafka.client.certificate.pem"),
        "ssl.key.location": os.getenv("KAFKA_SSL_KEY_LOCATION", "/app/security/client-creds/kafka.client.key"),
    }

def start_storage():
    print("Starting storage service...", flush=True)

    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["weather_archive"]
    collection = db["telemetry_history_data"]

    cons = Consumer({
        **kafka_ssl_base(),
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    })

    cons.subscribe([TOPIC])

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

                collection.insert_one(data)
                cons.commit(asynchronous=False)

                print(f"Saved weather data for {data.get('city')}", flush=True)
            except Exception as e:
                print(f"Error processing message: {e}")
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cons.close()
        mongo_client.close()

if __name__ == "__main__":
    start_storage()