"""
Tests for core event system and data structures.
"""

import unittest
import time
from unittest.mock import MagicMock
import sys

# Mock cv2/mediapipe for structure tests if needed
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()

from core.event_system import Event, EventBus, EventType
from inputs.gesture_input import GestureState

class TestEventSystem(unittest.TestCase):
    """Test cases for Event and EventBus classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event_bus = EventBus()
        self.received_events = []
    
    def tearDown(self):
        """Clean up after tests."""
        self.event_bus.clear_subscribers()
    
    def test_event_creation(self):
        """Test Event creation."""
        event = Event(
            type=EventType.GESTURE,
            source="test",
            action="TEST_ACTION",
            data={"key": "value"}
        )
        
        self.assertEqual(event.type, EventType.GESTURE)
        self.assertEqual(event.source, "test")
        self.assertEqual(event.action, "TEST_ACTION")
        self.assertEqual(event.data["key"], "value")
        self.assertIsInstance(event.timestamp, float)
    
    def test_subscribe_and_publish(self):
        """Test basic publish-subscribe."""
        def callback(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.GESTURE, callback)
        
        event = Event(
            type=EventType.GESTURE,
            source="test",
            action="TEST"
        )
        
        self.event_bus.publish(event)
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].action, "TEST")
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event type."""
        events1 = []
        events2 = []
        
        def callback1(event):
            events1.append(event)
        
        def callback2(event):
            events2.append(event)
        
        self.event_bus.subscribe(EventType.GESTURE, callback1)
        self.event_bus.subscribe(EventType.GESTURE, callback2)
        
        event = Event(type=EventType.GESTURE, source="test", action="TEST")
        self.event_bus.publish(event)
        
        self.assertEqual(len(events1), 1)
        self.assertEqual(len(events2), 1)
    
    def test_event_type_filtering(self):
        """Test that subscribers only receive events of subscribed type."""
        gesture_events = []
        button_events = []
        
        def gesture_callback(event):
            gesture_events.append(event)
        
        def button_callback(event):
            button_events.append(event)
        
        self.event_bus.subscribe(EventType.GESTURE, gesture_callback)
        self.event_bus.subscribe(EventType.BUTTON, button_callback)
        
        gesture_event = Event(type=EventType.GESTURE, source="test", action="GESTURE")
        button_event = Event(type=EventType.BUTTON, source="test", action="BUTTON")
        
        self.event_bus.publish(gesture_event)
        self.event_bus.publish(button_event)
        
        self.assertEqual(len(gesture_events), 1)
        self.assertEqual(len(button_events), 1)
        self.assertEqual(gesture_events[0].action, "GESTURE")
        self.assertEqual(button_events[0].action, "BUTTON")
    
    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        def callback(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.GESTURE, callback)
        
        event = Event(type=EventType.GESTURE, source="test", action="TEST")
        self.event_bus.publish(event)
        
        self.assertEqual(len(self.received_events), 1)
        
        self.event_bus.unsubscribe(EventType.GESTURE, callback)
        self.event_bus.publish(event)
        
        # Should still be 1, not 2
        self.assertEqual(len(self.received_events), 1)
    
    def test_subscriber_count(self):
        """Test getting subscriber count."""
        self.assertEqual(self.event_bus.get_subscriber_count(EventType.GESTURE), 0)
        
        def callback(event):
            pass
        
        self.event_bus.subscribe(EventType.GESTURE, callback)
        self.assertEqual(self.event_bus.get_subscriber_count(EventType.GESTURE), 1)
        
        self.event_bus.subscribe(EventType.GESTURE, callback)
        self.assertEqual(self.event_bus.get_subscriber_count(EventType.GESTURE), 2)
    
    def test_event_counter(self):
        """Test total event count."""
        initial_count = self.event_bus.get_total_events()
        
        event = Event(type=EventType.GESTURE, source="test", action="TEST")
        self.event_bus.publish(event)
        self.event_bus.publish(event)
        
        self.assertEqual(self.event_bus.get_total_events(), initial_count + 2)
    
    def test_error_in_subscriber_doesnt_crash(self):
        """Test that errors in subscribers don't crash the event bus."""
        def bad_callback(event):
            raise ValueError("Test error")
        
        def good_callback(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.GESTURE, bad_callback)
        self.event_bus.subscribe(EventType.GESTURE, good_callback)
        
        event = Event(type=EventType.GESTURE, source="test", action="TEST")
        
        # Should not raise exception
        self.event_bus.publish(event)
        
        # Good callback should still receive event
        self.assertEqual(len(self.received_events), 1)

