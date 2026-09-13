"""
Unit Tests for Tool Registry and Individual Tool Execution
"""

import pytest
import asyncio
from tools.registry import tool_registry, BaseTool
from tools.system import GetCpuUsageTool, GetCurrentTimeTool
from tools.files import CreateFileTool, ReadFileTool, DeleteFileTool


@pytest.mark.asyncio
async def test_tool_registry_registration():
    class DummyTool(BaseTool):
        name = "dummy_tool"
        description = "Test tool"
        parameters = {"type": "object", "properties": {}, "required": []}

        async def execute(self, **kwargs):
            return "dummy_result"

    t = DummyTool()
    tool_registry.register(t)
    assert tool_registry.get_tool("dummy_tool") is not None
    assert tool_registry.get_tool("dummy_tool").name == "dummy_tool"


@pytest.mark.asyncio
async def test_system_tools():
    cpu_tool = GetCpuUsageTool()
    res = await cpu_tool.execute()
    assert "usage_percent" in res

    time_tool = GetCurrentTimeTool()
    tres = await time_tool.execute()
    assert "formatted" in tres


@pytest.mark.asyncio
async def test_file_tools(tmp_path):
    test_file = tmp_path / "test_notes.txt"
    content = "Hello JARVIS test file"

    create_tool = CreateFileTool()
    cres = await create_tool.execute(filepath=str(test_file), content=content)
    assert cres["success"] is True

    read_tool = ReadFileTool()
    rres = await read_tool.execute(filepath=str(test_file))
    assert rres["success"] is True
    assert content in rres["content"]

    del_tool = DeleteFileTool()
    dres = await del_tool.execute(filepath=str(test_file))
    assert dres["success"] is True
