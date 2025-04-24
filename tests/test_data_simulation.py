import unittest
import sys
import os
from datetime import datetime

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_simulation.simulate_data import generate_event, EVENT_TYPES

class TestDataSimulation(unittest.TestCase):

    def test_generate_event_returns_dict(self):
        """Test that generate_event returns a dictionary."""
        event = generate_event()
        self.assertIsInstance(event, dict)

    def test_generate_event_has_required_keys(self):
        """Test that the generated event contains essential keys."""
        event = generate_event()
        required_keys = [
            "event_id", "user_id", "session_id", "product_id",
            "event_type", "timestamp", "user_agent", "ip_address",
            "platform", "country"
        ]
        for key in required_keys:
            self.assertIn(key, event)
            self.assertIsNotNone(event[key])

    def test_generate_event_event_type_is_valid(self):
        """Test that the event_type is one of the predefined types."""
        event = generate_event()
        self.assertIn(event['event_type'], EVENT_TYPES)

    def test_generate_event_timestamp_format(self):
        """Test that the timestamp is in the correct ISO format with Z."""
        event = generate_event()
        try:
            # Check if it ends with 'Z' and the rest is parsable
            self.assertTrue(event['timestamp'].endswith('Z'))
            datetime.fromisoformat(event['timestamp'][:-1]) # Parse without the Z
        except ValueError:
            self.fail("Timestamp is not in the expected ISO format (YYYY-MM-DDTHH:MM:SS.ffffffZ)")

    def test_event_specific_keys(self):
        """Test for the presence of event-specific keys."""
        # Run multiple times to increase chance of hitting all event types
        for _ in range(len(EVENT_TYPES) * 5):
            event = generate_event()
            event_type = event['event_type']

            if event_type == 'product_view':
                self.assertIn('view_duration_seconds', event)
                self.assertIsInstance(event['view_duration_seconds'], int)
            elif event_type == 'add_to_cart':
                self.assertIn('quantity', event)
                self.assertIsInstance(event['quantity'], int)
                self.assertIn('price', event)
                self.assertIsInstance(event['price'], float)
            elif event_type == 'purchase':
                self.assertIn('quantity', event)
                self.assertIsInstance(event['quantity'], int)
                self.assertIn('total_amount', event)
                self.assertIsInstance(event['total_amount'], float)
                self.assertIn('currency', event)
                self.assertEqual(event['currency'], 'USD')
            elif event_type in ['checkout_start', 'product_click']:
                # Check that other event-specific keys are NOT present
                self.assertNotIn('view_duration_seconds', event)
                self.assertNotIn('price', event)
                self.assertNotIn('total_amount', event)
                self.assertNotIn('currency', event)

if __name__ == '__main__':
    unittest.main()