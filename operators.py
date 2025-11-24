"""
Operators

All gesture control operators with comprehensive type annotations.
"""

import bpy
from bpy.types import Operator, Context, Event
from bpy.props import StringProperty
from typing import Set, Optional, Any

# We use a lazy import inside the operator to prevent circular dependency errors
# during the initial load of the addon.

class GESTURE_OT_Start(Operator):
    """Start gesture recognition system"""
    bl_idname = "gesture.start"
    bl_label = "Start Gesture Control"
    bl_description = "Start gesture recognition and control"
    bl_options = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        # Ensure the property group exists (safety check)
        if not hasattr(context.scene, "gesture_state"):
            self.report({'ERROR'}, "Gesture properties not registered")
            return {'CANCELLED'}

        state = context.scene.gesture_state
        
        if state.is_running:
            self.report({'WARNING'}, "Gesture control already running")
            return {'CANCELLED'}
        
        # Call the modal operator
        bpy.ops.gesture.run('INVOKE_DEFAULT')
        
        return {'FINISHED'}


class GESTURE_OT_Stop(Operator):
    """Stop gesture recognition system"""
    bl_idname = "gesture.stop"
    bl_label = "Stop Gesture Control"
    bl_description = "Stop gesture recognition and control"
    bl_options = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        if not hasattr(context.scene, "gesture_state"):
            return {'CANCELLED'}

        state = context.scene.gesture_state
        
        if not state.is_running:
            self.report({'WARNING'}, "Gesture control not running")
            return {'CANCELLED'}
        
        state.is_running = False
        state.is_paused = False
        
        self.report({'INFO'}, "Gesture control stop signal sent")
        return {'FINISHED'}


class GESTURE_OT_TogglePause(Operator):
    """Pause/resume gesture recognition"""
    bl_idname = "gesture.toggle_pause"
    bl_label = "Toggle Pause"
    bl_description = "Pause or resume gesture recognition"
    bl_options = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        state = context.scene.gesture_state
        
        if not state.is_running:
            self.report({'WARNING'}, "Gesture control not running")
            return {'CANCELLED'}
        
        state.is_paused = not state.is_paused
        
        status = "paused" if state.is_paused else "resumed"
        self.report({'INFO'}, f"Gesture control {status}")
        
        return {'FINISHED'}


class GESTURE_OT_Run(Operator):
    """Modal operator for continuous gesture processing"""
    bl_idname = "gesture.run"
    bl_label = "Run Gesture Engine"
    bl_description = "Run gesture recognition engine (modal)"
    bl_options = {'INTERNAL'}  # INTERNAL hides it from the F3 search menu
    
    # Type hinting for class attributes
    _timer: Optional[Any] = None
    _engine: Optional[Any] = None
    
    def modal(self, context: Context, event: Event) -> Set[str]:
        """
        Process gestures every frame.
        """
        state = context.scene.gesture_state
        
        # 1. STOP CONDITION: Check if stopped via UI (GESTURE_OT_Stop)
        if not state.is_running:
            self.cancel(context)
            return {'CANCELLED'}
        
        # 2. TIMER EVENT: Run computer vision processing
        if event.type == 'TIMER':
            if not state.is_paused and self._engine:
                try:
                    self._engine.process_frame(context)
                except Exception as e:
                    print(f"[Gesture Control] Error: {e}")
            
            # PASS_THROUGH is critical so we don't block the UI
            return {'PASS_THROUGH'}
        
        # 3. EMERGENCY ESCAPE
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        """
        Initialize and start modal operation.
        """
        # Lazy import to avoid circular dependency at module level
        from . import gesture_engine
        
        # Create engine instance
        self._engine = gesture_engine.GestureEngine(context)
        
        # Try to start engine (open camera)
        success, message = self._engine.start()
        
        if not success:
            self.report({'ERROR'}, f"Failed to start: {message}")
            return {'CANCELLED'}
        
        # Register modal timer
        wm = context.window_manager
        # 0.033s is approx 30 FPS. 
        self._timer = wm.event_timer_add(0.033, window=context.window)
        wm.modal_handler_add(self)
        
        # Update state
        context.scene.gesture_state.is_running = True
        context.scene.gesture_state.camera_ready = True
        
        self.report({'INFO'}, "Gesture control engine started")
        return {'RUNNING_MODAL'}
    
    def execute(self, context: Context) -> Set[str]:
        # execute() is called if invoked via script without user interaction
        return self.invoke(context, None)
    
    def cancel(self, context: Context) -> None:
        """
        Cleanup when modal operator ends.
        """
        # Stop engine (release camera)
        if self._engine:
            self._engine.stop()
            self._engine = None
        
        # Remove timer
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        
        # Update state
        if hasattr(context.scene, "gesture_state"):
            state = context.scene.gesture_state
            state.is_running = False
            state.is_paused = False
            state.camera_ready = False
        
        self.report({'INFO'}, "Gesture control engine stopped")


class GESTURE_OT_TestCamera(Operator):
    """Test camera connectivity"""
    bl_idname = "gesture.test_camera"
    bl_label = "Test Camera"
    bl_options = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        # Mock validation logic if utils is not yet available
        try:
            from . import utils
            from . import config
            prefs = context.preferences.addons[__package__].preferences
            idx = prefs.camera_index
            
            if utils.validate_camera(idx):
                self.report({'INFO'}, f"Camera {idx} OK")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Camera {idx} not available")
                return {'CANCELLED'}
        except ImportError:
            self.report({'WARNING'}, "Utils module not found")
            return {'CANCELLED'}


class GESTURE_OT_ShowHelp(Operator):
    """Show help dialog"""
    bl_idname = "gesture.show_help"
    bl_label = "Help"
    bl_options = {'REGISTER'}
    
    # CORRECT SYNTAX: No type hint on the left side for properties
    message: StringProperty(
        name="Message",
        default=(
            "Gestures:\n"
            "  🤏 Pinch & Drag - Rotate viewport\n"
            "  ✌️ V-Gesture & Move - Pan camera\n"
            "  🖐️ Open Palm - Play animation\n"
            "  ✊ Closed Fist - Stop animation"
        ),
        options={'HIDDEN'} # We don't want this animatable
    ) # type: ignore
    
    def execute(self, context: Context) -> Set[str]:
        # If run from search, just print to info
        print(self.message)
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        # If run from button, show popup
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context: Context) -> None:
        layout = self.layout
        # We must manually split lines for labels
        # We access 'self.message' which is a native python string at runtime
        for line in self.message.split('\n'): 
            layout.label(text=line)


# ============================================================================
# Registration
# ============================================================================

classes = (
    GESTURE_OT_Start,
    GESTURE_OT_Stop,
    GESTURE_OT_TogglePause,
    GESTURE_OT_Run,
    GESTURE_OT_TestCamera,
    GESTURE_OT_ShowHelp,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)