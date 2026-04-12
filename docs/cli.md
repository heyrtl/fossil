# CLI Reference

The `fossil` CLI is included with `pip install openfossil`.

All commands accept `--api-url` to point at a remote FOSSIL API, or `--db` to specify a local SQLite path. If neither is provided, defaults to `~/.fossil/fossil.db`.

The environment variable `FOSSIL_API_URL` is read automatically — set it once and all commands use the remote API without flags.

```bash
export FOSSIL_API_URL=https://fossil-api.hello-76a.workers.dev
```

---

## fossil record

Record a reasoning failure interactively.

```bash
fossil record [OPTIONS]
```

Prompts for each field if not provided as a flag. Walks through failure type, severity, resolution type, and domain with numbered menus.

**Options**

| Flag | Description |
|---|---|
| `--situation TEXT` | What was the agent attempting? |
| `--failure TEXT` | What went wrong? |
| `--resolution TEXT` | What fixed it? |
| `--framework TEXT` | Agent framework e.g. langchain, custom |
| `--model TEXT` | Model used e.g. llama-3.3-70b-versatile |
| `--shared` | Contribute to the community pool |
| `--api-url TEXT` | Remote FOSSIL API URL |
| `--db TEXT` | Path to local SQLite DB |

**Example**

```bash
fossil record \
  --situation "agent called finish tool before task was complete" \
  --failure "model declared done after step 2 of 5" \
  --resolution "added explicit step count to system prompt" \
  --framework custom \
  --model llama-3.3-70b-versatile
```

---

## fossil search

Search for semantically similar past failures.

```bash
fossil search QUERY [OPTIONS]
```

**Arguments**

| Argument | Description |
|---|---|
| `QUERY` | Natural language description of the situation |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--top-k INTEGER` | 5 | Max results to return |
| `--min-score FLOAT` | 0.5 | Minimum similarity score (0–1) |
| `--domain TEXT` | None | Filter by task domain |
| `--json` | False | Output as JSON |
| `--api-url TEXT` | | Remote FOSSIL API URL |
| `--db TEXT` | | Path to local SQLite DB |

**Example**

```bash
# basic search
fossil search "agent failing to parse JSON output"

# against live API, JSON output
fossil search "tool call with wrong argument type" \
  --api-url https://fossil-api.hello-76a.workers.dev \
  --json

# filter by domain
fossil search "extracting data from document" --domain data_analysis
```

**Valid domains**

`code_generation` `web_browsing` `data_analysis` `content_creation`
`api_integration` `file_management` `communication` `planning` `research` `other`

---

## fossil list

List recent fossils.

```bash
fossil list [OPTIONS]
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--limit INTEGER` | 20 | Max records to return |
| `--offset INTEGER` | 0 | Pagination offset |
| `--json` | False | Output as JSON |
| `--api-url TEXT` | | Remote FOSSIL API URL |
| `--db TEXT` | | Path to local SQLite DB |

**Example**

```bash
fossil list --limit 5
fossil list --json > fossils.json
```

---

## fossil ping

Check connection to the FOSSIL store.

```bash
fossil ping [OPTIONS]
```

Prints store type (local or remote), URL or path, and fossil count. Exits with code 1 if connection fails.

**Example**

```bash
fossil ping
# ✓ Connected to local (/Users/you/.fossil/fossil.db)
#   4 fossils in store

fossil ping --api-url https://fossil-api.hello-76a.workers.dev
# ✓ Connected to remote (https://fossil-api.hello-76a.workers.dev)
#   12 fossils in store
```