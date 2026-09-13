"""
File System Management Tools
Provides safe local file operations: listing, searching, reading, creating, moving, copying, deleting.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List

from tools.registry import BaseTool, tool_registry


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "List files and subdirectories in a given directory path."
    parameters = {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to directory (defaults to current directory if empty).",
            }
        },
        "required": [],
    }

    async def execute(self, directory_path: str = ".", **kwargs) -> Dict[str, Any]:
        p = Path(directory_path).resolve()
        if not p.exists():
            return {"success": False, "error": f"Directory path '{directory_path}' does not exist."}
        if not p.is_dir():
            return {"success": False, "error": f"Path '{directory_path}' is a file, not a directory."}

        items = []
        for child in p.iterdir():
            items.append(
                {
                    "name": child.name,
                    "is_dir": child.is_dir(),
                    "size_bytes": child.stat().st_size if child.is_file() else 0,
                }
            )

        return {"success": True, "path": str(p), "items_count": len(items), "items": items}


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files matching a keyword or pattern within a folder."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Filename keyword or pattern to search for."},
            "directory_path": {"type": "string", "description": "Starting directory (defaults to current dir)."},
            "max_results": {"type": "integer", "description": "Maximum search results to return (default: 20)."},
        },
        "required": ["query"],
    }

    async def execute(self, query: str, directory_path: str = ".", max_results: int = 20, **kwargs) -> Dict[str, Any]:
        p = Path(directory_path).resolve()
        if not p.exists():
            return {"success": False, "error": f"Directory path '{directory_path}' does not exist."}

        matches = []
        query_lower = query.lower()
        for root, dirs, files in os.walk(p):
            for file in files:
                if query_lower in file.lower():
                    matches.append(str(Path(root) / file))
                    if len(matches) >= max_results:
                        break
            if len(matches) >= max_results:
                break

        return {"success": True, "query": query, "matches_count": len(matches), "matches": matches}


class CreateFileTool(BaseTool):
    name = "create_file"
    description = "Create a new file with specified content."
    parameters = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string", "description": "Path of file to create."},
            "content": {"type": "string", "description": "Text content to write into the file."},
            "overwrite": {"type": "boolean", "description": "Overwrite file if it already exists."},
        },
        "required": ["filepath", "content"],
    }

    async def execute(self, filepath: str, content: str, overwrite: bool = False, **kwargs) -> Dict[str, Any]:
        p = Path(filepath).resolve()
        if p.exists() and not overwrite:
            return {"success": False, "error": f"File '{filepath}' already exists. Set overwrite=True to replace it."}

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "message": f"Successfully created file: '{str(p)}'"}


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read text content from a local file."
    parameters = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string", "description": "Path of file to read."},
            "max_lines": {"type": "integer", "description": "Max lines to read (default 200)."},
        },
        "required": ["filepath"],
    }

    async def execute(self, filepath: str, max_lines: int = 200, **kwargs) -> Dict[str, Any]:
        p = Path(filepath).resolve()
        if not p.exists():
            return {"success": False, "error": f"File '{filepath}' not found."}
        if not p.is_file():
            return {"success": False, "error": f"Path '{filepath}' is a directory."}

        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[:max_lines]
        return {
            "success": True,
            "filepath": str(p),
            "lines_count": len(lines),
            "content": "\n".join(lines),
        }


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a specified file or directory from disk."
    parameters = {
        "type": "object",
        "properties": {"filepath": {"type": "string", "description": "Path of file or folder to delete."}},
        "required": ["filepath"],
    }

    async def execute(self, filepath: str, **kwargs) -> Dict[str, Any]:
        p = Path(filepath).resolve()
        if not p.exists():
            return {"success": False, "error": f"Path '{filepath}' does not exist."}

        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

        return {"success": True, "message": f"Successfully deleted '{str(p)}'."}


class CopyFileTool(BaseTool):
    name = "copy_file"
    description = "Copy a file or directory to a destination path."
    parameters = {
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "Source path."},
            "dst": {"type": "string", "description": "Destination path."},
        },
        "required": ["src", "dst"],
    }

    async def execute(self, src: str, dst: str, **kwargs) -> Dict[str, Any]:
        s = Path(src).resolve()
        d = Path(dst).resolve()
        if not s.exists():
            return {"success": False, "error": f"Source '{src}' does not exist."}

        if s.is_file():
            shutil.copy2(s, d)
        else:
            shutil.copytree(s, d, dirs_exist_ok=True)

        return {"success": True, "message": f"Copied '{str(s)}' to '{str(d)}'."}


class MoveFileTool(BaseTool):
    name = "move_file"
    description = "Move or rename a file/directory."
    parameters = {
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "Source path."},
            "dst": {"type": "string", "description": "Destination path."},
        },
        "required": ["src", "dst"],
    }

    async def execute(self, src: str, dst: str, **kwargs) -> Dict[str, Any]:
        s = Path(src).resolve()
        d = Path(dst).resolve()
        if not s.exists():
            return {"success": False, "error": f"Source '{src}' does not exist."}

        shutil.move(s, d)
        return {"success": True, "message": f"Moved '{str(s)}' to '{str(d)}'."}


def register_file_tools():
    tool_registry.register(ListFilesTool())
    tool_registry.register(SearchFilesTool())
    tool_registry.register(CreateFileTool())
    tool_registry.register(ReadFileTool())
    tool_registry.register(DeleteFileTool())
    tool_registry.register(CopyFileTool())
    tool_registry.register(MoveFileTool())


register_file_tools()
