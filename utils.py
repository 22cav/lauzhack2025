"""
Utility Functions

Helper functions for camera validation, error formatting, and dependency checking.
"""

from typing import Optional, Tuple
import bpy


def validate_camera(camera_index: int) -> bool:
    """
    Check if camera is available.
    
    Args:
        camera_index: Camera device index to validate
        
    Returns:
        bool: True if camera can be opened successfully
        
    #TODO: Implement camera validation
    Implementation steps:
    1. Import cv2
    2. Try cv2.VideoCapture(camera_index)
    3. Try cap.read() to test frame capture
    4. Release camera immediately
    5. Return True if successful, False otherwise
    6. Handle exceptions gracefully
    """
    try:
        import cv2
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        return ret
    except Exception as e:
        print(f"[3DX] Camera validation error: {e}")
        return False


def get_blender_version() -> Tuple[int, int, int]:
    """
    Get current Blender version as tuple.
    
    Returns:
        Tuple[int, int, int]: (major, minor, patch)
    """
    return bpy.app.version


def format_error_message(error_type: str, details: str) -> str:
    """
    Create user-friendly error messages.
    
    Args:
        error_type: Type of error ("camera", "permission", "dependency", etc.)
        details: Error details string
        
    Returns:
        str: Formatted error message with helpful suggestions
        
    #TODO: Implement comprehensive error formatting
    Handle different error types:
    - "camera_not_found": Camera device not available
    - "camera_in_use": Camera already in use by another app
    - "permission_denied": Camera permission not granted
    - "dependency_missing": Required library not installed
    - "mediapipe_error": MediaPipe initialization failed
    - "unknown": Generic error
    
    Each case should provide specific troubleshooting steps.
    """
    error_messages = {
        "camera_not_found": (
            f"Camera not found: {details}\n\n"
            "Troubleshooting:\n"
            "1. Check camera is connected\n"
            "2. Try a different camera index (0, 1, 2...)\n"
            "3. Test camera in another application\n"
            "4. Restart Blender"
        ),
        "camera_in_use": (
            f"Camera in use: {details}\n\n"
            "Please close other applications using the camera."
        ),
        "permission_denied": (
            f"Camera permission denied: {details}\n\n"
            "macOS: System Preferences > Security & Privacy > Camera\n"
            "Windows: Settings > Privacy > Camera\n"
            "Linux: Check user camera permissions"
        ),
        "dependency_missing": (
            f"Dependency missing: {details}\n\n"
            "Please install required packages:\n"
            "pip install opencv-python mediapipe numpy"
        ),
        "mediapipe_error": (
            f"MediaPipe error: {details}\n\n"
            "Try reinstalling: pip install --upgrade mediapipe"
        ),
        "unknown": f"Error: {details}"
    }
    
    return error_messages.get(error_type, error_messages["unknown"])


def check_dependencies() -> Tuple[bool, str]:
    """
    Verify all required dependencies are available.
    
    Returns:
        Tuple[bool, str]: (success, message)
            - success: True if all dependencies available
            - message: Status message or error details
            
    #TODO: Implement dependency checking
    Check for:
    1. cv2 (OpenCV)
    2. mediapipe
    3. numpy
    
    Return (True, "All dependencies OK") if all succeed
    Return (False, "Missing: <list>") if any fail
    """
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        return False, f"Missing dependencies: {', '.join(missing_deps)}"
    
    return True, "All dependencies OK"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(max_value, value))


def validate_gesture_data(data: dict) -> bool:
    """
    Validate gesture data structure.
    
    Args:
        data: Gesture data dictionary
        
    Returns:
        bool: True if data is valid
        
    #TODO: Implement data validation
    Check that data contains expected keys:
    - For movement gestures: 'dx', 'dy' (floats)
    - For state gestures: 'confidence' (float 0-1)
    - All numeric values are valid (not NaN, not Inf)
    """
    if not isinstance(data, dict):
        return False
    
    # Check for movement data
    if 'dx' in data or 'dy' in data:
        try:
            dx = float(data.get('dx', 0))
            dy = float(data.get('dy', 0))
            
            # Check for NaN or Inf
            if not (abs(dx) < float('inf') and abs(dy) < float('inf')):
                return False
        except (TypeError, ValueError):
            return False
    
    # Check confidence if present
    if 'confidence' in data:
        try:
            conf = float(data['confidence'])
            if not (0.0 <= conf <= 1.0):
                return False
        except (TypeError, ValueError):
            return False
    
    return True
