from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple

from .schema import (
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
from .store import FossilStore, DEFAULT_DB_PATH
from .embedder import BaseEmbedder


class Fossil:
    """
    Primary interface for FOSSIL.

    Usage:
        fossil = Fossil()

        fossil.record(
            situation="agent was extracting structured data from a PDF invoice",
            failure_type=FailureType.FORMAT_FAILURE,
            failure="output JSON had string where int expected in 'total' field",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.SCHEMA_CORRECTION,
            resolution="added explicit type coercion instruction to extraction prompt",
            framework="langchain",
            model="llama-3.3-70b",
            domain=TaskDomain.DATA_ANALYSIS,
        )

        results = fossil.search("extracting numbers from PDF documents")
        for record, score in results:
            print(score, record.resolution.description)
    """

    def __init__(
        self,
        db_path: Path | str = DEFAULT_DB_PATH,
        embedder: Optional[BaseEmbedder] = None,
    ):
        self._store = FossilStore(db_path=db_path, embedder=embedder)

    def record(
        self,
        situation: str,
        failure_type: FailureType,
        failure: str,
        severity: Severity,
        resolution_type: ResolutionType,
        resolution: str,
        framework: str,
        model: str,
        domain: TaskDomain = TaskDomain.OTHER,
        context_snapshot: Optional[str] = None,
        was_irreversible: bool = False,
        verified: bool = False,
        time_to_resolve_minutes: Optional[int] = None,
        shared: bool = False,
    ) -> FossilRecord:
        record = FossilRecord(
            agent=AgentMeta(
                framework=framework,
                model=model,
                task_domain=domain,
            ),
            situation=Situation(
                description=situation,
                context_snapshot=context_snapshot,
            ),
            failure=Failure(
                type=failure_type,
                description=failure,
                severity=severity,
                was_irreversible=was_irreversible,
            ),
            resolution=Resolution(
                type=resolution_type,
                description=resolution,
                verified=verified,
                time_to_resolve_minutes=time_to_resolve_minutes,
            ),
            shared=shared,
        )
        return self._store.insert(record)

    def record_raw(self, record: FossilRecord) -> FossilRecord:
        return self._store.insert(record)

    def search(
        self,
        situation: str,
        top_k: int = 5,
        min_score: float = 0.5,
        domain: Optional[TaskDomain] = None,
    ) -> List[Tuple[FossilRecord, float]]:
        return self._store.search(
            situation_text=situation,
            top_k=top_k,
            min_score=min_score,
            domain=domain.value if domain else None,
        )

    def get(self, fossil_id: str) -> Optional[FossilRecord]:
        return self._store.get(fossil_id)

    def delete(self, fossil_id: str) -> bool:
        return self._store.delete(fossil_id)

    def count(self) -> int:
        return self._store.count()

    def list(self, limit: int = 100, offset: int = 0) -> List[FossilRecord]:
        return self._store.list_all(limit=limit, offset=offset)

    def close(self) -> None:
        self._store.close()

    def __enter__(self) -> Fossil:
        return self

    def __exit__(self, *_) -> None:
        self.close()