"""
Tema visual para Athena IDE.
Define colores, estilos y paleta para la interfaz.
Soporta múltiples temas con cambio dinámico.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class Theme:
    """Definición de un tema de colores."""
    name: str
    display_name: str
    
    # Fondos
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str
    bg_selected: str
    
    # Texto
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # Acentos
    accent_blue: str
    accent_green: str
    accent_red: str
    accent_yellow: str
    accent_purple: str
    accent_teal: str
    accent_orange: str
    
    # Bordes
    border: str
    border_focus: str
    
    # Syntax highlighting
    syntax_keyword: str
    syntax_string: str
    syntax_number: str
    syntax_comment: str
    syntax_function: str
    syntax_class: str
    syntax_operator: str
    syntax_decorator: str


# === TEMAS DISPONIBLES ===

THEME_DARK_DEFAULT = Theme(
    name="dark_default",
    display_name="🌙 Oscuro (Por defecto)",
    bg_primary="#1e1e2e",
    bg_secondary="#181825",
    bg_tertiary="#11111b",
    bg_hover="#313244",
    bg_selected="#45475a",
    text_primary="#cdd6f4",
    text_secondary="#a6adc8",
    text_muted="#6c7086",
    accent_blue="#89b4fa",
    accent_green="#a6e3a1",
    accent_red="#f38ba8",
    accent_yellow="#f9e2af",
    accent_purple="#cba6f7",
    accent_teal="#94e2d5",
    accent_orange="#fab387",
    border="#313244",
    border_focus="#89b4fa",
    syntax_keyword="#cba6f7",
    syntax_string="#a6e3a1",
    syntax_number="#fab387",
    syntax_comment="#6c7086",
    syntax_function="#89b4fa",
    syntax_class="#f9e2af",
    syntax_operator="#89dceb",
    syntax_decorator="#f5c2e7",
)

THEME_DARK_BLUE = Theme(
    name="dark_blue",
    display_name="🔵 Oscuro Azul",
    bg_primary="#0d1117",
    bg_secondary="#161b22",
    bg_tertiary="#010409",
    bg_hover="#21262d",
    bg_selected="#30363d",
    text_primary="#c9d1d9",
    text_secondary="#8b949e",
    text_muted="#484f58",
    accent_blue="#58a6ff",
    accent_green="#3fb950",
    accent_red="#f85149",
    accent_yellow="#d29922",
    accent_purple="#a371f7",
    accent_teal="#39d353",
    accent_orange="#f0883e",
    border="#30363d",
    border_focus="#58a6ff",
    syntax_keyword="#ff7b72",
    syntax_string="#a5d6ff",
    syntax_number="#79c0ff",
    syntax_comment="#8b949e",
    syntax_function="#d2a8ff",
    syntax_class="#ffa657",
    syntax_operator="#79c0ff",
    syntax_decorator="#ff7b72",
)

THEME_DARK_GREEN = Theme(
    name="dark_green",
    display_name="🌲 Oscuro Verde",
    bg_primary="#1a1d1a",
    bg_secondary="#141614",
    bg_tertiary="#0f110f",
    bg_hover="#252825",
    bg_selected="#2f332f",
    text_primary="#d4e4d4",
    text_secondary="#a8b8a8",
    text_muted="#6a7a6a",
    accent_blue="#7ec8e3",
    accent_green="#7dce82",
    accent_red="#e57373",
    accent_yellow="#ffd54f",
    accent_purple="#b39ddb",
    accent_teal="#4db6ac",
    accent_orange="#ffb74d",
    border="#2f332f",
    border_focus="#7dce82",
    syntax_keyword="#b39ddb",
    syntax_string="#7dce82",
    syntax_number="#ffb74d",
    syntax_comment="#6a7a6a",
    syntax_function="#7ec8e3",
    syntax_class="#ffd54f",
    syntax_operator="#4db6ac",
    syntax_decorator="#e57373",
)

THEME_LIGHT = Theme(
    name="light",
    display_name="☀️ Claro",
    bg_primary="#ffffff",
    bg_secondary="#f5f5f5",
    bg_tertiary="#ebebeb",
    bg_hover="#e0e0e0",
    bg_selected="#d0d0d0",
    text_primary="#1e1e1e",
    text_secondary="#444444",
    text_muted="#888888",
    accent_blue="#0066cc",
    accent_green="#28a745",
    accent_red="#dc3545",
    accent_yellow="#ffc107",
    accent_purple="#6f42c1",
    accent_teal="#17a2b8",
    accent_orange="#fd7e14",
    border="#d0d0d0",
    border_focus="#0066cc",
    syntax_keyword="#0000ff",
    syntax_string="#008000",
    syntax_number="#098658",
    syntax_comment="#6a737d",
    syntax_function="#795e26",
    syntax_class="#267f99",
    syntax_operator="#000000",
    syntax_decorator="#af00db",
)

THEME_MONOKAI = Theme(
    name="monokai",
    display_name="🎨 Monokai",
    bg_primary="#272822",
    bg_secondary="#1e1f1c",
    bg_tertiary="#171814",
    bg_hover="#3e3d32",
    bg_selected="#49483e",
    text_primary="#f8f8f2",
    text_secondary="#cfcfc2",
    text_muted="#75715e",
    accent_blue="#66d9ef",
    accent_green="#a6e22e",
    accent_red="#f92672",
    accent_yellow="#e6db74",
    accent_purple="#ae81ff",
    accent_teal="#66d9ef",
    accent_orange="#fd971f",
    border="#49483e",
    border_focus="#a6e22e",
    syntax_keyword="#f92672",
    syntax_string="#e6db74",
    syntax_number="#ae81ff",
    syntax_comment="#75715e",
    syntax_function="#a6e22e",
    syntax_class="#66d9ef",
    syntax_operator="#f92672",
    syntax_decorator="#a6e22e",
)

THEME_DRACULA = Theme(
    name="dracula",
    display_name="🧛 Dracula",
    bg_primary="#282a36",
    bg_secondary="#21222c",
    bg_tertiary="#191a21",
    bg_hover="#44475a",
    bg_selected="#44475a",
    text_primary="#f8f8f2",
    text_secondary="#e0e0e0",
    text_muted="#6272a4",
    accent_blue="#8be9fd",
    accent_green="#50fa7b",
    accent_red="#ff5555",
    accent_yellow="#f1fa8c",
    accent_purple="#bd93f9",
    accent_teal="#8be9fd",
    accent_orange="#ffb86c",
    border="#44475a",
    border_focus="#bd93f9",
    syntax_keyword="#ff79c6",
    syntax_string="#f1fa8c",
    syntax_number="#bd93f9",
    syntax_comment="#6272a4",
    syntax_function="#50fa7b",
    syntax_class="#8be9fd",
    syntax_operator="#ff79c6",
    syntax_decorator="#50fa7b",
)

# Diccionario de temas disponibles
AVAILABLE_THEMES: Dict[str, Theme] = {
    "dark_default": THEME_DARK_DEFAULT,
    "dark_blue": THEME_DARK_BLUE,
    "dark_green": THEME_DARK_GREEN,
    "light": THEME_LIGHT,
    "monokai": THEME_MONOKAI,
    "dracula": THEME_DRACULA,
}

# Tema actual (global)
_current_theme: Theme = THEME_DARK_DEFAULT


def get_current_theme() -> Theme:
    """Retorna el tema actual."""
    return _current_theme


def set_theme(theme_name: str) -> Theme:
    """Cambia el tema actual."""
    global _current_theme
    if theme_name in AVAILABLE_THEMES:
        _current_theme = AVAILABLE_THEMES[theme_name]
    return _current_theme


def get_theme_names() -> list:
    """Retorna lista de nombres de temas disponibles."""
    return [(t.name, t.display_name) for t in AVAILABLE_THEMES.values()]


# Alias para compatibilidad
def get_colors() -> dict:
    """Retorna los colores del tema actual como diccionario."""
    t = _current_theme
    return {
        "bg_primary": t.bg_primary,
        "bg_secondary": t.bg_secondary,
        "bg_tertiary": t.bg_tertiary,
        "bg_hover": t.bg_hover,
        "bg_selected": t.bg_selected,
        "text_primary": t.text_primary,
        "text_secondary": t.text_secondary,
        "text_muted": t.text_muted,
        "accent_blue": t.accent_blue,
        "accent_green": t.accent_green,
        "accent_red": t.accent_red,
        "accent_yellow": t.accent_yellow,
        "accent_purple": t.accent_purple,
        "accent_teal": t.accent_teal,
        "accent_orange": t.accent_orange,
        "border": t.border,
        "border_focus": t.border_focus,
        "syntax_keyword": t.syntax_keyword,
        "syntax_string": t.syntax_string,
        "syntax_number": t.syntax_number,
        "syntax_comment": t.syntax_comment,
        "syntax_function": t.syntax_function,
        "syntax_class": t.syntax_class,
        "syntax_operator": t.syntax_operator,
        "syntax_decorator": t.syntax_decorator,
    }


# Para compatibilidad con código existente
COLORS = get_colors()


def get_main_stylesheet() -> str:
    """Retorna el stylesheet principal para toda la aplicación."""
    c = get_colors()
    return f"""
    /* === GLOBAL === */
    QMainWindow, QWidget {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }}
    
    /* === SCROLL BARS === */
    QScrollBar:vertical {{
        background: {c['bg_secondary']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['bg_hover']};
        border-radius: 6px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['bg_selected']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {c['bg_secondary']};
        height: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['bg_hover']};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    /* === BUTTONS === */
    QPushButton {{
        background-color: {c['accent_blue']};
        color: {c['bg_primary']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        opacity: 0.9;
    }}
    QPushButton:pressed {{
        opacity: 0.8;
    }}
    QPushButton:disabled {{
        background-color: {c['bg_hover']};
        color: {c['text_muted']};
    }}
    
    /* === TEXT INPUTS === */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {c['bg_tertiary']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px;
        selection-background-color: {c['accent_blue']};
        selection-color: {c['bg_primary']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {c['border_focus']};
    }}
    
    /* === LABELS === */
    QLabel {{
        color: {c['text_primary']};
    }}
    
    /* === TREE VIEW (Project Explorer) === */
    QTreeView {{
        background-color: {c['bg_secondary']};
        border: none;
        outline: none;
    }}
    QTreeView::item {{
        padding: 4px 8px;
        border-radius: 4px;
    }}
    QTreeView::item:hover {{
        background-color: {c['bg_hover']};
    }}
    QTreeView::item:selected {{
        background-color: {c['accent_blue']};
        color: {c['bg_primary']};
    }}
    QTreeView::branch {{
        background: transparent;
    }}
    
    /* === TAB WIDGET === */
    QTabWidget::pane {{
        border: none;
        background-color: {c['bg_primary']};
    }}
    QTabBar::tab {{
        background-color: {c['bg_secondary']};
        color: {c['text_secondary']};
        padding: 8px 16px;
        border: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {c['bg_hover']};
    }}
    
    /* === SPLITTER === */
    QSplitter::handle {{
        background-color: {c['border']};
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* === MENU === */
    QMenuBar {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        border-bottom: 1px solid {c['border']};
        padding: 2px;
    }}
    QMenuBar::item {{
        padding: 6px 10px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background-color: {c['bg_hover']};
    }}
    QMenu {{
        background-color: {c['bg_secondary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 8px 32px 8px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {c['accent_blue']};
        color: {c['bg_primary']};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {c['border']};
        margin: 4px 8px;
    }}
    
    /* === STATUS BAR === */
    QStatusBar {{
        background-color: {c['bg_secondary']};
        color: {c['text_secondary']};
        border-top: 1px solid {c['border']};
    }}
"""


def get_editor_stylesheet() -> str:
    """Stylesheet específico para el editor de código."""
    c = get_colors()
    return f"""
    QPlainTextEdit {{
        background-color: {c['bg_primary']};
        color: {c['text_primary']};
        border: none;
        font-family: 'Consolas', 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 14px;
        line-height: 1.5;
    }}
    """


def get_ai_panel_stylesheet() -> str:
    """Stylesheet específico para el panel de Athena."""
    c = get_colors()
    return f"""
    QWidget#ai_panel {{
        background-color: {c['bg_secondary']};
        border-left: 1px solid {c['border']};
    }}
    """


# Exportar 
__all__ = [
    'Theme', 'COLORS', 'AVAILABLE_THEMES',
    'get_current_theme', 'set_theme', 'get_theme_names', 'get_colors',
    'get_main_stylesheet', 'get_editor_stylesheet', 'get_ai_panel_stylesheet'
]
