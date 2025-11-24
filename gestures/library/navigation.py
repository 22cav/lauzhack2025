"""
Navigation Gestures

Implementation of navigation gestures (Pinch, V-Gesture) with Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, "../../.."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, Optional
from pydantic import BaseModel
import mediapipe as mp

from gestures.detector import Gesture, GestureResult
from gestures.landmarks import (
    HandLandmarkIndices,
    calculate_distance,
    calculate_distance_squared,
    is_finger_extended,
    is_finger_curled
)
import config



class NavigationGesture(Gesture):
    """Base class for navigation gestures."""
    
    def __init__(self, name: str):
        self._name = name
        self.last_position: Optional[Dict[str, float]] = None
    
    @property
    def name(self) -> str:
        return self._name
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect navigation gesture.
        
        This method should be overridden by subclasses.
        """
        return None


class PinchGesture(NavigationGesture):
    """
    Pinch gesture for viewport rotation.
    
    Detects when thumb and index finger are pinched together,
    and tracks movement for rotation control.
    """
    
    def __init__(self):
        super().__init__(config.GESTURE_PINCH)
        self.pinch_threshold = 0.05  # Distance threshold for pinch detection
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect pinch gesture and calculate movement delta.
        
        Criteria:
        - Thumb tip and index tip must be close together (within threshold)
        - Other fingers should be curled or at least not interfering
        - Movement is tracked when pinch is maintained
        
        Args:
            landmarks: MediaPipe hand landmarks
            context: Context dictionary with previous frame data
            
        Returns:
            GestureResult with dx, dy data if pinching, None otherwise
        """
        # Get thumb and index finger tips
        thumb_tip = landmarks[HandLandmarkIndices.THUMB_TIP]
        index_tip = landmarks[HandLandmarkIndices.INDEX_FINGER_TIP]
        
        # Calculate 3D distance between thumb and index
        distance_3d = calculate_distance(thumb_tip, index_tip)
        
        # Also check 2D distance (x, y only) for better robustness
        # Sometimes z-depth can be noisy
        dx_2d = thumb_tip.x - index_tip.x
        dy_2d = thumb_tip.y - index_tip.y
        distance_2d = (dx_2d * dx_2d + dy_2d * dy_2d) ** 0.5
        
        # Check if pinched - use 3D distance primarily, 2D as backup
        is_pinched = distance_3d < self.pinch_threshold or distance_2d < (self.pinch_threshold * 0.8)
        
        if not is_pinched:
            self.last_position = None
            return None
        
        # Additional check: middle finger should not be too close (avoid confusion with other gestures)
        middle_tip = landmarks[HandLandmarkIndices.MIDDLE_FINGER_TIP]
        middle_to_thumb = calculate_distance(middle_tip, thumb_tip)
        
        # If middle finger is also very close to thumb, this might be a different gesture
        if middle_to_thumb < self.pinch_threshold * 0.9:
            self.last_position = None
            return None
        
        # Calculate center of pinch
        center_x = (thumb_tip.x + index_tip.x) / 2
        center_y = (thumb_tip.y + index_tip.y) / 2
        
        # Calculate movement delta
        dx, dy = 0.0, 0.0
        if self.last_position is not None:
            dx = center_x - self.last_position['x']
            dy = center_y - self.last_position['y']
            
            # Add noise filtering: ignore very small movements (jitter)
            movement_magnitude = (dx * dx + dy * dy) ** 0.5
            if movement_magnitude < 0.002:  # Threshold for noise
                dx, dy = 0.0, 0.0
        
        # Update last position
        self.last_position = {'x': center_x, 'y': center_y}
        
        # Calculate confidence based on pinch tightness
        # Tighter pinch = higher confidence
        # Use normalized distance: pinch_threshold is max, 0 is perfect
        tightness = 1.0 - (distance_3d / self.pinch_threshold)
        confidence = max(0.6, min(1.0, 0.7 + tightness * 0.3))
        
        return GestureResult(
            name=self.name,
            confidence=confidence,
            data={
                'dx': dx,
                'dy': dy,
                'pinch_distance': distance_3d,
                'pinch_distance_2d': distance_2d,
                'center_x': center_x,
                'center_y': center_y,
                'tightness': tightness
            }
        )



class VGesture(NavigationGesture):
    """
    V-Gesture (peace sign) for viewport panning.
    
    Detects when index and middle fingers are extended in a V shape,
    and tracks their movement for camera panning.
    """
    
    def __init__(self):
        super().__init__(config.GESTURE_V_MOVE)
    
    def detect(self, landmarks: Any, context: Dict[str, Any]) -> Optional[GestureResult]:
        """
        Detect V-gesture and calculate movement delta.
        
        Criteria:
        - Index and middle fingers must be extended
        - Ring and pinky fingers must be curled
        - Thumb should be curled or neutral (not extended like palm)
        - Fingers should have decent separation (V shape)
        
        Args:
            landmarks: MediaPipe hand landmarks
            context: Context dictionary
            
        Returns:
            GestureResult with dx, dy data if V-gesture detected, None otherwise
        """
        wrist_idx = HandLandmarkIndices.WRIST
        
        # 1. Check if index and middle fingers are extended
        index_extended = is_finger_extended(
            landmarks, 
            HandLandmarkIndices.INDEX_FINGER_TIP, 
            HandLandmarkIndices.INDEX_FINGER_PIP, 
            wrist_idx
        )
        middle_extended = is_finger_extended(
            landmarks, 
            HandLandmarkIndices.MIDDLE_FINGER_TIP, 
            HandLandmarkIndices.MIDDLE_FINGER_PIP, 
            wrist_idx
        )
        
        if not (index_extended and middle_extended):
            self.last_position = None
            return None
        
        # 2. Check if ring and pinky are curled
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
        
        # V-gesture requires ring and pinky to be curled
        if not (ring_curled and pinky_curled):
            self.last_position = None
            return None
        
        # 3. Check thumb: should not be extended like in palm gesture
        # Thumb should be either curled or in neutral position
        thumb_tip = landmarks[HandLandmarkIndices.THUMB_TIP]
        thumb_mcp = landmarks[HandLandmarkIndices.THUMB_MCP]
        wrist = landmarks[wrist_idx]
        
        dist_thumb_tip = calculate_distance_squared(thumb_tip, wrist)
        dist_thumb_mcp = calculate_distance_squared(thumb_mcp, wrist)
        
        # If thumb is strongly extended (much farther than MCP), this might be palm
        # Allow some extension but not as much as a palm
        thumb_extension_ratio = dist_thumb_tip / (dist_thumb_mcp + 0.001)  # Avoid division by zero
        if thumb_extension_ratio > 2.0:  # Thumb is too extended
            self.last_position = None
            return None
        
        # 4. Calculate center point between index and middle fingertips
        index_tip = landmarks[HandLandmarkIndices.INDEX_FINGER_TIP]
        middle_tip = landmarks[HandLandmarkIndices.MIDDLE_FINGER_TIP]
        
        center_x = (index_tip.x + middle_tip.x) / 2
        center_y = (index_tip.y + middle_tip.y) / 2
        
        # 5. Calculate movement delta
        dx, dy = 0.0, 0.0
        if self.last_position is not None:
            dx = center_x - self.last_position['x']
            dy = center_y - self.last_position['y']
            
            # Add noise filtering: ignore very small movements (jitter)
            movement_magnitude = (dx * dx + dy * dy) ** 0.5
            if movement_magnitude < 0.002:  # Threshold for noise
                dx, dy = 0.0, 0.0
        
        # Update last position
        self.last_position = {'x': center_x, 'y': center_y}
        
        # 6. Calculate finger spread for confidence scoring
        finger_spread = calculate_distance(index_tip, middle_tip)
        
        # V-gesture should have good separation between fingers
        # Typical V spread: 0.05-0.15
        # Too close together: might be pointing gesture
        # Too far: might be transitioning to palm
        if finger_spread < 0.03:
            # Fingers too close - might be a different gesture
            confidence = 0.6
        elif finger_spread > 0.15:
            # Fingers too spread - might be transitioning
            confidence = 0.7
        else:
            # Good V shape
            # Normalize: 0.03-0.15 maps to 0.8-1.0 confidence
            spread_score = (finger_spread - 0.03) / 0.12
            confidence = 0.8 + (spread_score * 0.2)
        
        return GestureResult(
            name=self.name,
            confidence=min(1.0, max(0.6, confidence)),
            data={
                'dx': dx,
                'dy': dy,
                'center_x': center_x,
                'center_y': center_y,
                'finger_spread': finger_spread,
                'thumb_extension_ratio': thumb_extension_ratio
            }
        )

