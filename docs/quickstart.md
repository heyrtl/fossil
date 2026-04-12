# Quickstart

Get FOSSIL running in under 5 minutes.

---

## 1. Install

```bash
pip install openfossil[local]
```

`[local]` includes `sentence-transformers` for on-device embeddings. No API key needed.

---

## 2. Record your first fossil

```python
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain

fossil = Fossil()  # stores in ~/.fossil/fossil.db

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
```

---

## 3. Search before acting

```python
results = fossil.search("parsing structured data from LLM text output")

for record, score in results:
    print(f"{score:.2f} — {record.resolution.description}")
```

---

## 4. Inject into your agent

```python
from fossil import Fossil, format_for_injection

fossil = Fossil()

results = fossil.search("what the agent is about to attempt")
context = format_for_injection(results)

system_prompt = your_base_prompt + "\n\n" + context
# pass system_prompt to your LLM
```

---

## 5. Try the CLI

```bash
# record interactively
fossil record

# search
fossil search "JSON parsing failure"

# list recent fossils
fossil list

# check connection
fossil ping
```

---

## Use the community API instead

Skip the local embedder entirely. Point at the live API:

```python
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```

Or with the CLI:

```bash
fossil search "JSON parsing failure" --api-url https://fossil-api.hello-76a.workers.dev
fossil ping --api-url https://fossil-api.hello-76a.workers.dev
```

No install of `sentence-transformers` or `torch` required.

---

## Use the MCP server

For Claude Code, Codex CLI, Cursor, or any MCP-compatible agent:

```bash
npx @openfossil/mcp
```

Add to your MCP config:

```json
{
  "mcpServers": {
    "fossil": {
      "command": "npx",
      "args": ["@openfossil/mcp"]
    }
  }
}
```

Your agent can now call `fossil_search` before any step and `fossil_record` after any failure automatically.

---

## Next steps

- [Concepts](./concepts.md) — understand the mental model and how search works
- [CLI Reference](./cli.md) — full command reference
- [Integrations](./integrations/README.md) — framework-specific guides
- [Protocol Spec](./protocol.md) — full schema reference