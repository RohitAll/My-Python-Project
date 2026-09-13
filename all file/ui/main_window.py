"""
JARVIS Desktop Assistant Main Window
Assembles header, animated AI orb, chat feed, input controls, side panel, and safety dialogs.
"""

import asyncio
import logging
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFrame,
    QApplication,
)
from PySide6.QtCore import Qt, QThread, Signal, Slot

from config.settings import settings
from ui.styles.theme import DARK_FUTURISTIC_QSS
from ui.components.header_widget import HeaderWidget
from ui.components.orb_widget import OrbWidget
from ui.components.chat_widget import ChatWidget
from ui.components.side_panel import SidePanelWidget
from ui.components.confirmation_dialog import ConfirmationDialog
from core.assistant import jarvis_assistant, AssistantState
from security.confirmations import confirmation_manager

logger = logging.getLogger("JARVIS.UI.MainWindow")


class AsyncWorker(QThread):
    """Worker thread for running async coroutines without blocking PySide6 GUI loop."""

    result_signal = Signal(dict)

    def __init__(self, coro_func, *args):
        super().__init__()
        self.coro_func = coro_func
        self.args = args

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            res = loop.run_until_complete(self.coro_func(*self.args))
            if isinstance(res, dict):
                self.result_signal.emit(res)
        finally:
            loop.close()


class MainWindow(QMainWindow):
    """Primary JARVIS Desktop Assistant GUI Window."""

    confirmation_signal = Signal(str, str, str, dict, object)
    response_signal = Signal(dict)
    state_signal = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS // PERSONAL AI ASSISTANT")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        # Apply QSS Theme
        self.setStyleSheet(DARK_FUTURISTIC_QSS)

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Header Widget
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # 2. Main Content Splitter Row
        content_row = QHBoxLayout()
        content_row.setContentsMargins(15, 15, 15, 15)
        content_row.setSpacing(15)

        # Left Column: Orb + Chat Area
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        # Center Orb Container
        orb_container = QFrame()
        orb_container.setObjectName("glassPanel")
        orb_container.setFixedHeight(210)
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setContentsMargins(0, 0, 0, 0)

        self.orb = OrbWidget()
        orb_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        left_col.addWidget(orb_container)

        # Chat Feed Container
        chat_container = QFrame()
        chat_container.setObjectName("glassPanel")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_feed = ChatWidget()
        chat_layout.addWidget(self.chat_feed)

        # Bottom Input Controls Bar
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.text_input = QLineEdit()
        self.text_input.setObjectName("chatInput")
        self.text_input.setPlaceholderText("Ask JARVIS anything or enter a command...")
        self.text_input.returnPressed.connect(self._on_send_clicked)
        input_row.addWidget(self.text_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("primaryBtn")
        self.send_btn.setFixedSize(85, 38)
        self.send_btn.clicked.connect(self._on_send_clicked)
        input_row.addWidget(self.send_btn)

        self.mic_btn = QPushButton("🎙")
        self.mic_btn.setObjectName("iconBtn")
        self.mic_btn.setFixedSize(38, 38)
        self.mic_btn.setToolTip("Toggle Voice Listening")
        self.mic_btn.clicked.connect(self._on_mic_clicked)
        input_row.addWidget(self.mic_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedSize(70, 38)
        self.stop_btn.setToolTip("Stop speech or current action")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        input_row.addWidget(self.stop_btn)

        chat_layout.addLayout(input_row)
        left_col.addWidget(chat_container, stretch=1)

        content_row.addLayout(left_col, stretch=2)

        # Right Column: Side Dashboard Panel
        self.side_panel = SidePanelWidget()
        content_row.addWidget(self.side_panel, stretch=1)

        main_layout.addLayout(content_row)

        # Connect Qt Signals to Slots on Main Thread
        self.response_signal.connect(self._on_assistant_response_slot)
        self.state_signal.connect(self._on_assistant_state_change_slot)
        self.confirmation_signal.connect(self._show_confirmation_dialog_slot)

        # Attach Assistant Engine Callbacks
        jarvis_assistant.register_callbacks(
            state_callback=self._on_assistant_state_change,
            response_callback=self._on_assistant_response,
        )

        # Attach Security Confirmation Callback Bridge
        confirmation_manager.set_gui_callback(self._request_gui_confirmation)

        # Initialize Wake Word Listener
        jarvis_assistant.init_wake_word()

    def _on_send_clicked(self):
        text = self.text_input.text().strip()
        if not text:
            return

        self.text_input.clear()
        self.chat_feed.add_user_message(text)

        # Launch command processing on worker thread
        self.worker = AsyncWorker(jarvis_assistant.handle_text_command, text)
        self.worker.start()

    def _on_mic_clicked(self):
        self.header.set_mic_active(True)
        self.mic_worker = AsyncWorker(jarvis_assistant.start_listening_voice)
        self.mic_worker.start()

    def _on_stop_clicked(self):
        jarvis_assistant.set_state(AssistantState.IDLE)
        self.header.set_mic_active(False)
        self.chat_feed.add_system_notification("ACTION STOPPED", "Operation cancelled by user.")

    def _on_assistant_state_change(self, state: AssistantState):
        """Thread-safe signal emission to Qt main thread."""
        self.state_signal.emit(state)

    def _on_assistant_response(self, result: dict):
        """Thread-safe signal emission to Qt main thread."""
        self.response_signal.emit(result)

    @Slot(object)
    def _on_assistant_state_change_slot(self, state: AssistantState):
        """Update orb state on PySide6 main thread."""
        self.orb.set_state(state)
        if state != AssistantState.LISTENING:
            self.header.set_mic_active(False)

    @Slot(dict)
    def _on_assistant_response_slot(self, result: dict):
        """Append assistant response to chat feed on main Qt thread."""
        response_text = result.get("response", "")
        tool_name = result.get("tool")
        if response_text:
            self.chat_feed.add_jarvis_message(response_text, tool_name=tool_name)
            self.side_panel.refresh_memory()

    async def _request_gui_confirmation(self, tool_name: str, risk_level: str, message: str, kwargs: dict) -> bool:
        """Async bridge method called by tool execution layer."""
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        self.confirmation_signal.emit(tool_name, risk_level, message, kwargs, future)
        return await future

    @Slot(str, str, str, dict, object)
    def _show_confirmation_dialog_slot(self, tool_name: str, risk_level: str, message: str, kwargs: dict, future: object):
        """Displays modal dialog on main Qt thread."""
        dialog = ConfirmationDialog(tool_name, risk_level, message, self)
        res = dialog.exec_()
        is_approved = (res == ConfirmationDialog.Accepted)
        future.get_loop().call_soon_threadsafe(future.set_result, is_approved)
