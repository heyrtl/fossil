# Concepts

## The Problem

Every AI agent is born knowing nothing.

It fails. You fix it. The fix lives in your head, your Slack, your commit message — nowhere structured. Next week the same agent fails again on a slightly different input. Next month a different developer's agent hits the same root cause.

There is no shared memory for agent failure.

Current observability tools (LangSmith, Langfuse, Datadog) capture *what happened* — token counts, latency, traces, stack traces. They do not capture *why reasoning failed* in a form that is reusable or searchable.

---

## What FOSSIL Does

FOSSIL introduces three primitives:

**RECORD** — structure a reasoning failure and its resolution into a typed, versioned artifact called a FossilRecord.

**SEARCH** — given a description of what an agent is about to attempt, find semantically similar past failures.

**INJECT** — surface matching fossils as context before the agent acts, so it can avoid known failure modes.

---

## The FossilRecord

A fossil is not a log line. It is a structured reasoning artifact with five parts:

```
agent      → who failed (framework, model, domain)
situation  → what was being attempted (embedded for semantic search)
failure    → what went wrong (typed by failure category)
resolution → what fixed it (typed by resolution category)
shared     → whether it contributes to the community pool
```

The situation and failure descriptions are embedded into a vector at record time. Search queries are embedded at query time. Retrieval is cosine similarity over those vectors.

---

## Failure Taxonomy

FOSSIL classifies failures by reasoning category, not by exception type. Each category implies a class of resolutions.

| Type | What it means |
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

## Resolution Taxonomy

| Type | What it means |
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

## How Search Works

1. At record time: `situation.description + failure.description` is embedded using `bge-small-en-v1.5`.
2. At search time: the query string is embedded with the same model.
3. Cosine similarity is computed between the query vector and all stored situation vectors.
4. Results above `min_score` (default 0.5) are returned sorted by score descending.

The embedding model is the same whether you use the local SDK or the remote API — `bge-small-en-v1.5` in both cases.

---

## Context Injection Pattern

The most effective usage pattern:

```python
from fossil import Fossil, format_for_injection

fossil = Fossil()

# before each agent step
results = fossil.search(situation_description, top_k=3, min_score=0.5)
context = format_for_injection(results)

# inject into system prompt
system_prompt = base_system_prompt + "\n\n" + context
```

`format_for_injection` produces a structured block like:

```
[FOSSIL: Similar past failures retrieved]

--- Fossil 1 (similarity: 0.79) ---
Situation: agent extracting JSON from LLM output that returned markdown-fenced text
What failed: json.loads() failed — model wrapped output in ```json fences
How it was resolved: strip markdown fences with regex before parsing

[End of FOSSIL context]
```

Drop this directly into your system prompt. No framework lock-in. Works with any LLM.

---

## Local vs Remote Store

**Local (default)** — SQLite at `~/.fossil/fossil.db`. Embeddings run on-device with `sentence-transformers`. Zero config, zero cost, zero data egress.

**Remote** — FOSSIL REST API at `https://fossil-api.hello-76a.workers.dev`. Embeddings run on Cloudflare Workers AI. No local model needed. Community pool available via `shared=True`.

```python
# local
fossil = Fossil()

# remote
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```

---

## Privacy

Records with `shared=False` (default) never leave your machine or your self-hosted server.

Records with `shared=True` are anonymized and contributed to the community pool — making FOSSIL more useful for everyone.

`context_snapshot` is optional and your responsibility to anonymize before storing.