"""
Blender Gesture Control Addon - Full Control Interface

This addon runs inside Blender and acts as the control center for the gesture recognition system.
It manages the external Python process, handles configuration, and executes gesture commands.

Features:
- 🚀 Start/Stop the external gesture engine directly from Blender
- ⚙️ Configure sensitivity, camera index, and port
- 🎮 Toggle gesture recognition and switch modalities
- 🔄 Auto-reconnect and robust error handling
"""

bl_info = {
    "name": "Gesture Control Center",
    "author": "Lauzhack Team",
    "version": (2, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Gesture",
    "description": "Complete control center for webcam gesture recognition",
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
from bpy.app.handlers import persistent
from enum import Enum

# Global state
gesture_listener = None
gesture_process = None

class Modality(Enum):
    """Available gesture modalities."""
    CONTROL = "Control"
    NAVIGATION = "Navigation"

class ModalityManager:
    """Manages modality state and routing."""
    
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
    
    # Engine Settings
    python_path: bpy.props.StringProperty(
        name="Python Path",
        description="Path to Python executable (must have dependencies installed)",
        default='/opt/homebrew/Caskroom/miniconda/base/envs/lauzhack/bin/python', # Default to Blender's python, user might need to change this
        subtype='FILE_PATH'
    )
    
    project_path: bpy.props.StringProperty(
        name="Project Path",
        description="Path to the Lauzhack project root",
        default="/Users/matte/MDS/Personal/lauzhack", # Hardcoded default for convenience
        subtype='DIR_PATH'
    )
    
    camera_index: bpy.props.IntProperty(
        name="Camera Index",
        description="Index of the webcam to use",
        default=0,
        min=0
    )
    
    # Connection Settings
    port: bpy.props.IntProperty(
        name="Port",
        description="Port for socket communication",
        default=8888,
        min=1024,
        max=65535
    )
    
    # Sensitivity Settings
    rotation_sensitivity: bpy.props.FloatProperty(
        name="Rotation Sensitivity",
        description="Sensitivity for viewport rotation",
        default=0.02,
        min=0.001,
        max=0.1,
        precision=3
    )
    
    pan_sensitivity: bpy.props.FloatProperty(
        name="Pan Sensitivity",
        description="Sensitivity for viewport panning",
        default=0.005,
        min=0.001,
        max=0.1,
        precision=3
    )

# --- Process Management ---

def update_config_file(context):
    """Update the external YAML config file with current Blender settings."""
    props = context.scene.gesture_props
    config_path = os.path.join(props.project_path, "config", "blender_mode.yaml")
    
    try:
        # We read the file and replace specific lines to avoid pyyaml dependency in Blender
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if "blender_port:" in line:
                new_lines.append(f"    blender_port: {props.port}\n")
            elif "camera_index:" in line:
                new_lines.append(f"    camera_index: {props.camera_index}\n")
            else:
                new_lines.append(line)
                
        with open(config_path, 'w') as f:
            f.writelines(new_lines)
            
        print(f"[Gesture Control] Updated config file: {config_path}")
        return True
    except Exception as e:
        print(f"[Gesture Control] Failed to update config: {e}")
        return False

def start_engine_process(context):
    """Start the external Python orchestrator process with DEBUGGING."""
    global gesture_process
    
    # Se è già attivo, esci
    if gesture_process and gesture_process.poll() is None:
        print("[Gesture Control] Engine already running")
        return True
    
    props = context.scene.gesture_props
    script_path = os.path.join(props.project_path, "main_orchestrator.py")
    config_path = os.path.join(props.project_path, "config", "blender_mode.yaml")
    
    # Update config first
    update_config_file(context)
    
    # Verifica che i file esistano prima di lanciare
    if not os.path.exists(props.python_path):
        print(f"[ERRORE] Python non trovato al percorso: {props.python_path}")
        return False
    if not os.path.exists(script_path):
        print(f"[ERRORE] Script non trovato al percorso: {script_path}")
        return False

    cmd = [
        props.python_path,
        script_path,
        "--config", config_path
    ]
    
    print(f"[Gesture Control] Tentativo di lancio: {' '.join(cmd)}")
    
    try:
        # Launch process catturando gli errori (PIPE)
        gesture_process = subprocess.Popen(
            cmd,
            cwd=props.project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Catturiamo gli errori
            text=True
        )
        
        # --- DEBUG AGGIUNTO ---
        # Aspettiamo un attimo per vedere se crasha subito
        time.sleep(1.0) 
        
        # Controlliamo se è ancora vivo
        if gesture_process.poll() is not None:
            # È MORTO! Leggiamo perché
            stdout, stderr = gesture_process.communicate()
            print("\n" + "="*40)
            print("!!! ERRORE FATALE MOTORE GESTI !!!")
            print("Il processo si è avviato ma si è chiuso subito.")
            print("-" * 20)
            print(f"CODICE DI USCITA: {gesture_process.returncode}")
            print("-" * 20)
            print("ERRORE (STDERR):")
            print(stderr) # <--- QUESTO È QUELLO CHE TI SERVE
            print("-" * 20)
            print("OUTPUT (STDOUT):")
            print(stdout)
            print("="*40 + "\n")
            
            gesture_process = None # Resettiamo la variabile
            return False
        # ----------------------

        print(f"[Gesture Control] Engine started successfully (PID: {gesture_process.pid})")
        return True
        
    except Exception as e:
        print(f"[Gesture Control] Failed to launch engine: {e}")
        return False

def stop_engine_process():
    """Stop the external Python orchestrator process."""
    global gesture_process
    
    if gesture_process:
        print(f"[Gesture Control] Stopping engine (PID: {gesture_process.pid})...")
        gesture_process.terminate()
        try:
            gesture_process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            gesture_process.kill()
        
        gesture_process = None
        print("[Gesture Control] Engine stopped")

# --- Socket Listener ---

class GestureControlListener:
    """Handles socket communication and command execution."""
    
    def __init__(self, port=8888):
        self.port = port
        self.server = None
        self.running = False
        self.active = False  # Gesture recognition active/inactive
        self.thread = None
        self.last_command = "None"
        self.command_count = 0
        self.modality_manager = ModalityManager()
        
    def start(self):
        """Start the gesture listener server."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print(f"[Gesture Control] Listener started on port {self.port}")
        
    def stop(self):
        """Stop the gesture listener server."""
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass
        print("[Gesture Control] Listener stopped")
    
    def toggle_active(self):
        """Toggle gesture recognition active/inactive."""
        self.active = not self.active
        status = "ACTIVE" if self.active else "INACTIVE"
        print(f"[Gesture Control] Gesture recognition {status}")
        return self.active
        
    def _listen(self):
        """Listen for incoming gesture commands."""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('localhost', self.port))
            self.server.listen(5)
            print(f"[Gesture Control] Listening on localhost:{self.port}")
            
            while self.running:
                try:
                    self.server.settimeout(1.0) # Allow checking self.running periodically
                    try:
                        client, addr = self.server.accept()
                    except socket.timeout:
                        continue
                        
                    # print(f"[Gesture Control] Client connected: {addr}")
                    
                    while self.running:
                        try:
                            data = client.recv(1024)
                            if not data:
                                break
                            
                            # Parse JSON command
                            # Handle multiple concatenated JSONs if they arrive together
                            decoded = data.decode('utf-8')
                            for part in decoded.split('\n'):
                                if not part.strip(): continue
                                try:
                                    command = json.loads(part)
                                    self._execute_command(command)
                                except json.JSONDecodeError:
                                    pass
                        except Exception:
                            break
                    
                    client.close()
                            
                except Exception as e:
                    if self.running:
                        print(f"[Gesture Control] Connection error: {e}")
                        
        except Exception as e:
            print(f"[Gesture Control] Server error: {e}")
            self.running = False
            
    def _execute_command(self, command):
        """Execute a gesture command in Blender."""
        # Ignore commands if gesture recognition is inactive
        if not self.active:
            return
        
        cmd_type = command.get('command')
        self.last_command = cmd_type
        self.command_count += 1
        
        # Schedule command execution in main thread
        bpy.app.timers.register(lambda: self._execute_in_main_thread(cmd_type, command), first_interval=0.0)
        
    def _execute_in_main_thread(self, cmd_type, command):
        """Execute command in Blender's main thread (required for operators)."""
        try:
            # Route through modality system
            if self.modality_manager.active_modality == Modality.CONTROL:
                self._execute_control_modality(cmd_type, command)
            elif self.modality_manager.active_modality == Modality.NAVIGATION:
                self._execute_navigation_modality(cmd_type, command)
                
        except Exception as e:
            print(f"[Gesture Control] Execution error: {e}")
            
        return None
    
    def _execute_control_modality(self, cmd_type, command):
        """Execute commands in Control modality."""
        if cmd_type == 'rotate_viewport':
            self._rotate_viewport(command)
        elif cmd_type == 'play_animation':
            self._play_animation()
        elif cmd_type == 'stop_animation':
            self._pause_animation()
    
    def _execute_navigation_modality(self, cmd_type, command):
        """Execute commands in Navigation modality."""
        if cmd_type == 'pan_viewport':
            self._pan_viewport(command)
            
    def _rotate_viewport(self, command):
        """Rotate the 3D viewport based on hand movement (YAW and PITCH)."""
        dx = command.get('dx', 0)
        dy = command.get('dy', 0)
        
        # Use configured sensitivity
        props = bpy.context.scene.gesture_props
        sensitivity = props.rotation_sensitivity
        
        # Get active 3D view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        space = area.spaces.active
                        rv3d = space.region_3d
                        
                        # Apply rotation
                        rotation_pitch = mathutils.Euler((dy * sensitivity, 0, 0))
                        rotation_yaw = mathutils.Euler((0, 0, dx * sensitivity))
                        
                        rv3d.view_rotation = rv3d.view_rotation @ rotation_pitch.to_quaternion()
                        rv3d.view_rotation = rv3d.view_rotation @ rotation_yaw.to_quaternion()
                        
                        area.tag_redraw()
                        break
    
    def _pan_viewport(self, command):
        """Pan the viewport based on V-gesture movement."""
        dx = command.get('dx', 0)
        dy = command.get('dy', 0)
        
        # Use configured sensitivity
        props = bpy.context.scene.gesture_props
        sensitivity = props.pan_sensitivity
        
        # Get active 3D view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                rv3d = space.region_3d
                
                # Pan viewport (move location)
                rv3d.view_location.x -= dx * sensitivity
                rv3d.view_location.z += dy * sensitivity
                
                area.tag_redraw()
                break
        
    def _play_animation(self):
        if not bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        
    def _pause_animation(self):
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel()

# --- Operators ---

class GESTURE_OT_StartEngine(bpy.types.Operator):
    """Start the external gesture recognition engine."""
    bl_idname = "gesture.start_engine"
    bl_label = "Start Engine"
    
    def execute(self, context):
        global gesture_listener
        
        # 1. Start Socket Listener
        if gesture_listener is None:
            gesture_listener = GestureControlListener(port=context.scene.gesture_props.port)
        
        if not gesture_listener.running:
            gesture_listener.start()
            
        # 2. Start External Process
        if start_engine_process(context):
            self.report({'INFO'}, "Gesture Engine Started")
        else:
            self.report({'ERROR'}, "Failed to start engine")
            
        return {'FINISHED'}

class GESTURE_OT_StopEngine(bpy.types.Operator):
    """Stop the external gesture recognition engine."""
    bl_idname = "gesture.stop_engine"
    bl_label = "Stop Engine"
    
    def execute(self, context):
        global gesture_listener
        
        # 1. Stop External Process
        stop_engine_process()
        
        # 2. Stop Socket Listener
        if gesture_listener:
            gesture_listener.stop()
            
        self.report({'INFO'}, "Gesture Engine Stopped")
        return {'FINISHED'}

class GESTURE_OT_ToggleActive(bpy.types.Operator):
    """Toggle gesture recognition active/inactive"""
    bl_idname = "gesture.toggle_active"
    bl_label = "Toggle Active"
    
    def execute(self, context):
        global gesture_listener
        if gesture_listener:
            gesture_listener.toggle_active()
            # Force UI update
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}

class GESTURE_OT_SelectModality(bpy.types.Operator):
    """Select gesture modality"""
    bl_idname = "gesture.select_modality"
    bl_label = "Select Modality"
    
    modality: bpy.props.EnumProperty(
        name="Modality",
        items=lambda self, context: gesture_listener.modality_manager.get_available_modalities() if gesture_listener else [("NONE", "No Listener", "")],
    )
    
    def execute(self, context):
        global gesture_listener
        if gesture_listener:
            for mod in Modality:
                if mod.value == self.modality:
                    gesture_listener.modality_manager.set_modality(mod)
                    self.report({'INFO'}, f"Modality: {mod.value}")
                    break
        return {'FINISHED'}

# --- UI Panel ---

class VIEW3D_PT_GestureControl(bpy.types.Panel):
    """UI panel for gesture control."""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gesture"
    bl_label = "Gesture Control Center"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.gesture_props
        global gesture_listener, gesture_process
        
        # --- Status Indicator ---
        box = layout.box()
        row = box.row()
        
        is_engine_running = gesture_process and gesture_process.poll() is None
        is_listener_running = gesture_listener and gesture_listener.running
        
        if is_engine_running and is_listener_running:
            row.label(text="System Online", icon='CHECKMARK')
            if gesture_listener.active:
                row.label(text="ACTIVE", icon='REC')
            else:
                row.label(text="Standby", icon='PAUSE')
        else:
            row.label(text="System Offline", icon='ERROR')
            
        # --- Main Controls ---
        box = layout.box()
        box.label(text="Engine Control", icon='CONSOLE')
        
        if is_engine_running:
            box.operator("gesture.stop_engine", text="Stop Engine", icon='QUIT')
            
            # Activation Toggle
            row = box.row()
            row.scale_y = 1.5
            if gesture_listener and gesture_listener.active:
                row.operator("gesture.toggle_active", text="Pause Gestures", icon='PAUSE')
            else:
                row.operator("gesture.toggle_active", text="Activate Gestures", icon='PLAY')
                
            # Modality Selector
            box.label(text="Modality:")
            row = box.row()
            if gesture_listener:
                curr_mod = gesture_listener.modality_manager.get_modality_name()
                row.label(text=curr_mod, icon='PRESET')
                row.operator("gesture.select_modality", text="Switch", icon='UV_SYNC_SELECT')
                
        else:
            box.operator("gesture.start_engine", text="Start Engine", icon='PLAY')

        layout.separator()
        
        # --- Settings ---
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        box.prop(props, "rotation_sensitivity")
        box.prop(props, "pan_sensitivity")
        box.prop(props, "camera_index")
        
        # --- Advanced ---
        box = layout.box()
        box.label(text="Advanced", icon='SETTINGS')
        box.prop(props, "port")
        box.prop(props, "python_path")
        box.prop(props, "project_path")

# --- Registration ---

classes = (
    GestureAddonProperties,
    GESTURE_OT_StartEngine,
    GESTURE_OT_StopEngine,
    GESTURE_OT_ToggleActive,
    GESTURE_OT_SelectModality,
    VIEW3D_PT_GestureControl,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.gesture_props = bpy.props.PointerProperty(type=GestureAddonProperties)
    
    # Auto-detect python path if possible (e.g. if running from venv)
    # This is a best-guess default
    # bpy.context.scene.gesture_props.python_path = sys.executable

def unregister():
    global gesture_listener, gesture_process
    
    if gesture_listener:
        gesture_listener.stop()
    
    if gesture_process:
        try:
            gesture_process.terminate()
        except:
            pass
            
    del bpy.types.Scene.gesture_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
