# fossil-sdk

Python SDK for FOSSIL — semantic failure memory for AI agents.

## Install

```bash
# core (no embedder — bring your own)
pip install fossil-sdk

# with local embedder (recommended, no API key needed)
pip install fossil-sdk[local]

# with OpenAI embedder
pip install fossil-sdk[openai]
```

## Quickstart

```python
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain

fossil = Fossil()  # stores in ~/.fossil/fossil.db by default

# record a failure after it happens
fossil.record(
    situation="agent extracting JSON from LLM output that returned markdown-fenced text",
    failure_type=FailureType.FORMAT_FAILURE,
    failure="json.loads() raised JSONDecodeError — model wrapped output in ```json fences",
    severity=Severity.MAJOR,
    resolution_type=ResolutionType.INPUT_SANITIZATION,
    resolution="strip markdown fences with regex before parsing",
    framework="langchain",
    model="llama-3.3-70b-versatile",
    domain=TaskDomain.DATA_ANALYSIS,
    verified=True,
)

# search before a task step
results = fossil.search("parsing structured data from LLM text output")
for record, score in results:
    print(f"{score:.2f} — {record.resolution.description}")
```

## Inject into agent context

```python
from fossil import Fossil, format_for_injection

fossil = Fossil()

def run_step(task: str, system_prompt: str) -> str:
    results = fossil.search(task, top_k=3, min_score=0.5)
    fossil_context = format_for_injection(results)

    augmented_prompt = system_prompt + "\n\n" + fossil_context
    # pass augmented_prompt to your LLM call
    ...
```

`format_for_injection` returns a string you drop directly into any system prompt or context window. No framework lock-in.

## Custom embedder

```python
from fossil import Fossil
from fossil.embedder import OpenAIEmbedder

embedder = OpenAIEmbedder(model_name="text-embedding-3-small", api_key="sk-...")
fossil = Fossil(embedder=embedder)
```

## Custom store location

```python
fossil = Fossil(db_path="/path/to/my/fossil.db")
```

## Context manager

```python
with Fossil() as fossil:
    fossil.record(...)
    results = fossil.search(...)
```

## API

| Method | Description |
|---|---|
| `fossil.record(...)` | Record a failure + resolution |
| `fossil.search(situation, top_k, min_score, domain)` | Semantic similarity search |
| `fossil.get(id)` | Fetch a single record |
| `fossil.delete(id)` | Delete a record |
| `fossil.list(limit, offset)` | Paginate all records |
| `fossil.count()` | Total records in store |

## Failure types

`misinterpretation` `hallucinated_tool` `format_failure` `context_loss`
`infinite_loop` `premature_termination` `scope_creep` `ambiguity_paralysis`
`tool_misuse` `adversarial_input` `compounding_error`

## Resolution types

`prompt_change` `tool_fix` `retry` `human_override` `context_injection`
`schema_correction` `step_decomposition` `input_sanitization`

## Running tests

```bash
cd packages/sdk-python
pip install -e ".[dev,local]"
pytest
```

First run downloads the embedding model (~80MB, cached after that).