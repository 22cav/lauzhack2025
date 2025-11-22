"""
Gesture Input Module - Enhanced gesture recognition with pinch-drag support.

This module extracts gesture detection from the original main.py and adds
advanced gestures like pinch detection and hand position tracking for drag operations.
"""

import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import logging
from typing import Optional, Dict, Any

import sys
sys.path.append('/Users/matte/MDS/Personal/lauzhack')

from core.event_system import Event, EventBus, EventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MediaPipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class GestureState:
    """Tracks the state of gestures to handle state transitions."""
    
    def __init__(self):
        self.current_gesture = "UNKNOWN"
        self.is_pinching = False
        self.pinch_start_pos = None
        self.last_hand_pos = None
        

class GestureInput:
    """
    Gesture recognition input source.
    
    Captures webcam feed, detects hand gestures using MediaPipe Holistic,
    and publishes gesture events to the EventBus.
    
    Supported gestures:
    - OPEN_PALM: All fingers extended
    - CLOSED_FIST: All fingers closed
    - POINTING: Index finger extended
    - PINCH_START: Thumb and index finger come together
    - PINCH_DRAG: Pinching while moving hand
    - PINCH_RELEASE: Fingers separate after pinch
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Initialize gesture input.
        
        Args:
            event_bus: EventBus instance for publishing events
            config: Configuration dictionary with camera settings
        """
        self.event_bus = event_bus
        self.config = config
        
        # Camera settings
        self.camera_index = config.get('camera_index', 0)
        self.min_detection_confidence = config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = config.get('min_tracking_confidence', 0.5)
        self.pinch_threshold = config.get('pinch_threshold', 0.05)
        self.show_preview = config.get('show_preview', True)
        
        # State
        self.cap = None
        self.running = False
        self.thread = None
        self.state = GestureState()
        
        logger.info(f"GestureInput initialized with camera {self.camera_index}")
    
    def start(self):
        """Start the gesture recognition thread."""
        if self.running:
            logger.warning("GestureInput already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("GestureInput started")
    
    def stop(self):
        """Stop the gesture recognition thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("GestureInput stopped")
    
    def _run(self):
        """Main processing loop (runs in separate thread)."""
        # Initialize webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {self.camera_index}")
            self.running = False
            return
        
        logger.info("Camera initialized successfully")
        
        if self.show_preview:
            logger.info("=" * 60)
            logger.info("📹 CAMERA WINDOW OPENING - Look for 'Gesture Recognition' window!")
            logger.info("   The window shows:")
            logger.info("   - Live camera feed")
            logger.info("   - Skeleton tracking (green lines)")
            logger.info("   - Hand landmarks (colored dots)")
            logger.info("   - Current gesture at top")
            logger.info("=" * 60)
        
        with mp_holistic.Holistic(
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence) as holistic:
            
            while self.running:
                success, image = self.cap.read()
                if not success:
                    logger.warning("Empty camera frame")
                    continue
                
                # Process frame
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                
                # Draw annotations
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                if self.show_preview:
                    self._draw_landmarks(image, results)
                
                # Detect gestures
                self._process_gestures(results)
                
                # Show preview
                if self.show_preview:
                    # Add gesture text
                    cv2.putText(image, f"Gesture: {self.state.current_gesture}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Add status text
                    status_text = "PINCHING" if self.state.is_pinching else "Ready"
                    cv2.putText(image, f"Status: {status_text}", 
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # Show window (imshow creates window automatically)
                    cv2.imshow('Gesture Recognition - Press ESC to exit', image)
                    
                    # Wait for key press
                    if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
                        break
        
        self.stop()
    
    def _draw_landmarks(self, image, results):
        """Draw pose and hand landmarks on the image."""
        # Draw pose
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        
        # Draw hands
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    
    def _process_gestures(self, results):
        """Process MediaPipe results and detect gestures."""
        # Check right hand first, then left
        hand_landmarks = None
        if results.right_hand_landmarks:
            hand_landmarks = results.right_hand_landmarks
        elif results.left_hand_landmarks:
            hand_landmarks = results.left_hand_landmarks
        
        if hand_landmarks is None:
            # No hand detected - reset pinch state
            if self.state.is_pinching:
                self._publish_event("PINCH_RELEASE", {})
                self.state.is_pinching = False
            self.state.current_gesture = "UNKNOWN"
            return
        
        # Detect pinch gesture
        is_pinching = self._detect_pinch(hand_landmarks)
        hand_pos = self._get_hand_position(hand_landmarks)
        
        # Handle pinch state transitions
        if is_pinching and not self.state.is_pinching:
            # Pinch started
            self.state.is_pinching = True
            self.state.pinch_start_pos = hand_pos
            self.state.last_hand_pos = hand_pos
            self._publish_event("PINCH_START", {"position": hand_pos})
            
        elif is_pinching and self.state.is_pinching:
            # Pinch dragging
            if self.state.last_hand_pos:
                delta = {
                    'dx': hand_pos['x'] - self.state.last_hand_pos['x'],
                    'dy': hand_pos['y'] - self.state.last_hand_pos['y']
                }
                self._publish_event("PINCH_DRAG", {
                    "position": hand_pos,
                    "delta": delta,
                    "start_position": self.state.pinch_start_pos
                })
            self.state.last_hand_pos = hand_pos
            
        elif not is_pinching and self.state.is_pinching:
            # Pinch released
            self.state.is_pinching = False
            self._publish_event("PINCH_RELEASE", {"position": hand_pos})
        
        # Detect basic gestures (when not pinching)
        if not is_pinching:
            gesture = self._detect_basic_gesture(hand_landmarks)
            if gesture != self.state.current_gesture and gesture != "UNKNOWN":
                self.state.current_gesture = gesture
                self._publish_event(gesture, {})
    
    def _detect_pinch(self, hand_landmarks) -> bool:
        """
        Detect if thumb and index finger are pinched together.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            True if pinching, False otherwise
        """
        thumb_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
        
        # Calculate Euclidean distance
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x) ** 2 +
            (thumb_tip.y - index_tip.y) ** 2 +
            (thumb_tip.z - index_tip.z) ** 2
        )
        
        return distance < self.pinch_threshold
    
    def _get_hand_position(self, hand_landmarks) -> Dict[str, float]:
        """
        Get the center position of the hand.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            Dictionary with x, y, z coordinates (normalized 0-1)
        """
        # Use wrist as hand position reference
        wrist = hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        return {
            'x': wrist.x,
            'y': wrist.y,
            'z': wrist.z
        }
    
    def _detect_basic_gesture(self, hand_landmarks) -> str:
        """
        Detect basic hand gestures (open palm, closed fist, pointing).
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            Detected gesture name
        """
        if not hand_landmarks:
            return "UNKNOWN"
        
        # Count extended fingers
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
        
        extended_fingers = 0
        for tip, pip in zip(fingers, fingers_pip):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                extended_fingers += 1
        
        # Classify gesture
        if extended_fingers == 4:
            return "OPEN_PALM"
        elif extended_fingers == 0:
            return "CLOSED_FIST"
        elif extended_fingers == 1:
            index_extended = hand_landmarks.landmark[
                mp_holistic.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[
                mp_holistic.HandLandmark.INDEX_FINGER_PIP].y
            if index_extended:
                return "POINTING"
        
        return "UNKNOWN"
    
    def _publish_event(self, action: str, data: Dict[str, Any]):
        """
        Publish a gesture event to the EventBus.
        
        Args:
            action: Gesture action name
            data: Additional event data
        """
        event = Event(
            type=EventType.GESTURE,
            source="gesture_engine",
            action=action,
            data=data
        )
        self.event_bus.publish(event)
        logger.debug(f"Published gesture event: {action}")
