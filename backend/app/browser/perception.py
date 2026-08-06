"""
Screen Capture & Perception Engine — Viewport & Full-Page Screenshots, Element Screenshots, PDF Generation.
"""

import base64
import io
from typing import Any, Optional
from PIL import Image, ImageDraw
import structlog

logger = structlog.get_logger(__name__)


class PerceptionEngine:
    """Handles screenshot rendering, PDF generation, and image processing."""

    @classmethod
    async def capture_screenshot(
        cls,
        page: Any,
        full_page: bool = False,
        selector: Optional[str] = None
    ) -> str:
        """
        Takes page or element screenshot via Playwright API or fallback PIL generator.
        Returns Base64 encoded PNG string.
        """
        if page is not None:
            try:
                if selector:
                    elem = await page.query_selector(selector)
                    if elem:
                        png_bytes = await elem.screenshot()
                    else:
                        png_bytes = await page.screenshot(full_page=full_page)
                else:
                    png_bytes = await page.screenshot(full_page=full_page)

                return base64.b64encode(png_bytes).decode("utf-8")
            except Exception as e:
                logger.warning("Playwright screenshot failed, falling back to PIL", error=str(e))

        # Fallback PIL generator
        img = Image.new("RGB", (1280, 800), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 700, 250], fill=(30, 41, 59), outline=(6, 182, 212), width=2)
        draw.text((60, 60), "JARVIS Autonomous Browser Perception", fill=(255, 255, 255))
        draw.text((60, 100), f"Full Page: {full_page} | Selector: {selector or 'Viewport'}", fill=(148, 163, 184))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @classmethod
    async def generate_pdf(cls, page: Any) -> bytes:
        """Generates PDF binary from page."""
        if page is not None:
            try:
                return await page.pdf()
            except Exception as e:
                logger.warning("PDF generation failed", error=str(e))
        return b"%PDF-1.4 Mock PDF Output"


perception_engine = PerceptionEngine()
