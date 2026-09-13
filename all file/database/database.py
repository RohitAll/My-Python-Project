"""
SQLite Database Layer for JARVIS Assistant
Manages local persistence for memory, tasks, notes, reminders, and history.
"""

import sqlite3
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.settings import settings

logger = logging.getLogger("JARVIS.Database")


class Database:
    """Thread-safe SQLite database manager."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a sqlite3 connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates database schema if tables do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Memories Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key_term TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key_term)
                )
            """
            )

            # Tasks Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    steps_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """
            )

            # Notes Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Reminders Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    remind_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Conversation History Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            logger.info("Database schema initialized at %s", self.db_path)

    # ---------------- Memory Operations ----------------
    def store_memory(self, category: str, key_term: str, value: str) -> bool:
        """Insert or update a persistent memory entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memories (category, key_term, value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key_term) DO UPDATE SET
                    value=excluded.value,
                    updated_at=CURRENT_TIMESTAMP
            """,
                (category.lower(), key_term.lower(), value),
            )
            conn.commit()
            return True

    def get_memories(self, category: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve stored memories matching optional category and query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM memories WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category.lower())

            if search_query:
                query += " AND (key_term LIKE ? OR value LIKE ?)"
                like_str = f"%{search_query.lower()}%"
                params.extend([like_str, like_str])

            query += " ORDER BY updated_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_memory(self, key_term: str) -> bool:
        """Delete memory entries matching a key term."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE key_term LIKE ?", (f"%{key_term.lower()}%",))
            conn.commit()
            return cursor.rowcount > 0

    # ---------------- Task Operations ----------------
    def create_task(self, title: str, steps: List[Dict[str, Any]]) -> int:
        """Record a new task plan into the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (title, status, steps_json)
                VALUES (?, 'pending', ?)
            """,
                (title, json.dumps(steps)),
            )
            conn.commit()
            return cursor.lastrowid

    def update_task_status(self, task_id: int, status: str, steps: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Update status and steps state for a task."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat() if status in ["completed", "failed"] else None
            if steps is not None:
                cursor.execute(
                    """
                    UPDATE tasks SET status = ?, steps_json = ?, completed_at = ? WHERE id = ?
                """,
                    (status, json.dumps(steps), now, task_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?
                """,
                    (status, now, task_id),
                )
            conn.commit()
            return cursor.rowcount > 0

    def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch list of tasks with parsed steps JSON."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY id DESC", (status,))
            else:
                cursor.execute("SELECT * FROM tasks ORDER BY id DESC")

            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["steps"] = json.loads(item["steps_json"])
                results.append(item)
            return results

    # ---------------- Notes & Reminders Operations ----------------
    def add_note(self, title: str, content: str, tags: str = "") -> int:
        """Store a new note."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO notes (title, content, tags)
                VALUES (?, ?, ?)
            """,
                (title, content, tags),
            )
            conn.commit()
            return cursor.lastrowid

    def get_notes(self, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve notes matching query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                q = f"%{search_query}%"
                cursor.execute(
                    "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC",
                    (q, q),
                )
            else:
                cursor.execute("SELECT * FROM notes ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    # ---------------- Conversation History ----------------
    def log_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a conversation message in history log."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversation_logs (role, content, metadata_json)
                VALUES (?, ?, ?)
            """,
                (role, content, json.dumps(metadata or {})),
            )
            conn.commit()
            return cursor.lastrowid

    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent conversation logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversation_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = [dict(r) for r in cursor.fetchall()]
            rows.reverse()
            return rows


db = Database()
