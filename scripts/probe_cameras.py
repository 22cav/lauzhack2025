#!/usr/bin/env python3
"""Probe available camera indices using OpenCV.

Usage: python scripts/probe_cameras.py [max_index]

Prints which indices OpenCV can open and whether a frame read succeeded.
"""
import sys
import cv2


def probe(max_index=6):
    found = []
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        ok = cap.isOpened()
        ret = False
        shape = None
        if ok:
            ret, frame = cap.read()
            shape = None if frame is None else frame.shape
            cap.release()
        print(f"Index {i}: opened={ok}, read={ret}, frame={shape}")
        if ok:
            found.append(i)
    print("Detected indices:", found)


if __name__ == '__main__':
    max_idx = 6
    if len(sys.argv) > 1:
        try:
            max_idx = int(sys.argv[1])
        except ValueError:
            print("Invalid max_index, using default 6")
    probe(max_idx)
