"""
macOS-inspired dark theme with San Francisco-style aesthetics
"""

COLORS = {
    "bg_primary": "#1c1c1e",
    "bg_secondary": "#2c2c2e", 
    "bg_tertiary": "#3a3a3c",
    "bg_elevated": "#48484a",
    "accent": "#0a84ff",
    "accent_hover": "#409cff",
    "accent_pressed": "#0077ed",
    "text_primary": "#ffffff",
    "text_secondary": "#ebebf5",
    "text_tertiary": "#8e8e93",
    "separator": "#38383a",
    "success": "#30d158",
    "warning": "#ff9f0a",
    "error": "#ff453a",
    "overlay": "rgba(0, 0, 0, 0.6)",
}

STYLESHEET = f"""
* {{
    font-family: ".AppleSystemUIFont", "Helvetica Neue", sans-serif;
}}

QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
}}

/* Search Bar */
QLineEdit#searchBar {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['separator']};
    border-radius: 12px;
    padding: 14px 20px 14px 48px;
    font-size: 17px;
    font-weight: 400;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent']};
}}

QLineEdit#searchBar:focus {{
    border: 2px solid {COLORS['accent']};
    background-color: {COLORS['bg_tertiary']};
}}

QLineEdit#searchBar::placeholder {{
    color: {COLORS['text_tertiary']};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['accent_pressed']};
}}

QPushButton#secondaryBtn {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {COLORS['bg_elevated']};
}}

QPushButton#iconBtn {{
    background-color: transparent;
    border-radius: 6px;
    padding: 8px;
}}

QPushButton#iconBtn:hover {{
    background-color: {COLORS['bg_tertiary']};
}}

/* Scroll Area */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_elevated']};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['bg_elevated']};
    border-radius: 4px;
}}

/* Labels */
QLabel {{
    color: {COLORS['text_primary']};
}}

QLabel#sectionTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}

QLabel#subtitle {{
    font-size: 13px;
    color: {COLORS['text_tertiary']};
}}

QLabel#statusLabel {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
    padding: 4px 8px;
    background-color: {COLORS['bg_secondary']};
    border-radius: 6px;
}}

/* Frame */
QFrame#card {{
    background-color: {COLORS['bg_secondary']};
    border-radius: 12px;
    border: 1px solid {COLORS['separator']};
}}

QFrame#imageCard {{
    background-color: {COLORS['bg_secondary']};
    border-radius: 8px;
    border: none;
}}

QFrame#imageCard:hover {{
    background-color: {COLORS['bg_tertiary']};
}}

/* Tab Widget */
QTabWidget::pane {{
    border: none;
    background-color: {COLORS['bg_primary']};
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_tertiary']};
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLORS['accent']};
    border-bottom: 2px solid {COLORS['accent']};
}}

QTabBar::tab:hover {{
    color: {COLORS['text_primary']};
}}

/* Progress Bar */
QProgressBar {{
    background-color: {COLORS['bg_tertiary']};
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 4px;
}}

/* Menu */
QMenu {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['separator']};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent']};
}}

/* Dialog */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['separator']};
}}

/* Tool Tip */
QToolTip {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['separator']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* List Widget */
QListWidget {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['separator']};
    border-radius: 8px;
    padding: 4px;
}}

QListWidget::item {{
    padding: 8px 12px;
    border-radius: 6px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_tertiary']};
}}
"""

