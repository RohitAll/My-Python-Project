"""
Computer Control Subsystem
Allows safe interaction with mouse, keyboard, and hotkeys using PyAutoGUI.
"""

import logging
from typing import Dict, Any, List

from tools.registry import BaseTool, tool_registry

logger = logging.getLogger("JARVIS.Tools.Computer")


class MouseClickTool(BaseTool):
    name = "mouse_click"
    description = "Perform a mouse click at specified (x, y) screen coordinates."
    parameters = {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "X coordinate on screen."},
            "y": {"type": "integer", "description": "Y coordinate on screen."},
            "button": {"type": "string", "description": "'left', 'right', or 'middle' (default 'left')."},
        },
        "required": ["x", "y"],
    }

    async def execute(self, x: int, y: int, button: str = "left", **kwargs) -> Dict[str, Any]:
        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            pyautogui.click(x=x, y=y, button=button)
            return {"success": True, "message": f"Clicked mouse {button} button at ({x}, {y})."}
        except Exception as e:
            return {"success": False, "error": f"Mouse click error: {str(e)}"}


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "Type text characters sequentially into the active desktop window."
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text string to type out."},
            "interval": {"type": "number", "description": "Delay between keypresses in seconds (default 0.05)."},
        },
        "required": ["text"],
    }

    async def execute(self, text: str, interval: float = 0.05, **kwargs) -> Dict[str, Any]:
        try:
            import pyautogui

            pyautogui.typewrite(text, interval=interval)
            return {"success": True, "message": f"Typed text ({len(text)} characters)."}
        except Exception as e:
            return {"success": False, "error": f"Type text error: {str(e)}"}


class PressKeyTool(BaseTool):
    name = "press_key"
    description = "Press a specific keyboard key (e.g. 'enter', 'tab', 'escape', 'space')."
    parameters = {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Keyboard key name."},
        },
        "required": ["key"],
    }

    async def execute(self, key: str, **kwargs) -> Dict[str, Any]:
        try:
            import pyautogui

            pyautogui.press(key)
            return {"success": True, "message": f"Pressed key '{key}'."}
        except Exception as e:
            return {"success": False, "error": f"Press key error: {str(e)}"}


class HotkeyTool(BaseTool):
    name = "hotkey"
    description = "Execute a keyboard shortcut combination (e.g. ['ctrl', 'c'], ['alt', 'tab']).' "
    parameters = {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key names to press in sequence (e.g. ['ctrl', 's']).",
            }
        },
        "required": ["keys"],
    }

    async def execute(self, keys: List[str], **kwargs) -> Dict[str, Any]:
        try:
            import pyautogui

            pyautogui.hotkey(*keys)
            return {"success": True, "message": f"Pressed hotkey shortcut: {keys}."}
        except Exception as e:
            return {"success": False, "error": f"Hotkey error: {str(e)}"}


def register_computer_tools():
    tool_registry.register(MouseClickTool())
    tool_registry.register(TypeTextTool())
    tool_registry.register(PressKeyTool())
    tool_registry.register(HotkeyTool())


register_computer_tools()
