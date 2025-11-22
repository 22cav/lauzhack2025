"""
Validators for Gesture Quality and Confidence

Provides validation logic for ensuring gesture detection quality.
"""

from typing import Optional, List
import numpy as np
import logging
from .detector import GestureResult

logger = logging.getLogger(__name__)


class ConfidenceValidator:
    """
    Validates gesture confidence scores.
    
    Ensures gestures meet minimum quality thresholds before acceptance.
    """
    
    def __init__(self, min_confidence: float = 0.5, stability_frames: int = 3):
        """
        Initialize validator.
        
        Args:
            min_confidence: Minimum confidence threshold
            stability_frames: Number of consecutive frames required for stability
        """
        self.min_confidence = min_confidence
        self.stability_frames = stability_frames
        self.gesture_history: List[Optional[str]] = []
    
    def validate(self, result: Optional[GestureResult]) -> bool:
        """
        Validate a gesture result.
        
        Args:
            result: GestureResult to validate
        
        Returns:
            True if valid, False otherwise
        """
        if result is None:
            return False
        
        # Check confidence threshold
        if result.confidence < self.min_confidence:
            return False
        
        # Check stability (same gesture detected for N frames)
        self.gesture_history.append(result.name)
        if len(self.gesture_history) > self.stability_frames:
            self.gesture_history.pop(0)
        
        # Require last N detections to be the same gesture
        if len(self.gesture_history) >= self.stability_frames:
            if len(set(self.gesture_history)) == 1:  # All same
                return True
            return False
        
        # Not enough history yet
        return False
    
    def reset(self):
        """Reset validator state."""
        self.gesture_history.clear()


class QualityValidator:
    """
    Validates landmark quality based on visibility and presence.
    
    Ensures landmarks are well-tracked before attempting gesture detection.
    """
    
    def __init__(self, min_visibility: float = 0.1, min_presence: float = 0.1):
        """
        Initialize quality validator.
        
        Args:
            min_visibility: Minimum average visibility score (0.0-1.0) - LOWERED from 0.5
            min_presence: Minimum average presence score (0.0-1.0) - LOWERED from 0.5
        """
        self.min_visibility = min_visibility
        self.min_presence = min_presence
    
    def validate(self, landmarks) -> bool:
        """
        Validate landmark quality.
        
        Args:
            landmarks: MediaPipe hand landmarks
        
        Returns:
            True if quality is sufficient, False otherwise
        """
        if landmarks is None:
            return False
        
        # MediaPipe Hands (21 landmarks) does not provide visibility/presence scores
        # so we skip this check for hands to avoid false negatives
        if len(landmarks.landmark) == 21:
            return True
        
        # Calculate average visibility and presence
        total_visibility = 0.0
        total_presence = 0.0
        count = 0
        
        for landmark in landmarks.landmark:
            # Hand landmarks don't always have visibility/presence, so default to 1.0
            if hasattr(landmark, 'visibility'):
                total_visibility += landmark.visibility
            else:
                total_visibility += 1.0
                
            if hasattr(landmark, 'presence'):
                total_presence += landmark.presence
            else:
                total_presence += 1.0
                
            count += 1
        
        if count == 0:
            return False
        
        avg_visibility = total_visibility / count
        avg_presence = total_presence / count
        
        # Very permissive thresholds - just need basic tracking
        return avg_visibility >= self.min_visibility and avg_presence >= self.min_presence
    
    def get_quality_score(self, landmarks) -> float:
        """
        Get overall quality score for landmarks.
        
        Args:
            landmarks: MediaPipe hand landmarks
        
        Returns:
            Quality score 0.0-1.0
        """
        if landmarks is None:
            return 0.0
        
        scores = []
        
        # Visibility scores
        visibilities = [lm.visibility for lm in landmarks.landmark if hasattr(lm, 'visibility')]
        if visibilities:
            scores.append(np.mean(visibilities))
        
        # Presence scores  
        presences = [lm.presence for lm in landmarks.landmark if hasattr(lm, 'presence')]
        if presences:
            scores.append(np.mean(presences))
        
        return np.mean(scores) if scores else 0.0


class TemporalValidator:
    """
    Validates gesture temporal consistency.
    
    Ensures gestures are held for minimum duration before accepting.
    """
    
    def __init__(self, min_duration: float = 0.1):
        """
        Initialize temporal validator.
        
        Args:
            min_duration: Minimum gesture duration in seconds
        """
        self.min_duration = min_duration
        self.current_gesture = None
        self.gesture_start_time = None
    
    def validate(self, result: Optional[GestureResult], current_time: float) -> bool:
        """
        Validate gesture has been held long enough.
        
        Args:
            result: GestureResult to validate
            current_time: Current timestamp
        
        Returns:
            True if gesture held long enough, False otherwise
        """
        if result is None:
            self.current_gesture = None
            self.gesture_start_time = None
            return False
        
        # New gesture started
        if result.name != self.current_gesture:
            self.current_gesture = result.name
            self.gesture_start_time = current_time
            return False
        
        # Same gesture continuing
        if self.gesture_start_time is None:
            self.gesture_start_time = current_time
            return False
        
        duration = current_time - self.gesture_start_time
        return duration >= self.min_duration
    
    def reset(self):
        """Reset validator state."""
        self.current_gesture = None
        self.gesture_start_time = None
