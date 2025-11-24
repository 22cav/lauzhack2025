"""
Camera Capture

Wrapper for OpenCV camera capture with Pydantic configuration and error handling.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Optional, Tuple, Any
from pydantic import BaseModel, Field
from numpy.typing import NDArray
import cv2

import config


class CameraConfig(BaseModel):
    """Configuration for camera capture."""
    index: int = Field(0, ge=0)
    width: int = Field(640, gt=0)
    height: int = Field(480, gt=0)
    fps: int = Field(30, gt=0)


class CameraCapture:
    """
    Wrapper for OpenCV camera capture.
    """
    
    def __init__(self, config: CameraConfig):
        self.config = config
        self.cap: Optional[Any] = None
        self.is_open: bool = False
        self.frame_count: int = 0
    
    def open(self) -> bool:
        """
        Open camera device.
        
        Returns:
            bool: True if camera opened successfully, False otherwise.
        """
        try:
            self.cap = cv2.VideoCapture(self.config.index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            self.is_open = True
            return True
        except Exception as e:
            print(f"Error opening camera: {e}")
            return False

    def read_frame(self) -> Tuple[bool, Optional[NDArray]]:
        """
        Read one frame from camera.
        
        Returns:
            Tuple[bool, Optional[NDArray]]: Tuple of (success, frame).
        """
        if not self.is_open or not self.cap:
            return False, None
        
        # Read Frame, returns (success, frame)
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        
        self.frame_count += 1
        return True, frame
    
    def release(self) -> None:
        """
        Release camera resources.
        """
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.is_open = False
        self.frame_count = 0
    
    def __del__(self):
        self.release()
