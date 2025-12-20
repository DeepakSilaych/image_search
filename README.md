<p align="center">
  <img src="resources/profile.png" alt="Image Search" width="120" height="120">
</p>

<h1 align="center">Image Search</h1>

<p align="center">
  <strong>Semantic photo search powered by Apple Silicon</strong>
</p>

<p align="center">
  Search your photos using natural language. Find <em>"beach sunset with Sarah"</em> or <em>"birthday party last summer"</em> instantly.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/macOS-12+-000000?logo=apple&logoColor=white" alt="macOS">
  <img src="https://img.shields.io/badge/Apple%20Silicon-optimized-000000?logo=apple" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version">
</p>

<p align="center">
  <a href="#-the-problem">Problem</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-usage">Usage</a>
</p>

---

## 🎯 The Problem

Your photo library has thousands of images. Finding a specific one is painful:

- **Filename search?** Useless. `IMG_4392.jpg` tells you nothing.
- **Date-based browsing?** Hope you remember when it was taken.
- **Manual tagging?** Nobody has time for that.
- **Cloud AI services?** Your private photos uploaded to someone else's servers.

You remember _what's in the photo_, not when you took it or what you named it.

## 💡 How It Works

Image Search understands the _meaning_ of your photos using state-of-the-art ML models running **entirely on your device**:

```
┌─────────────────────────────────────────────────────────────┐
│                        Your Photo                           │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  MLX-CLIP │       │  ocrmac   │       │ DeepFace  │
   │  (GPU)    │       │ (Vision)  │       │ (ArcFace) │
   └───────────┘       └───────────┘       └───────────┘
    "sunset",          "Starbucks"         "Mom", "Dad"
    "beach",           "receipt"
    "golden hour"
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                     ┌───────────────┐
                     │ Vector Search │
                     │   (Qdrant)    │
                     └───────────────┘
                              │
                              ▼
                      Your results in <50ms
```

**Three AI models work together:**

| Model        | Purpose                                       | Hardware      |
| ------------ | --------------------------------------------- | ------------- |
| **MLX-CLIP** | Understands image content semantically        | Apple GPU     |
| **ocrmac**   | Reads text in images (receipts, signs, notes) | Neural Engine |
| **DeepFace** | Recognizes faces of people you know           | CPU/MPS       |

All processing happens locally. Your photos **never leave your device**.

---

## ✨ Features

| Feature              | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| **Semantic Search**  | Search by meaning, not keywords. _"cozy evening"_ finds candlelit dinners |
| **Face Recognition** | Search by person. _"photos of mom"_ returns exactly that                  |
| **OCR Search**       | Find text in images. _"receipt from Starbucks"_ just works                |
| **Fast**             | ~750ms to index, <50ms to search                                          |
| **100% Local**       | No cloud. No API keys. No privacy concerns                                |
| **Beautiful UI**     | Native macOS dark theme with PyQt6                                        |

---

## 🚀 Quick Start

### Prerequisites

- macOS 12+ (Monterey or later)
- Apple Silicon (M1/M2/M3/M4) recommended
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone https://github.com/DeepakSilaych/image_search.git
cd image_search

# Install dependencies (using uv - recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Run the App

```bash
# GUI application
uv run python run.py

# Or use the CLI
uv run python cli.py --help
```

First launch downloads the CLIP model (~350MB). Subsequent launches are instant.

---

## 📖 Usage

### GUI Application

```bash
uv run python run.py
```

- **Drag & drop** images or folders to index them
- **Type naturally** in the search bar
- **Click "Faces"** tab to add known people
- **Click any image** to preview with metadata

### CLI (for development/debugging)

```bash
# Index images
uv run python cli.py index ~/Pictures --limit 100

# Search
uv run python cli.py search "sunset at beach"

# Manage faces
uv run python cli.py faces list
uv run python cli.py faces add --name "Alice" --photos photo1.jpg photo2.jpg

# Database stats
uv run python cli.py stats

# Test individual components
uv run python cli.py test clip --input "a cat on a couch"
uv run python cli.py test ocr --image receipt.jpg
uv run python cli.py test faces --image group_photo.jpg
```

### Python API

```python
from image_search.core import SearchEngine

engine = SearchEngine(data_dir="./data")

# Index an image
engine.add_image("vacation/beach.jpg")

# Search
results = engine.search("golden hour at the beach")
for path, score, ocr_text, faces in results:
    print(f"{score:.0%} | {path} | people: {faces}")

engine.close()
```

---

## 📁 Project Structure

```
image_search/
├── src/image_search/        # Main package
│   ├── app.py               # GUI entry point
│   ├── cli.py               # CLI interface
│   ├── core/                # ML components
│   │   ├── embedder.py      # CLIP embeddings
│   │   ├── face_recognition.py
│   │   ├── ocr.py
│   │   └── search_engine.py
│   └── gui/                 # PyQt6 interface
│       ├── main_window.py
│       ├── image_grid.py
│       └── theme.py
├── scripts/                 # Build tools
├── resources/               # App icons
├── data/                    # User data (gitignored)
├── pyproject.toml
└── README.md
```

---

## 🛠️ Building

### Create macOS App Bundle

```bash
uv run python scripts/build_app.py
```

### Create DMG for Distribution

```bash
./scripts/create_dmg.sh
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for Apple Silicon
</p>
