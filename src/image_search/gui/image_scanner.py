"""
Auto-discover images from macOS standard locations
"""
import os
from pathlib import Path
from typing import List, Set

from PyQt6.QtCore import QObject, pyqtSignal


# Common image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.tiff', '.tif', '.gif', '.bmp'}

# Directories to skip
SKIP_DIRS = {
    '.git', '.svn', 'node_modules', '__pycache__', '.Trash',
    'Library', 'Applications', '.cache', '.npm', '.venv', 'venv',
}


def get_macos_image_locations() -> List[Path]:
    """Get standard macOS locations where photos are typically stored"""
    home = Path.home()
    
    locations = [
        home / "Pictures",
        home / "Desktop",
        home / "Downloads",
        home / "Documents",
        # Photos Library exports
        home / "Pictures" / "Photos Library.photoslibrary" / "originals",
        # iCloud Photos
        home / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Pictures",
        # Screenshots
        home / "Desktop",  # macOS default screenshot location
    ]
    
    return [loc for loc in locations if loc.exists()]


def scan_directory(directory: Path, max_depth: int = 5) -> List[str]:
    """
    Recursively scan directory for images
    
    Args:
        directory: Root directory to scan
        max_depth: Maximum recursion depth
        
    Returns:
        List of image file paths
    """
    images = []
    
    def _scan(path: Path, depth: int):
        if depth > max_depth:
            return
            
        try:
            for entry in os.scandir(path):
                if entry.name.startswith('.'):
                    continue
                    
                if entry.is_dir(follow_symlinks=False):
                    if entry.name not in SKIP_DIRS:
                        _scan(Path(entry.path), depth + 1)
                elif entry.is_file():
                    ext = Path(entry.name).suffix.lower()
                    if ext in IMAGE_EXTENSIONS:
                        images.append(entry.path)
        except PermissionError:
            pass
        except OSError:
            pass
            
    _scan(directory, 0)
    return images


class ImageScanner(QObject):
    """Background scanner for discovering images on the system"""
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(str, int)  # location name, count found so far
    finished = pyqtSignal(list)  # all image paths
    error = pyqtSignal(str)
    
    def __init__(self, locations: List[Path] = None, max_images: int = 10000):
        super().__init__()
        self.locations = locations or get_macos_image_locations()
        self.max_images = max_images
        self._cancelled = False
        
    def run(self):
        """Scan all locations for images"""
        self.started.emit()
        all_images: Set[str] = set()
        
        try:
            for location in self.locations:
                if self._cancelled:
                    break
                    
                if not location.exists():
                    continue
                    
                self.progress.emit(str(location.name), len(all_images))
                
                # Scan this location
                found = scan_directory(location)
                all_images.update(found)
                
                # Cap at max_images
                if len(all_images) >= self.max_images:
                    break
                    
            # Convert to sorted list
            result = sorted(all_images)[:self.max_images]
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
            
    def cancel(self):
        self._cancelled = True


def quick_scan_count() -> int:
    """Quick count of images in standard locations (for UI preview)"""
    count = 0
    for location in get_macos_image_locations():
        if location.exists():
            try:
                for entry in os.scandir(location):
                    if entry.is_file():
                        ext = Path(entry.name).suffix.lower()
                        if ext in IMAGE_EXTENSIONS:
                            count += 1
            except (PermissionError, OSError):
                pass
    return count

