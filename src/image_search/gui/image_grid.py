"""
Scrollable image grid with lazy loading pagination
"""
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)

from .image_card import ImageCard
from .theme import COLORS


class ImageGrid(QScrollArea):
    """Scrollable grid with pagination - loads images on scroll"""
    
    image_clicked = pyqtSignal(str, dict)  # path, metadata
    load_more = pyqtSignal()  # request more images
    
    PAGE_SIZE = 40  # images per page
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.columns = 5
        self._all_data = []  # full dataset
        self._loaded_count = 0  # how many loaded so far
        self._is_search_mode = False
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: none;")
        
        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.setWidget(self.container)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 16, 24, 24)
        self.main_layout.setSpacing(16)
        
        # Grid layout - centered
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        grid_container = QHBoxLayout()
        grid_container.addStretch()
        grid_container.addWidget(self.grid_widget)
        grid_container.addStretch()
        self.main_layout.addLayout(grid_container)
        
        # Load more button
        self.load_more_btn = QPushButton("Load More")
        self.load_more_btn.setObjectName("secondaryBtn")
        self.load_more_btn.setFixedWidth(200)
        self.load_more_btn.clicked.connect(self._load_next_page)
        self.load_more_btn.hide()
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.load_more_btn)
        btn_container.addStretch()
        self.main_layout.addLayout(btn_container)
        
        self.main_layout.addStretch()
        
        # Empty state
        self._show_empty_state()
        
        # Connect scroll event for lazy loading
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
    def _show_empty_state(self, message: str = None):
        """Show empty state with icon and message"""
        self._clear_grid()
        
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(16)
        
        # Icon
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_label)
        
        # Message
        if message is None:
            message = "Search for images using natural language"
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text_tertiary']};
        """)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(msg_label)
        
        # Hint
        hint_label = QLabel('Try: "sunset at the beach" or "photos of mom"')
        hint_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_tertiary']};
            opacity: 0.7;
        """)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(hint_label)
        
        self.grid_layout.addWidget(empty_widget, 0, 0, 1, self.columns)
        self.load_more_btn.hide()
        
    def _clear_grid(self):
        """Remove all items from grid"""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def _add_cards(self, data_slice: list):
        """Add cards for a slice of data"""
        start_idx = len(self.cards)
        
        for i, item in enumerate(data_slice):
            idx = start_idx + i
            
            # Extract data based on mode
            if self._is_search_mode:
                path, score, ocr_text, faces = item
            else:
                path, metadata = item
                score = 0
                faces = metadata.get("faces", [])
                ocr_text = metadata.get("ocr_text", "")
            
            card = ImageCard(
                image_path=path,
                score=score,
                faces=faces,
                ocr_text=ocr_text
            )
            card.clicked.connect(self._on_card_clicked)
            
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            
    def _load_next_page(self):
        """Load next page of images"""
        if self._loaded_count >= len(self._all_data):
            self.load_more_btn.hide()
            return
            
        end = min(self._loaded_count + self.PAGE_SIZE, len(self._all_data))
        data_slice = self._all_data[self._loaded_count:end]
        self._add_cards(data_slice)
        self._loaded_count = end
        
        # Update button
        remaining = len(self._all_data) - self._loaded_count
        if remaining > 0:
            self.load_more_btn.setText(f"Load More ({remaining} remaining)")
            self.load_more_btn.show()
        else:
            self.load_more_btn.hide()
            
    def _on_scroll(self, value):
        """Auto-load more when near bottom"""
        scrollbar = self.verticalScrollBar()
        if scrollbar.maximum() > 0:
            ratio = value / scrollbar.maximum()
            if ratio > 0.85 and self._loaded_count < len(self._all_data):
                self._load_next_page()
                
    def display_results(self, results: list):
        """
        Display search results in grid
        results: [(path, score, ocr_text, faces), ...]
        """
        self._clear_grid()
        self._all_data = results
        self._loaded_count = 0
        self._is_search_mode = True
        
        if not results:
            self._show_empty_state("No images found")
            return
            
        self._load_next_page()
            
    def display_indexed_images(self, images: list):
        """
        Display all indexed images (for browse mode)
        images: [(path, metadata), ...]
        """
        self._clear_grid()
        self._all_data = images
        self._loaded_count = 0
        self._is_search_mode = False
        
        if not images:
            self._show_empty_state("No images indexed yet.\nDrag & drop images to add them.")
            return
            
        self._load_next_page()
            
    def _on_card_clicked(self, path: str, metadata: dict):
        self.image_clicked.emit(path, metadata)
        
    def resizeEvent(self, event):
        """Adjust columns based on width - calculate for symmetric fit"""
        width = event.size().width() - 48  # subtract margins
        card_width = 192  # 180 card + 12 spacing
        new_cols = max(2, width // card_width)
        if new_cols != self.columns:
            self.columns = new_cols
            self._reflow_grid()
        super().resizeEvent(event)
        
    def _reflow_grid(self):
        """Reflow cards to new column count"""
        for idx, card in enumerate(self.cards):
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(card, row, col)
