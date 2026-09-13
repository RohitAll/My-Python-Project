"""
Conversation Context & History Window Manager
Manages history logs, summarization, and context window pruning for LLM prompts.
"""

from typing import List, Dict, Any
from database.database import db


class ContextManager:
    """Manages short-term conversation context."""

    def __init__(self, max_history: int = 15):
        self.max_history = max_history

    def add_message(self, role: str, content: str, metadata: dict = None):
        """Log message to database and update history buffer."""
        db.log_message(role, content, metadata)

    def get_context_history(self) -> List[Dict[str, str]]:
        """Retrieve recent conversation turns formatted for LLM context."""
        recent_logs = db.get_recent_history(limit=15)
        history = []
        for log in recent_logs:
            role = "assistant" if log["role"] == "jarvis" else log["role"]
            history.append({"role": role, "content": log["content"]})
        return history


context_manager = ContextManager()
