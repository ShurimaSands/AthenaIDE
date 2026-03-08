"""
Editor de código mejorado con números de línea y syntax highlighting.
"""
import os
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QTextCursor,
    QKeyEvent, QFontMetrics
)
from PySide6.QtCore import Qt, QRect, QSize, Signal

from ui.theme import COLORS, get_editor_stylesheet
from ui.syntax_highlighter import SyntaxHighlighter, get_language_from_extension


class LineNumberArea(QWidget):
    """Widget para mostrar números de línea."""
    
    def __init__(self, editor: 'CodeEditor'):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """
    Editor de código profesional con:
    - Números de línea
    - Syntax highlighting
    - Highlight de línea actual
    - Detección de lenguaje por extensión
    """
    
    # Señales
    file_modified = Signal(bool)  # Emitida cuando el contenido cambia
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración de fuente
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Configuración de tabulación
        self.setTabStopDistance(
            QFontMetrics(self.font()).horizontalAdvance(' ') * 4
        )
        
        # Estilo
        self.setStyleSheet(get_editor_stylesheet())
        
        # Area de números de línea
        self.line_number_area = LineNumberArea(self)
        
        # Highlighter (se configura al abrir archivo)
        self.highlighter = None
        self._current_file = None
        self._is_modified = False
        
        # Conectar señales
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self._on_text_changed)
        
        # Inicializar
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    
    @property
    def current_file(self) -> str:
        return self._current_file
    
    @property
    def is_modified(self) -> bool:
        return self._is_modified
    
    def _on_text_changed(self):
        """Maneja cambios en el texto."""
        if not self._is_modified:
            self._is_modified = True
            self.file_modified.emit(True)
    
    def set_file(self, path: str, content: str):
        """Carga un archivo en el editor."""
        self._current_file = path
        self._is_modified = False
        
        # Configurar highlighter según extensión
        ext = os.path.splitext(path)[1] if path else ''
        language = get_language_from_extension(ext)
        
        if self.highlighter:
            self.highlighter.set_language(language)
        else:
            self.highlighter = SyntaxHighlighter(self.document(), language)
        
        # Cargar contenido
        self.setPlainText(content)
        self._is_modified = False
        self.file_modified.emit(False)
        
    def animate_typing(self, content: str):
        """
        Simula la escritura mágica de código en tiempo real
        """
        import time
        from PySide6.QtWidgets import QApplication
        
        self.clear()
        self._is_modified = True
        
        # Opcional: configurar highlighter primero si no estaba
        if not self.highlighter and self._current_file:
             ext = os.path.splitext(self._current_file)[1]
             self.highlighter = SyntaxHighlighter(self.document(), get_language_from_extension(ext))
        
        # Añadir caracteres más rápido para archivos grandes
        chunk_size = max(1, len(content) // 200) 
        
        cursor = self.textCursor()
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            cursor.insertText(chunk)
            
            # Hacer scroll para seguir el cursor
            self.ensureCursorVisible()
            
            # Forzar actualización de UI para animación
            QApplication.processEvents()
            
            # Retardo mínimo para efecto visual pero que no sea eterno
            time.sleep(0.005)
            
        self.file_modified.emit(True)
        
    def get_content(self) -> str:
        """Retorna el contenido actual."""
        return self.toPlainText()
    
    def mark_saved(self):
        """Marca el archivo como guardado."""
        self._is_modified = False
        self.file_modified.emit(False)
    
    def selected_or_all(self) -> str:
        """Retorna el texto seleccionado o todo el contenido."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText().replace('\u2029', '\n')
        return self.toPlainText()
    
    def get_selected_text(self) -> str:
        """Retorna solo el texto seleccionado."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText().replace('\u2029', '\n')
        return ""
    
    def line_number_area_width(self) -> int:
        """Calcula el ancho necesario para el área de números."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        # Mínimo 3 dígitos de espacio
        digits = max(digits, 3)
        
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Actualiza el margen izquierdo para los números de línea."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect: QRect, dy: int):
        """Actualiza el área de números cuando hay scroll."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), 
                                         rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Ajusta el área de números al redimensionar."""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), 
                  self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Dibuja los números de línea."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(COLORS["bg_secondary"]))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        # Color para números normales y línea actual
        current_line = self.textCursor().blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                if block_number == current_line:
                    painter.setPen(QColor(COLORS["text_primary"]))
                else:
                    painter.setPen(QColor(COLORS["text_muted"]))
                
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
        
        painter.end()
    
    def highlight_current_line(self):
        """Resalta la línea actual."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(COLORS["bg_hover"])
            line_color.setAlpha(80)
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QTextFormat.Property.FullWidthSelection, True
            )
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Maneja atajos de teclado y auto-indentación."""
        # Tab → 4 espacios
        if event.key() == Qt.Key.Key_Tab and not event.modifiers():
            self.insertPlainText("    ")
            return
        
        # Enter → mantener indentación
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Calcular indentación actual
            indent = ""
            for char in text:
                if char in (' ', '\t'):
                    indent += char
                else:
                    break
            
            # Aumentar indent después de : 
            if text.rstrip().endswith(':'):
                indent += "    "
            
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return
        
        super().keyPressEvent(event)
    
    def get_cursor_position(self) -> tuple:
        """Retorna (línea, columna) actual."""
        cursor = self.textCursor()
        return (cursor.blockNumber() + 1, cursor.columnNumber() + 1)
