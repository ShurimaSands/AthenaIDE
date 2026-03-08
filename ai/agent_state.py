"""
Estados del agente Athena.
Define el ciclo de vida del agente durante una operación.
"""
from enum import Enum, auto


class AgentState(Enum):
    """Estados posibles del agente Athena."""
    
    IDLE = "idle"
    """Esperando instrucciones del usuario."""
    
    ANALYZING = "analyzing"
    """Analizando la estructura del proyecto y el contexto."""
    
    PLANNING = "planning"
    """Generando plan de acción basado en la instrucción."""
    
    AWAITING_APPROVAL = "awaiting_approval"
    """Plan generado, esperando confirmación del usuario."""
    
    EXECUTING = "executing"
    """Ejecutando los pasos del plan aprobado."""
    
    REPORTING = "reporting"
    """Reportando resultados de la ejecución."""
    
    ERROR = "error"
    """Error durante alguna fase del proceso."""


# Mensajes de estado para mostrar en la UI
STATE_MESSAGES = {
    AgentState.IDLE: "Athena lista",
    AgentState.ANALYZING: "Analizando proyecto...",
    AgentState.PLANNING: "Generando plan de acción...",
    AgentState.AWAITING_APPROVAL: "Plan listo - Esperando aprobación",
    AgentState.EXECUTING: "Ejecutando plan...",
    AgentState.REPORTING: "Reportando resultados...",
    AgentState.ERROR: "Error",
}


# Colores para cada estado (formato hex para QSS)
STATE_COLORS = {
    AgentState.IDLE: "#6b7280",        # gris
    AgentState.ANALYZING: "#3b82f6",   # azul
    AgentState.PLANNING: "#8b5cf6",    # violeta
    AgentState.AWAITING_APPROVAL: "#f59e0b",  # naranja
    AgentState.EXECUTING: "#10b981",   # verde
    AgentState.REPORTING: "#06b6d4",   # cyan
    AgentState.ERROR: "#ef4444",       # rojo
}
