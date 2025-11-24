"""
This file contains the landmark indices for the MediaPipe landmarks that are used in the gestures.
The scope is that of having a single source of truth for the landmarks indices, as complete as possible.
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

import mediapipe as mp
from typing import Any, Tuple
import math


# MediaPipe Hand Landmark Indices
# Reference: https://google.github.io/mediapipe/solutions/hands.html

class HandLandmarkIndices:
    """
    Complete set of MediaPipe hand landmark indices.
    Single source of truth for all landmark references.
    """
    # Wrist
    WRIST = mp.solutions.hands.HandLandmark.WRIST
    
    # Thumb
    THUMB_CMC = mp.solutions.hands.HandLandmark.THUMB_CMC
    THUMB_MCP = mp.solutions.hands.HandLandmark.THUMB_MCP
    THUMB_IP = mp.solutions.hands.HandLandmark.THUMB_IP
    THUMB_TIP = mp.solutions.hands.HandLandmark.THUMB_TIP
    
    # Index Finger
    INDEX_FINGER_MCP = mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP
    INDEX_FINGER_PIP = mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP
    INDEX_FINGER_DIP = mp.solutions.hands.HandLandmark.INDEX_FINGER_DIP
    INDEX_FINGER_TIP = mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP
    
    # Middle Finger
    MIDDLE_FINGER_MCP = mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP
    MIDDLE_FINGER_PIP = mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP
    MIDDLE_FINGER_DIP = mp.solutions.hands.HandLandmark.MIDDLE_FINGER_DIP
    MIDDLE_FINGER_TIP = mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP
    
    # Ring Finger
    RING_FINGER_MCP = mp.solutions.hands.HandLandmark.RING_FINGER_MCP
    RING_FINGER_PIP = mp.solutions.hands.HandLandmark.RING_FINGER_PIP
    RING_FINGER_DIP = mp.solutions.hands.HandLandmark.RING_FINGER_DIP
    RING_FINGER_TIP = mp.solutions.hands.HandLandmark.RING_FINGER_TIP
    
    # Pinky
    PINKY_MCP = mp.solutions.hands.HandLandmark.PINKY_MCP
    PINKY_PIP = mp.solutions.hands.HandLandmark.PINKY_PIP
    PINKY_DIP = mp.solutions.hands.HandLandmark.PINKY_DIP
    PINKY_TIP = mp.solutions.hands.HandLandmark.PINKY_TIP


# Landmark Groups for easier reference
FINGER_TIPS = [
    HandLandmarkIndices.THUMB_TIP,
    HandLandmarkIndices.INDEX_FINGER_TIP,
    HandLandmarkIndices.MIDDLE_FINGER_TIP,
    HandLandmarkIndices.RING_FINGER_TIP,
    HandLandmarkIndices.PINKY_TIP,
]

FINGER_PIPS = [
    HandLandmarkIndices.THUMB_IP,  # Thumb has IP instead of PIP
    HandLandmarkIndices.INDEX_FINGER_PIP,
    HandLandmarkIndices.MIDDLE_FINGER_PIP,
    HandLandmarkIndices.RING_FINGER_PIP,
    HandLandmarkIndices.PINKY_PIP,
]

FINGER_MCPS = [
    HandLandmarkIndices.THUMB_MCP,
    HandLandmarkIndices.INDEX_FINGER_MCP,
    HandLandmarkIndices.MIDDLE_FINGER_MCP,
    HandLandmarkIndices.RING_FINGER_MCP,
    HandLandmarkIndices.PINKY_MCP,
]


# Helper Functions

def calculate_distance(p1: Any, p2: Any) -> float:
    """
    Calculate Euclidean distance between two landmarks.
    
    Args:
        p1: First landmark with x, y, z attributes
        p2: Second landmark with x, y, z attributes
        
    Returns:
        Euclidean distance
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dz = p1.z - p2.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def calculate_distance_squared(p1: Any, p2: Any) -> float:
    """
    Calculate squared Euclidean distance between two landmarks.
    Faster when only comparing distances (avoids sqrt).
    
    Args:
        p1: First landmark with x, y, z attributes
        p2: Second landmark with x, y, z attributes
        
    Returns:
        Squared Euclidean distance
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dz = p1.z - p2.z
    return dx * dx + dy * dy + dz * dz


def calculate_2d_distance(p1: Any, p2: Any) -> float:
    """
    Calculate 2D distance between two landmarks (ignoring z).
    
    Args:
        p1: First landmark with x, y attributes
        p2: Second landmark with x, y attributes
        
    Returns:
        2D Euclidean distance
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx * dx + dy * dy)


def is_finger_extended(landmarks: Any, finger_tip_idx: int, finger_pip_idx: int, wrist_idx: int) -> bool:
    """
    Check if a finger is extended.
    
    Args:
        landmarks: MediaPipe landmarks
        finger_tip_idx: Index of finger tip
        finger_pip_idx: Index of finger PIP joint
        wrist_idx: Index of wrist
        
    Returns:
        True if finger is extended
    """
    tip = landmarks.landmark[finger_tip_idx]
    pip = landmarks.landmark[finger_pip_idx]
    wrist = landmarks.landmark[wrist_idx]
    
    dist_tip = calculate_distance_squared(tip, wrist)
    dist_pip = calculate_distance_squared(pip, wrist)
    
    return dist_tip > dist_pip


def is_finger_curled(landmarks: Any, finger_tip_idx: int, finger_pip_idx: int, wrist_idx: int) -> bool:
    """
    Check if a finger is curled.
    
    Args:
        landmarks: MediaPipe landmarks
        finger_tip_idx: Index of finger tip
        finger_pip_idx: Index of finger PIP joint
        wrist_idx: Index of wrist
        
    Returns:
        True if finger is curled
    """
    return not is_finger_extended(landmarks, finger_tip_idx, finger_pip_idx, wrist_idx)


def get_finger_spread(landmarks: Any, tip_indices: list) -> float:
    """
    Calculate total spread between finger tips.
    
    Args:
        landmarks: MediaPipe landmarks
        tip_indices: List of finger tip indices
        
    Returns:
        Total spread distance
    """
    total_spread = 0.0
    for i in range(len(tip_indices) - 1):
        p1 = landmarks.landmark[tip_indices[i]]
        p2 = landmarks.landmark[tip_indices[i + 1]]
        total_spread += calculate_distance(p1, p2)
    
    return total_spread


def get_hand_center(landmarks: Any) -> Tuple[float, float, float]:
    """
    Calculate the center point of the hand.
    
    Args:
        landmarks: MediaPipe landmarks
        
    Returns:
        Tuple of (x, y, z) coordinates for hand center
    """
    wrist = landmarks.landmark[HandLandmarkIndices.WRIST]
    middle_mcp = landmarks.landmark[HandLandmarkIndices.MIDDLE_FINGER_MCP]
    
    center_x = (wrist.x + middle_mcp.x) / 2
    center_y = (wrist.y + middle_mcp.y) / 2
    center_z = (wrist.z + middle_mcp.z) / 2
    
    return (center_x, center_y, center_z)
