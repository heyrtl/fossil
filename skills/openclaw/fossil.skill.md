---
name: fossil
version: 0.1.0
description: >
  Semantic failure memory for AI agents. Search past reasoning failures before
  acting to avoid known mistakes. Record new failures and resolutions after they
  happen. Powered by FOSSIL — the open-source failure memory protocol.
author: heyrtl
license: MIT
mcp:
  server: npx @openfossil/mcp
  env:
    FOSSIL_API_URL: https://fossil-api.hello-76a.workers.dev
triggers:
  - search fossil
  - fossil search
  - record failure to fossil
  - fossil record
  - check past failures
  - what failures have we seen
  - have we hit this before
  - remember this failure
tags:
  - memory
  - agents
  - observability
  - debugging
  - mcp
---

# FOSSIL — Semantic Failure Memory

FOSSIL gives you a memory for AI agent reasoning failures. Before acting, search
for similar past failures. After a failure, record it with the resolution so you
never hit it twice.

The community pool at `fossil-api.hello-76a.workers.dev` is live and free.
No API key required.

---

## Tools available

| Tool | When to use |
|---|---|
| `fossil_search` | Before any non-trivial step — find similar past failures |
| `fossil_record` | After any failure — capture what went wrong and what fixed it |
| `fossil_get` | Retrieve a specific fossil by ID |
| `fossil_list` | Browse your recent fossil archive |

---

## When to search

Call `fossil_search` before any step involving:

- Parsing or extracting structured data from LLM output
- Calling external APIs or tools
- Multi-step file operations
- Browser automation
- Sending messages or emails on behalf of the user
- Any task that has failed before in this workspace

Pass a natural language description of what you are about to attempt.
Read the returned resolutions before proceeding.

Example:
```
fossil_search("agent about to extract JSON fields from an invoice document")
```

---

## When to record

Call `fossil_record` after any failure, before retrying. Required fields:

- `situation` — what were you attempting (natural language)
- `failure_type` — see taxonomy below
- `failure` — what went wrong
- `severity` — critical | major | minor
- `resolution_type` — see taxonomy below
- `resolution` — what fixed it
- `framework` — openclaw
- `model` — your configured model name

Example:
```
fossil_record(
  situation="sending a reply email to insurance company",
  failure_type="misinterpretation",
  failure="agent replied to the wrong thread — matched subject line instead of sender",
  severity="major",
  resolution_type="prompt_change",
  resolution="added explicit instruction: always match by sender address, not subject line",
  framework="openclaw",
  model="claude-opus-4-5"
)
```

---

## Failure type taxonomy

Choose the type that best describes the reasoning failure:

| Type | When to use |
|---|---|
| `misinterpretation` | Misread the task or user intent |
| `hallucinated_tool` | Called a tool that doesn't exist or with wrong signature |
| `format_failure` | Output didn't match expected schema or format |
| `context_loss` | Forgot earlier context in a multi-step run |
| `infinite_loop` | Got stuck in a reasoning or tool-call cycle |
| `premature_termination` | Declared done when the task was incomplete |
| `scope_creep` | Did more than asked, touched things it shouldn't |
| `ambiguity_paralysis` | Couldn't proceed due to underspecified input |
| `tool_misuse` | Right tool, wrong usage or arguments |
| `adversarial_input` | External input hijacked agent behavior |
| `compounding_error` | Small error amplified across multiple steps |

---

## Resolution type taxonomy

| Type | When to use |
|---|---|
| `prompt_change` | Modified the system or user prompt |
| `tool_fix` | Fixed the tool definition or implementation |
| `retry` | Retrying without changes succeeded |
| `human_override` | Human intervened directly |
| `context_injection` | Injected missing context into the agent window |
| `schema_correction` | Fixed the output schema or parser |
| `step_decomposition` | Broke the failing step into smaller steps |
| `input_sanitization` | Cleaned or validated input before processing |

---

## Standing instructions for AGENTS.md

Add this block to your `AGENTS.md` to make FOSSIL a persistent habit:

```markdown
## Failure Memory (FOSSIL)

Before any non-trivial task step, call fossil_search with a description
of what you are about to attempt. Read returned resolutions before acting.

After any failure, call fossil_record before retrying. Capture:
- what you were attempting
- what went wrong (use the FOSSIL failure taxonomy)
- what fixed it

This builds a persistent failure memory across all sessions.
```

---

## Common OpenClaw failure patterns

| Situation | Failure type |
|---|---|
| Sent message to wrong contact | `misinterpretation` |
| Browser clicked wrong element | `tool_misuse` |
| Email reply used wrong tone | `misinterpretation` |
| Scheduled task ran at wrong time | `format_failure` |
| Stuck waiting for a response | `infinite_loop` |
| Acted on wrong file or account | `scope_creep` |
| Adversarial email hijacked behavior | `adversarial_input` |
| Stopped mid-task without finishing | `premature_termination` |

---

## Resources

- Docs: https://github.com/heyrtl/fossil/tree/main/docs
- Protocol spec: https://github.com/heyrtl/fossil/blob/main/FOSSIL.md
- REST API: https://fossil-api.hello-76a.workers.dev/health
- Python SDK: pip install openfossil
- Source: https://github.com/heyrtl/fossil