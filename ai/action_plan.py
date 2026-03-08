"""
Modelos de datos para planes de acción de Athena.
Define la estructura de los planes que el agente genera y ejecuta.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ActionType(Enum):
    """Tipos de acciones que Athena puede ejecutar."""
    
    READ_FILE = "read_file"
    """Leer contenido de un archivo."""
    
    CREATE_FILE = "create_file"
    """Crear un nuevo archivo con contenido."""
    
    MODIFY_FILE = "modify_file"
    """Modificar contenido de un archivo existente."""
    
    PATCH_FILE = "patch_file"
    """Aplicar un parche (buscar y reemplazar) en un archivo."""
    
    DELETE_FILE = "delete_file"
    """Eliminar un archivo (requiere confirmación extra)."""
    
    CREATE_DIR = "create_dir"
    """Crear un nuevo directorio."""
    
    FINISH = "finish"
    """Finalizar la tarea de forma exitosa y detener el ciclo."""
    
    RENAME = "rename"
    """Renombrar archivo o directorio."""


class StepStatus(Enum):
    """Estado de ejecución de un paso del plan."""
    
    PENDING = "pending"
    """Pendiente de ejecución."""
    
    RUNNING = "running"
    """En ejecución actualmente."""
    
    COMPLETED = "completed"
    """Ejecutado exitosamente."""
    
    FAILED = "failed"
    """Error durante la ejecución."""
    
    SKIPPED = "skipped"
    """Saltado (por cancelación o dependencia fallida)."""


@dataclass
class PlanStep:
    """Un paso individual dentro de un plan de acción."""
    
    id: int
    """Identificador único del paso dentro del plan."""
    
    action: ActionType
    """Tipo de acción a ejecutar."""
    
    target: str                  # path del archivo o directorio
    description: str             # Qué se va a hacer (para UI)
    content: Optional[str] = None # Contenido para CREATE/MODIFY (o contenido de reemplazo para compatibilidad de animación visual)
    search_text: Optional[str] = None   # Texto a buscar para PATCH_FILE
    replace_text: Optional[str] = None  # Texto a insertar para PATCH_FILE
    new_name: Optional[str] = None      # Nuevo nombre para RENAME
    status: StepStatus = StepStatus.PENDING
    """Estado actual de ejecución."""
    
    error_message: Optional[str] = None
    """Mensaje de error si status == FAILED."""
    
    def to_markdown(self) -> str:
        """Convierte el paso a formato Markdown para mostrar."""
        status_icons = {
            StepStatus.PENDING: "⏳",
            StepStatus.RUNNING: "🔄",
            StepStatus.COMPLETED: "✅",
            StepStatus.FAILED: "❌",
            StepStatus.SKIPPED: "⏭️",
        }
        icon = status_icons.get(self.status, "•")
        action_name = self.action.value.replace("_", " ").title()
        
        md = f"{icon} **Paso {self.id}**: {action_name}\n"
        md += f"   - **Archivo**: `{self.target}`\n"
        md += f"   - **Descripción**: {self.description}\n"
        
        if self.error_message:
            md += f"   - **Error**: {self.error_message}\n"
        
        return md


@dataclass
class ActionPlan:
    """Plan de acción completo generado por Athena."""
    
    summary: str
    """Resumen del plan en lenguaje natural."""
    
    steps: List[PlanStep] = field(default_factory=list)
    """Lista ordenada de pasos a ejecutar."""
    
    approved: bool = False
    """Si el usuario ha aprobado el plan."""
    
    raw_response: str = ""
    """Respuesta original del LLM (para debugging)."""
    
    def add_step(self, action: ActionType, target: str, description: str,
                 content: Optional[str] = None, new_name: Optional[str] = None,
                 search_text: Optional[str] = None, replace_text: Optional[str] = None) -> PlanStep:
        """Añade un nuevo paso al plan."""
        step = PlanStep(
            id=len(self.steps) + 1,
            action=action,
            target=target,
            description=description,
            content=content,
            new_name=new_name,
            search_text=search_text,
            replace_text=replace_text
        )
        self.steps.append(step)
        return step
    
    def get_pending_steps(self) -> List[PlanStep]:
        """Retorna los pasos pendientes de ejecución."""
        return [s for s in self.steps if s.status == StepStatus.PENDING]
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Retorna el próximo paso a ejecutar."""
        pending = self.get_pending_steps()
        return pending[0] if pending else None
    
    def mark_step_completed(self, step_id: int) -> None:
        """Marca un paso como completado."""
        for step in self.steps:
            if step.id == step_id:
                step.status = StepStatus.COMPLETED
                break
    
    def mark_step_failed(self, step_id: int, error: str) -> None:
        """Marca un paso como fallido."""
        for step in self.steps:
            if step.id == step_id:
                step.status = StepStatus.FAILED
                step.error_message = error
                break
    
    def is_complete(self) -> bool:
        """Verifica si todos los pasos fueron ejecutados."""
        return all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED, StepStatus.FAILED) 
                   for s in self.steps)
    
    def has_failures(self) -> bool:
        """Verifica si hubo pasos fallidos."""
        return any(s.status == StepStatus.FAILED for s in self.steps)
    
    def to_markdown(self) -> str:
        """Convierte el plan completo a Markdown."""
        md = f"## 📋 Plan de Acción\n\n"
        md += f"{self.summary}\n\n"
        md += f"### Pasos ({len(self.steps)} total)\n\n"
        
        for step in self.steps:
            md += step.to_markdown() + "\n"
        
        if not self.approved:
            md += "\n---\n"
            md += "⚠️ **Este plan requiere tu aprobación antes de ejecutarse.**\n"
        
        return md
    
    def execution_report(self) -> str:
        """Genera un reporte de la ejecución."""
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        total = len(self.steps)
        
        md = f"## 📊 Reporte de Ejecución\n\n"
        md += f"- **Completados**: {completed}/{total}\n"
        md += f"- **Fallidos**: {failed}/{total}\n\n"
        
        if failed > 0:
            md += "### Errores\n\n"
            for step in self.steps:
                if step.status == StepStatus.FAILED:
                    md += f"- Paso {step.id}: {step.error_message}\n"
        
        return md
