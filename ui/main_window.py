"""
Ventana principal de Athena IDE.
Integra todos los componentes: explorador, editor de tabs, panel de Athena.
Estilo similar a VS Code con menús completos y selector de temas.
"""
import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QMenu, QStatusBar, QLabel, QFileDialog, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QActionGroup

from ui.tab_widget import EditorTabWidget
from ui.ai_panel import AIPanel
from ui.project_explorer import ProjectExplorer
from ui.theme import get_main_stylesheet, get_colors, set_theme, get_theme_names, AVAILABLE_THEMES
from config import get_config, save_config


class MainWindow(QMainWindow):
    """
    Ventana principal del IDE Athena.
    Layout: [Explorer | Editor Tabs | AI Panel]
    """
    
    def __init__(self, project_root: str = None):
        super().__init__()
        
        # Configuración
        self.config = get_config()
        
        # Cargar tema guardado
        if hasattr(self.config, 'theme') and self.config.theme:
            set_theme(self.config.theme)
        
        # Inicialmente sin proyecto abierto
        self.project_root = None
        self.explorer = None
        
        # Configurar ventana
        self.setWindowTitle("Athena IDE")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)
        
        # Aplicar tema
        self.setStyleSheet(get_main_stylesheet())
        
        # Crear componentes básicos (sin proyecto)
        self._create_components_no_project()
        self._create_menu()
        self._create_status_bar()
        self._setup_layout()
        
        # Verificar estado del modelo
        QTimer.singleShot(2000, self._check_model_status)
        
        # Si se pasó un proyecto, abrirlo
        if project_root:
            self._set_project(project_root)
        else:
            # Mostrar diálogo para seleccionar carpeta
            QTimer.singleShot(100, self._show_open_folder_dialog)
    
    def _create_components_no_project(self):
        """Crea los componentes sin proyecto abierto."""
        c = get_colors()
        
        # Placeholder para el explorador
        self.explorer_placeholder = QWidget()
        self.explorer_placeholder.setMinimumWidth(200)
        self.explorer_placeholder.setMaximumWidth(400)
        self.explorer_placeholder.setStyleSheet(f"""
            background-color: {c['bg_secondary']};
        """)
        
        # Label de "Sin proyecto"
        layout = QVBoxLayout(self.explorer_placeholder)
        no_project_label = QLabel("📁 Sin proyecto abierto\n\nUsa Archivo → Abrir carpeta\no Ctrl+K")
        no_project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_project_label.setStyleSheet(f"color: {c['text_muted']}; padding: 20px;")
        no_project_label.setWordWrap(True)
        layout.addWidget(no_project_label)
        
        # Editor con tabs
        self.editor_tabs = EditorTabWidget()
        
        # Panel de Athena (sin proyecto específico por ahora)
        self.ai_panel = AIPanel(None)
        self.ai_panel.set_editor_tabs(self.editor_tabs)
        self.ai_panel.setMinimumWidth(350)
    
    def _create_menu(self):
        """Crea el menú principal estilo VS Code."""
        c = get_colors()
        menubar = self.menuBar()
        
        # === Menú Archivo ===
        file_menu = menubar.addMenu("&Archivo")
        
        # Nuevo archivo
        action_new = QAction("Nuevo archivo", self)
        action_new.setShortcut(QKeySequence.StandardKey.New)
        action_new.triggered.connect(self._new_file)
        file_menu.addAction(action_new)
        
        file_menu.addSeparator()
        
        # Abrir archivo
        action_open_file = QAction("Abrir archivo...", self)
        action_open_file.setShortcut(QKeySequence.StandardKey.Open)
        action_open_file.triggered.connect(self._open_file_dialog)
        file_menu.addAction(action_open_file)
        
        # Abrir carpeta
        action_open_folder = QAction("Abrir carpeta...", self)
        action_open_folder.setShortcut(QKeySequence("Ctrl+K, Ctrl+O"))
        action_open_folder.triggered.connect(self._open_folder)
        file_menu.addAction(action_open_folder)
        
        # Cerrar carpeta
        action_close_folder = QAction("Cerrar carpeta", self)
        action_close_folder.triggered.connect(self._close_folder)
        file_menu.addAction(action_close_folder)
        
        file_menu.addSeparator()
        
        # Guardar
        action_save = QAction("Guardar", self)
        action_save.setShortcut(QKeySequence.StandardKey.Save)
        action_save.triggered.connect(self._save_current)
        file_menu.addAction(action_save)
        
        # Guardar todo
        action_save_all = QAction("Guardar todo", self)
        action_save_all.setShortcut(QKeySequence("Ctrl+Shift+S"))
        action_save_all.triggered.connect(self._save_all)
        file_menu.addAction(action_save_all)
        
        file_menu.addSeparator()
        
        # Salir
        action_exit = QAction("Salir", self)
        action_exit.setShortcut(QKeySequence("Alt+F4"))
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # === Menú Editar ===
        edit_menu = menubar.addMenu("&Editar")
        
        # Deshacer
        action_undo = QAction("Deshacer", self)
        action_undo.setShortcut(QKeySequence("Ctrl+Z"))
        action_undo.triggered.connect(self._undo)
        edit_menu.addAction(action_undo)
        
        # Rehacer
        action_redo = QAction("Rehacer", self)
        action_redo.setShortcut(QKeySequence("Ctrl+Y"))
        action_redo.triggered.connect(self._redo)
        edit_menu.addAction(action_redo)
        
        edit_menu.addSeparator()
        
        # Cortar
        action_cut = QAction("Cortar", self)
        action_cut.setShortcut(QKeySequence.StandardKey.Cut)
        action_cut.triggered.connect(self._cut)
        edit_menu.addAction(action_cut)
        
        # Copiar
        action_copy = QAction("Copiar", self)
        action_copy.setShortcut(QKeySequence.StandardKey.Copy)
        action_copy.triggered.connect(self._copy)
        edit_menu.addAction(action_copy)
        
        # Pegar
        action_paste = QAction("Pegar", self)
        action_paste.setShortcut(QKeySequence.StandardKey.Paste)
        action_paste.triggered.connect(self._paste)
        edit_menu.addAction(action_paste)
        
        edit_menu.addSeparator()
        
        # Seleccionar todo
        action_select_all = QAction("Seleccionar todo", self)
        action_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        action_select_all.triggered.connect(self._select_all)
        edit_menu.addAction(action_select_all)
        
        # === Menú Ver ===
        view_menu = menubar.addMenu("&Ver")
        
        # Toggle explorador
        action_toggle_explorer = QAction("Explorador", self)
        action_toggle_explorer.setShortcut(QKeySequence("Ctrl+B"))
        action_toggle_explorer.setCheckable(True)
        action_toggle_explorer.setChecked(True)
        action_toggle_explorer.triggered.connect(self._toggle_explorer)
        view_menu.addAction(action_toggle_explorer)
        self.action_toggle_explorer = action_toggle_explorer
        
        # Toggle panel Athena
        action_toggle_ai = QAction("Panel Athena", self)
        action_toggle_ai.setShortcut(QKeySequence("Ctrl+J"))
        action_toggle_ai.setCheckable(True)
        action_toggle_ai.setChecked(True)
        action_toggle_ai.triggered.connect(self._toggle_ai_panel)
        view_menu.addAction(action_toggle_ai)
        self.action_toggle_ai = action_toggle_ai
        
        view_menu.addSeparator()
        
        # Submenú de Temas
        theme_menu = view_menu.addMenu("🎨 Tema de color")
        
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        for theme_name, display_name in get_theme_names():
            action = QAction(display_name, self)
            action.setCheckable(True)
            action.setData(theme_name)
            
            # Marcar tema actual
            from ui.theme import get_current_theme
            if get_current_theme().name == theme_name:
                action.setChecked(True)
            
            action.triggered.connect(lambda checked, t=theme_name: self._change_theme(t))
            theme_group.addAction(action)
            theme_menu.addAction(action)
        
        view_menu.addSeparator()
        
        # Zoom (placeholder)
        action_zoom_in = QAction("Aumentar zoom", self)
        action_zoom_in.setShortcut(QKeySequence("Ctrl++"))
        view_menu.addAction(action_zoom_in)
        
        action_zoom_out = QAction("Reducir zoom", self)
        action_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        view_menu.addAction(action_zoom_out)
        
        # === Menú Athena ===
        athena_menu = menubar.addMenu("🦉 &Athena")
        
        # Enfocar Athena
        action_focus_athena = QAction("Enfocar Panel", self)
        action_focus_athena.setShortcut(QKeySequence("Ctrl+Shift+A"))
        action_focus_athena.triggered.connect(lambda: self.ai_panel.input.setFocus())
        athena_menu.addAction(action_focus_athena)
        
        # Nuevo chat
        action_new_chat = QAction("Nuevo chat", self)
        action_new_chat.setShortcut(QKeySequence("Ctrl+Shift+N"))
        action_new_chat.triggered.connect(self._new_chat)
        athena_menu.addAction(action_new_chat)
        
        athena_menu.addSeparator()
        
        # Cancelar
        action_cancel = QAction("Cancelar operación", self)
        action_cancel.setShortcut(QKeySequence("Escape"))
        action_cancel.triggered.connect(self._cancel_athena)
        athena_menu.addAction(action_cancel)
        
        # === Menú Ayuda ===
        help_menu = menubar.addMenu("&Ayuda")
        
        action_about = QAction("Acerca de Athena IDE", self)
        action_about.triggered.connect(self._show_about)
        help_menu.addAction(action_about)
    
    def _create_status_bar(self):
        """Crea la barra de estado."""
        c = get_colors()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Label para posición del cursor
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.cursor_label.setStyleSheet(f"color: {c['text_muted']}; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.cursor_label)
        
        # Separador
        sep = QLabel("|")
        sep.setStyleSheet(f"color: {c['border']};")
        self.status_bar.addPermanentWidget(sep)
        
        # Label para estado del modelo
        self.model_label = QLabel("🔴 Modelo: Desconectado")
        self.model_label.setStyleSheet(f"color: {c['text_muted']}; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.model_label)
    
    def _setup_layout(self):
        """Configura el layout principal."""
        c = get_colors()
        
        # Splitter principal
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(2)
        
        # Añadir placeholder o explorador
        if self.explorer:
            self.splitter.addWidget(self.explorer)
        else:
            self.splitter.addWidget(self.explorer_placeholder)
        
        self.splitter.addWidget(self.editor_tabs)
        self.splitter.addWidget(self.ai_panel)
        
        # Proporciones iniciales: 1:3:2
        self.splitter.setSizes([250, 900, 450])
        
        self.setCentralWidget(self.splitter)
    
    def _set_project(self, folder: str):
        """Establece el proyecto actual."""
        self.project_root = os.path.abspath(folder)
        self.setWindowTitle(f"Athena IDE - {os.path.basename(self.project_root)}")
        
        # Crear explorador real
        if self.explorer:
            self.explorer.set_root(folder)
        else:
            # Reemplazar placeholder con explorador real
            self.explorer = ProjectExplorer(self.project_root)
            self.explorer.setMinimumWidth(200)
            self.explorer.setMaximumWidth(400)
            
            # Conectar señales
            self.explorer.file_selected.connect(self._open_file)
            self.explorer.file_created.connect(self._open_file)
            
            # Reemplazar en splitter
            self.splitter.replaceWidget(0, self.explorer)
            if self.explorer_placeholder:
                self.explorer_placeholder.deleteLater()
                self.explorer_placeholder = None
        
        
        # Actualizar agente con nuevo root
        self.ai_panel.set_project_root(self.project_root)
        
        # Conectar señal de edición mágica en tiempo real al editor
        self.ai_panel.agent.file_editing_started.connect(self._handle_magic_typing)
        
        # Guardar en configuración
        self.config.last_project = folder
        save_config()
        
    def _handle_magic_typing(self, path: str, content: str):
        """Abre el archivo y lanza el efecto de escritura en tiempo real de Athena."""
        editor = self.editor_tabs.open_file(path)
        if editor:
            # Hacer que se enfoque para que el usuario pueda ver la magia
            editor.setFocus()
            # Animar
            editor.animate_typing(content)
            # Auto-guardar para que el motor siga
            self.editor_tabs.save_file(path)
    
    def _close_folder(self):
        """Cierra el proyecto actual."""
        if not self.project_root:
            return
        
        # Verificar cambios sin guardar
        if self.editor_tabs.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Cambios sin guardar",
                "Hay archivos con cambios sin guardar. ¿Deseas guardarlos antes de cerrar?",
                QMessageBox.StandardButton.SaveAll |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.SaveAll:
                self.editor_tabs.save_all()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Cerrar todas las tabs
        while self.editor_tabs.count() > 0:
            self.editor_tabs.close_tab(0)
        
        # Recrear placeholder
        c = get_colors()
        self.explorer_placeholder = QWidget()
        self.explorer_placeholder.setMinimumWidth(200)
        self.explorer_placeholder.setMaximumWidth(400)
        self.explorer_placeholder.setStyleSheet(f"background-color: {c['bg_secondary']};")
        
        layout = QVBoxLayout(self.explorer_placeholder)
        no_project_label = QLabel("📁 Sin proyecto abierto\n\nUsa Archivo → Abrir carpeta")
        no_project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_project_label.setStyleSheet(f"color: {c['text_muted']}; padding: 20px;")
        no_project_label.setWordWrap(True)
        layout.addWidget(no_project_label)
        
        # Reemplazar explorador
        self.splitter.replaceWidget(0, self.explorer_placeholder)
        if self.explorer:
            self.explorer.deleteLater()
            self.explorer = None
        
        self.project_root = None
        self.setWindowTitle("Athena IDE")
    
    def _show_open_folder_dialog(self):
        """Muestra el diálogo para seleccionar carpeta al inicio."""
        folder = QFileDialog.getExistingDirectory(
            self, "Selecciona la carpeta del proyecto",
            os.path.expanduser("~")
        )
        if folder:
            self._set_project(folder)
    
    def _check_model_status(self):
        """Verifica el estado del modelo LLM."""
        c = get_colors()
        if self.ai_panel.agent and self.ai_panel.agent.is_model_ready():
            self.model_label.setText("🟢 Modelo: Conectado")
            self.model_label.setStyleSheet(f"color: {c['accent_green']}; padding: 0 8px;")
        elif self.ai_panel.llm_client.is_model_ready():
            self.model_label.setText("🟢 Modelo: Conectado")
            self.model_label.setStyleSheet(f"color: {c['accent_green']}; padding: 0 8px;")
        else:
            self.model_label.setText("🔴 Modelo: Desconectado")
            self.model_label.setStyleSheet(f"color: {c['accent_red']}; padding: 0 8px;")
        
        # Verificar cada 10 segundos
        QTimer.singleShot(10000, self._check_model_status)
    
    def _change_theme(self, theme_name: str):
        """Cambia el tema de colores."""
        set_theme(theme_name)
        
        # Guardar en config
        self.config.theme = theme_name
        save_config()
        
        # Aplicar nuevo stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        # Refrescar componentes
        self.ai_panel.refresh_theme()
        
        # Notificar
        self.status_bar.showMessage(f"Tema cambiado: {AVAILABLE_THEMES[theme_name].display_name}", 3000)
    
    # === Acciones de menú ===
    
    def _new_file(self):
        """Crea un nuevo archivo."""
        # Por ahora solo enfoca el editor
        pass
    
    def _open_folder(self):
        """Abre un diálogo para seleccionar carpeta de proyecto."""
        start_dir = self.project_root if self.project_root else os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(
            self, "Abrir carpeta de proyecto", 
            start_dir
        )
        if folder:
            self._set_project(folder)
    
    def _open_file_dialog(self):
        """Abre un diálogo para seleccionar archivo."""
        start_dir = self.project_root if self.project_root else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo",
            start_dir
        )
        if path:
            self._open_file(path)
    
    def _open_file(self, path: str):
        """Abre un archivo en el editor."""
        self.editor_tabs.open_file(path)
    
    def _save_current(self):
        """Guarda el archivo actual."""
        self.editor_tabs.save_current()
    
    def _save_all(self):
        """Guarda todos los archivos."""
        self.editor_tabs.save_all()
    
    def _undo(self):
        """Deshace la última acción."""
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        """Rehace la última acción deshecha."""
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.paste()
    
    def _select_all(self):
        editor = self.editor_tabs.current_editor()
        if editor:
            editor.selectAll()
    
    def _toggle_explorer(self):
        """Muestra/oculta el explorador."""
        widget = self.explorer if self.explorer else self.explorer_placeholder
        if widget:
            visible = not widget.isVisible()
            widget.setVisible(visible)
            self.action_toggle_explorer.setChecked(visible)
    
    def _toggle_ai_panel(self):
        """Muestra/oculta el panel de Athena."""
        visible = not self.ai_panel.isVisible()
        self.ai_panel.setVisible(visible)
        self.action_toggle_ai.setChecked(visible)
    
    def _new_chat(self):
        """Inicia un nuevo chat con Athena."""
        self.ai_panel.clear_chat()
    
    def _cancel_athena(self):
        """Cancela la operación actual de Athena."""
        if self.ai_panel.agent:
            self.ai_panel.agent.cancel_generation()
            self.ai_panel.agent.cancel_plan()
    
    def _show_about(self):
        """Muestra el diálogo Acerca de."""
        QMessageBox.about(
            self,
            "Acerca de Athena IDE",
            "🦉 **Athena IDE**\n\n"
            "Un IDE AI-first, local y autónomo con agente de programación integrado.\n\n"
            "• Modelos locales via koboldcpp\n"
            "• Funciona offline\n"
            "• Control total del usuario\n\n"
            "Versión 1.0.0"
        )
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana."""
        if self.editor_tabs.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Cambios sin guardar",
                "Hay archivos con cambios sin guardar. ¿Deseas guardarlos?",
                QMessageBox.StandardButton.SaveAll |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.SaveAll:
                self.editor_tabs.save_all()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Guardar configuración
        save_config()
        event.accept()
