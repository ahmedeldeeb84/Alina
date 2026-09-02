import pytest
from alina.models import SituationInput
from alina.providers.heuristic import HeuristicProvider
from alina.validator import AnalysisValidationError, validate_analysis


def test_rejects_unknown_evidence_reference():
    s=SituationInput(narrative="A team missed a delivery. The deadline was Friday. I need to decide whether to change the scope.")
    a=HeuristicProvider().analyze(s)
    a.recommendation.evidence_refs.append("F999")
    with pytest.raises(AnalysisValidationError): validate_analysis(a,s)


def test_caps_confidence_with_many_unknowns():
    s=SituationInput(narrative="My manager expects a fixed date and my team failed again. I think another team is intentionally blocking us and I stay late to fix it.")
    a=HeuristicProvider().analyze(s); a.confidence="high"
    a=validate_analysis(a,s)
    assert a.confidence.value!="high"
