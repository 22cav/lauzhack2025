"""
Operators

All gesture control operators with comprehensive type annotations.
"""

from typing import Set, Optional, Dict, Any
import bpy
from bpy.types import Operator, Context, Event
from bpy.props import StringProperty

# Will be set after gesture_engine module is created
GestureEngine = None  # type: Optional[type]


class GESTURE_OT_Start(Operator):
    """Start gesture recognition system"""
    bl_idname: str = "gesture.start"
    bl_label: str = "Start Gesture Control"
    bl_description: str = "Start gesture recognition and control"
    bl_options: Set[str] = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Start the gesture control system.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
            
        #TODO: Implement start logic
        1. Check if already running
        2. Validate camera is available
        3. Call GESTURE_OT_Run operator to start modal
        4. Update UI state
        5. Show success/error message
        """
        state = context.scene.gesture_state
        
        if state.is_running:
            self.report({'WARNING'}, "Gesture control already running")
            return {'CANCELLED'}
        
        # Start the modal operator
        bpy.ops.gesture.run()
        
        return {'FINISHED'}


class GESTURE_OT_Stop(Operator):
    """Stop gesture recognition system"""
    bl_idname: str = "gesture.stop"
    bl_label: str = "Stop Gesture Control"
    bl_description: str = "Stop gesture recognition and control"
    bl_options: Set[str] = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Stop the gesture control system.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
            
        #TODO: Implement stop logic
        1. Check if running
        2. Set state.is_running = False (modal operator will cleanup)
        3. Reset statistics
        4. Show confirmation message
        """
        state = context.scene.gesture_state
        
        if not state.is_running:
            self.report({'WARNING'}, "Gesture control not running")
            return {'CANCELLED'}
        
        # Signal modal operator to stop
        state.is_running = False
        state.is_paused = False
        
        self.report({'INFO'}, "Gesture control stopped")
        return {'FINISHED'}


class GESTURE_OT_TogglePause(Operator):
    """Pause/resume gesture recognition"""
    bl_idname: str = "gesture.toggle_pause"
    bl_label: str = "Toggle Pause"
    bl_description: str = "Pause or resume gesture recognition"
    bl_options: Set[str] = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Toggle pause state.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
        """
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
    bl_idname: str = "gesture.run"
    bl_label: str = "Run Gesture Engine"
    bl_description: str = "Run gesture recognition engine (modal)"
    bl_options: Set[str] = {'INTERNAL'}
    
    _timer: Optional[Any] = None
    _engine: Optional[Any] = None
    
    def modal(self, context: Context, event: Event) -> Set[str]:
        """
        Process gestures every frame.
        
        Args:
            context: Blender context
            event: Event data
            
        Returns:
            Set[str]: Modal operator status
            
        #TODO: Implement modal processing loop
        1. Check for TIMER event
        2. If state.is_running is False, cleanup and cancel
        3. If state.is_paused, skip processing but continue
        4. Process one frame with engine.process_frame()
        5. Handle ESC key to stop
        6. Return {'PASS_THROUGH'} to allow other operators
        """
        state = context.scene.gesture_state
        
        # Check if stopped externally
        if not state.is_running:
            self.cancel(context)
            return {'CANCELLED'}
        
        # Handle timer event
        if event.type == 'TIMER':
            if not state.is_paused and self._engine:
                # #TODO: Process frame
                # self._engine.process_frame(context)
                pass
            return {'PASS_THROUGH'}
        
        # Allow ESC to stop
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Initialize and start modal operation.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
            
        #TODO: Implement engine initialization
        1. Import GestureEngine
        2. Create engine instance with context
        3. Call engine.start() - opens camera, initializes MediaPipe
        4. If start fails, show error and cancel
        5. Register modal handler
        6. Register timer (interval from config)
        7. Update state.is_running = True
        8. Return {'RUNNING_MODAL'}
        """
        from . import gesture_engine
        
        # Create engine instance
        self._engine = gesture_engine.GestureEngine(context)
        
        # Try to start engine
        success, message = self._engine.start()
        
        if not success:
            self.report({'ERROR'}, f"Failed to start: {message}")
            return {'CANCELLED'}
        
        # Register modal handler
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.033, window=context.window)  # ~30 FPS
        wm.modal_handler_add(self)
        
        # Update state
        context.scene.gesture_state.is_running = True
        context.scene.gesture_state.camera_ready = True
        
        self.report({'INFO'}, "Gesture control started")
        return {'RUNNING_MODAL'}
    
    def cancel(self, context: Context) -> None:
        """
        Cleanup when modal operator ends.
        
        Args:
            context: Blender context
            
        #TODO: Implement cleanup
        1. Stop engine (releases camera, MediaPipe)
        2. Remove timer
        3. Update state
        4. Clear statistics
        """
        # Stop engine
        if self._engine:
            self._engine.stop()
            self._engine = None
        
        # Remove timer
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        
        # Update state
        state = context.scene.gesture_state
        state.is_running = False
        state.is_paused = False
        state.camera_ready = False


