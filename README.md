<p align="center">
  <h1 align="center">🔍 Personal Photo Search</h1>
  <p align="center">
    <strong>Semantic image search powered by Apple Silicon</strong>
  </p>
  <p align="center">
    Search your photos using natural language. Find "beach sunset with Sarah" or "birthday party last summer" instantly.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Apple%20Silicon-Optimized-black?logo=apple" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Semantic Search** | Find images by meaning, not keywords. "cozy evening" finds candlelit dinners. |
| 👤 **Face Recognition** | Search by person name. "photos of mom" returns exactly that. |
| 📝 **OCR** | Finds text in images. Search "receipt from Starbucks" and it's there. |
| ⚡ **Fast** | ~750ms per image indexing. Search results in <50ms. |
| 🔒 **100% Local** | Your photos never leave your device. No cloud APIs. |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/DeepakSilaych/image_search.git
cd image_search

# Install (requires Python 3.11+)
uv pip install -r requirements.txt

# Add your photos
cp ~/Pictures/*.jpg img/

# Optional: Add known faces for person search
mkdir -p known_faces/Mom
cp mom_photo.jpg known_faces/Mom/

# Run
python vector_db.py
```

**First run** downloads the CLIP model (~350MB) — subsequent runs are instant.

---

## 🔎 Usage

### Python API

```python
from vector_db import SearchEngine

engine = SearchEngine()

# Index images
engine.add_image("vacation/beach.jpg")
engine.add_image("vacation/sunset.jpg")

# Search
results = engine.search("golden hour at the beach")
for path, score, ocr_text, faces in results:
    print(f"{score:.2f} | {path} | people: {faces}")
```

### Search Examples

| Query | What it finds |
|-------|---------------|
| `"sunset"` | Images with sunset colors/lighting |
| `"mom and dad"` | Photos containing both people (if faces are registered) |
| `"handwritten notes"` | Images with handwriting detected via OCR |
| `"deepak outdoor smiling"` | Deepak's outdoor photos, ranked by "smiling" |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Image Input                          │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  MLX-CLIP │       │  ocrmac   │       │ DeepFace  │
   │  (GPU)    │       │ (Vision)  │       │ (ArcFace) │
   └───────────┘       └───────────┘       └───────────┘
   512-dim vector        Raw text         Face embeddings
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                     ┌───────────────┐
                     │    Qdrant     │
                     │  (Local DB)   │
                     └───────────────┘
                              │
                              ▼
                     ┌───────────────┐
                     │ Hybrid Search │
                     │ Vector + Face │
                     │   Filtering   │
                     └───────────────┘
```

### Tech Stack

| Component | Technology | Hardware |
|-----------|------------|----------|
| Visual Embeddings | [MLX-CLIP](https://github.com/harperreed/mlx_clip) | Apple GPU |
| OCR | [ocrmac](https://github.com/straussmaximilian/ocrmac) | Neural Engine |
| Face Recognition | [DeepFace](https://github.com/serengil/deepface) + ArcFace | CPU/MPS |
| Vector Database | [Qdrant](https://qdrant.tech/) (local mode) | SSD |

---

## ⚡ Performance

Benchmarked on M4 MacBook Pro with 3072×4096 images:

| Operation | Latency |
|-----------|---------|
| **Index (per image)** | ~750ms |
| ├─ CLIP embedding | 170ms |
| ├─ OCR | 250ms |
| └─ Face detection | 330ms |
| **Search** | <50ms |

*Images are automatically resized to 1024px for processing speed.*

---

## 📁 Project Structure

```
image_search/
├── vector_db.py          # Main entry point & search engine
├── embed_img.py          # CLIP embeddings + pipeline
├── face_recognition.py   # Face detection & matching
├── ocr.py                # macOS Vision OCR
├── monitor.py            # Performance tracking
├── requirements.txt      # Dependencies
├── img/                  # Your photos (add here)
├── known_faces/          # Reference faces by person
│   └── <name>/           # e.g., known_faces/Mom/photo.jpg
└── qdrant_db/            # Vector database (auto-created)
```

---

## 🔧 Configuration

### Adding Known Faces

```bash
# Create folder for each person
mkdir -p known_faces/Alice
mkdir -p known_faces/Bob

# Add 1-3 clear face photos per person
cp alice_photo1.jpg known_faces/Alice/
cp bob_photo1.jpg known_faces/Bob/
```

The system learns faces on first run and caches embeddings in `known_faces/known_faces_db.pkl`.

### Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_IMAGE_DIM` | 1024 | Resize images before processing |
| `FACE_THRESHOLD` | 0.6 | Cosine distance threshold for face matching |

---

## 🛣️ Roadmap

- [ ] Web UI (FastAPI + React)
- [ ] Batch import from Apple Photos / Google Photos export
- [ ] Duplicate detection
- [ ] Auto-tagging (objects, scenes, activities)
- [ ] Multi-modal search (image + text query)

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/image_search.git

# Create branch
git checkout -b feature/amazing-feature

# Make changes & test
python vector_db.py

# Push & create PR
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ❤️ for Apple Silicon</sub>
</p>
