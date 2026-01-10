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
        auto_activate_frame = tk.Frame(settings_container, bg='#16213e')
        auto_activate_frame.pack(fill=tk.X, pady=10)
        
        self.auto_activate_var = tk.BooleanVar(value=self.settings.get('auto_activate', True))
        tk.Checkbutton(
            auto_activate_frame,
            text="Auto-activate on startup",
            variable=self.auto_activate_var,
            font=('Arial', 10),
            bg='#16213e',
            fg='#e0e0e0',
            selectcolor='#0f3460',
            activebackground='#16213e',
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
