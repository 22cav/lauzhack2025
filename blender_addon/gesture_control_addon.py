bl_info = {
    "name": "Gesture Control Center (Mac Fix)",
    "author": "Lauzhack Team",
    "version": (2, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Gesture",
    "description": "Control center with macOS Camera Permission Fix",
    "category": "3D View",
}

import bpy
import socket
import threading
import json
import mathutils
import subprocess
import sys
import os
import time
from enum import Enum

# Global state
gesture_listener = None
gesture_process = None

class Modality(Enum):
    CONTROL = "Control"
    NAVIGATION = "Navigation"

class ModalityManager:
    def __init__(self):
        self.active_modality = Modality.CONTROL
        self.modalities = [Modality.CONTROL, Modality.NAVIGATION]
    
    def set_modality(self, modality: Modality):
        if modality in self.modalities:
            self.active_modality = modality
            return True
        return False
    
    def get_modality_name(self):
        return self.active_modality.value
    
    def get_available_modalities(self):
        return [(m.value, m.value, f"{m.value} modality") for m in self.modalities]

# --- Configuration & Settings ---

class GestureAddonProperties(bpy.types.PropertyGroup):
    """Scene properties for gesture control settings."""
    
    python_path: bpy.props.StringProperty(
        name="Python Interpreter",
        description="Path to the Python executable with libraries installed",
        default='/opt/homebrew/Caskroom/miniconda/base/envs/lauzhack/bin/python', # Tenta di usare il python corrente come fallback
        subtype='FILE_PATH'
    )
    
    script_path: bpy.props.StringProperty(
        name="Orchestrator Script",
        description="Path to main_orchestrator.py",
        default='/Users/matte/MDS/Personal/lauzhack/main_orchestrator.py',
        subtype='FILE_PATH'
    )
    
    camera_index: bpy.props.IntProperty(
        name="Camera Index",
        default=0,
        min=0
    )
    
    port: bpy.props.IntProperty(
        name="Port",
        default=8888,
        min=1024, max=65535
    )
    
    rotation_sensitivity: bpy.props.FloatProperty(name="Rot Sens", default=0.5, min=0.001, max=2.0, precision=3)
    pan_sensitivity: bpy.props.FloatProperty(name="Pan Sens", default=0.1, min=0.001, max=1.0, precision=3)

# --- Process Management ---

def get_paths(context):
    """Get paths from settings."""
    props = context.scene.gesture_props
    python_path = props.python_path
    script_path = props.script_path
    project_root = os.path.dirname(script_path) if script_path else ""
    return python_path, script_path, project_root

def start_engine_process(context):
    """Start the external Python orchestrator process."""
    global gesture_process
    
    props = context.scene.gesture_props
    python_path, script_path, project_path = get_paths(context)
    
    # Validation
    if not os.path.exists(python_path):
        print(f"[ERROR] Python not found at: {python_path}")
        return False
    if not os.path.exists(script_path):
        print(f"[ERROR] Script not found at: {script_path}")
        return False

    config_path = os.path.join(project_path, "config", "blender_mode.yaml")
    
    print(f"[Gesture Control] Launching from: {project_path}")
    
    # --- MAC OS PERMISSION FIX ---
    # Invece di subprocess.Popen diretto, usiamo 'osascript' per dire al Terminale di lanciare il comando.
    # Questo garantisce l'accesso alla Camera.
    
    if sys.platform == "darwin":
        try:
            # Costruiamo il comando shell intero
            # Usiamo 'cd' per andare nella cartella del progetto, poi lanciamo python
            cmd_str = f"cd \\\"{project_path}\\\"; \\\"{python_path}\\\" -u \\\"{script_path}\\\" --config \\\"{config_path}\\\" --debug"
            
            # AppleScript per aprire una nuova finestra/tab di terminale ed eseguire
            apple_script = f"""
            tell application "Terminal"
                do script "{cmd_str}"
                activate
            end tell
            """
            
            subprocess.run(["osascript", "-e", apple_script], check=True)
            
            print("[Gesture Control] Launched via External Terminal (Check the new window!)")
            # Nota: Non possiamo tracciare il PID facilmente con questo metodo, 
            # quindi il pulsante "Stop" potrebbe non funzionare perfettamente se non implementiamo un kill by port.
            # Per ora, settiamo gesture_process a True dummy per aggiornare la UI.
            gesture_process = "EXTERNAL_TERMINAL" 
            return True
            
        except Exception as e:
            print(f"[Gesture Control] MacOS Launch Error: {e}")
            return False
            
    else:
        # --- WINDOWS / LINUX (Metodo Standard) ---
        try:
            cmd = [python_path, "-u", script_path, "--config", config_path, "--debug"]
            gesture_process = subprocess.Popen(cmd, cwd=project_path)
            print(f"[Gesture Control] Engine started (PID: {gesture_process.pid})")
            return True
        except Exception as e:
            print(f"[Gesture Control] Launch Error: {e}")
            return False

def stop_engine_process():
    """Stop the external process."""
    global gesture_process
    
    if gesture_process == "EXTERNAL_TERMINAL":
        print("[Gesture Control] Running in external terminal. Please close the Terminal window manually.")
        gesture_process = None
        return

    if gesture_process == "MANUAL_CONNECTION":
        print("[Gesture Control] Disconnecting from manual session.")
        gesture_process = None
        return

    if gesture_process:
        print(f"[Gesture Control] Stopping engine...")
        gesture_process.terminate()
        gesture_process = None

# --- Socket Listener (Invariato ma pulito) ---

class GestureControlListener:
    def __init__(self, port=8888):
        self.port = port
        self.server = None
        self.running = False
        self.active = False
        self.thread = None
        self.modality_manager = ModalityManager()
        
    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print(f"[Listener] Started on {self.port}")
        
    def stop(self):
        self.running = False
        if self.server:
            try: self.server.close()
            except: pass
    
    def toggle_active(self):
        self.active = not self.active
        return self.active
        
    def _listen(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('localhost', self.port))
            self.server.listen(5)
            
            while self.running:
                try:
                    self.server.settimeout(1.0)
                    try: client, addr = self.server.accept()
                    except socket.timeout: continue
                    
                    while self.running:
                        try:
                            data = client.recv(2048)
                            if not data: break
                            decoded = data.decode('utf-8')
                            for part in decoded.split('\n'):
                                if not part.strip(): continue
                                try:
                                    command = json.loads(part)
                                    print(f"[Listener] Received command: {command}")
                                    # Schedule execution in main thread
                                    bpy.app.timers.register(lambda cmd=command: self._execute_in_main_thread(cmd), first_interval=0.0)
                                except json.JSONDecodeError: pass
                        except Exception: break
                    client.close()
                except Exception as e:
                    print(f"Connection error: {e}")
        except Exception as e:
            print(f"Server error: {e}")
            self.running = False

    def _execute_in_main_thread(self, command):
        print(f"[Execute] Command={command.get('command')}")
        
        cmd_type = command.get('command')
        
        # Handle all commands regardless of modality
        # This matches the automatic modality switching in the gesture input
        if cmd_type == 'rotate_viewport':
            print(f"[Execute] Rotating viewport: dx={command.get('dx')}, dy={command.get('dy')}")
            self._rotate_viewport(command)
            
        elif cmd_type == 'pan_viewport':
            print(f"[Execute] Panning viewport: dx={command.get('dx')}, dy={command.get('dy')}")
            self._pan_viewport(command)
            
        elif cmd_type == 'play_animation': 
            if not bpy.context.screen.is_animation_playing:
                print(f"[Execute] Playing animation")
                bpy.ops.screen.animation_play()
                
        elif cmd_type == 'stop_animation': 
            if bpy.context.screen.is_animation_playing:
                print(f"[Execute] Stopping animation")
                bpy.ops.screen.animation_cancel()
                
        return None  # Unregister timer

    def _rotate_viewport(self, command):
        """Simplified viewport rotation."""
        dx, dy = command.get('dx', 0), command.get('dy', 0)
        sens = bpy.context.scene.gesture_props.rotation_sensitivity
        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                rv3d = area.spaces.active.region_3d
                
                # Simple rotation around Z-axis (horizontal) and local X-axis (vertical)
                rot_z = mathutils.Quaternion((0, 0, 1), dx * sens)
                
                # Get the view's right vector for vertical rotation
                view_matrix = rv3d.view_matrix.inverted()
                right_vector = view_matrix.col[0].to_3d().normalized()
                rot_x = mathutils.Quaternion(right_vector, -dy * sens)
                
                # Apply combined rotation
                rv3d.view_rotation = rot_z @ rot_x @ rv3d.view_rotation
                
                area.tag_redraw()
                break

    def _pan_viewport(self, command):
        """Simplified viewport panning."""
        dx, dy = command.get('dx', 0), command.get('dy', 0)
        sens = bpy.context.scene.gesture_props.pan_sensitivity
        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                rv3d = area.spaces.active.region_3d
                
                # Simple direct translation
                rv3d.view_location.x -= dx * sens
                rv3d.view_location.z += dy * sens
                
                area.tag_redraw()
                break

# --- Operators ---

class GESTURE_OT_StartEngine(bpy.types.Operator):
    bl_idname = "gesture.start_engine"
    bl_label = "Start Engine"
    
    def execute(self, context):
        global gesture_listener
        if gesture_listener is None:
            gesture_listener = GestureControlListener(port=context.scene.gesture_props.port)
        if not gesture_listener.running:
            gesture_listener.start()
            
        if start_engine_process(context):
            self.report({'INFO'}, "Launched via Terminal")
        else:
            self.report({'ERROR'}, "Failed to launch")
        return {'FINISHED'}

class GESTURE_OT_ConnectManual(bpy.types.Operator):
    """Connect to an already running engine."""
    bl_idname = "gesture.connect_manual"
    bl_label = "Connect Only"
    
    def execute(self, context):
        global gesture_listener, gesture_process
        
        # Start Listener
        if gesture_listener is None:
            gesture_listener = GestureControlListener(port=context.scene.gesture_props.port)
        if not gesture_listener.running:
            gesture_listener.start()
            
        # Activate gestures automatically
        gesture_listener.active = True
            
        # Set dummy process state
        gesture_process = "MANUAL_CONNECTION"
        
        self.report({'INFO'}, "Connected (Manual Mode)")
        return {'FINISHED'}

class GESTURE_OT_StopEngine(bpy.types.Operator):
    bl_idname = "gesture.stop_engine"
    bl_label = "Stop Engine"
    def execute(self, context):
        stop_engine_process()
        if gesture_listener: gesture_listener.stop()
        return {'FINISHED'}

class GESTURE_OT_ToggleActive(bpy.types.Operator):
    bl_idname = "gesture.toggle_active"
    bl_label = "Toggle"
    def execute(self, context):
        if gesture_listener: gesture_listener.toggle_active()
        return {'FINISHED'}

class GESTURE_OT_SelectModality(bpy.types.Operator):
    bl_idname = "gesture.select_modality"
    bl_label = "Modality"
    modality: bpy.props.EnumProperty(items=lambda s,c: gesture_listener.modality_manager.get_available_modalities() if gesture_listener else [("NONE","None","")])
    def execute(self, context):
        if gesture_listener:
            for m in Modality:
                if m.value == self.modality: gesture_listener.modality_manager.set_modality(m)
        return {'FINISHED'}

# --- UI Panel ---

class VIEW3D_PT_GestureControl(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gesture"
    bl_label = "Gesture Control"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.gesture_props
        global gesture_listener, gesture_process
        
        is_running = (gesture_process is not None)
        
        # Status
        box = layout.box()
        if is_running:
            if gesture_process == "MANUAL_CONNECTION":
                box.label(text="Manual Connection: ACTIVE", icon='LINKED')
            elif gesture_process == "EXTERNAL_TERMINAL":
                box.label(text="External Process: RUNNING", icon='CHECKMARK')
                box.label(text="(Managed by Terminal App)", icon='INFO')
            else:
                box.label(text="Process: RUNNING", icon='CHECKMARK')
        else:
            box.label(text="System: OFFLINE", icon='ERROR')

        # Controls
        row = layout.row()
        if not is_running:
            row.operator("gesture.start_engine", icon='PLAY')
            row.operator("gesture.connect_manual", icon='LINKED')
        else:
            row.operator("gesture.stop_engine", text="Disconnect / Stop", icon='QUIT')
            
            row = layout.row()
            if gesture_listener and gesture_listener.active:
                row.operator("gesture.toggle_active", text="Pause Gestures", icon='PAUSE')
            else:
                row.operator("gesture.toggle_active", text="Resume Gestures", icon='PLAY')
                
            # Modality
            box = layout.box()
            row = box.row()
            if gesture_listener:
                row.label(text=f"Mode: {gesture_listener.modality_manager.get_modality_name()}")
                row.operator("gesture.select_modality", text="Switch")

        # Configuration
        layout.separator()
        box = layout.box()
        box.label(text="Configuration", icon='PREFERENCES')
        box.prop(props, "python_path")
        box.prop(props, "script_path")
        box.prop(props, "port")
        box.prop(props, "camera_index")
        
        layout.separator()
        box = layout.box()
        box.label(text="Sensitivity", icon='DRIVER')
        box.prop(props, "rotation_sensitivity")
        box.prop(props, "pan_sensitivity")

# --- Registration ---

classes = (GestureAddonProperties, GESTURE_OT_StartEngine, GESTURE_OT_ConnectManual, 
           GESTURE_OT_StopEngine, GESTURE_OT_ToggleActive, GESTURE_OT_SelectModality, 
           VIEW3D_PT_GestureControl)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.gesture_props = bpy.props.PointerProperty(type=GestureAddonProperties)

def unregister():
    stop_engine_process()
    if gesture_listener: gesture_listener.stop()
    del bpy.types.Scene.gesture_props
    for cls in reversed(classes): bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()