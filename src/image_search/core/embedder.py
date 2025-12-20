"""
Image embedding using MLX CLIP
"""
from __future__ import annotations

import os
from pathlib import Path

from .monitor import PerformanceMonitor
from .ocr import OCR
from .face_recognition import FaceIdentifier


class MLXClipWrapper:
    """Wrapper for mlx_clip that handles model loading and encoding."""
    
    def __init__(self, hf_repo: str = "openai/clip-vit-base-patch32"):
        from mlx_clip import CLIPModel, CLIPImageProcessor, CLIPTokenizer
        from mlx_clip.convert import convert_weights
        import mlx.core as mx
        
        # Local path for converted weights
        mlx_path = Path.home() / ".cache" / "mlx_clip" / hf_repo.replace("/", "_")
        
        # Convert weights if not already done
        if not mlx_path.exists():
            print(f"Converting {hf_repo} to MLX format (one-time)...")
            convert_weights(hf_repo, str(mlx_path), dtype="float32")
        
        # Load model components
        self.model = CLIPModel.from_pretrained(str(mlx_path))
        self.processor = CLIPImageProcessor.from_pretrained(str(mlx_path))
        self.tokenizer = CLIPTokenizer.from_pretrained(str(mlx_path))
        self.mx = mx
        
    def encode_image(self, img_path: str) -> list[float]:
        """Generate CLIP embedding for an image"""
        from PIL import Image
        
        img = Image.open(img_path).convert("RGB")
        pixel_values = self.processor([img])
        features = self.model.get_image_features(pixel_values)
        self.mx.eval(features)
        
        return features.tolist()[0]
    
    def encode_text(self, text: str) -> list[float]:
        """Generate CLIP embedding for text query"""
        input_ids = self.tokenizer(text)[None]
        features = self.model.get_text_features(input_ids)
        self.mx.eval(features)
        
        return features.tolist()[0]


class ImageEmbedder:
    """
    Complete image processing pipeline:
    - CLIP embeddings for semantic search
    - OCR for text extraction
    - Face detection and recognition
    """
    
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path.cwd()

        print("--- Loading MLX CLIP (Apple Silicon Optimized) ---")
        self.clip = MLXClipWrapper()
        self.ocr = OCR()
        self.face_identifier = FaceIdentifier(data_dir=self.data_dir)

    def process(self, img_path: str) -> tuple[list[float], dict, dict]:
        """
        Process an image and extract all features.
        
        Returns:
            (vector, metadata, performance_metrics)
        """
        monitor = PerformanceMonitor()
        final_data = {}

        img_path = str(Path(img_path))
        if not os.path.isabs(img_path):
            img_path = str(self.data_dir / img_path)

        # 1. OCR (Vision Framework)
        with monitor.measure("OCR"):
            final_data["ocr_text"] = self.ocr.process(img_path)

        # 2. Face Detection (DeepFace)
        with monitor.measure("Face_Detection"):
            faces = self.face_identifier.detect_and_name(img_path)
            final_data["faces"] = [f.get("name") for f in faces if f.get("name")]

        # 3. CLIP Embedding (MLX GPU)
        with monitor.measure("CLIP_Embedding"):
            vector = self.clip.encode_image(img_path)

        return vector, final_data, monitor.get_summary()

    def embed_query(self, query_text: str) -> list[float]:
        """Generate embedding for a text query"""
        return self.clip.encode_text(query_text)

