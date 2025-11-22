"""
Smoothing Filters for Landmark and Movement Data

Provides noise reduction and smoothing algorithms for robust gesture detection.
"""

import numpy as np
from collections import deque
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MovingAverageFilter:
    """Simple moving average filter for smoothing landmark positions."""
    
    def __init__(self, window_size: int = 5):
        """
        Initialize filter.
        
        Args:
            window_size: Number of samples to average
        """
        self.window_size = window_size
        self.buffer_x = deque(maxlen=window_size)
        self.buffer_y = deque(maxlen=window_size)
        self.buffer_z = deque(maxlen=window_size)
    
    def update(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Update filter with new position.
        
        Args:
            x, y, z: New position coordinates
        
        Returns:
            Smoothed (x, y, z) coordinates
        """
        self.buffer_x.append(x)
        self.buffer_y.append(y)
        self.buffer_z.append(z)
        
        return (
            sum(self.buffer_x) / len(self.buffer_x),
            sum(self.buffer_y) / len(self.buffer_y),
            sum(self.buffer_z) / len(self.buffer_z)
        )
    
    def reset(self):
        """Clear filter buffer."""
        self.buffer_x.clear()
        self.buffer_y.clear()
        self.buffer_z.clear()


class LandmarkFilter:
    """
    Filter for smoothing all hand landmarks.
    
    Uses moving average for each landmark point.
    """
    
    def __init__(self, window_size: int = 5, num_landmarks: int = 21):
        """
        Initialize landmark filter.
        
        Args:
            window_size: Smoothing window size
            num_landmarks: Number of landmarks (default 21 for hand)
        """
        self.filters = [MovingAverageFilter(window_size) for _ in range(num_landmarks)]
        self.window_size = window_size
    
    def update(self, landmarks):
        """
        Smooth all landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
        
        Returns:
            Smoothed landmarks (same structure as input)
        """
        if landmarks is None:
            return None
        
        # Create copy to avoid modifying original
        import copy
        smoothed = copy.deepcopy(landmarks)
        
        # Smooth each landmark
        for i, landmark in enumerate(landmarks.landmark):
            if i < len(self.filters):
                x, y, z = self.filters[i].update(landmark.x, landmark.y, landmark.z)
                smoothed.landmark[i].x = x
                smoothed.landmark[i].y = y
                smoothed.landmark[i].z = z
        
        return smoothed
    
    def reset(self):
        """Reset all filters."""
        for f in self.filters:
            f.reset()


class MovementFilter:
    """
    Filter for detecting and smoothing hand movements.
    
    Calculates velocity and acceleration with noise reduction.
    """
    
    def __init__(self, window_size: int = 3):
        """
        Initialize movement filter.
        
        Args:
            window_size: Window for velocity/acceleration calculation
        """
        self.window_size = window_size
        self.position_history = deque(maxlen=window_size)
        self.velocity_history = deque(maxlen=window_size)
        self.last_time = None
    
    def update(self, position: Tuple[float, float, float], timestamp: float) -> dict:
        """
        Update with new position and calculate movement metrics.
        
        Args:
            position: (x, y, z) position tuple
            timestamp: Current timestamp in seconds
        
        Returns:
            Dictionary with position, velocity, acceleration, speed
        """
        self.position_history.append(position)
        
        result = {
            'position': position,
            'velocity': (0.0, 0.0, 0.0),
            'acceleration': (0.0, 0.0, 0.0),
            'speed': 0.0,
            'is_moving': False
        }
        
        # Calculate velocity
        if len(self.position_history) >= 2 and self.last_time is not None:
            dt = timestamp - self.last_time
            if dt > 0:
                prev_pos = self.position_history[-2]
                velocity = tuple((position[i] - prev_pos[i]) / dt for i in range(3))
                self.velocity_history.append(velocity)
                
                # Average velocity for smoothing
                if self.velocity_history:
                    avg_velocity = tuple(
                        sum(v[i] for v in self.velocity_history) / len(self.velocity_history)
                        for i in range(3)
                    )
                    result['velocity'] = avg_velocity
                    result['speed'] = np.linalg.norm(avg_velocity)
                    result['is_moving'] = result['speed'] > 0.01  # Threshold
        
        # Calculate acceleration
        if len(self.velocity_history) >= 2 and self.last_time is not None:
            dt = timestamp - self.last_time
            if dt > 0:
                prev_vel = self.velocity_history[-2]
                curr_vel = self.velocity_history[-1]
                acceleration = tuple((curr_vel[i] - prev_vel[i]) / dt for i in range(3))
                result['acceleration'] = acceleration
        
        self.last_time = timestamp
        return result
    
    def reset(self):
        """Reset movement history."""
        self.position_history.clear()
        self.velocity_history.clear()
        self.last_time = None


class OutlierFilter:
    """
    Filter to remove outlier positions.
    
    Uses statistical methods to detect and remove anomalous readings.
    """
    
    def __init__(self, threshold: float = 3.0):
        """
        Initialize outlier filter.
        
        Args:
            threshold: Standard deviation threshold for outlier detection
        """
        self.threshold = threshold
        self.history = deque(maxlen=10)
    
    def is_outlier(self, value: float) -> bool:
        """
        Check if value is an outlier.
        
        Args:
            value: Value to check
        
        Returns:
            True if outlier, False otherwise
        """
        if len(self.history) < 3:
            return False
        
        mean = np.mean(self.history)
        std = np.std(self.history)
        
        if std == 0:
            return False
        
        z_score = abs((value - mean) / std)
        return z_score > self.threshold
    
    def update(self, value: float) -> float:
        """
        Update filter and return filtered value.
        
        Args:
            value: New value
        
        Returns:
            Filtered value (original or median of history if outlier)
        """
        if self.is_outlier(value):
            # Return median of history instead
            if self.history:
                return float(np.median(self.history))
        
        self.history.append(value)
        return value
    
    def reset(self):
        """Reset history."""
        self.history.clear()
