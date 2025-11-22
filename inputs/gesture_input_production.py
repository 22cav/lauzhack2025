"""
Production Gesture Input with Platform Support

Provides both threaded and main-thread gesture detection modes for
cross-platform compatibility. Integrates with production gesture detector.
"""

import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import logging
import platform
from typing import Optional, Dict, Any

import sys
sys.path.append('/Users/matte/MDS/Personal/lauzhack')

from core.event_system import Event, EventBus, EventType
from gestures import GestureDetector
from gestures.filters import LandmarkFilter
from gestures.validators import ConfidenceValidator, QualityValidator
from gestures.library import basic, advanced

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# MediaPipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class GestureInputBase:
    """
    Base class for gesture input with production detector.
    
    Provides shared initialization and processing logic that works
    in both threaded and main-thread modes.
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        """
        Initialize gesture input base.
        
        Args:
            event_bus: EventBus instance for publishing events
            config: Configuration dictionary
        """
        self.event_bus = event_bus
        self.config = config
        
        # Camera settings
        self.camera_index = config.get('camera_index', 0)
        self.min_detection_confidence = config.get('min_detection_confidence', 0.5)
        self.min_tracking_confidence = config.get('min_tracking_confidence', 0.5)
        self.show_preview = config.get('show_preview', True)
        
        # Camera
        self.cap = None
        self.running = False
        
        # Production gesture system
        self.detector = GestureDetector(min_confidence=config.get('min_confidence', 0.6))
        self.landmark_filter = LandmarkFilter(window_size=config.get('filter_window', 5))
        self.confidence_validator = ConfidenceValidator(
            min_confidence=config.get('min_confidence', 0.6),
            stability_frames=config.get('stability_frames', 2)
        )
        self.quality_validator = QualityValidator()
        
        # Load gestures from config
        gesture_sets = config.get('gesture_sets', ['basic', 'advanced'])
        self._load_gestures(gesture_sets)
        
        # Legacy pinch state for backward compatibility
        self.is_pinching = False
        self.last_hand_pos = None
        self.pinch_start_pos = None
        
        logger.info(f"GestureInputBase initialized with {len(self.detector.gestures)} gestures")
    
    def _load_gestures(self, sets: list):
        """Load gesture sets into detector."""
        loaded_count = 0
        
        if 'basic' in sets:
            for attr_name in dir(basic):
                attr = getattr(basic, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'detect'):
                    try:
                        self.detector.register(attr())
                        loaded_count += 1
                    except:
                        pass
        
        if 'advanced' in sets:
            for attr_name in dir(advanced):
                attr = getattr(advanced, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'detect'):
                    try:
                        self.detector.register(attr())
                        loaded_count += 1
                    except:
                        pass
        
        logger.info(f"Loaded {loaded_count} gestures from sets: {sets}")
    
    def _initialize_camera(self):
        """Initialize webcam."""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {self.camera_index}")
            return False
        
        logger.info("Camera initialized successfully")
        return True
    
    def _process_frame(self, image, results) -> Optional[str]:
        """
        Process a single frame and detect gestures.
        
        Args:
            image: OpenCV image (BGR)
            results: MediaPipe holistic results
        
        Returns:
            Detected gesture name or None
        """
        # Draw landmarks if preview enabled
        if self.show_preview:
            self._draw_landmarks(image, results)
        
        # Get hand landmarks
        hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks
        
        if hand_landmarks is None:
            # Reset pinch state for legacy compatibility
            if self.is_pinching:
                self._publish_event("PINCH_RELEASE", {})
                self.is_pinching = False
            logger.debug("No hand detected in frame")
            return None
        
        logger.debug("✓ Hand detected")
        
        # Validate quality
        if not self.quality_validator.validate(hand_landmarks):
            logger.debug("✗ Hand quality validation failed")
            return None
        
        logger.debug("✓ Hand quality OK")
        
        # Smooth landmarks
        smoothed_landmarks = self.landmark_filter.update(hand_landmarks)
        
        # Detect with production detector
        result = self.detector.detect_best(smoothed_landmarks)
        
        if result:
            logger.info(f"🎯 Detected: {result.name} (confidence: {result.confidence:.2f})")
        else:
            logger.debug("No gesture detected by detector")
        
        if result and self.confidence_validator.validate(result):
            logger.info(f"✅ Publishing gesture: {result.name}")
            # Handle special PINCH_DRAG for legacy compatibility
            if result.name == "PINCH_DRAG":
                self._handle_pinch_drag(result, hand_landmarks)
            else:
                # Publish standard gesture event
                self._publish_event(result.name, result.data)
            
            return result.name
        elif result:
            logger.debug(f"✗ Gesture {result.name} failed confidence validation")
        
        return None
    
    def _handle_pinch_drag(self, result, hand_landmarks):
        """Handle PINCH_DRAG with legacy-compatible delta calculation."""
        wrist = hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
        current_pos = {'x': wrist.x, 'y': wrist.y, 'z': wrist.z}
        
        # Calculate delta from last position
        if self.last_hand_pos:
            delta = {
                'dx': current_pos['x'] - self.last_hand_pos['x'],
                'dy': current_pos['y'] - self.last_hand_pos['y']
            }
            
            self._publish_event("PINCH_DRAG", {
                "position": current_pos,
                "delta": delta,
                "start_position": self.pinch_start_pos or current_pos
            })
        else:
            # First pinch drag frame
            self.pinch_start_pos = current_pos
        
        self.last_hand_pos = current_pos
        self.is_pinching = True
    
    def _draw_landmarks(self, image, results):
        """Draw pose and hand landmarks."""
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        
        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    
    def _publish_event(self, action: str, data: Dict[str, Any]):
        """Publish gesture event to EventBus."""
        event = Event(
            type=EventType.GESTURE,
            source="gesture_engine",
            action=action,
            data=data
        )
        self.event_bus.publish(event)
        logger.debug(f"Published: {action}")


class GestureInput(GestureInputBase):
    """
    Threaded gesture input (for Linux/Windows).
    
    Runs camera processing in background thread.
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        super().__init__(event_bus, config)
        self.thread = None
        logger.info("GestureInput (threaded mode) initialized")
    
    def start(self):
        """Start gesture recognition thread."""
        if self.running:
            logger.warning("GestureInput already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("GestureInput started (background thread)")
    
    def stop(self):
        """Stop gesture recognition thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("GestureInput stopped")
    
    def _run(self):
        """Main processing loop in thread."""
        if not self._initialize_camera():
            self.running = False
            return
        
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
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Detect gestures
                detected = self._process_frame(image, results)
                
                # Show preview (may not work on macOS)
                if self.show_preview:
                    if detected:
                        cv2.putText(image, f"Gesture: {detected}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Gesture Recognition', image)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
        
        self.stop()


class GestureInputMainThread(GestureInputBase):
    """
    Main-thread gesture input (for macOS).
    
    Camera processing happens in main thread via update() calls.
    Must be called repeatedly from main loop.
    """
    
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        super().__init__(event_bus, config)
        self.holistic = None
        logger.info("GestureInputMainThread (main thread mode) initialized for macOS")
    
    def start(self):
        """Initialize camera and MediaPipe."""
        if self.running:
            return
        
        logger.info("Starting camera initialization...")
        
        if not self._initialize_camera():
            logger.error("Failed to initialize camera!")
            return
        
        logger.info("Initializing MediaPipe Holistic...")
        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        self.running = True
        logger.info("✓ GestureInputMainThread started (call update() from main loop)")
        logger.info("📹 Camera ready - processing will begin when update() is called")
    
    def stop(self):
        """Stop and cleanup."""
        self.running = False
        if self.cap:
            self.cap.release()
        if self.holistic:
            self.holistic.close()
        cv2.destroyAllWindows()
        logger.info("GestureInputMainThread stopped")
    
    def update(self) -> bool:
        """
        Process one frame (call from main loop).
        
        Returns:
            True if should continue, False to stop
        """
        if not self.running or not self.cap:
            return False
        
        success, image = self.cap.read()
        if not success:
            return True  # Continue despite empty frame
        
        # Process frame
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Detect gestures
        detected = self._process_frame(image, results)
        
        # Show preview (works in main thread on macOS)
        if self.show_preview:
            if detected:
                cv2.putText(image, f"Gesture: {detected}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, "macOS Mode (Press ESC to exit)",
                       (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow('Gesture Recognition - macOS', image)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                return False
        
        return True


def create_gesture_input(event_bus: EventBus, config: Dict[str, Any]) -> GestureInputBase:
    """
    Factory function to create appropriate gesture input for platform.
    
    Args:
        event_bus: EventBus instance
        config: Configuration dictionary
    
    Returns:
        GestureInput or GestureInputMainThread based on platform
    """
    is_macos = platform.system() == "Darwin"
    show_preview = config.get('show_preview', True)
    
    if is_macos and show_preview:
        logger.info("Platform: macOS - using main-thread mode")
        return GestureInputMainThread(event_bus, config)
    else:
        logger.info(f"Platform: {platform.system()} - using threaded mode")
        return GestureInput(event_bus, config)
