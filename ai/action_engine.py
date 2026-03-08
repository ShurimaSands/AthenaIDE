"""
Motor de ejecución de acciones de Athena.
Ejecuta los pasos de un plan de forma segura y controlada.
"""
import os
import shutil
from datetime import datetime
from typing import Optional, Tuple
from dataclasses import dataclass

from ai.action_plan import ActionPlan, PlanStep, ActionType, StepStatus
from project.project_manager import ProjectManager


@dataclass
class ActionResult:
    """Resultado de ejecutar una acción."""
    success: bool
    message: str
    data: Optional[str] = None  # Contenido leído, etc.


class ActionEngine:
    """
    Motor de ejecución de acciones sobre el proyecto.
    Todas las operaciones pasan por aquí para garantizar seguridad y logging.
    """
    
    def __init__(self, project: ProjectManager):
        self.project = project
        self.backup_dir = os.path.join(project.root, ".athena_backups")
        self.log: list[str] = []
    
    def _log(self, message: str) -> None:
        """Añade un mensaje al log interno."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.log.append(entry)
        print(entry)  # También a consola para debugging
    
    def _backup_file(self, path: str) -> Optional[str]:
        """Crea backup de un archivo antes de modificarlo."""
        full_path = os.path.join(self.project.root, path)
        if not os.path.exists(full_path):
            return None
        
        # Crear directorio de backups si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Nombre de backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{os.path.basename(path)}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        shutil.copy2(full_path, backup_path)
        self._log(f"Backup creado: {backup_path}")
        return backup_path
    
    def validate_step(self, step: PlanStep) -> Tuple[bool, str]:
        """
        Valida que un paso puede ejecutarse de forma segura.
        Retorna (es_valido, mensaje_error).
        """
        full_path = os.path.join(self.project.root, step.target)
        
        if step.action == ActionType.CREATE_FILE:
            if os.path.exists(full_path):
                return False, f"El archivo ya existe: {step.target}"
            parent = os.path.dirname(full_path)
            if parent and not os.path.exists(parent):
                return False, f"El directorio padre no existe: {parent}"
        
        elif step.action == ActionType.MODIFY_FILE:
            if not os.path.exists(full_path):
                return False, f"El archivo no existe: {step.target}"
            if not os.path.isfile(full_path):
                return False, f"No es un archivo: {step.target}"
        
        elif step.action == ActionType.PATCH_FILE:
            if not os.path.exists(full_path):
                return False, f"El archivo no existe: {step.target}"
            if not step.search_text or step.replace_text is None:
                return False, "Falta search_text o replace_text para el parche"
        
        elif step.action == ActionType.READ_FILE:
            if not os.path.exists(full_path):
                return False, f"El archivo no existe: {step.target}"
            if not os.path.isfile(full_path):
                return False, f"No es un archivo: {step.target}"
        
        elif step.action == ActionType.CREATE_DIR:
            if os.path.exists(full_path):
                return False, f"El directorio ya existe: {step.target}"
        
        elif step.action == ActionType.RENAME:
            if not os.path.exists(full_path):
                return False, f"El archivo/directorio no existe: {step.target}"
        elif step.action == ActionType.FINISH:
            pass # Siempre es valido terminar
        
        return True, ""
    
    def execute_step(self, step: PlanStep) -> ActionResult:
        """
        Ejecuta un paso individual del plan.
        Crea backups automáticamente para operaciones destructivas.
        """
        self._log(f"Ejecutando: {step.action.value} -> {step.target}")
        
        # Validar primero
        valid, error = self.validate_step(step)
        if not valid:
            self._log(f"Validación fallida: {error}")
            return ActionResult(success=False, message=error)
        
        full_path = os.path.join(self.project.root, step.target)
        
        try:
            if step.action == ActionType.READ_FILE:
                content = self.project.read(step.target)
                self._log(f"Leído: {step.target} ({len(content)} chars)")
                return ActionResult(success=True, message="Archivo leído", data=content)
            
            elif step.action == ActionType.MODIFY_FILE:
                # Backup antes de modificar (Mantenemos backup por seguridad)
                self._backup_file(step.target)
                
                # La escritura REAL se difiere a la interfaz (MainWindow._handle_magic_typing)
                # para que el usuario pueda ver el efecto de escritura en vivo.
                # ProjectManager ya no hace write directamente aquí.
                
                self._log(f"Modificación visual iniciada: {step.target}")
                return ActionResult(success=True, message=f"Archivo modificado (visual): {step.target}")
            
            elif step.action == ActionType.CREATE_FILE:
                # Escribimos el archivo vacío primero para que el editor de la interfaz no se estrelle al intentar abrirlo
                self.project.write(step.target, "")
                
                # La escritura REAL y animación se difiere a la interfaz
                self._log(f"Creación visual iniciada: {step.target}")
                return ActionResult(success=True, message=f"Archivo creado (visual): {step.target}")
            
            elif step.action == ActionType.PATCH_FILE:
                # Backup por seguridad antes de mofificar
                self._backup_file(step.target)
                
                # Aplicamos el parche en memoria
                content = self.project.read(step.target)
                
                if step.search_text not in content:
                    return ActionResult(success=False, message=f"No se encontró el texto a buscar en {step.target}")
                    
                # Reemplazar la primera ocurrencia o todas. Es mejor reemplazar todas las exactas.
                new_content = content.replace(step.search_text, step.replace_text)
                
                # Devolver el nuevo contenido para que la UI lo escriba mágicamente
                self._log(f"Parche visual listo: {step.target}")
                return ActionResult(success=True, message=f"Archivo parcheado (visual): {step.target}", data=new_content)
            
            elif step.action == ActionType.DELETE_FILE:
                # Backup antes de eliminar
                self._backup_file(step.target)
                os.remove(full_path)
                self._log(f"Eliminado: {step.target}")
                return ActionResult(success=True, message=f"Archivo eliminado: {step.target}")
            
            elif step.action == ActionType.CREATE_DIR:
                os.makedirs(full_path, exist_ok=True)
                self._log(f"Directorio creado: {step.target}")
                return ActionResult(success=True, message=f"Directorio creado: {step.target}")
            
            elif step.action == ActionType.RENAME:
                new_path = os.path.join(os.path.dirname(full_path), step.new_name)
                os.rename(full_path, new_path)
                self._log(f"Renombrado: {step.target} -> {step.new_name}")
                return ActionResult(success=True, message=f"Renombrado a: {step.new_name}")
            
            elif step.action == ActionType.FINISH:
                self._log("Tarea finalizada por Athena")
                return ActionResult(success=True, message="Tarea declarada como completada.")
            
            else:
                return ActionResult(success=False, message=f"Acción no soportada: {step.action}")
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._log(error_msg)
            return ActionResult(success=False, message=error_msg)
    
    def execute_plan(self, plan: ActionPlan, on_step_complete=None) -> bool:
        """
        Ejecuta todos los pasos de un plan aprobado.
        
        Args:
            plan: El plan a ejecutar (debe estar aprobado)
            on_step_complete: Callback opcional llamado después de cada paso
        
        Returns:
            True si todos los pasos se ejecutaron exitosamente
        """
        if not plan.approved:
            self._log("ERROR: Plan no aprobado")
            return False
        
        self._log(f"Iniciando ejecución de plan con {len(plan.steps)} pasos")
        
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            step.status = StepStatus.RUNNING
            result = self.execute_step(step)
            
            if result.success:
                plan.mark_step_completed(step.id)
            else:
                plan.mark_step_failed(step.id, result.message)
                self._log(f"Plan detenido en paso {step.id} debido a error")
                return False
            
            if on_step_complete:
                on_step_complete(step, result)
        
        self._log("Plan ejecutado completamente")
        return True
    
    def get_log(self) -> str:
        """Retorna el log como string."""
        return "\n".join(self.log)
