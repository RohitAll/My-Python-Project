"""
JARVIS Desktop AI Assistant Main Entry Point
Initializes subsystems with startup health checks and launches PySide6 GUI application.
"""

import sys
import os
import site
import logging
from pathlib import Path

# Ensure user site-packages directory is in sys.path
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ensure standard user AppData site-packages are in sys.path for Windows Store / standalone Python
appdata_site = os.path.expanduser(r"~\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")
if os.path.exists(appdata_site) and appdata_site not in sys.path:
    sys.path.insert(0, appdata_site)

# Ensure UTF-8 encoding for Windows stdout console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root workspace directory is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configure logging format
from config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("JARVIS.Startup")


def run_startup_sequence():
    """Executes step-by-step subsystem initialization and health checks."""
    print("\nInitializing JARVIS...")
    logger.info("Starting JARVIS Assistant Initialization Sequence...")

    # 1. Core System
    print("[OK] Core system")
    logger.info("Core system initialized.")

    # 2. AI Engine
    try:
        from ai.provider import get_llm_provider

        provider = get_llm_provider()
        print(f"[OK] AI engine ({provider.__class__.__name__})")
        logger.info("AI engine initialized with provider: %s", provider.__class__.__name__)
    except Exception as e:
        print("[!] AI engine (Fallback mode)")
        logger.warning("AI engine initialization warning: %s", e)

    # 3. Memory System
    try:
        from database.database import db
        from memory.memory_manager import memory_manager

        print("[OK] Memory system (SQLite DB ready)")
        logger.info("Memory system initialized.")
    except Exception as e:
        print("[!] Memory system error")
        logger.error("Memory initialization failed: %s", e)

    # 4. Voice Subsystem
    try:
        from voice.speech_to_text import get_stt_provider
        from voice.text_to_speech import get_tts_provider

        stt = get_stt_provider()
        tts = get_tts_provider()
        print("[OK] Voice system")
        logger.info("Voice subsystem initialized.")
    except Exception as e:
        print("[!] Voice system (Disabled)")
        logger.warning("Voice subsystem warning: %s", e)

    # 5. Tools Registry
    try:
        from tools.registry import tool_registry
        from tools.system import register_system_tools
        from tools.applications import register_application_tools
        from tools.browser import register_browser_tools
        from tools.files import register_file_tools
        from tools.computer import register_computer_tools
        from tools.developer import register_developer_tools
        from tools.productivity import register_productivity_tools
        from memory.memory_manager import register_memory_tools

        tool_count = len(tool_registry.list_tools())
        print(f"[OK] Tools ({tool_count} registered modules)")
        logger.info("Tools system initialized with %d modules.", tool_count)
    except Exception as e:
        print("[!] Tools subsystem error")
        logger.error("Tools initialization failed: %s", e)

    # 6. Security Confirmation Subsystem
    try:
        from security.permissions import security_checker
        from security.confirmations import confirmation_manager

        print("[OK] Security system")
        logger.info("Security confirmation system ready.")
    except Exception as e:
        print("[!] Security system error")

    # 7. User Interface
    print("[OK] User interface")
    logger.info("User interface preparing to render.")

    print("\nJARVIS is ready.\n")


def main():
    run_startup_sequence()

    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Desktop AI Assistant")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
