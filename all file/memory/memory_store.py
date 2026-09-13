"""
Memory Store Persistence Layer
Interactions with local SQLite memory tables.
"""

from typing import List, Dict, Any, Optional
from database.database import db


class MemoryStore:
    """Low-level SQLite memory storage operations."""

    def save_fact(self, category: str, key_term: str, value: str) -> bool:
        return db.store_memory(category, key_term, value)

    def fetch_all(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.get_memories(category=category)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return db.get_memories(search_query=query)

    def delete(self, key_term: str) -> bool:
        return db.delete_memory(key_term)


memory_store = MemoryStore()
