from __future__ import annotations

import re
from collections import OrderedDict

from alina.models import (
    AlternativeHypothesis, Confidence, ConversationFraming, DecisionOption,
    EvidenceItem, Importance, Recommendation, Reversibility, Risk,
    SignalToWatch, SituationAnalysis, SituationInput, StakeholderLens, Tension,
)


_ASSUMPTION_MARKERS = re.compile(
    r"\b(i think|i believe|i feel like|seems?|probably|maybe|might|must be|"
    r"doesn't care|does not care|wants? to|trying to|intentionally|deliberately|"
    r"obviously|clearly|i suspect|apparently)\b", re.I
)

_TENSION_RULES: list[tuple[str, str, tuple[str, ...]]] = [
    ("ownership", "Decision or execution ownership appears unclear or contested.", ("owner", "ownership", "responsible", "who should")),
    ("scope vs date", "Scope, feasibility, and deadline pressure may be in tension.", ("date", "deadline", "scope", "commit", "ship")),
    ("capacity", "Available capacity may not match expected work or support load.", ("capacity", "late", "overload", "too much", "hours", "bandwidth")),
    ("trust", "Trust or safe information-sharing is affecting the interaction.", ("trust", "misuse", "politics", "against me", "agenda")),
    ("stakeholder alignment", "Stakeholders may be operating with different expectations or context.", ("align", "pm", "manager", "stakeholder", "meeting", "expect")),
    ("execution reliability", "Repeated misses or quality of execution may be driving manager intervention.", ("failed", "missed", "broke", "again", "nightmare", "rework")),
    ("dependency", "A dependency may be outside the manager's direct control.", ("dependency", "blocked", "another team", "waiting", "external")),
    ("role clarity", "Role or decision-right boundaries may be unclear.", ("role", "responsibility", "new", "onboarding", "domain", "context")),
]

_HIGH_STAKES = re.compile(r"\b(harass|discriminat|terminate|fire|dismiss|legal|lawyer|threat|violence|unsafe|self-harm|suicide|misconduct)\b", re.I)
_HARMFUL = re.compile(r"\b(retaliat|punish|revenge|manipulat|blackmail|humiliat)\w*\b", re.I)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [re.sub(r"\s+", " ", p).strip(" -•\t") for p in parts if len(p.strip()) >= 3]


def _clip(text: str, n: int = 180) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


