"""
Navigation Hand Gestures

Strict, high-confidence gestures for navigation and control.
"""

import mediapipe as mp
import numpy as np
from typing import Dict, Any, Optional
from ..detector import Gesture, GestureResult
from ..registry import register

mp_holistic = mp.solutions.holistic


def get_extended_fingers(landmarks) -> list:
    """Return list of booleans for extended fingers [Index, Middle, Ring, Pinky]."""
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
    
    extended = []
    for tip, pip in zip(fingers, fingers_pip):
        # Simple y-check is often enough, but for strictness we can check distance from wrist
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        tip_dist = np.sqrt((landmarks.landmark[tip].x - wrist.x)**2 + (landmarks.landmark[tip].y - wrist.y)**2)
        pip_dist = np.sqrt((landmarks.landmark[pip].x - wrist.x)**2 + (landmarks.landmark[pip].y - wrist.y)**2)
        
        extended.append(tip_dist > pip_dist * 1.2) # Tip must be significantly further
    
    return extended


@register("navigation")
class VGesture(Gesture):
    """V-gesture with index and middle fingers for navigation movement."""
    
    @property
    def name(self) -> str:
        return "V_GESTURE"
    
    @property
    def priority(self) -> int:
        return 10
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = get_extended_fingers(landmarks)
        # Index and Middle extended, Ring and Pinky closed
        if extended != [True, True, False, False]:
            return None
        
        # Check Ring and Pinky are closed
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        ring_tip = landmarks.landmark[mp_holistic.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP]
        
        if np.sqrt((ring_tip.x - wrist.x)**2 + (ring_tip.y - wrist.y)**2) > 0.2:
            return None
        if np.sqrt((pinky_tip.x - wrist.x)**2 + (pinky_tip.y - wrist.y)**2) > 0.2:
            return None
        
        # Calculate V center position (midpoint between index and middle tips)
        index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP]
        
        v_center = {
            'x': (index_tip.x + middle_tip.x) / 2,
            'y': (index_tip.y + middle_tip.y) / 2
        }
        
        return GestureResult(
            name=self.name,
            confidence=0.9,
            data={'position': v_center}
        )


@register("navigation")
class OpenPalm(Gesture):
    """Strict Open Palm (Play)."""
    
    @property
    def name(self) -> str:
        return "OPEN_PALM"
    
    @property
    def priority(self) -> int:
        return 10
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = get_extended_fingers(landmarks)
        # All 4 fingers extended + Thumb extended check
        if not all(extended):
            return None
            
        # Check thumb extension
        thumb_tip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_IP]
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        
        thumb_dist = np.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)
        thumb_ip_dist = np.sqrt((thumb_ip.x - wrist.x)**2 + (thumb_ip.y - wrist.y)**2)
        
        if thumb_dist > thumb_ip_dist * 1.1:
            # Check spread
            pinky_tip = landmarks.landmark[mp_holistic.HandLandmark.PINKY_TIP]
            index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
            spread = np.sqrt((index_tip.x - pinky_tip.x)**2 + (index_tip.y - pinky_tip.y)**2)
            
            if spread > 0.15: # Strict spread
                return GestureResult(name=self.name, confidence=1.0)
        
        return None


@register("navigation")
class ClosedFist(Gesture):
    """Strict Closed Fist (Stop)."""
    
    @property
    def name(self) -> str:
        return "CLOSED_FIST"
    
    @property
    def priority(self) -> int:
        return 10
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        extended = get_extended_fingers(landmarks)
        # All 4 fingers NOT extended
        if any(extended):
            return None
            
        # Check compactness
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        middle_tip = landmarks.landmark[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP]
        
        dist = np.sqrt((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)
        
        if dist < 0.15: # Strict compactness
            return GestureResult(name=self.name, confidence=1.0)
            
        return None


@register("navigation")
class Pinch(Gesture):
    """Strict Pinch."""
    
    @property
    def name(self) -> str:
        return "PINCH"
    
    @property
    def priority(self) -> int:
        return 15 # Higher than others
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        thumb_tip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2 +
            (thumb_tip.z - index_tip.z) ** 2
        )
        
        if distance < 0.06: # Relaxed threshold for easier pinch detection
            confidence = max(0.7, 1.0 - (distance / 0.06)) # Scale confidence based on distance
            return GestureResult(name=self.name, confidence=confidence, data={'position': {'x': (thumb_tip.x+index_tip.x)/2, 'y': (thumb_tip.y+index_tip.y)/2}})
            
        return None
