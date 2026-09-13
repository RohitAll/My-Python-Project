"""
Asynchronous Confirmation Manager for Safety Verification
Bridging tool execution requests with PySide6 interactive UI modal confirmation dialogs.
"""

import asyncio
import logging
from typing import Optional, Callable
from security.permissions import RiskLevel, security_checker
from config.settings import settings

logger = logging.getLogger("JARVIS.Security")


class ConfirmationManager:
    """Handles runtime safety approval requests from tools before execution."""

    def __init__(self):
        self._gui_callback: Optional[Callable] = None

    def set_gui_callback(self, callback: Callable):
        """Register the PySide6 UI modal dialog handler callback."""
        self._gui_callback = callback

    async def request_confirmation(self, tool_name: str, kwargs: dict) -> bool:
        """
        Evaluates risk and prompts for user confirmation if action is high risk or dangerous.
        """
        risk_level, message = security_checker.evaluate_action(tool_name, kwargs)

        logger.info("Security Evaluation: Tool='%s', Risk='%s', Message='%s'", tool_name, risk_level.value, message)

        # If confirmation is disabled in settings or low risk auto-approved
        if not settings.REQUIRE_CONFIRMATION_FOR_DESTRUCTIVE:
            return True

        if risk_level == RiskLevel.LOW or (risk_level == RiskLevel.MEDIUM and settings.AUTO_APPROVE_LOW_RISK):
            return True

        # Require explicit user confirmation for HIGH and DANGEROUS actions
        if self._gui_callback is None:
            logger.warning("No GUI confirmation callback attached. Denying high-risk action: %s", message)
            return False

        try:
            # Trigger async confirmation on GUI thread
            is_approved = await self._gui_callback(tool_name, risk_level.value, message, kwargs)
            logger.info("User confirmation response for %s: %s", tool_name, is_approved)
            return is_approved
        except Exception as e:
            logger.error("Error during security confirmation request: %s", e)
            return False


confirmation_manager = ConfirmationManager()
