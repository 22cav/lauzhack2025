# tests/test_structures.py
"""Tests for data structures and type integrity.

Validates the structural integrity of Events, GestureStates, and Configuration dictionaries.
"""

import unittest
import time
import unittest
import time
from unittest.mock import MagicMock
import sys

# Mock cv2 before importing gesture_input
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()

from core.event_system import Event, EventType, EventBus
from inputs.gesture_input import GestureState

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
        # Ensure we can't easily overwrite them (though Python enums/classes are mutable unless protected)
        # This is more of a sanity check that they exist.

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

if __name__ == "__main__":
    unittest.main()
