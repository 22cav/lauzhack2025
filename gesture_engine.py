"""
Gesture Engine

Main gesture detection and processing engine.
Dependency-free version (removes Pydantic/External imports for portability).
"""

import sys
import os
import time
import bpy
from typing import Optional, Tuple, Any, Dict
from dataclasses import dataclass

# ------------------------------------------------------------------------
# 1. LIBRARY HANDLING
# Safely handle external libraries that might not be in Blender
# ------------------------------------------------------------------------
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Import Gesture Library
# We use local imports to avoid circular dependencies if this file is imported early
try:
    from gestures.detector import GestureDetector
    from gestures.library.basic import OpenPalmGesture, ClosedFistGesture
    from gestures.library.advanced import PointingGesture, ThumbsUpGesture
    from gestures.library.navigation import PinchGesture, VGesture
    GESTURES_AVAILABLE = True
except ImportError as e:
    print(f"[Gesture Engine] Could not import gesture library: {e}")
    GESTURES_AVAILABLE = False

# ------------------------------------------------------------------------
# 2. DATA STRUCTURES (Replaces Pydantic)
# ------------------------------------------------------------------------

@dataclass
class EngineState:
    """Runtime state of the engine."""
    running: bool = False
    camera_ready: bool = False
    frame_count: int = 0
    last_frame_time: float = 0.0
    fps: float = 0.0

# ------------------------------------------------------------------------
# 3. CLASSES
# ------------------------------------------------------------------------

class CameraCapture:
    """
    Camera Capture Handler
    """
    def __init__(self, index=0, width=640, height=480):
        self.index = index
        self.width = width
        self.height = height
        self.cap = None
        
    def open(self) -> bool:
        """Opens the camera and sets low-latency parameters."""
        if not OPENCV_AVAILABLE:
            print("[Camera] OpenCV not installed.")
            return False
            
        try:
            if sys.platform == 'win32':
                self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            elif sys.platform == 'darwin':
                self.cap = cv2.VideoCapture(self.index, cv2.CAP_AVFOUNDATION)
            else:
                self.cap = cv2.VideoCapture(self.index)
                
            if not self.cap.isOpened():
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return True
        
        except Exception as e:
            print(f"[Camera] Error opening: {e}")
            return False

    def read_frame(self):
        """Reads a frame. Returns (success, frame)."""
        if self.cap and self.cap.isOpened():
            return self.cap.read()
        return False, None

    def release(self):
        """Releases hardware resources."""
        if self.cap:
            self.cap.release()
            self.cap = None

