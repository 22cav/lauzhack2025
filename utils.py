"""
Utilities

Helper functions for the 3DX addon with pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from typing import Optional, Tuple
from pydantic import BaseModel, Field
import cv2

import config


class CameraInfo(BaseModel):
    """Camera information model."""
    index: int = Field(..., ge=0)
    available: bool
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    error: Optional[str] = None


def validate_camera(camera_index: int = 0) -> bool:
    """
    Validate if camera is available and accessible.
    
    Args:
        camera_index: Camera index to test (default: 0)
        
    Returns:
        bool: True if camera is available, False otherwise
    """
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            cap.release()
            return False
        
        # Try to read a frame
        ret, _ = cap.read()
        cap.release()
        
        return ret
        
    except Exception as e:
        print(f"[3DX Utils] Camera validation error: {e}")
        return False


def get_camera_info(camera_index: int = 0) -> CameraInfo:
    """
    Get detailed camera information.
    
    Args:
        camera_index: Camera index to query
        
    Returns:
        CameraInfo: Detailed camera information with pydantic validation
    """
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return CameraInfo(
                index=camera_index,
                available=False,
                error="Camera could not be opened"
            )
        
        # Get properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Try to read a frame
        ret, _ = cap.read()
        cap.release()
        
        if not ret:
            return CameraInfo(
                index=camera_index,
                available=False,
                width=width,
                height=height,
                fps=fps,
                error="Could not read from camera"
            )
        
        return CameraInfo(
            index=camera_index,
            available=True,
            width=width,
            height=height,
            fps=fps
        )
        
    except Exception as e:
        return CameraInfo(
            index=camera_index,
            available=False,
            error=str(e)
        )


def list_available_cameras(max_index: int = 10) -> list[CameraInfo]:
    """
    List all available cameras on the system.
    
    Args:
        max_index: Maximum camera index to check
        
    Returns:
        List of CameraInfo for all available cameras
    """
    available_cameras = []
    
    for i in range(max_index):
        info = get_camera_info(i)
        if info.available:
            available_cameras.append(info)
        # Continue checking all indices - some systems may have gaps
    
    return available_cameras


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def normalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
    """
    Normalize pixel coordinates to [-1, 1] range.
    
    Args:
        x: X pixel coordinate
        y: Y pixel coordinate
        width: Image width
        height: Image height
        
    Returns:
        Tuple of normalized (x, y) coordinates
    """
    norm_x = (2.0 * x / width) - 1.0
    norm_y = (2.0 * y / height) - 1.0
    return norm_x, norm_y


def calculate_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate 2D Euclidean distance between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        
    Returns:
        Distance between points
    """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def calculate_distance_3d(x1: float, y1: float, z1: float, 
                         x2: float, y2: float, z2: float) -> float:
    """
    Calculate 3D Euclidean distance between two points.
    
    Args:
        x1, y1, z1: First point coordinates
        x2, y2, z2: Second point coordinates
        
    Returns:
        Distance between points
    """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
