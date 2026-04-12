import { Hono } from "hono";
import { buildRecord, validateRecord } from "@openfossil/core";
import { embed } from "../lib/embedder";
import {
  deleteFossil,
  getFossil,
  insertFossil,
  listFossils,
  countFossils,
} from "../lib/store";
import type { Bindings } from "../index";

export const records = new Hono<{ Bindings: Bindings }>();

records.post("/", async (c) => {
  const body = await c.req.json().catch(() => null);
  if (!body) return c.json({ error: "invalid JSON" }, 400);

  let record;
  if (body.id && body.protocol_version) {
    if (!validateRecord(body)) return c.json({ error: "invalid fossil record" }, 400);
    record = body;
  } else {
    if (!body.situation || !body.failure_type || !body.failure || !body.severity ||
        !body.resolution_type || !body.resolution || !body.framework || !body.model) {
      return c.json({ error: "missing required fields" }, 400);
    }
    record = buildRecord(body);
  }

  const situationText = `${record.situation.description} | ${record.failure.description}`;
  const embedding = await embed(c.env.AI, situationText);
  await insertFossil(c.env.DB, record, embedding);

  return c.json(record, 201);
});

records.get("/", async (c) => {
  const limit = Math.min(parseInt(c.req.query("limit") ?? "20"), 100);
  const offset = parseInt(c.req.query("offset") ?? "0");
  const [items, total] = await Promise.all([
    listFossils(c.env.DB, limit, offset),
    countFossils(c.env.DB),
  ]);
  return c.json({ items, total, limit, offset });
});

records.get("/:id", async (c) => {
  const record = await getFossil(c.env.DB, c.req.param("id"));
  if (!record) return c.json({ error: "not found" }, 404);
  return c.json(record);
});

records.delete("/:id", async (c) => {
  const deleted = await deleteFossil(c.env.DB, c.req.param("id"));
  if (!deleted) return c.json({ error: "not found" }, 404);
  return c.json({ deleted: true });
});