# Protocol Specification

FOSSIL Protocol v1.0

The full JSON Schema is at `schema/fossil.v1.json` in the repository.

---

## FossilRecord

```typescript
interface FossilRecord {
  id: string                  // "fossil_" + 12 hex chars
  protocol_version: "1.0"
  timestamp: string           // ISO 8601 UTC
  agent: AgentMeta
  situation: Situation
  failure: Failure
  resolution: Resolution
  shared: boolean             // default false
}
```

---

## AgentMeta

```typescript
interface AgentMeta {
  framework: string           // "langchain" | "crewai" | "claude" | "custom" | ...
  model: string               // "llama-3.3-70b-versatile" | "gpt-4o" | ...
  task_domain: TaskDomain
}
```

---

## Situation

```typescript
interface Situation {
  description: string         // what was the agent attempting (min 10 chars)
  context_snapshot?: string   // truncated, anonymized context window (optional)
}
```

`description` is the primary semantic search field. It is embedded at record time and used for cosine similarity retrieval.

---

## Failure

```typescript
interface Failure {
  type: FailureType
  description: string         // what went wrong (min 10 chars)
  severity: "critical" | "major" | "minor"
  was_irreversible: boolean   // caused side effects that cannot be undone
}
```

---

## Resolution

```typescript
interface Resolution {
  type: ResolutionType
  description: string         // what fixed it (min 10 chars)
  verified: boolean           // was the fix confirmed to work
  time_to_resolve_minutes?: number
}
```

---

## FailureType

| Value | When to use |
|---|---|
| `misinterpretation` | Agent misread the task or user intent |
| `hallucinated_tool` | Called a tool that doesn't exist or with wrong signature |
| `format_failure` | Output didn't match expected schema or format |
| `context_loss` | Forgot earlier context in a multi-step run |
| `infinite_loop` | Got stuck in a reasoning or tool-call cycle |
| `premature_termination` | Declared done when the task was incomplete |
| `scope_creep` | Did more than asked, touched things it shouldn't |
| `ambiguity_paralysis` | Couldn't proceed due to underspecified input |
| `tool_misuse` | Right tool, wrong usage or arguments |
| `adversarial_input` | User input caused unexpected behavior |
| `compounding_error` | Small error amplified across multiple steps |

---

## ResolutionType

| Value | When to use |
|---|---|
| `prompt_change` | Modified the system or user prompt |
| `tool_fix` | Fixed the tool definition, schema, or implementation |
| `retry` | Retrying the step succeeded without changes |
| `human_override` | A human intervened directly |
| `context_injection` | Injected missing context into the agent's window |
| `schema_correction` | Fixed the output schema or parser |
| `step_decomposition` | Broke the failing step into smaller sub-steps |
| `input_sanitization` | Cleaned or validated input before processing |

---

## TaskDomain

`code_generation` `web_browsing` `data_analysis` `content_creation`
`api_integration` `file_management` `communication` `planning` `research` `other`

---

## Full example

```json
{
  "id": "fossil_7b0b0ce1999a",
  "protocol_version": "1.0",
  "timestamp": "2026-04-12T02:32:56.323Z",
  "agent": {
    "framework": "langchain",
    "model": "llama-3.3-70b-versatile",
    "task_domain": "data_analysis"
  },
  "situation": {
    "description": "agent extracting JSON from LLM output that returned markdown-fenced text",
    "context_snapshot": null
  },
  "failure": {
    "type": "format_failure",
    "description": "json.loads raised JSONDecodeError — model wrapped output in ```json fences",
    "severity": "major",
    "was_irreversible": false
  },
  "resolution": {
    "type": "input_sanitization",
    "description": "strip markdown fences with regex before parsing",
    "verified": true,
    "time_to_resolve_minutes": 12
  },
  "shared": false
}
```

---

## Versioning

`protocol_version` is independent of SDK versions. Breaking schema changes increment the protocol version. Implementations must reject records with unknown protocol versions.

---

## Conformance

An implementation is conformant if it:

1. Produces records that validate against `schema/fossil.v1.json`
2. Correctly parses records produced by other conformant implementations
3. Never transmits records with `shared: false` to any external service