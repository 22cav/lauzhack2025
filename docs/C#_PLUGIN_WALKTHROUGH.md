# Gesture Control Plugin Walkthrough

## Overview
The **Gesture Control Plugin** allows you to control your PC using hand gestures captured by a webcam. It consists of two parts:
1.  **C# Plugin**: Runs within the Logi Options+ / Loupedeck ecosystem. It listens for gesture commands on a local TCP port (5000) and triggers plugin events.
2.  **Python Gesture Engine**: Uses MediaPipe to detect hand gestures from the webcam and sends them to the C# plugin.

## Changes Made
- **Renaming**: Renamed the project from `LauzhackPlugin` to `GestureControlPlugin`.
- **Python Engine**: Created `gesture_engine/` with `main.py` for gesture detection.
- **C# Integration**: Added `GestureServer.cs` to handle TCP connections and trigger events (`gestureOpenPalm`, `gestureClosedFist`, `gesturePointing`).

## How to Run
### 1. Prerequisites
- **Python 3.x**: Ensure Python is installed.
- **Dependencies**: Install required Python packages:
    ```bash
    pip install -r gesture_engine/requirements.txt
    ```

### 2. Build the Plugin
> [!WARNING]
> The build is currently failing due to a missing `PluginApi.dll` reference. Please ensure the Logi Plugin Service is installed correctly.

Once the dependency issue is resolved:
```bash
dotnet build
```

### 3. Run the Gesture Engine
Start the Python script:
```bash
python gesture_engine/main.py
```
It will attempt to connect to `localhost:5000`. Ensure the plugin is loaded (which starts the server) before running the script, or restart the script after loading the plugin.

## Supported Gestures
- **Open Palm**: Triggers `gestureOpenPalm`
- **Closed Fist**: Triggers `gestureClosedFist`
- **Pointing**: Triggers `gesturePointing`
