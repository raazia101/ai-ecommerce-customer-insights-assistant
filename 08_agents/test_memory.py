import importlib.util
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Load memory.py safely because 08_agents is not a valid Python package name.
# ---------------------------------------------------------------------------
MEMORY_PATH = Path(__file__).resolve().parent / "memory.py"

spec = importlib.util.spec_from_file_location(
    "memory_test_module",
    MEMORY_PATH,
)

memory = importlib.util.module_from_spec(spec)
sys.modules["memory_test_module"] = memory
spec.loader.exec_module(memory)


SessionMemory = memory.SessionMemory
DurableMemory = memory.DurableMemory
classify_information = memory.classify_information


# ---------------------------------------------------------------------------
# SessionMemory tests
# ---------------------------------------------------------------------------

def test_session_add_and_context():
    session = SessionMemory(session_id="test-session")

    session.add_turn("user", "Hello")
    session.add_turn("assistant", "Hi there")

    context = session.get_context()

    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Hello"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Hi there"


def test_session_clear():
    session = SessionMemory(session_id="test-session")

    session.add_turn("user", "Hello")
    session.clear()

    assert session.get_context() == []


def test_session_limits_turns():
    session = SessionMemory(session_id="test-session")

    for i in range(25):
        session.add_turn("user", f"Message {i}")

    context = session.get_context()

    assert len(context) == memory.MAX_SESSION_TURNS
    assert context[0]["content"] == "Message 5"
    assert context[-1]["content"] == "Message 24"


def test_session_rejects_invalid_role():
    session = SessionMemory(session_id="test-session")

    try:
        session.add_turn("system", "Invalid role")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_session_rejects_empty_content():
    session = SessionMemory(session_id="test-session")

    try:
        session.add_turn("user", "")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# DurableMemory tests
# ---------------------------------------------------------------------------

def test_durable_memory_remember_and_recall(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store = DurableMemory(memory_file)

    result = store.remember(
        "CUST-0001",
        "User prefers concise answers.",
    )

    assert result["success"] is True

    memories = store.recall("CUST-0001")

    assert memories == ["User prefers concise answers."]


def test_durable_memory_deduplicates(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store = DurableMemory(memory_file)

    store.remember("CUST-0001", "User prefers concise answers.")
    store.remember("CUST-0001", "User prefers concise answers.")

    memories = store.recall("CUST-0001")

    assert len(memories) == 1


def test_durable_memory_persists_to_disk(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store1 = DurableMemory(memory_file)

    store1.remember(
        "CUST-0001",
        "User prefers concise answers.",
    )

    store2 = DurableMemory(memory_file)

    memories = store2.recall("CUST-0001")

    assert memories == ["User prefers concise answers."]


def test_durable_memory_forget(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store = DurableMemory(memory_file)

    store.remember(
        "CUST-0001",
        "User prefers concise answers.",
    )

    result = store.forget(
        "CUST-0001",
        "User prefers concise answers.",
    )

    assert result["success"] is True
    assert store.recall("CUST-0001") == []


def test_durable_memory_clear_user(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store = DurableMemory(memory_file)

    store.remember("CUST-0001", "Preference A")
    store.remember("CUST-0001", "Preference B")

    result = store.clear_user("CUST-0001")

    assert result["success"] is True
    assert store.recall("CUST-0001") == []


def test_durable_memory_limits_items(tmp_path):
    memory_file = tmp_path / "user_memory.json"

    store = DurableMemory(memory_file)

    for i in range(25):
        store.remember(
            "CUST-0001",
            f"Preference {i}",
        )

    memories = store.recall("CUST-0001")

    assert len(memories) == memory.MAX_MEMORY_ITEMS
    assert memories[0] == "Preference 5"
    assert memories[-1] == "Preference 24"


def test_durable_memory_rejects_invalid_user():
    store = DurableMemory()

    try:
        store.recall("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Information classification tests
# ---------------------------------------------------------------------------

def test_classify_durable_memory():
    assert (
        classify_information("Remember that I prefer concise answers.")
        == "durable_memory"
    )


def test_classify_session_context():
    assert (
        classify_information("We discussed my order earlier.")
        == "session_context"
    )


def test_classify_knowledge_retrieval():
    assert (
        classify_information("What is the return policy?")
        == "knowledge_retrieval"
    )


def test_classify_application_context():
    assert (
        classify_information("Show me customer CUST-0001.")
        == "application_context"
    )


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Run with pytest:")
    print("pytest 08_agents\\test_memory.py -v")