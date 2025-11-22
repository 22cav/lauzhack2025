# tests/test_gesture_input.py
"""Tests for gesture input handling.

Covers the detection helpers in `inputs/gesture_input.py` and the
publishing of events via the `EventBus`.
"""

import unittest
from unittest.mock import MagicMock

import unittest
from unittest.mock import MagicMock, patch
import sys

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
from inputs.gesture_input import GestureInput, GestureState
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
        hand = _FakeHandLandmarks([thumb, index])
        # MediaPipe expects a list with many landmarks; we only need the two we use
        # Insert placeholders for other indices
        landmarks = [None] * 21
        landmarks[mp_holistic.HandLandmark.THUMB_TIP] = thumb
        landmarks[mp_holistic.HandLandmark.INDEX_FINGER_TIP] = index
        hand.landmark = landmarks
        # Directly call the private method
        result = self.gi._detect_pinch(hand)
        self.assertTrue(result)

    def test_detect_basic_gesture_open_palm(self):
        # Simulate all fingers extended (tips above PIP)
        def make_finger(tip_y, pip_y):
            return _FakeLandmark(y=tip_y), _FakeLandmark(y=pip_y)
        # Create landmarks list with required indices
        landmarks = [None] * 21
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
        landmarks = [None] * 21
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

if __name__ == "__main__":
    unittest.main()
