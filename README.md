<div align="center">

![Gesture Control System](logo/logo.jpg)

# Gesture Control System

**Real-time hand gesture recognition for controlling Blender's 3D viewport**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-green.svg)](https://google.github.io/mediapipe/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](https://github.com)

</div>

---

## Overview

A production-ready gesture recognition system that enables intuitive control of Blender's 3D viewport through hand gestures. Built with MediaPipe for robust hand tracking and featuring platform-specific optimizations for macOS, Linux, and Windows.

### Core Features

- 🎯 **4 Core Gestures** - Pinch, V-gesture, Open Palm, Closed Fist
- 🔄 **Viewport Control** - Rotate and pan Blender's 3D viewport naturally
- 🎬 **Animation Control** - Play/stop timeline with hand gestures
- 🖥️ **Cross-Platform** - Optimized for macOS (main-thread), Linux/Windows (threaded)
- ⚡ **Low Latency** - Real-time processing with smoothing filters
- 🎛️ **Configurable** - YAML-based configuration for sensitivity and mappings

---

## Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Running the System

**1. Start the gesture engine:**

```bash
python main_orchestrator.py --config config/blender_mode.yaml --debug
```

**2. In Blender:**
- Install the addon from `blender_addon/gesture_control_addon.py`
- Enable "Gesture Control Center" in Preferences → Add-ons
- Open the sidebar (N key) → Gesture tab
- Click **"Connect Only"** to link with the running engine

**3. Control Blender with gestures!**

---

## Gestures

The system recognizes 4 core hand gestures for Blender control:

| Gesture | Description | Action |
|---------|-------------|--------|
| 🤏 **Pinch** | Thumb + index finger touching | **Rotate viewport** - Move hand while pinching to orbit camera |
| ✌️ **V-Gesture** | Index + middle fingers extended | **Pan viewport** - Move hand to pan camera position |
| 🖐️ **Open Palm** | All fingers extended | **Play animation** - Start timeline playback |
| ✊ **Closed Fist** | All fingers closed | **Stop animation** - Pause timeline |

### Gesture Details

**Pinch (Rotation Mode)**
- Pinch thumb and index finger together
- Move your hand to rotate the viewport
- Automatic orbit around scene center
- Release to exit rotation mode

**V-Gesture (Navigation Mode)**
- Extend index and middle fingers (peace sign)
- Keep ring and pinky fingers closed
- Move your hand to pan the viewport
- Release to exit navigation mode

**Animation Control**
- Open palm to start playback
- Closed fist to stop
- Works independently of viewport modes

---

## Architecture

```
┌─────────────┐
│   Camera    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ MediaPipe       │
│ Hand Tracking   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Gesture         │
│ Detector        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Filters &       │
│ Validators      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Event Bus       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Gesture         │
│ Handlers        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Blender Output  │
│ (Socket)        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Blender Addon   │
│ (Viewport)      │
└─────────────────┘
```

### Key Components

**Gesture Detection** (`gestures/`)
- MediaPipe-based hand landmark tracking
- Confidence validation and quality checks
- Smoothing filters for stable detection

**Event System** (`core/`)
- Central EventBus for message routing
- Type-safe event handling
- Modular handler registration

**Handlers** (`handlers/`)
- `blender_viewport_handler.py` - Viewport rotation and panning
- `blender_animation_handler.py` - Timeline control
- Configurable sensitivity and behavior

**Blender Integration** (`blender_addon/`)
- Socket-based communication (port 8888)
- Real-time viewport manipulation
- Simplified rotation and pan functions

---

## Configuration

Edit `config/blender_mode.yaml` to customize behavior:

```yaml
# Gesture detection settings
inputs:
  gesture:
    enabled: true
    camera_index: 0
    show_preview: true
    min_confidence: 0.6
    filter_window: 3

# Blender output
outputs:
  blender:
    enabled: true
    host: localhost
    port: 8888
```

### Sensitivity Tuning

In the Blender addon panel, adjust:
- **Rotation Sensitivity** - Controls viewport rotation speed (default: 0.5)
- **Pan Sensitivity** - Controls viewport panning speed (default: 0.1)

---

## Project Structure

```
lauzhack2025/
├── config/                      # YAML configuration files
├── core/                        # Event system and orchestration
│   ├── event_system.py         # EventBus implementation
│   ├── gesture_handler.py      # Handler base classes
│   └── launcher.py             # Application launcher
├── gestures/                    # Gesture recognition
│   ├── detector.py             # Main detection engine
│   ├── filters.py              # Smoothing filters
│   ├── validators.py           # Quality validation
│   └── library/
│       └── navigation.py       # Core gesture definitions
├── handlers/                    # Gesture handlers
│   ├── blender_viewport_handler.py
│   └── blender_animation_handler.py
├── inputs/                      # Input modules
│   └── gesture_input_production.py
├── outputs/                     # Output modules
│   └── blender_output.py       # Blender socket communication
├── blender_addon/               # Blender addon
│   └── gesture_control_addon.py
├── main_orchestrator.py         # Main entry point
└── requirements.txt             # Python dependencies
```

---

## Platform Support

### macOS
- **Main-thread camera mode** - Required for camera permissions
- Camera window displays in foreground
- Launched via Terminal.app for proper access

### Linux / Windows
- **Threaded camera mode** - Background processing
- Standard OpenCV camera access
- Preview window optional

The system automatically detects your platform and uses the appropriate mode.

---

## Troubleshooting

**Camera doesn't open?**
- Check camera permissions in System Preferences (macOS)
- Try a different camera: `--camera-index 1`
- Ensure no other app is using the camera

**Gestures not detected?**
- Improve lighting conditions
- Position hand clearly in frame
- Adjust `min_confidence` in config (lower = more sensitive)
- Check debug output with `--debug` flag

**Blender not responding?**
- Verify addon is installed and enabled
- Check port 8888 is available: `lsof -i :8888`
- Ensure "Connect Only" button was clicked in Blender
- Check Blender's system console for errors

**Viewport movement too fast/slow?**
- Adjust sensitivity in Blender addon panel
- Modify `sensitivity` in handler config
- Fine-tune in real-time without restarting

---

## Development

### Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific components
python -m pytest tests/test_gestures.py
python -m pytest tests/test_handler_system.py
```

### Adding Custom Gestures

1. Define gesture in `gestures/library/navigation.py`:
```python
@register("navigation")
class MyGesture(Gesture):
    @property
    def name(self) -> str:
        return "MY_GESTURE"
    
    def detect(self, landmarks, context):
        # Detection logic
        return GestureResult(name=self.name, confidence=0.9)
```

2. Add handler in `handlers/`
3. Configure mapping in YAML

---

## Technical Details

**Gesture Detection Pipeline:**
1. MediaPipe extracts hand landmarks (21 points per hand)
2. Landmarks filtered through smoothing window (reduces jitter)
3. Quality validator checks landmark visibility and confidence
4. Gesture detector matches against registered patterns
5. Confidence validator ensures stable detection
6. Event published to EventBus
7. Handlers process and route to outputs

**Movement Tracking:**
- Pinch: Tracks midpoint of thumb/index, calculates deltas
- V-Gesture: Tracks midpoint of index/middle, applies smoothing
- Sensitivity multipliers: Rotation (20x), Navigation (150x)
- Deadzone filtering to ignore micro-movements

---

## Requirements

```
mediapipe>=0.10.0
opencv-python>=4.8.0
PyYAML>=6.0
numpy>=1.24.0
```

---

## License

MIT License - See LICENSE file for details.

---

<div align="center">

**Built for LauzHack 2025**

Made with ❤️ by the gesture control team

</div>
