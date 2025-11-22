#!/usr/bin/env python3
"""
Camera Gesture Test - Main Thread Version

Displays camera with gesture detection running in the MAIN thread
(required for OpenCV on macOS).

Usage:
    python test_camera_main.py

Press ESC to exit.
"""

import cv2
import mediapipe as mp
import numpy as np
import sys
from pathlib import Path

# MediaPipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def detect_pinch(hand_landmarks, threshold=0.05):
    """Detect if thumb and index are pinched."""
    thumb_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
    
    distance = np.sqrt(
        (thumb_tip.x - index_tip.x) ** 2 +
        (thumb_tip.y - index_tip.y) ** 2 +
        (thumb_tip.z - index_tip.z) ** 2
    )
    
    return distance < threshold


def detect_gesture(hand_landmarks):
    """Detect basic hand gestures."""
    if not hand_landmarks:
        return "UNKNOWN"
    
    # Count extended fingers
    fingers = [
        mp_holistic.HandLandmark.INDEX_FINGER_TIP,
        mp_holistic.HandLandmark.MIDDLE_FINGER_TIP,
        mp_holistic.HandLandmark.RING_FINGER_TIP,
        mp_holistic.HandLandmark.PINKY_TIP
    ]
    
    fingers_pip = [
        mp_holistic.HandLandmark.INDEX_FINGER_PIP,
        mp_holistic.HandLandmark.MIDDLE_FINGER_PIP,
        mp_holistic.HandLandmark.RING_FINGER_PIP,
        mp_holistic.HandLandmark.PINKY_PIP
    ]
    
    extended_fingers = 0
    for tip, pip in zip(fingers, fingers_pip):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            extended_fingers += 1
    
    # Classify gesture
    if extended_fingers == 4:
        return "OPEN_PALM"
    elif extended_fingers == 0:
        return "CLOSED_FIST"
    elif extended_fingers == 1:
        index_extended = hand_landmarks.landmark[
            mp_holistic.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[
            mp_holistic.HandLandmark.INDEX_FINGER_PIP].y
        if index_extended:
            return "POINTING"
    
    return "UNKNOWN"


def main():
    print("="*60)
    print("📹 Camera Gesture Recognition Test (Main Thread)")
    print("="*60)
    print("\n🎬 Starting camera...")
    print("\n🤏 Try these gestures:")
    print("   • Open Palm (🖐️) - All 4 fingers extended")
    print("   • Closed Fist (✊) - All fingers closed")
    print("   • Pointing (👆) - Index finger extended")
    print("   • Pinch (🤏) - Bring thumb and index together")
    print("\n⌨️  Press ESC to exit")
    print("="*60)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("\n❌ Error: Could not open camera!")
        print("Please check:")
        print("  - Camera is connected")
        print("  - No other app is using the camera")
        print("  - Camera permissions granted (System Preferences → Security)")
        return 1
    
    print("\n✅ Camera opened successfully!")
    print("📹 Window should appear now...\n")
    
    # State tracking
    current_gesture = "UNKNOWN"
    is_pinching = False
    
    # Run gesture detection
    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:
        
        while True:
            success, image = cap.read()
            if not success:
                print("⚠️  Warning: Empty camera frame, retrying...")
                continue
            
            # Process frame
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            
            # Convert back for display
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Draw landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            
            # Detect gestures
            hand_landmarks = results.right_hand_landmarks or results.left_hand_landmarks
            
            if hand_landmarks:
                # Check for pinch
                if detect_pinch(hand_landmarks):
                    if not is_pinching:
                        print("🤏 PINCH DETECTED!")
                        is_pinching = True
                    current_gesture = "PINCHING"
                else:
                    if is_pinching:
                        print("🔓 Pinch released")
                        is_pinching = False
                    current_gesture = detect_gesture(hand_landmarks)
            else:
                current_gesture = "UNKNOWN"
                if is_pinching:
                    is_pinching = False
            
            # Add text overlay
            cv2.putText(image, f"Gesture: {current_gesture}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            status = "PINCHING" if is_pinching else "Ready"
            cv2.putText(image, f"Status: {status}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.putText(image, "Press ESC to exit", 
                       (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show image
            cv2.imshow('Gesture Recognition', image)
            
            # Check for exit
            if cv2.waitKey(5) & 0xFF == 27:  # ESC key
                break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Test complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
