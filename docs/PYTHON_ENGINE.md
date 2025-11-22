# Python Gesture Recognition Engine

## Overview

The Python engine uses MediaPipe Holistic to detect hand gestures from webcam input and communicates detected gestures to the C# plugin via WebSocket.

## Dependencies

```txt
opencv-python
mediapipe
```

Install via:
```bash
conda activate lauzhack
pip install -r requirements.txt
```

## Configuration

### Constants (main.py)

- `HOST`: WebSocket server address (default: `'127.0.0.1'`)
- `PORT`: WebSocket server port (default: `5000`)
- `CONFIDENCE_THRESHOLD`: Minimum confidence for detection (default: `0.7`)

### MediaPipe Settings

- `min_detection_confidence`: `0.5` - Minimum confidence for initial detection
- `min_tracking_confidence`: `0.5` - Minimum confidence for tracking across frames

## Architecture

### Main Components

1. **Camera Capture**: OpenCV VideoCapture for webcam input
2. **MediaPipe Holistic**: ML model for hand/pose landmark detection
3. **Gesture Detector**: Logic to classify gestures from landmarks
4. **WebSocket Client**: TCP socket to send gestures to C# plugin
5. **Visualization**: CV2 window with gesture overlay

## Gesture Detection Logic

### Function: `detect_gesture(hand_landmarks)`

Takes MediaPipe hand landmarks and returns gesture name.

#### OPEN_PALM
- **Condition**: 4 fingers extended (index, middle, ring, pinky)
- **Detection**: Finger tip Y < Finger PIP Y for all 4 fingers

#### CLOSED_FIST
- **Condition**: No fingers extended
- **Detection**: All finger tips Y ≥ Finger PIP Y

#### POINTING
- **Condition**: Only index finger extended
- **Detection**: Index tip Y < Index PIP Y, 1 extended finger total

#### UNKNOWN
- **Condition**: None of the above patterns match
- **Detection**: Default case

### Gesture State Management

- **Debouncing**: Only sends gesture when state changes
- **Last gesture tracking**: Prevents duplicate messages
- **UNKNOWN filtering**: Does not send UNKNOWN gestures

## Main Loop

```python
while cap.isOpened():
    1. Read frame from camera
    2. Process with MediaPipe Holistic
    3. Draw landmarks on image
    4. Detect gesture from hand landmarks
    5. Send gesture if changed from last state
    6. Display annotated frame
    7. Check for ESC key to exit
```

## Visual Feedback

The display window shows:

- **Pose landmarks**: Body pose skeleton
- **Hand landmarks**: Hand skeleton and connections
- **Gesture text**: Current detected gesture
- **Connection status**: "Online" (green) or "Offline" (red)

## Error Handling

### Camera Not Available
```python
if not success:
    print("Ignoring empty camera frame.")
    continue
```

### Connection Refused
```python
except ConnectionRefusedError:
    print(f"Could not connect to {HOST}:{PORT}. Running in offline mode.")
    sock = None
```

### Socket Send Error
```python
except Exception as e:
    print(f"Error sending data: {e}")
```

## Running the Engine

```bash
cd GestureControlPlugin/gesture_engine
conda activate lauzhack
python main.py
```

**Exit**: Press `ESC` key to quit

## Performance Optimization

- **Image flags**: Sets `writeable=False` during processing to enable pass-by-reference
- **Color conversion**: Only converts BGR↔RGB when necessary
- **Frame skipping**: `cv2.waitKey(5)` limits processing to ~200 FPS max

## Limitations and Future Improvements

### Current Limitations
- **Hand side detection**: Simplified thumb logic assumes right hand
- **Single hand**: Only processes one hand at a time (right hand priority)
- **Static gestures**: Only detects static poses, not dynamic movements
- **No reconnection**: If connection fails, requires manual restart

### Future Enhancements
- **Dynamic gestures**: Swipe, wave, rotation detection
- **Two-hand gestures**: Clapping, spreading, etc.
- **Hand side detection**: Proper left/right hand differentiation
- **Auto-reconnection**: Retry connection on failure
- **Configuration file**: External config for thresholds and settings
- **Gesture customization**: User-defined gesture training
