"""
FOSSIL demo agent — runs on Groq free tier, zero cost.

What this shows:
  1. Seed FOSSIL with known real-world agent failures
  2. Agent searches FOSSIL before each step
  3. FOSSIL injects past failure context into the prompt
  4. Agent avoids the failure it would have otherwise hit
  5. New failures get recorded automatically

Setup:
  pip install fossil-sdk[local] groq
  export GROQ_API_KEY=your_key_here
  python examples/groq-agent/agent.py
"""

from __future__ import annotations
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TQDM_DISABLE"] = "1"
import json
import sys
from pathlib import Path
from typing import Any

# allow running from repo root
sys.path.insert(0, str(Path(__file__).parents[2] / "packages" / "sdk-python"))

from fossil import (
    Fossil,
    FailureType,
    ResolutionType,
    Severity,
    TaskDomain,
    format_for_injection,
)

try:
    from groq import Groq
except ImportError:
    sys.exit("Install groq: pip install groq")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
FOSSIL_DB = Path.home() / ".fossil" / "demo.db"

if not GROQ_API_KEY:
    sys.exit("Set GROQ_API_KEY environment variable")


def seed_fossils(fossil: Fossil) -> None:
    """
    Seeds FOSSIL with real known failure patterns before the demo runs.
    In production these accumulate naturally — here we front-load them
    so the demo shows injection working on the very first run.
    """
    if fossil.count() > 0:
        return

    print("Seeding FOSSIL with known failure patterns...\n")

    seeds = [
        dict(
            situation="agent asked to extract a JSON object from a markdown code block returned by an LLM",
            failure_type=FailureType.FORMAT_FAILURE,
            failure="json.loads() failed because the string included ```json and ``` fences — the model wrapped the output in markdown even though raw JSON was requested",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.INPUT_SANITIZATION,
            resolution="strip markdown fences before parsing: re.sub(r'^```[a-z]*\n|```$', '', text.strip())",
            framework="custom",
            model="llama-3.3-70b-versatile",
            domain=TaskDomain.DATA_ANALYSIS,
            verified=True,
        ),
        dict(
            situation="agent given a multi-step task told to call a tool named 'finish' when done",
            failure_type=FailureType.HALLUCINATED_TOOL,
            failure="model called 'complete' instead of 'finish' — a tool that doesn't exist in the schema, causing a tool_not_found error",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.PROMPT_CHANGE,
            resolution="explicitly list available tool names in the system prompt. 'When done, call the finish tool. Available tools: search, calculate, finish.'",
            framework="custom",
            model="llama-3.3-70b-versatile",
            domain=TaskDomain.PLANNING,
            verified=True,
        ),
        dict(
            situation="agent processing a long document loses track of a constraint mentioned early in the context",
            failure_type=FailureType.CONTEXT_LOSS,
            failure="agent correctly identified the constraint in step 1 but violated it by step 4 when the original instruction had scrolled far back in context",
            severity=Severity.CRITICAL,
            resolution_type=ResolutionType.CONTEXT_INJECTION,
            resolution="re-inject critical constraints at the start of each step prompt, not just in the system prompt. treat constraints as stateful, not static.",
            framework="custom",
            model="llama-3.3-70b-versatile",
            domain=TaskDomain.RESEARCH,
            verified=True,
        ),
        dict(
            situation="agent asked to summarize a list of items produces output for only the first few items",
            failure_type=FailureType.PREMATURE_TERMINATION,
            failure="model stopped after processing 3 of 10 items with no indication it was done — simply ended the list mid-way",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.PROMPT_CHANGE,
            resolution="add explicit count to the prompt: 'There are exactly N items. Process all N. Do not stop early.'",
            framework="custom",
            model="llama-3.3-70b-versatile",
            domain=TaskDomain.CONTENT_CREATION,
            verified=True,
        ),
    ]

    for s in seeds:
        fossil.record(**s)

    print(f"Seeded {len(seeds)} fossils.\n")


def search_fossils(fossil: Fossil, situation: str) -> str:
    results = fossil.search(situation, top_k=2, min_score=0.45)
    return format_for_injection(results, max_results=2)


def run_agent_step(
    client: Groq,
    task: str,
    fossil_context: str,
    history: list[dict],
    tools: list[dict],
) -> tuple[str, Any]:
    system = f"""You are a precise data extraction agent.
Extract structured information from the text the user provides.
Return a valid JSON object. Do not wrap it in markdown fences.
Always include all fields even if empty string.

{fossil_context}"""

    messages = [{"role": "system", "content": system}] + history
    messages.append({"role": "user", "content": task})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
        **({"tools": tools, "tool_choice": "auto"} if tools else {}),
    )

    msg = response.choices[0].message
    return msg.content or "", msg


def parse_json_safe(text: str) -> dict | None:
    import re
    cleaned = re.sub(r"^```[a-z]*\n?|```$", "", text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def main() -> None:
    fossil = Fossil(db_path=FOSSIL_DB)
    client = Groq(api_key=GROQ_API_KEY)

    seed_fossils(fossil)

    task_text = """
    Extract the following fields from this invoice snippet:
    vendor, amount, currency, due_date, invoice_number

    Invoice snippet:
    INVOICE #INV-2024-0892
    From: Acme Software Ltd
    Amount Due: $4,250.00 USD
    Payment Due: March 15, 2025
    """

    situation = "extracting structured JSON fields from a plain-text invoice using an LLM"

    print("=" * 60)
    print("TASK")
    print("=" * 60)
    print(task_text.strip())
    print()

    print("=" * 60)
    print("FOSSIL SEARCH — checking for similar past failures")
    print("=" * 60)
    fossil_context = search_fossils(fossil, situation)
    if fossil_context:
        print(fossil_context)
    else:
        print("No relevant fossils found.\n")

    print("=" * 60)
    print(f"AGENT RUNNING — {GROQ_MODEL}")
    print("=" * 60)

    raw_output, _ = run_agent_step(
        client=client,
        task=task_text,
        fossil_context=fossil_context,
        history=[],
        tools=[],
    )

    print(f"Raw output:\n{raw_output}\n")

    parsed = parse_json_safe(raw_output)

    if parsed is None:
        print("PARSE FAILED — recording to FOSSIL")
        rec = fossil.record(
            situation=situation,
            failure_type=FailureType.FORMAT_FAILURE,
            failure=f"json.loads failed on model output: {raw_output[:200]}",
            severity=Severity.MAJOR,
            resolution_type=ResolutionType.INPUT_SANITIZATION,
            resolution="strip markdown fences and retry parse",
            framework="groq",
            model=GROQ_MODEL,
            domain=TaskDomain.DATA_ANALYSIS,
        )
        print(f"Fossil recorded: {rec.id}")
    else:
        print("EXTRACTED:")
        print(json.dumps(parsed, indent=2))
        print(f"\nFOSSIL store now holds {fossil.count()} records.")

    fossil.close()


if __name__ == "__main__":
    main()
