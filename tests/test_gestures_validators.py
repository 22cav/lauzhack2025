import pytest
from gestures.validators import ConfidenceValidator, QualityValidator
from gestures.detector import GestureResult

class DummyResult(GestureResult):
    pass

def test_confidence_validator_basic():
    validator = ConfidenceValidator(min_confidence=0.5, stability_frames=2)
    # Below confidence should be invalid
    low = GestureResult(name="test", confidence=0.4)
    assert not validator.validate(low)
    # Above confidence but need stability frames
    high = GestureResult(name="test", confidence=0.8)
    assert not validator.validate(high)  # first frame not enough
    assert validator.validate(high)      # second consecutive same gesture passes
    # Different gesture resets stability
    other = GestureResult(name="other", confidence=0.9)
    assert not validator.validate(other)
    # Reset clears history
    validator.reset()
    assert validator.gesture_history == []

def test_quality_validator_permissive():
    validator = QualityValidator(min_visibility=0.0, min_presence=0.0)
    class DummyLandmark:
        def __init__(self, visibility=None, presence=None):
            if visibility is not None:
                self.visibility = visibility
            if presence is not None:
                self.presence = presence
    class DummyLandmarks:
        def __init__(self, landmarks):
            self.landmark = landmarks
    # All landmarks with default (no attributes) should pass
    lm = DummyLandmarks([DummyLandmark() for _ in range(5)])
    assert validator.validate(lm)
    # Landmarks with low visibility/presence should still pass due to low thresholds
    lm2 = DummyLandmarks([DummyLandmark(visibility=0.1, presence=0.1) for _ in range(5)])
    assert validator.validate(lm2)
