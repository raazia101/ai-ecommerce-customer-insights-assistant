"""
Week 9 - Memory Management

This module demonstrates three distinct kinds of information handling:

1. Session Context
   Temporary information belonging to the current conversation/session.

2. Durable User Memory
   Explicitly stored user preferences or facts that persist across sessions.

3. Knowledge Retrieval
   Information that should come from the existing Week 8 RAG system rather
   than from conversational memory.

The implementation is intentionally local and deterministic for the internship
demonstration. No external database or hosted memory service is required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEMORY_DIR = PROJECT_ROOT / "08_agents" / "artifacts"
MEMORY_FILE = MEMORY_DIR / "user_memory.json"

MAX_SESSION_TURNS = 20
MAX_MEMORY_ITEMS = 20
MAX_TEXT_LENGTH = 500


# ============================================================================
# Session Memory
# ============================================================================

@dataclass
class SessionMemory:
    """
    Temporary memory for the current conversation/session.

    Session memory is intentionally not durable. It exists only for the
    lifetime of the SessionMemory object.
    """

    session_id: str
    turns: list[dict[str, str]] = field(default_factory=list)

    def add_turn(self, role: str, content: str) -> None:
        """
        Add a conversation turn to the current session.

        Allowed roles:
            - user
            - assistant

        The number of stored turns is bounded by MAX_SESSION_TURNS.
        """

        if role not in {"user", "assistant"}:
            raise ValueError(
                "role must be either 'user' or 'assistant'"
            )

        if not isinstance(content, str):
            raise ValueError("content must be a string")

        content = content.strip()

        if not content:
            raise ValueError("content cannot be empty")

        if len(content) > MAX_TEXT_LENGTH:
            raise ValueError(
                f"content exceeds maximum length of {MAX_TEXT_LENGTH}"
            )

        self.turns.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only the most recent turns.
        self.turns = self.turns[-MAX_SESSION_TURNS:]

    def get_context(self) -> list[dict[str, str]]:
        """
        Return the current session conversation context.
        """

        return list(self.turns)

    def clear(self) -> None:
        """
        Clear all session context.
        """

        self.turns.clear()


# ============================================================================
# Durable User Memory
# ============================================================================

class DurableMemory:
    """
    Simple local JSON-backed durable memory store.

    The store is deliberately explicit:
    information is persisted only when remember() is called.

    This prevents arbitrary conversation text from automatically becoming
    long-term user memory.
    """

    def __init__(
        self,
        path: Path | str = MEMORY_FILE,
    ) -> None:
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._memory: dict[str, list[str]] = {}

        self._load()

    # ------------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------------

    def _load(self) -> None:
        """
        Load durable memory from disk.

        Missing files and malformed files are handled safely by starting
        with an empty memory store.
        """

        if not self.path.exists():
            self._memory = {}
            return

        try:
            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:
                raw_data = json.load(file)

        except (json.JSONDecodeError, OSError):
            self._memory = {}
            return

        if not isinstance(raw_data, dict):
            self._memory = {}
            return

        cleaned: dict[str, list[str]] = {}

        for user_id, memories in raw_data.items():

            if not isinstance(user_id, str):
                continue

            if not isinstance(memories, list):
                continue

            valid_memories: list[str] = []

            for memory in memories:

                if not isinstance(memory, str):
                    continue

                memory = memory.strip()

                if not memory:
                    continue

                if len(memory) > MAX_TEXT_LENGTH:
                    continue

                if memory not in valid_memories:
                    valid_memories.append(memory)

            if valid_memories:
                cleaned[user_id] = valid_memories[-MAX_MEMORY_ITEMS:]

        self._memory = cleaned

    def _save(self) -> None:
        """
        Persist the current memory store to disk.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self._memory,
                file,
                indent=2,
                ensure_ascii=False,
            )

    @staticmethod
    def _validate_user_id(user_id: str) -> str:
        """
        Validate a customer/user identifier.
        """

        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")

        user_id = user_id.strip().upper()

        if not user_id:
            raise ValueError("user_id cannot be empty")

        if len(user_id) > 50:
            raise ValueError(
                "user_id exceeds maximum length of 50"
            )

        return user_id

    @staticmethod
    def _validate_memory(memory: str) -> str:
        """
        Validate a durable memory item.
        """

        if not isinstance(memory, str):
            raise ValueError("memory must be a string")

        memory = memory.strip()

        if not memory:
            raise ValueError("memory cannot be empty")

        if len(memory) > MAX_TEXT_LENGTH:
            raise ValueError(
                f"memory exceeds maximum length of {MAX_TEXT_LENGTH}"
            )

        return memory

    # ------------------------------------------------------------------------
    # Public durable-memory operations
    # ------------------------------------------------------------------------

    def remember(
        self,
        user_id: str,
        memory: str,
    ) -> dict[str, Any]:
        """
        Explicitly store a durable memory for a user.

        Duplicate memories are not stored twice.
        The store is bounded by MAX_MEMORY_ITEMS.
        """

        user_id = self._validate_user_id(user_id)
        memory = self._validate_memory(memory)

        if user_id not in self._memory:
            self._memory[user_id] = []

        if memory not in self._memory[user_id]:
            self._memory[user_id].append(memory)

        self._memory[user_id] = (
            self._memory[user_id][-MAX_MEMORY_ITEMS:]
        )

        self._save()

        return {
            "success": True,
            "user_id": user_id,
            "memory": memory,
            "total_memories": len(self._memory[user_id]),
        }

    def recall(
        self,
        user_id: str,
    ) -> list[str]:
        """
        Retrieve all durable memories associated with a user.
        """

        user_id = self._validate_user_id(user_id)

        return list(
            self._memory.get(user_id, [])
        )

    def forget(
        self,
        user_id: str,
        memory: str,
    ) -> dict[str, Any]:
        """
        Remove one specific durable memory.
        """

        user_id = self._validate_user_id(user_id)
        memory = self._validate_memory(memory)

        memories = self._memory.get(user_id, [])

        if memory in memories:
            memories.remove(memory)

            if memories:
                self._memory[user_id] = memories
            else:
                self._memory.pop(user_id, None)

            self._save()

            return {
                "success": True,
                "user_id": user_id,
                "memory": memory,
                "removed": True,
            }

        return {
            "success": True,
            "user_id": user_id,
            "memory": memory,
            "removed": False,
        }

    def clear_user(
        self,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Clear all durable memories belonging to one user.
        """

        user_id = self._validate_user_id(user_id)

        existed = user_id in self._memory

        if existed:
            del self._memory[user_id]

        self._save()

        return {
            "success": True,
            "user_id": user_id,
            "cleared": existed,
        }


# ============================================================================
# Information Classification
# ============================================================================

def classify_information(
    information: str,
) -> str:
    """
    Classify information into the appropriate storage/retrieval mechanism.

    Returns one of:

        durable_memory
        session_context
        knowledge_retrieval
        application_context

    The classifier is intentionally deterministic for testing and
    demonstration purposes.
    """

    if not isinstance(information, str):
        raise ValueError("information must be a string")

    information = information.strip()

    if not information:
        raise ValueError("information cannot be empty")

    text = information.lower()

    # ------------------------------------------------------------------------
    # Durable user memory
    # ------------------------------------------------------------------------

    durable_phrases = [
        "remember",
        "my preference",
        "i prefer",
        "my name",
        "i like",
    ]

    if any(
        phrase in text
        for phrase in durable_phrases
    ):
        return "durable_memory"

    # ------------------------------------------------------------------------
    # Current conversation/session context
    # ------------------------------------------------------------------------

    session_phrases = [
        "previous message",
        "earlier in this conversation",
        "we discussed",
        "this conversation",
    ]

    if any(
        phrase in text
        for phrase in session_phrases
    ):
        return "session_context"

    # ------------------------------------------------------------------------
    # Knowledge retrieval / RAG
    # ------------------------------------------------------------------------

    knowledge_phrases = [
        "policy",
        "faq",
        "documentation",
        "return",
        "refund",
        "company policy",
    ]

    if any(
        phrase in text
        for phrase in knowledge_phrases
    ):
        return "knowledge_retrieval"

    # ------------------------------------------------------------------------
    # Application/customer context
    # ------------------------------------------------------------------------

    return "application_context"


# ============================================================================
# Demonstration
# ============================================================================

def run_demo() -> None:
    """
    Run a small demonstration of all memory categories.
    """

    print("=" * 70)
    print("MEMORY DEMONSTRATION")
    print("=" * 70)

    # ------------------------------------------------------------------------
    # Session memory demonstration
    # ------------------------------------------------------------------------

    session = SessionMemory(
        session_id="demo-session"
    )

    session.add_turn(
        "user",
        "What is my order status?",
    )

    session.add_turn(
        "assistant",
        "Your order is pending.",
    )

    print("\nSESSION CONTEXT:")
    print(session.get_context())

    # ------------------------------------------------------------------------
    # Durable memory demonstration
    # ------------------------------------------------------------------------

    demo_path = (
        MEMORY_DIR / "demo_memory.json"
    )

    # Ensure the demonstration starts clean.
    if demo_path.exists():
        demo_path.unlink()

    durable = DurableMemory(demo_path)

    durable.remember(
        "CUST-0001",
        "User prefers concise answers.",
    )

    print("\nDURABLE MEMORY:")
    print(durable.recall("CUST-0001"))

    # ------------------------------------------------------------------------
    # Classification demonstration
    # ------------------------------------------------------------------------

    examples = [
        "Remember that I prefer concise answers.",
        "We discussed my order earlier.",
        "What is the return policy?",
    ]

    print("\nCLASSIFICATION:")

    for example in examples:
        print(
            f"{example}\n"
            f"  -> {classify_information(example)}"
        )

    # ------------------------------------------------------------------------
    # Cleanup demonstration file
    # ------------------------------------------------------------------------

    if demo_path.exists():
        demo_path.unlink()

    print("\nDemo complete.")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    run_demo()