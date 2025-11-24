"""
Advanced Gestures

Implementation of advanced gestures (Pointing, Thumbs Up) with robust detection.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "../../.."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, Optional
from gestures.detector import Gesture, GestureResult
from gestures.landmarks import (
    HandLandmarkIndices,
    calculate_distance,
    calculate_distance_squared,
    is_finger_extended,
    is_finger_curled
)


class AdvancedGesture(Gesture):
    """Base class for advanced gestures."""
    
    def __init__(self, name: str):
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name
        
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        return None


class PointingGesture(AdvancedGesture):
    """
    Pointing Gesture (Index finger extended, others curled).
    
    Criteria:
    - Index finger extended
    - Middle, ring, and pinky curled
    - Thumb can be extended or curled
    """
    
    def __init__(self):
        super().__init__("POINTING")
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect pointing gesture.
        
        Args:
            landmarks: MediaPipe landmarks
            context: Context dictionary
            
        Returns:
            GestureResult if detected, None otherwise
        """
        wrist_idx = HandLandmarkIndices.WRIST
        
        # 1. Index must be extended
        index_extended = is_finger_extended(
            landmarks,
            HandLandmarkIndices.INDEX_FINGER_TIP,
            HandLandmarkIndices.INDEX_FINGER_PIP,
            wrist_idx
        )
        
        if not index_extended:
            return None
        
        # 2. Middle, ring, and pinky must be curled
        middle_curled = is_finger_curled(
            landmarks,
            HandLandmarkIndices.MIDDLE_FINGER_TIP,
            HandLandmarkIndices.MIDDLE_FINGER_PIP,
            wrist_idx
        )
        ring_curled = is_finger_curled(
            landmarks,
            HandLandmarkIndices.RING_FINGER_TIP,
            HandLandmarkIndices.RING_FINGER_PIP,
            wrist_idx
        )
        pinky_curled = is_finger_curled(
            landmarks,
            HandLandmarkIndices.PINKY_TIP,
            HandLandmarkIndices.PINKY_PIP,
            wrist_idx
        )
        
        if not (middle_curled and ring_curled and pinky_curled):
            return None
        
        # 3. Calculate index finger straightness for confidence
        # More straight = higher confidence
        index_tip = landmarks[HandLandmarkIndices.INDEX_FINGER_TIP]
        index_mcp = landmarks[HandLandmarkIndices.INDEX_FINGER_MCP]
        index_pip = landmarks[HandLandmarkIndices.INDEX_FINGER_PIP]
        
        # Distance from tip to MCP should be larger than typical bent finger
        tip_to_mcp_dist = calculate_distance(index_tip, index_mcp)
        pip_to_mcp_dist = calculate_distance(index_pip, index_mcp)
        
        # Straightness ratio: closer to 2.0 means straighter
        straightness_ratio = tip_to_mcp_dist / (pip_to_mcp_dist + 0.001)
        
        # Typical straight finger: ratio ~1.8-2.2
        # Bent finger: ratio ~1.2-1.5
        if straightness_ratio < 1.5:
            confidence = 0.7
        elif straightness_ratio < 1.8:
            confidence = 0.85
        else:
            confidence = 1.0
        
        return GestureResult(
            name=self.name,
            confidence=confidence,
            data={
                "straightness_ratio": straightness_ratio,
                "index_extended": index_extended
            }
        )


class ThumbsUpGesture(AdvancedGesture):
    """
    Thumbs Up Gesture.
    
    Criteria:
    - Thumb extended upward
    - All other fingers curled
    - Wrist orientation matters (thumb should be pointing up, not sideways)
    """
    
    def __init__(self):
        super().__init__("THUMBS_UP")
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect thumbs up gesture.
        
        Args:
            landmarks: MediaPipe landmarks
            context: Context dictionary
            
        Returns:
            GestureResult if detected, None otherwise
        """
        wrist_idx = HandLandmarkIndices.WRIST
        wrist = landmarks[wrist_idx]
        
        # 1. Thumb must be extended
        thumb_tip = landmarks[HandLandmarkIndices.THUMB_TIP]
        thumb_mcp = landmarks[HandLandmarkIndices.THUMB_MCP]
        
        dist_thumb_tip = calculate_distance_squared(thumb_tip, wrist)
        dist_thumb_mcp = calculate_distance_squared(thumb_mcp, wrist)
        
        thumb_extended = dist_thumb_tip > dist_thumb_mcp
        
        if not thumb_extended:
            return None
        
        # 2. Thumb should be pointing upward (y coordinate)
        # In MediaPipe, lower y = higher on screen
        # Thumb tip should be above (lower y) than MCP
        if thumb_tip.y > thumb_mcp.y:
            # Thumb pointing down or sideways
            return None
        
        # 3. All fingers must be curled
        fingers_curled = 0
        finger_checks = [
            (HandLandmarkIndices.INDEX_FINGER_TIP, HandLandmarkIndices.INDEX_FINGER_PIP),
            (HandLandmarkIndices.MIDDLE_FINGER_TIP, HandLandmarkIndices.MIDDLE_FINGER_PIP),
            (HandLandmarkIndices.RING_FINGER_TIP, HandLandmarkIndices.RING_FINGER_PIP),
            (HandLandmarkIndices.PINKY_TIP, HandLandmarkIndices.PINKY_PIP),
        ]
        
        for tip_idx, pip_idx in finger_checks:
            if is_finger_curled(landmarks, tip_idx, pip_idx, wrist_idx):
                fingers_curled += 1
        
        # All 4 fingers must be curled
        if fingers_curled < 4:
            return None
        
        # 4. Calculate thumb verticality for confidence
        # More vertical = higher confidence
        thumb_vertical_offset = abs(thumb_mcp.y - thumb_tip.y)
        thumb_horizontal_offset = abs(thumb_mcp.x - thumb_tip.x)
        
        # Vertical to horizontal ratio
        # Higher ratio = more vertical
        verticality_ratio = thumb_vertical_offset / (thumb_horizontal_offset + 0.001)
        
        if verticality_ratio > 2.0:
            confidence = 1.0  # Very vertical
        elif verticality_ratio > 1.5:
            confidence = 0.9
        else:
            confidence = 0.75
        
        return GestureResult(
            name=self.name,
            confidence=confidence,
            data={
                "verticality_ratio": verticality_ratio,
                "fingers_curled": fingers_curled,
                "thumb_extended": thumb_extended
            }
        )
