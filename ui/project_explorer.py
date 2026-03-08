"""
Explorador de proyecto mejorado.
Árbol de archivos con iconos, menú contextual y operaciones.
"""
import os
from PySide6.QtWidgets import (
    QTreeView, QFileSystemModel, QMenu, QInputDialog, 
    QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from ui.theme import COLORS


class ProjectExplorer(QTreeView):
    """
    Explorador de archivos del proyecto.
    Muestra el árbol de carpetas y archivos con operaciones básicas.
    """
    
    # Señales
    file_selected = Signal(str)      # Cuando se hace doble click en un archivo
    file_created = Signal(str)       # Cuando se crea un archivo nuevo
    directory_created = Signal(str)  # Cuando se crea un directorio
    
    def __init__(self, root: str, parent=None):
        super().__init__(parent)
        
        self.root_path = os.path.abspath(root)
        
        # Modelo del sistema de archivos
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.root_path)
        
        # Mostrar todos los archivos (sin filtros)
        # Esto permite ver archivos en subcarpetas
        
        # Configurar vista
        self.setModel(self.file_model)
        self.setRootIndex(self.file_model.index(self.root_path))
        
        # Ocultar columnas innecesarias (tamaño, tipo, fecha)
        self.setHeaderHidden(True)
        for i in range(1, self.file_model.columnCount()):
            self.hideColumn(i)
        
        # Configuración de selección
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAnimated(True)
        self.setIndentation(16)
        
        # Estilo
        self.setStyleSheet(f"""
            QTreeView {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                outline: none;
                font-size: 12px;
            }}
            QTreeView::item {{
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QTreeView::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QTreeView::item:selected {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['bg_primary']};
            }}
            QTreeView::branch {{
                background: transparent;
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {{
                image: none;
                border-image: none;
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {{
                image: none;
                border-image: none;
            }}
        """)
        
        # Conectar señales
        self.doubleClicked.connect(self._on_double_click)
    
    def _on_double_click(self, index):
        """Callback para doble click en un item."""
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.file_selected.emit(path)
    
    def get_selected_path(self) -> str:
        """Retorna la ruta del item seleccionado."""
        indexes = self.selectedIndexes()
        if indexes:
            return self.file_model.filePath(indexes[0])
        return self.root_path
    
    def contextMenuEvent(self, event):
        """Menú contextual para operaciones de archivos."""
        index = self.indexAt(event.pos())
        path = self.file_model.filePath(index) if index.isValid() else self.root_path
        
        # Determinar directorio base para nuevos archivos
        if os.path.isfile(path):
            base_dir = os.path.dirname(path)
        else:
            base_dir = path if path else self.root_path
        
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['bg_primary']};
            }}
        """)
        
        # Acciones
        action_new_file = menu.addAction("📄 Nuevo archivo")
        action_new_folder = menu.addAction("📁 Nueva carpeta")
        menu.addSeparator()
        
        action_rename = None
        action_delete = None
        
        if index.isValid():
            action_rename = menu.addAction("✏️ Renombrar")
            action_delete = menu.addAction("🗑️ Eliminar")
        
        menu.addSeparator()
        action_refresh = menu.addAction("🔄 Actualizar")
        
        # Ejecutar menú
        action = menu.exec(event.globalPos())
        
        if action == action_new_file:
            self._create_file(base_dir)
        elif action == action_new_folder:
            self._create_folder(base_dir)
        elif action == action_rename and index.isValid():
            self._rename_item(path)
        elif action == action_delete and index.isValid():
            self._delete_item(path)
        elif action == action_refresh:
            self._refresh()
    
    def _create_file(self, base_dir: str):
        """Crea un nuevo archivo."""
        name, ok = QInputDialog.getText(
            self, "Nuevo archivo",
            "Nombre del archivo (con extensión):"
        )
        
        if ok and name:
            full_path = os.path.join(base_dir, name)
            
            if os.path.exists(full_path):
                QMessageBox.warning(
                    self, "Error",
                    f"Ya existe un archivo con ese nombre."
                )
                return
            
            try:
                # Crear archivo vacío
                with open(full_path, 'w', encoding='utf-8') as f:
                    pass
                
                self.file_created.emit(full_path)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error",
                    f"No se pudo crear el archivo:\n{str(e)}"
                )
    
    def _create_folder(self, base_dir: str):
        """Crea una nueva carpeta."""
        name, ok = QInputDialog.getText(
            self, "Nueva carpeta",
            "Nombre de la carpeta:"
        )
        
        if ok and name:
            full_path = os.path.join(base_dir, name)
            
            try:
                os.makedirs(full_path, exist_ok=True)
                self.directory_created.emit(full_path)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error",
                    f"No se pudo crear la carpeta:\n{str(e)}"
                )
    
    def _rename_item(self, path: str):
        """Renombra un archivo o carpeta."""
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(
            self, "Renombrar",
            "Nuevo nombre:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            
            if os.path.exists(new_path):
                QMessageBox.warning(
                    self, "Error",
                    "Ya existe un elemento con ese nombre."
                )
                return
            
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error",
                    f"No se pudo renombrar:\n{str(e)}"
                )
    
    def _delete_item(self, path: str):
        """Elimina un archivo o carpeta."""
        name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar {'la carpeta' if is_dir else 'el archivo'} '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.warning(
                    self, "Error",
                    f"No se pudo eliminar:\n{str(e)}"
                )
    
    def _refresh(self):
        """Refresca el árbol de archivos."""
        self.file_model.setRootPath("")
        self.file_model.setRootPath(self.root_path)
    
    def set_root(self, path: str):
        """Cambia el directorio raíz."""
        self.root_path = os.path.abspath(path)
        self.file_model.setRootPath(self.root_path)
        self.setRootIndex(self.file_model.index(self.root_path))
