import { Hono } from "hono";
import { cors } from "hono/cors";
import { records } from "./routes/records";
import { search } from "./routes/search";

export type Bindings = {
  DB: D1Database;
  AI: Ai;
};

const app = new Hono<{ Bindings: Bindings }>();

app.use("*", cors());

app.get("/health", (c) =>
  c.json({ status: "ok", version: "0.1.0", timestamp: new Date().toISOString() })
);

app.route("/records", records);
app.route("/search", search);

app.notFound((c) => c.json({ error: "not found" }, 404));
app.onError((err, c) => {
  console.error(err);
  return c.json({ error: "internal server error" }, 500);
});

export default app;