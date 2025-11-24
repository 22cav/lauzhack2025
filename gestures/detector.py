"""
Gesture Detector

Core gesture detection logic.
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import config

@dataclass
class GestureResult:
    """Result of a gesture detection."""
    name: str
    confidence: float
    data: Dict[str, Any]

class Gesture:
    """Abstract base class for gestures."""
    
    @property
    def name(self) -> str:
        raise NotImplementedError
        
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        raise NotImplementedError

class GestureDetector:
    """
    Manages multiple gestures and detects the best match.
    """
    
    def __init__(self, min_confidence: float = 0.5):
        self.gestures: List[Gesture] = []
        self.min_confidence = min_confidence
        
        # Hysteresis state
        self.history_size = config.TUNING_CONFIG.get("engine", {}).get("hysteresis_frames", 2)
        self.gesture_history = []  # List of detected gesture names
        self.last_confirmed_gesture = None

    def register(self, gesture: Gesture):
        """Register a new gesture."""
        self.gestures.append(gesture)

    def detect_best(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect the single best gesture from the list.
        Applies hysteresis to prevent flickering.
        """
        best_result = None
        max_confidence = 0.0
        
        # 1. Find best raw detection for this frame
        for gesture in self.gestures:
            try:
                result = gesture.detect(landmarks, context)
                if result and result.confidence >= self.min_confidence:
                    if result.confidence > max_confidence:
                        max_confidence = result.confidence
                        best_result = result
            except Exception as e:
                logging.error(f"Error detecting gesture {gesture.name}: {e}")
        
        # 2. Update History
        current_gesture_name = best_result.name if best_result else "None"
        self.gesture_history.append(current_gesture_name)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
            
        # 3. Apply Hysteresis
        # Check if the history is consistent
        # All frames in history must match the current gesture to switch
        is_consistent = all(name == current_gesture_name for name in self.gesture_history)
        
        if is_consistent:
            self.last_confirmed_gesture = current_gesture_name
            return best_result
        else:
            # If not consistent, stick to the last confirmed gesture if possible
            # But we can't return a result object if we don't have one for the current frame
            # So we might return None or the best result but with lower confidence?
            # Strategy: If the current best result matches the last confirmed, return it.
            # If it's different, return None (stabilizing period).
            if best_result and best_result.name == self.last_confirmed_gesture:
                return best_result
            return None
