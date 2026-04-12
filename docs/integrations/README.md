# Integrations

FOSSIL works with any agent framework. The MCP server (`@openfossil/mcp`) is the universal integration — if your agent supports MCP, FOSSIL works with zero Python required.

---

## Integration matrix

| Agent / Framework | Method | Guide |
|---|---|---|
| Claude Code | MCP server | [claude-code.md](./claude-code.md) |
| OpenAI Codex CLI | MCP server | [codex-cli.md](./codex-cli.md) |
| OpenClaw | MCP server + Skill | [openclaw.md](./openclaw.md) |
| LangChain | Python SDK | [langchain.md](./langchain.md) |
| CrewAI | Python SDK | [crewai.md](./crewai.md) |
| Cursor / Windsurf | MCP server | same as [claude-code.md](./claude-code.md) |
| Any MCP client | MCP server | see MCP setup below |
| Any Python agent | Python SDK | `pip install openfossil[local]` |
| Any HTTP client | REST API | [../api.md](../api.md) |

---

## MCP setup (universal)

Install the MCP server once:

```bash
npx @openfossil/mcp
```

Add to your MCP client config:

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

This gives your agent four tools:

| Tool | What it does |
|---|---|
| `fossil_search` | Find similar past failures before acting |
| `fossil_record` | Record a failure + resolution after it happens |
| `fossil_get` | Fetch a single fossil by ID |
| `fossil_list` | List recent fossils |

---

## Python SDK setup (universal)

```bash
pip install openfossil[local]    # local embedder, no API key
pip install openfossil           # remote API only
```

```python
from fossil import Fossil, format_for_injection

# local store
fossil = Fossil()

# remote store
fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")
```