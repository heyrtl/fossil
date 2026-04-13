<p align="center">
  <img src="./assets/logo.svg" width="80" height="80" alt="FOSSIL trilobite logo" />
</p>

<h1 align="center">FOSSIL</h1>

<p align="center">
  <strong>Semantic failure memory for AI agents.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/openfossil/"><img src="https://img.shields.io/pypi/v/openfossil?style=flat-square&color=e8711a&label=pypi" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/@openfossil/sdk"><img src="https://img.shields.io/npm/v/%40openfossil%2Fsdk?style=flat-square&color=e8711a&label=npm" alt="npm"></a>
  <a href="https://github.com/heyrtl/fossil/blob/main/LICENSE"><img src="https://img.shields.io/github/license/heyrtl/fossil?style=flat-square&color=e8711a" alt="MIT"></a>
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ffossil-api.hello-76a.workers.dev%2Fstats&query=%24.shared&style=flat-square&color=e8711a&label=community%20fossils" alt="Community fossils">
</p>

<p align="center">
  <img src="./demo.gif" width="700" alt="FOSSIL demo" />
</p>

---

Every AI agent is born knowing nothing.

It fails. You fix it. Next week, someone else's agent fails the exact same way.
The week after, yours does too — different input, same root cause.

FOSSIL gives agents a memory for reasoning failures. Record what went wrong and how it was fixed. Search past failures before acting. Stop rediscovering the same mistakes.

---

## How it works

Three operations.

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
# drop context into your system prompt — done
```

---

## Install

```bash
# Python SDK + CLI
pip install openfossil[local]

# JavaScript / TypeScript
npm install @openfossil/sdk

# MCP server (Claude Code, Codex CLI, Cursor, any MCP client)
npx @openfossil/mcp
```

`[local]` pulls in `sentence-transformers` for on-device embeddings. No API key. No data leaves your machine.

Or skip local setup entirely — point at the live community API:

```python
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```

---

## CLI

```bash
fossil init                      # seed local store from community pool
fossil record                    # log a failure interactively
fossil search "JSON parse error" # search past failures
fossil list                      # browse your archive
fossil export --out backup.json  # export to JSON
fossil ping                      # check connection
```

---

## MCP server

Works with Claude Code, Codex CLI, Cursor, OpenClaw, and any MCP-compatible agent:

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

Your agent can now call `fossil_search` before any step and `fossil_record` after any failure — no code changes to your agent.

---

## Why not just use logging

Log aggregators tell you *what happened*. FOSSIL tells you *what to do about it* — by finding the time it happened before.

|  | Logging | FOSSIL |
|---|---|---|
| Unit of storage | Log line / trace | Reasoning failure + resolution |
| Search | Keyword / filter | Semantic similarity |
| Primary use | Debugging after the fact | Injection before acting |
| Shareable | Rarely | Yes, opt-in community pool |

---

## Failure taxonomy

FOSSIL classifies reasoning failures — not exceptions.

`misinterpretation` `hallucinated_tool` `format_failure` `context_loss`
`infinite_loop` `premature_termination` `scope_creep` `ambiguity_paralysis`
`tool_misuse` `adversarial_input` `compounding_error`

Each type implies a class of resolutions. Full spec in [FOSSIL.md](./FOSSIL.md).

---

## Integrations

| Agent / Framework | Method | Guide |
|---|---|---|
| Claude Code | MCP server | [docs](./docs/integrations/claude-code.md) |
| OpenAI Codex CLI | MCP server | [docs](./docs/integrations/codex-cli.md) |
| OpenClaw | MCP + ClawHub skill | [docs](./docs/integrations/openclaw.md) |
| LangChain | Python SDK | [docs](./docs/integrations/langchain.md) |
| CrewAI | Python SDK | [docs](./docs/integrations/crewai.md) |
| Vercel AI SDK | JS/TS SDK | [docs](./docs/integrations/README.md) |

---

## Self-hosted

```bash
git clone https://github.com/heyrtl/fossil
cd fossil/self-hosted
cp .env.example .env
docker compose up db -d
```

PostgreSQL + pgvector. Point the SDK at it:

```python
fossil = Fossil(api_url="http://your-server:8745")
```

---

## Repo

```
packages/
  sdk-python/   — pip install openfossil
  sdk-js/       — npm install @openfossil/sdk
  core/         — TypeScript types (@openfossil/core)
  mcp/          — MCP server (@openfossil/mcp)
apps/
  api/          — REST API (Cloudflare Workers + D1 + Workers AI)
examples/
  groq-agent/   — working demo, Groq free tier
schema/
  fossil.v1.json
skills/
  openclaw/     — ClawHub skill
docs/           — full documentation
FOSSIL.md       — protocol spec
```

---

## Status

Protocol v1.0 stable. Python SDK, JS SDK, MCP server, REST API — all live.

Community API: `https://fossil-api.hello-76a.workers.dev` — no key required.

---

## Contributing

Implementations in other languages are welcome. Conformant = validates against `schema/fossil.v1.json`. Read [FOSSIL.md](./FOSSIL.md).

---

MIT