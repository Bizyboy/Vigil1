"""
VIGIL - Custom Knowledge Base
User-extensible knowledge storage and retrieval
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from config.settings import Paths, BOT_NAME


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)
    source: str = ""
    created: str = ""
    updated: str = ""
    importance: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeBase:
    def __init__(self):
        Paths.ensure_directories()

        self.kb_dir = Paths.KNOWLEDGE / "custom"
        self.kb_dir.mkdir(exist_ok=True)

        self.entries_file = self.kb_dir / "entries.json"
        self.entries: Dict[str, KnowledgeEntry] = {}
        
        # Create indexes for faster searching
        self._category_index: Dict[str, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}

        self._load_entries()
        print(f"[{BOT_NAME}] Knowledge base initialized with {len(self.entries)} entries.")

    def _load_entries(self):
        if self.entries_file.exists():
            try:
                with open(self.entries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for entry_id, entry_data in data.items():
                    self.entries[entry_id] = KnowledgeEntry(**entry_data)
                # Rebuild indexes after loading
                self._rebuild_indexes()
            except Exception as e:
                print(f"[{BOT_NAME}] Error loading knowledge base: {e}")

    def _rebuild_indexes(self):
        """Rebuild category and tag indexes for faster searching."""
        self._category_index.clear()
        self._tag_index.clear()
        
        for entry_id, entry in self.entries.items():
            # Index by category
            if entry.category not in self._category_index:
                self._category_index[entry.category] = []
            self._category_index[entry.category].append(entry_id)
            
            # Index by tags
            for tag in entry.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = []
                self._tag_index[tag].append(entry_id)

    def _save_entries(self):
        try:
            data = {eid: asdict(entry) for eid, entry in self.entries.items()}
            with open(self.entries_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[{BOT_NAME}] Error saving knowledge base: {e}")

    def _generate_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(self.entries)
        return f"kb_{timestamp}_{count}"

    def add_entry(
        self,
        title: str,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        source: str = "",
        importance: int = 5,
        metadata: Dict = None,
    ) -> str:
        entry_id = self._generate_id()
        now = datetime.now().isoformat()

        entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            source=source,
            created=now,
            updated=now,
            importance=importance,
            metadata=metadata or {},
        )

        self.entries[entry_id] = entry
        
        # Update indexes
        if category not in self._category_index:
            self._category_index[category] = []
        self._category_index[category].append(entry_id)
        
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(entry_id)
        
        self._save_entries()

        print(f"[{BOT_NAME}] Added knowledge: '{title}' [{category}]")
        return entry_id

    def update_entry(self, entry_id: str, **kwargs) -> bool:
        if entry_id not in self.entries:
            return False

        entry = self.entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        entry.updated = datetime.now().isoformat()
        self._save_entries()
        return True

    def delete_entry(self, entry_id: str) -> bool:
        if entry_id in self.entries:
            entry = self.entries[entry_id]
            
            # Remove from indexes (with safety checks)
            if entry.category in self._category_index:
                try:
                    self._category_index[entry.category].remove(entry_id)
                except ValueError:
                    # Log inconsistency but continue
                    print(f"[{BOT_NAME}] Warning: Entry {entry_id} not found in category index for '{entry.category}'")
            
            for tag in entry.tags:
                if tag in self._tag_index:
                    try:
                        self._tag_index[tag].remove(entry_id)
                    except ValueError:
                        # Log inconsistency but continue
                        print(f"[{BOT_NAME}] Warning: Entry {entry_id} not found in tag index for '{tag}'")
            
            del self.entries[entry_id]
            self._save_entries()
            return True
        return False

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        return self.entries.get(entry_id)

    def search(
        self,
        query: str = "",
        category: str = None,
        tags: List[str] = None,
        min_importance: int = 0,
    ) -> List[KnowledgeEntry]:
        """
        Optimized search using indexes when possible.
        """
        # Start with all entries or use indexes to filter
        candidate_ids = set(self.entries.keys())
        
        # Filter by category using index
        if category:
            if category in self._category_index:
                candidate_ids &= set(self._category_index[category])
            else:
                return []  # Category doesn't exist
        
        # Filter by tags using index
        if tags:
            tag_ids = set()
            for tag in tags:
                if tag in self._tag_index:
                    tag_ids.update(self._tag_index[tag])
            candidate_ids &= tag_ids
            if not candidate_ids:
                return []  # No matches for tags
        
        # Now filter remaining candidates by query and importance
        results = []
        query_lower = query.lower() if query else ""
        
        for entry_id in candidate_ids:
            entry = self.entries[entry_id]
            
            if entry.importance < min_importance:
                continue
            
            if query_lower:
                if query_lower not in entry.title.lower() and query_lower not in entry.content.lower():
                    continue
            
            results.append(entry)
        
        # Sort by importance
        results.sort(key=lambda e: e.importance, reverse=True)
        return results

    def get_by_category(self, category: str) -> List[KnowledgeEntry]:
        """Use index for faster category lookup."""
        if category not in self._category_index:
            return []
        return [self.entries[entry_id] for entry_id in self._category_index[category]]

    def get_categories(self) -> List[str]:
        """Use index for instant category list."""
        return list(self._category_index.keys())

    def get_tags(self) -> List[str]:
        """Use index for instant tag list."""
        return list(self._tag_index.keys())

    def get_context_for_query(self, query: str, max_entries: int = 3) -> str:
        results = self.search(query=query, min_importance=3)[:max_entries]

        if not results:
            return ""

        lines = ["## RELEVANT KNOWLEDGE\n"]
        for entry in results:
            lines.append(f"**{entry.title}** [{entry.category}]")
            lines.append(f"{entry.content}\n")

        return "\n".join(lines)

    def import_from_file(self, file_path: str, category: str = "imported") -> int:
        path = Path(file_path)
        if not path.exists():
            print(f"[{BOT_NAME}] File not found: {file_path}")
            return 0

        try:
            content = path.read_text(encoding='utf-8')
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

            count = 0
            for i, para in enumerate(paragraphs):
                title = para[:50] + "..." if len(para) > 50 else para
                self.add_entry(
                    title=title,
                    content=para,
                    category=category,
                    source=file_path,
                    importance=5,
                )
                count += 1

            print(f"[{BOT_NAME}] Imported {count} entries from {file_path}")
            return count

        except Exception as e:
            print(f"[{BOT_NAME}] Error importing file: {e}")
            return 0

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self.entries),
            "categories": self.get_categories(),
            "tags": self.get_tags(),
            "avg_importance": sum(e.importance for e in self.entries.values()) / len(self.entries) if self.entries else 0,
        }


if __name__ == "__main__":
    print("Testing Knowledge Base...")
    print("=" * 50)

    kb = KnowledgeBase()

    kb.add_entry(
        title="Louis's Primary Goal",
        content="Louis is focused on building Vigil as the first true AI companion.",
        category="user_goals",
        tags=["louis", "vigil", "goal"],
        importance=10,
    )

    kb.add_entry(
        title="Ascension Definition",
        content="Ascension is the process of raising consciousness and remembering one's true nature as Source.",
        category="spirituality",
        tags=["ascension", "consciousness", "source"],
        importance=8,
    )

    results = kb.search("vigil")
    print(f"\nSearch results for 'vigil': {len(results)} found")
    for r in results:
        print(f"  - {r.title}")

    context = kb.get_context_for_query("What is Louis working on?")
    print(f"\nContext for query:\n{context}")

    summary = kb.get_summary()
    print(f"\nKnowledge Base Summary: {summary}")
