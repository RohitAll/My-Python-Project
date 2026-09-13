"""
Application Control Tools
Supports opening, launching, focusing, and closing applications on Windows.
"""

import os
import subprocess
import psutil
import logging
from typing import Dict, Any, Optional

from tools.registry import BaseTool, tool_registry

logger = logging.getLogger("JARVIS.Tools.Applications")

# Common application aliases on Windows
COMMON_APPS = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "browser": "chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "vs code": "code",
    "vscode": "code",
    "code": "code",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
}


class OpenApplicationTool(BaseTool):
    name = "open_application"
    description = "Launch or open a desktop application by name or path."
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name or alias of the application to open (e.g. 'chrome', 'notepad', 'code', 'calculator').",
            }
        },
        "required": ["app_name"],
    }

    async def execute(self, app_name: str, **kwargs) -> Dict[str, Any]:
        app_lower = app_name.lower().strip()
        target = COMMON_APPS.get(app_lower, app_name)

        try:
            # Try launching using os.startfile on Windows
            os.startfile(target)
            return {"success": True, "message": f"Successfully launched '{app_name}'."}
        except Exception:
            try:
                # Fallback to subprocess Popen
                subprocess.Popen(target, shell=True)
                return {"success": True, "message": f"Launched '{app_name}' via command shell."}
            except Exception as e:
                return {"success": False, "error": f"Could not launch '{app_name}': {str(e)}"}


class CloseApplicationTool(BaseTool):
    name = "close_application"
    description = "Close or terminate a running application process by name."
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of process or application to terminate (e.g. 'chrome', 'notepad', 'code').",
            }
        },
        "required": ["app_name"],
    }

    async def execute(self, app_name: str, **kwargs) -> Dict[str, Any]:
        target = app_name.lower().replace(".exe", "")
        closed_count = 0

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info["name"].lower().replace(".exe", "")
                if target in pname:
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            return {"success": True, "message": f"Terminated {closed_count} process(es) matching '{app_name}'."}
        else:
            return {"success": False, "error": f"No running application processes matching '{app_name}' were found."}


class FocusApplicationTool(BaseTool):
    name = "focus_application"
    description = "Bring a running application window to the foreground."
    parameters = {
        "type": "object",
        "properties": {
            "window_title": {
                "type": "string",
                "description": "Title or partial name of the target application window.",
            }
        },
        "required": ["window_title"],
    }

    async def execute(self, window_title: str, **kwargs) -> Dict[str, Any]:
        try:
            import pygetwindow as gw

            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                return {"success": True, "message": f"Focused window: '{win.title}'"}
            return {"success": False, "error": f"No active window found matching title '{window_title}'."}
        except Exception as e:
            return {"success": False, "error": f"Focus window error: {str(e)}"}


def register_application_tools():
    tool_registry.register(OpenApplicationTool())
    tool_registry.register(CloseApplicationTool())
    tool_registry.register(FocusApplicationTool())


register_application_tools()
