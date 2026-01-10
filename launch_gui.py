#!/usr/bin/env python3
"""
Vigil GUI Launcher
==================

Standalone launcher for Vigil's GUI components.
Can be run independently to test widgets without the full Vigil system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Check for tkinter before importing GUI
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def main():
    """Launch Vigil GUI in standalone mode."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    VIGIL GUI LAUNCHER                         ║
║                  The Watchful Guardian                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if not GUI_AVAILABLE:
        print("[ERROR] tkinter not available!")
        print()
        print("GUI mode requires tkinter, which is not installed.")
        print()
        print("Installation instructions:")
        print("  - Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - Fedora: sudo dnf install python3-tkinter")
        print("  - Windows: tkinter should be included with Python")
        print()
        print("After installation, run this script again.")
        return 1
    
    from gui.window_manager import WindowManager
    
    print("[GUI] Launching Vigil GUI components...")
    print("[GUI] Note: Running in standalone mode (no voice system)")
    print()
    
    # Create window manager without Vigil instance
    manager = WindowManager(vigil_instance=None)
    
    # Activate and show windows
    print("[GUI] Activating widgets...")
    manager.activate()
    
    print("[GUI] Opening chat window...")
    manager.show_chat()
    
    print()
    print("═" * 60)
    print("VIGIL GUI IS READY")
    print("═" * 60)
    print()
    print("Hotkeys:")
    print("  Ctrl+Alt+C - Toggle Chat Window")
    print("  Ctrl+Alt+S - Toggle Settings Window (Forward Operating Base)")
    print("  Ctrl+Alt+W - Toggle Desktop Widget")
    print()
    print("Click the desktop widget to open chat.")
    print("Right-click the desktop widget to open settings.")
    print()
    print("Close all windows or press Ctrl+C to exit.")
    print("═" * 60)
    print()
    
    # Run the GUI
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\n[GUI] Shutting down...")
        manager.stop()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
