"""
Worker para streaming asíncrono con koboldcpp.
Ejecuta las llamadas al LLM en un hilo separado para no bloquear la UI.
"""
import json
import requests
from PySide6.QtCore import QThread, Signal


class StreamWorker(QThread):
    """
    Worker que ejecuta streaming del LLM en un hilo separado.
    Emite señales para comunicar progreso a la UI.
    """
    
    # Señales
    token_received = Signal(str)      # Cada token recibido
    response_complete = Signal(str)   # Respuesta completa
    error_occurred = Signal(str)      # Error durante streaming
    
    def __init__(self, url: str, payload: dict, parent=None):
        super().__init__(parent)
        self.url = url
        self.payload = payload
        self._cancelled = False
        self._response = ""
    
    def cancel(self):
        """Solicita cancelación del streaming."""
        self._cancelled = True
    
    def run(self):
        """Ejecuta el streaming en el hilo."""
        try:
            response = requests.post(
                self.url,
                json=self.payload,
                stream=True,
                timeout=120
            )
            
            if response.status_code != 200:
                self.error_occurred.emit(f"Error HTTP {response.status_code}")
                return
            
            for line in response.iter_lines():
                if self._cancelled:
                    break
                
                if not line:
                    continue
                
                if line.startswith(b"data: "):
                    data = line.replace(b"data: ", b"").decode("utf-8")
                    
                    if data == "[DONE]":
                        break
                    
                    try:
                        parsed = json.loads(data)
                        token = parsed.get("choices", [{}])[0].get("delta", {}).get("content")
                        if token:
                            self._response += token
                            self.token_received.emit(token)
                    except json.JSONDecodeError:
                        continue
            
            if not self._cancelled:
                self.response_complete.emit(self._response)
        
        except requests.exceptions.Timeout:
            self.error_occurred.emit("Timeout: El modelo no respondió a tiempo")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Error de conexión: ¿Está koboldcpp ejecutándose?")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


class KoboldStreamClient:
    """
    Cliente para streaming con koboldcpp.
    Maneja la creación de workers y la cola de requests.
    """
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/v1/chat/completions"
        self.current_worker: StreamWorker = None
    
    def is_model_ready(self) -> bool:
        """Verifica si el modelo está listo."""
        try:
            r = requests.get(f"{self.base_url}/v1/models", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    def stream_completion(self, 
                          messages: list,
                          on_token=None,
                          on_complete=None,
                          on_error=None,
                          temperature: float = 0.3,
                          max_tokens: int = 4096) -> StreamWorker:
        """
        Inicia streaming de una completion.
        
        Args:
            messages: Lista de mensajes [{role, content}, ...]
            on_token: Callback para cada token
            on_complete: Callback cuando termina
            on_error: Callback para errores
            temperature: Temperatura del modelo
            max_tokens: Máximo de tokens a generar
        
        Returns:
            StreamWorker para control adicional
        """
        # Cancelar worker previo si existe
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()
        
        payload = {
            "model": "koboldcpp",
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        worker = StreamWorker(self.endpoint, payload)
        
        if on_token:
            worker.token_received.connect(on_token)
        if on_complete:
            worker.response_complete.connect(on_complete)
        if on_error:
            worker.error_occurred.connect(on_error)
        
        self.current_worker = worker
        worker.start()
        
        return worker
    
    def cancel_current(self):
        """Cancela el streaming actual."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
