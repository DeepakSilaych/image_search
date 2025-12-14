# Image Search System

A powerful AI-powered image search and analysis system that combines computer vision, natural language processing, and vector database technology to enable semantic search through personal photo collections.

## Features

- **Multi-modal Image Analysis**: Extracts comprehensive information from images using:
  - OCR (Optical Character Recognition) for text extraction
  - Face recognition and identification
  - Visual scene analysis using AI models
- **Semantic Search**: Search images using natural language queries
- **Vector Database**: Efficient similarity search using ChromaDB
- **Performance Monitoring**: Built-in performance tracking and optimization
- **Face Database**: Learn and recognize specific individuals

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
pip install -e .
```

3. Additional dependencies (install manually if needed):

```bash
pip install deepface easyocr chromadb sentence-transformers opencv-python pillow
```

## Usage

### Setting up Face Recognition

1. Create a `known_faces/` directory structure:

```
known_faces/
├── person_name_1/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── ...
├── person_name_2/
│   ├── photo1.jpg
│   └── ...
```

2. Place reference images of people you want to recognize in their respective folders

### Indexing Images

1. Place images in the `img/` directory
2. Run the vector database to index them:

```python
from vector_db import SearchEngine

engine = SearchEngine()

# Index all images in img/ directory
import os
for img_file in os.listdir("img/"):
    if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
        engine.add_image(f"img/{img_file}")
```

### Searching Images

```python
from vector_db import SearchEngine

engine = SearchEngine()

# Search for images using natural language
results = engine.search("person wearing white shirt", n_results=5)

# Display results
for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"Result {i+1}:")
    print(f"  File: {metadata['path']}")
    print(f"  Description: {doc}")
    print()
```

### Processing Individual Images

```python
from embed_img import ImageEmbedder
import cv2

embedder = ImageEmbedder()
img = cv2.imread("path/to/image.jpg")

# Get comprehensive analysis
search_text, metadata = embedder.process(img)

print("Searchable text:", search_text)
print("Full metadata:", metadata)
```

## How It Works

### 1. Image Processing Pipeline

The [`ImageEmbedder.process()`](embed_img.py:49) method performs:

1. **OCR Extraction**: Extracts and cleans text from images
2. **Face Detection**: Identifies and recognizes known faces
3. **Visual Analysis**: Uses Moondream2 VLM to generate scene descriptions and person details
4. **Metadata Consolidation**: Combines all extracted information into searchable text

### 2. Vector Database

- Uses ChromaDB with cosine similarity for efficient semantic search
- Employs SentenceTransformers for text embedding
- Stores image paths and metadata snippets for quick retrieval

### 3. Face Recognition

- Uses DeepFace with ArcFace model for face embedding
- Maintains persistent database of known faces
- Supports incremental learning - add new reference images anytime

### 4. Performance Optimization

- Built-in performance monitoring tracks processing time and memory usage
- Image resizing for optimal VLM processing
- Caching of face embeddings to avoid recomputation

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
# Optional: Model paths or API keys
HUGGINGFACE_CACHE_DIR=./cache
```

### Performance Tuning

- Adjust image resolution in [`embed_img.py:71`](embed_img.py:71) for speed/quality tradeoff
- Modify face recognition threshold in [`face_recognition.py:125`](face_recognition.py:125)
- Change OCR confidence threshold in [`ocr.py:34`](ocr.py:34)

## Examples

### Search Queries

- "deepak with white tshirt"
- "people sitting outdoors"
- "document with text"
- "group photo with multiple people"
- "indoor office setting"

### Output Format

Search results include:

- Image file path
- Relevance score (implicit in ordering)
- Scene description snippet
- Identified people and their descriptions
- Extracted text content

## Performance

Typical processing times per image:

- OCR: 1-3 seconds
- Face Detection: 0.5-2 seconds
- Visual Analysis: 10-15 seconds (VLM encoding)
- Total: 12-20 seconds per image

## Troubleshooting

### Common Issues

1. **VLM Loading Issues**: Ensure sufficient RAM (8GB+ recommended)
2. **Face Recognition Errors**: Check image quality and lighting in reference photos
3. **OCR Accuracy**: Ensure text is clear and properly oriented
4. **Database Errors**: Verify write permissions for `image_search_db/` directory

### Debug Mode

Enable detailed logging by running individual modules:

```bash
python embed_img.py  # Test image processing
python face_recognition.py  # Test face recognition
python ocr.py  # Test OCR extraction
python vllm_logic.py  # Test visual language model
```

## Dependencies

- **deepface**: Face recognition and analysis
- **easyocr**: Text extraction from images
- **chromadb**: Vector database for similarity search
- **sentence-transformers**: Text embedding models
- **transformers**: Hugging Face models (Moondream2)
- **opencv-python**: Image processing
- **pillow**: Image manipulation
- **psutil**: System monitoring
- **paddleocr**: Alternative OCR engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Moondream2 by [vikhyatk](https://huggingface.co/vikhyatk/moondream2) for visual language modeling
- DeepFace for face recognition capabilities
- ChromaDB for vector database functionality
- EasyOCR for text extraction
