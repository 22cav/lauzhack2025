import pytest
from gestures.detector import GestureResult, Gesture, GestureDetector

class DummyGesture(Gesture):
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, landmarks, context):
        # Always return a result with confidence 0.8
        return GestureResult(name=self.name, confidence=0.8)

def test_gesture_result_validation():
    # Valid confidence
    result = GestureResult(name="test", confidence=0.7)
    assert result.confidence == 0.7
    # Invalid confidence should raise
    with pytest.raises(ValueError):
        GestureResult(name="bad", confidence=1.5)

def test_gesture_detector_register_and_detect():
    detector = GestureDetector(min_confidence=0.5)
    dummy = DummyGesture()
    detector.register(dummy)
    # Mock landmarks (can be None as dummy gesture ignores)
    # Provide dummy landmarks (empty list) to avoid early exit
    dummy_landmarks = []
    results = detector.detect(landmarks=dummy_landmarks)
    assert len(results) == 1
    assert results[0].name == "dummy"
    assert results[0].confidence == 0.8
