# @openfossil/sdk

JavaScript/TypeScript SDK for FOSSIL — semantic failure memory for AI agents.

Works in Node.js, Deno, Bun, Cloudflare Workers, and any environment with `fetch`.
No local embedder needed — embeddings run on the FOSSIL API side.

## Install

```bash
npm install @openfossil/sdk
```

## Quickstart

```typescript
import { createFossil } from "@openfossil/sdk";
import { FailureType, ResolutionType, Severity, TaskDomain } from "@openfossil/core";

const fossil = createFossil();
// or point at self-hosted:
// const fossil = createFossil({ apiUrl: "https://your-server.com" });

// record a failure
const record = await fossil.record({
  situation: "agent extracting JSON from LLM output that returned markdown-fenced text",
  failure_type: "format_failure",
  failure: "JSON.parse failed — model wrapped output in ```json fences",
  severity: "major",
  resolution_type: "input_sanitization",
  resolution: "strip markdown fences before parsing",
  framework: "custom",
  model: "claude-opus-4-5",
  domain: "data_analysis",
  verified: true,
});

console.log(record.id);

// search before acting
const results = await fossil.search("parsing structured data from LLM output");
for (const { record, score } of results) {
  console.log(score, record.resolution.description);
}
```

## Inject into agent context

```typescript
import { createFossil, formatForInjection } from "@openfossil/sdk";

const fossil = createFossil();

async function runStep(task: string, basePrompt: string): Promise<string> {
  const results = await fossil.search(task, { top_k: 3, min_score: 0.5 });
  const context = formatForInjection(results);
  const systemPrompt = basePrompt + "\n\n" + context;
  // pass systemPrompt to your LLM
  return systemPrompt;
}
```

## Community pool

```typescript
// search only shared community fossils
const results = await fossil.search("tool call with wrong arguments", {
  pool: "community",
  min_score: 0.3,
});

// contribute a fossil to the community pool
await fossil.record({
  ...fields,
  shared: true,
});
```

## API

```typescript
const fossil = createFossil({ apiUrl?: string });

fossil.record(input: RecordInput): Promise<FossilRecord>
fossil.recordRaw(record: FossilRecord): Promise<FossilRecord>
fossil.search(situation: string, options?: SearchOptions & { pool?: "community" | "all" }): Promise<SearchResult[]>
fossil.get(id: string): Promise<FossilRecord | null>
fossil.list(limit?: number, offset?: number): Promise<ListResult>
fossil.delete(id: string): Promise<boolean>
fossil.stats(): Promise<StatsResult>
fossil.health(): Promise<{ status: string; version: string; timestamp: string }>
```

## With LangChain.js

```typescript
import { createFossil, formatForInjection } from "@openfossil/sdk";
import { ChatGroq } from "@langchain/groq";
import { SystemMessage, HumanMessage } from "@langchain/core/messages";

const fossil = createFossil();
const llm = new ChatGroq({ model: "llama-3.3-70b-versatile" });

async function runWithFossil(task: string): Promise<string> {
  const results = await fossil.search(task, { top_k: 3 });
  const context = formatForInjection(results);

  const response = await llm.invoke([
    new SystemMessage("You are a precise agent.\n\n" + context),
    new HumanMessage(task),
  ]);

  return response.content as string;
}
```

## With Vercel AI SDK

```typescript
import { createFossil, formatForInjection } from "@openfossil/sdk";
import { generateText } from "ai";
import { groq } from "@ai-sdk/groq";

const fossil = createFossil();

async function runWithFossil(task: string): Promise<string> {
  const results = await fossil.search(task, { top_k: 3 });
  const context = formatForInjection(results);

  const { text } = await generateText({
    model: groq("llama-3.3-70b-versatile"),
    system: "You are a precise agent.\n\n" + context,
    prompt: task,
  });

  return text;
}
```

## With Claude Code / Codex CLI

Use the MCP server instead — no SDK needed:

```bash
npx @openfossil/mcp
```

See [docs/integrations/claude-code.md](../../docs/integrations/claude-code.md).