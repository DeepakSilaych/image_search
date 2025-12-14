# Image Search System
An advanced image search system that combines OCR, face recognition, and visual language models to enable rich semantic search capabilities over image datasets.

## Architecture

The system consists of several core components:

### Core Modules

- **[`embed_img.py`](embed_img.py)**: Main image processing pipeline that orchestrates OCR, face detection, and visual analysis
- **[`vector_db.py`](vector_db.py)**: Vector database management using ChromaDB for semantic search
- **[`face_recognition.py`](face_recognition.py)**: Face detection and recognition system with persistent face database
- **[`ocr.py`](ocr.py)**: Text extraction from images using EasyOCR
- **[`vllm_logic.py`](vllm_logic.py)**: Visual language model integration using Moondream2
- **[`monitor.py`](monitor.py)**: Performance monitoring and profiling utilities

## Installation

### Prerequisites

- Python 3.11 or higher
- UV package manager (recommended) or pip

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd image_search
```

2. Install dependencies using UV:

```bash
uv sync
```

Or using pip:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```


### run 

To run the image search system, execute the main script:

```bash
python vector_db.py
```


