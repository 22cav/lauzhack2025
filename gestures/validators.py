"""
Gesture Validators

Validation logic for gestures with Pydantic models.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class HandLandmark(BaseModel):
    """
    Single hand landmark.
    """
    x: float
    y: float
    z: float
    visibility: float = 0.0


class HandData(BaseModel):
    """
    Complete hand data structure.
    """
    landmarks: List[HandLandmark]
    handedness: str  # "Left" or "Right"
    score: float


class ValidatorConfig(BaseModel):
    """
    Configuration for validators.
    """
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)
    require_two_hands: bool = False


class GestureValidator:
    """
    Validates detected gestures against rules.
    """
    
    def __init__(self, config: ValidatorConfig):
        self.config = config
        
    def validate(self, gesture_name: str, hand_data: Any) -> bool:
        """
        Validate a gesture.
        
        Args:
            gesture_name: Name of gesture
            hand_data: MediaPipe hand data (raw or processed)
            
        Returns:
            bool: True if valid
        """
        # 1. Check if hand_data exists
        if hand_data is None:
            return False
        
        # 2. Check if multi_hand_landmarks exists (MediaPipe format)
        if hasattr(hand_data, 'multi_hand_landmarks'):
            landmarks_list = hand_data.multi_hand_landmarks
            
            # Check if any hands are detected
            if not landmarks_list or len(landmarks_list) == 0:
                return False
            
            # 3. Validate number of hands based on gesture requirements
            if self.config.require_two_hands and len(landmarks_list) < 2:
                return False
            
            # 4. Check landmarks quality - ensure all landmarks are present
            for hand_landmarks in landmarks_list:
                if not hand_landmarks or not hand_landmarks.landmark:
                    return False
                
                # MediaPipe hands should have 21 landmarks
                if len(hand_landmarks.landmark) != 21:
                    return False
                
                # 5. Check landmark visibility/presence (z-depth shouldn't be extreme)
                for lm in hand_landmarks.landmark:
                    # Extreme z values suggest poor tracking
                    if abs(lm.z) > 0.5:  # Heuristic threshold
                        return False
                    
                    # Coordinates should be normalized (0-1 range typically)
                    # Allow some margin for edge cases
                    if lm.x < -0.5 or lm.x > 1.5 or lm.y < -0.5 or lm.y > 1.5:
                        return False
        
        # 6. Gesture-specific validation rules
        # These can be extended based on gesture type
        gesture_validators = {
            'PINCH_DRAG': self._validate_pinch,
            'V_GESTURE_MOVE': self._validate_v_gesture,
            'OPEN_PALM': self._validate_palm,
            'CLOSED_FIST': self._validate_fist,
        }
        
        validator_func = gesture_validators.get(gesture_name)
        if validator_func:
            return validator_func(hand_data)
        
        # Default: pass validation if no specific rules
        return True
    
    def _validate_pinch(self, hand_data: Any) -> bool:
        """Validate pinch gesture - requires single hand."""
        if hasattr(hand_data, 'multi_hand_landmarks'):
            # Pinch works best with single hand
            return len(hand_data.multi_hand_landmarks) == 1
        return True
    
    def _validate_v_gesture(self, hand_data: Any) -> bool:
        """Validate V-gesture - requires single hand."""
        if hasattr(hand_data, 'multi_hand_landmarks'):
            # V-gesture works with single hand
            return len(hand_data.multi_hand_landmarks) == 1
        return True
    
    def _validate_palm(self, hand_data: Any) -> bool:
        """Validate palm gesture - can work with one or two hands."""
        # No specific constraints beyond basic validation
        return True
    
    def _validate_fist(self, hand_data: Any) -> bool:
        """Validate fist gesture - can work with one or two hands."""
        # No specific constraints beyond basic validation
        return True
