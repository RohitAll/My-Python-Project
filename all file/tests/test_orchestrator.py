"""
Unit Tests for Request Orchestration Engine
"""

import pytest
from core.orchestrator import orchestrator


@pytest.mark.asyncio
async def test_offline_orchestrator_routing():
    # Test CPU usage command
    res = await orchestrator.process_user_input("What is my CPU usage?")
    assert res["success"] is True
    assert "CPU" in res["response"] or "usage" in res["response"]

    # Test time command
    tres = await orchestrator.process_user_input("Tell me the current time")
    assert tres["success"] is True

    # Test memory command
    mres = await orchestrator.process_user_input("Remember that my preferred editor is VS Code")
    assert mres["success"] is True
