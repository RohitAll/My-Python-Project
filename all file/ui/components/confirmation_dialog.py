"""
Security Action Confirmation Modal Dialog
Provides interactive user confirmation UI before dangerous operations execute.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt


class ConfirmationDialog(QDialog):
    """Custom futuristic modal dialog for safety action approval."""

    def __init__(self, tool_name: str, risk_level: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS // SECURITY CONFIRMATION REQUIRED")
        self.setFixedWidth(460)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        # Apply dark theme stylesheet to dialog
        self.setStyleSheet(
            "QDialog { background-color: #0F172A; border: 2px solid #EF4444; border-radius: 12px; }"
            "QLabel { color: #F8FAFC; font-size: 13px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_lbl = QLabel("⚠️ ACTION CONFIRMATION REQUIRED")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #EF4444;")
        layout.addWidget(title_lbl)

        # Action Details Card
        card = QFrame()
        card.setStyleSheet(
            "background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px;"
        )
        card_layout = QVBoxLayout(card)

        tool_lbl = QLabel(f"ACTION: {tool_name.upper()} (RISK: {risk_level})")
        tool_lbl.setStyleSheet("font-weight: bold; color: #F59E0B;")
        card_layout.addWidget(tool_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #E2E8F0; font-size: 13px;")
        card_layout.addWidget(msg_lbl)

        layout.addWidget(card)

        # Question prompt
        prompt_lbl = QLabel("Do you want JARVIS to proceed with this operation?")
        prompt_lbl.setStyleSheet("font-weight: bold; color: #F8FAFC;")
        layout.addWidget(prompt_lbl)

        # Buttons Row
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(110, 36)
        self.cancel_btn.setStyleSheet(
            "background-color: #334155; color: #F8FAFC; border: none; border-radius: 18px; font-weight: bold;"
        )
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()

        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setFixedSize(110, 36)
        self.confirm_btn.setStyleSheet(
            "background-color: #DC2626; color: #FFFFFF; border: none; border-radius: 18px; font-weight: bold;"
        )
        self.confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)
