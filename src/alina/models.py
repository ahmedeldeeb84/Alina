from __future__ import annotations

from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Mode(str, Enum):
    NAVIGATION = "navigation"
    REALITY_CHECK = "reality_check"


class Importance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Reversibility(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PriorSituationContext(StrictModel):
    created_at: str | None = None
    title: str | None = None
    summary: str
    tensions: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    outcome: str | None = None


class SituationInput(StrictModel):
    title: str | None = None
    narrative: str = Field(min_length=20, max_length=30_000)
    goal: str | None = None
    constraints: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    mode: Mode = Mode.NAVIGATION
    history_context: list[PriorSituationContext] = Field(default_factory=list, max_length=8)

    @field_validator("title", "goal")
    @classmethod
    def clean_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class EvidenceItem(StrictModel):
    id: str = Field(pattern=r"^[FAU]\d+$")
    statement: str = Field(min_length=3)
    kind: Literal["stated_fact", "assumption", "unknown"]
    importance: Importance = Importance.MEDIUM


class Tension(StrictModel):
    name: str
    description: str
    evidence_refs: list[str] = Field(default_factory=list)


class StakeholderLens(StrictModel):
    stakeholder: str
    role: str = "unknown"
    stated_interests: list[str] = Field(default_factory=list)
    hypothesized_interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    uncertainty: str = "Material context may be missing."


class AlternativeHypothesis(StrictModel):
    hypothesis: str
    supporting_signals: list[str] = Field(default_factory=list)
    weakening_signals: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class Risk(StrictModel):
    description: str
    severity: Importance = Importance.MEDIUM
    evidence_refs: list[str] = Field(default_factory=list)


class DecisionOption(StrictModel):
    name: str
    action: str
    benefits: list[str] = Field(default_factory=list)
    downsides: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    reversibility: Reversibility = Reversibility.MEDIUM
    evidence_refs: list[str] = Field(default_factory=list)


class Recommendation(StrictModel):
    action: str
    rationale: str
    first_step: str
    evidence_refs: list[str] = Field(default_factory=list)


class ConversationFraming(StrictModel):
    objective: str
    opening: str
    facts_to_state: list[str] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(default_factory=list)
    clear_ask: str
    avoid: list[str] = Field(default_factory=list)


class SignalToWatch(StrictModel):
    signal: str
    meaning: str


class LongitudinalInsight(StrictModel):
    pattern: str
    implication: str
    evidence: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM


class SituationAnalysis(StrictModel):
    schema_version: str = "1.0"
    summary: str
    facts: list[EvidenceItem]
    assumptions: list[EvidenceItem]
    unknowns: list[EvidenceItem]
    tensions: list[Tension] = Field(default_factory=list)
    stakeholders: list[StakeholderLens] = Field(default_factory=list)
    alternative_hypotheses: list[AlternativeHypothesis] = Field(default_factory=list)
    risks_of_action: list[Risk] = Field(default_factory=list)
    risks_of_inaction: list[Risk] = Field(default_factory=list)
    options: list[DecisionOption]
    recommendation: Recommendation
    conversation_framing: ConversationFraming
    signals_to_watch: list[SignalToWatch] = Field(default_factory=list)
    longitudinal_insights: list[LongitudinalInsight] = Field(default_factory=list)
    confidence: Confidence
    confidence_reason: str
    cautions: list[str] = Field(default_factory=list)
    provider: str = "unknown"
    model: str | None = None


class PatternFinding(StrictModel):
    label: str
    count: int = Field(ge=1)
    share: float = Field(ge=0.0, le=1.0)
    examples: list[str] = Field(default_factory=list)


class PatternReport(StrictModel):
    total_situations: int = Field(ge=0)
    window_days: int | None = None
    recurring_tensions: list[PatternFinding] = Field(default_factory=list)
    recurring_unknowns: list[PatternFinding] = Field(default_factory=list)
    recurring_stakeholders: list[PatternFinding] = Field(default_factory=list)
    confidence_distribution: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class StoredSituation(StrictModel):
    id: str
    created_at: str
    input: SituationInput
    analysis: SituationAnalysis