class GESTURE_OT_TestCamera(Operator):
    """Test camera connectivity"""
    bl_idname: str = "gesture.test_camera"
    bl_label: str = "Test Camera"
    bl_description: str = "Test if camera can be opened"
    bl_options: Set[str] = {'REGISTER'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Test camera availability.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
            
        #TODO: Implement camera test
        1. Get camera_index from preferences
        2. Call utils.validate_camera()
        3. Show success or error message
        4. Update UI with result
        """
        from . import utils
        
        prefs = context.preferences.addons[__package__].preferences
        camera_index = prefs.camera_index
        
        if utils.validate_camera(camera_index):
            self.report({'INFO'}, f"Camera {camera_index} OK")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Camera {camera_index} not available")
            return {'CANCELLED'}


class GESTURE_OT_ResetSettings(Operator):
    """Reset all settings to defaults"""
    bl_idname: str = "gesture.reset_settings"
    bl_label: str = "Reset to Defaults"
    bl_description: str = "Reset all settings to default values"
    bl_options: Set[str] = {'REGISTER', 'UNDO'}
    
    def execute(self, context: Context) -> Set[str]:
        """
        Reset settings to defaults.
        
        Args:
            context: Blender context
            
        Returns:
            Set[str]: Operator return status
            
        #TODO: Implement settings reset
        1. Get preferences
        2. Set each property to default from config.DEFAULT_SETTINGS
        3. Show confirmation message
        """
        from . import config
        
        prefs = context.preferences.addons[__package__].preferences
        
        # Reset to defaults
        for key, value in config.DEFAULT_SETTINGS.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        self.report({'INFO'}, "Settings reset to defaults")
        return {'FINISHED'}


class GESTURE_OT_ShowHelp(Operator):
    """Show help dialog"""
    bl_idname: str = "gesture.show_help"
    bl_label: str = "Help"
    bl_description: str = "Show gesture control help"
    bl_options: Set[str] = {'REGISTER'}
    
    message: StringProperty = StringProperty(  # type: ignore
        default=(
            "3DX Gesture Control Help\n"
            "\n"
            "Gestures:\n"
            "  🤏 Pinch & Drag - Rotate viewport\n"
            "  ✌️ V-Gesture & Move - Pan camera\n"
            "  🖐️ Open Palm - Play animation\n"
            "  ✊ Closed Fist - Stop animation\n"
            "\n"
            "Tips:\n"
            "  - Ensure good lighting\n"
            "  - Keep hand visible to camera\n"
            "  - Adjust sensitivity in settings\n"
            "  - Check camera permissions if issues\n"
        )
    )
    
    def execute(self, context: Context) -> Set[str]:
        """Show help message."""
        self.report({'INFO'}, self.message)
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        """Show popup dialog."""
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context: Context) -> None:
        """Draw help dialog."""
        layout = self.layout
        for line in self.message.split('\n'):
            layout.label(text=line)


# ============================================================================
# Registration
# ============================================================================

classes: tuple = (
    GESTURE_OT_Start,
    GESTURE_OT_Stop,
    GESTURE_OT_TogglePause,
    GESTURE_OT_Run,
    GESTURE_OT_TestCamera,
    GESTURE_OT_ResetSettings,
    GESTURE_OT_ShowHelp,
)


def register() -> None:
    """Register operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
