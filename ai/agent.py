"""
Agente principal Athena.
Coordina el flujo completo: análisis → planificación → aprobación → ejecución → reporte.
"""
import os
import json
import re
from typing import Optional, Callable, List
from PySide6.QtCore import QObject, Signal

from ai.agent_state import AgentState, STATE_MESSAGES
from ai.action_plan import ActionPlan, PlanStep, ActionType, StepStatus
from ai.action_engine import ActionEngine
from ai.stream_worker import KoboldStreamClient
from ai.prompts import ATHENA_SYSTEM_PROMPT, build_planning_prompt, PLAN_FORMAT_INSTRUCTION, build_replanning_prompt
from ai.context_builder import ContextBuilder
from project.project_manager import ProjectManager


class AthenaAgent(QObject):
    """
    Agente de programación Athena.
    
    Flujo de trabajo:
    1. Recibe instrucción del usuario
    2. Analiza el proyecto y contexto
    3. Genera un plan de acción
    4. Espera aprobación del usuario
    5. Ejecuta el plan paso a paso
    6. Reporta resultados
    """
    
    # Señales para comunicar con la UI
    state_changed = Signal(AgentState)
    token_received = Signal(str)
    plan_ready = Signal(ActionPlan)
    step_executed = Signal(PlanStep, str)  # paso, mensaje
    file_editing_started = Signal(str, str) # filepath, new_content
    execution_complete = Signal(bool, str)  # éxito, reporte
    error_occurred = Signal(str)
    
    def __init__(self, project_root: str, parent=None):
        super().__init__(parent)
        
        self.project = ProjectManager(project_root)
        self.context_builder = ContextBuilder(self.project)
        self.action_engine = ActionEngine(self.project)
        self.llm_client = KoboldStreamClient()
        
        self._state = AgentState.IDLE
        self._current_plan: Optional[ActionPlan] = None
        self._response_buffer = ""
        self._conversation_history: List[dict] = []
        self._accumulated_context: str = ""  # Memoria persistente de archivos leídos en la sesión
    
    @property
    def state(self) -> AgentState:
        return self._state
    
    @state.setter
    def state(self, new_state: AgentState):
        if new_state != self._state:
            self._state = new_state
            self.state_changed.emit(new_state)
    
    @property
    def current_plan(self) -> Optional[ActionPlan]:
        return self._current_plan
    
    def get_status_message(self) -> str:
        """Retorna el mensaje de estado actual."""
        return STATE_MESSAGES.get(self.state, "Estado desconocido")
    
    def is_model_ready(self) -> bool:
        """Verifica si el modelo LLM está disponible."""
        return self.llm_client.is_model_ready()
    
    def plan_request(self, 
                     instruction: str,
                     selected_code: Optional[str] = None,
                     current_file: Optional[str] = None):
        """
        Inicia una nueva solicitud de planificación.
        
        Args:
            instruction: Instrucción del usuario
            selected_code: Código seleccionado en el editor
            current_file: Ruta del archivo actualmente abierto
        """
        if self.state not in (AgentState.IDLE, AgentState.AWAITING_APPROVAL, AgentState.ERROR):
            self.error_occurred.emit("Athena está ocupada. Espera a que termine.")
            return
        
        # Cambiar a estado de análisis
        self.state = AgentState.ANALYZING
        self._response_buffer = ""
        self._current_plan = None
        
        # Limpiar memoria acumulada para una nueva solicitud completamente fresca
        self._accumulated_context = ""
        
        # Construir contexto base
        context = self.context_builder.build_context(
            instruction=instruction,
            selected_code=selected_code,
            current_file=current_file
        )
        
        # Construir prompt
        prompt = build_planning_prompt(
            project_tree=context["project_tree"],
            instruction=instruction,
            selected_code=selected_code,
            file_contents=context.get("files")
        )
        
        # Preparar mensajes
        if not hasattr(self, '_conversation_history'):
            self._conversation_history = []
            
        self._conversation_history = [
            {"role": "system", "content": ATHENA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        self._start_planning_cycle()

    def _start_planning_cycle(self):
        """Inicia una nueva fase de planificación con el LLM enviando el historial de conversación actual."""
        # Cambiar a estado de planificación
        self.state = AgentState.PLANNING
        self._response_buffer = ""
        self._current_plan = None
        
        # Iniciar streaming
        self.llm_client.stream_completion(
            messages=self._conversation_history,
            on_token=self._on_token,
            on_complete=self._on_planning_complete,
            on_error=self._on_error
        )
    
    def _on_token(self, token: str):
        """Callback para cada token recibido."""
        self._response_buffer += token
        self.token_received.emit(token)
    
    def _on_planning_complete(self, full_response: str):
        """Callback cuando termina la generación del plan."""
        # Intentar parsear el plan
        plan = self._parse_plan(full_response)
        
        if plan:
            self._current_plan = plan
            self.state = AgentState.AWAITING_APPROVAL
            self.plan_ready.emit(plan)
        else:
            # Si no se pudo parsear un plan estructurado, NO crear un plan ficticio
            # que causaría un loop infinito de replanning.
            # En su lugar, mostrar la respuesta como texto final y detenerse.
            self.token_received.emit("\n\n⚠️ *No se detectó un plan estructurado. Sesión finalizada.*\n")
            self.state = AgentState.IDLE
            self.execution_complete.emit(True, "Athena terminó de responder (sin plan estructurado).")
    
    def _on_error(self, error: str):
        """Callback para errores."""
        self.state = AgentState.ERROR
        self.error_occurred.emit(error)
    
    def _parse_plan(self, response: str) -> Optional[ActionPlan]:
        """
        Intenta extraer un plan estructurado de la respuesta del LLM.
        Busca un bloque JSON con el formato especificado.
        """
        # Buscar bloque JSON en la respuesta
        json_pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
        matches = re.findall(json_pattern, response)
        
        if not matches:
            # Intentar buscar JSON sin bloques de código
            json_pattern = r'\{[\s\S]*"steps"[\s\S]*\}'
            matches = re.findall(json_pattern, response)
        
        for match in matches:
            try:
                data = json.loads(match)
                
                if "steps" in data:
                    plan = ActionPlan(
                        summary=data.get("summary", "Plan de acción"),
                        raw_response=response
                    )
                    
                    for i, step_data in enumerate(data["steps"], 1):
                        action_str = step_data.get("action", "").lower()
                        
                        # Mapear string a ActionType
                        action_map = {
                            "create_file": ActionType.CREATE_FILE,
                            "modify_file": ActionType.MODIFY_FILE,
                            "delete_file": ActionType.DELETE_FILE,
                            "create_dir": ActionType.CREATE_DIR,
                            "read_file": ActionType.READ_FILE,
                            "rename": ActionType.RENAME,
                            "patch_file": ActionType.PATCH_FILE,
                            "finish": ActionType.FINISH,
                        }
                        
                        action = action_map.get(action_str)
                        if not action:
                            continue
                        
                        step = PlanStep(
                            id=i,
                            action=action,
                            target=step_data.get("target", ""),
                            description=step_data.get("description", ""),
                            content=step_data.get("content"),
                            new_name=step_data.get("new_name"),
                            search_text=step_data.get("search_text"),
                            replace_text=step_data.get("replace_text")
                        )
                        plan.steps.append(step)
                    
                    if plan.steps:
                        return plan
            
            except json.JSONDecodeError:
                continue
        
        return None
    
    def approve_plan(self):
        """Aprueba el plan actual y comienza la ejecución."""
        if self.state != AgentState.AWAITING_APPROVAL:
            self.error_occurred.emit("No hay plan pendiente de aprobación")
            return
        
        if not self._current_plan:
            self.error_occurred.emit("No hay plan cargado")
            return
        
        self._current_plan.approved = True
        self.state = AgentState.EXECUTING
        
        # Guardar respuesta del LLM en contexto
        if not hasattr(self, '_conversation_history'):
            self._conversation_history = []
        self._conversation_history.append({"role": "assistant", "content": self._current_plan.raw_response})
        
        # === PASO 0: Crear athena_plan.md con todos los pasos como [ ] ===
        completed_step_ids = set()
        has_real_steps = any(s.action != ActionType.FINISH for s in self._current_plan.steps)
        
        if has_real_steps:
            self._write_plan_file(self._current_plan, completed_step_ids)
        
        # === Ejecutar plan paso a paso ===
        success = True
        is_finished = False
        new_context = ""
        
        for step in self._current_plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            step.status = StepStatus.RUNNING
            result = self.action_engine.execute_step(step)
            
            if step.action == ActionType.FINISH:
                is_finished = True
                
            if step.action in (ActionType.CREATE_FILE, ActionType.MODIFY_FILE, ActionType.PATCH_FILE):
                full_path = os.path.join(self.project.root, step.target)
                
                if step.action in (ActionType.CREATE_FILE, ActionType.MODIFY_FILE):
                    self.file_editing_started.emit(full_path, step.content or "")
                elif step.action == ActionType.PATCH_FILE and result.success and result.data:
                    self.file_editing_started.emit(full_path, result.data)
                
            if step.action == ActionType.READ_FILE and result.success and result.data:
                content = result.data
                if len(content) > 16000:
                    content = content[:16000] + f"\n...[Contenido truncado. Original: {len(result.data)} chars]"
                
                file_context = f"\n<archivo path='{step.target}'>\n{content}\n</archivo>\n"
                if file_context not in self._accumulated_context:
                    self._accumulated_context += file_context
                
                new_context += f"\nContenido de {step.target}:\n```\n{content}\n```\n"
            
            if result.success:
                self._current_plan.mark_step_completed(step.id)
                self.step_executed.emit(step, result.message)
                
                # === MARCAR PASO COMPLETADO EN athena_plan.md ===
                if has_real_steps and step.action != ActionType.FINISH:
                    completed_step_ids.add(step.id)
                    self._write_plan_file(self._current_plan, completed_step_ids)
            else:
                self._current_plan.mark_step_failed(step.id, result.message)
                self.step_executed.emit(step, f"Error: {result.message}")
                
                # Marcar como fallido en el plan también
                if has_real_steps:
                    self._write_plan_file(self._current_plan, completed_step_ids, failed_id=step.id)
                
                success = False
                break
        
        # Generar reporte
        self.state = AgentState.REPORTING
        report = self._current_plan.execution_report()
        
        if is_finished or not success:
            if is_finished:
                self._accumulated_context = ""
                self._conversation_history = []
            
            self.execution_complete.emit(success, report)
            self.state = AgentState.IDLE
        else:
            # Replan
            full_context_to_send = new_context
            if self._accumulated_context:
                full_context_to_send += f"\n\n--- MEMORIA DE ARCHIVOS PREVIAMENTE LEÍDOS ---\n{self._accumulated_context}"
                
            replan_prompt = build_replanning_prompt(report, full_context_to_send)
            self._conversation_history.append({"role": "user", "content": replan_prompt})
            
            if len(self._conversation_history) > 21:
                self._conversation_history = [self._conversation_history[0]] + self._conversation_history[-20:]
            
            self.token_received.emit(f"\n\n{report}\n\n*Continuando automáticamente con la siguiente fase del plan...*\n\n---\n\n**🔄 Analizando siguiente paso...**\n\n")
            self._start_planning_cycle()
    
    def _generate_plan_md(self, plan: ActionPlan, completed_ids: set, failed_id: int = None) -> str:
        """Genera el contenido markdown del archivo de plan con checkboxes."""
        lines = []
        lines.append(f"# 📋 Plan de Athena")
        lines.append(f"")
        lines.append(f"> {plan.summary}")
        lines.append(f"")
        lines.append(f"## Pasos")
        lines.append(f"")
        
        for step in plan.steps:
            if step.action == ActionType.FINISH:
                continue  # No mostrar el paso finish en el plan visual
            
            if step.id == failed_id:
                checkbox = "[❌]"
            elif step.id in completed_ids:
                checkbox = "[x]"
            else:
                checkbox = "[ ]"
            
            action_name = step.action.value.replace("_", " ").title()
            lines.append(f"- {checkbox} **Paso {step.id}**: {step.description}")
            lines.append(f"  - Acción: `{action_name}` → `{step.target}`")
            lines.append(f"")
        
        return "\n".join(lines)
    
    def _write_plan_file(self, plan: ActionPlan, completed_ids: set, failed_id: int = None):
        """Escribe/actualiza athena_plan.md y emite señal para animación visual."""
        content = self._generate_plan_md(plan, completed_ids, failed_id)
        plan_path = "athena_plan.md"
        
        # Escribir al disco
        self.project.write(plan_path, content)
        
        # Emitir señal para que el editor lo muestre en tiempo real
        full_path = os.path.join(self.project.root, plan_path)
        self.file_editing_started.emit(full_path, content)
    
    def cancel_plan(self):
        """Cancela el plan actual sin ejecutar."""
        if self._current_plan:
            for step in self._current_plan.steps:
                if step.status == StepStatus.PENDING:
                    step.status = StepStatus.SKIPPED
        
        self._current_plan = None
        self.state = AgentState.IDLE
    
    def cancel_generation(self):
        """Cancela la generación actual del LLM."""
        self.llm_client.cancel_current()
        self.state = AgentState.IDLE
    
    def get_project_tree(self) -> str:
        """Retorna el árbol de archivos del proyecto."""
        return self.context_builder.get_project_tree()
    
    def read_file(self, path: str) -> Optional[str]:
        """Lee un archivo del proyecto."""
        return self.context_builder.read_file_safe(path)
