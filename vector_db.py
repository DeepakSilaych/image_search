from __future__ import annotations

import os
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models

from embed_img import ImageEmbedder


class SearchEngine:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        self.collection_name = "personal_photos"

        print("--- Initializing Qdrant DB ---")
        self.client = QdrantClient(path=str(self.base_dir / "qdrant_db"))
        self.embedder: ImageEmbedder | None = None  # lazy

    def _init_embedder(self):
        if self.embedder is None:
            self.embedder = ImageEmbedder(base_dir=self.base_dir)

    def _ensure_collection(self, vector_size: int):
        if self.client.collection_exists(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=int(vector_size),
                distance=models.Distance.COSINE,
            ),
        )

        # Optional text index on OCR content (Qdrant versions vary; keep best-effort).
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="ocr_text",
                field_schema=models.TextIndexParams(
                    type="text",
                    tokenizer=models.TokenizerType.WORD,
                    lowercase=True,
                ),
            )
        except Exception:
            pass

    def add_image(self, image_path: str):
        self._init_embedder()

        image_path = str(Path(image_path))
        if not os.path.isabs(image_path):
            image_path = str(self.base_dir / image_path)

        # deterministic id so we can skip duplicates
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, image_path))
        try:
            existing = self.client.retrieve(self.collection_name, ids=[doc_id])
            if existing:
                return
        except Exception:
            # collection may not exist yet
            pass

        print(f"Indexing: {image_path}...")
        vector, metadata, perf = self.embedder.process(image_path)  # type: ignore[union-attr]
        self._ensure_collection(vector_size=len(vector))

        payload = {
            "path": image_path,
            "ocr_text": metadata.get("ocr_text", ""),
            "faces": metadata.get("faces", []),
            "perf": perf,
        }

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        print(" -> Saved!")

    def _get_known_names(self) -> set[str]:
        """Get list of known face names from the face identifier."""
        self._init_embedder()
        return set(self.embedder.face_identifier.known_db.keys())  # type: ignore

    def search(self, query_text: str, limit: int = 5):
        self._init_embedder()
        print(f"\n--- Searching for: '{query_text}' ---")

        query_vector = self.embedder.embed_query(query_text)  # type: ignore[union-attr]
        self._ensure_collection(vector_size=len(query_vector))

        # Check if query mentions a known person → add face filter
        query_lower = query_text.lower()
        known_names = self._get_known_names()
        mentioned_names = [n for n in known_names if n.lower() in query_lower]

        query_filter = None
        if mentioned_names:
            # Filter to images containing any of the mentioned people
            query_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key="faces",
                        match=models.MatchAny(any=mentioned_names),
                    )
                ]
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=int(limit),
        )

        final = []
        for hit in response.points or []:
            # Qdrant: higher score is better for cosine similarity
            final.append(
                (
                    hit.payload.get("path"),
                    float(hit.score),
                    hit.payload.get("ocr_text", ""),
                    hit.payload.get("faces", []),
                )
            )
        return final


if __name__ == "__main__":
    engine = SearchEngine()

    img_dir = Path(__file__).resolve().parent / "img"
    if img_dir.exists():
        for img_file in os.listdir(img_dir):
            if img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                engine.add_image(str(img_dir / img_file))

    results = engine.search("deepak with white tshirt")
    for path, score, text, faces in results:
        print(f"{score:.3f} | {path} | faces={faces} | ocr='{text[:80]}'")

    # Clean shutdown
    engine.client.close()

