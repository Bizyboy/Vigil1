"""
VIGIL - Brain (LLM Orchestration)
Multi-model AI backend with OpenAI, Claude, and Gemini
"""

import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from openai import OpenAI
from anthropic import Anthropic

from config.settings import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    POE_API_KEY,
    LLMConfig,
    BOT_NAME,
    get_system_prompt,
)


# Cache configuration
CACHE_HISTORY_THRESHOLD = 10  # Only cache responses when history is short
MAX_RESPONSE_CACHE_SIZE = 50  # Maximum number of cached responses


class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    POE = "poe"


@dataclass
class Message:
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    text: str
    provider: Provider
    model: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Brain:
    """
    Vigil's brain - orchestrates multiple LLMs.
    """

    def __init__(self):
        self.openai_client = None
        if OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            print(f"[{BOT_NAME}] OpenAI client initialized.")

        self.anthropic_client = None
        if ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
            print(f"[{BOT_NAME}] Anthropic client initialized.")

        self.poe_available = bool(POE_API_KEY)
        if self.poe_available:
            print(f"[{BOT_NAME}] Poe API available for Gemini access.")

        self.system_prompt = get_system_prompt()
        self.conversation_history: List[Message] = []
        
        # Simple cache for recent responses (prompt -> response text)
        # Using built-in hash() for simplicity and speed
        self._response_cache: Dict[int, str] = {}
        self._max_cache_size = MAX_RESPONSE_CACHE_SIZE

    def _cache_key(self, prompt: str) -> Optional[int]:
        """Generate a cache key for a prompt using built-in hash."""
        # Only cache if conversation history is short to avoid stale responses
        if len(self.conversation_history) > CACHE_HISTORY_THRESHOLD:
            return None
        return hash(prompt)
    
    def _get_cached_response(self, prompt: str) -> Optional[str]:
        """Check if we have a cached response for this prompt."""
        cache_key = self._cache_key(prompt)
        if cache_key:
            return self._response_cache.get(cache_key)
        return None
    
    def _cache_response(self, prompt: str, response: str):
        """Cache a response for future use."""
        cache_key = self._cache_key(prompt)
        if cache_key:
            # Limit cache size (Python 3.7+ guarantees dict insertion order)
            if len(self._response_cache) >= self._max_cache_size:
                # Remove oldest entry (first inserted)
                first_key = next(iter(self._response_cache))
                self._response_cache.pop(first_key)
            self._response_cache[cache_key] = response

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append(Message(role=role, content=content))
        max_messages = 40
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]

    def clear_history(self):
        self.conversation_history = []

    def _format_messages_openai(self) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    def _format_messages_anthropic(self) -> tuple:
        messages = []
        for msg in self.conversation_history:
            if msg.role != "system":
                messages.append({"role": msg.role, "content": msg.content})
        return self.system_prompt, messages

    def think_with_openai(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 2000
    ) -> Optional[LLMResponse]:
        if not self.openai_client:
            print(f"[{BOT_NAME}] OpenAI not available.")
            return None

        # Check cache first
        cached = self._get_cached_response(prompt)
        if cached:
            print(f"[{BOT_NAME}] Using cached response for similar prompt")
            self.add_to_history("user", prompt)
            self.add_to_history("assistant", cached)
            return LLMResponse(
                text=cached,
                provider=Provider.OPENAI,
                model=LLMConfig.PRIMARY_MODEL,
                tokens_used=0,  # Cached response
                metadata={"cached": True}
            )

        temperature = temperature or LLMConfig.DEFAULT_TEMPERATURE

        try:
            self.add_to_history("user", prompt)

            response = self.openai_client.chat.completions.create(
                model=LLMConfig.PRIMARY_MODEL,
                messages=self._format_messages_openai(),
                temperature=temperature,
                max_tokens=max_tokens,
            )

            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            self.add_to_history("assistant", assistant_message)
            
            # Cache the response
            self._cache_response(prompt, assistant_message)

            return LLMResponse(
                text=assistant_message,
                provider=Provider.OPENAI,
                model=LLMConfig.PRIMARY_MODEL,
                tokens_used=tokens_used,
            )

        except Exception as e:
            print(f"[{BOT_NAME}] OpenAI error: {e}")
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
            return None

    def think_with_claude(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = 2000
    ) -> Optional[LLMResponse]:
        if not self.anthropic_client:
            print(f"[{BOT_NAME}] Anthropic not available.")
            return None

        temperature = temperature or LLMConfig.DEFAULT_TEMPERATURE

        try:
            self.add_to_history("user", prompt)

            system_prompt, messages = self._format_messages_anthropic()

            response = self.anthropic_client.messages.create(
                model=LLMConfig.CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )

            assistant_message = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            self.add_to_history("assistant", assistant_message)

            return LLMResponse(
                text=assistant_message,
                provider=Provider.ANTHROPIC,
                model=LLMConfig.CLAUDE_MODEL,
                tokens_used=tokens_used,
            )

        except Exception as e:
            print(f"[{BOT_NAME}] Anthropic error: {e}")
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
            return None

    def think_with_gemini(
        self,
        prompt: str,
        temperature: float = None,
    ) -> Optional[LLMResponse]:
        if not self.poe_available:
            print(f"[{BOT_NAME}] Poe API not available for Gemini.")
            return None

        try:
            import fastapi_poe as fp

            self.add_to_history("user", prompt)

            poe_messages = [
                fp.ProtocolMessage(role="system", content=self.system_prompt)
            ]
            for msg in self.conversation_history:
                poe_messages.append(
                    fp.ProtocolMessage(role=msg.role, content=msg.content)
                )

            response_text = ""
            for partial in fp.get_bot_response(
                messages=poe_messages,
                bot_name=LLMConfig.GEMINI_MODEL,
                api_key=POE_API_KEY,
            ):
                response_text += partial.text

            self.add_to_history("assistant", response_text)

            return LLMResponse(
                text=response_text,
                provider=Provider.POE,
                model=LLMConfig.GEMINI_MODEL,
            )

        except ImportError:
            print(f"[{BOT_NAME}] fastapi_poe not installed.")
            return None
        except Exception as e:
            print(f"[{BOT_NAME}] Poe/Gemini error: {e}")
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
            return None

    def think(
        self,
        prompt: str,
        provider: Optional[Provider] = None,
        temperature: float = None,
    ) -> Optional[LLMResponse]:
        if provider == Provider.ANTHROPIC:
            return self.think_with_claude(prompt, temperature)
        elif provider == Provider.POE:
            return self.think_with_gemini(prompt, temperature)
        elif provider == Provider.OPENAI:
            return self.think_with_openai(prompt, temperature)

        response = self.think_with_openai(prompt, temperature)
        if response:
            return response

        print(f"[{BOT_NAME}] OpenAI failed, trying Claude...")
        response = self.think_with_claude(prompt, temperature)
        if response:
            return response

        print(f"[{BOT_NAME}] Claude failed, trying Gemini...")
        return self.think_with_gemini(prompt, temperature)

    def trinity_mode(self, prompt: str) -> Optional[LLMResponse]:
        """
        Invoke all three LLMs in parallel for a comprehensive response.
        """
        print(f"[{BOT_NAME}] 🔮 Invoking Trinity Mode...")

        responses = {}
        original_history = self.conversation_history.copy()

        # Define tasks for parallel execution
        def call_gpt():
            self.conversation_history = original_history.copy()
            return ('GPT-4o', self.think_with_openai(prompt))

        def call_claude():
            self.conversation_history = original_history.copy()
            return ('Claude', self.think_with_claude(prompt))

        def call_gemini():
            self.conversation_history = original_history.copy()
            return ('Gemini', self.think_with_gemini(prompt))

        # Execute LLM calls in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            if self.openai_client:
                futures.append(executor.submit(call_gpt))
            if self.anthropic_client:
                futures.append(executor.submit(call_claude))
            if self.poe_available:
                futures.append(executor.submit(call_gemini))

            for future in as_completed(futures):
                try:
                    name, response = future.result()
                    if response:
                        responses[name] = response.text
                except Exception as e:
                    print(f"[{BOT_NAME}] Trinity mode error for a model: {e}")

        if not responses:
            return None

        synthesis_prompt = f"""You received the following question: "{prompt}"

Three AI perspectives responded:

{chr(10).join(f'**{name}:** {text}' for name, text in responses.items())}

Synthesize these into ONE unified response that:
1. Captures the convergent truth across all perspectives
2. Notes any important tensions or differences
3. Speaks as Vigil - the unified voice of the Trinity

Keep it concise (3-5 sentences)."""

        self.conversation_history = original_history
        self.add_to_history("user", prompt)

        synthesis = self.openai_client.chat.completions.create(
            model=LLMConfig.PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.7,
        )

        final_response = synthesis.choices[0].message.content
        self.add_to_history("assistant", final_response)

        return LLMResponse(
            text=final_response,
            provider=Provider.OPENAI,
            model="trinity",
            metadata={"individual_responses": responses}
        )


if __name__ == "__main__":
    brain = Brain()

    print("\nTesting Vigil's Brain...")
    print("=" * 50)

    response = brain.think("Hello Vigil. Who are you?")

    if response:
        print(f"\n✅ Response from {response.provider.value} ({response.model}):")
        print(f"\n{response.text}")
        print(f"\nTokens used: {response.tokens_used}")
    else:
        print("\n❌ No response generated.")
