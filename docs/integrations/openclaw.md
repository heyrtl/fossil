# FOSSIL + OpenClaw

OpenClaw is a self-hosted, persistent AI agent daemon with 200k+ GitHub stars. It is model-agnostic, skill-extensible, and MCP-compatible. FOSSIL integrates via MCP server or as a native OpenClaw skill.

---

## Method 1: MCP Server (recommended)

OpenClaw supports MCP servers via `openclaw.json`.

**1. Add FOSSIL to openclaw.json**

```json
{
  "mcp": {
    "servers": [
      {
        "name": "fossil",
        "command": "npx",
        "args": ["@openfossil/mcp"],
        "env": {
          "FOSSIL_API_URL": "https://fossil-api.hello-76a.workers.dev"
        }
      }
    ]
  }
}
```

**2. Restart your OpenClaw gateway**

```bash
openclaw restart
```

**3. Verify**

Send to your agent via Telegram/WhatsApp:

```
/status
```

FOSSIL tools should appear in the tool list.

---

## Method 2: OpenClaw Skill

Create a skill file at `~/.openclaw/skills/fossil.md`:

````markdown
---
name: fossil
description: Search and record AI agent failures using FOSSIL semantic memory
triggers:
  - "search fossil"
  - "record failure"
  - "fossil search"
  - "fossil record"
---

# FOSSIL Skill

Search for similar past agent failures before attempting a task,
or record a failure after it occurs.

## Search

To search: describe the situation to fossil_search.
Inject returned resolutions into your context before proceeding.

## Record

To record: after any failure, call fossil_record with:
- situation: what were you attempting
- failure_type: one of the FOSSIL taxonomy values
- failure: what went wrong
- resolution_type: how it was fixed
- resolution: the fix description
- framework: openclaw
- model: your configured model name

## Taxonomy reference

Failure types: misinterpretation, hallucinated_tool, format_failure,
context_loss, infinite_loop, premature_termination, scope_creep,
ambiguity_paralysis, tool_misuse, adversarial_input, compounding_error

Resolution types: prompt_change, tool_fix, retry, human_override,
context_injection, schema_correction, step_decomposition, input_sanitization
````

---

## Standing instructions in AGENTS.md

Add to your OpenClaw `AGENTS.md`:

```markdown
## Failure Memory (FOSSIL)

Before any non-trivial task step, call fossil_search with a description
of what you are about to attempt. Read the returned resolutions before acting.

After any failure, call fossil_record before retrying. Include:
- what you were attempting
- what went wrong (use the FOSSIL failure taxonomy)
- what you did to fix it

This builds a persistent failure memory across all your sessions.
```

---

## Common OpenClaw failure patterns to record

| Situation | Failure type |
|---|---|
| Sent message to wrong channel/contact | `misinterpretation` |
| Browser automation clicked wrong element | `tool_misuse` |
| Email reply tone was wrong | `misinterpretation` |
| Scheduled task ran at wrong time | `format_failure` |
| Got stuck waiting for response that never came | `infinite_loop` |
| Took action on wrong file/account | `scope_creep` |
| Adversarial content in email hijacked behavior | `adversarial_input` |

---

## Why FOSSIL matters for OpenClaw specifically

OpenClaw runs continuously and autonomously — it acts while you sleep. Failures at 3am don't have a human to catch them. FOSSIL gives your always-on agent a memory for past mistakes so it can avoid them proactively, even on novel inputs that share a root cause with something that failed before.