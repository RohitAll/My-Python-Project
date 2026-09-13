"""
Modular Tool System Registry
Provides base tool interface, schema generation for LLM tool calling, and tool execution orchestration.
"""

import abc
import logging
import inspect
from typing import Dict, Any, Type, List, Optional
from security.confirmations import confirmation_manager

logger = logging.getLogger("JARVIS.Tools")


class BaseTool(abc.ABC):
    """Abstract base class for all JARVIS tools."""

    name: str
    description: str
    parameters: Dict[str, Any]

    @abc.abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool logic asynchronously."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Returns JSON schema representation for OpenAI / Gemini function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Registry managing all available JARVIS tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_instance: BaseTool):
        """Register a tool instance."""
        if not hasattr(tool_instance, "name") or not tool_instance.name:
            raise ValueError(f"Tool {tool_instance} must have a valid 'name' attribute.")
        self._tools[tool_instance.name] = tool_instance
        logger.debug("Registered tool: %s", tool_instance.name)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """Return list of all registered tools."""
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return function calling schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a registered tool with security confirmation check and error handling.
        """
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found."}

        # Security check
        approved = await confirmation_manager.request_confirmation(name, kwargs)
        if not approved:
            return {
                "success": False,
                "error": f"Action '{name}' was cancelled by the user for security reasons.",
            }

        try:
            logger.info("Executing tool: %s with args: %s", name, kwargs)
            if inspect.iscoroutinefunction(tool.execute):
                result = await tool.execute(**kwargs)
            else:
                result = tool.execute(**kwargs)

            return {"success": True, "result": result}
        except Exception as e:
            logger.error("Error executing tool '%s': %s", name, e, exc_info=True)
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}


tool_registry = ToolRegistry()
