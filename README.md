### v2 (Apple Silicon native)

This version swaps the internal engines to native/fast alternatives:

- **Embeddings**: `mlx-clip` (MLX)
- **OCR**: `ocrmac` (macOS Vision)
- **Vector DB**: `qdrant-client` (local persisted)
- **Faces (optional)**: `deepface`

#### Run

```bash
cd v2
uv pip install -r requirements.txt  # or: pip install -r requirements.txt
python vector_db.py
```

#### Data folders

- `img/`: images to index
- `known_faces/<name>/*.jpg`: reference faces (optional)
- `qdrant_db/`: created automatically

