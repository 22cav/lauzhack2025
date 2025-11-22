#!/usr/bin/env python3
"""Quick camera preview for a single device index.

Usage: python scripts/test_camera.py [index]

Press ESC in the preview window to exit.
"""
import sys
import cv2


def test(idx=0):
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        print(f"Cannot open camera {idx}")
        return
    print(f"Opened camera {idx}. Press ESC to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Empty frame")
                break
            cv2.imshow(f"Camera {idx}", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    idx = 0
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1])
        except ValueError:
            print("Invalid index, using 0")
    test(idx)