class TestEventStructures(unittest.TestCase):
    def test_event_attributes_types(self):
        """Test that Event attributes have correct types."""
        data = {"x": 1, "y": 2}
        event = Event(
            type=EventType.GESTURE,
            source="test_source",
            action="TEST_ACTION",
            data=data
        )
        
        self.assertIsInstance(event.type, EventType)
        self.assertIsInstance(event.source, str)
        self.assertIsInstance(event.action, str)
        self.assertIsInstance(event.data, dict)
        self.assertIsInstance(event.timestamp, float)
        
        # Verify data integrity
        self.assertEqual(event.data, data)
        # Ensure data copy if mutable (Event implementation might not copy, but good to check behavior)
        data["z"] = 3
        # If Event stores reference, it changes. If copy, it doesn't. 
        # We just want to know it behaves as expected (reference usually).
        self.assertEqual(event.data["z"], 3)

    def test_event_type_enum(self):
        """Test EventType constants."""
        self.assertEqual(EventType.GESTURE.value, "GESTURE")
        self.assertEqual(EventType.BUTTON.value, "BUTTON")

class TestGestureStateStructure(unittest.TestCase):
    def test_initial_state(self):
        """Test GestureState initialization values and types."""
        state = GestureState()
        
        self.assertIsInstance(state.current_gesture, str)
        self.assertEqual(state.current_gesture, "UNKNOWN")
        
        self.assertIsInstance(state.is_pinching, bool)
        self.assertFalse(state.is_pinching)
        
        self.assertIsNone(state.pinch_start_pos)
        self.assertIsNone(state.last_hand_pos)

    def test_state_mutability(self):
        """Test that state attributes can be updated with correct types."""
        state = GestureState()
        
        # Update gesture
        state.current_gesture = "OPEN_PALM"
        self.assertEqual(state.current_gesture, "OPEN_PALM")
        
        # Update pinch
        state.is_pinching = True
        self.assertTrue(state.is_pinching)
        
        # Update positions
        pos = {'x': 0.5, 'y': 0.5, 'z': 0.0}
        state.pinch_start_pos = pos
        state.last_hand_pos = pos
        
        self.assertEqual(state.pinch_start_pos, pos)
        self.assertEqual(state.last_hand_pos, pos)

class TestConfigurationSchema(unittest.TestCase):
    """Tests for configuration dictionary validation."""
    
    def validate_gesture_input_config(self, config):
        """Helper to validate gesture input config schema."""
        required_keys = {'camera_index', 'min_detection_confidence'}
        if not all(key in config for key in required_keys):
            return False
        if not isinstance(config['camera_index'], int):
            return False
        if not isinstance(config['min_detection_confidence'], float):
            return False
        return True

    def test_valid_gesture_config(self):
        config = {
            'camera_index': 0,
            'min_detection_confidence': 0.7,
            'show_preview': True
        }
        self.assertTrue(self.validate_gesture_input_config(config))

    def test_invalid_gesture_config_missing_key(self):
        config = {
            'camera_index': 0
            # missing min_detection_confidence
        }
        self.assertFalse(self.validate_gesture_input_config(config))

    def test_invalid_gesture_config_wrong_type(self):
        config = {
            'camera_index': "0", # Should be int
            'min_detection_confidence': 0.7
        }
        self.assertFalse(self.validate_gesture_input_config(config))

if __name__ == '__main__':
    unittest.main()
