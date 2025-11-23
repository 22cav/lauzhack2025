"""
Tests for Navigation Gestures and State Machine.
"""

import unittest
from unittest.mock import MagicMock
import sys

# Mock cv2/mediapipe BEFORE importing modules that use them
sys.modules['cv2'] = MagicMock()
sys.modules['mediapipe'] = MagicMock()
mp_holistic = MagicMock()
sys.modules['mediapipe'].solutions.holistic = mp_holistic

# Constants
mp_holistic.HandLandmark.WRIST = 0
mp_holistic.HandLandmark.THUMB_CMC = 1
mp_holistic.HandLandmark.THUMB_MCP = 2
mp_holistic.HandLandmark.THUMB_IP = 3
mp_holistic.HandLandmark.THUMB_TIP = 4
mp_holistic.HandLandmark.INDEX_FINGER_MCP = 5
mp_holistic.HandLandmark.INDEX_FINGER_PIP = 6
mp_holistic.HandLandmark.INDEX_FINGER_DIP = 7
mp_holistic.HandLandmark.INDEX_FINGER_TIP = 8
mp_holistic.HandLandmark.MIDDLE_FINGER_MCP = 9
mp_holistic.HandLandmark.MIDDLE_FINGER_PIP = 10
mp_holistic.HandLandmark.MIDDLE_FINGER_DIP = 11
mp_holistic.HandLandmark.MIDDLE_FINGER_TIP = 12
mp_holistic.HandLandmark.RING_FINGER_MCP = 13
mp_holistic.HandLandmark.RING_FINGER_PIP = 14
mp_holistic.HandLandmark.RING_FINGER_DIP = 15
mp_holistic.HandLandmark.RING_FINGER_TIP = 16
mp_holistic.HandLandmark.PINKY_MCP = 17
mp_holistic.HandLandmark.PINKY_PIP = 18
mp_holistic.HandLandmark.PINKY_DIP = 19
mp_holistic.HandLandmark.PINKY_TIP = 20

import numpy as np
from gestures.library import navigation
from inputs.gesture_input_production import GestureInputBase
from core.event_system import EventBus

class FakeLandmark:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class FakeLandmarks:
    def __init__(self, landmarks):
        self.landmark = landmarks

