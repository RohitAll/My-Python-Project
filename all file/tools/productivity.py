"""
Productivity Tools Subsystem
Allows managing user notes, reminders, tasks, and to-do lists stored in local SQLite database.
"""

from typing import Dict, Any, Optional
from database.database import db
from tools.registry import BaseTool, tool_registry


class CreateNoteTool(BaseTool):
    name = "create_note"
    description = "Create a new text note with title and optional tags."
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title of the note."},
            "content": {"type": "string", "description": "Body text content of the note."},
            "tags": {"type": "string", "description": "Comma-separated tag strings (e.g. 'work, project')."},
        },
        "required": ["title", "content"],
    }

    async def execute(self, title: str, content: str, tags: str = "", **kwargs) -> Dict[str, Any]:
        note_id = db.add_note(title, content, tags)
        return {"success": True, "note_id": note_id, "message": f"Successfully saved note '{title}'."}


class ReadNotesTool(BaseTool):
    name = "read_notes"
    description = "Search or retrieve saved notes."
    parameters = {
        "type": "object",
        "properties": {
            "search_query": {"type": "string", "description": "Optional keyword query to filter notes."}
        },
        "required": [],
    }

    async def execute(self, search_query: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        notes = db.get_notes(search_query)
        return {"success": True, "notes_count": len(notes), "notes": notes}


class CreateTaskTool(BaseTool):
    name = "create_task"
    description = "Create a new to-do task or task plan item."
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Title or task description."},
            "steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of sub-step descriptions.",
            },
        },
        "required": ["title"],
    }

    async def execute(self, title: str, steps: Optional[list] = None, **kwargs) -> Dict[str, Any]:
        formatted_steps = [{"step_index": i + 1, "description": s, "status": "pending"} for i, s in enumerate(steps or [])]
        task_id = db.create_task(title, formatted_steps)
        return {"success": True, "task_id": task_id, "message": f"Created task plan '{title}' with {len(formatted_steps)} step(s)."}


class ReadTasksTool(BaseTool):
    name = "read_tasks"
    description = "Retrieve list of all tasks or tasks filtered by status."
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Optional status filter ('pending', 'completed', 'failed')."}
        },
        "required": [],
    }

    async def execute(self, status: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        tasks = db.get_tasks(status)
        return {"success": True, "tasks_count": len(tasks), "tasks": tasks}


class MarkTaskCompleteTool(BaseTool):
    name = "mark_task_complete"
    description = "Mark a task as completed."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "Database ID of the task to complete."}
        },
        "required": ["task_id"],
    }

    async def execute(self, task_id: int, **kwargs) -> Dict[str, Any]:
        success = db.update_task_status(task_id, "completed")
        if success:
            return {"success": True, "message": f"Task #{task_id} marked as completed."}
        else:
            return {"success": False, "error": f"Task #{task_id} not found."}


def register_productivity_tools():
    tool_registry.register(CreateNoteTool())
    tool_registry.register(ReadNotesTool())
    tool_registry.register(CreateTaskTool())
    tool_registry.register(ReadTasksTool())
    tool_registry.register(MarkTaskCompleteTool())


register_productivity_tools()
