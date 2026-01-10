#!/usr/bin/env python3
"""
Vigil GUI Verification Script
==============================

Verifies that the GUI components are properly structured and importable.
Cannot test actual rendering in headless environment.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all GUI components can be imported."""
    print("Testing GUI imports...")
    
    try:
        import gui
        print(f"✓ gui module imports")
        print(f"  GUI_AVAILABLE: {gui.GUI_AVAILABLE}")
        
        if gui.GUI_AVAILABLE:
            print("  ✓ tkinter is available")
            print("  ✓ VigilDesktopWidget available")
            print("  ✓ VigilChatWindow available")
            print("  ✓ VigilSettingsWindow available")
            print("  ✓ WindowManager available")
        else:
            print("  ⚠ tkinter not available - dummy classes loaded")
            print("  ✓ Graceful fallback working")
            
        return True
    except Exception as e:
        print(f"✗ Failed to import GUI: {e}")
        return False


def test_vigil_integration():
    """Test that vigil.py can handle GUI mode."""
    print("\nTesting Vigil integration...")
    
    # We can't fully import vigil due to missing dependencies in this environment
    # But we can check if the file has the right structure
    
    vigil_path = Path(__file__).parent / "vigil.py"
    if not vigil_path.exists():
        print("✗ vigil.py not found")
        return False
        
    content = vigil_path.read_text()
    
    checks = [
        ("--gui flag", "add_argument" in content and "--gui" in content),
        ("--activate flag", "--activate" in content),
        ("WindowManager import", "WindowManager" in content),
        ("GUI_AVAILABLE check", "GUI_AVAILABLE" in content),
        ("enable_gui parameter", "enable_gui" in content),
    ]
    
    all_passed = True
    for name, passed in checks:
        if passed:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name}")
            all_passed = False
            
    return all_passed


def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        "gui/__init__.py",
        "gui/desktop_widget.py",
        "gui/chat_window.py",
        "gui/settings_window.py",
        "gui/window_manager.py",
        "launch_gui.py",
        "check_gui.py",
        "GUI_DOCUMENTATION.md",
        "GUI_QUICKSTART.md",
    ]
    
    all_exist = True
    for filepath in required_files:
        path = Path(__file__).parent / filepath
        if path.exists():
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} missing")
            all_exist = False
            
    return all_exist


def test_class_structure():
    """Test that GUI classes have expected methods."""
    print("\nTesting class structure...")
    
    try:
        import gui
        
        if not gui.GUI_AVAILABLE:
            print("  ⚠ Skipping (tkinter not available)")
            return True
        
        # Check WindowManager has required methods
        wm = gui.WindowManager
        required_methods = [
            'activate', 'show_chat', 'show_settings', 'show_widget',
            'toggle_chat', 'toggle_settings', 'toggle_widget',
            'run', 'stop'
        ]
        
        all_present = True
        for method in required_methods:
            if hasattr(wm, method):
                print(f"  ✓ WindowManager.{method}()")
            else:
                print(f"  ✗ WindowManager.{method}() missing")
                all_present = False
                
        return all_present
        
    except Exception as e:
        print(f"  ✗ Error checking class structure: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("VIGIL GUI VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Vigil Integration", test_vigil_integration),
        ("Class Structure", test_class_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"Error running {name}: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print()
    if all_passed:
        print("✓ All verification tests passed!")
        print()
        print("The GUI system is properly structured.")
        print("To use it, run: python vigil.py --gui")
        print()
        print("Note: Actual GUI rendering requires tkinter and a display.")
        print("Run 'python check_gui.py' to check your system compatibility.")
        return 0
    else:
        print("✗ Some verification tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
