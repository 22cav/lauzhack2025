"""
Advanced Hand Gestures

Complex gestures involving movement, pinching, and directional actions.
"""

import mediapipe as mp
import numpy as np
import time
from typing import Dict, Any, Optional
from ..detector import Gesture, GestureResult
from ..registry import register

mp_holistic = mp.solutions.holistic


@register("advanced")
class Pinch(Gesture):
    """Thumb and index finger pinched together."""
    
    @property
    def name(self) -> str:
        return "PINCH"
    
    @property
    def priority(self) -> int:
        return 10  # High priority
    
    @property
    def description(self) -> str:
        return "Pinch thumb and index finger together"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        thumb_tip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        
        # Calculate 3D distance
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2 +
            (thumb_tip.z - index_tip.z) ** 2
        )
        
        # Pinch threshold
        threshold = 0.05
        
        if distance < threshold:
            # Confidence inversely proportional to distance
            confidence = 1.0 - (distance / threshold)
            
            # Get pinch position (midpoint)
            pinch_pos = {
                'x': (thumb_tip.x + index_tip.x) / 2,
                'y': (thumb_tip.y + index_tip.y) / 2,
                'z': (thumb_tip.z + index_tip.z) / 2
            }
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'distance': distance, 'position': pinch_pos}
            )
        
        return None


@register("advanced")
class PinchDrag(Gesture):
    """Pinching while moving hand (for dragging/rotating)."""
    
    @property
    def name(self) -> str:
        return "PINCH_DRAG"
    
    @property
    def priority(self) -> int:
        return 15  # Highest priority
    
    @property
    def description(self) -> str:
        return "Pinch and drag for viewport control"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        # First check if pinching
        thumb_tip = landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2 +
            (thumb_tip.z - index_tip.z) ** 2
        )
        
        if distance >= 0.05:
            return None  # Not pinching
        
        # Get wrist position for movement tracking
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = (wrist.x, wrist.y, wrist.z)
        
        # Check history for previous position
        history = context.get('history', [])
        if history:
            last_result = history[-1]
            if last_result.name == self.name and 'position' in last_result.data:
                last_pos = last_result.data['position']
                
                # Calculate delta
                delta = {
                    'dx': current_pos[0] - last_pos[0],
                    'dy': current_pos[1] - last_pos[1],
                    'dz': current_pos[2] - last_pos[2]
                }
                
                # Calculate speed
                speed = np.sqrt(delta['dx']**2 + delta['dy']**2 + delta['dz']**2)
                
                # Higher confidence if moving
                confidence = min(1.0, 0.7 + speed * 10)
                
                return GestureResult(
                    name=self.name,
                    confidence=confidence,
                    data={
                        'position': current_pos,
                        'delta': delta,
                        'speed': speed
                    }
                )
        
        # First frame of pinch drag
        return GestureResult(
            name=self.name,
            confidence=0.7,
            data={'position': current_pos, 'delta': {'dx': 0, 'dy': 0, 'dz': 0}}
        )


@register("advanced")
class SwipeLeft(Gesture):
    """Fast horizontal movement to the left."""
    
    @property
    def name(self) -> str:
        return "SWIPELEFT"
    
    @property
    def priority(self) -> int:
        return 8
    
    @property
    def description(self) -> str:
        return "Swipe hand quickly to the left"
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = (wrist.x, wrist.y)
        
        # Need history to detect movement
        history = context.get('history', [])
        if len(history) < 2:
            return None
        
        # Look at last few frames
        positions = []
        for i in range(min(5, len(history))):
            result = history[-(i+1)]
            if 'wrist_pos' in result.data:
                positions.append(result.data['wrist_pos'])
        
        if len(positions) < 2:
            return None
        
        # Calculate horizontal movement
        total_dx = current_pos[0] - positions[-1][0]
        
        # Swipe left means negative dx and fast
        if total_dx < -0.1:  # Moved left significantly
            # Check it's fast (happened in short time)
            speed = abs(total_dx)
            confidence = min(1.0, speed * 5)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'speed': speed, 'distance': total_dx, 'wrist_pos': current_pos}
            )
        
        return None


@register("advanced")
class SwipeRight(Gesture):
    """Fast horizontal movement to the right."""
    
    @property
    def name(self) -> str:
        return "SWIPE_RIGHT"
    
    @property
    def priority(self) -> int:
        return 8
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = (wrist.x, wrist.y)
        
        history = context.get('history', [])
        if len(history) < 2:
            return None
        
        positions = []
        for i in range(min(5, len(history))):
            result = history[-(i+1)]
            if 'wrist_pos' in result.data:
                positions.append(result.data['wrist_pos'])
        
        if len(positions) < 2:
            return None
        
        total_dx = current_pos[0] - positions[-1][0]
        
        if total_dx > 0.1:  # Moved right
            speed = abs(total_dx)
            confidence = min(1.0, speed * 5)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'speed': speed, 'distance': total_dx, 'wrist_pos': current_pos}
            )
        
        return None


