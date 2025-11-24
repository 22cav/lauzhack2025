"""
Basic Gestures

Implementation of basic gestures (Palm, Fist) with Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "../../.."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, Optional
import mediapipe as mp

from gestures.detector import Gesture, GestureResult
from gestures.landmarks import (
    HandLandmarkIndices,
    FINGER_TIPS, 
    calculate_distance_squared,
    is_finger_extended,
    is_finger_curled,
    get_finger_spread
)
import config



class BasicGesture(Gesture):
    """
    Base class for basic static gestures.
    """
    
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Method to be implemented by subclasses.
        """
        raise NotImplementedError

class OpenPalmGesture(BasicGesture):
    """
    Open Palm Gesture.
    """
    def __init__(self):
        super().__init__(config.GESTURE_PALM)

    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect open palm gesture.
        
        Criteria:
        - All 5 fingers must be extended
        - Fingers should be spread apart (higher confidence)
        
        Args:
            landmarks: MediaPipe landmarks
            context: Context dictionary
            
        Returns:
            GestureResult if detected, None otherwise
        """
        wrist_idx = HandLandmarkIndices.WRIST
        
        # 1. Check if all fingers are extended
        finger_checks = [
            (HandLandmarkIndices.INDEX_FINGER_TIP, HandLandmarkIndices.INDEX_FINGER_PIP),
            (HandLandmarkIndices.MIDDLE_FINGER_TIP, HandLandmarkIndices.MIDDLE_FINGER_PIP),
            (HandLandmarkIndices.RING_FINGER_TIP, HandLandmarkIndices.RING_FINGER_PIP),
            (HandLandmarkIndices.PINKY_TIP, HandLandmarkIndices.PINKY_PIP),
        ]
        
        extended_count = 0
        for tip_idx, pip_idx in finger_checks:
            if is_finger_extended(landmarks, tip_idx, pip_idx, wrist_idx):
                extended_count += 1
        
        # 2. Check thumb separately (different joint structure)
        thumb_tip = landmarks.landmark[HandLandmarkIndices.THUMB_TIP]
        thumb_mcp = landmarks.landmark[HandLandmarkIndices.THUMB_MCP]
        wrist = landmarks.landmark[wrist_idx]
        
        dist_thumb_tip = calculate_distance_squared(thumb_tip, wrist)
        dist_thumb_mcp = calculate_distance_squared(thumb_mcp, wrist)
        
        thumb_extended = dist_thumb_tip > dist_thumb_mcp
        if thumb_extended:
            extended_count += 1
        
        # All 5 fingers must be extended
        if extended_count < 5:
            return None
        
        # 3. Calculate finger spread for confidence scoring
        spread = get_finger_spread(landmarks, FINGER_TIPS)
        
        # Normalize spread score: typical palm spread is around 0.3-0.5
        # Higher spread = higher confidence
        spread_score = min(spread / 0.4, 1.0)
        
        # Base confidence of 0.7, boost up to 1.0 with good spread
        confidence = 0.7 + (spread_score * 0.3)
        
        return GestureResult(
            name=self.name,
            confidence=confidence,
            data={
                "extended_fingers": extended_count, 
                "spread": spread,
                "spread_score": spread_score
            }
        )



class ClosedFistGesture(BasicGesture):
    """
    Closed Fist Gesture.
    """
    def __init__(self):
        super().__init__(config.GESTURE_FIST)

    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect closed fist gesture.
        
        Criteria:
        - All 4 fingers (index, middle, ring, pinky) must be curled
        - Thumb should be tucked in or curled
        
        Args:
            landmarks: MediaPipe landmarks
            context: Context dictionary
            
        Returns:
            GestureResult if detected, None otherwise
        """
        wrist_idx = HandLandmarkIndices.WRIST
        
        # 1. Check if all fingers are curled
        finger_checks = [
            (HandLandmarkIndices.INDEX_FINGER_TIP, HandLandmarkIndices.INDEX_FINGER_PIP),
            (HandLandmarkIndices.MIDDLE_FINGER_TIP, HandLandmarkIndices.MIDDLE_FINGER_PIP),
            (HandLandmarkIndices.RING_FINGER_TIP, HandLandmarkIndices.RING_FINGER_PIP),
            (HandLandmarkIndices.PINKY_TIP, HandLandmarkIndices.PINKY_PIP),
        ]
        
        curled_count = 0
        for tip_idx, pip_idx in finger_checks:
            if is_finger_curled(landmarks, tip_idx, pip_idx, wrist_idx):
                curled_count += 1
        
        # All 4 fingers must be curled
        if curled_count < 4:
            return None
        
        # 2. Check thumb: should be tucked or curled
        # For fist, thumb is usually curled over fingers or tucked at side
        thumb_tip = landmarks.landmark[HandLandmarkIndices.THUMB_TIP]
        index_mcp = landmarks.landmark[HandLandmarkIndices.INDEX_FINGER_MCP]
        middle_mcp = landmarks.landmark[HandLandmarkIndices.MIDDLE_FINGER_MCP]
        
        # Check distance to index and middle MCP (thumb should be close to hand body)
        dist_to_index = calculate_distance_squared(thumb_tip, index_mcp)
        dist_to_middle = calculate_distance_squared(thumb_tip, middle_mcp)
        
        # Threshold for "close" - empirically determined
        # Thumb tip should be within ~0.05 distance (squared: 0.0025) to hand body
        thumb_tucked_threshold = 0.06  # Generous threshold for robustness
        
        thumb_curled = (dist_to_index < thumb_tucked_threshold or 
                       dist_to_middle < thumb_tucked_threshold)
        
        if not thumb_curled:
            return None
        
        # Calculate confidence based on how tightly curled the fist is
        # Tighter curl = smaller average distance from fingertips to wrist
        wrist = landmarks.landmark[wrist_idx]
        total_tip_distance = 0.0
        
        for tip_idx, _ in finger_checks:
            tip = landmarks.landmark[tip_idx]
            total_tip_distance += calculate_distance_squared(tip, wrist)
        
        avg_tip_distance = total_tip_distance / len(finger_checks)
        
        # Normalize confidence: tighter fist has lower avg distance
        # Typical fist: avg_tip_distance ~ 0.01-0.04
        # Looser curl: avg_tip_distance ~ 0.05-0.08
        if avg_tip_distance < 0.03:
            confidence = 1.0  # Very tight fist
        elif avg_tip_distance < 0.05:
            confidence = 0.9
        else:
            confidence = 0.75  # Looser fist but still valid
        
        return GestureResult(
            name=self.name,
            confidence=confidence,
            data={
                "curled_fingers": curled_count, 
                "thumb_curled": thumb_curled,
                "avg_tip_distance": avg_tip_distance
            }
        )
