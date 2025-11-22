"""
Basic Hand Gestures

Simple, single-hand gestures for common actions.
"""

import mediapipe as mp
import numpy as np
from typing import Dict, Any, Optional
from ..detector import Gesture, GestureResult
from ..registry import register

mp_holistic = mp.solutions.holistic


def count_extended_fingers(landmarks) -> int:
    """Count number of extended fingers (excluding thumb)."""
    fingers = [
        mp_holistic.HandLandmark.INDEX_FINGER_TIP,
        mp_holistic.HandLandmark.MIDDLE_FINGER_TIP,
        mp_holistic.HandLandmark.RING_FINGER_TIP,
        mp_holistic.HandLandmark.PINKY_TIP
    ]
    
    fingers_pip = [
        mp_holistic.HandLandmark.INDEX_FINGER_PIP,
        mp_holistic.HandLandmark.MIDDLE_FINGER_PIP,
        mp_holistic.HandLandmark.RING_FINGER_PIP,
        mp_holistic.HandLandmark.PINKY_PIP
    ]
    
    extended = 0
    for tip, pip in zip(fingers, fingers_pip):
        if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
            extended += 1
    
    return extended


@register("basic")
class OpenPalm(Gesture):
    """All four fingers extended (palm open)."""
    
    @property
    def name(self) -> str:
        return "OPEN_PALM"
    
    @property
    def priority(self) -> int:
        return 5
    
    @property
    def description(self) -> str:
        return "Open palm with all fingers extended"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = count_extended_fingers(landmarks)
        
        if extended == 4:
            # Check fingers are spread (not closed)
            index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
            pinky_tip = landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP]
            spread = abs(index_tip.x - pinky_tip.x)
            
            confidence = min(1.0, spread * 5)  # More spread = higher confidence
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'extended_fingers': extended, 'spread': spread}
            )
        
        return None


@register("basic")
class ClosedFist(Gesture):
    """All fingers closed (fist)."""
    
    @property
    def name(self) -> str:
        return "CLOSED_FIST"
    
    @property
    def priority(self) -> int:
        return 5
    
    @property
    def description(self) -> str:
        return "Closed fist with all fingers down"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = count_extended_fingers(landmarks)
        
        if extended == 0:
            # Check fist is compact
            index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
            wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
            compactness = np.sqrt(
                (index_tip.x - wrist.x) ** 2 +
                (index_tip.y - wrist.y) ** 2
            )
            
            # Smaller distance = more compact = higher confidence
            confidence = max(0.0, 1.0 - compactness * 3)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'extended_fingers': extended, 'compactness': compactness}
            )
        
        return None


@register("basic")
class Pointing(Gesture):
    """Index finger extended, others closed."""
    
    @property
    def name(self) -> str:
        return "POINTING"
    
    @property
    def priority(self) -> int:
        return 6
    
    @property
    def description(self) -> str:
        return "Pointing with index finger"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = count_extended_fingers(landmarks)
        
        if extended == 1:
            # Check it's the index finger
            index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
            index_pip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_PIP]
            
            if index_tip.y < index_pip.y:
                # Calculate pointing direction
                index_mcp = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_MCP]
                direction_x = index_tip.x - index_mcp.x
                direction_y = index_tip.y - index_mcp.y
                
                # Confidence based on finger extension
                extension = np.sqrt(direction_x**2 + direction_y**2)
                confidence = min(1.0, extension * 3)
                
                return GestureResult(
                    name=self.name,
                    confidence=confidence,
                    data={
                        'direction': {'x': direction_x, 'y': direction_y},
                        'extension': extension
                    }
                )
        
        return None


@register("basic")
class PeaceSign(Gesture):
    """Index and middle fingers extended (V sign)."""
    
    @property
    def name(self) -> str:
        return "PEACE_SIGN"
    
    @property
    def priority(self) -> int:
        return 6
    
    @property
    def description(self) -> str:
        return "Peace sign (V) with two fingers"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = count_extended_fingers(landmarks)
        
        if extended == 2:
            # Check it's index and middle fingers
            index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
            index_pip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_PIP]
            middle_tip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP]
            middle_pip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_PIP]
            
            index_extended = index_tip.y < index_pip.y
            middle_extended = middle_tip.y < middle_pip.y
            
            if index_extended and middle_extended:
                # Measure V angle (spread)
                spread = abs(index_tip.x - middle_tip.x)
                confidence = min(1.0, spread * 8)
                
                return GestureResult(
                    name=self.name,
                    confidence=confidence,
                    data={'spread': spread}
                )
        
        return None


@register("basic")
class ThumbsUp(Gesture):
    """Thumb extended, other fingers closed."""
    
    @property
    def name(self) -> str:
        return "THUMBS_UP"
    
    @property
    def priority(self) -> int:
        return 7
    
    @property
    def description(self) -> str:
        return "Thumbs up gesture"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = count_extended_fingers(landmarks)
        
        if extended == 0:
            # Check thumb is up
            thumb_tip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
            thumb_mcp = landmarks.landmark[mp_holistic.HandLandmark.THUMB_CMC]
            wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
            
            # Thumb should be above wrist
            thumb_up = thumb_tip.y < wrist.y
            
            if thumb_up:
                # Calculate how far up
                height = wrist.y - thumb_tip.y
                confidence = min(1.0, height * 5)
                
                return GestureResult(
                    name=self.name,
                    confidence=confidence,
                    data={'height': height}
                )
        
        return None


@register("basic")
class RockOn(Gesture):
    """Index and pinky extended (rock/metal sign)."""
    
    @property
    def name(self) -> str:
        return "ROCK_ON"
    
    @property
    def priority(self) -> int:
        return 6
    
    @property
    def description(self) -> str:
        return "Rock on / metal horns gesture"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        # Check index extended
        index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_PIP]
        index_extended = index_tip.y < index_pip.y
        
        # Check pinky extended
        pinky_tip = landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks.landmark[mp_holistic.HandLandmark.PINKY_PIP]
        pinky_extended = pinky_tip.y < pinky_pip.y
        
        # Check middle and ring closed
        middle_tip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_PIP]
        middle_closed = middle_tip.y >= middle_pip.y
        
        if index_extended and pinky_extended and middle_closed:
            # Measure spread
            spread = abs(index_tip.x - pinky_tip.x)
            confidence = min(1.0, spread * 3)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'spread': spread}
            )
        
        return None
