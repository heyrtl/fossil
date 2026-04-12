import { Hono } from "hono";
import type { Bindings } from "../index";

export const stats = new Hono<{ Bindings: Bindings }>();

stats.get("/", async (c) => {
  const [totals, domains, failures, shared] = await Promise.all([
    c.env.DB.prepare("SELECT COUNT(*) as total FROM fossils").first<{ total: number }>(),
    c.env.DB.prepare(`
      SELECT task_domain as domain, COUNT(*) as count
      FROM fossils
      GROUP BY task_domain
      ORDER BY count DESC
    `).all(),
    c.env.DB.prepare(`
      SELECT failure_type as type, COUNT(*) as count
      FROM fossils
      GROUP BY failure_type
      ORDER BY count DESC
    `).all(),
    c.env.DB.prepare("SELECT COUNT(*) as total FROM fossils WHERE shared = 1").first<{ total: number }>(),
  ]);

  return c.json({
    total: totals?.total ?? 0,
    shared: shared?.total ?? 0,
    by_domain: domains.results,
    by_failure_type: failures.results,
  });
});