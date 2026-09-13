"""
Header Widget Component
Displays logo, live digital clock, mic state, AI provider badge, and status indicators.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QTime
from config.settings import settings


class HeaderWidget(QFrame):
    """Futuristic top header panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassHeader")
        self.setFixedHeight(65)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        # 1. JARVIS Logo & Title
        self.logo_label = QLabel("JARVIS // PERSONAL AI ASSISTANT")
        self.logo_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00F0FF; letter-spacing: 1px;")
        layout.addWidget(self.logo_label)

        layout.addStretch()

        # 2. AI Provider Status Badge
        provider_name = settings.DEFAULT_AI_PROVIDER.upper()
        self.provider_badge = QLabel(f"ENGINE: {provider_name}")
        self.provider_badge.setStyleSheet(
            "background-color: rgba(0, 240, 255, 0.15); color: #00F0FF; "
            "border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 12px; "
            "padding: 4px 12px; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(self.provider_badge)

        # 3. Microphone Status Badge
        self.mic_badge = QLabel("MIC: ACTIVE" if settings.ENABLE_VOICE else "MIC: OFF")
        mic_color = "#10B981" if settings.ENABLE_VOICE else "#94A3B8"
        self.mic_badge.setStyleSheet(
            f"background-color: rgba(16, 185, 129, 0.15); color: {mic_color}; "
            f"border: 1px solid {mic_color}; border-radius: 12px; "
            "padding: 4px 12px; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(self.mic_badge)

        # 4. Live Digital Clock
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #F8FAFC; margin-left: 15px;")
        layout.addWidget(self.clock_label)

        # Clock update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_clock)
        self.timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss A")
        self.clock_label.setText(current_time)

    def set_mic_active(self, active: bool):
        mic_color = "#10B981" if active else "#94A3B8"
        status_text = "MIC: LISTENING" if active else "MIC: IDLE"
        self.mic_badge.setText(status_text)
        self.mic_badge.setStyleSheet(
            f"background-color: rgba(16, 185, 129, 0.15); color: {mic_color}; "
            f"border: 1px solid {mic_color}; border-radius: 12px; "
            "padding: 4px 12px; font-size: 11px; font-weight: bold;"
        )
