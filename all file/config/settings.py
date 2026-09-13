"""
JARVIS Assistant Configuration Module
Manages environment variables, defaults, logging configuration, and runtime settings.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path=None, override=False):
        path = Path(dotenv_path) if dotenv_path else BASE_DIR / ".env"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if override or k not in os.environ:
                        os.environ[k] = v

# Load environment variables from .env if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()


class Settings:
    """Central configuration class for JARVIS assistant."""

    def __init__(self):
        self.BASE_DIR: Path = BASE_DIR
        self.LOGS_DIR: Path = BASE_DIR / "logs"
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE: Path = self.LOGS_DIR / "jarvis.log"

        # AI Configuration
        self.DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini").lower()
        self.AI_MODEL: str = os.getenv("AI_MODEL", "gemini-2.5-flash")
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

        # Voice Settings
        self.ENABLE_VOICE: bool = os.getenv("ENABLE_VOICE", "true").lower() == "true"
        self.STT_PROVIDER: str = os.getenv("STT_PROVIDER", "google").lower()
        self.TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "pyttsx3").lower()
        self.TTS_VOICE: str = os.getenv("TTS_VOICE", "")
        self.WAKE_WORD_ENABLED: bool = os.getenv("WAKE_WORD_ENABLED", "false").lower() == "true"
        self.WAKE_WORD: str = os.getenv("WAKE_WORD", "hey jarvis").lower()

        # Security & Confirmation Settings
        self.REQUIRE_CONFIRMATION_FOR_DESTRUCTIVE: bool = (
            os.getenv("REQUIRE_CONFIRMATION_FOR_DESTRUCTIVE", "true").lower() == "true"
        )
        self.AUTO_APPROVE_LOW_RISK: bool = os.getenv("AUTO_APPROVE_LOW_RISK", "true").lower() == "true"

        # System & Database Settings
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.DATABASE_PATH: Path = BASE_DIR / os.getenv("DATABASE_PATH", "jarvis.db")
        self.APP_THEME: str = os.getenv("APP_THEME", "futuristic_dark")

    def reload(self):
        """Reload configuration from disk."""
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
        self.__init__()


settings = Settings()
