"""
JARVIS Request Orchestrator
Determines user intent and routes processing to chat, tool call execution, or task plan.
"""

import json
import logging
from typing import Dict, Any, Tuple, Optional, List

from ai.model import ai_model
from core.context import context_manager
from core.task_manager import task_manager, TaskPlan, TaskStep
from database.database import db
from tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Core.Orchestrator")


class Orchestrator:
    """Central processing router for user queries."""

    async def process_user_input(
        self, user_text: str, progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Process user input and return result object containing status, message, and tool metadata.
        """
        # Save user message to context history
        context_manager.add_message("user", user_text)

        # 1. Check for multi-step task intent
        if task_manager.is_multi_step_request(user_text):
            plan = self._build_multi_step_plan(user_text)
            if plan:
                if progress_callback:
                    task_manager.set_progress_callback(progress_callback)
                res = await task_manager.execute_plan(plan)
                response_msg = f"Task completed:\n{res.get('summary')}"
                context_manager.add_message("jarvis", response_msg)
                return {
                    "type": "multi_step_task",
                    "response": response_msg,
                    "plan": plan.to_dict(),
                    "success": res.get("success", False),
                }

        # 2. Process query via AI model
        history = context_manager.get_context_history()
        ai_response_text, tool_call = await ai_model.process_user_request(user_text, history=history)

        # 3. Handle single tool execution if returned by AI
        if tool_call:
            tool_name = tool_call["tool"]
            kwargs = tool_call.get("kwargs", {})
            logger.info("Orchestrator executing tool call: %s with args %s", tool_name, kwargs)

            tool_result = await tool_registry.execute_tool(tool_name, kwargs)

            if tool_result.get("success"):
                res_val = tool_result.get("result")
                # Format friendly summary for user
                if isinstance(res_val, dict) and "formatted" in res_val:
                    summary = f"The time is {res_val['formatted']}."
                elif isinstance(res_val, dict) and "message" in res_val:
                    summary = res_val["message"]
                elif isinstance(res_val, dict) and "usage_percent" in res_val:
                    summary = f"CPU usage is currently {res_val['usage_percent']}%."
                elif isinstance(res_val, dict) and "percent" in res_val and "total_gb" in res_val:
                    summary = f"RAM usage is {res_val['percent']}% ({res_val['used_gb']} GB / {res_val['total_gb']} GB)."
                else:
                    summary = f"Action executed successfully: {res_val}"

                context_manager.add_message("jarvis", summary, metadata={"tool": tool_name})
                return {
                    "type": "tool_execution",
                    "response": summary,
                    "tool": tool_name,
                    "tool_result": tool_result,
                    "success": True,
                }
            else:
                err_msg = f"Sorry, action failed: {tool_result.get('error')}"
                context_manager.add_message("jarvis", err_msg)
                return {
                    "type": "tool_execution",
                    "response": err_msg,
                    "tool": tool_name,
                    "tool_result": tool_result,
                    "success": False,
                }

        # 4. Standard conversational response
        context_manager.add_message("jarvis", ai_response_text)
        return {
            "type": "chat",
            "response": ai_response_text,
            "success": True,
        }

    def _build_multi_step_plan(self, user_request: str) -> Optional[TaskPlan]:
        """Creates a TaskPlan object for combined commands."""
        steps: List[TaskStep] = []
        p_lower = user_request.lower()

        idx = 1
        # Check for browser search + note combination
        if "open chrome" in p_lower or "launch chrome" in p_lower or "open browser" in p_lower:
            steps.append(TaskStep(idx, "Opening browser", "open_application", {"app_name": "chrome"}))
            idx += 1

        if "search for" in p_lower or "search" in p_lower:
            q = p_lower.split("search")[-1].replace("the web for", "").replace("for", "").split("and")[0].strip()
            if q:
                steps.append(TaskStep(idx, f"Searching web for '{q}'", "web_search", {"query": q}))
                idx += 1

        if "create a note" in p_lower or "save a note" in p_lower:
            steps.append(
                TaskStep(
                    idx,
                    "Creating note with findings",
                    "create_note",
                    {"title": "Search Findings", "content": f"Results collected for query: {user_request}"},
                )
            )
            idx += 1

        if steps:
            task_id = db.create_task(user_request, [s.to_dict() for s in steps])
            return TaskPlan(task_id, user_request, steps)

        return None


orchestrator = Orchestrator()
