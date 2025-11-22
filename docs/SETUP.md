# Setup Guide - Multi-Input Gesture Control System

This guide covers installation and setup of the modern event-driven gesture control system.

> [!NOTE]
> This replaces the old standalone system. For legacy documentation, see [GUIDE_LEGACY.md](GUIDE_LEGACY.md).

## Prerequisites

- **Python**: 3.8 or higher
- **Conda**: Recommended for environment management
- **Webcam**: Built-in or USB camera
- **(Optional) Blender**: 3.0+ for 3D integration
- **(Optional) MX Creative Console**: For button controls

## Quick Installation

```bash
# Create conda environment
conda create -n lauzhack python=3.9 -y
conda activate lauzhack

# Navigate to project root
cd /Users/matte/MDS/Personal/lauzhack

# Install dependencies
pip install -r requirements.txt
```

## Dependencies Installed

- `mediapipe`: Hand/pose tracking ML models
- `opencv-python`: Camera capture
- `pyautogui`: System actions (volume, media)
- `pyyaml`: Configuration parsing
- `pytest`: Unit testing
- `bleak`: Bluetooth support (optional)
- `numpy`: Math operations

## Verification

Test the installation:

```bash
# Run unit tests
python -m pytest tests/ -v

# Quick integration test
python test_quick.py
```

Expected output:
```
================== 8 passed in 0.05s ===================
✅ All tests passed!
```

## Basic Usage

### 1. System Control Mode (Default)

Volume and media control with gestures:

```bash
python main_orchestrator.py --config config/test_gesture_only.yaml
```

**Gestures**:
- 🖐️ Open Palm → Volume up
- ✊ Closed Fist → Volume down
- 👆 Pointing → Play/pause

Press **ESC** in camera window to exit.

### 2. Blender Mode

3D viewport control:

```bash
# Start orchestrator
python main_orchestrator.py --config config/blender_mode.yaml
```

**Gestures**:
- 🤏 Pinch + Drag → Rotate viewport
- 🖐️ Open Palm → Play animation
- ✊ Closed Fist → Pause animation
- 👆 Pointing → Next frame

### 3. Custom Configuration

Edit `config/event_mappings.yaml` to customize behavior:

```yaml
inputs:
  gesture:
    enabled: true
    camera_index: 0           # Try 1, 2 if camera not detected
    pinch_threshold: 0.05     # Lower = more sensitive pinch
    show_preview: true        # Display camera feed

outputs:
  blender:
    enabled: true
    drag_sensitivity: 100.0   # Viewport rotation speed
    mappings:
      PINCH_DRAG: viewport_rotate
      OPEN_PALM: play_animation
  
  system:
    enabled: true
    cooldown: 1.0             # Seconds between actions
    mappings:
      OPEN_PALM: volumeup
      CLOSED_FIST: volumedown
```

## Blender Integration Setup

### Option 1: External Control (Recommended)

1. **Start orchestrator** with Blender config:
   ```bash
   python main_orchestrator.py --config config/blender_mode.yaml
   ```

2. **In Blender**, run the listener script:
   - Open Blender
   - Go to Scripting workspace
   - Copy code from `outputs/blender_output.py` (search for `BLENDER_ADDON_TEMPLATE`)
   - Run the script
   - Socket listener will start on port 8888

3. **Perform gestures** to control Blender

### Option 2: Blender Addon (Future)

Package the system as a Blender addon for tighter integration.

## MX Creative Console Setup

> [!WARNING]
> MX Console support is currently a stub. Requires reverse-engineering the Bluetooth protocol.

To enable (when implemented):

```yaml
inputs:
  mx_console:
    enabled: true
    device_name: "MX Creative Console"
```

## C# Loupedeck Plugin (Legacy)

The system maintains backward compatibility with the existing C# plugin:

1. **Enable Loupedeck output**:
   ```yaml
   outputs:
     loupedeck:
       enabled: true
   ```

2. **Start C# plugin** in Logitech G Hub

3. **Run orchestrator**:
   ```bash
   python main_orchestrator.py
   ```

Gestures will be sent to C# plugin as before.

## Troubleshooting

### Camera Not Detected

```yaml
# Try different camera index in config
inputs:
  gesture:
    camera_index: 1  # Try 0, 1, 2...
```

Or check permissions:
- **macOS**: System Preferences → Security & Privacy → Camera
- **Linux**: Check `/dev/video*` permissions

### Low FPS / Performance

- Close other apps using camera
- Reduce camera resolution in code
- Ensure GPU drivers are updated (MediaPipe uses GPU)

### Gestures Not Detected

- **Lighting**: Face a window or light source
- **Distance**: Keep hand 30-60cm from camera
- **Gesture clarity**: Extend/close fingers fully
- **Lower threshold**:
  ```yaml
  inputs:
    gesture:
      min_detection_confidence: 0.3  # Lower = more sensitive
  ```

### Blender Not Receiving Events

- Verify Blender listener script is running
- Check port 8888 not blocked by firewall
- Look for connection errors in orchestrator logs:
  ```
  INFO:outputs.blender_output:Connected to Blender at localhost:8888
  ```

### Module Import Errors

```bash
# Ensure conda environment is activated
conda activate lauzhack

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Advanced Configuration

### Adding Custom Gestures

Edit `inputs/gesture_input.py` → `_detect_basic_gesture()`:

```python
def _detect_basic_gesture(self, hand_landmarks) -> str:
    # ... existing code ...
    
    # Add peace sign (2 fingers)
    if extended_fingers == 2:
        index_up = hand_landmarks.landmark[INDEX_FINGER_TIP].y < hand_landmarks.landmark[INDEX_FINGER_PIP].y
        middle_up = hand_landmarks.landmark[MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[MIDDLE_FINGER_PIP].y
        
        if index_up and middle_up:
            return "PEACE_SIGN"
```

Then map in config:
```yaml
outputs:
  system:
    mappings:
      PEACE_SIGN: nexttrack
```

### Custom System Actions

Use any `pyautogui` key name or hotkey combo:

```yaml
mappings:
  OPEN_PALM: brightnessup
  CLOSED_FIST: brightnessdown
  POINTING: command+tab        # App switcher on Mac
PEACE_SIGN: ctrl+c          # Custom hotkey
```

## Next Steps

1. ✅ Test basic gestures with `test_gesture_only.yaml`
2. 📝 Customize `config/event_mappings.yaml` for your workflow
3. 🎨 Try Blender integration
4. 🔧 Add custom gestures and mappings
5. 📚 Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system

## Getting Help

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Structure**: See [README.md](../README.md)
- **Legacy Docs**: See [GUIDE_LEGACY.md](GUIDE_LEGACY.md) for old standalone system

---

**Made with ❤️ by the Lauzhack Team**
