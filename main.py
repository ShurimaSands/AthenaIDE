"""
Athena IDE - Entry Point
Un IDE AI-first, local y autónomo con agente de programación integrado.
"""
import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from ai.kobold_launcher import launch_kobold


def main():
    """Punto de entrada principal de Athena IDE."""
    
    # Intentar lanzar koboldcpp si no está corriendo
    print("🦉 Athena IDE - Iniciando...")
    
    try:
        print("   Verificando koboldcpp...")
        launch_kobold()
        print("   ✓ Modelo listo")
    except Exception as e:
        print(f"   ⚠ No se pudo iniciar koboldcpp: {e}")
        print("   El IDE funcionará pero sin IA hasta que koboldcpp esté disponible.")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Athena IDE")
    app.setOrganizationName("Athena")
    
    # Configurar fuente por defecto
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Determinar directorio del proyecto
    # Si se pasa un argumento, usarlo como root
    project_root = None
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.isdir(arg_path):
            project_root = arg_path
        elif os.path.isfile(arg_path):
            project_root = os.path.dirname(arg_path)
    
    # Crear y mostrar ventana principal
    window = MainWindow(project_root)
    window.show()
    
    print("   ✓ IDE listo")
    print("")
    
    # Ejecutar loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
