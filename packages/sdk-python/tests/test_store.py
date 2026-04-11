import pytest
from pathlib import Path
from fossil.store import FossilStore
from fossil.schema import (
    AgentMeta,
    Failure,
    FailureType,
    FossilRecord,
    Resolution,
    ResolutionType,
    Severity,
    Situation,
    TaskDomain,
)


def make_record(suffix: str = "") -> FossilRecord:
    return FossilRecord(
        agent=AgentMeta(
            framework="pytest",
            model="test-model",
            task_domain=TaskDomain.CODE_GENERATION,
        ),
        situation=Situation(
            description=f"agent tried to parse JSON from markdown-wrapped LLM output {suffix}",
            context_snapshot="user asked for structured data extraction",
        ),
        failure=Failure(
            type=FailureType.FORMAT_FAILURE,
            description="json.loads failed on fenced output",
            severity=Severity.MAJOR,
            was_irreversible=False,
        ),
        resolution=Resolution(
            type=ResolutionType.INPUT_SANITIZATION,
            description="strip markdown fences before parsing",
            verified=True,
        ),
    )


@pytest.fixture
def store(tmp_path: Path) -> FossilStore:
    # uses local embedder — downloads once, cached by HuggingFace
    return FossilStore(db_path=tmp_path / "test.db")


def test_insert_and_get(store: FossilStore) -> None:
    record = make_record()
    inserted = store.insert(record)
    assert inserted.id == record.id

    fetched = store.get(record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.failure.type == FailureType.FORMAT_FAILURE


def test_count(store: FossilStore) -> None:
    assert store.count() == 0
    store.insert(make_record("a"))
    store.insert(make_record("b"))
    assert store.count() == 2


def test_search_returns_relevant(store: FossilStore) -> None:
    store.insert(make_record())
    results = store.search("parsing JSON from LLM response with markdown", top_k=5, min_score=0.3)
    assert len(results) > 0
    record, score = results[0]
    assert score > 0.3
    assert record.failure.type == FailureType.FORMAT_FAILURE


def test_search_min_score_filters(store: FossilStore) -> None:
    store.insert(make_record())
    results = store.search("completely unrelated query about cooking pasta", top_k=5, min_score=0.99)
    assert len(results) == 0


def test_delete(store: FossilStore) -> None:
    record = make_record()
    store.insert(record)
    assert store.count() == 1
    deleted = store.delete(record.id)
    assert deleted is True
    assert store.count() == 0
    assert store.get(record.id) is None


def test_list_all(store: FossilStore) -> None:
    for i in range(5):
        store.insert(make_record(str(i)))
    records = store.list_all(limit=3, offset=0)
    assert len(records) == 3
    records_page2 = store.list_all(limit=3, offset=3)
    assert len(records_page2) == 2


def test_roundtrip_serialization(store: FossilStore) -> None:
    record = make_record()
    store.insert(record)
    fetched = store.get(record.id)
    assert fetched is not None
    assert fetched.to_dict() == record.to_dict()