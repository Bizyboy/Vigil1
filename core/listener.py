"""
VIGIL - Wake Word Listener
Always-on audio monitoring for wake word detection
"""

import time
import threading
import queue
from typing import Callable, Optional
import speech_recognition as sr

from config.settings import WAKE_WORDS, VoiceConfig, BOT_NAME


class WakeWordListener:
    """
    Continuously listens for wake words and triggers callback when detected.
    Uses speech_recognition with Google's free speech-to-text for wake word detection.
    """

    def __init__(self, on_wake: Callable[[str], None], on_error: Optional[Callable[[Exception], None]] = None):
        self.on_wake = on_wake
        self.on_error = on_error or self._default_error_handler
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=VoiceConfig.SAMPLE_RATE)
        self.is_listening = False
        self._stop_event = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None

        self._calibrate_microphone()

    def _calibrate_microphone(self):
        print(f"[{BOT_NAME}] Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"[{BOT_NAME}] Microphone calibrated. Ready to listen.")

    def _default_error_handler(self, error: Exception):
        print(f"[{BOT_NAME}] Listener error: {error}")

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _contains_wake_word(self, text: str) -> bool:
        normalized = self._normalize_text(text)
        for wake_word in WAKE_WORDS:
            if wake_word.lower() in normalized:
                return True
        return False

    def _extract_command(self, text: str) -> str:
        normalized = self._normalize_text(text)
        for wake_word in sorted(WAKE_WORDS, key=len, reverse=True):
            wake_lower = wake_word.lower()
            if wake_lower in normalized:
                idx = normalized.find(wake_lower)
                command = text[idx + len(wake_word):].strip()
                for word in [",", ".", "?", "!"]:
                    command = command.strip(word)
                return command.strip()
        return text

    def _listen_loop(self):
        print(f"[{BOT_NAME}] Wake word listener active. Say one of: {', '.join(WAKE_WORDS)}")

        while not self._stop_event.is_set():
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=10
                    )

                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"[{BOT_NAME}] Heard: '{text}'")

                    if self._contains_wake_word(text):
                        command = self._extract_command(text)
                        print(f"[{BOT_NAME}] Wake word detected! Command: '{command}'")
                        self.on_wake(text)

                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.on_error(Exception(f"Speech recognition service error: {e}"))
                    time.sleep(1)

            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                self.on_error(e)
                time.sleep(0.5)

    def start(self):
        if self.is_listening:
            print(f"[{BOT_NAME}] Listener already running.")
            return

        self._stop_event.clear()
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        self.is_listening = True
        print(f"[{BOT_NAME}] Listener started.")

    def stop(self):
        if not self.is_listening:
            return

        self._stop_event.set()
        if self._listen_thread:
            self._listen_thread.join(timeout=3)
        self.is_listening = False
        print(f"[{BOT_NAME}] Listener stopped.")

    def restart(self):
        self.stop()
        time.sleep(0.5)
        self._calibrate_microphone()
        self.start()


class PushToTalkListener:
    """Alternative listener using push-to-talk."""

    def __init__(self, on_speech: Callable[[str], None], trigger_key: str = "space"):
        self.on_speech = on_speech
        self.trigger_key = trigger_key
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=VoiceConfig.SAMPLE_RATE)
        self.is_active = False

    def record_once(self) -> Optional[str]:
        print(f"[{BOT_NAME}] Listening...")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, phrase_time_limit=30)

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"[{BOT_NAME}] You said: '{text}'")
            return text
        except sr.UnknownValueError:
            print(f"[{BOT_NAME}] Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"[{BOT_NAME}] Recognition error: {e}")
            return None


if __name__ == "__main__":
    def on_wake(phrase):
        print(f"\n🔔 WAKE WORD DETECTED: '{phrase}'\n")

    listener = WakeWordListener(on_wake=on_wake)
    listener.start()

    try:
        print("Listening for wake words... Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()