class GestureEngine:
    """
    Main gesture detection and processing engine.
    """
    
    def __init__(self, context):
        self.context = context
        self.state = EngineState()
        
        # Components
        self.camera = None
        self.hands = None
        self.detector = None
        
        # FPS tracking
        self.frame_times = []
        self.max_frame_times = 30
        
        # Cache package name for preferences lookup
        self.package = __package__ if __package__ else __name__
    
    def _get_prefs(self):
        # Safely get preferences even in Text Editor mode
        if self.package in self.context.preferences.addons:
            return self.context.preferences.addons[self.package].preferences
        return None

    def start(self) -> Tuple[bool, str]:
        """Start camera and gesture detection."""
        
        # 1. Check Dependencies
        if not OPENCV_AVAILABLE:
            return False, "OpenCV (cv2) not installed in Blender Python"
        if not MEDIAPIPE_AVAILABLE:
            return False, "MediaPipe not installed in Blender Python"
        if not GESTURES_AVAILABLE:
            return False, "Gesture Library not found"

        try:
            prefs = self._get_prefs()
            cam_idx = prefs.camera_index if prefs else 0
            min_conf = prefs.min_confidence if prefs else 0.7
            
            # 2. Initialize Camera
            self.camera = CameraCapture(index=cam_idx)
            if not self.camera.open():
                return False, f"Could not open Camera {cam_idx}"
            
            # 3. Initialize MediaPipe
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=min_conf,
                min_tracking_confidence=min_conf
            )
            
            # 4. Initialize Detector
            self.detector = GestureDetector(min_confidence=min_conf)
            
            # Register Gestures
            self.detector.register(OpenPalmGesture())
            self.detector.register(ClosedFistGesture())
            self.detector.register(PinchGesture())
            self.detector.register(VGesture())
            self.detector.register(PointingGesture())
            self.detector.register(ThumbsUpGesture())
            
            # 5. Update Internal State
            self.state.running = True
            self.state.camera_ready = True
            
            return True, "Engine started successfully"
            
        except Exception as e:
            self.stop()
            import traceback
            traceback.print_exc()
            return False, f"Startup Error: {str(e)}"
    
    def stop(self) -> None:
        """Stop and cleanup."""
        print("[Gesture Engine] Stopping...")
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        if self.hands:
            self.hands.close()
            self.hands = None
            
        self.state.running = False
        self.state.camera_ready = False
        self.frame_times.clear()

    def process_frame(self, context) -> None:
        """
        Process one camera frame. Called by the Modal Operator.
        """
        if not self.state.running or not self.camera:
            return
        
        try:
            frame_start = time.time()
            
            # 1. Capture
            ret, frame = self.camera.read_frame()
            if not ret or frame is None:
                return
            
            # 2. Process (MediaPipe requires RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            # 3. Update Blender UI Data (Properties.py)
            # We access the property group defined in Step 2
            if hasattr(context.scene, "gesture_state"):
                scene_props = context.scene.gesture_state
                
                self.state.frame_count += 1
                scene_props.frames_processed = self.state.frame_count
                
                # 4. Handle Detections
                if results.multi_hand_landmarks:
                    landmarks = results.multi_hand_landmarks[0]
                    
                    # Detect Gesture
                    # We pass the previous frame's context if needed (not fully implemented here but prepared)
                    detection_context = {} 
                    result = self.detector.detect_best(landmarks, detection_context)
                    
                    if result:
                        scene_props.gestures_detected += 1
                        scene_props.last_gesture = result.name
                        scene_props.last_confidence = result.confidence
                        
                        # Execute Actions based on Gesture
                        self._handle_gesture_action(context, result)
                    else:
                        scene_props.last_gesture = "None"
                        scene_props.last_confidence = 0.0

                    # Optional: Debug View (OpenCV Window)
                    # Note: This causes issues on some Mac/Linux Blender builds.
                    # Use with caution.
                    prefs = self._get_prefs()
                    if prefs and prefs.show_preview:
                        # Draw landmarks
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                        cv2.imshow("Gesture Preview", frame)
                        cv2.waitKey(1)
                else:
                    scene_props.last_gesture = "No Hand"
                    scene_props.last_confidence = 0.0

            # 5. FPS Calculation
            frame_end = time.time()
            self.frame_times.append(frame_end - frame_start)
            if len(self.frame_times) > self.max_frame_times:
                self.frame_times.pop(0)
            
            if self.frame_times:
                avg = sum(self.frame_times) / len(self.frame_times)
                fps = 1.0 / avg if avg > 0 else 0
                self.state.fps = fps
                if hasattr(context.scene, "gesture_state"):
                    context.scene.gesture_state.current_fps = fps
                
        except Exception as e:
            print(f"[Gesture Engine] Error: {e}")
            import traceback
            traceback.print_exc()

    def _handle_gesture_action(self, context, result):
        """
        Execute Blender operators based on detected gesture.
        """
        name = result.name
        data = result.data
        
        # Helper to get 3D view context
        def get_3d_view_context():
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            return {'area': area, 'region': region}
            return None

        try:
            if name == "PINCH_DRAG": # Matches config.GESTURE_PINCH
                # Rotate Viewport
                # We need dx, dy from data
                dx = data.get('dx', 0.0)
                dy = data.get('dy', 0.0)
                
                if abs(dx) > 0.001 or abs(dy) > 0.001:
                    view_ctx = get_3d_view_context()
                    if view_ctx:
                        # Sensitivity factor
                        sens = 5.0
                        with context.temp_override(**view_ctx):
                            bpy.ops.view3d.view_orbit(angle=dx * sens, type='ORBITRIGHT')
                            bpy.ops.view3d.view_orbit(angle=dy * sens, type='ORBITUP')

            elif name == "V_GESTURE_MOVE": # Matches config.GESTURE_V_MOVE
                # Pan Viewport
                dx = data.get('dx', 0.0)
                dy = data.get('dy', 0.0)
                
                if abs(dx) > 0.001 or abs(dy) > 0.001:
                    view_ctx = get_3d_view_context()
                    if view_ctx:
                        # Sensitivity factor
                        sens = 5.0
                        with context.temp_override(**view_ctx):
                            bpy.ops.view3d.view_pan(type='PANRIGHT', value=dx * sens)
                            bpy.ops.view3d.view_pan(type='PANUP', value=-dy * sens) # Invert Y for natural feel

            elif name == "OPEN_PALM": # Matches config.GESTURE_PALM
                # Play Animation
                if not context.screen.is_animation_playing:
                    bpy.ops.screen.animation_play()

            elif name == "CLOSED_FIST": # Matches config.GESTURE_FIST
                # Stop Animation
                if context.screen.is_animation_playing:
                    bpy.ops.screen.animation_cancel()
                    
        except Exception as e:
            print(f"[Gesture Action] Error executing {name}: {e}")