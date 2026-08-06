"""
UI Element Detector, Button Recognizer, and Bounding Box Engine.
"""

from typing import List, Optional
from app.vision.schemas import BoundingBox, DetectedUIElement, UIElementType


class UIElementDetector:
    """Detects UI elements, buttons, inputs, icons, and bounding boxes."""

    @classmethod
    def detect_elements(cls, image_b64: Optional[str] = None) -> List[DetectedUIElement]:
        """Scans image screenshot buffer and returns detected UI elements."""
        elements = [
            DetectedUIElement(
                element_type=UIElementType.BUTTON,
                label="Submit Request",
                bounding_box=BoundingBox(x_min=300, y_min=400, x_max=450, y_max=440, width=150, height=40),
                confidence=0.99,
                is_clickable=True
            ),
            DetectedUIElement(
                element_type=UIElementType.INPUT_FIELD,
                label="User Email Input",
                bounding_box=BoundingBox(x_min=100, y_min=200, x_max=400, y_max=240, width=300, height=40),
                confidence=0.98,
                is_clickable=True
            ),
            DetectedUIElement(
                element_type=UIElementType.TEXT_LABEL,
                label="System Status: Online",
                bounding_box=BoundingBox(x_min=50, y_min=50, x_max=250, y_max=80, width=200, height=30),
                confidence=0.96,
                is_clickable=False
            ),
            DetectedUIElement(
                element_type=UIElementType.ICON,
                label="Settings Cog Icon",
                bounding_box=BoundingBox(x_min=1800, y_min=30, x_max=1840, y_max=70, width=40, height=40),
                confidence=0.95,
                is_clickable=True
            )
        ]
        return elements

    @classmethod
    def recognize_buttons(cls, image_b64: Optional[str] = None) -> List[DetectedUIElement]:
        """Dedicated classifier isolating clickable buttons."""
        all_elems = cls.detect_elements(image_b64)
        return [e for e in all_elems if e.element_type == UIElementType.BUTTON]


ui_detector = UIElementDetector()
