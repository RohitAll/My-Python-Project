"""
Security Risk Level Definitions and Action Evaluation System
Categories actions by risk level to enforce safety checks before tool execution.
"""

from enum import Enum
from typing import Dict, Any, Tuple


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    DANGEROUS = "DANGEROUS"


# Map tool names and actions to default risk levels
TOOL_RISK_MAPPING: Dict[str, RiskLevel] = {
    "get_system_info": RiskLevel.LOW,
    "get_cpu_usage": RiskLevel.LOW,
    "get_ram_usage": RiskLevel.LOW,
    "get_disk_usage": RiskLevel.LOW,
    "get_battery_status": RiskLevel.LOW,
    "get_current_time": RiskLevel.LOW,
    "get_network_info": RiskLevel.LOW,
    "web_search": RiskLevel.LOW,
    "open_website": RiskLevel.LOW,
    "read_file": RiskLevel.LOW,
    "list_files": RiskLevel.LOW,
    "search_files": RiskLevel.LOW,
    "create_note": RiskLevel.LOW,
    "get_notes": RiskLevel.LOW,
    "remember_fact": RiskLevel.LOW,
    "get_memories": RiskLevel.LOW,
    "open_application": RiskLevel.MEDIUM,
    "close_application": RiskLevel.MEDIUM,
    "focus_application": RiskLevel.MEDIUM,
    "create_file": RiskLevel.MEDIUM,
    "rename_file": RiskLevel.MEDIUM,
    "copy_file": RiskLevel.MEDIUM,
    "move_file": RiskLevel.MEDIUM,
    "mouse_click": RiskLevel.MEDIUM,
    "type_text": RiskLevel.MEDIUM,
    "press_key": RiskLevel.MEDIUM,
    "create_code_file": RiskLevel.MEDIUM,
    "explain_code": RiskLevel.LOW,
    "run_safe_script": RiskLevel.HIGH,
    "delete_file": RiskLevel.DANGEROUS,
    "delete_memory": RiskLevel.HIGH,
    "run_command": RiskLevel.DANGEROUS,
}


class SecurityChecker:
    """Evaluates requested tool executions against safety policies."""

    @staticmethod
    def evaluate_action(tool_name: str, kwargs: Dict[str, Any]) -> Tuple[RiskLevel, str]:
        """
        Determines the risk level and description for a tool execution request.
        """
        base_risk = TOOL_RISK_MAPPING.get(tool_name, RiskLevel.MEDIUM)

        # Dynamic risk assessment based on parameters
        if tool_name == "delete_file":
            filepath = kwargs.get("filepath", "target file")
            return RiskLevel.DANGEROUS, f"Deleting file/folder '{filepath}' permanently removes data."

        if tool_name == "run_command" or tool_name == "run_safe_script":
            cmd = kwargs.get("command", kwargs.get("script_path", "unknown command"))
            return RiskLevel.DANGEROUS, f"Executing shell command: '{cmd}'"

        if tool_name == "move_file" or tool_name == "rename_file":
            src = kwargs.get("src", kwargs.get("filepath", "file"))
            dst = kwargs.get("dst", kwargs.get("new_name", "target"))
            return RiskLevel.HIGH, f"Moving or renaming '{src}' to '{dst}'."

        if tool_name == "create_file" and kwargs.get("overwrite", False):
            filepath = kwargs.get("filepath", "target file")
            return RiskLevel.HIGH, f"Overwriting existing file '{filepath}'."

        return base_risk, f"Executing tool '{tool_name}'"


security_checker = SecurityChecker()
