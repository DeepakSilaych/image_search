"""
Vector database and search engine
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models

from .embedder import ImageEmbedder


class SearchEngine:
    """
    Search engine combining vector similarity with face filtering.
    Uses Qdrant for vector storage and search.
    """
    
    COLLECTION_NAME = "personal_photos"

    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path.cwd()

        print("--- Initializing Qdrant DB ---")
        self.client = QdrantClient(path=str(self.data_dir / "qdrant_db"))
        self.embedder: ImageEmbedder | None = None  # lazy initialization

    def _init_embedder(self):
        """Lazy initialization of embedder (heavy ML models)"""
        if self.embedder is None:
            self.embedder = ImageEmbedder(data_dir=self.data_dir)

    def _ensure_collection(self, vector_size: int):
        """Create collection if it doesn't exist"""
        if self.client.collection_exists(self.COLLECTION_NAME):
            return

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=int(vector_size),
                distance=models.Distance.COSINE,
            ),
        )

        # Optional text index on OCR content
        try:
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="ocr_text",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    lowercase=True,
                ),
            )
        except Exception:
            pass

    def add_image(self, image_path: str) -> bool:
        """
        Index an image for search.
        
        Returns:
            True if indexed, False if already exists
        """
        self._init_embedder()

        image_path = str(Path(image_path))
        if not os.path.isabs(image_path):
            image_path = str(self.data_dir / image_path)

        # Deterministic ID for deduplication
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, image_path))
        
        try:
            existing = self.client.retrieve(self.COLLECTION_NAME, ids=[doc_id])
            if existing:
                return False
        except Exception:
            pass  # Collection may not exist yet

        print(f"Indexing: {image_path}...")
        vector, metadata, perf = self.embedder.process(image_path)
        self._ensure_collection(vector_size=len(vector))

        payload = {
            "path": image_path,
            "ocr_text": metadata.get("ocr_text", ""),
            "faces": metadata.get("faces", []),
            "perf": perf,
        }

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        print(" -> Saved!")
        return True

    def _get_known_names(self) -> set[str]:
        """Get list of known face names"""
        self._init_embedder()
        return set(self.embedder.face_identifier.known_db.keys())

    def search(self, query_text: str, limit: int = 20) -> list[tuple]:
        """
        Search for images matching query.
        
        Args:
            query_text: Natural language query
            limit: Maximum results to return
            
        Returns:
            List of (path, score, ocr_text, faces)
        """
        self._init_embedder()
        print(f"\n--- Searching for: '{query_text}' ---")

        query_vector = self.embedder.embed_query(query_text)
        self._ensure_collection(vector_size=len(query_vector))

        # Check if query mentions a known person → add face filter
        query_lower = query_text.lower()
        known_names = self._get_known_names()
        mentioned_names = [n for n in known_names if n.lower() in query_lower]

        query_filter = None
        if mentioned_names:
            query_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key="faces",
                        match=models.MatchAny(any=mentioned_names),
                    )
                ]
            )

        response = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=int(limit),
        )

        results = []
        for hit in response.points or []:
            results.append((
                hit.payload.get("path"),
                float(hit.score),
                hit.payload.get("ocr_text", ""),
                hit.payload.get("faces", []),
            ))
        return results

    def get_all_images(self, limit: int = 1000) -> list[tuple]:
        """Get all indexed images"""
        try:
            scroll_result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            results = []
            for point in scroll_result[0]:
                path = point.payload.get("path", "")
                if path and Path(path).exists():
                    results.append((path, {
                        "faces": point.payload.get("faces", []),
                        "ocr_text": point.payload.get("ocr_text", ""),
                    }))
            return results
        except Exception:
            return []

    def close(self):
        """Clean shutdown"""
        self.client.close()

