# New GUI Features - Enhanced Customization

## Overview
Three new tabs have been added to the Forward Operating Base (FOB) settings window, providing enhanced customization and integration capabilities.

## New Features

### 1. 🎭 Character Store Tab
Choose from different character designs for your desktop widget mascot.

**Available Characters:**
- **Classic Vigil** 👁️ - Original V logo design
- **Cyber Guardian** 🤖 - Futuristic robot aesthetic
- **Digital Spirit** 👻 - Ethereal holographic form
- **Wise Owl** 🦉 - Scholarly and observant
- **Dragon** 🐉 - Powerful and protective
- **Phoenix** 🔥 - Rebirth and transformation

**Features:**
- Grid layout with character cards
- Radio button selection
- Character preview with emoji/icon
- Description for each character
- Selection persists in settings

### 2. 🎯 Mode Selection Tab
Choose how Vigil assists you across different interaction modes.

**Available Modes:**
- **Copilot 💻** - Code-focused assistant for programming, debugging, and development
- **Chat 💬** - Conversational AI for general questions and friendly interaction
- **Agent 🤖** - Autonomous task executor for multi-step objectives
- **Codex 📚** - Knowledge base mode with access to Ascension Codex teachings

**Features:**
- Large, easy-to-read mode cards
- Clear descriptions for each mode
- Radio button selection
- Mode changes update status immediately
- Settings persist between sessions

### 3. 🔌 API Agents Tab
Manage external API integrations to extend Vigil's capabilities.

**Features:**
- **Add Agent** - Integrate new API services
  - Agent name configuration
  - API endpoint URL
  - API key (secure input)
  - Custom icon (emoji)
  
- **Agent Management**
  - Enable/disable agents with one click
  - Edit agent configurations
  - Remove agents
  - Visual status indicators (enabled/disabled)
  
- **Agent Cards Display**
  - Shows agent icon and name
  - Displays API endpoint
  - Status indicator (green for enabled, red for disabled)
  - Action buttons (Edit, Toggle, Remove)

**Example Agents:**
- Custom LLM endpoints
- Specialized AI services
- Third-party integrations
- Custom API wrappers

## How to Access

1. Open Vigil with GUI mode:
   ```bash
   python vigil.py --gui
   ```

2. Right-click the desktop widget OR press `Ctrl+Alt+S`

3. Navigate to the new tabs:
   - **🎭 Character Store**
   - **🎯 Mode Selection**
   - **🔌 API Agents**

## Settings Persistence

All settings are saved to `config/gui_settings.json`:
```json
{
  "widget_character": "Classic Vigil",
  "vigil_mode": "Chat",
  "api_agents": [
    {
      "name": "Custom LLM",
      "api_endpoint": "https://api.example.com/v1",
      "api_key": "***",
      "icon": "🤖",
      "enabled": true
    }
  ]
}
```

## UI Design

All new features follow the existing color scheme:
- **Background Dark**: #1a1a2e
- **Background Medium**: #16213e
- **Background Light**: #0f3460
- **Accent**: #e94560
- **Text Primary**: #e0e0e0
- **Success**: #00ff00
- **Error**: #ff0000

## Future Enhancements

Potential additions:
- More character designs
- Community character marketplace
- Advanced mode configurations
- Agent templates and presets
- Agent health monitoring
- Rate limiting controls
