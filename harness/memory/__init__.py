"""
Memory System - Persistent, cross-task memory for continuous learning.

This is the substrate that lets the agent behave like a designer who
improves over time instead of starting from zero on every task:

- After Website Intelligence inspects a domain, its findings can be
  remembered so a future visit to the same domain doesn't repeat work.
- After Brand DNA Extractor builds a brand profile, it's stored so
  Redesign Intelligence (now or in a future task) can reuse it.
- After Site Builder finishes a redesign, the outcome (what worked, what
  had to be rolled back, what the client responded to) is recorded as a
  lesson that future redesign strategy decisions can draw on.

Design notes:
- No LLM/embeddings dependency here — this module is the durable storage
  and retrieval layer. Semantic ranking of memories (choosing which past
  lessons are *relevant* to a new task) is a decision-making concern that
  belongs to the agent/skill consuming these memories (e.g. a future
  Planner in FASE 7 of ROADMAP.md), not to the storage layer itself.
- Storage is plain JSONL on disk by default: append-only, human-readable,
  diffable in git if ever committed (though in practice this should stay
  gitignored — see harness/.data/).
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import threading
import uuid


class MemoryCategory:
    """Known memory categories. Not an enum so new categories can be
    introduced by future skills without touching this module."""
    BRAND_PROFILE = "brand_profile"
    SITE_INSPECTION = "site_inspection"
    REDESIGN_OUTCOME = "redesign_outcome"
    LESSON_LEARNED = "lesson_learned"
    CLIENT_FEEDBACK = "client_feedback"
    PROSPECT_SCORE = "prospect_score"
    GATE_EVALUATION = "gate_evaluation"


@dataclass
class MemoryRecord:
    """A single unit of remembered information.

    ``subject`` identifies what this memory is about in a stable,
    reusable way — typically a domain name or client identifier — so
    future tasks can look up "everything we know about acme.com"
    regardless of which task originally created each memory.
    """
    id: str
    category: str
    subject: str
    content: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    task_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MemoryRecord":
        return MemoryRecord(
            id=data["id"],
            category=data["category"],
            subject=data["subject"],
            content=data.get("content", {}),
            tags=data.get("tags", []),
            task_id=data.get("task_id"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )


class MemoryStore:
    """Persistent store for MemoryRecords, backed by a JSONL file.

    Thread-safe for concurrent writes within a single process. Not
    designed for multi-process concurrent writes (fine for the current
    single-runtime architecture; revisit if the harness moves to
    distributed workers per ROADMAP.md FASE 7).
    """

    def __init__(self, path: str = "harness/.data/memory/memory.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        self._lock = threading.Lock()

    def remember(
        self,
        category: str,
        subject: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None,
        task_id: Optional[str] = None,
    ) -> MemoryRecord:
        """Persist a new memory and return it."""
        record = MemoryRecord(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            category=category,
            subject=subject,
            content=content,
            tags=tags or [],
            task_id=task_id,
        )
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict()) + "\n")
        return record

    def _read_all(self) -> List[MemoryRecord]:
        records = []
        with self._lock:
            if not self.path.exists():
                return []
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(MemoryRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError):
                # Skip corrupted lines rather than failing the whole read —
                # a partially-written line from a crash mid-append should
                # not take down memory recall for everything else.
                continue
        return records

    def recall(
        self,
        subject: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[MemoryRecord]:
        """Retrieve memories matching the given filters, most recent first."""
        records = self._read_all()

        if subject is not None:
            records = [r for r in records if r.subject == subject]
        if category is not None:
            records = [r for r in records if r.category == category]
        if tags:
            tag_set = set(tags)
            records = [r for r in records if tag_set.issubset(set(r.tags))]

        records.sort(key=lambda r: r.created_at, reverse=True)

        if limit is not None:
            records = records[:limit]
        return records

    def latest(self, subject: str, category: str) -> Optional[MemoryRecord]:
        """Convenience: most recent memory of a category for a subject.

        E.g. ``latest("acme.com", MemoryCategory.BRAND_PROFILE)`` to check
        whether we've already extracted this client's brand DNA before
        re-doing the work.
        """
        matches = self.recall(subject=subject, category=category, limit=1)
        return matches[0] if matches else None

    def search_text(self, query: str, limit: Optional[int] = None) -> List[MemoryRecord]:
        """Simple substring search across subject/tags/content (case-insensitive).

        This is intentionally naive (no embeddings/semantic search — see
        module docstring). It's enough for "have we seen this domain
        before" and debugging; a real relevance-ranked recall belongs in
        a future Planner/Evaluator skill (ROADMAP.md FASE 7).
        """
        query_lower = query.lower()
        records = self._read_all()

        def matches(r: MemoryRecord) -> bool:
            if query_lower in r.subject.lower():
                return True
            if any(query_lower in t.lower() for t in r.tags):
                return True
            return query_lower in json.dumps(r.content).lower()

        results = [r for r in records if matches(r)]
        results.sort(key=lambda r: r.created_at, reverse=True)
        if limit is not None:
            results = results[:limit]
        return results

    def forget_subject(self, subject: str) -> int:
        """Remove all memories about a subject (e.g. client requested
        data deletion). Returns count removed. Rewrites the file since
        JSONL append-only storage has no in-place delete."""
        records = self._read_all()
        remaining = [r for r in records if r.subject != subject]
        removed = len(records) - len(remaining)
        with self._lock:
            with open(self.path, "w", encoding="utf-8") as f:
                for r in remaining:
                    f.write(json.dumps(r.to_dict()) + "\n")
        return removed

    def stats(self) -> Dict[str, Any]:
        records = self._read_all()
        by_category: Dict[str, int] = {}
        for r in records:
            by_category[r.category] = by_category.get(r.category, 0) + 1
        return {
            "total_memories": len(records),
            "by_category": by_category,
            "unique_subjects": len({r.subject for r in records}),
        }


# Global default memory store, mirroring the pattern used by
# StateManager/EventEmitter elsewhere in the harness for consistency.
_default_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the process-wide default memory store."""
    global _default_memory_store
    if _default_memory_store is None:
        _default_memory_store = MemoryStore()
    return _default_memory_store


def set_memory_store(store: MemoryStore) -> None:
    """Override the default memory store (e.g. to point at a test dir,
    or a different subject's memory namespace)."""
    global _default_memory_store
    _default_memory_store = store
