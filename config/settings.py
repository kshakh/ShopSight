import os

# Kafka Configuration
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'product_events')

# Kafka Producer Configuration
EVENTS_PER_SECOND = float(os.environ.get('EVENTS_PER_SECOND', 1.0))

# Spark Streaming Configuration
DELTA_TABLE_PATH = os.environ.get('DELTA_TABLE_PATH', '/tmp/delta/product_events')
CHECKPOINT_LOCATION = os.environ.get('CHECKPOINT_LOCATION', '/tmp/spark_checkpoints/product_events')

# Add other configurations as needed