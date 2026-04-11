import pytest
from pathlib import Path
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain


@pytest.fixture
def fossil(tmp_path: Path) -> Fossil:
    return Fossil(db_path=tmp_path / "client_test.db")


def test_record_and_search(fossil: Fossil) -> None:
    rec = fossil.record(
        situation="agent called a tool with wrong argument types",
        failure_type=FailureType.TOOL_MISUSE,
        failure="passed string where int expected in page_number argument",
        severity=Severity.MINOR,
        resolution_type=ResolutionType.SCHEMA_CORRECTION,
        resolution="added explicit type annotation and coercion in tool wrapper",
        framework="langchain",
        model="llama-3.3-70b-versatile",
        domain=TaskDomain.CODE_GENERATION,
        verified=True,
    )

    assert rec.id.startswith("fossil_")
    assert fossil.count() == 1

    results = fossil.search(
        "wrong argument type passed to tool call",
        top_k=3,
        min_score=0.3,
    )
    assert len(results) > 0
    found, score = results[0]
    assert found.id == rec.id
    assert score > 0.3


def test_record_defaults(fossil: Fossil) -> None:
    rec = fossil.record(
        situation="agent lost context mid-task",
        failure_type=FailureType.CONTEXT_LOSS,
        failure="forgot constraint from earlier in conversation",
        severity=Severity.MAJOR,
        resolution_type=ResolutionType.CONTEXT_INJECTION,
        resolution="re-inject constraints at each step",
        framework="custom",
        model="gemini-2.0-flash",
    )
    assert rec.failure.was_irreversible is False
    assert rec.resolution.verified is False
    assert rec.shared is False
    assert rec.agent.task_domain.value == "other"


def test_get(fossil: Fossil) -> None:
    rec = fossil.record(
        situation="test situation",
        failure_type=FailureType.MISINTERPRETATION,
        failure="misread the task",
        severity=Severity.MINOR,
        resolution_type=ResolutionType.PROMPT_CHANGE,
        resolution="clarified the task description",
        framework="custom",
        model="test",
    )
    fetched = fossil.get(rec.id)
    assert fetched is not None
    assert fetched.id == rec.id


def test_get_missing(fossil: Fossil) -> None:
    assert fossil.get("fossil_000000000000") is None


def test_delete(fossil: Fossil) -> None:
    rec = fossil.record(
        situation="test",
        failure_type=FailureType.FORMAT_FAILURE,
        failure="bad output",
        severity=Severity.MINOR,
        resolution_type=ResolutionType.RETRY,
        resolution="retry worked",
        framework="custom",
        model="test",
    )
    assert fossil.delete(rec.id) is True
    assert fossil.get(rec.id) is None
    assert fossil.delete(rec.id) is False


def test_list(fossil: Fossil) -> None:
    for i in range(4):
        fossil.record(
            situation=f"situation {i}",
            failure_type=FailureType.FORMAT_FAILURE,
            failure=f"failure {i}",
            severity=Severity.MINOR,
            resolution_type=ResolutionType.RETRY,
            resolution=f"resolution {i}",
            framework="custom",
            model="test",
        )
    records = fossil.list(limit=2)
    assert len(records) == 2


def test_domain_filter(fossil: Fossil) -> None:
    fossil.record(
        situation="browsing a webpage and extracting links",
        failure_type=FailureType.TOOL_MISUSE,
        failure="clicked wrong element",
        severity=Severity.MINOR,
        resolution_type=ResolutionType.RETRY,
        resolution="added wait before click",
        framework="custom",
        model="test",
        domain=TaskDomain.WEB_BROWSING,
    )
    fossil.record(
        situation="generating a Python function from a docstring",
        failure_type=FailureType.FORMAT_FAILURE,
        failure="output missing return type",
        severity=Severity.MINOR,
        resolution_type=ResolutionType.PROMPT_CHANGE,
        resolution="added return type to prompt",
        framework="custom",
        model="test",
        domain=TaskDomain.CODE_GENERATION,
    )

    results = fossil.search(
        "writing code from description",
        top_k=5,
        min_score=0.1,
        domain=TaskDomain.CODE_GENERATION,
    )
    assert all(r.agent.task_domain == TaskDomain.CODE_GENERATION for r, _ in results)