"""
Tests for input and output modules (Integration Tests).

Covers:
- GestureInput (mocked MediaPipe)
- BlenderOutput (mocked Socket)
- LoupedeckOutput (mocked Socket)
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import importlib

# Mock cv2 and mediapipe before importing modules that use them
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
mp_holistic = MagicMock()
sys.modules['mediapipe'].solutions.holistic = mp_holistic

# Define constants used in the code
mp_holistic.HandLandmark.THUMB_TIP = 4
mp_holistic.HandLandmark.INDEX_FINGER_TIP = 8
mp_holistic.HandLandmark.INDEX_FINGER_PIP = 6
mp_holistic.HandLandmark.MIDDLE_FINGER_TIP = 12
mp_holistic.HandLandmark.MIDDLE_FINGER_PIP = 10
mp_holistic.HandLandmark.RING_FINGER_TIP = 16
mp_holistic.HandLandmark.RING_FINGER_PIP = 14
mp_holistic.HandLandmark.PINKY_TIP = 20
mp_holistic.HandLandmark.PINKY_PIP = 18
mp_holistic.HandLandmark.WRIST = 0

# Import the classes under test
# We reload gesture_input to ensure it picks up the fresh mocks if it was imported before
import inputs.gesture_input
importlib.reload(inputs.gesture_input)
from inputs.gesture_input import GestureInput, GestureState

from outputs.blender_output import BlenderOutput
from outputs.loupedeck_output import LoupedeckOutput
from core.event_system import EventBus, Event, EventType

# Helper classes to simulate MediaPipe landmarks
class _FakeLandmark:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class _FakeHandLandmarks:
    def __init__(self, landmarks):
        self.landmark = landmarks

class TestGestureInput(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        # Capture published events
        self.published = []
        self.event_bus.publish = MagicMock(side_effect=lambda e: self.published.append(e))
        config = {
            "camera_index": 0,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5,
            "show_preview": False,
            "pinch_threshold": 0.05,
        }
        self.gi = GestureInput(self.event_bus, config)
        # Ensure state is clean
        self.gi.state = GestureState()

    def test_detect_pinch_true(self):
        # Thumb and index tip very close
        thumb = _FakeLandmark(x=0.1, y=0.1, z=0.0)
        index = _FakeLandmark(x=0.12, y=0.12, z=0.0)
        
        # Initialize all landmarks to avoid NoneType errors
        landmarks = [_FakeLandmark() for _ in range(21)]
        
        landmarks[mp_holistic.HandLandmark.THUMB_TIP] = thumb
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_TIP] = index
        
        hand = _FakeHandLandmarks(landmarks)
        
        # Directly call the private method
        result = self.gi._detect_pinch(hand)
        self.assertTrue(result)

    def test_detect_basic_gesture_open_palm(self):
        # Simulate all fingers extended (tips above PIP)
        def make_finger(tip_y, pip_y):
            return _FakeLandmark(y=tip_y), _FakeLandmark(y=pip_y)
            
        # Initialize all landmarks
        landmarks = [_FakeLandmark() for _ in range(21)]
        
        # Index finger
        tip, pip = make_finger(tip_y=0.2, pip_y=0.4)
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_TIP] = tip
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_PIP] = pip
        # Middle finger
        tip, pip = make_finger(tip_y=0.2, pip_y=0.4)
        landmarks[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP] = tip
        landmarks[mp_holistic.HandLandmark.MIDDLE_FINGER_PIP] = pip
        # Ring finger
        tip, pip = make_finger(tip_y=0.2, pip_y=0.4)
        landmarks[mp_holistic.HandLandmark.RING_FINGER_TIP] = tip
        landmarks[mp_holistic.HandLandmark.RING_FINGER_PIP] = pip
        # Pinky
        tip, pip = make_finger(tip_y=0.2, pip_y=0.4)
        landmarks[mp_holistic.HandLandmark.PINKY_TIP] = tip
        landmarks[mp_holistic.HandLandmark.PINKY_PIP] = pip
        
        hand = _FakeHandLandmarks(landmarks)
        gesture = self.gi._detect_basic_gesture(hand)
        self.assertEqual(gesture, "OPEN_PALM")

    def test_process_frame_publishes_event(self):
        # Create a hand that will be recognised as POINTING
        # Only index finger extended
        landmarks = [_FakeLandmark() for _ in range(21)]
        
        # Index finger tip above PIP
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_TIP] = _FakeLandmark(y=0.2, x=0.5)
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_PIP] = _FakeLandmark(y=0.4, x=0.5)
        # Add THUMB_TIP far away to avoid pinch detection
        landmarks[mp_holistic.HandLandmark.THUMB_TIP] = _FakeLandmark(y=0.2, x=0.9)
        
        # Other fingers not extended (tip below PIP)
        for lm in [
            (mp_holistic.HandLandmark.MIDDLE_FINGER_TIP, mp_holistic.HandLandmark.MIDDLE_FINGER_PIP),
            (mp_holistic.HandLandmark.RING_FINGER_TIP, mp_holistic.HandLandmark.RING_FINGER_PIP),
            (mp_holistic.HandLandmark.PINKY_TIP, mp_holistic.HandLandmark.PINKY_PIP),
        ]:
            landmarks[lm[0]] = _FakeLandmark(y=0.6)
            landmarks[lm[1]] = _FakeLandmark(y=0.4)
            
        # Wrist needed for position calculations
        landmarks[mp_holistic.HandLandmark.WRIST] = _FakeLandmark(x=0.5, y=0.5, z=0.0)
        
        hand = _FakeHandLandmarks(landmarks)
        # Mock results object with required attributes
        class _FakeResults:
            def __init__(self, hand):
                self.right_hand_landmarks = hand
                self.left_hand_landmarks = None
        results = _FakeResults(hand)
        # Call _process_gestures directly
        self.gi._process_gestures(results=results)
        # Verify an event was published
        self.assertEqual(len(self.published), 1)
        ev = self.published[0]
        self.assertIsInstance(ev, Event)
        self.assertEqual(ev.type, EventType.GESTURE)
        self.assertEqual(ev.action, "POINTING")

class TestBlenderOutput(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.config = {
            "blender_host": "localhost",
            "blender_port": 8888,
            "enabled": True,
            "mappings": {
                "PINCH_DRAG": "viewport_rotate",
                "OPEN_PALM": "play_animation"
            }
        }
        self.blender = BlenderOutput(self.event_bus, self.config)

    @patch('socket.socket')
    def test_send_mapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        # Simulate successful connection
        self.blender._connect()
        # Publish a mapped gesture event
        event = Event(type=EventType.GESTURE, source="test", action="OPEN_PALM")
        self.blender._handle_event(event)
        # Verify that sendall was called with JSON containing the command
        expected_json = {"command": "play_animation", "timestamp": event.timestamp}
        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0]
        self.assertIn(b'play_animation', sent_data)

    @patch('socket.socket')
    def test_ignore_unmapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.blender._connect()
        event = Event(type=EventType.GESTURE, source="test", action="UNKNOWN_GESTURE")
        self.blender._handle_event(event)
        mock_socket.sendall.assert_not_called()

    @patch('socket.socket', side_effect=ConnectionRefusedError)
    def test_connection_failure(self, mock_socket_cls):
        # Connection should fail gracefully and not raise
        self.blender._connect()
        self.assertFalse(self.blender.connected)

class TestLoupedeckOutput(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.config = {
            "loupedeck_host": "localhost",
            "loupedeck_port": 5000,
            "enabled": True,
            "mappings": {
                "OPEN_PALM": "OPEN_PALM",
                "CLOSED_FIST": "CLOSED_FIST"
            }
        }
        self.loupedeck = LoupedeckOutput(self.event_bus, self.config)

    @patch('socket.socket')
    def test_send_mapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.loupedeck._connect()
        event = Event(type=EventType.GESTURE, source="test", action="CLOSED_FIST")
        self.loupedeck._handle_gesture(event)
        mock_socket.sendall.assert_called_once()
        sent_data = mock_socket.sendall.call_args[0][0]
        self.assertTrue(sent_data.startswith(b'CLOSED_FIST'))

    @patch('socket.socket')
    def test_ignore_unmapped_gesture(self, mock_socket_cls):
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket
        self.loupedeck._connect()
        event = Event(type=EventType.GESTURE, source="test", action="UNKNOWN")
        self.loupedeck._handle_gesture(event)
        mock_socket.sendall.assert_not_called()

    @patch('socket.socket', side_effect=ConnectionRefusedError)
    def test_connection_failure(self, mock_socket_cls):
        self.loupedeck._connect()
        self.assertFalse(self.loupedeck.connected)

if __name__ == "__main__":
    unittest.main()
