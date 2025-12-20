"""
Settings panel for face management and preferences
"""
import os
import shutil
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QFileDialog,
    QLineEdit, QMessageBox, QInputDialog, QGridLayout
)

from .theme import COLORS


class FaceCard(QFrame):
    """Card showing a known face"""
    
    delete_clicked = pyqtSignal(str)  # person name
    
    def __init__(self, name: str, image_paths: list, parent=None):
        super().__init__(parent)
        self.name = name
        self.image_paths = image_paths
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {COLORS['separator']};
            }}
        """)
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Thumbnail grid (show up to 3 face samples)
        thumb_container = QWidget()
        thumb_layout = QHBoxLayout(thumb_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.setSpacing(4)
        
        for img_path in self.image_paths[:3]:
            thumb = self._create_thumbnail(img_path)
            thumb_layout.addWidget(thumb)
            
        layout.addWidget(thumb_container)
        
        # Name and count
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.name)
        name_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        info_layout.addWidget(name_label)
        
        count_label = QLabel(f"{len(self.image_paths)} reference photo(s)")
        count_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_tertiary']};
        """)
        info_layout.addWidget(count_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(36, 36)
        delete_btn.setObjectName("iconBtn")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.name))
        layout.addWidget(delete_btn)
        
    def _create_thumbnail(self, image_path: str) -> QLabel:
        label = QLabel()
        label.setFixedSize(48, 48)
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Scale and crop to square
            size = min(pixmap.width(), pixmap.height())
            cropped = pixmap.copy(
                (pixmap.width() - size) // 2,
                (pixmap.height() - size) // 2,
                size, size
            )
            scaled = cropped.scaled(
                48, 48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Round corners
            rounded = QPixmap(48, 48)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, 48, 48, 24, 24)  # Circular
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled)
            painter.end()
            
            label.setPixmap(rounded)
        else:
            label.setStyleSheet(f"""
                background-color: {COLORS['bg_tertiary']};
                border-radius: 24px;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setText("?")
            
        return label


class SettingsPanel(QWidget):
    """Settings panel with face management"""
    
    faces_updated = pyqtSignal()
    
    def __init__(self, data_dir: Path, parent=None):
        super().__init__(parent)
        self.data_dir = data_dir
        self.known_faces_dir = data_dir / "known_faces"
        
        self._setup_ui()
        self._load_faces()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Known Faces")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        
        header.addStretch()
        
        add_btn = QPushButton("+ Add Person")
        add_btn.clicked.connect(self._add_person)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Description
        desc = QLabel("Add reference photos for people you want to search by name.")
        desc.setObjectName("subtitle")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Face list scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.face_container = QWidget()
        self.face_layout = QVBoxLayout(self.face_container)
        self.face_layout.setContentsMargins(0, 0, 0, 0)
        self.face_layout.setSpacing(12)
        self.face_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.face_container)
        layout.addWidget(self.scroll, stretch=1)
        
        # Empty state
        self.empty_label = QLabel("No known faces yet.\nClick '+ Add Person' to get started.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_tertiary']};
            padding: 40px;
        """)
        self.face_layout.addWidget(self.empty_label)
        
    def _load_faces(self):
        """Load existing known faces"""
        # Clear existing cards
        for i in reversed(range(self.face_layout.count())):
            widget = self.face_layout.itemAt(i).widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
                
        if not self.known_faces_dir.exists():
            self.empty_label.show()
            return
            
        has_faces = False
        for person_dir in sorted(self.known_faces_dir.iterdir()):
            if not person_dir.is_dir():
                continue
                
            # Get image paths for this person
            images = [
                str(person_dir / f) 
                for f in os.listdir(person_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            
            if images:
                has_faces = True
                card = FaceCard(person_dir.name, images)
                card.delete_clicked.connect(self._delete_person)
                self.face_layout.addWidget(card)
                
        self.empty_label.setVisible(not has_faces)
        
    def _add_person(self):
        """Add a new person with reference photos"""
        name, ok = QInputDialog.getText(
            self, "Add Person",
            "Enter person's name:",
            QLineEdit.EchoMode.Normal
        )
        
        if not ok or not name.strip():
            return
            
        name = name.strip()
        person_dir = self.known_faces_dir / name
        
        if person_dir.exists():
            QMessageBox.warning(
                self, "Already Exists",
                f"A person named '{name}' already exists."
            )
            return
            
        # Select photos
        files, _ = QFileDialog.getOpenFileNames(
            self, f"Select photos of {name}",
            str(Path.home() / "Pictures"),
            "Images (*.jpg *.jpeg *.png)"
        )
        
        if not files:
            return
            
        # Create directory and copy photos
        person_dir.mkdir(parents=True, exist_ok=True)
        for src in files:
            dst = person_dir / Path(src).name
            shutil.copy2(src, dst)
            
        self._load_faces()
        self.faces_updated.emit()
        
    def _delete_person(self, name: str):
        """Delete a person and their photos"""
        reply = QMessageBox.question(
            self, "Delete Person",
            f"Delete '{name}' and all their reference photos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            person_dir = self.known_faces_dir / name
            if person_dir.exists():
                shutil.rmtree(person_dir)
                
            # Also remove from DB cache
            db_path = self.known_faces_dir / "known_faces_db.pkl"
            if db_path.exists():
                import pickle
                try:
                    with open(db_path, "rb") as f:
                        db = pickle.load(f)
                    if name in db:
                        del db[name]
                    with open(db_path, "wb") as f:
                        pickle.dump(db, f)
                except Exception:
                    pass
                    
            self._load_faces()
            self.faces_updated.emit()

