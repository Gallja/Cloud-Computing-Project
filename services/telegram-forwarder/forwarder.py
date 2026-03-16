import os, json 
import requests
from confluent_kafka import Consumer

BOOT = os.getenv('KAFKA_BOOTSTRAP', 'kafka-1:9093')
TOPIC = os.getenv('TOPIC_ALERTS', 'weather-alerts')
GROUP_ID = os.getenv('GROUP_ID', 'telegram-forwarder-group')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def kafka_ssl_base():
    return {
        'bootstrap.servers': BOOT,
        'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'SSL'),
        'ssl.ca.location': os.getenv('KAFKA_SSL_CA_LOCATION', '/app/security/ca.crt'),
        'ssl.certificate.location': os.getenv('KAFKA_SSL_CERTIFICATE_LOCATION', '/app/security/client-creds/kafka.client.certificate.pem'),
        'ssl.key.location': os.getenv('KAFKA_SSL_KEY_LOCATION', '/app/security/client-creds/kafka.client.key'),
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest'
    }

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram bot token or chat ID not set. Skipping message.")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"Message sent to Telegram successfully.")
        else:
            print(f"Failed to send message to Telegram. Status code: {response.status_code}, Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

def start_forwarder():
    print(f"Starting Telegram forwarder with Kafka bootstrap: {BOOT}, topic: {TOPIC}, group ID: {GROUP_ID}")

    cons = Consumer(**kafka_ssl_base())
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
                alert = json.loads(msg.value().decode('utf-8'))
                
            except json.JSONDecodeError as e:
                print(f"Failed to decode message: {e}")

            send_telegram_message(alert['alert'])

    except KeyboardInterrupt:
        print("Shutting down forwarder...")
    finally:
        cons.close()

if __name__ == "__main__":
    start_forwarder()