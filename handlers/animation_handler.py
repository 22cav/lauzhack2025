"""
Animation Handler

Handle animation playback control gestures with Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any
from bpy.types import Context
import bpy
from pydantic import BaseModel

from handlers.handler_base import BaseHandler, HandlerConfig
import config


class AnimationGestureData(BaseModel):
    """Data for animation control (mostly empty but validates presence)."""
    confidence: float


class AnimationHandler(BaseHandler):
    """
    Handle animation control gestures.
    """
    
    def can_handle(self, gesture: str) -> bool:
        return gesture in [config.GESTURE_PALM, config.GESTURE_FIST]
    
    def handle(self, context: Context, gesture: str, data: Dict[str, Any]) -> None:
        """
        Execute animation control.
        """
        if not self.is_enabled():
            return
            
        try:
            # Validate data
            _ = AnimationGestureData(**data)
            
            if gesture == config.GESTURE_PALM:
                self._play_animation(context)
            elif gesture == config.GESTURE_FIST:
                self._stop_animation(context)
                
        except Exception as e:
            print(f"[3DX] Animation handler error: {e}")
    
    def _play_animation(self, context: Context) -> None:
        if not context.screen.is_animation_playing:
            try:
                bpy.ops.screen.animation_play()
            except Exception as e:
                print(f"[3DX] Animation play error: {e}")
    
    def _stop_animation(self, context: Context) -> None:
        if context.screen.is_animation_playing:
            try:
                bpy.ops.screen.animation_cancel()
            except Exception as e:
                print(f"[3DX] Animation stop error: {e}")
