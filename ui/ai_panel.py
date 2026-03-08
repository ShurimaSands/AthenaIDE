"""
Panel de Athena rediseñado.
Interfaz para interactuar con el agente, mostrar planes y aprobar acciones.
Soporta tanto chat conversacional como modo de planificación de agente.
Usa MarkdownViewer para renderizar respuestas con formato.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor

from ai.agent import AthenaAgent
from ai.agent_state import AgentState, STATE_MESSAGES, STATE_COLORS
from ai.action_plan import ActionPlan, PlanStep
from ai.stream_worker import KoboldStreamClient
from ai.prompts import ATHENA_SYSTEM_PROMPT
from ui.theme import get_colors
from ui.markdown_viewer import MarkdownViewer


class StatusIndicator(QFrame):
    """Indicador visual del estado de Athena."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Punto de estado
        self.dot = QLabel("●")
        self.dot.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.dot)
        
        # Texto de estado
        self.label = QLabel("Athena lista")
        self.label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        self.set_state(AgentState.IDLE)
    
    def set_state(self, state: AgentState):
        """Actualiza el indicador según el estado."""
        color = STATE_COLORS.get(state, "#6b7280")
        message = STATE_MESSAGES.get(state, "Estado desconocido")
        
        c = get_colors()
        self.dot.setStyleSheet(f"color: {color};")
        self.label.setText(message)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_secondary']};
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
    
    def set_custom_message(self, message: str, color: str = None):
        """Establece un mensaje personalizado."""
        c = get_colors()
        self.label.setText(message)
        if color:
            self.dot.setStyleSheet(f"color: {color};")
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['bg_secondary']};
                    border-radius: 8px;
                    border-left: 4px solid {color};
                }}
            """)


class AIPanel(QWidget):
    """
    Panel principal de Athena.
    Soporta:
    - Chat conversacional (sin plan)
    - Modo agente con planificación y aprobación
    - Renderizado Markdown para respuestas formateadas
    """
    
    # Señal para solicitar cambio de tema
    theme_changed = Signal()
    
    def __init__(self, project_root: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("ai_panel")
        self.setMinimumWidth(400)
        
        # Agente (puede ser None si no hay proyecto)
        self.agent = None
        self.project_root = project_root
        if project_root:
            self.agent = AthenaAgent(project_root)
            self._connect_agent_signals()
        
        # Cliente LLM para chat directo
        self.llm_client = KoboldStreamClient()
        self._is_chatting = False
        self._chat_response = ""
        self._current_markdown = ""
        self._is_session_finished = False  # Controla que no se auto-apruebe después de FINISH
        
        # Referencia al editor (se configura desde MainWindow)
        self.editor_tabs = None
        
        # Historial de conversación
        self._conversation_history = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        c = get_colors()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("🦉 Athena")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {c['accent_purple']};")
        layout.addWidget(header)
        
        # Indicador de estado
        self.status = StatusIndicator()
        layout.addWidget(self.status)
        
        # Area de output con Markdown (sin bordes feos)
        self.output = MarkdownViewer()
        self.output.setPlaceholderText(
            "💬 Escribe un mensaje para chatear con Athena\n"
            "📋 O da una instrucción para que genere un plan de trabajo"
        )
        layout.addWidget(self.output, stretch=3)
        
        # Botones de acción (inicialmente ocultos)
        self.action_frame = QFrame()
        action_layout = QHBoxLayout(self.action_frame)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        
        self.btn_approve = QPushButton("✓ Aprobar Plan")
        self.btn_approve.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent_green']};
                color: {c['bg_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8fdb8f;
            }}
        """)
        self.btn_approve.clicked.connect(self._approve_plan)
        action_layout.addWidget(self.btn_approve)
        
        self.btn_cancel = QPushButton("✗ Cancelar")
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent_red']};
                color: {c['bg_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e87a8f;
            }}
        """)
        self.btn_cancel.clicked.connect(self._cancel_plan)
        action_layout.addWidget(self.btn_cancel)
        
        self.action_frame.hide()
        layout.addWidget(self.action_frame)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {c['border']};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Input modernizado
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)
        
        self.input = QTextEdit()
        self.input.setMaximumHeight(120)
        self.input.setFont(QFont("Segoe UI", 12))
        self.input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {c['bg_primary']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                padding: 12px;
            }}
            QTextEdit:focus {{
                border-color: {c['accent_purple']};
                background-color: {c['bg_tertiary']};
            }}
        """)
        self.input.setPlaceholderText("Envía un mensaje o instrucción asombrosa...")
        input_layout.addWidget(self.input)
        layout.addLayout(input_layout)
        
        # Botones de envío
        btn_layout = QHBoxLayout()
        
        self.btn_chat = QPushButton("Enviar")
        self.btn_chat.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent_purple']};
                color: {c['bg_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #b896e7;
            }}
            QPushButton:disabled {{
                background-color: {c['bg_hover']};
                color: {c['text_muted']};
            }}
        """)
        self.btn_chat.clicked.connect(self._send_chat)
        btn_layout.addWidget(self.btn_chat)
        
        self.btn_plan = QPushButton("✨ Generar Plan Mágico")
        self.btn_plan.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['accent_blue']};
                color: {c['bg_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #7aa2f7;
            }}
            QPushButton:disabled {{
                background-color: {c['bg_hover']};
                color: {c['text_muted']};
            }}
        """)
        self.btn_plan.clicked.connect(self._send_plan_request)
        btn_layout.addWidget(self.btn_plan)
        
        layout.addLayout(btn_layout)
        
        # Footer con info minimalista
        footer = QLabel("Ctrl+Enter para enviar chat | Shift+Enter para plan")
        footer.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
    
    def _connect_agent_signals(self):
        """Conecta las señales del agente."""
        if not self.agent:
            return
        
        self.agent.state_changed.connect(self._on_state_changed)
        self.agent.token_received.connect(self._on_token)
        self.agent.plan_ready.connect(self._on_plan_ready)
        self.agent.step_executed.connect(self._on_step_executed)
        self.agent.file_editing_started.connect(self._on_file_editing_started)
        self.agent.execution_complete.connect(self._on_execution_complete)
        self.agent.error_occurred.connect(self._on_error)
        
    @Slot(str, str)
    def _on_file_editing_started(self, path: str, content: str):
        """Callback cuando el agente comienza a editar un archivo físicamente."""
        # Se redirige a MainWindow a través de una señal para abrir la pestaña si no está abierta 
        # Pero podemos emitirla a MainWindow usando parent o simplemente guardando un ref,
        # O MEJOR AÚN, dado que AIPanel no conoce el layout general:
        pass # La reconectaremos en main_window.py donde tenemos acceso a editor_tabs
    
    def set_editor_tabs(self, editor_tabs):
        """Configura la referencia al widget de tabs del editor."""
        self.editor_tabs = editor_tabs
    
    def set_project_root(self, project_root: str):
        """Configura o cambia el proyecto."""
        self.project_root = project_root
        
        # Crear nuevo agente
        if self.agent:
            try:
                self.agent.state_changed.disconnect()
                self.agent.token_received.disconnect()
                self.agent.plan_ready.disconnect()
                self.agent.step_executed.disconnect()
                self.agent.execution_complete.disconnect()
                self.agent.error_occurred.disconnect()
            except:
                pass
        
        self.agent = AthenaAgent(project_root)
        self._connect_agent_signals()
    
    def refresh_theme(self):
        """Refresca los estilos cuando cambia el tema."""
        self.output.refresh_style()
        # Reconstruir UI con nuevos colores sería ideal pero complejo
        # Por ahora solo refrescamos el markdown viewer
    
    # === Chat Mode ===
    
    @Slot()
    def _send_chat(self):
        """Envía un mensaje de chat conversacional."""
        message = self.input.toPlainText().strip()
        if not message:
            return
        
        # Verificar que el modelo esté disponible
        if not self.llm_client.is_model_ready():
            self._current_markdown += "\n\n❌ **Error**: El modelo no está disponible. Verifica que koboldcpp esté ejecutándose.\n"
            self.output.set_markdown(self._current_markdown)
            return
        
        self._is_chatting = True
        self._chat_response = ""
        
        # Añadir mensaje del usuario al markdown
        self._current_markdown += f"\n\n**Tú**: {message}\n\n**Athena**: "
        self.output.set_markdown(self._current_markdown)
        
        c = get_colors()
        # Actualizar estado
        self.status.set_custom_message("Pensando...", c['accent_purple'])
        
        # Deshabilitar inputs
        self._set_inputs_enabled(False)
        
        # Añadir a historial
        self._conversation_history.append({"role": "user", "content": message})
        
        # Preparar mensajes para el LLM
        messages = [
            {"role": "system", "content": ATHENA_SYSTEM_PROMPT + "\n\nPuedes responder preguntas generales y mantener una conversación útil. "
             "Usa formato Markdown en tus respuestas para mejor legibilidad (headers, listas, código, etc). "
             "No necesitas generar un plan para respuestas conversacionales simples."}
        ]
        messages.extend(self._conversation_history[-10:])
        
        # Iniciar streaming
        self.llm_client.stream_completion(
            messages=messages,
            on_token=self._on_chat_token,
            on_complete=self._on_chat_complete,
            on_error=self._on_chat_error
        )
        
        self.input.clear()
    
    def _on_chat_token(self, token: str):
        """Callback para tokens en modo chat - actualiza Markdown en tiempo real."""
        self._chat_response += token
        self._current_markdown += token
        # Actualizar vista con markdown renderizado
        self.output.set_markdown(self._current_markdown)
        # Scroll al final ya es manejado por set_markdown con retardo seguro
        
    
    def _on_chat_complete(self, response: str):
        """Callback cuando termina el chat."""
        self._is_chatting = False
        self._conversation_history.append({"role": "assistant", "content": response})
        self._current_markdown += "\n"
        self.output.set_markdown(self._current_markdown)
        self.status.set_state(AgentState.IDLE)
        self._set_inputs_enabled(True)
    
    def _on_chat_error(self, error: str):
        """Callback para errores en chat."""
        self._is_chatting = False
        self._current_markdown += f"\n\n❌ **Error**: {error}\n"
        self.output.set_markdown(self._current_markdown)
        self.status.set_state(AgentState.ERROR)
        self._set_inputs_enabled(True)
    
    # === Plan Mode ===
    
    @Slot()
    def _send_plan_request(self):
        """Envía una instrucción para generar un plan."""
        instruction = self.input.toPlainText().strip()
        if not instruction:
            return
        
        if not self.agent:
            self._current_markdown += "\n\n⚠️ **Aviso**: Abre un proyecto primero para usar el modo de planificación.\n"
            self.output.set_markdown(self._current_markdown)
            return
        
        # Obtener contexto del editor
        selected_code = None
        current_file = None
        
        if self.editor_tabs:
            selected_code = self.editor_tabs.get_selected_code()
            current_file = self.editor_tabs.current_file_path()
        
        # Añadir instrucción al markdown
        self._current_markdown += f"\n\n---\n\n**📋 Instrucción**: {instruction}\n\n"
        self.output.set_markdown(self._current_markdown)
        
        # Deshabilitar input mientras procesa
        self._set_inputs_enabled(False)
        
        # Reset del flag de sesión terminada para una nueva tarea
        self._is_session_finished = False
        
        # Enviar request al agente
        self.agent.plan_request(
            instruction=instruction,
            selected_code=selected_code,
            current_file=current_file
        )
        
        self.input.clear()
    
    @Slot()
    def _approve_plan(self):
        """Aprueba el plan actual."""
        if not self.agent:
            return
        self.action_frame.hide()
        self._current_markdown += "\n\n---\n\n**Ejecutando plan...**\n"
        self.output.set_markdown(self._current_markdown)
        self.agent.approve_plan()
    
    @Slot()
    def _cancel_plan(self):
        """Cancela el plan actual."""
        if not self.agent:
            return
        self.action_frame.hide()
        self._current_markdown += "\n\n---\n\n*Plan cancelado por el usuario.*\n"
        self.output.set_markdown(self._current_markdown)
        self.agent.cancel_plan()
        self._set_inputs_enabled(True)
    
    @Slot(AgentState)
    def _on_state_changed(self, state: AgentState):
        """Callback cuando cambia el estado del agente."""
        self.status.set_state(state)
        
        if state == AgentState.IDLE:
            self._set_inputs_enabled(True)
    
    @Slot(str)
    def _on_token(self, token: str):
        """Callback para cada token recibido (streaming del agente)."""
        self._current_markdown += token
        self.output.set_markdown(self._current_markdown)
    
    @Slot(ActionPlan)
    def _on_plan_ready(self, plan: ActionPlan):
        """Callback cuando el plan está listo."""
        # Si la sesión ya terminó, NO auto-aprobar más planes
        if self._is_session_finished:
            return
        
        # Si hay pasos estructurados, mostrar el plan formateado
        if plan.steps:
            self._current_markdown += "\n\n" + plan.to_markdown()
            self.output.set_markdown(self._current_markdown)
        
        # Modo Autónomo: Auto-aprobar *todo* plan generado para que el flujo sea continuo
        self._current_markdown += "\n\n*Aprobando automáticamente y ejecutando...*\n"
        self.output.set_markdown(self._current_markdown)
        
        # Usar un timer muy corto para que la UI se renderice antes de trabarse ejecutando
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._approve_plan)
    
    @Slot(PlanStep, str)
    def _on_step_executed(self, step: PlanStep, message: str):
        """Callback cuando se ejecuta un paso."""
        icon = "✅" if step.status.value == "completed" else "❌"
        self._current_markdown += f"\n{icon} **Paso {step.id}**: {message}"
        self.output.set_markdown(self._current_markdown)
    
    @Slot(bool, str)
    def _on_execution_complete(self, success: bool, report: str):
        """Callback cuando termina la ejecución."""
        # Marcar sesión como finalizada para detener completamente el auto-loop
        self._is_session_finished = True
        
        self._current_markdown += f"\n\n{report}"
        self._current_markdown += "\n\n---\n\n✅ **Sesión finalizada.** Puedes enviar una nueva instrucción.\n"
        self.output.set_markdown(self._current_markdown)
        self._set_inputs_enabled(True)
        self.status.set_state(AgentState.IDLE)
    
    @Slot(str)
    def _on_error(self, error: str):
        """Callback para errores."""
        self._current_markdown += f"\n\n❌ **Error**: {error}\n"
        self.output.set_markdown(self._current_markdown)
        self._set_inputs_enabled(True)
    
    def _set_inputs_enabled(self, enabled: bool):
        """Habilita o deshabilita los controles de input."""
        self.btn_chat.setEnabled(enabled)
        self.btn_plan.setEnabled(enabled)
        self.input.setEnabled(enabled)
    
    def clear_chat(self):
        """Limpia el historial de chat y la memoria del agente."""
        self._current_markdown = ""
        self._conversation_history = []
        self._is_session_finished = False
        if self.agent:
            self.agent._accumulated_context = ""
        self.output._think_states = {}  # Reset think toggle states
        self.output.clear()
