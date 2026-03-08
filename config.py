"""
Configuración global de Athena IDE.
"""
import os
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AthenaConfig:
    """Configuración del IDE."""
    
    # Kobold/LLM
    kobold_port: int = 5001
    kobold_host: str = "localhost"
    kobold_path: str = "../koboldcpp.exe"
    model_path: str = "../qwen2.5-coder-7b-instruct-q8_0.gguf"
    context_size: int = 8192
    max_tokens: int = 4096
    temperature: float = 0.3
    
    # UI
    theme: str = "dark_default"
    font_size: int = 12
    font_family: str = "Consolas"
    
    # Proyecto
    last_project: Optional[str] = None
    recent_files: list = None
    
    def __post_init__(self):
        if self.recent_files is None:
            self.recent_files = []
    
    @property
    def kobold_url(self) -> str:
        return f"http://{self.kobold_host}:{self.kobold_port}"
    
    def save(self, path: str = None):
        """Guarda la configuración a JSON."""
        if path is None:
            path = self._default_config_path()
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: str = None) -> 'AthenaConfig':
        """Carga la configuración desde JSON."""
        if path is None:
            path = cls._default_config_path()
        
        if not os.path.exists(path):
            return cls()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except:
            return cls()
    
    @staticmethod
    def _default_config_path() -> str:
        """Ruta por defecto del archivo de configuración."""
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'AthenaIDE', 'config.json')
    
    def add_recent_file(self, path: str):
        """Añade un archivo a la lista de recientes."""
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:10]  # Máximo 10


# Instancia global
_config: AthenaConfig = None


def get_config() -> AthenaConfig:
    """Obtiene la configuración global."""
    global _config
    if _config is None:
        _config = AthenaConfig.load()
    return _config


def save_config():
    """Guarda la configuración global."""
    if _config:
        _config.save()
