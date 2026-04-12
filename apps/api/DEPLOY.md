# Deploying FOSSIL API

Cloudflare Workers + D1 + Workers AI. All free tier.

## Prerequisites

```bash
npm install -g wrangler
wrangler login
```

## 1. Create the D1 database

```bash
wrangler d1 create fossil
```

Copy the `database_id` from the output into `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "fossil"
database_id = "your-database-id-here"
```

## 2. Run the schema

```bash
cd apps/api

# local dev
npm run db:init

# production
npm run db:init:remote
```

## 3. Run locally

```bash
npm run dev
```

API available at `http://localhost:8787`.

## 4. Deploy

```bash
npm run deploy
```

Your API is live at `https://fossil-api.<your-subdomain>.workers.dev`.

## API

```
GET  /health
POST /records          body: RecordInput or FossilRecord
GET  /records?limit=20&offset=0
GET  /records/:id
DELETE /records/:id
GET  /search?q=<situation>&top_k=5&min_score=0.5&domain=<domain>
```

## Point the MCP server at your deployment

```bash
FOSSIL_API_URL=https://fossil-api.<your-subdomain>.workers.dev npx @fossil/mcp
```

## Point the Python SDK at your deployment

```python
# coming in SDK v0.2.0 — remote store support
```