"""
GUI Compatibility Check
=======================

Checks if the required GUI libraries are available.
"""

import sys


def check_gui_available():
    """Check if GUI libraries are available."""
    try:
        import tkinter
        return True, "tkinter is available"
    except ImportError as e:
        return False, f"tkinter not available: {e}"


def check_display():
    """Check if display is available (not headless)."""
    import os
    if sys.platform == "win32":
        # On Windows, display is usually available
        return True, "Windows display assumed available"
    else:
        # On Linux/Mac, check DISPLAY environment variable
        if "DISPLAY" in os.environ:
            return True, f"DISPLAY={os.environ['DISPLAY']}"
        else:
            return False, "No DISPLAY environment variable (headless environment)"


def main():
    """Run compatibility checks."""
    print("Vigil GUI Compatibility Check")
    print("=" * 50)
    
    gui_ok, gui_msg = check_gui_available()
    print(f"GUI Library: {'✓' if gui_ok else '✗'} {gui_msg}")
    
    display_ok, display_msg = check_display()
    print(f"Display:     {'✓' if display_ok else '✗'} {display_msg}")
    
    print("=" * 50)
    
    if gui_ok and display_ok:
        print("✓ GUI mode should work on this system")
        return 0
    elif not gui_ok:
        print("✗ GUI mode not available: tkinter not installed")
        print("  On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  On Fedora: sudo dnf install python3-tkinter")
        print("  On Windows: tkinter should be included with Python")
        return 1
    elif not display_ok:
        print("✗ GUI mode not available: no display (headless environment)")
        print("  GUI mode requires a graphical environment")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
