"""
High-Level Memory Manager & Tool Integrations
Provides memory management logic and registers memory tools into JARVIS tool system.
"""

import logging
from typing import Dict, Any, Optional, List

from memory.memory_store import memory_store
from memory.memory_search import memory_search
from tools.registry import BaseTool, tool_registry

logger = logging.getLogger("JARVIS.Memory")


class MemoryManager:
    """Manages remembering user facts, preferences, and details."""

    def remember(self, key_term: str, value: str, category: str = "user_preference") -> Dict[str, Any]:
        """Store a fact in memory."""
        # Sanity check: do not store obvious API keys or secrets
        if any(secret in key_term.lower() or secret in value.lower() for secret in ["api_key", "password", "token", "secret", "bearer"]):
            return {"success": False, "error": "Refused to store sensitive security credential or secret in memory."}

        success = memory_store.save_fact(category, key_term, value)
        logger.info("Saved memory fact: [%s] %s = %s", category, key_term, value)
        return {"success": success, "message": f"I will remember that {key_term} is '{value}'."}

    def recall(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve memories matching query."""
        return memory_search.find_relevant(query)

    def forget(self, key_term: str) -> Dict[str, Any]:
        """Forget a fact from memory."""
        success = memory_store.delete(key_term)
        if success:
            return {"success": True, "message": f"Successfully removed '{key_term}' from memory."}
        else:
            return {"success": False, "error": f"No memory found matching '{key_term}'."}


memory_manager = MemoryManager()


# Register Memory Tools into Tool Registry
class RememberFactTool(BaseTool):
    name = "remember_fact"
    description = "Store a user preference, detail, or fact into persistent memory."
    parameters = {
        "type": "object",
        "properties": {
            "key_term": {"type": "string", "description": "Concept or key name (e.g. 'preferred_editor', 'name', 'project')."},
            "value": {"type": "string", "description": "Value to remember (e.g. 'VS Code', 'John')."},
            "category": {"type": "string", "description": "Category (default 'user_preference')."},
        },
        "required": ["key_term", "value"],
    }

    async def execute(self, key_term: str, value: str, category: str = "user_preference", **kwargs) -> Dict[str, Any]:
        return memory_manager.remember(key_term, value, category)


class GetMemoriesTool(BaseTool):
    name = "get_memories"
    description = "Retrieve stored user preferences or remembered facts."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Query term to search for in memory."}
        },
        "required": [],
    }

    async def execute(self, query: str = "", **kwargs) -> Dict[str, Any]:
        results = memory_manager.recall(query)
        return {"success": True, "count": len(results), "memories": results}


class DeleteMemoryTool(BaseTool):
    name = "delete_memory"
    description = "Forget a stored memory or preference by key term."
    parameters = {
        "type": "object",
        "properties": {
            "key_term": {"type": "string", "description": "Key term or detail to remove from memory."}
        },
        "required": ["key_term"],
    }

    async def execute(self, key_term: str, **kwargs) -> Dict[str, Any]:
        return memory_manager.forget(key_term)


def register_memory_tools():
    tool_registry.register(RememberFactTool())
    tool_registry.register(GetMemoriesTool())
    tool_registry.register(DeleteMemoryTool())


register_memory_tools()
