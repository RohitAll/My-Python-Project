"""
Developer Tools Subsystem
Supports code creation, code reading, code explanation, and safe script execution.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any

from tools.registry import BaseTool, tool_registry


class CreateCodeFileTool(BaseTool):
    name = "create_code_file"
    description = "Create or write a source code file (Python, JS, HTML, C++, etc.)."
    parameters = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string", "description": "Target source code file path."},
            "code": {"type": "string", "description": "Source code content to write."},
        },
        "required": ["filepath", "code"],
    }

    async def execute(self, filepath: str, code: str, **kwargs) -> Dict[str, Any]:
        p = Path(filepath).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code, encoding="utf-8")
        return {"success": True, "message": f"Source code file created at: '{str(p)}'"}


class ExplainCodeTool(BaseTool):
    name = "explain_code"
    description = "Analyze and summarize a code snippet or source file."
    parameters = {
        "type": "object",
        "properties": {
            "code_or_path": {"type": "string", "description": "Source code text or file path to analyze."}
        },
        "required": ["code_or_path"],
    }

    async def execute(self, code_or_path: str, **kwargs) -> Dict[str, Any]:
        p = Path(code_or_path)
        if p.exists() and p.is_file():
            code_text = p.read_text(encoding="utf-8", errors="replace")
            source = str(p)
        else:
            code_text = code_or_path
            source = "provided snippet"

        lines = code_text.splitlines()
        return {
            "success": True,
            "source": source,
            "total_lines": len(lines),
            "summary": f"Code file with {len(lines)} lines of source code.",
            "preview": "\n".join(lines[:30]),
        }


class RunSafeScriptTool(BaseTool):
    name = "run_safe_script"
    description = "Run a Python or Shell script with output capturing."
    parameters = {
        "type": "object",
        "properties": {
            "script_path": {"type": "string", "description": "Path to Python (.py) or Script file to execute."}
        },
        "required": ["script_path"],
    }

    async def execute(self, script_path: str, **kwargs) -> Dict[str, Any]:
        p = Path(script_path).resolve()
        if not p.exists():
            return {"success": False, "error": f"Script file '{script_path}' not found."}

        try:
            res = subprocess.run(
                ["python", str(p)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout[:2000],
                "stderr": res.stderr[:1000],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Script execution timed out after 15 seconds."}
        except Exception as e:
            return {"success": False, "error": f"Script execution error: {str(e)}"}


def register_developer_tools():
    tool_registry.register(CreateCodeFileTool())
    tool_registry.register(ExplainCodeTool())
    tool_registry.register(RunSafeScriptTool())


register_developer_tools()
