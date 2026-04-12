# FOSSIL + OpenAI Codex CLI

Codex CLI is OpenAI's terminal coding agent. It supports MCP servers via `~/.codex/config.toml`.

---

## Setup

**1. Install Codex CLI**

```bash
npm i -g @openai/codex
```

**2. Add FOSSIL to Codex MCP config**

Edit `~/.codex/config.toml`:

```toml
[[mcp_servers]]
name = "fossil"
command = "npx"
args = ["@openfossil/mcp"]

[mcp_servers.env]
FOSSIL_API_URL = "https://fossil-api.hello-76a.workers.dev"
```

**3. Verify**

Start Codex and type `/status` or check that `fossil_search` appears in the available tools.

---

## Usage

Codex can now call FOSSIL tools inline. Prompt it directly:

```
Search FOSSIL for similar failures before starting this task.
```

```
Record that failure to FOSSIL — failure type was format_failure,
we fixed it by adding explicit JSON schema to the prompt.
```

Add to your `AGENTS.md` in the Codex workspace for standing instructions:

```markdown
## Failure Memory

Use fossil_search before any step involving:
- parsing or extracting structured data
- calling external APIs
- multi-step file operations

Use fossil_record after any failure, before retrying.
```

---

## Common Codex failure patterns to record

| Situation | Failure type |
|---|---|
| Wrong file edited outside scope | `scope_creep` |
| Test command failed due to env assumption | `misinterpretation` |
| Generated code doesn't match codebase style | `format_failure` |
| Repeated same failing approach | `infinite_loop` |
| Stopped mid-refactor | `premature_termination` |