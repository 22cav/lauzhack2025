# 3DX - Hand Gesture Control for Blender

**Version:** 1.0.0 (High-level structure)  
**Status:** Ready for implementation

Control Blender with hand gestures using your webcam!

## 🎯 Features

- 🤏 **Pinch & Drag** - Rotate the viewport
- ✌️ **V-Gesture** - Pan the camera  
- 🖐️ **Open Palm** - Play animation
- ✊ **Closed Fist** - Stop animation

## 📦 What's Included

This repository contains a **complete Blender addon structure** with:
- ✅ 25+ Python files with comprehensive type annotations
- ✅ All required Blender addon components (operators, properties, panels)
- ✅ Gesture detection framework (detector, filters, validators)
- ✅ Handler system for direct Blender API manipulation
- ✅ TODO markers with pseudocode for implementation

## 🚀 Installation

### Prerequisites

Install required Python packages in **Blender's Python** (not your system Python):

```bash
# macOS example:
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3.11 -m pip install opencv-python mediapipe numpy

# Windows example:
"C:\Program Files\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe" -m pip install opencv-python mediapipe numpy

# Linux example:
/usr/share/blender/4.2/python/bin/python3.11 -m pip install opencv-python mediapipe numpy
```

### Install Addon

**Option 1: Development Mode**
1. Clone or download this repository
2. In Blender: Edit → Preferences → Add-ons
3. Click "Install"
4. Navigate to this folder and select it
5. Enable "3DX - Gesture Control"

**Option 2: As ZIP**
1. Create a ZIP of this entire folder
2. In Blender: Edit → Preferences → Add-ons → Install
3. Select the ZIP file
4. Enable the addon

## 🎨 Usage

1. Open Blender's 3D Viewport
2. Press `N` to open the sidebar
3. Click the **"3DX"** tab
4. Click **"Start"** to begin gesture control
5. Grant camera permission if prompted
6. Perform gestures in front of your camera!

### Settings

Adjust in the Settings panel:
- **Camera Index** - Select camera device (0 = default)
- **Rotation/Pan Sensitivity** - Adjust gesture responsiveness  
- **Enable/Disable** individual gestures
- **Show Preview** - Display camera feed in Blender

## 📁 Repository Structure

```
3dx/  (This is now the addon root)
├── __init__.py              # Addon entry point
├── config.py                # Configuration constants
├── utils.py                 # Utility functions
├── operators.py             # All Blender operators
├── properties.py            # Preferences & runtime state
├── panels.py                # UI panels
├── gesture_engine.py        # Main gesture engine
├── core/                    # Event system & modality
├── gestures/                # Detection, filters, validators
├── handlers/                # Direct Blender API handlers
├── camera/                  # Camera capture module
├── libs/                    # (Future: bundled dependencies)
├── assets/                  # (Future: icons & images)
└── OLD_REFERENCE/           # Archived old structure
```

## 🔧 Development Status

This is **Version 1.0.0** - a high-level structure with implementation guidance.

### ✅ Completed
- Complete addon file structure
- Type-annotated codebase
- All UI components (operators, panels, properties)
- Gesture detection framework
- Handler system architecture

### 🚧 TODO (Implementation Needed)
All complex logic is marked with `#TODO` and pseudocode:
- Camera capture implementation
- MediaPipe hands integration
- Frame processing pipeline
- Viewport manipulation logic
- Gesture handling execution

See `#TODO` markers in code for detailed implementation guidance.

## 📖 Documentation

- [`STRUCTURE_SUMMARY.md`](STRUCTURE_SUMMARY.md) - Complete structure overview
- [`OLD_REFERENCE/ROADMAP.md`](OLD_REFERENCE/ROADMAP.md) - Development roadmap
- [`OLD_REFERENCE/ADDON_COMPONENTS.md`](OLD_REFERENCE/ADDON_COMPONENTS.md) - Component specifications

## 🐛 Troubleshooting

### Camera not working
- Check camera permissions in system settings
- Try different camera indices (0, 1, 2...)
- Test camera in another application first

### Dependencies missing
Install packages in **Blender's Python**, not system Python:
```bash
<blender-python> -m pip install opencv-python mediapipe numpy
```

### Poor gesture detection
- Ensure good lighting
- Keep hand visible to camera
- Adjust sensitivity in settings
- Avoid cluttered backgrounds

## 🤝 Contributing

This is a structured template ready for implementation. Contributions welcome!

1. Implement TODO sections following pseudocode
2. Test with Blender
3. Submit pull request

## 📜 License

MIT License - See LICENSE file for details

## 👥 Credits

Developed by Matteo Caviglia (22cav)