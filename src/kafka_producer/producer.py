import json
import time
import random
import uuid
import os
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

from config import settings # Import the settings

fake = Faker()

EVENT_TYPES = ['product_view', 'add_to_cart', 'checkout_start', 'purchase', 'product_click']

# --- Configuration (Consider moving to a config file or env vars later) ---
# KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092') # Removed
# KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'product_events') # Removed
# EVENTS_PER_SECOND = float(os.environ.get('EVENTS_PER_SECOND', 1.0)) # Removed
# ------------------------------------------------------------------------

def generate_event():
    """Generates a single simulated product interaction event."""
    user_id = str(uuid.uuid4()) # Simulate unique users for each event for simplicity
    product_id = f"prod_{random.randint(100, 999)}"
    event_type = random.choice(EVENT_TYPES)
    timestamp = datetime.utcnow().isoformat() + "Z"

    event = {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": fake.sha1(raw_output=False)[:16], # Simulate a session ID
        "product_id": product_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "user_agent": fake.user_agent(),
        "ip_address": fake.ipv4(),
        "platform": random.choice(['web', 'mobile_app', 'tablet']),
        "country": fake.country_code(),
    }

    # Add event-specific details
    if event_type == 'product_view':
        event['view_duration_seconds'] = random.randint(5, 120)
    elif event_type == 'add_to_cart':
        event['quantity'] = random.randint(1, 5)
        event['price'] = round(random.uniform(10.0, 500.0), 2)
    elif event_type == 'purchase':
        event['quantity'] = random.randint(1, 3)
        event['total_amount'] = round(random.uniform(20.0, 1000.0), 2)
        event['currency'] = 'USD'

    return event

def create_kafka_producer(broker_servers):
    """Creates and returns a KafkaProducer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=broker_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all', # Ensure messages are acknowledged by leader and replicas
            retries=5, # Retry sending messages on failure
            linger_ms=100, # Batch messages for 100ms
            batch_size=16384 # 16KB batch size
        )
        print(f"Successfully connected to Kafka broker at {broker_servers}")
        return producer
    except KafkaError as e:
        print(f"Error connecting to Kafka: {e}")
        return None

def main():
    """Main function to generate events and send them to Kafka."""
    producer = create_kafka_producer(settings.KAFKA_BROKER) # Use settings.KAFKA_BROKER
    if not producer:
        print("Exiting due to Kafka connection failure.")
        return

    print(f"Starting data production for topic '{settings.KAFKA_TOPIC}'...") # Use settings.KAFKA_TOPIC
    print(f"Targeting ~{settings.EVENTS_PER_SECOND} events per second.") # Use settings.EVENTS_PER_SECOND
    print("Press Ctrl+C to stop.")

    try:
        while True:
            event_data = generate_event()
            try:
                # Send message (asynchronously)
                future = producer.send(settings.KAFKA_TOPIC, value=event_data) # Use settings.KAFKA_TOPIC
                # Optional: Block for ack (can reduce throughput)
                # record_metadata = future.get(timeout=10)
                # print(f"Sent event {event_data['event_id']} to topic {record_metadata.topic} partition {record_metadata.partition}")
            except KafkaError as e:
                print(f"Error sending message: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            # Control the rate of event generation
            sleep_time = 1.0 / settings.EVENTS_PER_SECOND # Use settings.EVENTS_PER_SECOND
            time.sleep(sleep_time * random.uniform(0.8, 1.2)) # Add some jitter

    except KeyboardInterrupt:
        print("\nStopping data production...")
    finally:
        if producer:
            print("Flushing remaining messages...")
            producer.flush() # Ensure all buffered messages are sent
            print("Closing Kafka producer.")
            producer.close()

if __name__ == "__main__":
    main()