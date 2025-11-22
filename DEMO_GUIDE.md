# Blender Gesture Control Demo

Complete demo showing gesture recognition with visual feedback controlling Blender in real-time.

## 🚀 Quick Start

```bash
python demo_blender.py
```

This will:
1. Check that Blender is installed
2. Guide you through addon installation
3. Start Blender
4. Start the gesture control system
5. Show camera feed with gesture detection
6. Control Blender with your gestures!

## 📋 Prerequisites

1. **Blender** installed (3.0 or later)
   - macOS: Download from [blender.org](https://www.blender.org/download/)
   - Add to PATH or edit `BLENDER_PATH` in `demo_blender.py`

2. **Python dependencies** installed:
   ```bash
   conda activate lauzhack
   pip install -r requirements.txt
   ```

3. **Webcam** connected and working

## 🎨 First Time Setup

### 1. Install Blender Addon

The demo script will guide you, but here's the manual process:

1. **Open Blender**
2. **Go to**: Edit → Preferences → Add-ons
3. **Click**: "Install..." button
4. **Navigate to**: `blender_addon/gesture_control_addon.py`
5. **Select the file** and click "Install Add-on"
6. **Enable the addon**: Check the box next to "Gesture Control Listener"
7. **Verify**: You should see a "Gesture" tab in the 3D Viewport sidebar (press N to toggle)

The addon will auto-start the listener on port 8888.

### 2. Run the Demo

```bash
python demo_blender.py
```

Follow the on-screen instructions!

## 🤏 Supported Gestures

Once running, try these gestures in front of your camera:

- **🤏 Pinch + Drag** → Rotate Blender 3D viewport
  - Pinch thumb and index finger together
  - Move your hand to rotate the view
  
- **🖐️ Open Palm** → Play animation
  - Extend all fingers
  
- **✊ Closed Fist** → Pause animation
  - Close all fingers
  
- **👆 Pointing** → Next frame
  - Extend only index finger

## 🎬 What You'll See

### Camera Window
- Live camera feed
- Skeleton tracking (green lines)
- Hand landmarks (red dots)
- Current gesture displayed at top
- Last action performed
- FPS counter

### Blender Window
- 3D viewport responds to pinch-drag gestures
- Timeline plays/pauses with open palm/closed fist
- Frame advances with pointing gesture
- Status panel shows received commands

## 🔧 Configuration

### Camera Settings

Edit `config/blender_mode.yaml`:

```yaml
inputs:
  gesture:
    camera_index: 0           # Try 1, 2 if camera not detected
    pinch_threshold: 0.05     # Lower = more sensitive
    show_preview: true        # Show camera window
```

### Blender Connection

Edit `config/blender_mode.yaml`:

```yaml
outputs:
  blender:
    blender_port: 8888        # Must match addon port
    drag_sensitivity: 100.0   # Viewport rotation sensitivity
```

### Gesture Mappings

Customize gesture → action mappings:

```yaml
outputs:
  blender:
    mappings:
      PINCH_DRAG: viewport_rotate
      OPEN_PALM: play_animation
      CLOSED_FIST: pause_animation
      POINTING: next_frame
```

## 🐛 Troubleshooting

### Camera Not Opening

- Check no other app is using the camera
- Try different `camera_index` (0, 1, 2...)
- Check camera permissions (System Preferences → Security & Privacy → Camera)

### Blender Not Responding

1. **Check addon is installed and enabled**:
   - In Blender: Edit → Preferences → Add-ons
   - Search for "Gesture Control"
   - Should show "Gesture Control Listener" with checkbox enabled

2. **Check port number matches**:
   - Addon default: 8888
   - Config default: 8888
   - Edit either to match if different

3. **Check Blender console for errors**:
   - Window → Toggle System Console (Windows)
   - Or run Blender from terminal to see output

4. **Manually start listener** (if auto-start failed):
   - Press `N` in 3D Viewport
   - Go to "Gesture" tab
   - Click "Start Listener"

### Gestures Not Detected

- **Improve lighting**: Face a light source
- **Hand position**: Keep hand 30-60cm from camera
- **Gesture clarity**: Extend/close fingers fully
- **Lower threshold**: Edit `pinch_threshold` in config

### Poor Performance

- Close other apps
- Lower camera resolution (edit `gesture_input.py`)
- Ensure GPU drivers updated (MediaPipe uses GPU)

## 📁 Files

```
lauzhack/
├── demo_blender.py                    # Main demo launcher
├── blender_addon/
│   └── gesture_control_addon.py       # Blender addon
├── config/
│   └── blender_mode.yaml              # Blender configuration
├── main_orchestrator.py               # Gesture system
└── DEMO_GUIDE.md                      # This file
```

## 🎓 How It Works

1. **Camera Capture**: OpenCV captures webcam feed
2. **Gesture Detection**: MediaPipe detects hand pose
3. **Event Publishing**: Detected gestures published to EventBus
4. **Network Transfer**: Events sent as JSON over TCP socket
5. **Blender Reception**: Addon receives JSON commands
6. **Command Execution**: Addon executes Blender operations
7. **Visual Feedback**: Both camera window and Blender show results

## 🔄 Advanced Usage

### Running Without Demo Script

```bash
# Terminal 1: Start orchestrator
python main_orchestrator.py --config config/blender_mode.yaml

# Terminal 2: Start Blender
blender

# In Blender: Enable the gesture control addon
```

### Creating Custom Blender Actions

Edit `blender_addon/gesture_control_addon.py`:

```python
def _execute_in_main_thread(self, cmd_type, command):
    if cmd_type == 'my_custom_action':
        self._my_custom_action()
    # ... existing code ...

def _my_custom_action(self):
    """My custom Blender action."""
    # Your Blender code here
    bpy.ops.mesh.subdivide()  # Example
```

Then map it in config:

```yaml
mappings:
  PEACE_SIGN: my_custom_action
```

## 📊 Performance Tips

- **Recommended FPS**: 20-30 FPS
- **Gesture cooldown**: ~100ms between detections
- **Viewport updates**: Real-time with pinch-drag
- **CPU usage**: ~30-40% (MediaPipe + Blender)

## 🆘 Getting Help

1. Check this guide's troubleshooting section
2. Review [SETUP.md](docs/SETUP.md) for general setup
3. See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
4. Check Blender console for error messages
5. Verify all components are running:
   - Camera window open?
   - Blender running?
   - Addon enabled?
   - Port 8888 listening?

## 🎉 Next Steps

Once the demo is working:

1. Experiment with different gestures
2. Customize gesture mappings
3. Create custom Blender actions
4. Adjust sensitivity settings
5. Try complex viewport manipulations
6. Create gesture macros

---

**Enjoy controlling Blender with your hands!** 🤏🎨
