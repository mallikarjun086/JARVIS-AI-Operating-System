"""
Vision Memory Cache Engine.
Caches screenshot hashes, OCR text, and UI element counts in Long-Term Memory.
"""

import hashlib
from typing import List, Optional
from app.vision.schemas import VisionMemoryRecord


class VisionMemoryEngine:
    """Manages visual scene memory records and hash indexing."""

    def __init__(self) -> None:
        self._memory_store: List[VisionMemoryRecord] = []

    def record_scene(
        self,
        image_b64: Optional[str],
        scene_summary: str,
        ocr_text: str,
        element_count: int
    ) -> VisionMemoryRecord:
        """Computes image hash and registers snapshot in vision memory cache."""
        img_bytes = (image_b64 or "default_screenshot_bytes").encode("utf-8")
        img_hash = hashlib.sha256(img_bytes).hexdigest()[:16]

        rec = VisionMemoryRecord(
            image_hash=img_hash,
            scene_summary=scene_summary,
            extracted_text=ocr_text,
            element_count=element_count
        )
        self._memory_store.append(rec)
        return rec

    def list_records(self) -> List[VisionMemoryRecord]:
        """Lists cached vision memory records."""
        return list(self._memory_store)


vision_memory_engine = VisionMemoryEngine()
