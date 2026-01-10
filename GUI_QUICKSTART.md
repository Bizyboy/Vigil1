# GUI Mode - Quick Reference

> **New Feature!** Vigil now supports an optional GUI mode with visual widgets.

## Quick Start

### Voice-Only Mode (Classic)
```bash
python vigil.py
```

### GUI Mode (Desktop Widget + Chat + Settings)
```bash
python vigil.py --gui
```

### GUI with Activation String
```bash
python vigil.py --gui --activate "your-key"
```

### Test GUI (Standalone)
```bash
python launch_gui.py
```

## GUI Requirements

- **Windows**: tkinter is included with Python (no extra steps needed)
- **Linux**: Install with `sudo apt-get install python3-tk` (Ubuntu/Debian)
- **Mac**: tkinter should be included with Python

Check compatibility:
```bash
python check_gui.py
```

## GUI Components

1. **🎯 Desktop Widget** - Flying mascot that represents Vigil
   - Always on top, semi-transparent
   - Gentle floating animations
   - Click to open chat, right-click for settings

2. **💬 Chat Window** - Text-based interface
   - Type messages or use voice input button
   - Chat history with timestamps
   - Hotkey: `Ctrl+Alt+C`

3. **⚙️ Forward Operating Base (FOB)** - Settings & Control
   - Task management
   - Configuration settings
   - Customization options
   - System status monitoring
   - Hotkey: `Ctrl+Alt+S`

## More Information

See [GUI_DOCUMENTATION.md](GUI_DOCUMENTATION.md) for complete documentation.
