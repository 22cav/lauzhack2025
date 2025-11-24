"""
3DX - Hand Gesture Control for Blender

A self-contained Blender addon for controlling Blender with hand gestures
detected via webcam using MediaPipe.
"""

from typing import Dict, Any, Optional, List
import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import bpy
from bpy.types import AddonPreferences, PropertyGroup

bl_info = {
    "name": "3DX - Gesture Control",
    "author": "22cav",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > 3DX",
    "description": "Control Blender with hand gestures using webcam",
    "warning": "Requires camera access and dependencies (opencv-python, mediapipe, numpy, pydantic)",
    "doc_url": "https://github.com/22cav/3DX",
    "tracker_url": "https://github.com/22cav/3DX/issues",
    "category": "3D View",
}


def load_dependencies() -> bool:
    """
    Load dependencies with a robust fallback strategy:
    1. Try importing from existing environment
    2. Try installing via pip

    Returns:
        bool: True if dependencies are loaded, False otherwise
    """
    required_modules = {
        "cv2": "opencv-python",
        "mediapipe": "mediapipe",
        "numpy": "numpy",
        "pydantic": "pydantic"
    }

    def check_imports() -> bool:
        """
        Check if all required modules are imported.

        Returns:
            bool: True if all modules are imported, False otherwise
        """
        try:
            import cv2
            import mediapipe
            import numpy
            import pydantic
            return True
        except ImportError:
            return False

    # 1. Try existing environment
    if check_imports():
        return True

    # 2. Try pip install
    print("[3DX] Dependencies missing. Attempting auto-installation...")
    try:
        import subprocess
        import sys
        
        # Build install command
        cmd = [sys.executable, "-m", "pip", "install"]
        for module, package in required_modules.items():
            try:
                __import__(module)
            except ImportError:
                cmd.append(package)
        
        if len(cmd) > 4: # If we have packages to install
            subprocess.check_call(cmd)
            
            # Invalidate caches to ensure new packages are found
            import importlib
            importlib.invalidate_caches()
            
            if check_imports():
                print("[3DX] Dependencies successfully installed and loaded.")
                return True
            else:
                print("[3DX] Installation succeeded but import failed. Please restart Blender.")
                return False
                
    except Exception as e:
        print(f"[3DX] Auto-installation failed: {e}")
        print(f"[3DX] Please manually install: pip install {' '.join(required_modules.values())}")
        return False

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
        # Import modules using relative imports
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
        # Import modules using relative imports
        from . import operators
        from . import properties
        from . import panels
        
        # Unregister in reverse order
        panels.unregister()
        operators.unregister()
        properties.unregister()
        
        print("[3DX] Addon unregistered successfully")
        
    except Exception as e:
        print(f"[3DX] Unregistration error: {e}")


if __name__ == "__main__":
    register()