class TestNavigationGestures(unittest.TestCase):
    def create_hand(self, fingers_extended):
        """
        Helper to create a hand with specific fingers extended.
        fingers_extended: list of bool [Index, Middle, Ring, Pinky]
        """
        landmarks = [FakeLandmark(0, 0) for _ in range(21)]
        
        # Wrist at 0.5, 0.8
        landmarks[0] = FakeLandmark(0.5, 0.8)
        
        # Thumb (neutral)
        landmarks[4] = FakeLandmark(0.6, 0.6)
        landmarks[3] = FakeLandmark(0.58, 0.65)
        
        # Fingers
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for i, extended in enumerate(fingers_extended):
            tip_idx = tips[i]
            pip_idx = pips[i]
            
            if extended:
                # Extended: Tip far from wrist (y=0.2), PIP closer (y=0.5)
                landmarks[tip_idx] = FakeLandmark(0.5 + i*0.1, 0.2)
                landmarks[pip_idx] = FakeLandmark(0.5 + i*0.1, 0.5)
            else:
                # Closed: Tip VERY close to wrist (y=0.75), PIP further (y=0.6)
                # Also reduce X spread for closed fingers
                landmarks[tip_idx] = FakeLandmark(0.5 + i*0.02, 0.75)
                landmarks[pip_idx] = FakeLandmark(0.5 + i*0.02, 0.6)
                
        return FakeLandmarks(landmarks)

    def test_two_fingers_forward(self):
        gesture = navigation.TwoFingersForward()
        
        # Correct fingers (Index+Middle)
        hand = self.create_hand([True, True, False, False])
        
        # Mock Z-axis (Tip closer to camera than PIP)
        # Z is relative to wrist. Negative is closer to camera.
        hand.landmark[8].z = -0.1
        hand.landmark[6].z = 0.0
        hand.landmark[12].z = -0.1
        hand.landmark[10].z = 0.0
        
        result = gesture.detect(hand, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "TWO_FINGERS_FORWARD")
        
        # Incorrect fingers (Ring extended)
        hand_bad = self.create_hand([True, True, True, False])
        self.assertIsNone(gesture.detect(hand_bad, {}))

    def test_two_fingers_left(self):
        gesture = navigation.TwoFingersLeft()
        hand = self.create_hand([True, True, False, False])
        
        # Tip left of PIP
        hand.landmark[8].x = 0.4
        hand.landmark[6].x = 0.5
        
        result = gesture.detect(hand, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "TWO_FINGERS_LEFT")

    def test_two_fingers_right(self):
        gesture = navigation.TwoFingersRight()
        hand = self.create_hand([True, True, False, False])
        
        # Tip right of PIP
        hand.landmark[8].x = 0.6
        hand.landmark[6].x = 0.5
        
        result = gesture.detect(hand, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "TWO_FINGERS_RIGHT")

    def test_open_palm(self):
        gesture = navigation.OpenPalm()
        hand = self.create_hand([True, True, True, True])
        
        # Thumb extended
        hand.landmark[4] = FakeLandmark(0.8, 0.5) # Tip
        hand.landmark[3] = FakeLandmark(0.7, 0.6) # IP
        hand.landmark[0] = FakeLandmark(0.5, 0.8) # Wrist
        
        # Spread
        hand.landmark[8] = FakeLandmark(0.2, 0.2) # Index
        hand.landmark[20] = FakeLandmark(0.8, 0.2) # Pinky
        
        result = gesture.detect(hand, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "OPEN_PALM")

    def test_closed_fist(self):
        gesture = navigation.ClosedFist()
        hand = self.create_hand([False, False, False, False])
        
        # Compactness
        hand.landmark[12] = FakeLandmark(0.5, 0.75) # Middle Tip
        hand.landmark[0] = FakeLandmark(0.5, 0.8) # Wrist
        
        result = gesture.detect(hand, {})
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "CLOSED_FIST")

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()
        self.config = {
            'gesture_sets': ['navigation'],
            'min_confidence': 0.0, # Allow mock detections
            'stability_frames': 1 # Immediate detection
        }
        self.input = GestureInputBase(self.bus, self.config)
        self.events = []
        self.bus.publish = MagicMock(side_effect=lambda e: self.events.append(e))
        
        # Mock dependencies
        self.input.quality_validator.validate = MagicMock(return_value=True)
        self.input.landmark_filter.update = MagicMock(side_effect=lambda x: x)
        self.input.confidence_validator.validate = MagicMock(return_value=True)

    def test_stop_play_logic(self):
        # Mock detector to return specific sequence
        mock_result_stop = MagicMock()
        mock_result_stop.name = "CLOSED_FIST"
        mock_result_stop.data = {}
        
        mock_result_play = MagicMock()
        mock_result_play.name = "OPEN_PALM"
        mock_result_play.data = {}
        
        mock_result_nav = MagicMock()
        mock_result_nav.name = "TWO_FINGERS_FORWARD"
        mock_result_nav.data = {}
        
        # 1. Initially Playing
        self.assertTrue(self.input.is_playing)
        
        # 2. Detect CLOSED_FIST -> Should Stop
        self.input.detector.detect_best = MagicMock(return_value=mock_result_stop)
        self.input._process_frame(None, MagicMock())
        
        self.assertFalse(self.input.is_playing)
        self.assertEqual(self.events[-1].action, "STOP")
        
        # 3. Detect Navigation while Stopped -> Should be ignored/blocked
        self.input.detector.detect_best = MagicMock(return_value=mock_result_nav)
        status = self.input._process_frame(None, MagicMock())
        
        self.assertEqual(status, "STOPPED")
        # Should NOT publish navigation event
        self.assertEqual(self.events[-1].action, "STOP") # Last event was still STOP
        
        # 4. Detect OPEN_PALM -> Should Play
        self.input.detector.detect_best = MagicMock(return_value=mock_result_play)
        self.input._process_frame(None, MagicMock())
        
        self.assertTrue(self.input.is_playing)
        self.assertEqual(self.events[-1].action, "PLAY")

if __name__ == '__main__':
    unittest.main()
