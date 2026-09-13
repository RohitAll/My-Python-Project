"""
Futuristic Glowing Animated AI Core Orb Widget
Custom PySide6 QWidget using QPainter to render dynamic AI orb states.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen, QBrush
from core.assistant import AssistantState


class OrbWidget(QWidget):
    """Futuristic animated AI orb representing JARVIS state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.state = AssistantState.IDLE
        self.phase = 0.0

        # Animation timer ~60 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16)

    def set_state(self, state: AssistantState):
        """Update current AI orb state."""
        self.state = state
        self.update()

    def _update_animation(self):
        self.phase += 0.05
        if self.phase > 2 * math.pi * 100:
            self.phase = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center = QPointF(width / 2.0, height / 2.0)
        radius = min(width, height) / 3.2

        # State color palettes
        if self.state == AssistantState.IDLE:
            base_color = QColor(0, 240, 255)  # Cyan
            outer_color = QColor(0, 150, 255, 40)
            pulse_speed = 1.0
        elif self.state == AssistantState.LISTENING:
            base_color = QColor(16, 185, 129)  # Green
            outer_color = QColor(52, 211, 153, 50)
            pulse_speed = 2.5
        elif self.state == AssistantState.THINKING:
            base_color = QColor(99, 102, 241)  # Indigo/Blue
            outer_color = QColor(129, 140, 248, 60)
            pulse_speed = 3.0
        elif self.state == AssistantState.SPEAKING:
            base_color = QColor(236, 72, 153)  # Pink/Magenta
            outer_color = QColor(244, 114, 182, 60)
            pulse_speed = 2.0
        elif self.state == AssistantState.EXECUTING:
            base_color = QColor(245, 158, 11)  # Amber/Gold
            outer_color = QColor(251, 191, 36, 60)
            pulse_speed = 4.0
        else:  # ERROR
            base_color = QColor(239, 68, 68)  # Red
            outer_color = QColor(248, 113, 113, 60)
            pulse_speed = 1.5

        # Dynamic pulse offset
        pulse = math.sin(self.phase * pulse_speed) * 8.0
        current_radius = radius + pulse

        # 1. Outer Glow Aura
        glow_grad = QRadialGradient(center, current_radius * 1.6)
        glow_grad.setColorAt(0.0, outer_color)
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, current_radius * 1.6, current_radius * 1.6)

        # 2. Outer Rotating Particle Rings
        painter.setPen(QPen(base_color, 2, Qt.DashLine))
        painter.drawEllipse(center, current_radius * 1.25, current_radius * 1.25)

        # 3. Inner Core Gradient Orb
        core_grad = QRadialGradient(center, current_radius)
        core_color = base_color.lighter(130)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        core_grad.setColorAt(0.4, base_color)
        core_grad.setColorAt(1.0, QColor(base_color.red(), base_color.green(), base_color.blue(), 30))

        painter.setBrush(QBrush(core_grad))
        painter.setPen(QPen(base_color, 1.5))
        painter.drawEllipse(center, current_radius, current_radius)

        # 4. State Title Text inside/below Orb
        painter.setPen(QColor(226, 232, 240))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)

        state_str = self.state.value
        painter.drawText(
            int(center.x() - 60),
            int(center.y() + current_radius * 1.7),
            120,
            25,
            Qt.AlignCenter,
            state_str,
        )
