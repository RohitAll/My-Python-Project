"""
Chat History Feed Widget
Displays interactive conversation history with user bubbles, JARVIS answers, and tool cards.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from database.database import db


class ChatWidget(QWidget):
    """Futuristic scrollable chat history view."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Container inside Scroll Area
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.feed_layout = QVBoxLayout(self.container)
        self.feed_layout.setAlignment(Qt.AlignTop)
        self.feed_layout.setSpacing(14)
        self.feed_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

        # Load recent history from database on startup
        self.load_history()

    def load_history(self):
        """Pre-populate chat feed with recent interaction logs."""
        recent_logs = db.get_recent_history(limit=20)
        for log in recent_logs:
            role = log["role"]
            content = log["content"]
            if role == "user":
                self.add_user_message(content, log_db=False)
            elif role == "jarvis":
                self.add_jarvis_message(content, log_db=False)

    def add_user_message(self, text: str, log_db: bool = True):
        """Append user message bubble."""
        row_layout = QHBoxLayout()
        row_layout.addStretch()

        bubble = QFrame()
        bubble.setStyleSheet(
            "background-color: rgba(30, 41, 59, 0.85); "
            "border: 1px solid rgba(59, 130, 246, 0.5); "
            "border-radius: 12px; padding: 10px 14px;"
        )
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(8, 6, 8, 6)

        sender_lbl = QLabel("YOU")
        sender_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #60A5FA;")
        b_layout.addWidget(sender_lbl)

        txt_lbl = QLabel(text)
        txt_lbl.setWordWrap(True)
        txt_lbl.setStyleSheet("font-size: 13px; color: #F8FAFC;")
        b_layout.addWidget(txt_lbl)

        row_layout.addWidget(bubble)
        self.feed_layout.addLayout(row_layout)
        self._scroll_to_bottom()

    def add_jarvis_message(self, text: str, tool_name: str = None, log_db: bool = True):
        """Append JARVIS response bubble."""
        row_layout = QHBoxLayout()

        bubble = QFrame()
        bubble.setStyleSheet(
            "background-color: rgba(15, 23, 42, 0.85); "
            "border: 1px solid rgba(0, 240, 255, 0.4); "
            "border-radius: 12px; padding: 10px 14px;"
        )
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(8, 6, 8, 6)

        header_str = f"JARVIS // {tool_name.upper()}" if tool_name else "JARVIS"
        sender_lbl = QLabel(header_str)
        sender_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #00F0FF;")
        b_layout.addWidget(sender_lbl)

        txt_lbl = QLabel(text)
        txt_lbl.setWordWrap(True)
        txt_lbl.setStyleSheet("font-size: 13px; color: #E2E8F0;")
        b_layout.addWidget(txt_lbl)

        row_layout.addWidget(bubble)
        row_layout.addStretch()
        self.feed_layout.addLayout(row_layout)
        self._scroll_to_bottom()

    def add_system_notification(self, title: str, text: str):
        """Append system alert notification card."""
        card = QFrame()
        card.setStyleSheet(
            "background-color: rgba(245, 158, 11, 0.1); "
            "border: 1px dashed #F59E0B; border-radius: 8px; padding: 8px 12px;"
        )
        layout = QVBoxLayout(card)
        t_lbl = QLabel(f"⚡ SYSTEM: {title}")
        t_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #F59E0B;")
        layout.addWidget(t_lbl)

        m_lbl = QLabel(text)
        m_lbl.setWordWrap(True)
        m_lbl.setStyleSheet("font-size: 12px; color: #CBD5E1;")
        layout.addWidget(m_lbl)

        self.feed_layout.addWidget(card)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
