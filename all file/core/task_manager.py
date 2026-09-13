"""
Multi-Step Task Execution Manager
Decomposes complex requests into task plans, executes steps, tracks progress, and updates GUI.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable

from database.database import db
from tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Core.TaskManager")


class TaskStep:
    def __init__(self, step_index: int, description: str, tool: str, kwargs: dict):
        self.step_index = step_index
        self.description = description
        self.tool = tool
        self.kwargs = kwargs
        self.status = "pending"  # pending, executing, completed, failed
        self.result = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "description": self.description,
            "tool": self.tool,
            "kwargs": self.kwargs,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


class TaskPlan:
    def __init__(self, task_id: int, title: str, steps: List[TaskStep]):
        self.task_id = task_id
        self.title = title
        self.steps = steps
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
        }


class TaskManager:
    """Manages creation, step execution, and monitoring of multi-step task plans."""

    def __init__(self):
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """Set GUI callback to receive live task progress updates."""
        self._progress_callback = callback

    def _notify(self, plan: TaskPlan, current_step: Optional[TaskStep] = None):
        if self._progress_callback:
            try:
                self._progress_callback(plan.to_dict(), current_step.to_dict() if current_step else None)
            except Exception as e:
                logger.error("Error in task progress notification callback: %s", e)

    async def execute_plan(self, plan: TaskPlan) -> Dict[str, Any]:
        """Execute a multi-step task plan sequentially."""
        logger.info("Starting execution of task plan #%d: '%s'", plan.task_id, plan.title)
        plan.status = "executing"
        db.update_task_status(plan.task_id, "executing", [s.to_dict() for s in plan.steps])
        self._notify(plan)

        final_summary = []

        for step in plan.steps:
            step.status = "executing"
            logger.info("Executing Task #%d Step %d: %s", plan.task_id, step.step_index, step.description)
            self._notify(plan, step)

            # Execute step tool
            tool_res = await tool_registry.execute_tool(step.tool, step.kwargs)

            if tool_res.get("success"):
                step.status = "completed"
                step.result = tool_res.get("result")
                final_summary.append(f"✓ {step.description}: {tool_res.get('result', 'Done')}")
            else:
                step.status = "failed"
                step.error = tool_res.get("error", "Unknown error")
                final_summary.append(f"✗ {step.description} failed: {step.error}")
                plan.status = "failed"
                db.update_task_status(plan.task_id, "failed", [s.to_dict() for s in plan.steps])
                self._notify(plan, step)
                return {
                    "success": False,
                    "task_id": plan.task_id,
                    "summary": "\n".join(final_summary),
                    "failed_step": step.to_dict(),
                }

            db.update_task_status(plan.task_id, "executing", [s.to_dict() for s in plan.steps])
            self._notify(plan, step)
            await asyncio.sleep(0.3)

        plan.status = "completed"
        db.update_task_status(plan.task_id, "completed", [s.to_dict() for s in plan.steps])
        self._notify(plan)

        return {
            "success": True,
            "task_id": plan.task_id,
            "summary": "\n".join(final_summary),
        }

    def is_multi_step_request(self, user_request: str) -> bool:
        """Heuristic check whether user request contains multiple combined commands."""
        req_lower = user_request.lower()
        triggers = [" then ", " and then ", " and create ", " and search ", " and save ", " and open "]
        return any(trig in req_lower for trig in triggers) or user_request.count(",") >= 2


task_manager = TaskManager()
