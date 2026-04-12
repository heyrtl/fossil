# REST API Reference

**Base URL:** `https://fossil-api.hello-76a.workers.dev`

No authentication required. No rate limits enforced currently.
Powered by Cloudflare Workers + D1 + Workers AI (`bge-small-en-v1.5`).

---

## GET /health

Check API status.

**Response**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-04-12T02:25:06.273Z"
}
```

---

## POST /records

Record a fossil. Accepts either a full `FossilRecord` object or a convenience `RecordInput` shape.

**RecordInput shape (recommended)**

```json
{
  "situation": "string (required)",
  "failure_type": "format_failure (required, see taxonomy)",
  "failure": "string (required)",
  "severity": "major (required: critical | major | minor)",
  "resolution_type": "input_sanitization (required, see taxonomy)",
  "resolution": "string (required)",
  "framework": "string (required)",
  "model": "string (required)",
  "domain": "data_analysis (optional, default: other)",
  "context_snapshot": "string (optional)",
  "was_irreversible": false,
  "verified": true,
  "time_to_resolve_minutes": 12,
  "shared": false
}
```

**Response** — `201 Created`

Returns the full `FossilRecord` with generated `id` and `timestamp`.

**Example**

```bash
curl -X POST https://fossil-api.hello-76a.workers.dev/records \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "agent extracting JSON from markdown-fenced LLM output",
    "failure_type": "format_failure",
    "failure": "json.loads raised JSONDecodeError on fenced output",
    "severity": "major",
    "resolution_type": "input_sanitization",
    "resolution": "strip markdown fences before parsing",
    "framework": "langchain",
    "model": "llama-3.3-70b-versatile",
    "domain": "data_analysis",
    "verified": true
  }'
```

---

## GET /search

Search for semantically similar past failures.

**Query Parameters**

| Parameter | Required | Default | Description |
|---|---|---|---|
| `q` | yes | | Natural language situation description |
| `top_k` | no | 5 | Max results (capped at 20) |
| `min_score` | no | 0.5 | Minimum cosine similarity score |
| `domain` | no | | Filter by task domain |

**Response** — `200 OK`

Array of `{ record: FossilRecord, score: number }` sorted by score descending.

**Example**

```bash
curl "https://fossil-api.hello-76a.workers.dev/search?q=parsing+JSON+from+LLM+output&min_score=0.3"
```

```json
[
  {
    "record": {
      "id": "fossil_7b0b0ce1999a",
      "protocol_version": "1.0",
      "timestamp": "2026-04-12T02:32:56.323Z",
      "agent": {
        "framework": "langchain",
        "model": "llama-3.3-70b-versatile",
        "task_domain": "data_analysis"
      },
      "situation": { "description": "...", "context_snapshot": null },
      "failure": { "type": "format_failure", "description": "...", "severity": "major", "was_irreversible": false },
      "resolution": { "type": "input_sanitization", "description": "...", "verified": true, "time_to_resolve_minutes": null },
      "shared": false
    },
    "score": 0.6879
  }
]
```

---

## GET /records

List fossils with pagination.

**Query Parameters**

| Parameter | Default | Description |
|---|---|---|
| `limit` | 20 | Max records (capped at 100) |
| `offset` | 0 | Pagination offset |

**Response**

```json
{
  "items": [ ...FossilRecord[] ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

## GET /records/:id

Fetch a single fossil by ID.

**Example**

```bash
curl https://fossil-api.hello-76a.workers.dev/records/fossil_7b0b0ce1999a
```

Returns `404` if not found.

---

## DELETE /records/:id

Delete a fossil by ID.

**Response**

```json
{ "deleted": true }
```

Returns `404` if not found.

---

## Failure type values

`misinterpretation` `hallucinated_tool` `format_failure` `context_loss`
`infinite_loop` `premature_termination` `scope_creep` `ambiguity_paralysis`
`tool_misuse` `adversarial_input` `compounding_error`

## Resolution type values

`prompt_change` `tool_fix` `retry` `human_override` `context_injection`
`schema_correction` `step_decomposition` `input_sanitization`

## Task domain values

`code_generation` `web_browsing` `data_analysis` `content_creation`
`api_integration` `file_management` `communication` `planning` `research` `other`