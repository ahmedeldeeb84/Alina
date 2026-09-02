from alina.models import Mode, SituationInput
from alina.providers.heuristic import HeuristicProvider
from alina.validator import validate_analysis


def test_separates_explicit_assumption():
    s=SituationInput(narrative="The PM committed to Friday. I think my manager wants me to keep the full scope. Engineering said the full scope needs another week.")
    a=validate_analysis(HeuristicProvider().analyze(s),s)
    assert any("I think" in x.statement for x in a.assumptions)
    assert all(x.kind=="stated_fact" for x in a.facts)
    assert a.recommendation.first_step


def test_reality_check_has_competing_hypotheses():
    s=SituationInput(narrative="A peer excluded me from two meetings. I think she is deliberately trying to take ownership away from me. She did not say that.",mode=Mode.REALITY_CHECK)
    a=validate_analysis(HeuristicProvider().analyze(s),s)
    assert len(a.alternative_hypotheses)>=2
    assert a.confidence.value in {"low","medium"}


def test_high_stakes_caution():
    s=SituationInput(narrative="I am considering whether to terminate an employee after a serious misconduct allegation, but the facts are still disputed.")
    a=validate_analysis(HeuristicProvider().analyze(s),s)
    assert any("HR" in x and "legal" in x for x in a.cautions)
