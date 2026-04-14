# Contributing to FOSSIL

FOSSIL is an open protocol and open source implementation. Contributions are welcome in three areas.

---

## 1. [Bug reports](./.github/ISSUE_TEMPLATE/bug_report.md)

Open an issue on GitHub. Include:

- What you were doing
- What you expected
- What actually happened
- Your OS, Python version, and `openfossil` version (`fossil --version`)

---

## 2. Protocol implementations

The most valuable contribution is a FOSSIL implementation in a new language or framework.

An implementation is conformant if it:

1. Produces records that validate against `schema/fossil.v1.json`
2. Correctly parses records produced by other conformant implementations
3. Never transmits records with `shared: false` to any external service

Read [FOSSIL.md](./FOSSIL.md) for the full protocol spec before implementing.

Once your implementation is working, open an issue linking to it and we'll add it to the implementations table in FOSSIL.md.

---

## 3. Community fossils

The most direct contribution is recording real agent failures to the community pool.

```python
from fossil import Fossil, FailureType, ResolutionType, Severity, TaskDomain

fossil = Fossil(api_url="https://fossil-api.hello-76a.workers.dev")

fossil.record(
    situation="...",
    failure_type=FailureType.FORMAT_FAILURE,
    failure="...",
    severity=Severity.MAJOR,
    resolution_type=ResolutionType.INPUT_SANITIZATION,
    resolution="...",
    framework="langchain",
    model="llama-3.3-70b-versatile",
    domain=TaskDomain.DATA_ANALYSIS,
    verified=True,
    shared=True,
)
```

Guidelines for community fossils:

- `verified=True` only if the resolution actually fixed the problem
- Anonymize `context_snapshot` before setting `shared=True` — remove API keys, user data, internal URLs
- No synthetic or fabricated failures — real failures only
- One root cause per fossil — if a step had multiple things go wrong, record them separately

---

## Code contributions

For changes to the Python SDK, JS SDK, MCP server, or REST API:

1. Open an issue first describing what you want to change and why
2. Fork the repo
3. Make your change with tests if applicable
4. Open a PR against `main`

The protocol schema (`schema/fossil.v1.json`) and failure taxonomy are intentionally stable. Changes to these require a protocol version bump and strong justification.

---

## [Code of conduct](./CODE_OF_CONDUCT.md)

Be direct. Be honest. Don't waste people's time.