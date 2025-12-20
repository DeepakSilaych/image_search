"""
Background worker threads for non-blocking operations
"""
from pathlib import Path
from typing import List

from PyQt6.QtCore import QObject, pyqtSignal


class SearchWorker(QObject):
    """Worker for running search in background thread"""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, engine, query: str, limit: int = 20):
        super().__init__()
        self.engine = engine
        self.query = query
        self.limit = limit
        
    def run(self):
        try:
            results = self.engine.search(self.query, limit=self.limit)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class IndexWorker(QObject):
    """Worker for indexing images in background"""
    
    progress = pyqtSignal(int, int, str)  # current, total, path
    finished = pyqtSignal(int)  # count indexed
    error = pyqtSignal(str)
    
    def __init__(self, engine, image_paths: List[str]):
        super().__init__()
        self.engine = engine
        self.image_paths = image_paths
        self._cancelled = False
        
    def run(self):
        try:
            indexed = 0
            total = len(self.image_paths)
            
            for i, path in enumerate(self.image_paths):
                if self._cancelled:
                    break
                    
                self.progress.emit(i + 1, total, path)
                
                try:
                    self.engine.add_image(path)
                    indexed += 1
                except Exception as e:
                    print(f"Failed to index {path}: {e}")
                    
            self.finished.emit(indexed)
        except Exception as e:
            self.error.emit(str(e))
            
    def cancel(self):
        self._cancelled = True


class BrowseWorker(QObject):
    """Worker for loading all indexed images"""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def run(self):
        try:
            results = self.engine.get_all_images(limit=1000)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

