# Athena IDE

**AI-First Local IDE with Integrated Programming Agent**

Athena IDE is a local AI-powered integrated development environment that provides support for autonomous programming directly on your desktop. Developed with Python and PySide 6, and connected to Koboldcpp and a gguf model, it can safely plan and modify code under your supervision.
![Athena IDE](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)

> **Watch it in action:**  
> ![Athena IDE Demo](URL_AQUI_DE_TU_VIDEO_O_GIF_DE_LA_CALCULADORA.gif)  
> *(Add your GIF URL showcasing the HTML/JS calculator generation)*

---

# 🌟 Killer Features
## Autonomous File Management

Athena can autonomously open, create, edit, and delete project files depending on the specific needs of your requested task. Instead of just giving you code snippets in a chat window, it acts directly on your workspace to build the solution step by step.

## Anti-Hallucination Memory

Enforces a strict `athena_plan.md` project index.

The AI is structurally forced to **read reality (`read_file`) before modifying code**, preventing hallucinations.




## Privacy First (Zero-Cloud)

Your code **never leaves your machine**.

## Modern Native UI

Clean **dark-themed UI built with PySide6 / Qt**.

No Electron or Chromium bloat.

## Privacy First (Zero-Cloud)

Your code **never leaves your machine**.

## Modern Native UI

Clean **dark-themed UI built with PySide6 / Qt**.

No Electron or Chromium bloat.

---

# 📋 Requirements

## System Requirements

- **Python:** 3.8+
- **Operating System:** Windows / Linux / macOS
- **RAM:**  
  - 8GB minimum  
  - 16GB recommended
- **Storage:**  
  - 500MB for application  
  - Space for GGUF models

---

## Software Dependencies

- **KoboldCPP** – Local LLM server
- **PySide6 >= 6.6** – GUI framework
- **requests** – HTTP client

---

## Model Requirements

Recommended model:

```
Qwen3.5-35B-A3B-Q6_K.gguf
```

Format:

```
GGUF
```

Recommended quantizations:

- Q4_K_M
- Q8_0

Recommended context size:

```
4096 – 8192 tokens
```

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/athena-ide.git
cd athena-ide
```

---

## 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Install KoboldCPP

Download KoboldCPP from the official repository.

### Windows

```bash
# Download koboldcpp.exe from
https://github.com/LostRuins/koboldcpp

# Place it in the project root as:
koboldcpp.exe
```

### Linux / macOS

```bash
# Download the binary
chmod +x koboldcpp

# Place it in the project root
```

---

## 4. Download a Model

Place your **GGUF model** in the project root.

Example structure:

```
athena-ide/

├── ai/                      # AI Engine & Agent
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
├── project/                 # Project management
│   └── project_manager.py
│
├── ui/                      # User Interface
│   ├── ai_panel.py
│   ├── editor.py
│   ├── main_window.py
│   ├── markdown_viewer.py
│   ├── project_explorer.py
│   ├── syntax_highlighter.py
│   ├── tab_widget.py
│   └── theme.py
│
├── config.py                # Global configuration
├── main.py                  # Application entry point
├── requirements.txt
└── README.md

# External files
├── Qwen3.5-35B-A3B-Q6_K.gguf
└── koboldcpp.exe
```

---

# 🏗️ Architecture

| Component | Description |
|-----------|-------------|
| **AthenaAgent** | Core programming agent that analyzes code, plans actions, and performs correction loops |
| **ActionEngine** | Executes file modifications safely using `.athena_backups` |
| **StreamWorker** | Asynchronous communication with KoboldCPP via Qt Threads |
| **MainWindow** | PySide6 UI containing the editor, project explorer, and AI panel |

---

# ⚙️ Configuration

Athena IDE uses a **JSON configuration file** stored in the system's application data folder.

## Default Configuration

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

# 🎮 Usage

## Launch the IDE

### Windows

```bash
run.bat
```

### Linux / macOS

```bash
python main.py
```

### Launch with Project Path

```bash
python main.py /path/to/your/project
```

---

# 🤖 The Autonomous Workflow

## 1. Open Project

Load your project folder via the **project explorer**.

---

## 2. Request Actions

Ask the AI to build something.

Example:

```
Build a traditional calculator using HTML and JS
```

---

## 3. Review Plan

The agent will generate a **step-by-step plan**.

---

## 4. Approve & Execute automatic

---

## 5. Monitor

You can watch:

- action plan progress
- file modifications
- live token counter

## BYOB (Bring Your Own Backend)

Natively optimized for **KoboldCPP**, but built on a **standard REST API architecture**.

Supported backends include:

- Ollama
- LM Studio
- vLLM

Simply change the backend URL in the configuration.

Athena ide By Pragmir
