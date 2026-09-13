"""
Unit Tests for Persistent Memory System
"""

import pytest
from memory.memory_manager import memory_manager


def test_memory_remember_and_recall():
    res = memory_manager.remember(key_term="test_editor", value="VS Code Test", category="preference")
    assert res["success"] is True

    memories = memory_manager.recall("test_editor")
    assert len(memories) > 0
    assert any(m["key_term"] == "test_editor" for m in memories)


def test_memory_forget():
    memory_manager.remember(key_term="temporary_fact", value="to be deleted")
    fres = memory_manager.forget("temporary_fact")
    assert fres["success"] is True
