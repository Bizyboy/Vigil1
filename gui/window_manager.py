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
        # Desktop widget (pass root as parent)
        self.desktop_widget = VigilDesktopWidget(
            on_click=self._on_widget_click,
            on_right_click=self._on_widget_right_click,
            parent=self.root,
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
        if self.vigil and hasattr(self.vigil, 'brain'):
            try:
                # Import required classes for processing (cached after first import)
                from knowledge.codex import AscensionCodex
                from knowledge.shrines import ShrineVirtues
                from knowledge.roles import SacredRoles
                
                # Get knowledge context (similar to Vigil._process_command)
                # These methods use LRU cache internally for performance
                codex_context = AscensionCodex.get_context_for_query(message)
                shrine_context = ShrineVirtues.get_context_for_query(message)
                role_context = SacredRoles.get_role_context(message)
                kb_context = self.vigil.knowledge_base.get_context_for_query(message)
                user_context = self.vigil.memory.get_user_context()
                
                # Build enhanced prompt
                enhanced_prompt = f"""{message}

---
## CONTEXT FOR VIGIL

{user_context}

{role_context}

{codex_context}

{shrine_context}

{kb_context}
---

Respond naturally as Vigil. Keep responses concise for chat.
"""
                
                # Get response from brain (with internal caching for similar prompts)
                response = self.vigil.brain.think(enhanced_prompt)
                
                if response and hasattr(response, 'text'):
                    # Record in memory (with debounced saving)
                    role = SacredRoles.detect_role(message)
                    domain = SacredRoles.detect_domain(message)
                    self.vigil.memory.record_interaction(
                        user_input=message,
                        vigil_response=response.text,
                        mode=domain or "conversation",
                    )
                    return response.text
                else:
                    return "I'm having trouble processing that request."
                    
            except Exception as e:
                return f"Error processing: {str(e)}"
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
        # Apply widget visibility settings
        if 'show_desktop_widget' in settings:
            if settings['show_desktop_widget']:
                self.desktop_widget.show()
            else:
                self.desktop_widget.hide()
                
        # Update Vigil settings if instance is available
        if self.vigil:
            # Update wake words if changed
            if 'wake_words' in settings:
                from config.settings import WAKE_WORDS
                new_wake_words = [w.strip() for w in settings['wake_words'].split(',')]
                # Note: Actual wake word update would require restarting the listener
                # For now, just update the settings file
                
            # Update user name if changed
            if 'user_name' in settings:
                from config.settings import PRIMARY_USER_NAME
                # Update in-memory reference
                # Note: This requires updating the config module dynamically
                
            # Update voice settings if changed
            if 'voice_id' in settings and hasattr(self.vigil, 'voice_output'):
                # Update voice output settings
                # Note: This would require voice_output to support runtime reconfiguration
                pass
            
    def activate(self, activation_string: Optional[str] = None):
        """
        Activate Vigil GUI with optional activation string.
        
        Args:
            activation_string: Optional string to activate Vigil. 
                             Currently accepts any non-empty string.
                             Can be customized to implement specific validation logic.
        """
        if activation_string:
            # Validate activation string
            if self._validate_activation(activation_string):
                self.is_activated = True
            else:
                messagebox.showerror(
                    "Activation Failed",
                    "Invalid activation string.\n\n"
                    "The activation string must be:\n"
                    "- At least 3 characters long\n"
                    "- Non-empty\n\n"
                    "You can customize validation in window_manager.py"
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
        """
        Validate the activation string.
        
        Default implementation accepts any non-empty string with at least 3 characters.
        You can customize this method to implement your own validation logic, such as:
        - Checking against a predefined key
        - Validating a specific format/pattern
        - Verifying through an external service
        
        Args:
            activation_string: The activation string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Default: Accept any string with 3+ characters
        return len(activation_string.strip()) >= 3
        
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
