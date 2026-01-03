#!/usr/bin/env python3
"""
VIGIL - The Watchful Guardian
=============================

A voice-first AI companion that never sleeps.

Features:
- Always-on wake word detection
- Multi-LLM support (GPT-4o, Claude, Gemini)
- Voice input (Whisper) and output (ElevenLabs)
- Daily midnight reflections
- Custom knowledge base
- Memory and learning from interactions

Usage:
    python vigil.py

Wake words: "Vigil", "Hey Vigil", "Yo Vigil", "Yo V", "Help",
            "The truth will set you free"

Author: Louis (Bizy/Lazurith)
"""

import sys
import time
import signal
import threading
from pathlib import Path

# Add parent directory to path for imports

from config.settings import (
    BOT_NAME,
    BOT_TITLE,
    WAKE_WORDS,
    PRIMARY_USER_NAME,
    Paths,
)
from core.listener import WakeWordListener
from core.voice_input import VoiceInput
from core.voice_output import VoiceOutput
from core.brain import Brain
from core.memory import Memory
from knowledge.codex import AscensionCodex
from knowledge.shrines import ShrineVirtues
from knowledge.roles import SacredRoles
from knowledge.knowledge_base import KnowledgeBase
from reflection.daily_reflection import ReflectionSystem


class Vigil:
    """
    The main Vigil application.

    Orchestrates all components:
    - Wake word detection
    - Speech-to-text
    - LLM processing
    - Text-to-speech
    - Memory & learning
    - Daily reflections
    """

    def __init__(self):
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██╗   ██╗██╗ ██████╗ ██╗██╗                             ║
║     ██║   ██║██║██╔════╝ ██║██║                             ║
║     ██║   ██║██║██║  ███╗██║██║                             ║
║     ╚██╗ ██╔╝██║██║   ██║██║██║                             ║
║      ╚████╔╝ ██║╚██████╔╝██║███████╗                        ║
║       ╚═══╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝                        ║
║                                                              ║
║                  THE WATCHFUL GUARDIAN                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)

        print(f"[{BOT_NAME}] Initializing systems...")

        # Ensure directories exist
        Paths.ensure_directories()

        # Initialize components
        self.voice_input = VoiceInput()
        self.voice_output = VoiceOutput()
        self.brain = Brain()
        self.memory = Memory()
        self.knowledge_base = KnowledgeBase()
        self.reflection_system = ReflectionSystem(
            brain=self.brain,
            memory=self.memory
        )

        # Wake word listener
        self.listener = WakeWordListener(
            on_wake=self._on_wake_word_detected,
            on_error=self._on_listener_error
        )

        # State
        self.is_running = False
        self.is_processing = False
        self._shutdown_event = threading.Event()

        print(f"[{BOT_NAME}] All systems initialized.")
        print(f"[{BOT_NAME}] Wake words: {', '.join(WAKE_WORDS)}")

    def _on_wake_word_detected(self, phrase: str):
        """Handle wake word detection."""
        if self.is_processing:
            return

        self.is_processing = True

        try:
            # Extract command from wake phrase
            command = self._extract_command(phrase)

            if command:
                # User said something after wake word
                self._process_command(command)
            else:
                # Just wake word - prompt for input
                self._acknowledge_wake()
                self._listen_for_command()

        finally:
            self.is_processing = False

    def _extract_command(self, phrase: str) -> str:
        """Extract command from the wake phrase."""
        phrase_lower = phrase.lower()

        # Find which wake word was used
        for wake_word in sorted(WAKE_WORDS, key=len, reverse=True):
            if wake_word.lower() in phrase_lower:
                idx = phrase_lower.find(wake_word.lower())
                remaining = phrase[idx + len(wake_word):].strip()
                # Clean up
                remaining = remaining.strip(",.?!")
                return remaining.strip()

        return phrase

    def _acknowledge_wake(self):
        """Acknowledge that we heard the wake word."""
        responses = [
            f"I'm here, {PRIMARY_USER_NAME}.",
            "Listening.",
            "Yes?",
            f"What do you need, {PRIMARY_USER_NAME}?",
            "I'm with you.",
        ]
        import random
        response = random.choice(responses)
        self.voice_output.speak(response)

    def _listen_for_command(self):
        """Listen for the user's command after wake word."""
        text = self.voice_input.listen_and_transcribe(timeout=10, phrase_limit=30)
        if text:
            self._process_command(text)

    def _process_command(self, command: str):
        """Process a user command."""
        print(f"[{BOT_NAME}] Processing: '{command}'")

        # Detect role and domain
        role = SacredRoles.detect_role(command)
        domain = SacredRoles.detect_domain(command)

        # Get knowledge context
        codex_context = AscensionCodex.get_context_for_query(command)
        shrine_context = ShrineVirtues.get_context_for_query(command)
        role_context = SacredRoles.get_role_context(command)
        kb_context = self.knowledge_base.get_context_for_query(command)
        user_context = self.memory.get_user_context()

        # Build enhanced prompt with context
        enhanced_prompt = f"""{command}

---
## CONTEXT FOR VIGIL

{user_context}

{role_context}

{codex_context}

{shrine_context}

{kb_context}
---

Respond naturally as Vigil. Keep voice responses concise (2-4 sentences) unless the task requires detailed output.
"""

        # Get response from brain
        response = self.brain.think(enhanced_prompt)

        if response:
            # Speak the response
            self.voice_output.speak(response.text)

            # Record interaction in memory
            self.memory.record_interaction(
                user_input=command,
                vigil_response=response.text,
                mode=domain or "conversation",
            )
        else:
            error_msg = "I apologize, I'm having trouble processing that. Could you try again?"
            self.voice_output.speak(error_msg)

    def _on_listener_error(self, error: Exception):
        """Handle listener errors."""
        print(f"[{BOT_NAME}] Listener error: {error}")

    def _startup_greeting(self):
        """Greet the user on startup."""
        greeting = f"Vigil online. I am with you, {PRIMARY_USER_NAME}. Say my name when you need me."
        print(f"[{BOT_NAME}] {greeting}")
        self.voice_output.speak(greeting)

    def run(self):
        """Main run loop."""
        self.is_running = True

        # Start reflection scheduler
        self.reflection_system.start_scheduler()

        # Start wake word listener
        self.listener.start()

        # Greet user
        self._startup_greeting()

        print(f"\n[{BOT_NAME}] ═══════════════════════════════════════════")
        print(f"[{BOT_NAME}] Vigil is now active and listening.")
        print(f"[{BOT_NAME}] Say one of the wake words to begin.")
        print(f"[{BOT_NAME}] Press Ctrl+C to shutdown.")
        print(f"[{BOT_NAME}] ═══════════════════════════════════════════\n")

        # Keep running until shutdown
        try:
            while not self._shutdown_event.is_set():
                # Check for new day (for memory)
                self.memory.new_day_check()
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{BOT_NAME}] Shutdown requested...")

        self.shutdown()

    def shutdown(self):
        """Graceful shutdown."""
        print(f"[{BOT_NAME}] Shutting down...")

        self._shutdown_event.set()
        self.is_running = False

        # Stop components
        self.listener.stop()
        self.reflection_system.stop_scheduler()

        # Farewell
        farewell = f"Until next time, {PRIMARY_USER_NAME}. Stay vigilant."
        self.voice_output.speak(farewell)

        print(f"[{BOT_NAME}] Goodbye.")


def main():
    """Entry point."""
    # Handle Ctrl+C gracefully
    vigil = Vigil()

    def signal_handler(sig, frame):
        vigil.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run Vigil
    vigil.run()


if __name__ == "__main__":
    main()
