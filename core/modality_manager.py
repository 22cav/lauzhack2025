"""
Modality Manager
"""

from typing import List
from enum import Enum


class Modality(str, Enum):
    CONTROL = "Control"
    NAVIGATION = "Navigation"


class ModalityManager:
    def __init__(self):
        self.active_modality: Modality = Modality.CONTROL
    
    def get_modality_name(self) -> str:
        return self.active_modality.value
