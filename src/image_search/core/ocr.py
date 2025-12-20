"""
OCR using Apple Vision Framework
"""
from __future__ import annotations

import os
import tempfile

from PIL import Image


class OCR:
    """Extract text from images using macOS Vision Framework"""
    
    def __init__(self, max_dim: int = 1024):
        self.max_dim = max_dim

    def process(self, img_path: str) -> str:
        """
        Extract text using Apple's Vision Framework (via ocrmac).
        Resizes large images first for speed.
        """
        if not img_path or not os.path.exists(img_path):
            return ""

        try:
            from ocrmac.ocrmac import OCR as OCRMac

            # Resize if needed for speed
            img = Image.open(img_path)
            if max(img.size) > self.max_dim:
                img.thumbnail((self.max_dim, self.max_dim), Image.Resampling.LANCZOS)
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    img.save(tmp.name, "JPEG", quality=85)
                    annotations = OCRMac(tmp.name).recognize()
                os.unlink(tmp.name)
            else:
                annotations = OCRMac(img_path).recognize()

            # annotations: [("Text", confidence, bbox), ...]
            parts = [str(item[0]) for item in (annotations or []) if item and item[0]]
            return " ".join(" ".join(parts).split())

        except Exception as e:
            print(f"[OCR Error] {e}")
            return ""

