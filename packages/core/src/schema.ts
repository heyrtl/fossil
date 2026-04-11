import type { FossilRecord, RecordInput } from "./types.js";

const FOSSIL_ID_PATTERN = /^fossil_[a-f0-9]{12}$/;

function generateId(): string {
  const bytes = Array.from(crypto.getRandomValues(new Uint8Array(6)));
  return "fossil_" + bytes.map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function buildRecord(input: RecordInput): FossilRecord {
  return {
    id: generateId(),
    protocol_version: "1.0",
    timestamp: new Date().toISOString(),
    agent: {
      framework: input.framework,
      model: input.model,
      task_domain: input.domain ?? "other",
    },
    situation: {
      description: input.situation,
      context_snapshot: input.context_snapshot ?? null,
    },
    failure: {
      type: input.failure_type,
      description: input.failure,
      severity: input.severity,
      was_irreversible: input.was_irreversible ?? false,
    },
    resolution: {
      type: input.resolution_type,
      description: input.resolution,
      verified: input.verified ?? false,
      time_to_resolve_minutes: input.time_to_resolve_minutes ?? null,
    },
    shared: input.shared ?? false,
  };
}

export function validateRecord(record: unknown): record is FossilRecord {
  if (typeof record !== "object" || record === null) return false;
  const r = record as Record<string, unknown>;

  if (!FOSSIL_ID_PATTERN.test(r.id as string)) return false;
  if (r.protocol_version !== "1.0") return false;
  if (typeof r.timestamp !== "string") return false;
  if (typeof r.agent !== "object" || r.agent === null) return false;
  if (typeof r.situation !== "object" || r.situation === null) return false;
  if (typeof r.failure !== "object" || r.failure === null) return false;
  if (typeof r.resolution !== "object" || r.resolution === null) return false;

  return true;
}

export function formatForInjection(
  results: Array<{ record: FossilRecord; score: number }>,
  maxResults = 3
): string {
  if (results.length === 0) return "";

  const lines = ["[FOSSIL: Similar past failures retrieved]\n"];
  for (const [i, { record, score }] of results.slice(0, maxResults).entries()) {
    lines.push(`--- Fossil ${i + 1} (similarity: ${score.toFixed(2)}) ---`);
    lines.push(`Situation: ${record.situation.description}`);
    lines.push(`What failed: ${record.failure.description}`);
    lines.push(`How it was resolved: ${record.resolution.description}`);
    lines.push("");
  }
  lines.push("[End of FOSSIL context]\n");
  return lines.join("\n");
}