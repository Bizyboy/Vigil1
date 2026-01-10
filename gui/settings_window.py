"""
Vigil Settings Window - Forward Operating Base (FOB)
=====================================================

Central control panel for Vigil's tasks, settings, and customizations.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable, Dict, Any
import json
from pathlib import Path


# Color scheme constants
class Colors:
    """Color constants for consistent theming."""
    BG_DARK = '#1a1a2e'
    BG_MEDIUM = '#16213e'
    BG_LIGHT = '#0f3460'
    ACCENT = '#e94560'
    ACCENT_HOVER = '#ff6b9d'
    TEXT_PRIMARY = '#e0e0e0'
    TEXT_SECONDARY = '#888888'
    SUCCESS = '#00ff00'
    WARNING = '#ffaa00'
    ERROR = '#ff0000'


class VigilSettingsWindow:
    """
    Forward Operating Base (FOB) for Vigil.
    
    Features:
    - Task management
    - Settings configuration
    - Customization options
    - Status monitoring
    - Memory browser
    """
    
    def __init__(
        self,
        settings_file: Optional[Path] = None,
        on_settings_changed: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """Initialize the settings window."""
        self.settings_file = settings_file
        self.on_settings_changed = on_settings_changed
        self.settings = {}
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title("Vigil - Forward Operating Base")
        self.window.geometry("700x600")
        self.window.configure(bg='#1a1a2e')
        
        # Set icon behavior
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Load settings
        self._load_settings()
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the settings UI."""
        # Header
        header_frame = tk.Frame(self.window, bg='#0f3460', height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="⚙️ FORWARD OPERATING BASE",
            font=('Arial', 16, 'bold'),
            bg='#0f3460',
            fg='#e94560',
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Command Center for Vigil",
            font=('Arial', 10),
            bg='#0f3460',
            fg='#888888',
        )
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=20)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1a1a2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#16213e', foreground='#e0e0e0', padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', '#0f3460')], foreground=[('selected', '#e94560')])
        
        # Create tabs
        self._create_tasks_tab()
        self._create_settings_tab()
        self._create_customization_tab()
        self._create_character_store_tab()
        self._create_mode_selection_tab()
        self._create_agents_tab()
        self._create_status_tab()
        
    def _create_tasks_tab(self):
        """Create the tasks management tab."""
        tab = tk.Frame(self.notebook, bg='#16213e')
        self.notebook.add(tab, text='📋 Tasks')
        
        # Instructions
        info_label = tk.Label(
            tab,
            text="Manage Vigil's tasks and commitments",
            font=('Arial', 11),
            bg='#16213e',
            fg='#888888',
        )
        info_label.pack(pady=10)
        
        # Task list
        task_frame = tk.Frame(tab, bg='#16213e')
        task_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Task display
        self.task_display = scrolledtext.ScrolledText(
            task_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#0f3460',
            fg='#e0e0e0',
            insertbackground='#e94560',
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.task_display.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder tasks
        self.task_display.insert(tk.END, "📌 Active Tasks:\n\n")
        self.task_display.insert(tk.END, "• Monitor system status\n")
        self.task_display.insert(tk.END, "• Listen for wake words\n")
        self.task_display.insert(tk.END, "• Process user requests\n")
        self.task_display.insert(tk.END, "• Daily reflection at midnight\n\n")
        self.task_display.insert(tk.END, "✅ Completed:\n\n")
        self.task_display.insert(tk.END, "• System initialization\n")
        self.task_display.insert(tk.END, "• Voice system ready\n")
        
        # Task input
        input_frame = tk.Frame(tab, bg='#16213e')
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Label(
            input_frame,
            text="New Task:",
            font=('Arial', 10),
            bg='#16213e',
            fg='#e0e0e0',
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.task_input = tk.Entry(
            input_frame,
            font=('Consolas', 10),
            bg='#0f3460',
            fg='#e0e0e0',
            insertbackground='#e94560',
            relief=tk.FLAT,
        )
        self.task_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            input_frame,
            text="Add Task",
            font=('Arial', 9, 'bold'),
            bg='#e94560',
            fg='#ffffff',
            activebackground='#ff6b9d',
            relief=tk.FLAT,
            command=self._add_task,
            cursor='hand2',
        ).pack(side=tk.LEFT)
        
    def _create_settings_tab(self):
        """Create the settings configuration tab."""
        tab = tk.Frame(self.notebook, bg='#16213e')
        self.notebook.add(tab, text='⚙️ Settings')
        
        # Settings container
        settings_container = tk.Frame(tab, bg='#16213e')
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Wake Words
        self._create_setting_section(
            settings_container,
            "Wake Words",
            "wake_words",
            "vigil, hey vigil, yo vigil, yo v",
        )
        
        # Voice Settings
        self._create_setting_section(
            settings_container,
            "ElevenLabs Voice ID",
            "voice_id",
            "pNInz6obpgDQGcFmaJgB",
        )
        
        # User Name
        self._create_setting_section(
            settings_container,
            "Your Name",
            "user_name",
            "Louis",
        )
        
        # Auto-activation
        auto_activate_frame = tk.Frame(settings_container, bg=Colors.BG_MEDIUM)
        auto_activate_frame.pack(fill=tk.X, pady=10)
        
        self.auto_activate_var = tk.BooleanVar(value=self.settings.get('auto_activate', True))
        tk.Checkbutton(
            auto_activate_frame,
            text="Auto-activate on startup",
            variable=self.auto_activate_var,
            font=('Arial', 10),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            selectcolor=Colors.BG_LIGHT,
            activebackground=Colors.BG_MEDIUM,
            command=self._on_auto_activate_changed,
        ).pack(anchor=tk.W)
        
        # Save button
        tk.Button(
            settings_container,
            text="Save Settings",
            font=('Arial', 11, 'bold'),
            bg='#e94560',
            fg='#ffffff',
            activebackground='#ff6b9d',
            relief=tk.FLAT,
            command=self._save_settings,
            cursor='hand2',
            pady=10,
        ).pack(pady=20)
        
    def _create_setting_section(self, parent, label: str, key: str, default: str):
        """Create a setting input section."""
        frame = tk.Frame(parent, bg='#16213e')
        frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            frame,
            text=f"{label}:",
            font=('Arial', 10, 'bold'),
            bg='#16213e',
            fg='#e0e0e0',
        ).pack(anchor=tk.W, pady=(0, 5))
        
        entry = tk.Entry(
            frame,
            font=('Consolas', 10),
            bg='#0f3460',
            fg='#e0e0e0',
            insertbackground='#e94560',
            relief=tk.FLAT,
        )
        entry.insert(0, self.settings.get(key, default))
        entry.pack(fill=tk.X)
        
        # Store reference
        if not hasattr(self, 'setting_entries'):
            self.setting_entries = {}
        self.setting_entries[key] = entry
        
    def _create_customization_tab(self):
        """Create the customization tab."""
        tab = tk.Frame(self.notebook, bg='#16213e')
        self.notebook.add(tab, text='🎨 Customize')
        
        # Info
        info_label = tk.Label(
            tab,
            text="Customize Vigil's appearance and behavior",
            font=('Arial', 11),
            bg='#16213e',
            fg='#888888',
        )
        info_label.pack(pady=20)
        
        # Widget visibility
        widget_frame = tk.LabelFrame(
            tab,
            text="Widget Display",
            font=('Arial', 10, 'bold'),
            bg='#16213e',
            fg='#e94560',
            relief=tk.FLAT,
        )
        widget_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.show_desktop_widget_var = tk.BooleanVar(value=self.settings.get('show_desktop_widget', True))
        tk.Checkbutton(
            widget_frame,
            text="Show floating desktop widget",
            variable=self.show_desktop_widget_var,
            font=('Arial', 10),
            bg='#16213e',
            fg='#e0e0e0',
            selectcolor='#0f3460',
            activebackground='#16213e',
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        self.show_chat_on_startup_var = tk.BooleanVar(value=self.settings.get('show_chat_on_startup', False))
        tk.Checkbutton(
            widget_frame,
            text="Show chat window on startup",
            variable=self.show_chat_on_startup_var,
            font=('Arial', 10),
            bg='#16213e',
            fg='#e0e0e0',
            selectcolor='#0f3460',
            activebackground='#16213e',
        ).pack(anchor=tk.W, padx=10, pady=5)
        
    def _create_status_tab(self):
        """Create the status monitoring tab."""
        tab = tk.Frame(self.notebook, bg='#16213e')
        self.notebook.add(tab, text='📊 Status')
        
        # Status display
        status_frame = tk.Frame(tab, bg='#16213e')
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.status_display = scrolledtext.ScrolledText(
            status_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#0f3460',
            fg='#e0e0e0',
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.status_display.pack(fill=tk.BOTH, expand=True)
        
        # Initial status
        self.update_status("🟢 System Online\n")
        self.update_status("🎤 Voice System: Ready\n")
        self.update_status("🧠 Brain: Active\n")
        self.update_status("💾 Memory: Loaded\n")
        self.update_status("🔊 Audio: Connected\n")
        
    def _create_character_store_tab(self):
        """Create the character store tab for widget designs."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_MEDIUM)
        self.notebook.add(tab, text='🎭 Character Store')
        
        # Header
        info_label = tk.Label(
            tab,
            text="Choose your desktop widget character",
            font=('Arial', 11),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
        )
        info_label.pack(pady=10)
        
        # Character grid
        characters_frame = tk.Frame(tab, bg=Colors.BG_MEDIUM)
        characters_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Character designs
        characters = [
            {"name": "Classic Vigil", "emoji": "👁️", "description": "Original V logo design"},
            {"name": "Cyber Guardian", "emoji": "🤖", "description": "Futuristic robot aesthetic"},
            {"name": "Digital Spirit", "emoji": "👻", "description": "Ethereal holographic form"},
            {"name": "Wise Owl", "emoji": "🦉", "description": "Scholarly and observant"},
            {"name": "Dragon", "emoji": "🐉", "description": "Powerful and protective"},
            {"name": "Phoenix", "emoji": "🔥", "description": "Rebirth and transformation"},
        ]
        
        # Current selection
        self.selected_character = tk.StringVar(value=self.settings.get('widget_character', 'Classic Vigil'))
        
        # Create character cards in grid
        for i, char in enumerate(characters):
            row = i // 3
            col = i % 3
            
            card = tk.Frame(
                characters_frame,
                bg=Colors.BG_LIGHT,
                relief=tk.RAISED,
                borderwidth=2,
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Character emoji/icon
            tk.Label(
                card,
                text=char['emoji'],
                font=('Arial', 40),
                bg=Colors.BG_LIGHT,
            ).pack(pady=(10, 5))
            
            # Character name
            tk.Label(
                card,
                text=char['name'],
                font=('Arial', 11, 'bold'),
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_PRIMARY,
            ).pack()
            
            # Description
            tk.Label(
                card,
                text=char['description'],
                font=('Arial', 9),
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_SECONDARY,
                wraplength=150,
            ).pack(pady=5)
            
            # Select button
            select_btn = tk.Radiobutton(
                card,
                text="Select",
                variable=self.selected_character,
                value=char['name'],
                font=('Arial', 9, 'bold'),
                bg=Colors.BG_LIGHT,
                fg=Colors.ACCENT,
                selectcolor=Colors.BG_LIGHT,
                activebackground=Colors.BG_LIGHT,
                command=lambda n=char['name']: self._on_character_selected(n),
            )
            select_btn.pack(pady=(0, 10))
            
        # Configure grid weights
        for i in range(3):
            characters_frame.columnconfigure(i, weight=1)
            
    def _create_mode_selection_tab(self):
        """Create the mode selection tab (Copilot, Chat, Agent, Codex)."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_MEDIUM)
        self.notebook.add(tab, text='🎯 Mode Selection')
        
        # Header
        info_label = tk.Label(
            tab,
            text="Select how Vigil assists you",
            font=('Arial', 11),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
        )
        info_label.pack(pady=10)
        
        # Mode container
        modes_container = tk.Frame(tab, bg=Colors.BG_MEDIUM)
        modes_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Current mode
        self.selected_mode = tk.StringVar(value=self.settings.get('vigil_mode', 'Chat'))
        
        # Mode options
        modes = [
            {
                "name": "Copilot",
                "icon": "💻",
                "description": "Code-focused assistant that helps with programming, debugging, and development tasks"
            },
            {
                "name": "Chat",
                "icon": "💬",
                "description": "Conversational AI for general questions, brainstorming, and friendly interaction"
            },
            {
                "name": "Agent",
                "icon": "🤖",
                "description": "Autonomous task executor that can plan and complete multi-step objectives"
            },
            {
                "name": "Codex",
                "icon": "📚",
                "description": "Knowledge base mode with access to Ascension Codex and sacred teachings"
            },
        ]
        
        for mode in modes:
            # Mode card
            card = tk.Frame(
                modes_container,
                bg=Colors.BG_LIGHT,
                relief=tk.RAISED,
                borderwidth=2,
            )
            card.pack(fill=tk.X, pady=10)
            
            # Header with icon and radio button
            header_frame = tk.Frame(card, bg=Colors.BG_LIGHT)
            header_frame.pack(fill=tk.X, padx=15, pady=10)
            
            tk.Label(
                header_frame,
                text=mode['icon'],
                font=('Arial', 24),
                bg=Colors.BG_LIGHT,
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Radiobutton(
                header_frame,
                text=mode['name'],
                variable=self.selected_mode,
                value=mode['name'],
                font=('Arial', 14, 'bold'),
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.BG_LIGHT,
                activebackground=Colors.BG_LIGHT,
                command=lambda m=mode['name']: self._on_mode_selected(m),
            ).pack(side=tk.LEFT)
            
            # Description
            tk.Label(
                card,
                text=mode['description'],
                font=('Arial', 10),
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_SECONDARY,
                wraplength=600,
                justify=tk.LEFT,
            ).pack(fill=tk.X, padx=15, pady=(0, 15))
            
    def _create_agents_tab(self):
        """Create the agents management tab for API integrations."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_MEDIUM)
        self.notebook.add(tab, text='🔌 API Agents')
        
        # Header
        header_frame = tk.Frame(tab, bg=Colors.BG_MEDIUM)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            header_frame,
            text="Manage API Agent Integrations",
            font=('Arial', 12, 'bold'),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header_frame,
            text="+ Add Agent",
            font=('Arial', 10, 'bold'),
            bg=Colors.ACCENT,
            fg='#ffffff',
            activebackground=Colors.ACCENT_HOVER,
            relief=tk.FLAT,
            command=self._add_agent,
            cursor='hand2',
        ).pack(side=tk.RIGHT)
        
        # Agents list
        agents_frame = tk.Frame(tab, bg=Colors.BG_MEDIUM)
        agents_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create scrollable frame for agents
        canvas = tk.Canvas(agents_frame, bg=Colors.BG_MEDIUM, highlightthickness=0)
        scrollbar = tk.Scrollbar(agents_frame, orient="vertical", command=canvas.yview)
        self.agents_list_frame = tk.Frame(canvas, bg=Colors.BG_MEDIUM)
        
        self.agents_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.agents_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load and display existing agents
        self.agents = self.settings.get('api_agents', [])
        self._refresh_agents_list()
        
    def _refresh_agents_list(self):
        """Refresh the agents list display."""
        # Clear existing widgets
        for widget in self.agents_list_frame.winfo_children():
            widget.destroy()
            
        if not self.agents:
            # Show empty state
            tk.Label(
                self.agents_list_frame,
                text="No API agents configured yet.\nClick '+ Add Agent' to integrate external AI services.",
                font=('Arial', 11),
                bg=Colors.BG_MEDIUM,
                fg=Colors.TEXT_SECONDARY,
                justify=tk.CENTER,
            ).pack(pady=50)
        else:
            # Display each agent
            for i, agent in enumerate(self.agents):
                self._create_agent_card(i, agent)
                
    def _create_agent_card(self, index: int, agent: dict):
        """Create a card for an agent."""
        card = tk.Frame(
            self.agents_list_frame,
            bg=Colors.BG_LIGHT,
            relief=tk.RAISED,
            borderwidth=2,
        )
        card.pack(fill=tk.X, pady=5)
        
        # Agent info
        info_frame = tk.Frame(card, bg=Colors.BG_LIGHT)
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Icon
        tk.Label(
            info_frame,
            text=agent.get('icon', '🤖'),
            font=('Arial', 20),
            bg=Colors.BG_LIGHT,
        ).grid(row=0, column=0, rowspan=2, padx=(0, 15))
        
        # Name
        tk.Label(
            info_frame,
            text=agent.get('name', 'Unnamed Agent'),
            font=('Arial', 12, 'bold'),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
        ).grid(row=0, column=1, sticky='w')
        
        # API endpoint
        tk.Label(
            info_frame,
            text=f"Endpoint: {agent.get('api_endpoint', 'Not configured')}",
            font=('Arial', 9),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_SECONDARY,
        ).grid(row=1, column=1, sticky='w')
        
        # Status
        enabled = agent.get('enabled', False)
        status_text = "🟢 Enabled" if enabled else "🔴 Disabled"
        tk.Label(
            info_frame,
            text=status_text,
            font=('Arial', 9),
            bg=Colors.BG_LIGHT,
            fg=Colors.SUCCESS if enabled else Colors.ERROR,
        ).grid(row=0, column=2, padx=20)
        
        # Action buttons
        btn_frame = tk.Frame(card, bg=Colors.BG_LIGHT)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Button(
            btn_frame,
            text="Edit",
            font=('Arial', 9),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            command=lambda i=index: self._edit_agent(i),
            cursor='hand2',
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="Toggle",
            font=('Arial', 9),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            command=lambda i=index: self._toggle_agent(i),
            cursor='hand2',
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="Remove",
            font=('Arial', 9),
            bg=Colors.ERROR,
            fg='#ffffff',
            relief=tk.FLAT,
            command=lambda i=index: self._remove_agent(i),
            cursor='hand2',
        ).pack(side=tk.LEFT)
        
    def _on_character_selected(self, character_name: str):
        """Handle character selection."""
        self.settings['widget_character'] = character_name
        self.update_status(f"✅ Character changed to: {character_name}\n")
        
    def _on_mode_selected(self, mode_name: str):
        """Handle mode selection."""
        self.settings['vigil_mode'] = mode_name
        self.update_status(f"✅ Mode changed to: {mode_name}\n")
        
    def _add_agent(self):
        """Add a new API agent."""
        # Create dialog for adding agent
        dialog = tk.Toplevel(self.window)
        dialog.title("Add API Agent")
        dialog.geometry("500x400")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Form fields
        fields = {}
        
        # Name
        tk.Label(
            dialog,
            text="Agent Name:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        fields['name'] = tk.Entry(
            dialog,
            font=('Arial', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
        )
        fields['name'].pack(fill=tk.X, padx=20)
        
        # API Endpoint
        tk.Label(
            dialog,
            text="API Endpoint URL:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['api_endpoint'] = tk.Entry(
            dialog,
            font=('Arial', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
        )
        fields['api_endpoint'].pack(fill=tk.X, padx=20)
        
        # API Key
        tk.Label(
            dialog,
            text="API Key (optional):",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['api_key'] = tk.Entry(
            dialog,
            font=('Arial', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
            show='*',
        )
        fields['api_key'].pack(fill=tk.X, padx=20)
        
        # Icon
        tk.Label(
            dialog,
            text="Icon (emoji):",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['icon'] = tk.Entry(
            dialog,
            font=('Arial', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
        )
        fields['icon'].insert(0, '🤖')
        fields['icon'].pack(fill=tk.X, padx=20)
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_agent():
            new_agent = {
                'name': fields['name'].get(),
                'api_endpoint': fields['api_endpoint'].get(),
                'api_key': fields['api_key'].get(),
                'icon': fields['icon'].get(),
                'enabled': True,
            }
            
            if new_agent['name'] and new_agent['api_endpoint']:
                self.agents.append(new_agent)
                self.settings['api_agents'] = self.agents
                self._refresh_agents_list()
                self.update_status(f"✅ Added agent: {new_agent['name']}\n")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Name and API Endpoint are required!")
                
        tk.Button(
            btn_frame,
            text="Save",
            font=('Arial', 10, 'bold'),
            bg=Colors.ACCENT,
            fg='#ffffff',
            relief=tk.FLAT,
            command=save_agent,
            cursor='hand2',
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=('Arial', 10),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            command=dialog.destroy,
            cursor='hand2',
        ).pack(side=tk.LEFT)
        
    def _edit_agent(self, index: int):
        """Edit an existing agent."""
        agent = self.agents[index]
        
        # Create edit dialog (similar to add dialog)
        dialog = tk.Toplevel(self.window)
        dialog.title("Edit API Agent")
        dialog.geometry("500x400")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.window)
        dialog.grab_set()
        
        fields = {}
        
        # Pre-fill with existing values
        tk.Label(
            dialog,
            text="Agent Name:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        fields['name'] = tk.Entry(dialog, font=('Arial', 10), bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY)
        fields['name'].insert(0, agent['name'])
        fields['name'].pack(fill=tk.X, padx=20)
        
        tk.Label(
            dialog,
            text="API Endpoint URL:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['api_endpoint'] = tk.Entry(dialog, font=('Arial', 10), bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY)
        fields['api_endpoint'].insert(0, agent['api_endpoint'])
        fields['api_endpoint'].pack(fill=tk.X, padx=20)
        
        tk.Label(
            dialog,
            text="API Key:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['api_key'] = tk.Entry(dialog, font=('Arial', 10), bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY, show='*')
        fields['api_key'].insert(0, agent.get('api_key', ''))
        fields['api_key'].pack(fill=tk.X, padx=20)
        
        tk.Label(
            dialog,
            text="Icon:",
            font=('Arial', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_PRIMARY,
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        fields['icon'] = tk.Entry(dialog, font=('Arial', 10), bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY)
        fields['icon'].insert(0, agent.get('icon', '🤖'))
        fields['icon'].pack(fill=tk.X, padx=20)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def save_changes():
            self.agents[index] = {
                'name': fields['name'].get(),
                'api_endpoint': fields['api_endpoint'].get(),
                'api_key': fields['api_key'].get(),
                'icon': fields['icon'].get(),
                'enabled': agent.get('enabled', True),
            }
            self.settings['api_agents'] = self.agents
            self._refresh_agents_list()
            self.update_status(f"✅ Updated agent: {fields['name'].get()}\n")
            dialog.destroy()
            
        tk.Button(
            btn_frame,
            text="Save",
            font=('Arial', 10, 'bold'),
            bg=Colors.ACCENT,
            fg='#ffffff',
            relief=tk.FLAT,
            command=save_changes,
            cursor='hand2',
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=('Arial', 10),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            command=dialog.destroy,
            cursor='hand2',
        ).pack(side=tk.LEFT)
        
    def _toggle_agent(self, index: int):
        """Toggle agent enabled/disabled state."""
        self.agents[index]['enabled'] = not self.agents[index].get('enabled', False)
        self.settings['api_agents'] = self.agents
        self._refresh_agents_list()
        status = "enabled" if self.agents[index]['enabled'] else "disabled"
        self.update_status(f"✅ Agent {self.agents[index]['name']} {status}\n")
        
    def _remove_agent(self, index: int):
        """Remove an agent."""
        agent_name = self.agents[index]['name']
        if messagebox.askyesno("Confirm", f"Remove agent '{agent_name}'?"):
            del self.agents[index]
            self.settings['api_agents'] = self.agents
            self._refresh_agents_list()
            self.update_status(f"✅ Removed agent: {agent_name}\n")
        
    def _add_task(self):
        """Add a new task."""
        task = self.task_input.get().strip()
        if task:
            self.task_display.insert(tk.END, f"• {task}\n")
            self.task_input.delete(0, tk.END)
            
    def _on_auto_activate_changed(self):
        """Handle auto-activate checkbox change."""
        self.settings['auto_activate'] = self.auto_activate_var.get()
        
    def _load_settings(self):
        """Load settings from file."""
        if self.settings_file and self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = {}
        else:
            self.settings = {
                'auto_activate': True,
                'show_desktop_widget': True,
                'show_chat_on_startup': False,
            }
            
    def _save_settings(self):
        """Save settings to file."""
        # Collect settings from entries
        if hasattr(self, 'setting_entries'):
            for key, entry in self.setting_entries.items():
                self.settings[key] = entry.get()
                
        # Collect checkbox settings
        self.settings['auto_activate'] = self.auto_activate_var.get()
        self.settings['show_desktop_widget'] = self.show_desktop_widget_var.get()
        self.settings['show_chat_on_startup'] = self.show_chat_on_startup_var.get()
        
        # Collect new settings
        if hasattr(self, 'selected_character'):
            self.settings['widget_character'] = self.selected_character.get()
        if hasattr(self, 'selected_mode'):
            self.settings['vigil_mode'] = self.selected_mode.get()
        if hasattr(self, 'agents'):
            self.settings['api_agents'] = self.agents
        
        # Save to file
        if self.settings_file:
            try:
                self.settings_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.settings_file, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                self.update_status("✅ Settings saved successfully\n")
            except Exception as e:
                self.update_status(f"❌ Error saving settings: {e}\n")
                
        # Notify callback
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)
            
    def update_status(self, message: str):
        """Update the status display."""
        if hasattr(self, 'status_display'):
            self.status_display.insert(tk.END, message)
            self.status_display.see(tk.END)
            
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return self.settings.copy()
        
    def show(self):
        """Show the settings window."""
        self.window.deiconify()
        
    def hide(self):
        """Hide the settings window."""
        self.window.withdraw()
        
    def destroy(self):
        """Destroy the settings window."""
        self.window.destroy()


# Test the settings window
if __name__ == '__main__':
    def on_settings_changed(settings):
        print(f"Settings changed: {settings}")
        
    root = tk.Tk()
    root.withdraw()
    
    settings_window = VigilSettingsWindow(
        settings_file=Path("test_settings.json"),
        on_settings_changed=on_settings_changed,
    )
    settings_window.show()
    
    root.mainloop()
