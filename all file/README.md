# JARVIS Personal AI Assistant

A futuristic, intelligent desktop companion built for Windows using Python 3.11+, PySide6 (Qt), AsyncIO, SQLite, LLM provider orchestration, STT/TTS voice provider abstractions, modular computer tools, safety confirmation dialogs, memory system, and multi-step task execution.

---

## 🌟 Features

- **Futuristic Desktop UI**: Dark neon glassmorphism interface featuring an animated glowing AI Core Orb (`IDLE`, `LISTENING`, `THINKING`, `SPEAKING`, `EXECUTING`, `ERROR`), digital header, chat feed, and live system dashboard.
- **Multi-Provider AI Brain**: Seamless orchestration across Google Gemini, OpenAI, Groq, or a built-in offline rule engine fallback.
- **Voice & Wake Word Subsystem**: Abstracted speech-to-text (STT) and text-to-speech (TTS - `pyttsx3` offline / `edge-tts` neural voice) with optional "Hey JARVIS" background wake word listener.
- **Modular Tool Ecosystem**:
  - **System Metrics**: CPU, RAM, Disk, Battery, Network, and Time metrics.
  - **Applications**: Open, launch, focus, and terminate desktop programs.
  - **Browser & Search**: Live web search (Google/DuckDuckGo/Wikipedia) and URL opener.
  - **File Management**: List, search, read, create, rename, copy, move, and delete files.
  - **Computer Control**: Keyboard typing, mouse click, hotkeys via PyAutoGUI.
  - **Developer Tools**: Create code files, read code, explain code, run safe scripts.
  - **Productivity**: Notes, reminders, and to-do task plan management.
- **Safety Confirmation System**: Intercepts dangerous actions (file deletion, mass modifications, shell execution) and displays an interactive modal dialog with `[Confirm]` and `[Cancel]` buttons.
- **Persistent Local Memory**: Stores user preferences and facts ("Remember X", "Recall Y", "Forget Z") securely in SQLite without storing passwords or secrets.
- **Multi-Step Task Execution**: Decomposes complex user prompts into step-by-step plans and tracks step progress on the UI dashboard.

---

## 🏗️ Architecture

```
JARVIS/
├── app.py                      # Main entry point & startup health checks
├── requirements.txt            # Project Python dependencies
├── .env.example                # Template environment variables
├── README.md                   # Complete documentation
│
├── config/
│   └── settings.py             # Configuration & environment manager
├── database/
│   └── database.py             # SQLite thread-safe database connection pool
├── security/
│   ├── permissions.py          # Action risk evaluation engine (LOW, MEDIUM, HIGH, DANGEROUS)
│   └── confirmations.py        # Async confirmation bridge to GUI modal
├── ai/
│   ├── provider.py             # LLM Base class (Gemini, OpenAI, Groq, Offline)
│   ├── model.py                # AI model request dispatcher & JSON tool parser
│   └── prompts.py              # System personality & tool schemas
├── voice/
│   ├── speech_to_text.py       # STT Provider abstraction (Google STT)
│   ├── text_to_speech.py       # TTS Provider abstraction (PyTTSx3, EdgeTTS)
│   └── wake_word.py            # Async "Hey JARVIS" wake word detector thread
├── tools/
│   ├── registry.py             # BaseTool interface & tool registry
│   ├── system.py               # Hardware metrics tools
│   ├── applications.py         # Application control tools
│   ├── browser.py              # Web browsing & live search tools
│   ├── files.py                # Local file system tools
│   ├── computer.py             # Mouse & keyboard control tools
│   ├── developer.py            # Code execution & explanation tools
│   └── productivity.py         # Notes & task plan tools
├── memory/
│   ├── memory_store.py         # Low-level SQLite memory table operations
│   ├── memory_search.py        # Relevant memory retrieval engine
│   └── memory_manager.py       # High-level memory operations ("Remember this")
├── core/
│   ├── assistant.py            # Master assistant state machine controller
│   ├── orchestrator.py         # Request router (Chat vs Single Tool vs Multi-step Task)
│   ├── context.py              # Conversation history window manager
│   └── task_manager.py         # Multi-step task planner & step tracker
├── ui/
│   ├── main_window.py          # PySide6 MainWindow layout assembly
│   ├── styles/
│   │   └── theme.py            # QSS stylesheet with cyan neon accents & glass cards
│   └── components/
│       ├── orb_widget.py       # Animated glowing QPainter AI Core Orb
│       ├── header_widget.py    # Digital clock, mic status, engine badge
│       ├── chat_widget.py      # Rich message history display
│       ├── side_panel.py       # Live gauges, task tracker, memory inspector, tool list
│       └── confirmation_dialog.py # Custom security modal dialog
└── tests/                      # Pytest unit test suite
```

---

## ⚡ Quick Start

### 1. Requirements
- **OS**: Windows 10/11
- **Python**: Python 3.11+
- **Microphone & Speakers** (for voice functionality)

### 2. Installation
Clone or open the project folder in terminal:
```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your API keys and options:
```ini
DEFAULT_AI_PROVIDER=gemini
AI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_gemini_api_key_here

ENABLE_VOICE=true
STT_PROVIDER=google
TTS_PROVIDER=pyttsx3
WAKE_WORD_ENABLED=false
```

*Note: If no API key is supplied, JARVIS automatically runs in **Offline Fallback Mode**, answering local system commands and executing system tools.*

### 4. Running JARVIS
Launch the assistant application:
```bash
python app.py
```

---

## 💡 Example Commands

Try typing or speaking any of the following natural language commands:

- **System Diagnostics**:
  - *"What is my CPU usage?"*
  - *"Check my RAM memory."*
  - *"Show battery status."*
  - *"What time is it?"*
- **Application Control**:
  - *"Open Chrome."*
  - *"Launch Notepad."*
  - *"Close Chrome."*
- **Web Search & Browsing**:
  - *"Search the web for today's technology news."*
  - *"Open youtube.com."*
- **Memory & Preferences**:
  - *"Remember that my preferred editor is VS Code."*
  - *"What did I ask you to remember?"*
  - *"Forget my preferred editor."*
- **File System Operations**:
  - *"List files in current directory."*
  - *"Create a file called notes.txt."*
  - *"Delete this folder."* (Triggers security modal confirmation)
- **Multi-Step Automation**:
  - *"Open Chrome, search for Python tutorials, and create a note with the findings."*

---

## 🛠️ How to Add a New Tool

To extend JARVIS with custom capabilities:

1. Create a new tool class in `tools/` inheriting from `BaseTool`:
```python
from tools.registry import BaseTool, tool_registry

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Description of what this tool does."
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description."}
        },
        "required": ["param1"]
    }

    async def execute(self, param1: str, **kwargs):
        # Your custom logic here
        return {"success": True, "result": f"Processed {param1}"}

# Register tool into registry
tool_registry.register(MyCustomTool())
```
2. Import the tool in `app.py` or the appropriate module. It will automatically register into the AI schema and GUI dashboard.

---

## 🧪 Running Unit Tests

Run the test suite using `pytest`:
```bash
pytest tests/ -v
```
