# FOSSIL Documentation

Semantic failure memory for AI agents.

FOSSIL gives agents a memory for reasoning failures. Record what went wrong and how it was fixed. Search past failures before acting. Stop rediscovering the same mistakes.

---

## Navigation

| Document | What it covers |
|---|---|
| [Quickstart](./quickstart.md) | Install, record your first fossil, search in 5 minutes |
| [Concepts](./concepts.md) | Why FOSSIL exists, core mental model, how search works |
| [CLI Reference](./cli.md) | `fossil record`, `fossil search`, `fossil list`, `fossil ping` |
| [REST API Reference](./api.md) | All endpoints, request/response shapes, live API URL |
| [Protocol Spec](./protocol.md) | Full FossilRecord schema, failure taxonomy, resolution taxonomy |
| [Self-Hosting](./self-hosting.md) | Run your own FOSSIL server with Docker |
| [Integrations](./integrations/README.md) | Claude Code, Codex CLI, OpenClaw, LangChain, CrewAI |

---

## Install

```bash
# Python SDK + CLI + local embedder
pip install openfossil[local]

# TypeScript types
npm install @openfossil/core

# MCP server (Claude Code, Codex CLI, Cursor, any MCP client)
npx @openfossil/mcp
```

---

## Live API

The FOSSIL community API is live and free to use:

```
https://fossil-api.hello-76a.workers.dev
```

No API key required. Powered by Cloudflare Workers + D1 + Workers AI.

---

## Packages

| Package | Registry | Description |
|---|---|---|
| `openfossil` | PyPI | Python SDK + CLI |
| `@openfossil/core` | npm | TypeScript types and utilities |
| `@openfossil/mcp` | npm | MCP server for any MCP-compatible agent |

---

## Source

[github.com/heyrtl/fossil](https://github.com/heyrtl/fossil)