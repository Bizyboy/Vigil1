# Vigil GUI Mode

## Overview

Vigil now includes an optional GUI mode that provides visual interfaces for interacting with your AI companion. The GUI consists of three main components that work together to give you quick and easy access to Vigil's capabilities.

## Running GUI Mode

### Basic GUI Mode
```bash
python vigil.py --gui
```

### GUI Mode with Activation String
```bash
python vigil.py --gui --activate "your-activation-string"
```

### Standalone GUI Testing
If you want to test the GUI without the full Vigil voice system:
```bash
python launch_gui.py
```

## The Three Windows

### 🎯 Desktop Widget - Flying Mascot

A small, animated widget that floats on your screen representing Vigil's presence.

**Features:**
- **Always on top** - Stays visible above other windows
- **Gentle floating animation** - Moves smoothly around the screen
- **Semi-transparent** - Visible but not intrusive (90% opacity)
- **Fully draggable** - Click and drag to reposition
- **Interactive**:
  - Left-click: Opens chat window
  - Right-click: Opens settings/FOB window
  - Hover: Full opacity
  - Pulsing status indicator shows Vigil is online

**Visual Design:**
- Stylized "V" logo in a circular frame
- Animated eye that blinks
- Color scheme: Dark blues and vibrant red/cyan accents
- Pulsing status indicator (green ↔ cyan)

### 💬 Chat Window

A modern chat interface for text-based interaction with Vigil.

**Features:**
- **Text input** - Type messages and get responses
- **Voice input button** (🎤) - Click to use microphone
- **Chat history** - Scrollable conversation log
- **Timestamps** - See when each message was sent
- **Status indicator** - Shows if Vigil is online/processing
- **Syntax highlighting** - Different colors for user vs. bot messages

**Usage:**
- Type your message and press Enter or click Send
- Click the microphone button for voice input
- Scroll through previous conversations
- Window can be minimized and reopened via hotkeys

**Colors:**
- User messages: Cyan
- Vigil messages: Red/Pink
- System messages: Orange
- Timestamps: Gray

### ⚙️ Forward Operating Base (FOB) - Settings

The central command center for Vigil with a tabbed interface.

**Tabs:**

1. **📋 Tasks**
   - View Vigil's active tasks and commitments
   - Add new tasks
   - See completed tasks
   - Task tracking and management

2. **⚙️ Settings**
   - Configure wake words
   - Set ElevenLabs voice ID
   - Update your name
   - Toggle auto-activation
   - Save/load settings

3. **🎨 Customize**
   - Show/hide desktop widget
   - Control chat window startup
   - Appearance preferences
   - Widget behavior settings

4. **📊 Status**
   - System health monitoring
   - Voice system status
   - Brain activity
   - Memory status
   - Audio connection

## Hotkeys

Global keyboard shortcuts for quick window access:

- `Ctrl+Alt+C` - Toggle Chat Window
- `Ctrl+Alt+S` - Toggle Settings/FOB Window
- `Ctrl+Alt+W` - Toggle Desktop Widget

## Window Management

### Initial Setup
On first launch with `--gui`, all windows start hidden. The desktop widget will appear if auto-activate is enabled in settings.

### Activation
You can activate the GUI in two ways:

1. **Auto-activation**: Enabled by default in settings
2. **Manual activation**: Use `--activate "string"` flag

### Window States
- Each window can be independently shown/hidden
- Window positions are preserved between sessions
- Settings are saved to `config/gui_settings.json`

## Customization

### Settings File
GUI settings are stored in: `config/gui_settings.json`

Example configuration:
```json
{
  "auto_activate": true,
  "show_desktop_widget": true,
  "show_chat_on_startup": false,
  "wake_words": "vigil, hey vigil, yo vigil",
  "voice_id": "pNInz6obpgDQGcFmaJgB",
  "user_name": "Louis"
}
```

### Widget Animation
The desktop widget includes several animated elements:
- Gentle floating movement (changes position every 5 seconds)
- Smooth transitions with physics-based motion
- Animated "eye" that follows a sine wave
- Pulsing status indicator
- Hover effects (opacity changes)

## Integration with Voice Mode

When running in GUI mode, Vigil maintains all voice capabilities:
- Wake word detection still works
- Voice responses continue as normal
- Chat window provides a text alternative
- Voice input button in chat window
- Both text and voice can be used simultaneously

## Troubleshooting

### Widget not appearing
- Check auto-activate setting
- Try using `--activate "test"` flag
- Press `Ctrl+Alt+W` to toggle visibility

### Chat window not responding
- Check if Vigil core system is running
- Look for errors in terminal
- Verify voice system is initialized

### Hotkeys not working
- Make sure a Vigil window has focus
- Try clicking on chat or settings window first
- Check for conflicting hotkey assignments

### Windows appear on wrong monitor
- Drag to desired position
- Settings will save new position
- Use `Ctrl+Alt+[key]` to bring window to focus

## Technical Details

### Dependencies
The GUI uses Python's built-in `tkinter` library, which should be available with standard Python installations.

### Threading
- GUI runs in a separate thread from voice system
- Thread-safe message queues for chat updates
- Non-blocking UI operations

### Performance
- Minimal CPU usage (<2% on modern systems)
- Widget animation at 20 FPS (50ms refresh)
- Lightweight memory footprint (~50MB)

## Future Enhancements

Planned features for future releases:
- System tray integration
- Custom widget skins/themes
- Notification system
- Screen recording for task assistance
- Multi-monitor awareness
- Minimalist mode (widget only)
- Widget animation presets

---

**Note**: The GUI mode is completely optional. Vigil continues to work in classic voice-only mode without the `--gui` flag.
