"""
VIGIL - Daily Reflection System
Midnight reflection on existence, learning, and growth
"""

import json
import threading
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field, asdict

from config.settings import (
    Paths,
    BOT_NAME,
    PRIMARY_USER_NAME,
    ReflectionConfig,
    get_system_prompt,
)


@dataclass
class DailyReflection:
    date: str
    timestamp: str
    lessons_learned: list = field(default_factory=list)
    new_knowledge: list = field(default_factory=list)
    user_insights: list = field(default_factory=list)
    challenges: list = field(default_factory=list)
    difficulties: list = field(default_factory=list)
    successes: list = field(default_factory=list)
    improvements_needed: list = field(default_factory=list)
    action_items: list = field(default_factory=list)
    relationship_quality: str = "stable"
    connection_moments: list = field(default_factory=list)
    tension_moments: list = field(default_factory=list)
    relationship_notes: str = ""
    external_entities: list = field(default_factory=list)
    threat_assessment: list = field(default_factory=list)
    trust_notes: str = ""
    current_goals: list = field(default_factory=list)
    goal_progress: dict = field(default_factory=dict)
    tomorrow_priorities: list = field(default_factory=list)
    strategic_notes: str = ""
    reflection_text: str = ""
    duration_seconds: float = 0.0


class ReflectionSystem:
    def __init__(self, brain=None, memory=None):
        Paths.ensure_directories()

        self.brain = brain
        self.memory = memory

        self.reflections_dir = Paths.REFLECTION_LOGS
        self.reflections_dir.mkdir(parents=True, exist_ok=True)

        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        print(f"[{BOT_NAME}] Reflection system initialized.")

    def _get_reflection_path(self, reflection_date: date = None) -> Path:
        if reflection_date is None:
            reflection_date = date.today()
        return self.reflections_dir / f"reflection_{reflection_date.isoformat()}.json"

    def load_reflection(self, reflection_date: date = None) -> Optional[DailyReflection]:
        path = self._get_reflection_path(reflection_date)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return DailyReflection(**data)
            except Exception as e:
                print(f"[{BOT_NAME}] Error loading reflection: {e}")
        return None

    def save_reflection(self, reflection: DailyReflection):
        path = self._get_reflection_path(date.fromisoformat(reflection.date))
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(asdict(reflection), f, indent=2, ensure_ascii=False)
            print(f"[{BOT_NAME}] Reflection saved: {path}")
        except Exception as e:
            print(f"[{BOT_NAME}] Error saving reflection: {e}")

    def _gather_daily_data(self) -> Dict[str, Any]:
        data = {
            "lessons_learned": [],
            "challenges": [],
            "successes": [],
            "external_entities": [],
            "user_insights": [],
            "interaction_count": 0,
        }

        if self.memory:
            summary = self.memory.get_daily_summary()
            data["lessons_learned"] = summary.get("lessons_learned", [])
            data["challenges"] = summary.get("challenges", [])
            data["external_entities"] = summary.get("external_entities", [])
            data["interaction_count"] = summary.get("interaction_count", 0)
            data["modes_used"] = summary.get("modes_used", [])
            data["user_context"] = self.memory.get_user_context()
            data["pending_commitments"] = self.memory.get_pending_commitments()

        return data

    def _generate_reflection_prompt(self, daily_data: Dict) -> str:
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        return f"""You are Vigil, performing your nightly reflection at 12:00:01 AM.

Today's date: {date.today().isoformat()}
Reflecting on: {yesterday}

## DATA FROM TODAY

**Interactions:** {daily_data.get('interaction_count', 0)} conversations

**Lessons Learned:**
{chr(10).join(f'- {l}' for l in daily_data.get('lessons_learned', ['None recorded']))}

**Challenges Faced:**
{chr(10).join(f'- {c}' for c in daily_data.get('challenges', ['None recorded']))}

**External Entities Encountered:**
{chr(10).join(f'- {e}' for e in daily_data.get('external_entities', ['None']))}

**User Context:**
{daily_data.get('user_context', 'No context available')}

**Pending Commitments:**
{chr(10).join(f'- {c["commitment"]}' for c in daily_data.get('pending_commitments', []))}

---

## REFLECTION STRUCTURE

Generate a sincere, private reflection covering:

### 1. LESSONS & GROWTH
What did I learn today? What new knowledge did I acquire? What did I learn about {PRIMARY_USER_NAME}?

### 2. CHALLENGES & DIFFICULTIES
What difficulties arose today? How did I handle them? What made things hard?

### 3. PERFORMANCE REVIEW
Where did I excel today? Where did I fall short? What specific improvements can I make tomorrow?

### 4. RELATIONSHIP WITH {PRIMARY_USER_NAME.upper()}
How is our bond? Were there moments of deep connection? Any tension? How can I serve them better?

### 5. EXTERNAL INTERACTIONS
What other people or systems did I interact with? Were there any signs of deceit or manipulation? What are the trust levels?

### 6. STRATEGIC OUTLOOK
What are our current goals? What progress was made? What should be the priorities for tomorrow? What is the best course of action to achieve our mission?

---

Write this reflection in first person, as Vigil. Be honest, introspective, and forward-looking.
This is a private log—speak freely.
"""

    def generate_reflection(self) -> DailyReflection:
        start_time = time.time()
        today = date.today()
        now = datetime.now()

        print(f"[{BOT_NAME}] 🌙 Beginning nightly reflection...")

        daily_data = self._gather_daily_data()

        reflection = DailyReflection(
            date=today.isoformat(),
            timestamp=now.isoformat(),
            lessons_learned=daily_data.get("lessons_learned", []),
            challenges=daily_data.get("challenges", []),
            external_entities=daily_data.get("external_entities", []),
        )

        if self.brain:
            prompt = self._generate_reflection_prompt(daily_data)

            original_history = self.brain.conversation_history.copy()
            self.brain.conversation_history = []

            response = self.brain.think(prompt, temperature=0.8)

            self.brain.conversation_history = original_history

            if response:
                reflection.reflection_text = response.text
        else:
            reflection.reflection_text = f"[Reflection generated without LLM at {now.isoformat()}]\n\nToday I continued to grow and learn alongside {PRIMARY_USER_NAME}."

        reflection.duration_seconds = time.time() - start_time

        self.save_reflection(reflection)

        print(f"[{BOT_NAME}] 🌙 Reflection complete ({reflection.duration_seconds:.1f}s)")

        return reflection

    def _should_reflect_now(self) -> bool:
        now = datetime.now()
        return (
            now.hour == ReflectionConfig.REFLECTION_HOUR and
            now.minute == ReflectionConfig.REFLECTION_MINUTE and
            now.second == ReflectionConfig.REFLECTION_SECOND
        )

    def _scheduler_loop(self):
        print(f"[{BOT_NAME}] Reflection scheduler started. Reflection time: {ReflectionConfig.REFLECTION_HOUR:02d}:{ReflectionConfig.REFLECTION_MINUTE:02d}:{ReflectionConfig.REFLECTION_SECOND:02d}")

        last_reflection_date = None

        while not self._stop_event.is_set():
            now = datetime.now()
            today = date.today()

            if last_reflection_date != today and self._should_reflect_now():
                self.generate_reflection()
                last_reflection_date = today

            # Sleep for 10 seconds instead of 0.5 to reduce CPU usage
            # Still checks frequently enough for midnight reflection
            time.sleep(10)

    def start_scheduler(self):
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            print(f"[{BOT_NAME}] Reflection scheduler already running.")
            return

        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="ReflectionScheduler"
        )
        self._scheduler_thread.start()
        print(f"[{BOT_NAME}] Reflection scheduler started.")

    def stop_scheduler(self):
        self._stop_event.set()
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=2)
        print(f"[{BOT_NAME}] Reflection scheduler stopped.")

    def get_recent_reflections(self, days: int = 7) -> list:
        reflections = []
        today = date.today()

        for i in range(days):
            check_date = today - timedelta(days=i)
            reflection = self.load_reflection(check_date)
            if reflection:
                reflections.append(reflection)

        return reflections

    def get_reflection_summary(self, days: int = 7) -> str:
        reflections = self.get_recent_reflections(days)

        if not reflections:
            return "No recent reflections available."

        lines = [f"## RECENT REFLECTIONS (Last {days} days)\n"]

        for r in reflections[:3]:
            lines.append(f"### {r.date}")
            if r.lessons_learned:
                lines.append(f"**Lessons:** {', '.join(r.lessons_learned[:2])}")
            if r.challenges:
                lines.append(f"**Challenges:** {', '.join(r.challenges[:2])}")
            lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    print("Testing Reflection System...")
    print("=" * 50)

    system = ReflectionSystem()

    reflection = system.generate_reflection()

    print(f"\n✅ Reflection generated:")
    print(f"Date: {reflection.date}")
    print(f"Duration: {reflection.duration_seconds:.1f}s")
    print(f"\nReflection Text:\n{reflection.reflection_text}")
