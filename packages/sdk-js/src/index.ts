import type {
  FossilRecord,
  RecordInput,
  SearchResult,
  SearchOptions,
  TaskDomain,
} from "@openfossil/core";
import { buildRecord, formatForInjection } from "@openfossil/core";

export type { FossilRecord, RecordInput, SearchResult, SearchOptions, TaskDomain };
export { formatForInjection };

const DEFAULT_API_URL = "https://fossil-api.hello-76a.workers.dev";
const SDK_VERSION = "0.1.0";

export interface FossilClientOptions {
  apiUrl?: string;
}

export interface StatsResult {
  total: number;
  shared: number;
  by_domain: Array<{ domain: string; count: number }>;
  by_failure_type: Array<{ type: string; count: number }>;
}

export interface ListResult {
  items: FossilRecord[];
  total: number;
  limit: number;
  offset: number;
}

export class FossilClient {
  private readonly base: string;
  private readonly headers: Record<string, string>;

  constructor(options: FossilClientOptions = {}) {
    this.base = (options.apiUrl ?? DEFAULT_API_URL).replace(/\/$/, "");
    this.headers = {
      "Content-Type": "application/json",
      "User-Agent": `@openfossil/sdk/${SDK_VERSION}`,
    };
  }

  private async request<T>(
    path: string,
    method: "GET" | "POST" | "DELETE" = "GET",
    body?: unknown
  ): Promise<T> {
    const res = await fetch(`${this.base}${path}`, {
      method,
      headers: this.headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`FOSSIL API ${method} ${path} → ${res.status}: ${text}`);
    }

    return res.json() as Promise<T>;
  }

  async record(input: RecordInput): Promise<FossilRecord> {
    return this.request<FossilRecord>("/records", "POST", input);
  }

  async recordRaw(record: FossilRecord): Promise<FossilRecord> {
    return this.request<FossilRecord>("/records", "POST", record);
  }

  async search(
    situation: string,
    options: SearchOptions & { pool?: "community" | "all" } = {}
  ): Promise<SearchResult[]> {
    const params = new URLSearchParams({
      q: situation,
      top_k: String(options.top_k ?? 5),
      min_score: String(options.min_score ?? 0.5),
    });
    if (options.domain) params.set("domain", options.domain);
    if (options.pool) params.set("pool", options.pool);

    return this.request<SearchResult[]>(`/search?${params.toString()}`);
  }

  async get(id: string): Promise<FossilRecord | null> {
    try {
      return await this.request<FossilRecord>(`/records/${id}`);
    } catch (err: any) {
      if (err.message?.includes("404")) return null;
      throw err;
    }
  }

  async list(limit = 20, offset = 0): Promise<ListResult> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    return this.request<ListResult>(`/records?${params.toString()}`);
  }

  async delete(id: string): Promise<boolean> {
    try {
      await this.request(`/records/${id}`, "DELETE");
      return true;
    } catch (err: any) {
      if (err.message?.includes("404")) return false;
      throw err;
    }
  }

  async stats(): Promise<StatsResult> {
    return this.request<StatsResult>("/stats");
  }

  async health(): Promise<{ status: string; version: string; timestamp: string }> {
    return this.request("/health");
  }
}

export function createFossil(options: FossilClientOptions = {}): FossilClient {
  return new FossilClient(options);
}