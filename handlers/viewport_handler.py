"""
Viewport Handler

Direct viewport manipulation using Blender API (no sockets).
Handles rotation and panning gestures with Pydantic validation.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from typing import Dict, Any
import bpy
from bpy.types import Context
from pydantic import BaseModel, Field

from handlers.handler_base import BaseHandler, HandlerConfig
import config


class ViewportGestureData(BaseModel):
    """Data required for viewport manipulation."""
    dx: float
    dy: float
    
    class Config:
        extra = "ignore"  # Ignore extra fields like confidence


class ViewportHandler(BaseHandler):
    """
    Handle viewport rotation and panning gestures.
    """
    
    def can_handle(self, gesture: str) -> bool:
        return gesture in [config.GESTURE_PINCH, config.GESTURE_V_MOVE]
    
    def handle(self, context: Context, gesture: str, data: Dict[str, Any]) -> None:
        """
        Execute viewport manipulation.
        """
        if not self.is_enabled():
            return
            
        try:
            # Validate data using Pydantic
            validated_data = ViewportGestureData(**data)
            
            if gesture == config.GESTURE_PINCH:
                self._rotate_viewport(context, validated_data)
            elif gesture == config.GESTURE_V_MOVE:
                self._pan_viewport(context, validated_data)
                
        except Exception as e:
            print(f"[3DX] Viewport handler error: {e}")
    
    def _rotate_viewport(self, context: Context, data: ViewportGestureData) -> None:
        """
        Rotate viewport using orbit-style rotation.
        
        Args:
            context: Blender context
            data: Validated gesture data with dx, dy
        """
        # Get 3D view region
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        # Get region 3D data
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                rv3d = space.region_3d
                                
                                # Apply rotation
                                # dx controls horizontal rotation (around Z axis)
                                # dy controls vertical rotation (around X axis)
                                
                                # Get sensitivity from preferences
                                # Compute package name from module path
                                addon_name = __name__.split('.')[0]
                                prefs = context.preferences.addons[addon_name].preferences
                                sensitivity = prefs.rotation_sensitivity
                                
                                # Scale deltas
                                rotation_x = -data.dy * sensitivity * 10.0
                                rotation_z = data.dx * sensitivity * 10.0
                                
                                # Use Blender's override to perform view rotation
                                with context.temp_override(area=area, region=region, space=space):
                                    # Rotate view
                                    try:
                                        bpy.ops.view3d.rotate(
                                            type='TRACKBALLSTART'
                                        )
                                        
                                        # Apply orbit-style rotation
                                        import math
                                        if abs(rotation_z) > 0.001:
                                            bpy.ops.view3d.view_orbit(angle=rotation_z, type='ORBITZ')
                                        if abs(rotation_x) > 0.001:
                                            bpy.ops.view3d.view_orbit(angle=rotation_x, type='ORBITX')
                                            
                                    except Exception as e:
                                        print(f"[3DX] Rotation error: {e}")
                                
                                return
    
    def _pan_viewport(self, context: Context, data: ViewportGestureData) -> None:
        """
        Pan viewport camera.
        
        Args:
            context: Blender context
            data: Validated gesture data with dx, dy
        """
        # Get 3D view
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                # Get sensitivity
                                addon_name = __name__.split('.')[0]
                                prefs = context.preferences.addons[addon_name].preferences
                                sensitivity = prefs.pan_sensitivity
                                
                                # Scale deltas - multiply by region size for pixel-based movement
                                delta_x = data.dx * sensitivity * region.width
                                delta_y = -data.dy * sensitivity * region.height
                                
                                # Use Blender's pan operator
                                with context.temp_override(area=area, region=region, space=space):
                                    try:
                                        bpy.ops.view3d.move(
                                            'EXEC_DEFAULT',
                                            x=int(delta_x),
                                            y=int(delta_y)
                                        )
                                    except Exception as e:
                                        print(f"[3DX] Pan error: {e}")
                                
                                return

