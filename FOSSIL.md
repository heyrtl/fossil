# FOSSIL Protocol v1.0

**Semantic Failure Memory for AI Agents**

---

## Abstract

FOSSIL defines a structured format for recording, storing, and retrieving AI agent reasoning failures. The goal is to make failure a first-class, semantically searchable artifact — so that agents, developers, and teams stop rediscovering the same failure modes from scratch.

---

## Motivation

Current observability tools for AI agents capture *what happened* — token counts, latency, stack traces, model outputs. None of them capture *why reasoning failed* in a form that is reusable.

Every agent deployment rediscovers the same failure modes. An agent misreads a date format from an API. You fix the prompt. Next week, a different team's agent hits the same issue. There is no mechanism for shared failure intelligence.

FOSSIL is that mechanism.

---

## Core Concepts

**Fossil** — a structured record of a single reasoning failure and its resolution.

**Situation** — a natural language description of what the agent was attempting when it failed. This is the primary unit of semantic search. It is embedded and stored so that future situations can be compared against it.

**Failure** — what went wrong, classified by type and severity.

**Resolution** — what fixed it, classified by type and marked as verified or not.

**Community Pool** — an opt-in, anonymized collection of fossils shared across users and teams. The flywheel that makes FOSSIL more valuable over time.

---

## Record Schema

Full JSON Schema: `schema/fossil.v1.json`

```json
{
  "id": "fossil_a1b2c3d4e5f6",
  "protocol_version": "1.0",
  "timestamp": "2025-03-09T14:32:00Z",
  "agent": {
    "framework": "langchain",
    "model": "llama-3.3-70b-versatile",
    "task_domain": "data_analysis"
  },
  "situation": {
    "description": "agent extracting JSON from LLM output that returned markdown-fenced text",
    "context_snapshot": null
  },
  "failure": {
    "type": "format_failure",
    "description": "json.loads raised JSONDecodeError — model wrapped output in ```json fences",
    "severity": "major",
    "was_irreversible": false
  },
  "resolution": {
    "type": "input_sanitization",
    "description": "strip markdown fences with regex before parsing",
    "verified": true,
    "time_to_resolve_minutes": 12
  },
  "shared": false
}
```

---

## Failure Type Taxonomy

The taxonomy is the intellectual core of the protocol. These categories were designed to be:
- **Mutually exclusive** — each failure maps to exactly one type
- **Actionable** — each type implies a class of resolutions
- **Model-agnostic** — apply equally to any LLM or agent framework

| Type | Description |
|---|---|
| `misinterpretation` | Agent misread the task or user intent |
| `hallucinated_tool` | Called a tool that doesn't exist or with wrong signature |
| `format_failure` | Output didn't match expected schema or format |
| `context_loss` | Forgot earlier context in a multi-step run |
| `infinite_loop` | Got stuck in a reasoning or tool-call cycle |
| `premature_termination` | Declared done when the task was incomplete |
| `scope_creep` | Did more than asked, touched things it shouldn't |
| `ambiguity_paralysis` | Couldn't proceed due to underspecified input |
| `tool_misuse` | Right tool, wrong usage or arguments |
| `adversarial_input` | User input caused unexpected behavior |
| `compounding_error` | Small error amplified across multiple steps |

---

## Resolution Type Taxonomy

| Type | Description |
|---|---|
| `prompt_change` | Modified the system or user prompt |
| `tool_fix` | Fixed the tool definition, schema, or implementation |
| `retry` | Retrying the step succeeded without changes |
| `human_override` | A human intervened directly |
| `context_injection` | Injected missing context into the agent's window |
| `schema_correction` | Fixed the output schema or parser |
| `step_decomposition` | Broke the failing step into smaller sub-steps |
| `input_sanitization` | Cleaned or validated input before processing |

---

## Embeddings

FOSSIL embeds the concatenation of `situation.description` and `failure.description` for each record. Embeddings are stored alongside the record and used for cosine similarity search at query time.

The embedding model is pluggable. The reference implementation defaults to `all-MiniLM-L6-v2` via `sentence-transformers` — no API key, no data egress, runs on CPU.

Embeddings are **never** included in exported records. They are implementation details of the store.

---

## Search Semantics

A search query is a natural language description of what an agent is currently attempting. FOSSIL computes cosine similarity between the query embedding and all stored situation embeddings, filters by `min_score`, and returns the top-k results sorted by score descending.

Domain filtering (`task_domain`) is applied as an exact match pre-filter before scoring.

---

## Privacy

- `shared: false` (default) — record stays local, never leaves the machine
- `shared: true` — record is opted into the community pool
- `context_snapshot` — optional, should be anonymized before storing. FOSSIL does not enforce anonymization; this is the responsibility of the recording party.

FOSSIL never embeds or transmits records marked `shared: false`.

---

## Implementations

| Language | Package | Status |
|---|---|---|
| Python | `fossil-sdk` | v0.1.0 |
| TypeScript (types) | `@fossil/core` | v0.1.0 |
| MCP server | `@fossil/mcp` | v0.1.0 |

---

## Versioning

The protocol version (`protocol_version`) is independent of SDK versions. Breaking changes to the record schema will increment the protocol version. Implementations must reject records with unknown protocol versions.

---

## Contributing

Implementations in other languages are welcome. An implementation is conformant if:

1. It produces records that validate against `schema/fossil.v1.json`
2. It correctly parses records produced by other conformant implementations
3. It does not transmit records with `shared: false` to any external service