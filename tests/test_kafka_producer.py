import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock the settings module before importing the producer
# This prevents the producer from trying to access actual settings during import
mock_settings = MagicMock()
mock_settings.KAFKA_BROKER = 'mock_broker:9092'
mock_settings.KAFKA_TOPIC = 'mock_topic'
mock_settings.EVENTS_PER_SECOND = 1.0
sys.modules['config.settings'] = mock_settings

# Now import the producer module
from kafka_producer.producer import create_kafka_producer
from kafka.errors import KafkaError

class TestKafkaProducer(unittest.TestCase):

    @patch('kafka_producer.producer.KafkaProducer') # Mock the KafkaProducer class
    def test_create_kafka_producer_success(self, MockKafkaProducer):
        """Test successful creation of KafkaProducer."""
        # Configure the mock to return a mock producer instance
        mock_producer_instance = MockKafkaProducer.return_value
        broker = 'test_broker:9092'

        producer = create_kafka_producer(broker)

        # Assert that KafkaProducer was called with the correct arguments
        MockKafkaProducer.assert_called_once_with(
            bootstrap_servers=broker,
            value_serializer=unittest.mock.ANY, # Serializer is a lambda, hard to match exactly
            acks='all',
            retries=5,
            linger_ms=100,
            batch_size=16384
        )
        # Assert that the returned value is the mock producer instance
        self.assertEqual(producer, mock_producer_instance)

    @patch('kafka_producer.producer.KafkaProducer') # Mock the KafkaProducer class
    def test_create_kafka_producer_failure(self, MockKafkaProducer):
        """Test handling of KafkaError during producer creation."""
        # Configure the mock to raise KafkaError when called
        MockKafkaProducer.side_effect = KafkaError("Test Kafka connection error")
        broker = 'test_broker:9092'

        producer = create_kafka_producer(broker)

        # Assert that KafkaProducer was called
        MockKafkaProducer.assert_called_once()
        # Assert that None is returned on error
        self.assertIsNone(producer)

if __name__ == '__main__':
    unittest.main()