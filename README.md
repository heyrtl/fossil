# FOSSIL

**Semantic failure memory for AI agents.**

> 🦴 [Community pool stats](https://fossil-api.hello-76a.workers.dev/stats) — growing with every shared fossil.

![FOSSIL demo](./demo.gif)

Every AI agent is born knowing nothing.

It fails. You fix it. Next week, someone else's agent fails the exact same way.
The week after, yours does too — on a different input, but the same root cause.

FOSSIL gives agents a memory for failure. Record reasoning failures when they happen.
Search past failures before acting. Stop rediscovering the same mistakes.

---

## How it works

Three operations. That's it.

```python
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain

fossil = Fossil()

# 1. record a failure after it happens
fossil.record(
    situation="agent extracting JSON from LLM output that returned markdown-fenced text",
    failure_type=FailureType.FORMAT_FAILURE,
    failure="json.loads() failed — model wrapped output in ```json fences",
    severity=Severity.MAJOR,
    resolution_type=ResolutionType.INPUT_SANITIZATION,
    resolution="strip markdown fences with regex before parsing",
    framework="langchain",
    model="llama-3.3-70b-versatile",
    domain=TaskDomain.DATA_ANALYSIS,
    verified=True,
)

# 2. search before a task step
results = fossil.search("parsing structured data from LLM text output")

# 3. inject into your agent's context
from fossil import format_for_injection
context = format_for_injection(results)
# drop `context` into your system prompt — done
```

---

## Install

```bash
pip install openfossil[local]
```

`[local]` pulls in `sentence-transformers` for on-device embeddings.
No API key. No data leaves your machine.

---

## MCP server

For Claude Code, Codex CLI, Cursor, and any MCP-compatible client:

```bash
npx @openfossil/mcp
```

Then add to your MCP config:

```json
{
  "mcpServers": {
    "fossil": {
      "command": "npx",
      "args": ["@openfossil/mcp"],
      "env": {
        "FOSSIL_API_URL": "https://fossil-api.hello-76a.workers.dev"
      }
    }
  }
}
```

Claude Code and Cursor can now call `fossil_search` before any agent step and `fossil_record` after any failure — with no code changes to your agent.

---

## Why FOSSIL is different from logging

Log aggregators (Datadog, LangSmith, Langfuse) tell you *what happened*.
FOSSIL tells you *what to do about it* — by finding the time it happened before.

The difference is semantic search over structured failure records, not keyword search over log lines.

| | Logging | FOSSIL |
|---|---|---|
| Unit of storage | Log line / trace | Reasoning failure + resolution |
| Search | Keyword / filter | Semantic similarity |
| Primary use | Debugging after the fact | Injection before acting |
| Shareable | Rarely | Yes, opt-in community pool |

---

## Self-hosted

```bash
git clone https://github.com/heyrtl/fossil
cd fossil/self-hosted
cp .env.example .env  # set POSTGRES_PASSWORD
docker compose up db -d
```

Runs PostgreSQL with pgvector. Point the SDK at your own deployed API:

```python
fossil = Fossil(api_url="http://your-server:8745")
```

The default SQLite store is fine for local and single-developer use.
Switch to self-hosted when you want a team-shared pool.

---

## Failure taxonomy

FOSSIL classifies failures — not stack traces.

`misinterpretation` `hallucinated_tool` `format_failure` `context_loss`
`infinite_loop` `premature_termination` `scope_creep` `ambiguity_paralysis`
`tool_misuse` `adversarial_input` `compounding_error`

Each type implies a class of resolutions. See [FOSSIL.md](./FOSSIL.md) for the full protocol spec.

---

## Repo structure

```
packages/
  sdk-python/   — pip install openfossil
  core/         — TypeScript types (@openfossil/core)
  mcp/          — MCP server (@openfossil/mcp)
apps/
  api/          — REST API (Cloudflare Workers + D1 + Workers AI)
examples/
  groq-agent/   — full working demo on Groq free tier
schema/
  fossil.v1.json — JSON Schema for the protocol
skills/
  openclaw/     — OpenClaw ClawHub skill
docs/           — full documentation
self-hosted/
  docker-compose.yml
FOSSIL.md       — protocol specification
```

---

## Status

FOSSIL is in early development. The protocol is v1.0 and stable.
The Python SDK, MCP server, and REST API are live and functional.

Live community API: `https://fossil-api.hello-76a.workers.dev` — no API key required.

---

## Contributing

Read [FOSSIL.md](./FOSSIL.md) for the protocol spec.
Implementations in other languages are welcome — anything that validates against `schema/fossil.v1.json` is conformant.

---

## License

MIT