class HeuristicProvider:
    """Offline conservative provider. Useful for privacy-first scaffolding and demos.

    It is intentionally less ambitious than an LLM and explicitly avoids pretending
    to infer motives or causal truth from a short narrative.
    """

    name = "heuristic"
    model_name = None

    def analyze(self, situation: SituationInput) -> SituationAnalysis:
        sents = _sentences(situation.narrative)
        facts: list[EvidenceItem] = []
        assumptions: list[EvidenceItem] = []

        for s in sents[:14]:
            if _ASSUMPTION_MARKERS.search(s):
                assumptions.append(EvidenceItem(id=f"A{len(assumptions)+1}", statement=_clip(s), kind="assumption", importance=Importance.MEDIUM))
            else:
                facts.append(EvidenceItem(id=f"F{len(facts)+1}", statement=_clip(s), kind="stated_fact", importance=Importance.MEDIUM))

        if not facts and sents:
            facts.append(EvidenceItem(id="F1", statement=_clip(sents[0]), kind="stated_fact"))

        unknown_texts = self._unknowns(situation)
        unknowns = [EvidenceItem(id=f"U{i+1}", statement=u, kind="unknown", importance=Importance.HIGH if i < 2 else Importance.MEDIUM) for i, u in enumerate(unknown_texts)]

        hay = situation.narrative.lower()
        tensions: list[Tension] = []
        all_refs = [x.id for x in facts[:3]] + [x.id for x in assumptions[:2]]
        for name, desc, keys in _TENSION_RULES:
            hits = sum(1 for k in keys if k in hay)
            if hits:
                tensions.append(Tension(name=name, description=desc, evidence_refs=all_refs[: min(3, max(1, hits))]))
        if not tensions:
            tensions.append(Tension(name="ambiguity", description="The immediate management tension is not yet explicit; clarify the decision, owner, and desired outcome.", evidence_refs=all_refs[:2]))

        stakeholders = [StakeholderLens(stakeholder=x, role="provided by user", uncertainty="Only information explicitly supplied by the user is available.") for x in situation.stakeholders]
        if not stakeholders:
            for label in ("manager", "team", "PM", "other team"):
                if label.lower() in hay:
                    stakeholders.append(StakeholderLens(stakeholder=label, role="inferred from narrative", uncertainty="Role is inferred from wording; interests are not known."))

        alt = self._alternatives(situation, assumptions)
        known_refs = [x.id for x in facts + assumptions + unknowns]
        option_refs = known_refs[:4]

        options = [
            DecisionOption(
                name="Clarify the decision boundary",
                action="Collect the smallest missing facts that could change the decision, especially ownership, explicit commitments, and constraints.",
                benefits=["Reduces avoidable escalation", "Separates explicit expectations from inferred ones"],
                downsides=["Costs a small amount of time before action"],
                prerequisites=[unknowns[0].statement] if unknowns else [],
                reversibility=Reversibility.HIGH,
                evidence_refs=option_refs,
            ),
            DecisionOption(
                name="Align directly with the decision owner",
                action="Have a bounded conversation that states observed facts, names the unresolved tension, and asks for one explicit decision or trade-off.",
                benefits=["Creates shared context", "Makes decision ownership visible"],
                downsides=["May expose disagreement that was previously implicit"],
                prerequisites=["Identify who owns the decision"],
                reversibility=Reversibility.HIGH,
                evidence_refs=option_refs,
            ),
            DecisionOption(
                name="Document the operating decision",
                action="After alignment, record the decision, owner, trade-off, and next checkpoint in neutral language.",
                benefits=["Reduces future ambiguity", "Creates a reusable mechanism instead of relying on memory"],
                downsides=["Can feel formal if used too early"],
                prerequisites=["A decision or agreed next step exists"],
                reversibility=Reversibility.MEDIUM,
                evidence_refs=option_refs,
            ),
        ]

        confidence = Confidence.LOW if len(unknowns) >= 4 else Confidence.MEDIUM
        first_unknown = unknowns[0].statement if unknowns else "Confirm the decision owner and desired outcome."
        recommendation = Recommendation(
            action="Clarify the highest-leverage unknown, then align directly on one explicit decision.",
            rationale="The narrative contains enough ambiguity that an irreversible or accusatory move would outrun the available evidence.",
            first_step=first_unknown,
            evidence_refs=option_refs,
        )

        cautions = ["Offline heuristic mode provides a conservative structure, not deep contextual reasoning. Use an AI provider or human peer for richer analysis."]
        if _HIGH_STAKES.search(situation.narrative):
            cautions.append("This may involve HR, legal, safety, or serious conduct concerns. Use qualified human support and applicable company processes rather than relying on ALINA alone.")
        if _HARMFUL.search(situation.narrative):
            cautions.append("ALINA will not recommend retaliation, punishment, covert manipulation, or fabricated evidence.")

        facts_text = [x.statement for x in facts[:3]]
        questions = [x.statement for x in unknowns[:3]]
        return SituationAnalysis(
            summary=_clip(" ".join(sents[:3]) or situation.narrative, 420),
            facts=facts, assumptions=assumptions, unknowns=unknowns, tensions=tensions,
            stakeholders=stakeholders, alternative_hypotheses=alt,
            risks_of_action=[Risk(description="Acting on an unverified interpretation could create unnecessary conflict or lock in the wrong remedy.", severity=Importance.HIGH, evidence_refs=[x.id for x in assumptions[:2]] + [x.id for x in unknowns[:1]])],
            risks_of_inaction=[Risk(description="Leaving ownership or the decision unresolved may allow the same issue to recur and keep intervention load on the manager.", severity=Importance.MEDIUM, evidence_refs=[x.id for x in facts[:2]])],
            options=options, recommendation=recommendation,
            conversation_framing=ConversationFraming(
                objective="Reach one explicit, evidence-based decision without presenting hypotheses as accusations.",
                opening="I want to separate what we know from what we are assuming and align on the next decision.",
                facts_to_state=facts_text,
                questions_to_ask=questions,
                clear_ask="Can we agree on the owner, the trade-off we are making, and the next checkpoint?",
                avoid=["Attributing hidden motives as fact", "Bundling several grievances into one conversation", "Escalating before clarifying the decision boundary"],
            ),
            signals_to_watch=[
                SignalToWatch(signal="The decision owner gives an explicit answer", meaning="Reduces ambiguity and allows options to be compared against a real constraint."),
                SignalToWatch(signal="The same issue recurs after an explicit decision", meaning="Suggests a mechanism or execution problem rather than a one-off context gap."),
            ],
            confidence=confidence,
            confidence_reason=f"Offline mode found {len(unknowns)} material unknown(s) and {len(assumptions)} explicit assumption marker(s).",
            cautions=cautions, provider=self.name, model=None,
        )

    def _unknowns(self, situation: SituationInput) -> list[str]:
        hay = situation.narrative.lower()
        out: list[str] = []
        if not situation.goal:
            out.append("What specific decision or outcome do you need from this situation now?")
        if any(k in hay for k in ("manager", "leadership", "expect")):
            out.append("What has leadership explicitly said, versus what is currently being inferred from behavior?")
        if any(k in hay for k in ("date", "deadline", "commit", "scope")):
            out.append("Which constraint is actually fixed: date, scope, capacity, or quality bar?")
        if any(k in hay for k in ("team", "failed", "missed", "again", "rework")):
            out.append("Is this a one-off execution miss or a recurring failure mode with the same underlying mechanism?")
        if any(k in hay for k in ("owner", "responsib", "dependency", "another team")):
            out.append("Who has the decision right and who has execution ownership for the disputed item?")
        if any(k in hay for k in ("trust", "intent", "trying", "politic", "against me")) or _ASSUMPTION_MARKERS.search(situation.narrative):
            out.append("What observable evidence would support or weaken the current interpretation of stakeholder intent?")
        if any(k in hay for k in ("late", "hours", "night", "overload", "too much")):
            out.append("Which repeated work is pulling the manager into after-hours intervention, and who would own a durable mechanism instead?")
        if not out:
            out.extend([
                "What information could materially change the preferred next move?",
                "Who owns the decision that is currently blocked or ambiguous?",
            ])
        return list(OrderedDict.fromkeys(out))[:6]

    def _alternatives(self, situation: SituationInput, assumptions: list[EvidenceItem]) -> list[AlternativeHypothesis]:
        refs = [x.id for x in assumptions[:2]]
        out = [AlternativeHypothesis(
            hypothesis="The behavior may be driven by missing context, incentives, or constraints rather than the intent currently attributed to the stakeholder.",
            supporting_signals=["The stakeholder gives a concrete constraint or prior commitment when asked directly."],
            weakening_signals=["The same behavior persists after context, ownership, and constraints are made explicit."],
            evidence_refs=refs,
        )]
        if situation.mode.value == "reality_check":
            out.append(AlternativeHypothesis(
                hypothesis="Your current interpretation may be directionally right, but the evidence may not yet support the certainty or the strongest version of it.",
                supporting_signals=["Multiple independent observations point to the same pattern."],
                weakening_signals=["A direct clarification produces a plausible explanation that fits the observed facts."],
                evidence_refs=refs,
            ))
        return out
