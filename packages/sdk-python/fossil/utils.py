from __future__ import annotations
from typing import List, Tuple

from .schema import FossilRecord


def truncate_context(text: str, max_chars: int = 1024) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n...[truncated]...\n" + text[-half:]


def format_for_injection(
    results: List[Tuple[FossilRecord, float]],
    max_results: int = 3,
) -> str:
    """
    Formats search results into a prompt-injectable string.
    Drop this directly into your agent's system prompt or context.
    """
    if not results:
        return ""

    lines = ["[FOSSIL: Similar past failures retrieved]\n"]
    for i, (record, score) in enumerate(results[:max_results], 1):
        lines.append(f"--- Fossil {i} (similarity: {score:.2f}) ---")
        lines.append(f"Situation: {record.situation.description}")
        lines.append(f"What failed: {record.failure.description}")
        lines.append(f"How it was resolved: {record.resolution.description}")
        lines.append("")

    lines.append("[End of FOSSIL context]\n")
    return "\n".join(lines)


def format_summary(record: FossilRecord) -> str:
    return (
        f"[{record.id}] {record.failure.type.value} | "
        f"{record.failure.severity.value} | "
        f"{record.agent.task_domain.value} | "
        f"{record.timestamp[:10]}\n"
        f"  situation:  {record.situation.description}\n"
        f"  failure:    {record.failure.description}\n"
        f"  resolution: {record.resolution.description}"
    )