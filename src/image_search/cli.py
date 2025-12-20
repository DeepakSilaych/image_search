#!/usr/bin/env python3
"""
Image Search CLI - Development and debugging interface

Usage:
    image-search-cli <command> [options]
    
Commands:
    index       Index images from a directory
    search      Search for images
    faces       Manage known faces
    stats       Show database statistics
    test        Test individual components
"""
import argparse
import sys
import os
from pathlib import Path
from typing import Optional


def get_data_dir() -> Path:
    """Get default data directory"""
    # Check if we're in project root
    cwd = Path.cwd()
    if (cwd / "data").exists():
        return cwd / "data"
    if (cwd / "pyproject.toml").exists():
        data_dir = cwd / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    return cwd


def cmd_index(args):
    """Index images from directory"""
    from image_search.core import SearchEngine
    
    engine = SearchEngine(data_dir=args.data_dir)
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    
    images = []
    if path.is_file():
        images = [str(path)]
    else:
        for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.heic'):
            images.extend(str(p) for p in path.rglob(ext))
    
    if not images:
        print(f"No images found in {path}")
        sys.exit(1)
    
    print(f"Found {len(images)} images")
    
    indexed = 0
    for i, img_path in enumerate(images[:args.limit] if args.limit else images):
        print(f"[{i+1}/{len(images)}] {Path(img_path).name}...", end=" ", flush=True)
        try:
            if engine.add_image(img_path):
                indexed += 1
                print("✓")
            else:
                print("(exists)")
        except Exception as e:
            print(f"✗ {e}")
    
    print(f"\nIndexed {indexed} new images")
    engine.close()


def cmd_search(args):
    """Search for images"""
    from image_search.core import SearchEngine
    
    engine = SearchEngine(data_dir=args.data_dir)
    
    results = engine.search(args.query, limit=args.limit)
    
    if not results:
        print("No results found")
    else:
        print(f"\nFound {len(results)} results:\n")
        for i, (path, score, ocr_text, faces) in enumerate(results, 1):
            name = Path(path).name
            print(f"{i}. [{score:.1%}] {name}")
            if faces:
                print(f"   Faces: {', '.join(faces)}")
            if ocr_text and args.show_ocr:
                preview = ocr_text[:80] + "..." if len(ocr_text) > 80 else ocr_text
                print(f"   OCR: {preview}")
            print()
    
    engine.close()


def cmd_faces(args):
    """Manage known faces"""
    from image_search.core import FaceIdentifier
    
    face_id = FaceIdentifier(data_dir=args.data_dir)
    
    if args.action == "list":
        if not face_id.known_db:
            print("No known faces registered")
        else:
            print(f"\nKnown faces ({len(face_id.known_db)} people):\n")
            for name, photos in face_id.known_db.items():
                print(f"  • {name} ({len(photos)} reference photos)")
    
    elif args.action == "add":
        if not args.name or not args.photos:
            print("Error: --name and --photos required")
            sys.exit(1)
        
        face_dir = Path(args.data_dir) / "known_faces" / args.name
        face_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        for photo in args.photos:
            src = Path(photo)
            if src.exists():
                shutil.copy2(src, face_dir / src.name)
                print(f"Added: {src.name}")
        
        # Reload to learn new faces
        face_id._scan_and_update_faces()
        print(f"\n✓ Added {args.name}")
    
    elif args.action == "remove":
        if not args.name:
            print("Error: --name required")
            sys.exit(1)
        
        face_dir = Path(args.data_dir) / "known_faces" / args.name
        if face_dir.exists():
            import shutil
            shutil.rmtree(face_dir)
        
        if args.name in face_id.known_db:
            del face_id.known_db[args.name]
            face_id._save_to_disk()
        
        print(f"✓ Removed {args.name}")


def cmd_stats(args):
    """Show database statistics"""
    from image_search.core import SearchEngine
    
    engine = SearchEngine(data_dir=args.data_dir)
    
    print("\n📊 Image Search Statistics\n")
    
    # Get all images
    images = engine.get_all_images(limit=10000)
    print(f"Total indexed images: {len(images)}")
    
    # Face stats
    faces_count = {}
    ocr_count = 0
    for path, meta in images:
        for face in meta.get("faces", []):
            faces_count[face] = faces_count.get(face, 0) + 1
        if meta.get("ocr_text"):
            ocr_count += 1
    
    print(f"Images with text (OCR): {ocr_count}")
    
    if faces_count:
        print(f"\nFaces detected:")
        for name, count in sorted(faces_count.items(), key=lambda x: -x[1]):
            print(f"  • {name}: {count} photos")
    
    # Known faces
    from image_search.core import FaceIdentifier
    face_id = FaceIdentifier(data_dir=args.data_dir)
    print(f"\nKnown faces registered: {len(face_id.known_db)}")
    
    # Database size
    db_path = Path(args.data_dir) / "qdrant_db"
    if db_path.exists():
        size = sum(f.stat().st_size for f in db_path.rglob("*") if f.is_file())
        print(f"Database size: {size / 1024 / 1024:.1f} MB")
    
    engine.close()


