"""
3DX - Hand Gesture Control for Blender

A self-contained Blender addon for controlling Blender with hand gestures
detected via webcam using MediaPipe.
"""

from typing import Dict, Any, Optional, List
import sys
import os
import bpy
from bpy.types import AddonPreferences, PropertyGroup

bl_info: Dict[str, Any] = {
    "name": "3DX - Gesture Control",
    "author": "LauzHack Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > 3DX",
    "description": "Control Blender with hand gestures using webcam",
    "warning": "Requires camera access",
    "doc_url": "https://github.com/22cav/3DX",
    "category": "3D View",
}


def load_dependencies() -> bool:
    """
    Load bundled dependencies from libs/ folder.
    
    #TODO: Implement dependency loading system
    For now, assumes dependencies are installed in Python environment:
    - opencv-python or opencv-python-headless
    - mediapipe
    - numpy
    - PyYAML (optional)
    
    Future implementation:
    1. Get addon directory path
    2. Add libs/ to sys.path
    3. Try importing each dependency
    4. Return True if all succeed, False otherwise
    5. Show user-friendly error if missing
    
    Returns:
        bool: True if all dependencies loaded successfully
    """
    try:
        import cv2
        import mediapipe
        import numpy
        return True
    except ImportError as e:
        print(f"[3DX] Dependency missing: {e}")
        print("[3DX] Please install: pip install opencv-python mediapipe numpy")
        return False


def register() -> None:
    """
    Register all addon components.
    
    Registers properties, operators, and panels in the correct order.
    """
    # Check dependencies
    if not load_dependencies():
        print("[3DX] Failed to load dependencies. Addon not registered.")
        print("[3DX] Please install: pip install opencv-python mediapipe numpy")
        return
    
    try:
        # Import modules
        from . import operators
        from . import properties
        from . import panels
        
        # Register property classes
        properties.register()
        
        # Register operator classes
        operators.register()
        
        # Register panel classes
        panels.register()
        
        print("[3DX] Addon registered successfully")
        
    except Exception as e:
        print(f"[3DX] Registration error: {e}")
        import traceback
        traceback.print_exc()


def unregister() -> None:
    """
    Unregister all addon components and cleanup.
    
    Cleanly unregisters all classes and cleans up resources.
    """
    try:
        # Import modules
        from . import operators
        from . import properties
        from . import panels
        
        # Stop any running gesture engine
        # (The modal operator will handle cleanup when cancelled)
        
        # Unregister in reverse order
        panels.unregister()
        operators.unregister()
        properties.unregister()
        
        print("[3DX] Addon unregistered successfully")
        
    except Exception as e:
        print(f"[3DX] Unregistration error: {e}")


if __name__ == "__main__":
    register()
