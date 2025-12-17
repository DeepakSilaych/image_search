from __future__ import annotations

import os
import pickle
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image


def _resize_for_detection(img_path: str, max_dim: int = 1024) -> str | None:
    """Resize image if needed, return temp path or None if no resize needed."""
    img = Image.open(img_path)
    if max(img.size) <= max_dim:
        return None
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name, "JPEG", quality=85)
    return tmp.name


def _cosine_distance(a, b) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0.0 or nb == 0.0:
        return 1.0
    return float(1.0 - np.dot(a, b) / (na * nb))


class FaceIdentifier:
    """
    - Known faces live in: known_faces/<person_name>/*.jpg
    - DB cache: known_faces/known_faces_db.pkl (embeddings by filename)
    """

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent
        self.known_faces_dir = self.base_dir / "known_faces"
        self.db_path = self.known_faces_dir / "known_faces_db.pkl"
        self.known_db = defaultdict(dict)

        self._load_from_disk()
        self._scan_and_update_faces()

    def _load_from_disk(self):
        if self.db_path.exists():
            try:
                with self.db_path.open("rb") as f:
                    self.known_db = defaultdict(dict, pickle.load(f))
                print(f"--- Loaded {len(self.known_db)} known people ---")
            except Exception as e:
                print(f"[Face DB Load Error] {e}")

    def _save_to_disk(self):
        self.known_faces_dir.mkdir(parents=True, exist_ok=True)
        with self.db_path.open("wb") as f:
            pickle.dump(dict(self.known_db), f)

    def _scan_and_update_faces(self):
        if not self.known_faces_dir.exists():
            self.known_faces_dir.mkdir(parents=True, exist_ok=True)
            return

        try:
            from deepface import DeepFace  # type: ignore
        except Exception as e:
            print(f"[DeepFace Missing] {e}")
            return

        updates = False
        for person in os.listdir(self.known_faces_dir):
            p_dir = self.known_faces_dir / person
            if not p_dir.is_dir():
                continue

            for img_name in os.listdir(p_dir):
                if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                if img_name in self.known_db[person]:
                    continue

                img_path = str(p_dir / img_name)
                print(f"Learning face: {person} ({img_name})")
                try:
                    emb = DeepFace.represent(
                        img_path=img_path,
                        model_name="ArcFace",
                        detector_backend="opencv",
                        enforce_detection=False,
                    )[0]["embedding"]
                    self.known_db[person][img_name] = emb
                    updates = True
                except Exception as e:
                    print(f"Skipped {img_name}: {e}")

        if updates:
            self._save_to_disk()

    def detect_and_name(self, img_path: str):
        """
        Returns list[dict]: [{'name': 'deepak', 'confidence': 0.92, 'box': {...}}, ...]
        """
        try:
            from deepface import DeepFace  # type: ignore
        except Exception as e:
            print(f"[DeepFace Missing] {e}")
            return []

        # Resize for speed
        tmp_path = _resize_for_detection(img_path)
        detect_path = tmp_path if tmp_path else img_path

        try:
            faces = DeepFace.extract_faces(
                img_path=detect_path,
                detector_backend="opencv",
                enforce_detection=False,
            )
        except Exception:
            if tmp_path:
                os.unlink(tmp_path)
            return []

        results = []
        for face_obj in faces or []:
            try:
                curr_emb = DeepFace.represent(
                    img_path=face_obj["face"],
                    model_name="ArcFace",
                    enforce_detection=False,
                    detector_backend="skip",
                )[0]["embedding"]
            except Exception:
                continue

            best_name = "Unknown"
            best_dist = 0.6  # distance threshold (lower is more similar)

            for name, examples in self.known_db.items():
                for _, known_emb in examples.items():
                    dist = _cosine_distance(known_emb, curr_emb)
                    if dist < best_dist:
                        best_dist = dist
                        best_name = name

            if best_name != "Unknown":
                results.append(
                    {
                        "name": best_name,
                        "confidence": 1.0 - float(best_dist),
                        "box": face_obj.get("facial_area", {}),
                    }
                )

        # Cleanup temp file
        if tmp_path:
            os.unlink(tmp_path)

        return results


