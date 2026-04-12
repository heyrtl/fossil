import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { TOOLS, type ToolName } from "./tools.js";

const FOSSIL_API_URL = process.env.FOSSIL_API_URL ?? "https://fossil-api.hello-76a.workers.dev";

async function callFossilAPI(
  path: string,
  method: "GET" | "POST" | "DELETE",
  body?: unknown
): Promise<unknown> {
  const url = `${FOSSIL_API_URL}${path}`;
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`FOSSIL API ${method} ${path} → ${res.status}: ${text}`);
  }

  return res.json();
}

function formatSearchResults(results: unknown[]): string {
  if (!results.length) return "No similar fossils found above the similarity threshold.";

  return results
    .map((r: any, i: number) => {
      const { record, score } = r;
      return [
        `--- Fossil ${i + 1} (similarity: ${score.toFixed(2)}) ---`,
        `ID: ${record.id}`,
        `Situation: ${record.situation.description}`,
        `Failure (${record.failure.type}): ${record.failure.description}`,
        `Severity: ${record.failure.severity}`,
        `Resolution (${record.resolution.type}): ${record.resolution.description}`,
        `Verified: ${record.resolution.verified}`,
      ].join("\n");
    })
    .join("\n\n");
}

function formatRecord(record: any): string {
  return [
    `ID: ${record.id}`,
    `Timestamp: ${record.timestamp}`,
    `Framework: ${record.agent.framework} | Model: ${record.agent.model} | Domain: ${record.agent.task_domain}`,
    `Situation: ${record.situation.description}`,
    `Failure (${record.failure.type}, ${record.failure.severity}): ${record.failure.description}`,
    `Irreversible: ${record.failure.was_irreversible}`,
    `Resolution (${record.resolution.type}): ${record.resolution.description}`,
    `Verified: ${record.resolution.verified}`,
  ].join("\n");
}

export function createServer(): Server {
  const server = new Server(
    { name: "openfossil", version: "0.1.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: TOOLS.map((t) => ({
      name: t.name,
      description: t.description,
      inputSchema: t.inputSchema,
    })),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (req) => {
    const { name, arguments: args = {} } = req.params;
    const tool = name as ToolName;

    try {
      switch (tool) {
        case "fossil_search": {
          const params = new URLSearchParams();
          params.set("q", args.situation as string);
          if (args.top_k) params.set("top_k", String(args.top_k));
          if (args.min_score) params.set("min_score", String(args.min_score));
          if (args.domain) params.set("domain", args.domain as string);

          const results = await callFossilAPI(
            `/search?${params.toString()}`,
            "GET"
          );
          return {
            content: [
              {
                type: "text",
                text: formatSearchResults(results as unknown[]),
              },
            ],
          };
        }

        case "fossil_record": {
          const record = await callFossilAPI("/records", "POST", args);
          return {
            content: [
              {
                type: "text",
                text: `Fossil recorded.\n${formatRecord(record)}`,
              },
            ],
          };
        }

        case "fossil_get": {
          const record = await callFossilAPI(`/records/${args.id}`, "GET");
          return {
            content: [{ type: "text", text: formatRecord(record) }],
          };
        }

        case "fossil_list": {
          const params = new URLSearchParams();
          if (args.limit) params.set("limit", String(args.limit));
          if (args.offset) params.set("offset", String(args.offset));

          const records = await callFossilAPI(
            `/records?${params.toString()}`,
            "GET"
          ) as any[];

          if (!records.length) {
            return {
              content: [{ type: "text", text: "No fossils recorded yet." }],
            };
          }

          const text = records.map(formatRecord).join("\n\n---\n\n");
          return { content: [{ type: "text", text }] };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (err: any) {
      return {
        content: [{ type: "text", text: `Error: ${err.message}` }],
        isError: true,
      };
    }
  });

  return server;
}