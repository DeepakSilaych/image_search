from __future__ import annotations

import os
import tempfile
from PIL import Image


class OCR_Object:
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
            from ocrmac.ocrmac import OCR

            # Resize if needed for speed
            img = Image.open(img_path)
            if max(img.size) > self.max_dim:
                img.thumbnail((self.max_dim, self.max_dim), Image.Resampling.LANCZOS)
                # Save to temp file for ocrmac
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    img.save(tmp.name, "JPEG", quality=85)
                    annotations = OCR(tmp.name).recognize()
                os.unlink(tmp.name)
            else:
                annotations = OCR(img_path).recognize()

            # annotations: [("Text", confidence, bbox), ...]
            parts = [str(item[0]) for item in (annotations or []) if item and item[0]]
            return " ".join(" ".join(parts).split())

        except Exception as e:
            print(f"[OCR Error] {e}")
            return ""


if __name__ == "__main__":
    import time
    ocr = OCR_Object()
    
    # Warmup
    ocr.process("img/1.jpg")
    
    # Benchmark
    for i in [1, 3, 5, 7, 9]:
        t0 = time.perf_counter()
        text = ocr.process(f"img/{i}.jpg")
        dt = (time.perf_counter() - t0) * 1000
        print(f"img/{i}.jpg: {dt:6.1f}ms | text='{text[:40]}'")
