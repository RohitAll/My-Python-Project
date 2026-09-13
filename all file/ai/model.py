"""
AI Model Orchestration Dispatcher
Handles prompt construction, provider query, and JSON tool response parsing.
"""

import json
import logging
import re
from typing import Dict, Any, Tuple, Optional, List

from ai.provider import get_llm_provider
from ai.prompts import JARVIS_SYSTEM_PROMPT
from tools.registry import tool_registry
from memory.memory_manager import memory_manager

logger = logging.getLogger("JARVIS.AI.Model")


class AIModel:
    """Orchestrates natural language processing and tool call extraction."""

    def __init__(self):
        self.provider = get_llm_provider()

    def reload_provider(self):
        """Reload LLM provider instance."""
        self.provider = get_llm_provider()

    async def process_user_request(
        self, user_text: str, history: List[Dict[str, str]] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process user text, returning (text_response, tool_call_dict).
        """
        # Fetch relevant memories to inject into prompt context
        memories = memory_manager.recall(user_text)
        mem_str = json.dumps(memories, indent=2) if memories else "No relevant memories found."

        # Fetch tools schema
        tools_schema = json.dumps(tool_registry.get_schemas(), indent=2)

        system_prompt = JARVIS_SYSTEM_PROMPT.format(
            tools_schema=tools_schema,
            user_memories=mem_str,
        )

        try:
            raw_response = await self.provider.generate_response(
                prompt=user_text,
                system_prompt=system_prompt,
                history=history,
            )

            # Check if response contains a tool execution request JSON
            tool_call = self._extract_tool_call(raw_response)
            if tool_call:
                return f"Executing action: {tool_call.get('tool')}", tool_call

            return raw_response, None
        except Exception as e:
            logger.error("AI Model processing error: %s", e)
            # Fallback attempt using offline engine if primary provider failed
            try:
                from ai.provider import OfflineFallbackProvider

                fallback = OfflineFallbackProvider()
                raw_response = await fallback.generate_response(user_text, system_prompt, history)
                tool_call = self._extract_tool_call(raw_response)
                if tool_call:
                    return f"Executing action: {tool_call.get('tool')}", tool_call
                return raw_response, None
            except Exception as fb_err:
                return f"I encountered an error processing your request: {str(e)}", None

    def _extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parses response string looking for valid tool call JSON."""
        if not text:
            return None

        # Clean code blocks
        clean_text = text.strip()
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(clean_text)
            if isinstance(data, dict) and "tool" in data:
                return {
                    "tool": data["tool"],
                    "kwargs": data.get("kwargs", {}),
                }
        except json.JSONDecodeError:
            # Try regex matching for tool json pattern
            match = re.search(r'\{\s*"tool"\s*:\s*"([^"]+)"\s*(?:,\s*"kwargs"\s*:\s*(\{.*?\}))?\s*\}', text, re.DOTALL)
            if match:
                tool_name = match.group(1)
                kwargs_str = match.group(2) or "{}"
                try:
                    kwargs = json.loads(kwargs_str)
                    return {"tool": tool_name, "kwargs": kwargs}
                except Exception:
                    pass

        return None


ai_model = AIModel()
