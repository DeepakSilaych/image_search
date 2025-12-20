"""
Full-screen image preview dialog
"""
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QKeyEvent, QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget, QApplication
)

from .theme import COLORS


class ImagePreviewDialog(QDialog):
    """Full image preview with metadata panel"""
    
    def __init__(self, image_path: str, metadata: dict = None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.metadata = metadata or {}
        
        self.setWindowTitle(Path(image_path).name)
        self.setModal(True)
        self.setMinimumSize(900, 700)
        
        # Remove window frame for more modern look
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Main container with rounded corners
        container = QFrame(self)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-radius: 16px;
                border: 1px solid {COLORS['separator']};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header bar
        header = self._create_header()
        container_layout.addWidget(header)
        
        # Content area
        content = QHBoxLayout()
        content.setContentsMargins(24, 16, 24, 24)
        content.setSpacing(24)
        
        # Image display
        image_container = self._create_image_display()
        content.addWidget(image_container, stretch=3)
        
        # Info panel
        info_panel = self._create_info_panel()
        content.addWidget(info_panel, stretch=1)
        
        container_layout.addLayout(content)
        
    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid {COLORS['separator']};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Title
        title = QLabel(Path(self.image_path).name)
        title.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("iconBtn")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                color: {COLORS['text_tertiary']};
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return header
        
    def _create_image_display(self) -> QLabel:
        # Scrollable image container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 12px;
                border: none;
            }}
        """)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("background-color: transparent;")
        
        # Load image
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            # Scale to fit dialog while maintaining aspect ratio
            scaled = pixmap.scaled(
                800, 600,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled)
        else:
            image_label.setText("Failed to load image")
            
        scroll.setWidget(image_label)
        return scroll
        
    def _create_info_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # File info section
        file_section = self._create_section("File Info")
        
        path = Path(self.image_path)
        file_section.addWidget(self._create_info_row("Name", path.name))
        file_section.addWidget(self._create_info_row("Type", path.suffix.upper()[1:]))
        
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            file_section.addWidget(self._create_info_row("Size", f"{size_mb:.2f} MB"))
            
        layout.addLayout(file_section)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['separator']};")
        layout.addWidget(sep)
        
        # Detection results
        detect_section = self._create_section("Detection")
        
        # Faces
        faces = self.metadata.get("faces", [])
        if faces:
            detect_section.addWidget(self._create_info_row("People", ", ".join(faces)))
        else:
            detect_section.addWidget(self._create_info_row("People", "None detected"))
            
        # OCR text
        ocr_text = self.metadata.get("ocr_text", "")
        if ocr_text:
            ocr_preview = ocr_text[:100] + "..." if len(ocr_text) > 100 else ocr_text
            detect_section.addWidget(self._create_info_row("Text", ocr_preview))
        else:
            detect_section.addWidget(self._create_info_row("Text", "None found"))
            
        # Match score
        score = self.metadata.get("score", 0)
        if score > 0:
            detect_section.addWidget(self._create_info_row("Match", f"{score:.0%}"))
            
        layout.addLayout(detect_section)
        
        layout.addStretch()
        
        # Action buttons
        open_btn = QPushButton("Open in Finder")
        open_btn.setObjectName("secondaryBtn")
        open_btn.clicked.connect(self._open_in_finder)
        layout.addWidget(open_btn)
        
        return panel
        
    def _create_section(self, title: str) -> QVBoxLayout:
        section = QVBoxLayout()
        section.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text_tertiary']};
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        section.addWidget(title_label)
        
        return section
        
    def _create_info_row(self, label: str, value: str) -> QWidget:
        row = QWidget()
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_tertiary']};
        """)
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setWordWrap(True)
        value_widget.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(value_widget)
        
        return row
        
    def _open_in_finder(self):
        import subprocess
        subprocess.run(["open", "-R", self.image_path])
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
        
    def mousePressEvent(self, event):
        # Allow dragging the dialog
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

