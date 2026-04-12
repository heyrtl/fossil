import type { FossilRecord } from "./types";
import { cosineSimilarity } from "./embedder";

export interface SearchResult {
  record: FossilRecord;
  score: number;
}

export async function insertFossil(
  db: D1Database,
  record: FossilRecord,
  embedding: number[]
): Promise<void> {
  const embeddingJson = JSON.stringify(embedding);
  await db
    .prepare(
      `INSERT OR REPLACE INTO fossils (
        id, protocol_version, timestamp,
        framework, model, task_domain,
        situation, context_snapshot,
        failure_type, failure_description, severity, was_irreversible,
        resolution_type, resolution_description, verified, time_to_resolve_minutes,
        embedding, shared
      ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
    )
    .bind(
      record.id,
      record.protocol_version,
      record.timestamp,
      record.agent.framework,
      record.agent.model,
      record.agent.task_domain,
      record.situation.description,
      record.situation.context_snapshot ?? null,
      record.failure.type,
      record.failure.description,
      record.failure.severity,
      record.failure.was_irreversible ? 1 : 0,
      record.resolution.type,
      record.resolution.description,
      record.resolution.verified ? 1 : 0,
      record.resolution.time_to_resolve_minutes ?? null,
      embeddingJson,
      record.shared ? 1 : 0
    )
    .run();
}

export async function searchFossils(
  db: D1Database,
  queryEmbedding: number[],
  topK: number,
  minScore: number,
  domain?: string,
  pool?: string
): Promise<SearchResult[]> {
  const conditions: string[] = [];
  const bindings: unknown[] = [];

  if (domain) {
    conditions.push("task_domain = ?");
    bindings.push(domain);
  }

  if (pool === "community") {
    conditions.push("shared = 1");
  }

  let query = "SELECT * FROM fossils";
  if (conditions.length > 0) {
    query += " WHERE " + conditions.join(" AND ");
  }

  const { results } = await db
    .prepare(query)
    .bind(...bindings)
    .all();

  const scored = results
    .map((row: any) => {
      const embedding = JSON.parse(row.embedding as string) as number[];
      const score = cosineSimilarity(queryEmbedding, embedding);
      return { row, score };
    })
    .filter(({ score }) => score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  return scored.map(({ row, score }) => ({
    record: rowToRecord(row),
    score: Math.round(score * 10000) / 10000,
  }));
}

export async function getFossil(
  db: D1Database,
  id: string
): Promise<FossilRecord | null> {
  const row = await db
    .prepare("SELECT * FROM fossils WHERE id = ?")
    .bind(id)
    .first();
  if (!row) return null;
  return rowToRecord(row as any);
}

export async function deleteFossil(
  db: D1Database,
  id: string
): Promise<boolean> {
  const result = await db
    .prepare("DELETE FROM fossils WHERE id = ?")
    .bind(id)
    .run();
  return (result.meta.changes ?? 0) > 0;
}

export async function listFossils(
  db: D1Database,
  limit: number,
  offset: number
): Promise<FossilRecord[]> {
  const { results } = await db
    .prepare(
      "SELECT * FROM fossils ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    )
    .bind(limit, offset)
    .all();
  return results.map((row) => rowToRecord(row as any));
}

export async function countFossils(db: D1Database): Promise<number> {
  const row = await db
    .prepare("SELECT COUNT(*) as count FROM fossils")
    .first<{ count: number }>();
  return row?.count ?? 0;
}

function rowToRecord(row: any): FossilRecord {
  return {
    id: row.id,
    protocol_version: row.protocol_version,
    timestamp: row.timestamp,
    agent: {
      framework: row.framework,
      model: row.model,
      task_domain: row.task_domain,
    },
    situation: {
      description: row.situation,
      context_snapshot: row.context_snapshot ?? null,
    },
    failure: {
      type: row.failure_type,
      description: row.failure_description,
      severity: row.severity,
      was_irreversible: row.was_irreversible === 1,
    },
    resolution: {
      type: row.resolution_type,
      description: row.resolution_description,
      verified: row.verified === 1,
      time_to_resolve_minutes: row.time_to_resolve_minutes ?? null,
    },
    shared: row.shared === 1,
  };
}