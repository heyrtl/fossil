# Self-Hosting

Run your own FOSSIL server with Docker. Useful for teams who want a shared failure pool without sending data to the community API.

---

## Requirements

- Docker and Docker Compose
- 512MB RAM minimum

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/heyrtl/fossil
cd fossil/self-hosted
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
POSTGRES_DB=fossil
POSTGRES_USER=fossil
POSTGRES_PASSWORD=your_strong_password_here

FOSSIL_HOST=0.0.0.0
FOSSIL_PORT=8745

EMBEDDING_BACKEND=local
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**3. Start the database**

```bash
docker compose up db -d
```

This starts PostgreSQL with pgvector. The `fossil` database and schema are created automatically.

---

## Pointing the SDK at your server

```python
from fossil import Fossil

fossil = Fossil(api_url="http://your-server:8745")
```

---

## Pointing the MCP server at your server

```json
{
  "mcpServers": {
    "fossil": {
      "command": "npx",
      "args": ["@openfossil/mcp"],
      "env": {
        "FOSSIL_API_URL": "http://your-server:8745"
      }
    }
  }
}
```

---

## Pointing the CLI at your server

```bash
export FOSSIL_API_URL=http://your-server:8745
fossil ping
fossil search "JSON parsing failure"
```

---

## Notes

The REST API server (`apps/api`) is currently designed for Cloudflare Workers deployment. A standalone Docker-compatible server is on the roadmap. For now, the self-hosted path covers the database layer — the API server runs on Cloudflare Workers and can be pointed at your own D1 database by updating `wrangler.toml`.

For full self-hosted deployments today, deploy your own Cloudflare Worker with your own D1 database. See `apps/api/DEPLOY.md`.