"""
Vigil Window Manager
====================

Coordinates all GUI windows and provides window switching functionality.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
from pathlib import Path
import threading

from .desktop_widget import VigilDesktopWidget
from .chat_window import VigilChatWindow
from .settings_window import VigilSettingsWindow


class WindowManager:
    """
    Manages all Vigil GUI windows.
    
    Features:
    - Coordinate desktop widget, chat, and settings windows
    - Hotkey support for quick switching
    - System tray integration (future)
    - Window state management
    """
    
    def __init__(
        self,
        vigil_instance=None,
        settings_file: Optional[Path] = None,
    ):
        """Initialize the window manager."""
        self.vigil = vigil_instance
        self.settings_file = settings_file or Path.home() / '.vigil' / 'gui_settings.json'
        
        # Create root window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Vigil")
        
        # Initialize windows
        self.desktop_widget: Optional[VigilDesktopWidget] = None
        self.chat_window: Optional[VigilChatWindow] = None
        self.settings_window: Optional[VigilSettingsWindow] = None
        
        # State
        self.is_activated = False
        self.is_running = False
        
        # Create windows
        self._create_windows()
        
        # Setup hotkeys
        self._setup_hotkeys()
        
    def _create_windows(self):
        """Create all GUI windows."""
        # Desktop widget
        self.desktop_widget = VigilDesktopWidget(
            on_click=self._on_widget_click,
            on_right_click=self._on_widget_right_click,
        )
        
        # Chat window
        self.chat_window = VigilChatWindow(
            on_message=self._on_chat_message,
            on_voice_input=self._on_voice_input,
            bot_name="Vigil",
        )
        
        # Settings window
        self.settings_window = VigilSettingsWindow(
            settings_file=self.settings_file,
            on_settings_changed=self._on_settings_changed,
        )
        
        # Initially hide all windows
        self.desktop_widget.hide()
        self.chat_window.hide()
        self.settings_window.hide()
        
    def _setup_hotkeys(self):
        """Setup global hotkeys."""
        # Register hotkeys with the root window
        self.root.bind('<Control-Alt-c>', lambda e: self.toggle_chat())
        self.root.bind('<Control-Alt-s>', lambda e: self.toggle_settings())
        self.root.bind('<Control-Alt-w>', lambda e: self.toggle_widget())
        
    def _on_widget_click(self):
        """Handle widget click - open chat."""
        self.show_chat()
        
    def _on_widget_right_click(self):
        """Handle widget right-click - open settings."""
        self.show_settings()
        
    def _on_chat_message(self, message: str):
        """Handle chat message."""
        if self.vigil:
            # Process through Vigil
            try:
                self.chat_window.set_status("Processing...", "#ffaa00")
                
                # Get response from Vigil
                response = self._get_vigil_response(message)
                
                # Display response
                if response:
                    self.chat_window.add_bot_message(response)
                else:
                    self.chat_window.add_bot_message("I'm having trouble processing that request.")
                    
                self.chat_window.set_status("Online", "#00ff00")
            except Exception as e:
                self.chat_window.add_system_message(f"Error: {str(e)}")
                self.chat_window.set_status("Error", "#ff0000")
        else:
            # No Vigil instance - echo mode
            self.chat_window.add_bot_message(f"Echo: {message}")
            
    def _get_vigil_response(self, message: str) -> str:
        """Get response from Vigil (if available)."""
        if self.vigil:
            # Call Vigil's process_command method
            # This is a simplified version - you'll need to adapt based on your Vigil class
            try:
                # Process command through Vigil's brain
                if hasattr(self.vigil, '_process_command'):
                    # Capture the response
                    # Note: The actual Vigil class uses voice output, so we need to adapt
                    return "Processing your request through Vigil..."
                else:
                    return "Vigil instance not fully initialized."
            except Exception as e:
                return f"Error processing command: {str(e)}"
        return ""
        
    def _on_voice_input(self):
        """Handle voice input request."""
        if self.vigil and hasattr(self.vigil, 'voice_input'):
            try:
                self.chat_window.add_system_message("🎤 Listening...")
                text = self.vigil.voice_input.listen_and_transcribe(timeout=10, phrase_limit=30)
                if text:
                    self.chat_window.add_user_message(text)
                    self._on_chat_message(text)
                else:
                    self.chat_window.add_system_message("No speech detected.")
            except Exception as e:
                self.chat_window.add_system_message(f"Voice input error: {str(e)}")
        else:
            self.chat_window.add_system_message("Voice input not available in this mode.")
            
    def _on_settings_changed(self, settings: dict):
        """Handle settings changes."""
        # Apply settings
        if 'show_desktop_widget' in settings:
            if settings['show_desktop_widget']:
                self.desktop_widget.show()
            else:
                self.desktop_widget.hide()
                
        # Update Vigil settings if instance is available
        if self.vigil:
            # Apply wake words, etc.
            pass
            
    def activate(self, activation_string: Optional[str] = None):
        """
        Activate Vigil GUI with optional activation string.
        
        Args:
            activation_string: Optional string to activate Vigil
        """
        if activation_string:
            # Validate activation string (placeholder)
            if self._validate_activation(activation_string):
                self.is_activated = True
            else:
                messagebox.showerror(
                    "Activation Failed",
                    "Invalid activation string. Please try again."
                )
                return
        else:
            self.is_activated = True
            
        # Show windows based on settings
        settings = self.settings_window.get_settings()
        
        if settings.get('show_desktop_widget', True):
            self.desktop_widget.show()
            
        if settings.get('show_chat_on_startup', False):
            self.chat_window.show()
            
        # Update status
        self.settings_window.update_status("✅ Vigil GUI activated\n")
        
    def _validate_activation(self, activation_string: str) -> bool:
        """Validate the activation string."""
        # For now, accept any non-empty string
        # You can implement your own validation logic here
        return len(activation_string.strip()) > 0
        
    def show_chat(self):
        """Show the chat window."""
        self.chat_window.show()
        
    def show_settings(self):
        """Show the settings window."""
        self.settings_window.show()
        
    def show_widget(self):
        """Show the desktop widget."""
        self.desktop_widget.show()
        
    def toggle_chat(self):
        """Toggle chat window visibility."""
        if self.chat_window.window.winfo_viewable():
            self.chat_window.hide()
        else:
            self.chat_window.show()
            
    def toggle_settings(self):
        """Toggle settings window visibility."""
        if self.settings_window.window.winfo_viewable():
            self.settings_window.hide()
        else:
            self.settings_window.show()
            
    def toggle_widget(self):
        """Toggle widget visibility."""
        if self.desktop_widget.window.winfo_viewable():
            self.desktop_widget.hide()
        else:
            self.desktop_widget.show()
            
    def run(self):
        """Start the window manager main loop."""
        self.is_running = True
        self.root.mainloop()
        
    def run_in_thread(self):
        """Run the window manager in a separate thread."""
        self.is_running = True
        gui_thread = threading.Thread(target=self.root.mainloop, daemon=True)
        gui_thread.start()
        return gui_thread
        
    def stop(self):
        """Stop the window manager and close all windows."""
        self.is_running = False
        
        # Close all windows
        if self.desktop_widget:
            self.desktop_widget.stop()
        if self.chat_window:
            self.chat_window.destroy()
        if self.settings_window:
            self.settings_window.destroy()
            
        # Quit root
        self.root.quit()
        self.root.destroy()


# Test the window manager
if __name__ == '__main__':
    manager = WindowManager()
    manager.activate()
    manager.show_chat()
    manager.run()
