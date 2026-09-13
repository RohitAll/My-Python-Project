"""
Memory Search & Retrieval Engine
Filters and ranks relevant memory entries for prompt context injection.
"""

from typing import List, Dict, Any
from memory.memory_store import memory_store


class MemorySearchEngine:
    """Ranks and retrieves relevant user memories."""

    @staticmethod
    def find_relevant(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to user request."""
        memories = memory_store.search(query)
        if not memories:
            # Fallback to fetching all general user preferences if query is generic
            memories = memory_store.fetch_all(category="user_preference")
        return memories[:limit]


memory_search = MemorySearchEngine()
