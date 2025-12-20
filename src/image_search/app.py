#!/usr/bin/env python3
"""
Image Search - macOS Application

A beautiful, local-first semantic image search powered by Apple Silicon.
Search your photos using natural language, face recognition, and OCR.
"""
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """Get the data directory for storing index and faces"""
    # In bundled app, use app support directory
    # In development, use project root/data
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        app_support = Path.home() / "Library" / "Application Support" / "ImageSearch"
        app_support.mkdir(parents=True, exist_ok=True)
        return app_support
    else:
        # Development mode - use project root/data
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Image Search")
    app.setApplicationDisplayName("Image Search")
    app.setOrganizationName("Personal")
    
    # Set default font
    font = QFont()
    font.setFamily(".AppleSystemUIFont")
    font.setPointSize(13)
    app.setFont(font)
    
    # Import and create main window
    from image_search.gui import MainWindow
    
    data_dir = get_data_dir()
    window = MainWindow(base_dir=data_dir)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

