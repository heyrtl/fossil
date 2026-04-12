import { Hono } from "hono";
import { embed } from "../lib/embedder";
import { searchFossils } from "../lib/store";
import type { Bindings } from "../index";

export const search = new Hono<{ Bindings: Bindings }>();

search.get("/", async (c) => {
  const q = c.req.query("q");
  if (!q) return c.json({ error: "q is required" }, 400);

  const topK = Math.min(parseInt(c.req.query("top_k") ?? "5"), 20);
  const minScore = parseFloat(c.req.query("min_score") ?? "0.5");
  const domain = c.req.query("domain") ?? undefined;
  const pool = c.req.query("pool") ?? undefined;

  const queryEmbedding = await embed(c.env.AI, q);
  const results = await searchFossils(c.env.DB, queryEmbedding, topK, minScore, domain, pool);

  return c.json(results);
});