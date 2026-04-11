export const TOOLS = [
  {
    name: "fossil_search",
    description:
      "Search FOSSIL for semantically similar past agent failures before attempting a task. " +
      "Returns matching failure records with resolutions you can learn from. " +
      "Call this at the start of any non-trivial agent step.",
    inputSchema: {
      type: "object",
      required: ["situation"],
      properties: {
        situation: {
          type: "string",
          description: "Describe what the agent is about to attempt or is currently doing.",
        },
        top_k: {
          type: "number",
          description: "Max number of results to return. Default 5.",
        },
        min_score: {
          type: "number",
          description: "Minimum similarity score 0-1. Default 0.5.",
        },
        domain: {
          type: "string",
          description:
            "Filter by task domain. One of: code_generation, web_browsing, data_analysis, " +
            "content_creation, api_integration, file_management, communication, planning, research, other.",
        },
      },
    },
  },
  {
    name: "fossil_record",
    description:
      "Record a reasoning failure and its resolution into FOSSIL. " +
      "Call this after any agent failure once you have identified the cause and fix.",
    inputSchema: {
      type: "object",
      required: [
        "situation",
        "failure_type",
        "failure",
        "severity",
        "resolution_type",
        "resolution",
        "framework",
        "model",
      ],
      properties: {
        situation: {
          type: "string",
          description: "What was the agent attempting when it failed?",
        },
        failure_type: {
          type: "string",
          enum: [
            "misinterpretation",
            "hallucinated_tool",
            "format_failure",
            "context_loss",
            "infinite_loop",
            "premature_termination",
            "scope_creep",
            "ambiguity_paralysis",
            "tool_misuse",
            "adversarial_input",
            "compounding_error",
          ],
        },
        failure: {
          type: "string",
          description: "What went wrong, in plain language.",
        },
        severity: {
          type: "string",
          enum: ["critical", "major", "minor"],
        },
        resolution_type: {
          type: "string",
          enum: [
            "prompt_change",
            "tool_fix",
            "retry",
            "human_override",
            "context_injection",
            "schema_correction",
            "step_decomposition",
            "input_sanitization",
          ],
        },
        resolution: {
          type: "string",
          description: "What fixed it.",
        },
        framework: {
          type: "string",
          description: "Agent framework e.g. langchain, claude, custom.",
        },
        model: {
          type: "string",
          description: "Model used e.g. llama-3.3-70b.",
        },
        domain: {
          type: "string",
          description: "Task domain. Defaults to other.",
        },
        context_snapshot: {
          type: "string",
          description: "Optional truncated context window at time of failure.",
        },
        was_irreversible: {
          type: "boolean",
          description: "Did the failure cause side effects that could not be undone?",
        },
        verified: {
          type: "boolean",
          description: "Was the resolution confirmed to work?",
        },
        shared: {
          type: "boolean",
          description: "Opt into the community pool. Default false.",
        },
      },
    },
  },
  {
    name: "fossil_get",
    description: "Retrieve a single FOSSIL record by ID.",
    inputSchema: {
      type: "object",
      required: ["id"],
      properties: {
        id: {
          type: "string",
          description: "The fossil ID e.g. fossil_a1b2c3d4e5f6",
        },
      },
    },
  },
  {
    name: "fossil_list",
    description: "List recent FOSSIL records. Useful for reviewing your failure archive.",
    inputSchema: {
      type: "object",
      properties: {
        limit: {
          type: "number",
          description: "Max records to return. Default 20.",
        },
        offset: {
          type: "number",
          description: "Pagination offset. Default 0.",
        },
      },
    },
  },
] as const;

export type ToolName = (typeof TOOLS)[number]["name"];