@register("advanced")
class SwipeUp(Gesture):
    """Fast upward movement."""
    
    @property
    def name(self) -> str:
        return "SWIPE_UP"
    
    @property
    def priority(self) -> int:
        return 8
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = (wrist.x, wrist.y)
        
        history = context.get('history', [])
        if len(history) < 2:
            return None
        
        positions = []
        for i in range(min(5, len(history))):
            result = history[-(i+1)]
            if 'wrist_pos' in result.data:
                positions.append(result.data['wrist_pos'])
        
        if len(positions) < 2:
            return None
        
        total_dy = current_pos[1] - positions[-1][1]
        
        # Up means negative dy (y decreases going up)
        if total_dy < -0.1:
            speed = abs(total_dy)
            confidence = min(1.0, speed * 5)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'speed': speed, 'distance': total_dy, 'wrist_pos': current_pos}
            )
        
        return None


@register("advanced")
class SwipeDown(Gesture):
    """Fast downward movement."""
    
    @property
    def name(self) -> str:
        return "SWIPE_DOWN"
    
    @property
    def priority(self) -> int:
        return 8
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = (wrist.x, wrist.y)
        
        history = context.get('history', [])
        if len(history) < 2:
            return None
        
        positions = []
        for i in range(min(5, len(history))):
            result = history[-(i+1)]
            if 'wrist_pos' in result.data:
                positions.append(result.data['wrist_pos'])
        
        if len(positions) < 2:
            return None
        
        total_dy = current_pos[1] - positions[-1][1]
        
        if total_dy > 0.1:  # Moved down
            speed = abs(total_dy)
            confidence = min(1.0, speed * 5)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'speed': speed, 'distance': total_dy, 'wrist_pos': current_pos}
            )
        
        return None


@register("advanced")
class RotateClockwise(Gesture):
    """Rotating hand clockwise."""
    
    @property
    def name(self) -> str:
        return "ROTATE_CW"
    
    @property
    def priority(self) -> int:
        return 9
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        # Calculate hand orientation using index and pinky
        index = landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_MCP]
        pinky = landmarks.landmark[mp_holistic.HandLandmark.PINKY_MCP]
        
        # Current angle
        dx = pinky.x - index.x
        dy = pinky.y - index.y
        current_angle = np.arctan2(dy, dx)
        
        # Check history
        history = context.get('history', [])
        if history:
            last_result = history[-1]
            if 'angle' in last_result.data:
                last_angle = last_result.data['angle']
                
                # Calculate angle change
                angle_delta = current_angle - last_angle
                
                # Normalize to -pi to pi
                while angle_delta > np.pi:
                    angle_delta -= 2 * np.pi
                while angle_delta < -np.pi:
                    angle_delta += 2 * np.pi
                
                # Clockwise is negative in our coordinate system
                if angle_delta < -0.05:  # Significant rotation
                    confidence = min(1.0, abs(angle_delta) * 3)
                    
                    return GestureResult(
                        name=self.name,
                        confidence=confidence,
                        data={'angle': current_angle, 'delta': angle_delta}
                    )
        
        # Store angle for next frame
        return None  # Or return low-confidence result to store angle


@register("advanced")
class Wave(Gesture):
    """Waving hand back and forth."""
    
    @property
    def name(self) -> str:
        return "WAVE"
    
    @property
    def priority(self) -> int:
        return 7
    
    def detect(self, landmarks, context: Dict[str, Any]) -> Optional[GestureResult]:
        # Wave detection requires oscillating x position
        wrist = landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_x = wrist.x
        
        history = context.get('history', [])
        if len(history) < 10:
            return None
        
        # Get last 10 x positions
        x_positions = []
        for i in range(10):
            result = history[-(i+1)]
            if 'wrist_x' in result.data:
                x_positions.append(result.data['wrist_x'])
        
        if len(x_positions) < 10:
            return None
        
        # Count direction changes (oscillations)
        direction_changes = 0
        for i in range(1, len(x_positions) - 1):
            if (x_positions[i] > x_positions[i-1] and x_positions[i] > x_positions[i+1]) or \
               (x_positions[i] < x_positions[i-1] and x_positions[i] < x_positions[i+1]):
                direction_changes += 1
        
        # Wave needs at least 2-3 oscillations
        if direction_changes >= 2:
            confidence = min(1.0, direction_changes / 3)
            
            return GestureResult(
                name=self.name,
                confidence=confidence,
                data={'oscillations': direction_changes, 'wrist_x': current_x}
            )
        
        return None
