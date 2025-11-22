"""
Tests for gesture detection, filtering, registry, and validation.
"""

import unittest
from unittest.mock import MagicMock
from gestures.detector import GestureResult, Gesture, GestureDetector
from gestures.filters import MovingAverageFilter, LandmarkFilter
from gestures.registry import GestureRegistry, get_registry, register
from gestures.validators import ConfidenceValidator, QualityValidator

# --- Detector Tests ---

class DummyGesture(Gesture):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, landmarks, context):
        # Always return a result with confidence 0.8
        return GestureResult(name=self.name, confidence=0.8)

class TestDetector(unittest.TestCase):
    def test_gesture_result_validation(self):
        # Valid confidence
        result = GestureResult(name="test", confidence=0.7)
        self.assertEqual(result.confidence, 0.7)
        # Invalid confidence should raise
        with self.assertRaises(ValueError):
            GestureResult(name="bad", confidence=1.5)

    def test_gesture_detector_register_and_detect(self):
        detector = GestureDetector(min_confidence=0.5)
        dummy = DummyGesture()
        detector.register(dummy)
        # Mock landmarks (can be None as dummy gesture ignores)
        # Provide dummy landmarks (empty list) to avoid early exit
        dummy_landmarks = []
        results = detector.detect(landmarks=dummy_landmarks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "dummy")
        self.assertEqual(results[0].confidence, 0.8)

# --- Filter Tests ---

class DummyLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class DummyLandmarks:
    def __init__(self, points):
        self.landmark = points

class TestFilters(unittest.TestCase):
    def test_moving_average_filter_basic(self):
        maf = MovingAverageFilter(window_size=3)
        # Feed three points
        self.assertEqual(maf.update(1, 2, 3), (1.0, 2.0, 3.0))
        self.assertEqual(maf.update(2, 3, 4), ((1+2)/2, (2+3)/2, (3+4)/2))
        self.assertEqual(maf.update(3, 4, 5), ((1+2+3)/3, (2+3+4)/3, (3+4+5)/3))
        # After buffer is full, oldest value drops
        self.assertEqual(maf.update(4, 5, 6), ((2+3+4)/3, (3+4+5)/3, (4+5+6)/3))

    def test_landmark_filter_smoothing(self):
        lf = LandmarkFilter(window_size=2, num_landmarks=2)
        # Create dummy landmarks with two points
        lm1 = DummyLandmark(0, 0, 0)
        lm2 = DummyLandmark(10, 10, 10)
        landmarks = DummyLandmarks([lm1, lm2])
        smoothed = lf.update(landmarks)
        # First update should return same values (average of single sample)
        self.assertEqual(smoothed.landmark[0].x, 0)
        self.assertEqual(smoothed.landmark[1].x, 10)
        # Update with new values
        lm1b = DummyLandmark(2, 2, 2)
        lm2b = DummyLandmark(12, 12, 12)
        landmarks2 = DummyLandmarks([lm1b, lm2b])
        smoothed2 = lf.update(landmarks2)
        # Now each coordinate should be average of the two samples
        self.assertAlmostEqual(smoothed2.landmark[0].x, (0+2)/2)
        self.assertAlmostEqual(smoothed2.landmark[1].x, (10+12)/2)

# --- Registry Tests ---

class RegistryDummyGesture(Gesture):
    @property
    def name(self) -> str:
        return "registry_dummy"

    def detect(self, landmarks, context):
        return None

class TestRegistry(unittest.TestCase):
    def test_registry_register_and_retrieve(self):
        registry = GestureRegistry()
        registry.register_gesture(RegistryDummyGesture, set_name="test_set")
        # Retrieve class
        cls = registry.get_gesture("registry_dummy")
        self.assertIs(cls, RegistryDummyGesture)
        # Create instance
        instance = registry.create_gesture("registry_dummy")
        self.assertIsInstance(instance, RegistryDummyGesture)
        # List gestures and sets
        self.assertIn("registry_dummy", registry.list_gestures())
        self.assertIn("test_set", registry.list_sets())
        # Get set returns instances
        gestures = registry.get_set("test_set")
        self.assertEqual(len(gestures), 1)
        self.assertIsInstance(gestures[0], RegistryDummyGesture)
        # Metadata
        meta = registry.get_metadata("registry_dummy")
        self.assertEqual(meta["name"], "registry_dummy")
        # Clear
        registry.clear()
        self.assertEqual(registry.list_gestures(), [])
        self.assertEqual(registry.list_sets(), [])

    def test_global_registry_decorator(self):
        # We need to be careful with global state in tests.
        # The decorator registers immediately.
        @register(set_name="global")
        class GlobalDummy(Gesture):
            @property
            def name(self) -> str:
                return "global_dummy"
            def detect(self, landmarks, context):
                return None
        
        global_reg = get_registry()
        self.assertIn("global_dummy", global_reg.list_gestures())
        self.assertIn("global", global_reg.list_sets())
        instance = global_reg.create_gesture("global_dummy")
        self.assertIsInstance(instance, GlobalDummy)

# --- Validator Tests ---

class DummyResult(GestureResult):
    pass

class TestValidators(unittest.TestCase):
    def test_confidence_validator_basic(self):
        validator = ConfidenceValidator(min_confidence=0.5, stability_frames=2)
        # Below confidence should be invalid
        low = GestureResult(name="test", confidence=0.4)
        self.assertFalse(validator.validate(low))
        # Above confidence but need stability frames
        high = GestureResult(name="test", confidence=0.8)
        self.assertFalse(validator.validate(high))  # first frame not enough
        self.assertTrue(validator.validate(high))      # second consecutive same gesture passes
        # Different gesture resets stability
        other = GestureResult(name="other", confidence=0.9)
        self.assertFalse(validator.validate(other))
        # Reset clears history
        validator.reset()
        self.assertEqual(validator.gesture_history, [])

    def test_quality_validator_permissive(self):
        validator = QualityValidator(min_visibility=0.0, min_presence=0.0)
        class ValidatorDummyLandmark:
            def __init__(self, visibility=None, presence=None):
                if visibility is not None:
                    self.visibility = visibility
                if presence is not None:
                    self.presence = presence
        class ValidatorDummyLandmarks:
            def __init__(self, landmarks):
                self.landmark = landmarks
        # All landmarks with default (no attributes) should pass
        lm = ValidatorDummyLandmarks([ValidatorDummyLandmark() for _ in range(5)])
        self.assertTrue(validator.validate(lm))
        # Landmarks with low visibility/presence should still pass due to low thresholds
        lm2 = ValidatorDummyLandmarks([ValidatorDummyLandmark(visibility=0.1, presence=0.1) for _ in range(5)])
        self.assertTrue(validator.validate(lm2))

if __name__ == '__main__':
    unittest.main()
