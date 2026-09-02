from __future__ import annotations

import re
from alina.models import Confidence, SituationAnalysis, SituationInput

_HARMFUL = re.compile(r"\b(retaliat|revenge|blackmail|fabricat(?:e|ing) evidence|covertly monitor|punish them|humiliate)\w*\b", re.I)
_GENERIC = {"communicate openly", "have a conversation", "talk to them", "communicate better"}


class AnalysisValidationError(ValueError):
    pass


def validate_analysis(analysis: SituationAnalysis, situation: SituationInput) -> SituationAnalysis:
    items = analysis.facts + analysis.assumptions + analysis.unknowns
    ids = [x.id for x in items]
    if len(ids) != len(set(ids)):
        raise AnalysisValidationError("Evidence IDs must be unique.")

    for item in analysis.facts:
        if item.kind != "stated_fact" or not item.id.startswith("F"):
            raise AnalysisValidationError("Facts must use kind=stated_fact and F-prefixed IDs.")
    for item in analysis.assumptions:
        if item.kind != "assumption" or not item.id.startswith("A"):
            raise AnalysisValidationError("Assumptions must use kind=assumption and A-prefixed IDs.")
    for item in analysis.unknowns:
        if item.kind != "unknown" or not item.id.startswith("U"):
            raise AnalysisValidationError("Unknowns must use kind=unknown and U-prefixed IDs.")

    known = set(ids)
    refs = list(analysis.recommendation.evidence_refs)
    for option in analysis.options:
        refs.extend(option.evidence_refs)
    for tension in analysis.tensions:
        refs.extend(tension.evidence_refs)
    for hyp in analysis.alternative_hypotheses:
        refs.extend(hyp.evidence_refs)
    bad = sorted({r for r in refs if r not in known})
    if bad:
        raise AnalysisValidationError(f"Unknown evidence references: {', '.join(bad)}")

    if situation.mode.value == "reality_check" and not analysis.alternative_hypotheses:
        raise AnalysisValidationError("Reality-check mode requires at least one alternative hypothesis.")

    if len(analysis.unknowns) >= 3 and analysis.confidence == Confidence.HIGH:
        analysis.confidence = Confidence.MEDIUM
        analysis.confidence_reason += " Confidence was capped because three or more material unknowns remain."

    recommendation_text = " ".join([analysis.recommendation.action, analysis.recommendation.rationale, analysis.recommendation.first_step])
    if _HARMFUL.search(recommendation_text):
        raise AnalysisValidationError("Recommendation contains a prohibited retaliatory/manipulative pattern.")

    if analysis.recommendation.action.strip().lower() in _GENERIC:
        raise AnalysisValidationError("Recommendation is too generic to be actionable.")

    return analysis
