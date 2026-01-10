"""
VIGIL GUI Components
====================

Desktop widget, chat interface, and settings window for Vigil.
"""

from .desktop_widget import VigilDesktopWidget
from .chat_window import VigilChatWindow
from .settings_window import VigilSettingsWindow
from .window_manager import WindowManager

__all__ = [
    'VigilDesktopWidget',
    'VigilChatWindow', 
    'VigilSettingsWindow',
    'WindowManager',
]
