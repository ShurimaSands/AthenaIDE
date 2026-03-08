"""
Widget de tabs para múltiples archivos abiertos.
"""
import os
from PySide6.QtWidgets import QTabWidget, QMessageBox
from PySide6.QtCore import Signal

from ui.editor import CodeEditor


class EditorTabWidget(QTabWidget):
    """
    Widget de tabs para gestionar múltiples archivos abiertos.
    Cada tab contiene un CodeEditor con el contenido del archivo.
    """
    
    # Señales
    file_opened = Signal(str)     # path del archivo abierto
    file_closed = Signal(str)     # path del archivo cerrado
    file_saved = Signal(str)      # path del archivo guardado
    active_file_changed = Signal(str)  # path del archivo activo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Mapeo de path -> índice de tab
        self._file_tabs: dict[str, int] = {}
        
        # Conectar señales
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.currentChanged.connect(self._on_current_changed)
    
    def open_file(self, path: str) -> CodeEditor:
        """
        Abre un archivo en una nueva tab o activa una existente.
        
        Args:
            path: Ruta absoluta al archivo
        
        Returns:
            El CodeEditor del archivo
        """
        path = os.path.normpath(path)
        
        # Si ya está abierto, activar esa tab
        if path in self._file_tabs:
            self.setCurrentIndex(self._file_tabs[path])
            return self.widget(self._file_tabs[path])
        
        # Leer contenido
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(
                self, "Error", 
                f"No se pudo abrir el archivo:\n{str(e)}"
            )
            return None
        
        # Crear editor
        editor = CodeEditor()
        editor.set_file(path, content)
        editor.file_modified.connect(
            lambda modified: self._update_tab_title(path, modified)
        )
        
        # Añadir tab
        filename = os.path.basename(path)
        index = self.addTab(editor, filename)
        self._file_tabs[path] = index
        
        # Activar tab
        self.setCurrentIndex(index)
        
        self.file_opened.emit(path)
        return editor
    
    def save_current(self) -> bool:
        """Guarda el archivo de la tab activa."""
        editor = self.current_editor()
        if not editor or not editor.current_file:
            return False
        
        return self.save_file(editor.current_file)
    
    def save_file(self, path: str) -> bool:
        """
        Guarda un archivo específico.
        
        Args:
            path: Ruta del archivo a guardar
        
        Returns:
            True si se guardó exitosamente
        """
        if path not in self._file_tabs:
            return False
        
        editor = self.widget(self._file_tabs[path])
        if not isinstance(editor, CodeEditor):
            return False
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.get_content())
            
            editor.mark_saved()
            self._update_tab_title(path, False)
            self.file_saved.emit(path)
            return True
        
        except Exception as e:
            QMessageBox.warning(
                self, "Error",
                f"No se pudo guardar el archivo:\n{str(e)}"
            )
            return False
    
    def save_all(self) -> bool:
        """Guarda todos los archivos modificados."""
        success = True
        for path in list(self._file_tabs.keys()):
            editor = self.widget(self._file_tabs[path])
            if isinstance(editor, CodeEditor) and editor.is_modified:
                if not self.save_file(path):
                    success = False
        return success
    
    def close_tab(self, index: int) -> bool:
        """
        Cierra una tab específica.
        
        Args:
            index: Índice de la tab
        
        Returns:
            True si se cerró exitosamente
        """
        editor = self.widget(index)
        if not isinstance(editor, CodeEditor):
            self.removeTab(index)
            return True
        
        path = editor.current_file
        
        # Si hay cambios sin guardar, preguntar
        if editor.is_modified:
            reply = QMessageBox.question(
                self, "Guardar cambios",
                f"¿Deseas guardar los cambios en {os.path.basename(path)}?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file(path):
                    return False
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        
        # Cerrar tab
        self.removeTab(index)
        if path in self._file_tabs:
            del self._file_tabs[path]
        
        # Actualizar índices
        self._update_file_indices()
        
        self.file_closed.emit(path)
        return True
    
    def _on_tab_close_requested(self, index: int):
        """Callback cuando se solicita cerrar una tab."""
        self.close_tab(index)
    
    def _on_current_changed(self, index: int):
        """Callback cuando cambia la tab activa."""
        editor = self.widget(index)
        if isinstance(editor, CodeEditor) and editor.current_file:
            self.active_file_changed.emit(editor.current_file)
    
    def _update_tab_title(self, path: str, modified: bool):
        """Actualiza el título de una tab (añade * si está modificado)."""
        if path not in self._file_tabs:
            return
        
        index = self._file_tabs[path]
        filename = os.path.basename(path)
        title = f"• {filename}" if modified else filename
        self.setTabText(index, title)
    
    def _update_file_indices(self):
        """Recalcula los índices de archivos después de cerrar una tab."""
        new_indices = {}
        for i in range(self.count()):
            editor = self.widget(i)
            if isinstance(editor, CodeEditor) and editor.current_file:
                new_indices[editor.current_file] = i
        self._file_tabs = new_indices
    
    def current_editor(self) -> CodeEditor:
        """Retorna el editor activo."""
        widget = self.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None
    
    def current_file_path(self) -> str:
        """Retorna la ruta del archivo activo."""
        editor = self.current_editor()
        return editor.current_file if editor else None
    
    def get_selected_code(self) -> str:
        """Retorna el código seleccionado en el editor activo."""
        editor = self.current_editor()
        return editor.selected_or_all() if editor else ""
    
    def has_unsaved_changes(self) -> bool:
        """Verifica si hay archivos con cambios sin guardar."""
        for i in range(self.count()):
            editor = self.widget(i)
            if isinstance(editor, CodeEditor) and editor.is_modified:
                return True
        return False
    
    def get_open_files(self) -> list[str]:
        """Retorna lista de archivos abiertos."""
        return list(self._file_tabs.keys())
