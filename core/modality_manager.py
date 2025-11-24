"""
Modality Manager
"""

import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(current_dir, ".."))
if root not in sys.path:
    sys.path.append(root)

from enum import Enum

class Modality(str, Enum):
    CONTROL = "Control"
    NAVIGATION = "Navigation"


class ModalityManager:
    def __init__(self):
        self.active_modality: Modality = Modality.CONTROL
    
    def get_modality(self) -> Modality:
        return self.active_modality
    
    def set_modality(self, modality: Modality) -> None:
        self.active_modality = modality
        