# Athena IDE

**Local AI-Based IDE with an Integrated Programming Agent**

Athena IDE is a **local AI-powered integrated development environment** that provides autonomous programming assistance directly on your desktop.

Built with **Python** and **PySide6**, and capable of connecting to **KoboldCPP** using a **GGUF model**, it allows you to safely plan and modify code under your supervision.

---

## Watch it in action

> (Add the URL of your GIF showing the HTML/JS calculator generation)

---

# Key Features

## Autonomous File Management

Athena can autonomously **open, create, edit, and delete project files** based on the needs of the requested task.

Instead of just showing code snippets in a chat window, it interacts directly with your workspace and builds the solution step by step.

---

## Anti-Hallucination Memory

Athena uses a strict project index called:

```
athena_plan.md
```

The AI is structurally forced to **read the actual files (`read_file`) before modifying code**, reducing hallucinations and ensuring that changes are grounded in the real structure of the project.

---

## Privacy First (Zero-Cloud)

Your code **never leaves your machine**.

Everything runs locally using your own models.

---

## Modern Native UI

Clean dark-themed interface built with **PySide6 / Qt**.

- No Electron
- No Chromium overhead

---

#  Requirements

## System Requirements

**Python:** 3.8+

**Operating System**

- Windows
- Linux
- macOS

**RAM**

- 8 GB minimum
- 16 GB recommended

**Storage**

- 500 MB for the application
- Additional space for GGUF models

---

## Software Dependencies

- **KoboldCPP** – Local LLM server
- **PySide6 >= 6.6** – GUI framework
- **requests** – HTTP client for API communication

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

#  Installation

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/athena-ide.git
cd athena-ide
```

---

## 2. Install Python dependencies

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

## 4. Download a model

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
├── main.py                  # Entry point
├── requirements.txt
└── README.md

# External files
├── Qwen3.5-35B-A3B-Q6_K.gguf
└── koboldcpp.exe
```

---

#  Architecture

| Component | Description |
|-----------|-------------|
| AthenaAgent | Core programming agent that analyzes code, plans actions, and executes correction loops |
| ActionEngine | Safely executes file modifications using `.athena_backups` |
| StreamWorker | Manages asynchronous communication with KoboldCPP using Qt threads |
| MainWindow | PySide6 interface containing the editor, project explorer, and AI panel |

---

#  Configuration

Athena IDE uses a **JSON configuration file** stored in the system's application data folder.

## Default configuration

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

# Usage

## Launch the IDE

### Windows

```bash
run.bat
```

### Linux / macOS

```bash
python main.py
```

### Launch with project path

```bash
python main.py /path/to/your/project
```

---

#  Autonomous Workflow

## 1. Open project

Load your project folder using the **project explorer**.

---

## 2. Request actions

Ask the AI to build something.

Example:

```
Build a traditional calculator using HTML and JavaScript
```

---

## 3. Review the plan

The agent will generate a **step-by-step plan** describing how it will complete the task.

---

## 4. Approve and execute

Once the plan is approved, Athena will automatically execute the steps:

- Read project files  
- Modify code  
- Apply changes  
- Iterate until the task is complete  

---

## 5. Monitor

You can observe:

- Plan progress  
- Modified files  
- Token usage  
- Agent activity  

---

#  BYOB (Bring Your Own Backend)

Athena is optimized for **KoboldCPP**, but it uses a **standard REST architecture**, allowing it to connect to other backends such as:

- Ollama
- LM Studio
- vLLM

You only need to change the backend URL in the configuration.

---

# Author

Created by **Pragmir**

Athena IDE is an experimental project exploring **local AI agents for software development**.
