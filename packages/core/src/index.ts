export type {
  FossilRecord,
  AgentMeta,
  Situation,
  Failure,
  Resolution,
  SearchResult,
  SearchOptions,
  RecordInput,
  FailureType,
  ResolutionType,
  Severity,
  TaskDomain,
} from "./types.js";

export { buildRecord, validateRecord, formatForInjection } from "./schema.js";