from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone
import uuid


class FailureType(str, Enum):
    MISINTERPRETATION = "misinterpretation"
    HALLUCINATED_TOOL = "hallucinated_tool"
    FORMAT_FAILURE = "format_failure"
    CONTEXT_LOSS = "context_loss"
    INFINITE_LOOP = "infinite_loop"
    PREMATURE_TERMINATION = "premature_termination"
    SCOPE_CREEP = "scope_creep"
    AMBIGUITY_PARALYSIS = "ambiguity_paralysis"
    TOOL_MISUSE = "tool_misuse"
    ADVERSARIAL_INPUT = "adversarial_input"
    COMPOUNDING_ERROR = "compounding_error"


class ResolutionType(str, Enum):
    PROMPT_CHANGE = "prompt_change"
    TOOL_FIX = "tool_fix"
    RETRY = "retry"
    HUMAN_OVERRIDE = "human_override"
    CONTEXT_INJECTION = "context_injection"
    SCHEMA_CORRECTION = "schema_correction"
    STEP_DECOMPOSITION = "step_decomposition"
    INPUT_SANITIZATION = "input_sanitization"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class TaskDomain(str, Enum):
    CODE_GENERATION = "code_generation"
    WEB_BROWSING = "web_browsing"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    API_INTEGRATION = "api_integration"
    FILE_MANAGEMENT = "file_management"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    RESEARCH = "research"
    OTHER = "other"


@dataclass
class AgentMeta:
    framework: str
    model: str
    task_domain: TaskDomain

    def to_dict(self) -> dict:
        return {
            "framework": self.framework,
            "model": self.model,
            "task_domain": self.task_domain.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> AgentMeta:
        return cls(
            framework=d["framework"],
            model=d["model"],
            task_domain=TaskDomain(d["task_domain"]),
        )


@dataclass
class Situation:
    description: str
    context_snapshot: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "context_snapshot": self.context_snapshot,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Situation:
        return cls(
            description=d["description"],
            context_snapshot=d.get("context_snapshot"),
        )


@dataclass
class Failure:
    type: FailureType
    description: str
    severity: Severity
    was_irreversible: bool = False

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "description": self.description,
            "severity": self.severity.value,
            "was_irreversible": self.was_irreversible,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Failure:
        return cls(
            type=FailureType(d["type"]),
            description=d["description"],
            severity=Severity(d["severity"]),
            was_irreversible=d.get("was_irreversible", False),
        )


@dataclass
class Resolution:
    type: ResolutionType
    description: str
    verified: bool = False
    time_to_resolve_minutes: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "description": self.description,
            "verified": self.verified,
            "time_to_resolve_minutes": self.time_to_resolve_minutes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Resolution:
        return cls(
            type=ResolutionType(d["type"]),
            description=d["description"],
            verified=d.get("verified", False),
            time_to_resolve_minutes=d.get("time_to_resolve_minutes"),
        )


@dataclass
class FossilRecord:
    agent: AgentMeta
    situation: Situation
    failure: Failure
    resolution: Resolution
    id: str = field(default_factory=lambda: f"fossil_{uuid.uuid4().hex[:12]}")
    protocol_version: str = "1.0"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    shared: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "protocol_version": self.protocol_version,
            "timestamp": self.timestamp,
            "agent": self.agent.to_dict(),
            "situation": self.situation.to_dict(),
            "failure": self.failure.to_dict(),
            "resolution": self.resolution.to_dict(),
            "shared": self.shared,
        }

    @classmethod
    def from_dict(cls, d: dict) -> FossilRecord:
        return cls(
            id=d["id"],
            protocol_version=d.get("protocol_version", "1.0"),
            timestamp=d["timestamp"],
            agent=AgentMeta.from_dict(d["agent"]),
            situation=Situation.from_dict(d["situation"]),
            failure=Failure.from_dict(d["failure"]),
            resolution=Resolution.from_dict(d["resolution"]),
            shared=d.get("shared", False),
        )