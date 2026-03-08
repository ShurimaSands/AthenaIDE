# Athena IDE

**IDE local basado en IA con agente de programación integrado**

Athena IDE es un **entorno de desarrollo integrado local impulsado por IA** que ofrece asistencia para programación autónoma directamente en tu escritorio. Desarrollado con **Python** y **PySide6**, y capaz de conectarse a **KoboldCPP** utilizando un **modelo GGUF**, permite planificar y modificar código de forma segura bajo tu supervisión.

![Athena IDE](https://img.shields.io/badge/Python-3.8+-blue)
![Plataforma](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)

> **Míralo en acción:**  
> ![Demostración de Athena IDE](URL_AQUI_DE_TU_VIDEO_O_GIF_DE_LA_CALCULADORA.gif)  
> *(Añade la URL de tu GIF mostrando la generación de la calculadora HTML/JS)*

---

# Funciones destacadas

## Gestión autónoma de archivos

Athena puede **abrir, crear, editar y eliminar archivos del proyecto** de forma autónoma según las necesidades de la tarea solicitada.

En lugar de limitarse a mostrar fragmentos de código en una ventana de chat, interactúa directamente con tu espacio de trabajo y construye la solución paso a paso.

## Memoria anti-alucinaciones

Athena utiliza un índice de proyecto estricto llamado `athena_plan.md`.

La IA está estructuralmente obligada a **leer los archivos reales (`read_file`) antes de modificar el código**, reduciendo alucinaciones y asegurando que los cambios se basen en la estructura real del proyecto.

## Privacidad ante todo (Zero-Cloud)

Tu código **nunca sale de tu máquina**.

Todo se ejecuta localmente usando tus propios modelos.

## Interfaz nativa moderna

Interfaz limpia en modo oscuro construida con **PySide6 / Qt**.

Sin Electron. Sin sobrecarga de Chromium.

---

# Requisitos

## Requisitos del sistema

- **Python:** 3.8+
- **Sistema operativo:** Windows / Linux / macOS
- **RAM:**
  - 8 GB mínimo
  - 16 GB recomendado
- **Almacenamiento:**
  - 500 MB para la aplicación
  - Espacio adicional para modelos GGUF

---

## Dependencias de software

- **KoboldCPP** – Servidor LLM local
- **PySide6 >= 6.6** – Framework de interfaz gráfica
- **requests** – Cliente HTTP para comunicación con la API

---

## Requisitos del modelo

Modelo recomendado:

```
Qwen3.5-35B-A3B-Q6_K.gguf
```

Formato:

```
GGUF
```

Cuantizaciones recomendadas:

- Q4_K_M
- Q8_0

Tamaño de contexto recomendado:

```
4096 – 8192 tokens
```

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/yourusername/athena-ide.git
cd athena-ide
```

---

## 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

---

## 3. Instalar KoboldCPP

Descarga KoboldCPP desde el repositorio oficial.

### Windows

```bash
# Descargar koboldcpp.exe desde
https://github.com/LostRuins/koboldcpp

# Colocarlo en la raíz del proyecto como:
koboldcpp.exe
```

### Linux / macOS

```bash
# Descargar el binario
chmod +x koboldcpp

# Colocarlo en la raíz del proyecto
```

---

## 4. Descargar un modelo

Coloca tu **modelo GGUF** en la raíz del proyecto.

Ejemplo de estructura:

```
athena-ide/

├── ai/                      # Motor y agente de IA
│   ├── action_engine.py
│   ├── action_plan.py
│   ├── agent.py
│   ├── agent_state.py
│   ├── context_builder.py
│   ├── kobold_client.py
│   ├── kobold_launcher.py
│   ├── prompts.py
│   └── stream_worker.py
│
├── project/                 # Gestión de proyectos
│   └── project_manager.py
│
├── ui/                      # Interfaz de usuario
│   ├── ai_panel.py
│   ├── editor.py
│   ├── main_window.py
│   ├── markdown_viewer.py
│   ├── project_explorer.py
│   ├── syntax_highlighter.py
│   ├── tab_widget.py
│   └── theme.py
│
├── config.py                # Configuración global
├── main.py                  # Punto de entrada
├── requirements.txt
└── README.md

# Archivos externos
├── Qwen3.5-35B-A3B-Q6_K.gguf
└── koboldcpp.exe
```

---

# Arquitectura

| Componente | Descripción |
|------------|-------------|
| **AthenaAgent** | Agente de programación principal que analiza código, planifica acciones y ejecuta bucles de corrección |
| **ActionEngine** | Ejecuta modificaciones de archivos de forma segura mediante `.athena_backups` |
| **StreamWorker** | Gestiona la comunicación asíncrona con KoboldCPP usando hilos de Qt |
| **MainWindow** | Interfaz PySide6 que contiene editor, explorador de proyectos y panel de IA |

---

# Configuración

Athena IDE utiliza un **archivo de configuración JSON** almacenado en la carpeta de datos de la aplicación del sistema.

## Configuración predeterminada

```json
{
  "kobold_port": 5001,
  "kobold_host": "localhost",
  "kobold_path": "../koboldcpp.exe",
  "model_path": "../Qwen3.5-35B-A3B-Q6_K.gguf",
  "context_size": 8192,
  "max_tokens": 20000,
  "temperature": 0.3,
  "theme": "dark_default",
  "font_size": 12,
  "font_family": "Consolas"
}
```

---

# Uso

## Iniciar el IDE

### Windows

```bash
run.bat
```

### Linux / macOS

```bash
python main.py
```

### Iniciar con ruta de proyecto

```bash
python main.py /path/to/your/project
```

---

# Flujo de trabajo autónomo

## 1. Abrir proyecto

Carga la carpeta de tu proyecto usando el **explorador de proyectos**.

---

## 2. Solicitar acciones

Pide a la IA que construya algo.

Ejemplo:

```
Construir una calculadora tradicional usando HTML y JavaScript
```

---

## 3. Revisar el plan

El agente generará un **plan paso a paso** que describe cómo completará la tarea.

---

## 4. Aprobar y ejecutar

Una vez aprobado el plan, Athena ejecutará automáticamente los pasos:

- leer archivos del proyecto
- modificar código
- aplicar cambios
- iterar hasta completar la tarea

---

## 5. Monitorear

Puedes observar:

- progreso del plan
- archivos modificados
- uso de tokens
- actividad del agente

---

# BYOB (Bring Your Own Backend)

Athena está optimizado para **KoboldCPP**, pero utiliza una **arquitectura REST estándar**, lo que permite conectarlo fácilmente a otros backends como:

- Ollama
- LM Studio
- vLLM

Solo debes cambiar la URL del backend en la configuración.

---

# Autor

Creado por **Pragmir**

Athena IDE es un proyecto experimental que explora **agentes de IA locales para el desarrollo de software**.