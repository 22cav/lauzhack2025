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
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.event_system import Event, EventBus, EventType
from gestures import GestureDetector
from gestures.filters import LandmarkFilter
from gestures.validators import ConfidenceValidator, QualityValidator
from gestures.library import navigation

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
    
    This class integrates the production gesture detection system with:
    - MediaPipe Holistic for hand/pose tracking
    - Gesture detector with confidence validation
    - Landmark filtering for noise reduction
    - Quality validation for reliable detection
    
    State Management:
    - is_playing: Animation playback state (controlled by OPEN_PALM/CLOSED_FIST)
    - is_pinching: Rotation mode active (PINCH gesture)
    - is_v_gesturing: Navigation mode active (V_GESTURE)
    
    Modality System:
    - ROTATION mode: PINCH gesture for viewport rotation
    - NAVIGATION mode: V_GESTURE for viewport panning
    - Automatic switching between modes based on detected gesture
    
    Movement Tracking:
    - Tracks hand position for continuous gestures (PINCH, V_GESTURE)
    - Calculates movement deltas for smooth control
    - Applies sensitivity and filtering for responsive yet stable input
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
        self.detector = GestureDetector(min_confidence=config.get('min_confidence', 0.6)) # Lowered for better detection
        self.landmark_filter = LandmarkFilter(window_size=config.get('filter_window', 3)) # Reduced smoothing
        self.confidence_validator = ConfidenceValidator(
            min_confidence=config.get('min_confidence', 0.5),
            stability_frames=config.get('stability_frames', 1) # Faster response
        )
        self.quality_validator = QualityValidator()
        
        # Load gestures from navigation library
        self._load_gestures()
        
        # State Machine
        self.is_playing = True
        self.is_pinching = False
        self.pinch_start_pos = None
        self.last_pinch_pos = None
        
        # V-gesture movement tracking
        self.is_v_gesturing = False
        self.last_v_pos = None
        self.smoothed_v_delta = {'dx': 0, 'dy': 0}  # For exponential smoothing
        
        # Feedback state
        self.last_command = "None"
        self.last_confidence = 0.0
        
        logger.info(f"GestureInputBase initialized with {len(self.detector.gestures)} gestures")
    
    def _load_gestures(self):
        """Load navigation gestures."""
        loaded_count = 0
        for attr_name in dir(navigation):
            attr = getattr(navigation, attr_name)
            if isinstance(attr, type) and hasattr(attr, 'detect'):
                try:
                    self.detector.register(attr())
                    loaded_count += 1
                except:
                    pass
        
        logger.info(f"Loaded {loaded_count} navigation gestures")
    
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
        
        This is the main gesture processing pipeline that:
        1. Validates hand landmarks are present
        2. Checks landmark quality
        3. Applies smoothing filter
        4. Detects gestures using production detector
        5. Validates confidence
        6. Routes to appropriate handler based on gesture type
        
        Gesture Processing Order:
        1. Animation Control (OPEN_PALM, CLOSED_FIST) - Always processed
        2. Modality Gestures (PINCH, V_GESTURE) - Automatic mode switching
        3. Other Gestures - Reset modality states
        
        Args:
            image: Camera frame (BGR format)
            results: MediaPipe Holistic results with hand/pose landmarks
        
        Returns:
            Detected gesture name or None
        """
        # Draw landmarks if preview enabled
        if self.show_preview:
            self._draw_landmarks(image, results)
        
        # Get hand landmarks
        hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks
        
        if hand_landmarks is None:
            # Reset pinch state
            if self.is_pinching:
                self.is_pinching = False
                self.pinch_start_pos = None
                self.last_pinch_pos = None
            
            self.last_command = "None"
            self.last_confidence = 0.0
            return None
        
        # Validate quality
        if not self.quality_validator.validate(hand_landmarks):
            self.last_command = "Low Quality"
            return None
        
        # Smooth landmarks
        smoothed_landmarks = self.landmark_filter.update(hand_landmarks)
        
        # Detect with production detector
        result = self.detector.detect_best(smoothed_landmarks)
        
        if result and self.confidence_validator.validate(result):
            gesture_name = result.name
            self.last_confidence = result.confidence
            
            # Animation Control (PLAY/STOP) - these control simulation state
            if gesture_name == "CLOSED_FIST":
                if self.is_playing:
                    self.is_playing = False
                    logger.info("🛑 Simulation STOPPED")
                    self._publish_event("STOP", {})
                self.last_command = "STOP (Fist)"
                return "CLOSED_FIST"
                
            elif gesture_name == "OPEN_PALM":
                if not self.is_playing:
                    self.is_playing = True
                    logger.info("▶️ Simulation STARTED")
                    self._publish_event("PLAY", {})
                self.last_command = "PLAY (Palm)"
                return "OPEN_PALM"
            
            # Automatic Modality Switching
            # PINCH = Rotation Mode (always available)
            # V_GESTURE = Navigation Mode (always available)
            
            if gesture_name == "PINCH":
                # Switch to rotation modality
                if self.is_v_gesturing:
                    # Switching from navigation to rotation
                    self.is_v_gesturing = False
                    self.last_v_pos = None
                    logger.info("🔄 Switched to ROTATION mode")
                
                self._handle_pinch_drag(result, hand_landmarks)
                self.last_command = "ROTATING (Pinch)"
                return "PINCH_DRAG"
                
            elif gesture_name == "V_GESTURE":
                # Switch to navigation modality
                if self.is_pinching:
                    # Switching from rotation to navigation
                    self.is_pinching = False
                    self.pinch_start_pos = None
                    self.last_pinch_pos = None
                    logger.info("🧭 Switched to NAVIGATION mode")
                
                self._handle_v_movement(result)
                self.last_command = "NAVIGATING (V)"
                return "V_NAVIGATE"
                
            else:
                # Other gestures - reset both modalities
                if self.is_pinching or self.is_v_gesturing:
                    self.is_pinching = False
                    self.pinch_start_pos = None
                    self.last_pinch_pos = None
                    self.is_v_gesturing = False
                    self.last_v_pos = None
                
                # Publish other gestures
                self._publish_event(gesture_name, result.data)
                
                # Format for display
                self.last_command = gesture_name.replace("_", " ").title()
                logger.info(f"🎯 Command: {self.last_command}")
                return gesture_name
        
        self.last_command = "None"
        return None
    
    def _handle_pinch_drag(self, result, hand_landmarks):
        """
        Handle PINCH_DRAG with proportional rotation.
        
        Tracks pinch position and calculates movement deltas for smooth
        viewport rotation. The rotation is proportional to hand movement,
        providing intuitive control.
        
        Tracking:
        - Uses pinch position from result data (midpoint of thumb/index)
        - Falls back to wrist position if pinch position unavailable
        - Tracks position between frames to calculate deltas
        
        Sensitivity:
        - Base sensitivity: 100.0x multiplier
        - Provides visible rotation with small hand movements
        - Can be adjusted via configuration
        
        State Management:
        - is_pinching: Tracks if currently in rotation mode
        - pinch_start_pos: Initial position when pinch starts
        - last_pinch_pos: Previous frame position for delta calculation
        
        Args:
            result: GestureResult with position data
            hand_landmarks: MediaPipe hand landmarks
        """
        # Use the pinch position from result data if available, else wrist
        current_pos = result.data.get('position', None)
        if not current_pos:
            wrist = hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST]
            current_pos = {'x': wrist.x, 'y': wrist.y}
        
        if not self.is_pinching:
            # Start pinching
            self.is_pinching = True
            self.pinch_start_pos = current_pos
            self.last_pinch_pos = current_pos
        else:
            # Dragging
            dx = current_pos['x'] - self.last_pinch_pos['x']
            dy = current_pos['y'] - self.last_pinch_pos['y']
            
            # Reduced sensitivity for more precise rotation control
            # Changed from 100.0 to 20.0 (0.2x base sensitivity)
            sensitivity = 20.0
            
            if abs(dx) > 0.001 or abs(dy) > 0.001:
                self._publish_event("ROTATE", {
                    "dx": dx * sensitivity,
                    "dy": dy * sensitivity
                })
            
            self.last_pinch_pos = current_pos

    def _handle_v_movement(self, result):
        """
        Handle V-gesture movement for navigation with improved sensitivity and noise filtering.
        
        This method tracks the V-gesture position and calculates movement deltas
        for smooth viewport panning/navigation. Includes several improvements:
        
        1. Higher sensitivity (150x vs 100x) for detecting small movements
        2. Deadzone filtering to ignore micro-jitter from hand tremor
        3. Exponential smoothing for fluid, natural movement
        
        Args:
            result: GestureResult containing position data
        
        Movement Calculation:
        - Tracks position between frames
        - Mirrors X-axis (negates dx) to correct camera coordinates
        - Applies sensitivity multiplier for responsive control
        - Filters movements below deadzone threshold
        
        Smoothing:
        - Uses exponential moving average on deltas
        - Smoothing factor: 0.7 (70% new, 30% old)
        - Reduces jitter while maintaining responsiveness
        """
        current_pos = result.data.get('position', None)
        if not current_pos:
            return
        
        if not self.is_v_gesturing:
            # Start V-gesturing - initialize tracking
            self.is_v_gesturing = True
            self.last_v_pos = current_pos
            # Initialize smoothed delta storage
            if not hasattr(self, 'smoothed_v_delta'):
                self.smoothed_v_delta = {'dx': 0, 'dy': 0}
        else:
            # Calculate movement delta
            # Note: Camera coordinates are mirrored, so negate dx for proper direction
            dx = -(current_pos['x'] - self.last_v_pos['x'])  # Negate for mirror correction
            dy = current_pos['y'] - self.last_v_pos['y']
            
            # IMPROVED: Higher sensitivity for better small movement detection
            # Increased from 100.0 to 150.0 for more responsive navigation
            sensitivity = 150.0
            
            # IMPROVED: Larger deadzone to filter micro-movements and reduce jitter
            # Increased from 0.0005 to 0.001 for cleaner, less laggy movement
            deadzone = 0.001
            
            # Check if movement exceeds deadzone
            if abs(dx) > deadzone or abs(dy) > deadzone:
                # Apply sensitivity
                dx_scaled = dx * sensitivity
                dy_scaled = dy * sensitivity
                
                # IMPROVED: Stronger exponential smoothing for uniform movement
                # Increased from 0.7 to 0.85 for smoother, less back-and-forth motion
                # Higher alpha = more weight on new value, but still smooths out jitter
                smoothing_alpha = 0.85  # 85% new value, 15% old value
                
                self.smoothed_v_delta['dx'] = (
                    smoothing_alpha * dx_scaled + 
                    (1 - smoothing_alpha) * self.smoothed_v_delta['dx']
                )
                self.smoothed_v_delta['dy'] = (
                    smoothing_alpha * dy_scaled + 
                    (1 - smoothing_alpha) * self.smoothed_v_delta['dy']
                )
                
                # Publish smoothed movement
                self._publish_event("NAVIGATE", {
                    "dx": self.smoothed_v_delta['dx'],
                    "dy": self.smoothed_v_delta['dy']
                })
            
            # Update last position for next frame
            self.last_v_pos = current_pos


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
    
    def _draw_status(self, image):
        """Draw status overlay on image."""
        # Status Background
        h, w, _ = image.shape
        
        # Top bar for status
        cv2.rectangle(image, (0, 0), (w, 100), (0, 0, 0), -1)
        
        # System State (PLAYING/STOPPED)
        status_text = "PLAYING" if self.is_playing else "STOPPED"
        status_color = (0, 255, 0) if self.is_playing else (0, 0, 255)
        cv2.putText(image, f"SIM: {status_text}", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Current Modality
        if self.is_pinching:
            modality = "ROTATION"
            modality_color = (255, 165, 0)  # Orange
        elif self.is_v_gesturing:
            modality = "NAVIGATION"
            modality_color = (0, 255, 255)  # Cyan
        else:
            modality = "IDLE"
            modality_color = (128, 128, 128)  # Gray
        
        cv2.putText(image, f"MODE: {modality}", 
                   (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, modality_color, 2)
        
        # Current Command
        cmd_color = (255, 255, 0)  # Yellow
        cv2.putText(image, f"CMD: {self.last_command}", 
                   (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cmd_color, 2)
                   
        # Confidence bar if command detected
        if self.last_command != "None" and self.last_confidence > 0:
            bar_width = int(self.last_confidence * 200)
            cv2.rectangle(image, (300, 55), (300 + bar_width, 70), (0, 255, 255), -1)
            cv2.rectangle(image, (300, 55), (500, 70), (255, 255, 255), 1)
            
        # Help text
        help_text = "PINCH=Rotate | V=Navigate | PALM=Play | FIST=Stop"
        cv2.putText(image, help_text, 
                   (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _publish_event(self, action: str, data: Dict[str, Any]):
        """Publish gesture event to EventBus."""
        logger.info(f"📤 Publishing event: {action} with data: {data}")
        event = Event(
            type=EventType.GESTURE,
            source="gesture_engine",
            action=action,
            data=data
        )
        self.event_bus.publish(event)
        # logger.debug(f"Published: {action}") # Reduce noise, rely on command log


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
                self._process_frame(image, results)
                
                # Show preview (may not work on macOS)
                if self.show_preview:
                    self._draw_status(image)
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
        self._process_frame(image, results)
        
        # Show preview (works in main thread on macOS)
        if self.show_preview:
            self._draw_status(image)
            
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
