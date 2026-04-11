export type FailureType =
  | "misinterpretation"
  | "hallucinated_tool"
  | "format_failure"
  | "context_loss"
  | "infinite_loop"
  | "premature_termination"
  | "scope_creep"
  | "ambiguity_paralysis"
  | "tool_misuse"
  | "adversarial_input"
  | "compounding_error";

export type ResolutionType =
  | "prompt_change"
  | "tool_fix"
  | "retry"
  | "human_override"
  | "context_injection"
  | "schema_correction"
  | "step_decomposition"
  | "input_sanitization";

export type Severity = "critical" | "major" | "minor";

export type TaskDomain =
  | "code_generation"
  | "web_browsing"
  | "data_analysis"
  | "content_creation"
  | "api_integration"
  | "file_management"
  | "communication"
  | "planning"
  | "research"
  | "other";

export interface AgentMeta {
  framework: string;
  model: string;
  task_domain: TaskDomain;
}

export interface Situation {
  description: string;
  context_snapshot?: string | null;
}

export interface Failure {
  type: FailureType;
  description: string;
  severity: Severity;
  was_irreversible?: boolean;
}

export interface Resolution {
  type: ResolutionType;
  description: string;
  verified?: boolean;
  time_to_resolve_minutes?: number | null;
}

export interface FossilRecord {
  id: string;
  protocol_version: "1.0";
  timestamp: string;
  agent: AgentMeta;
  situation: Situation;
  failure: Failure;
  resolution: Resolution;
  shared?: boolean;
}

export interface SearchResult {
  record: FossilRecord;
  score: number;
}

export interface SearchOptions {
  top_k?: number;
  min_score?: number;
  domain?: TaskDomain;
}

export interface RecordInput {
  situation: string;
  context_snapshot?: string;
  failure_type: FailureType;
  failure: string;
  severity: Severity;
  was_irreversible?: boolean;
  resolution_type: ResolutionType;
  resolution: string;
  verified?: boolean;
  time_to_resolve_minutes?: number;
  framework: string;
  model: string;
  domain?: TaskDomain;
  shared?: boolean;
}