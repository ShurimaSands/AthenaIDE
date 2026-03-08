"""
Lanzador de koboldcpp.
Inicia el servidor del modelo local si no está corriendo.
"""
import subprocess
import time
import requests
import os

PORT = 5001
HOST = "0.0.0.0"

# Rutas por defecto (pueden ser configuradas)
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KOBOLD = os.path.join(BASE, "koboldcpp.exe")
MODEL = os.path.join(BASE, "qwen2.5-coder-7b-instruct-q8_0.gguf")


def get_launch_args(kobold_path: str = None, model_path: str = None) -> list:
    """Retorna los argumentos para lanzar koboldcpp."""
    kobold = kobold_path or KOBOLD
    model = model_path or MODEL
    
    return [
        kobold,
        "--model", model,
        "--host", HOST,
        "--port", str(PORT),
    ]


def is_running(port: int = PORT) -> bool:
    """Verifica si koboldcpp está corriendo."""
    try:
        response = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
        return response.status_code == 200
    except:
        return False


def launch_kobold(kobold_path: str = None, model_path: str = None, wait: bool = True) -> bool:
    """
    Lanza koboldcpp si no está corriendo.
    
    Args:
        kobold_path: Ruta al ejecutable koboldcpp.exe
        model_path: Ruta al modelo .gguf
        wait: Si esperar a que el modelo esté listo
    
    Returns:
        True si el modelo está disponible
    """
    # Si ya está corriendo, no hacer nada
    if is_running():
        return True
    
    # Verificar que existen los archivos
    kobold = kobold_path or KOBOLD
    model = model_path or MODEL
    
    if not os.path.exists(kobold):
        raise FileNotFoundError(f"No se encontró koboldcpp.exe en: {kobold}")
    
    if not os.path.exists(model):
        raise FileNotFoundError(f"No se encontró el modelo en: {model}")
    
    # Construir comando
    args = get_launch_args(kobold_path, model_path)
    
    # Lanzar proceso
    try:
        subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        raise RuntimeError(f"Error al lanzar koboldcpp: {e}")
    
    if not wait:
        return True
    
    # Esperar a que esté listo (máximo 60 segundos)
    for i in range(60):
        if is_running():
            return True
        time.sleep(1)
    
    raise RuntimeError("koboldcpp no respondió después de 60 segundos")
