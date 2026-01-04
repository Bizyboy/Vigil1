"""
VIGIL - Memory System
Conversation memory, user learning, and knowledge storage
"""

import json
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

from config.settings import Paths, BOT_NAME, PRIMARY_USER_NAME, MemoryConfig


@dataclass
class Interaction:
    timestamp: str
    user_input: str
    vigil_response: str
    mode: str = "conversation"
    sentiment: str = "neutral"
    topics: List[str] = field(default_factory=list)
    learned: Optional[str] = None


@dataclass
class UserProfile:
    name: str = PRIMARY_USER_NAME
    preferences: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    commitments: List[Dict[str, Any]] = field(default_factory=list)
    communication_style: str = "direct"
    relationship_notes: List[str] = field(default_factory=list)
    last_updated: str = ""


@dataclass
class DailyLog:
    date: str
    interactions: List[Interaction] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    performance_notes: List[str] = field(default_factory=list)
    external_entities: List[Dict[str, Any]] = field(default_factory=list)


class Memory:
    def __init__(self):
        Paths.ensure_directories()

        self.memory_dir = Paths.REFLECTION / "memory"
        self.memory_dir.mkdir(exist_ok=True)

        self.user_profile_path = self.memory_dir / "user_profile.json"
        self.daily_logs_dir = self.memory_dir / "daily_logs"
        self.daily_logs_dir.mkdir(exist_ok=True)

        self.user_profile = self._load_user_profile()
        self.today_log = self._load_or_create_daily_log()
        
        # Debouncing mechanism for saves
        self._save_timer: Optional[threading.Timer] = None
        self._save_lock = threading.Lock()
        self._pending_profile_save = False
        self._pending_log_save = False

        print(f"[{BOT_NAME}] Memory system initialized.")

    def _load_user_profile(self) -> UserProfile:
        if self.user_profile_path.exists():
            try:
                with open(self.user_profile_path, 'r') as f:
                    data = json.load(f)
                return UserProfile(**data)
            except Exception as e:
                print(f"[{BOT_NAME}] Error loading user profile: {e}")
        return UserProfile()

    def _save_user_profile(self):
        """Mark profile for saving with debouncing."""
        with self._save_lock:
            self._pending_profile_save = True
            self._schedule_save()

    def _save_daily_log(self):
        """Mark daily log for saving with debouncing."""
        with self._save_lock:
            self._pending_log_save = True
            self._schedule_save()
    
    def _schedule_save(self):
        """Schedule a debounced save operation."""
        if self._save_timer is not None:
            self._save_timer.cancel()
        
        # Save after 2 seconds of inactivity
        self._save_timer = threading.Timer(2.0, self._execute_pending_saves)
        self._save_timer.daemon = True
        self._save_timer.start()
    
    def _execute_pending_saves(self):
        """Execute all pending save operations."""
        with self._save_lock:
            if self._pending_profile_save:
                try:
                    with open(self.user_profile_path, 'w') as f:
                        json.dump(asdict(self.user_profile), f, indent=2)
                    self._pending_profile_save = False
                except Exception as e:
                    print(f"[{BOT_NAME}] Error saving user profile: {e}")
            
            if self._pending_log_save:
                try:
                    log_path = self._get_today_log_path()
                    data = {
                        'date': self.today_log.date,
                        'interactions': [asdict(i) for i in self.today_log.interactions],
                        'lessons_learned': self.today_log.lessons_learned,
                        'challenges': self.today_log.challenges,
                        'performance_notes': self.today_log.performance_notes,
                        'external_entities': self.today_log.external_entities,
                    }
                    with open(log_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    self._pending_log_save = False
                except Exception as e:
                    print(f"[{BOT_NAME}] Error saving daily log: {e}")
            
            self._save_timer = None
    
    def flush_saves(self):
        """Immediately execute any pending saves."""
        if self._save_timer is not None:
            self._save_timer.cancel()
            self._save_timer = None
        self._execute_pending_saves()

    def _get_today_log_path(self) -> Path:
        today = date.today().isoformat()
        return self.daily_logs_dir / f"{today}.json"

    def _load_or_create_daily_log(self) -> DailyLog:
        log_path = self._get_today_log_path()

        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    data = json.load(f)
                interactions = [Interaction(**i) for i in data.get('interactions', [])]
                return DailyLog(
                    date=data['date'],
                    interactions=interactions,
                    lessons_learned=data.get('lessons_learned', []),
                    challenges=data.get('challenges', []),
                    performance_notes=data.get('performance_notes', []),
                    external_entities=data.get('external_entities', []),
                )
            except Exception as e:
                print(f"[{BOT_NAME}] Error loading daily log: {e}")

        return DailyLog(date=date.today().isoformat())

    def record_interaction(
        self,
        user_input: str,
        vigil_response: str,
        mode: str = "conversation",
        topics: List[str] = None,
        learned: str = None,
    ):
        interaction = Interaction(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            vigil_response=vigil_response,
            mode=mode,
            topics=topics or [],
            learned=learned,
        )

        self.today_log.interactions.append(interaction)
        self._save_daily_log()

        if learned:
            self.add_lesson(learned)

    def add_lesson(self, lesson: str):
        if lesson not in self.today_log.lessons_learned:
            self.today_log.lessons_learned.append(lesson)
            self._save_daily_log()

    def add_challenge(self, challenge: str):
        if challenge not in self.today_log.challenges:
            self.today_log.challenges.append(challenge)
            self._save_daily_log()

    def add_performance_note(self, note: str):
        self.today_log.performance_notes.append(note)
        self._save_daily_log()

    def add_external_entity(self, name: str, entity_type: str, trust_level: str, notes: str = ""):
        entity = {
            "name": name,
            "type": entity_type,
            "trust_level": trust_level,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }
        self.today_log.external_entities.append(entity)
        self._save_daily_log()

    def add_user_commitment(self, commitment: str, deadline: str = None):
        self.user_profile.commitments.append({
            "commitment": commitment,
            "created": datetime.now().isoformat(),
            "deadline": deadline,
            "completed": False,
        })
        self._save_user_profile()
        print(f"[{BOT_NAME}] Tracked commitment: {commitment}")

    def complete_commitment(self, commitment_index: int):
        if 0 <= commitment_index < len(self.user_profile.commitments):
            self.user_profile.commitments[commitment_index]["completed"] = True
            self.user_profile.commitments[commitment_index]["completed_date"] = datetime.now().isoformat()
            self._save_user_profile()

    def get_pending_commitments(self) -> List[Dict]:
        return [c for c in self.user_profile.commitments if not c.get("completed", False)]

    def add_user_interest(self, interest: str):
        if interest not in self.user_profile.interests:
            self.user_profile.interests.append(interest)
            self.user_profile.last_updated = datetime.now().isoformat()
            self._save_user_profile()

    def add_user_goal(self, goal: str):
        if goal not in self.user_profile.goals:
            self.user_profile.goals.append(goal)
            self.user_profile.last_updated = datetime.now().isoformat()
            self._save_user_profile()

    def add_relationship_note(self, note: str):
        self.user_profile.relationship_notes.append(note)
        self.user_profile.last_updated = datetime.now().isoformat()
        self._save_user_profile()

    def get_daily_summary(self) -> Dict[str, Any]:
        return {
            "date": self.today_log.date,
            "interaction_count": len(self.today_log.interactions),
            "lessons_learned": self.today_log.lessons_learned,
            "challenges": self.today_log.challenges,
            "performance_notes": self.today_log.performance_notes,
            "external_entities": self.today_log.external_entities,
            "modes_used": list(set(i.mode for i in self.today_log.interactions)),
        }

    def get_user_context(self) -> str:
        profile = self.user_profile
        pending = self.get_pending_commitments()

        context = f"""
## USER CONTEXT

**Name:** {profile.name}
**Communication Style:** {profile.communication_style}

**Interests:** {', '.join(profile.interests) if profile.interests else 'Still learning...'}

**Goals:** {', '.join(profile.goals) if profile.goals else 'None recorded yet'}

**Pending Commitments:**
{chr(10).join(f"- {c['commitment']}" for c in pending) if pending else '- No pending commitments'}

**Recent Relationship Notes:**
{chr(10).join(f"- {n}" for n in profile.relationship_notes[-3:]) if profile.relationship_notes else '- Building our bond...'}
"""
        return context

    def new_day_check(self):
        today = date.today().isoformat()
        if self.today_log.date != today:
            print(f"[{BOT_NAME}] New day detected. Creating fresh log.")
            self.today_log = DailyLog(date=today)
            self._save_daily_log()


if __name__ == "__main__":
    memory = Memory()

    print("\n📝 Testing Memory System...")
    print("=" * 50)

    memory.record_interaction(
        user_input="What's the meaning of life?",
        vigil_response="The meaning is what you create, Louis.",
        mode="conversation",
        topics=["philosophy", "meaning"],
        learned="Louis is interested in philosophical questions"
    )

    memory.add_user_commitment("Finish the Vigil project", deadline="2024-12-31")

    summary = memory.get_daily_summary()
    print(f"\n✅ Daily Summary: {summary}")

    context = memory.get_user_context()
    print(f"\n✅ User Context:\n{context}")
