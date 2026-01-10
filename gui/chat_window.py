"""
Vigil Chat Window
=================

A GUI chat interface for interacting with Vigil through text and voice.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from datetime import datetime
from typing import Optional, Callable
import queue


class VigilChatWindow:
    """
    Chat window for text and voice interaction with Vigil.
    
    Features:
    - Text input and output
    - Chat history display
    - Voice input button
    - Auto-scroll
    - Timestamps
    - Status indicator
    """
    
    def __init__(
        self,
        on_message: Optional[Callable[[str], None]] = None,
        on_voice_input: Optional[Callable] = None,
        bot_name: str = "Vigil",
    ):
        """Initialize the chat window."""
        self.on_message = on_message
        self.on_voice_input = on_voice_input
        self.bot_name = bot_name
        
        # Message queue for thread-safe updates
        self.message_queue = queue.Queue()
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title(f"{bot_name} - Chat")
        self.window.geometry("500x600")
        self.window.configure(bg='#1a1a2e')
        
        # Set icon behavior
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Create UI
        self._create_ui()
        
        # Start message processing
        self._process_message_queue()
        
    def _create_ui(self):
        """Create the chat UI."""
        # Header
        header_frame = tk.Frame(self.window, bg='#0f3460', height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=f"💬 {self.bot_name}",
            font=('Arial', 16, 'bold'),
            bg='#0f3460',
            fg='#e94560',
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="● Online",
            font=('Arial', 10),
            bg='#0f3460',
            fg='#00ff00',
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Chat display area
        chat_frame = tk.Frame(self.window, bg='#16213e')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrolled text widget for chat history
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#16213e',
            fg='#e0e0e0',
            insertbackground='#e94560',
            selectbackground='#533483',
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)  # Read-only
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#00ffff', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_config('bot', foreground='#e94560', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_config('timestamp', foreground='#888888', font=('Consolas', 8))
        self.chat_display.tag_config('system', foreground='#ffaa00', font=('Consolas', 9, 'italic'))
        
        # Input area
        input_frame = tk.Frame(self.window, bg='#1a1a2e')
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        # Voice button
        self.voice_button = tk.Button(
            input_frame,
            text="🎤",
            font=('Arial', 14),
            bg='#0f3460',
            fg='#00ffff',
            activebackground='#533483',
            activeforeground='#00ffff',
            relief=tk.FLAT,
            width=3,
            command=self._on_voice_button,
            cursor='hand2',
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text input
        self.input_field = tk.Entry(
            input_frame,
            font=('Consolas', 11),
            bg='#16213e',
            fg='#e0e0e0',
            insertbackground='#e94560',
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground='#533483',
            highlightcolor='#e94560',
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind('<Return>', self._on_send)
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=('Arial', 10, 'bold'),
            bg='#e94560',
            fg='#ffffff',
            activebackground='#ff6b9d',
            activeforeground='#ffffff',
            relief=tk.FLAT,
            width=8,
            command=self._on_send,
            cursor='hand2',
        )
        self.send_button.pack(side=tk.LEFT)
        
        # Add welcome message
        self.add_system_message(f"{self.bot_name} is ready. Type a message or use voice input.")
        
    def _on_send(self, event=None):
        """Handle send button click."""
        message = self.input_field.get().strip()
        if message:
            # Display user message
            self.add_user_message(message)
            
            # Clear input
            self.input_field.delete(0, tk.END)
            
            # Call callback
            if self.on_message:
                # Run in separate thread to avoid blocking UI
                threading.Thread(
                    target=self.on_message,
                    args=(message,),
                    daemon=True,
                ).start()
                
    def _on_voice_button(self):
        """Handle voice button click."""
        if self.on_voice_input:
            # Change button appearance
            self.voice_button.config(bg='#e94560')
            self.add_system_message("Listening...")
            
            # Call callback in separate thread
            def voice_thread():
                self.on_voice_input()
                self.window.after(100, lambda: self.voice_button.config(bg='#0f3460'))
                
            threading.Thread(target=voice_thread, daemon=True).start()
            
    def add_user_message(self, message: str):
        """Add a user message to the chat."""
        self.message_queue.put(('user', message))
        
    def add_bot_message(self, message: str):
        """Add a bot message to the chat."""
        self.message_queue.put(('bot', message))
        
    def add_system_message(self, message: str):
        """Add a system message to the chat."""
        self.message_queue.put(('system', message))
        
    def _process_message_queue(self):
        """Process messages from the queue (thread-safe)."""
        try:
            while True:
                msg_type, message = self.message_queue.get_nowait()
                self._add_message_to_display(msg_type, message)
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.window.after(100, self._process_message_queue)
            
    def _add_message_to_display(self, msg_type: str, message: str):
        """Add a message to the display area."""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == 'user':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, "You: ", 'user')
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif msg_type == 'bot':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"{self.bot_name}: ", 'bot')
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif msg_type == 'system':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"{message}\n", 'system')
            
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def set_status(self, status: str, color: str = '#00ff00'):
        """Set the status indicator."""
        self.status_label.config(text=f"● {status}", fg=color)
        
    def show(self):
        """Show the chat window."""
        self.window.deiconify()
        self.input_field.focus()
        
    def hide(self):
        """Hide the chat window."""
        self.window.withdraw()
        
    def destroy(self):
        """Destroy the chat window."""
        self.window.destroy()


# Test the chat window
if __name__ == '__main__':
    import time
    
    def on_message(msg):
        print(f"Received message: {msg}")
        time.sleep(1)  # Simulate processing
        chat.add_bot_message(f"Echo: {msg}")
        
    def on_voice():
        print("Voice input requested")
        chat.add_system_message("Voice input feature coming soon...")
        
    root = tk.Tk()
    root.withdraw()
    
    chat = VigilChatWindow(
        on_message=on_message,
        on_voice_input=on_voice,
    )
    chat.show()
    
    root.mainloop()
