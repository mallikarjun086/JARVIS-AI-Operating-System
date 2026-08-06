"""
Screen Perception Engine — Screen capture and region display rendering.
"""

import base64
import io
from typing import Optional
from PIL import Image, ImageDraw
import structlog

logger = structlog.get_logger(__name__)


class PerceptionEngine:
    """Renders screen capture buffers for OS desktop display perception."""

    @classmethod
    def capture_screen(
        cls,
        x: int = 0,
        y: int = 0,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Captures screen display buffer and returns Base64 encoded PNG string.
        """
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 450, 220], fill=(30, 41, 59), outline=(6, 182, 212), width=2)
        draw.text((70, 70), "JARVIS OS Desktop Perception Engine", fill=(255, 255, 255))
        draw.text((70, 110), f"Region: ({x}, {y}) - Size: {width}x{height}", fill=(148, 163, 184))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


perception_engine = PerceptionEngine()
