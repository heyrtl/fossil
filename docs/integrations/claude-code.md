# FOSSIL + Claude Code

Claude Code is Anthropic's terminal coding agent. It is MCP-native — FOSSIL plugs in with a single config entry.

---

## Setup

**1. Add to Claude Code MCP config**

Claude Code reads MCP servers from `~/.claude/claude.json` (or your project-level `.claude/claude.json`).

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

**2. Verify**

Start Claude Code and run:

```
/mcp
```

You should see `fossil` listed with tools: `fossil_search`, `fossil_record`, `fossil_get`, `fossil_list`.

---

## Usage

Claude Code will now automatically have access to FOSSIL tools. You can instruct it explicitly:

```
Before starting this refactor, search FOSSIL for similar past failures.
```

```
That tool call failed. Record this to FOSSIL so we don't hit it again.
```

Or add a standing instruction to your `CLAUDE.md`:

```markdown
## FOSSIL

Before any non-trivial agent step, call fossil_search with a description
of what you are about to do. If results are returned, read the resolutions
before proceeding.

After any failure, call fossil_record to capture what went wrong and what fixed it.
```

---

## What gets recorded

Claude Code hits these failure types most often:

- `hallucinated_tool` — calling an MCP tool with wrong arguments
- `format_failure` — output schema mismatch
- `scope_creep` — editing files outside the intended scope
- `context_loss` — losing track of constraints in long sessions
- `tool_misuse` — correct tool, wrong usage pattern

---

## Local vs remote store

**Remote (recommended for Claude Code)** — set `FOSSIL_API_URL` in the MCP config env block. No local model download needed.

**Local** — omit `FOSSIL_API_URL`. The MCP server defaults to `http://127.0.0.1:8745` and requires the FOSSIL server running locally (see [self-hosting](../self-hosting.md)).