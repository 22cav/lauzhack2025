"""
UI Panels

All UI panels for gesture control with type-safe layout code.
"""

import sys
import os
import bpy
from bpy.types import Panel, Context, UILayout

class VIEW3D_PT_GestureControl(Panel):
    """Main gesture control panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "3DX"
    bl_label = "Gesture Control"
    
    def draw(self, context):
        """
        Draws the layout using the UILayout API provided in documentation.
        """
        layout = self.layout
        
        # Safety check
        if not hasattr(context.scene, "gesture_state"):
            layout.label(text="Properties not registered", icon='ERROR')
            return
            
        # Use the correct property group from properties.py
        state = context.scene.gesture_state
        
        # --- STATUS SECTION ---
        box = layout.box()
        col = box.column(align=True)
        
        if state.is_running:
            if state.is_paused:
                col.label(text="PAUSED", icon='PAUSE')
                col.label(text="Gestures suspended")
            else:
                col.label(text="ACTIVE", icon='PLAY')
                col.label(text="Detecting gestures...")
        else:
            col.label(text="STOPPED", icon='SNAP_FACE')
            col.label(text="Ready to launch")
            
        layout.separator()
        
        # --- CONTROLS SECTION ---
        box = layout.box()
        col = box.column(align=True)
        
        if not state.is_running:
            row = col.row(align=True)
            row.scale_y = 1.5 
            
            # Start Button
            row.operator("gesture.start", text="Start Engine", icon='PLAY')
            
            # Test Camera Button
            row = col.row()
            row.operator("gesture.test_camera", text="Test Camera", icon='CAMERA_DATA')
        else:
            row = col.row(align=True)
            row.scale_y = 1.5
            
            # Stop Button
            row.operator("gesture.stop", text="Stop", icon='QUIT')
            
            # Pause/Resume Button
            icon = 'PLAY' if state.is_paused else 'PAUSE'
            text = "Resume" if state.is_paused else "Pause"
            row.operator("gesture.toggle_pause", text=text, icon=icon)

        # --- STATISTICS SECTION ---
        if state.is_running:
            layout.separator()
            box = layout.box()
            
            # Header
            row = box.row()
            row.label(text="Live Statistics", icon='GRAPH')
            
            # FPS Row
            row = box.row()
            row.label(text="FPS:")
            row.label(text=f"{state.current_fps:.1f}")
            
            # Frames Row
            row = box.row()
            row.label(text="Frames:")
            row.label(text=str(state.frames_processed))
            
            box.separator()
            
            # Gesture info
            if state.last_gesture != "None":
                row = box.row()
                row.label(text="Gesture:", icon='HAND')
                row.label(text=state.last_gesture)
                
                row = box.row()
                row.label(text="Confidence:")
                row.label(text=f"{state.last_confidence * 100:.0f}%")


class VIEW3D_PT_GestureSettings(Panel):
    """Gesture settings panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "3DX"
    bl_label = "Settings"
    bl_parent_id = "VIEW3D_PT_GestureControl"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Get addon preferences
        # We need to use the package name to find the addon
        package_name = __package__ if __package__ else "3dx"
        if package_name in context.preferences.addons:
            prefs = context.preferences.addons[package_name].preferences
        else:
            layout.label(text="Preferences not found", icon='ERROR')
            return
        
        # --- CAMERA ---
        box = layout.box()
        box.label(text="Camera", icon='CAMERA_DATA')
        box.prop(prefs, "camera_index")
        
        # --- SENSITIVITY ---
        box = layout.box()
        box.label(text="Sensitivity", icon='DRIVER')
        col = box.column(align=True)
        col.prop(prefs, "rotation_sensitivity", slider=True)
        col.prop(prefs, "pan_sensitivity", slider=True)
        
        # --- DISPLAY ---
        box = layout.box()
        box.label(text="Display", icon='WINDOW')
        col = box.column(align=True)
        col.prop(prefs, "show_preview")
        col.prop(prefs, "show_debug")
        
        # --- ADVANCED ---
        box = layout.box()
        box.label(text="Advanced", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(prefs, "frame_rate")
        col.prop(prefs, "min_confidence", slider=True)


class VIEW3D_PT_GestureHelp(Panel):
    """Help and documentation panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "3DX"
    bl_label = "Help"
    bl_parent_id = "VIEW3D_PT_GestureControl"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # --- GESTURE LIST ---
        box = layout.box()
        box.label(text="Gestures", icon='INFO')
        
        col = box.column()
        col.label(text="🤏 Pinch & Drag: Rotate View")
        col.label(text="✌️ V-Gesture: Pan View")
        col.label(text="🖐️ Open Palm: Play Animation")
        col.label(text="✊ Closed Fist: Stop Animation")
        
        layout.separator()
        
        # --- TIPS ---
        box = layout.box()
        box.label(text="Tips", icon='LIGHT')
        col = box.column()
        col.label(text="• Ensure good lighting")
        col.label(text="• Keep hand visible")
        
        layout.separator()
        layout.operator("gesture.show_help", text="Show Full Help", icon='HELP')

# ------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------

classes = (
    VIEW3D_PT_GestureControl,
    VIEW3D_PT_GestureSettings,
    VIEW3D_PT_GestureHelp,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)