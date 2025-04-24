import json
import time
import random
import uuid
from datetime import datetime
from faker import Faker

fake = Faker()

EVENT_TYPES = ['product_view', 'add_to_cart', 'checkout_start', 'purchase', 'product_click']

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

def main():
    """Main function to generate and print events."""
    print("Starting data simulation...")
    try:
        while True:
            event_data = generate_event()
            print(json.dumps(event_data))
            time.sleep(random.uniform(0.1, 1.5)) # Simulate variable time between events
    except KeyboardInterrupt:
        print("\nStopping data simulation.")

if __name__ == "__main__":
    main()