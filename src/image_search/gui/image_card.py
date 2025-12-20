"""
Image card widget for displaying search results
"""
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
)

from .theme import COLORS


class ImageCard(QFrame):
    """A clickable image card with hover effects - thumbnail only"""
    
    clicked = pyqtSignal(str, dict)  # path, metadata
    
    def __init__(self, image_path: str, score: float = 0.0, 
                 faces: list = None, ocr_text: str = "", parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.score = score
        self.faces = faces or []
        self.ocr_text = ocr_text
        self.setObjectName("imageCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_ui()
        self._setup_effects()
        
    def _setup_ui(self):
        # Compact size - just thumbnail
        self.setFixedSize(180, 180)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)
        
        # Thumbnail container
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(168, 168)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-radius: 8px;
        """)
        
        # Load and display thumbnail
        self._load_thumbnail()
        layout.addWidget(self.thumbnail_label)
        
    def _load_thumbnail(self):
        """Load and scale image thumbnail"""
        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self.thumbnail_label.setText("⚠️")
            return
            
        # Scale to cover (crop to square)
        size = 168
        w, h = pixmap.width(), pixmap.height()
        
        # Crop to square from center
        if w > h:
            x = (w - h) // 2
            pixmap = pixmap.copy(x, 0, h, h)
        elif h > w:
            y = (h - w) // 2
            pixmap = pixmap.copy(0, y, w, w)
            
        scaled = pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Create rounded corners
        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, 8, 8)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        
        self.thumbnail_label.setPixmap(rounded)
        
    def _setup_effects(self):
        """Add subtle shadow effect"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        
    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#imageCard {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 10px;
            }}
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#imageCard {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
            }}
        """)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            metadata = {
                "score": self.score,
                "faces": self.faces,
                "ocr_text": self.ocr_text,
            }
            self.clicked.emit(self.image_path, metadata)
        super().mousePressEvent(event)
