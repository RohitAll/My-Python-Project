"""
Futuristic Dark Theme QSS Stylesheet for JARVIS GUI
Features dark slate background, glassmorphism containers, cyan neon accents, and custom scrollbars.
"""

DARK_FUTURISTIC_QSS = """
QMainWindow {
    background-color: #0B0E14;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

QWidget {
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    color: #E2E8F0;
}

/* Glassmorphism Panels */
QFrame#glassPanel {
    background-color: rgba(19, 27, 46, 0.75);
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 12px;
}

QFrame#glassHeader {
    background-color: rgba(13, 19, 33, 0.9);
    border-bottom: 1px solid rgba(0, 240, 255, 0.3);
}

QFrame#cardWidget {
    background-color: rgba(23, 32, 54, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px;
}

/* Input Box */
QLineEdit#chatInput {
    background-color: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(0, 240, 255, 0.4);
    border-radius: 20px;
    padding: 10px 18px;
    color: #F8FAFC;
    font-size: 14px;
}

QLineEdit#chatInput:focus {
    border: 1px solid #00F0FF;
    background-color: rgba(15, 23, 42, 1.0);
}

/* Action Buttons */
QPushButton#primaryBtn {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0052D4, stop:0.5 #4364F7, stop:1 #6FB1FC);
    color: #FFFFFF;
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton#primaryBtn:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066FF, stop:1 #00F0FF);
}

QPushButton#iconBtn {
    background-color: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-radius: 18px;
    color: #00F0FF;
    padding: 8px;
}

QPushButton#iconBtn:hover {
    background-color: rgba(0, 240, 255, 0.2);
    border: 1px solid #00F0FF;
}

QPushButton#stopBtn {
    background-color: rgba(225, 29, 72, 0.8);
    border: 1px solid #F43F5E;
    border-radius: 18px;
    color: #FFFFFF;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#stopBtn:hover {
    background-color: #F43F5E;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: rgba(15, 23, 42, 0.5);
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 240, 255, 0.3);
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 8px;
    background-color: rgba(13, 19, 33, 0.6);
}

QTabBar::tab {
    background-color: rgba(30, 41, 59, 0.6);
    color: #94A3B8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: rgba(0, 240, 255, 0.15);
    color: #00F0FF;
    border-bottom: 2px solid #00F0FF;
}
"""