def cmd_test(args):
    """Test individual components"""
    print(f"\n🧪 Testing: {args.component}\n")
    
    if args.component == "clip":
        from image_search.core.embedder import MLXClipWrapper
        
        print("Loading CLIP model...")
        clip = MLXClipWrapper()
        
        # Test text encoding
        text = args.input or "a photo of a cat"
        print(f"Encoding text: '{text}'")
        vec = clip.encode_text(text)
        print(f"Vector dim: {len(vec)}")
        print(f"First 5 values: {vec[:5]}")
        print("✓ CLIP text encoding works")
        
        # Test image encoding if provided
        if args.image:
            print(f"\nEncoding image: {args.image}")
            vec = clip.encode_image(args.image)
            print(f"Vector dim: {len(vec)}")
            print("✓ CLIP image encoding works")
    
    elif args.component == "ocr":
        from image_search.core import OCR
        
        if not args.image:
            print("Error: --image required for OCR test")
            sys.exit(1)
        
        print(f"Running OCR on: {args.image}")
        ocr = OCR()
        text = ocr.process(args.image)
        
        if text:
            print(f"Extracted text:\n{text}")
        else:
            print("No text found")
        print("✓ OCR works")
    
    elif args.component == "faces":
        if not args.image:
            print("Error: --image required for face test")
            sys.exit(1)
        
        from image_search.core import FaceIdentifier
        
        print(f"Detecting faces in: {args.image}")
        face_id = FaceIdentifier(data_dir=args.data_dir)
        faces = face_id.detect_and_name(args.image)
        
        if faces:
            print(f"Found {len(faces)} face(s):")
            for f in faces:
                print(f"  • {f['name']} (confidence: {f['confidence']:.1%})")
        else:
            print("No faces detected")
        print("✓ Face detection works")
    
    elif args.component == "all":
        # Run all tests
        for comp in ["clip", "ocr", "faces"]:
            args.component = comp
            try:
                cmd_test(args)
            except Exception as e:
                print(f"✗ {comp} failed: {e}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Image Search CLI - Development and debugging interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index all images in a folder
  image-search-cli index ~/Pictures --limit 100
  
  # Search for images
  image-search-cli search "sunset at beach"
  
  # List known faces
  image-search-cli faces list
  
  # Add a new person
  image-search-cli faces add --name "Alice" --photos photo1.jpg photo2.jpg
  
  # Test CLIP model
  image-search-cli test clip --input "a cat sitting on a couch"
  
  # Test OCR on an image
  image-search-cli test ocr --image receipt.jpg
"""
    )
    
    parser.add_argument(
        "--data-dir", "-d",
        type=Path,
        default=get_data_dir(),
        help="Data directory for index and faces (default: current dir)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index images from a directory")
    index_parser.add_argument("path", type=str, help="Path to image or directory")
    index_parser.add_argument("--limit", "-n", type=int, help="Max images to index")
    index_parser.set_defaults(func=cmd_index)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for images")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    search_parser.add_argument("--show-ocr", action="store_true", help="Show OCR text")
    search_parser.set_defaults(func=cmd_search)
    
    # Faces command
    faces_parser = subparsers.add_parser("faces", help="Manage known faces")
    faces_parser.add_argument("action", choices=["list", "add", "remove"], help="Action")
    faces_parser.add_argument("--name", type=str, help="Person name")
    faces_parser.add_argument("--photos", nargs="+", help="Photo paths (for add)")
    faces_parser.set_defaults(func=cmd_faces)
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test individual components")
    test_parser.add_argument(
        "component",
        choices=["clip", "ocr", "faces", "all"],
        help="Component to test"
    )
    test_parser.add_argument("--image", type=str, help="Test image path")
    test_parser.add_argument("--input", type=str, help="Test input text")
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()

