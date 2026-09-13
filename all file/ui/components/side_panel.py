"""
Side Panel Dashboard Component
Displays system hardware monitors, multi-step task tracker, memory inspector, and tool registry.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer
import psutil
from tools.registry import tool_registry
from memory.memory_manager import memory_manager
from database.database import db


class SidePanelWidget(QFrame):
    """Futuristic side panel displaying diagnostics, tasks, memory, and tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassPanel")
        self.setMinimumWidth(280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("SYSTEM DASHBOARD")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #00F0FF; letter-spacing: 1px;")
        main_layout.addWidget(title)

        # Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: System Info
        self.sys_tab = QWidget()
        self._build_sys_tab()
        self.tabs.addTab(self.sys_tab, "STATS")

        # Tab 2: Task Execution Plan
        self.tasks_tab = QWidget()
        self._build_tasks_tab()
        self.tabs.addTab(self.tasks_tab, "TASKS")

        # Tab 3: Memory Inspector
        self.memory_tab = QWidget()
        self._build_memory_tab()
        self.tabs.addTab(self.memory_tab, "MEMORY")

        # Tab 4: Tools
        self.tools_tab = QWidget()
        self._build_tools_tab()
        self.tabs.addTab(self.tools_tab, "TOOLS")

        # Metrics refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(2000)
        self._update_metrics()

    def _build_sys_tab(self):
        layout = QVBoxLayout(self.sys_tab)

        # CPU Progress Bar
        layout.addWidget(QLabel("CPU USAGE:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet("QProgressBar { border: 1px solid #334155; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #00F0FF; }")
        layout.addWidget(self.cpu_bar)

        # RAM Progress Bar
        layout.addWidget(QLabel("RAM USAGE:"))
        self.ram_bar = QProgressBar()
        self.ram_bar.setStyleSheet("QProgressBar { border: 1px solid #334155; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #6366F1; }")
        layout.addWidget(self.ram_bar)

        # Disk Progress Bar
        layout.addWidget(QLabel("DISK STORAGE:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setStyleSheet("QProgressBar { border: 1px solid #334155; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #10B981; }")
        layout.addWidget(self.disk_bar)

        layout.addStretch()

    def _build_tasks_tab(self):
        layout = QVBoxLayout(self.tasks_tab)
        self.tasks_list = QListWidget()
        self.tasks_list.setStyleSheet("background: transparent; border: none; font-size: 12px;")
        layout.addWidget(self.tasks_list)
        self.refresh_tasks()

    def _build_memory_tab(self):
        layout = QVBoxLayout(self.memory_tab)
        self.memory_list = QListWidget()
        self.memory_list.setStyleSheet("background: transparent; border: none; font-size: 12px;")
        layout.addWidget(self.memory_list)
        self.refresh_memory()

    def _build_tools_tab(self):
        layout = QVBoxLayout(self.tools_tab)
        self.tools_list = QListWidget()
        self.tools_list.setStyleSheet("background: transparent; border: none; font-size: 12px;")
        layout.addWidget(self.tools_list)

        # Load tools
        for tool in tool_registry.list_tools():
            item = QListWidgetItem(f"⚡ {tool.name}")
            item.setToolTip(tool.description)
            self.tools_list.addItem(item)

    def _update_metrics(self):
        cpu = int(psutil.cpu_percent())
        ram = int(psutil.virtual_memory().percent)
        disk = int(psutil.disk_usage("/").percent)

        self.cpu_bar.setValue(cpu)
        self.ram_bar.setValue(ram)
        self.disk_bar.setValue(disk)

    def refresh_tasks(self, plan_dict: dict = None):
        """Refresh current task list display."""
        self.tasks_list.clear()
        if plan_dict:
            title_item = QListWidgetItem(f"PLAN: {plan_dict.get('title')}")
            title_item.setForeground(Qt.cyan)
            self.tasks_list.addItem(title_item)

            for s in plan_dict.get("steps", []):
                st = s.get("status")
                icon = "✓" if st == "completed" else "→" if st == "executing" else "✗" if st == "failed" else "•"
                item = QListWidgetItem(f"  {icon} Step {s['step_index']}: {s['description']}")
                self.tasks_list.addItem(item)

    def refresh_memory(self):
        """Refresh memory entries list."""
        self.memory_list.clear()
        memories = memory_manager.recall("")
        for m in memories:
            item = QListWidgetItem(f"• {m['key_term']}: {m['value']}")
            self.memory_list.addItem(item)
