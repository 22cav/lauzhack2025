import pytest
from gestures.filters import MovingAverageFilter, LandmarkFilter

class DummyLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class DummyLandmarks:
    def __init__(self, points):
        self.landmark = points

def test_moving_average_filter_basic():
    maf = MovingAverageFilter(window_size=3)
    # Feed three points
    assert maf.update(1, 2, 3) == (1.0, 2.0, 3.0)
    assert maf.update(2, 3, 4) == ((1+2)/2, (2+3)/2, (3+4)/2)
    assert maf.update(3, 4, 5) == ((1+2+3)/3, (2+3+4)/3, (3+4+5)/3)
    # After buffer is full, oldest value drops
    assert maf.update(4, 5, 6) == ((2+3+4)/3, (3+4+5)/3, (4+5+6)/3)

def test_landmark_filter_smoothing():
    lf = LandmarkFilter(window_size=2, num_landmarks=2)
    # Create dummy landmarks with two points
    lm1 = DummyLandmark(0, 0, 0)
    lm2 = DummyLandmark(10, 10, 10)
    landmarks = DummyLandmarks([lm1, lm2])
    smoothed = lf.update(landmarks)
    # First update should return same values (average of single sample)
    assert smoothed.landmark[0].x == 0
    assert smoothed.landmark[1].x == 10
    # Update with new values
    lm1b = DummyLandmark(2, 2, 2)
    lm2b = DummyLandmark(12, 12, 12)
    landmarks2 = DummyLandmarks([lm1b, lm2b])
    smoothed2 = lf.update(landmarks2)
    # Now each coordinate should be average of the two samples
    assert smoothed2.landmark[0].x == pytest.approx((0+2)/2)
    assert smoothed2.landmark[1].x == pytest.approx((10+12)/2)
