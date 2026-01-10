"""
VIGIL GUI Components
====================

Desktop widget, chat interface, and settings window for Vigil.

Requires: tkinter (included with Python on Windows, may need installation on Linux)
"""

# Check if GUI is available
try:
    import tkinter as _tk_test
    GUI_AVAILABLE = True
    del _tk_test
except ImportError:
    GUI_AVAILABLE = False
    import warnings
    warnings.warn("tkinter not available - GUI features disabled. Install python3-tk package.")

if GUI_AVAILABLE:
    from .desktop_widget import VigilDesktopWidget
    from .chat_window import VigilChatWindow
    from .settings_window import VigilSettingsWindow
    from .window_manager import WindowManager
    
    __all__ = [
        'VigilDesktopWidget',
        'VigilChatWindow', 
        'VigilSettingsWindow',
        'WindowManager',
        'GUI_AVAILABLE',
    ]
else:
    # Provide dummy classes when GUI is not available
    class VigilDesktopWidget:
        def __init__(self, *args, **kwargs):
            raise ImportError("GUI not available. Install python3-tk package.")
    
    class VigilChatWindow:
        def __init__(self, *args, **kwargs):
            raise ImportError("GUI not available. Install python3-tk package.")
    
    class VigilSettingsWindow:
        def __init__(self, *args, **kwargs):
            raise ImportError("GUI not available. Install python3-tk package.")
    
    class WindowManager:
        def __init__(self, *args, **kwargs):
            raise ImportError("GUI not available. Install python3-tk package.")
    
    __all__ = [
        'VigilDesktopWidget',
        'VigilChatWindow', 
        'VigilSettingsWindow',
        'WindowManager',
        'GUI_AVAILABLE',
    ]
