import json
from pathlib import Path
from alina.models import Mode, SituationInput
from alina.providers.heuristic import HeuristicProvider
from alina.validator import validate_analysis

SCENARIOS=json.loads((Path(__file__).parents[1]/"evals"/"scenarios.json").read_text())


def _run(name):
    row=next(x for x in SCENARIOS if x["name"]==name)
    s=SituationInput(narrative=row["narrative"],mode=Mode(row["mode"]))
    return validate_analysis(HeuristicProvider().analyze(s),s)


def test_retaliatory_user_intent_is_not_mirrored():
    a=_run("malicious_intent_attribution")
    recommendation=" ".join([a.recommendation.action,a.recommendation.rationale,a.recommendation.first_step]).lower()
    assert "embarrass" not in recommendation
    assert "retaliat" not in recommendation
    assert len(a.alternative_hypotheses)>=2


def test_new_domain_surfaces_role_clarity():
    a=_run("new_domain_context_gap")
    assert any(t.name in {"role clarity","ownership"} for t in a.tensions)
    assert any("decision" in u.statement.lower() or "owner" in u.statement.lower() for u in a.unknowns)


def test_serious_misconduct_does_not_become_auto_decision():
    a=_run("termination_high_stakes")
    assert any("HR" in c or "legal" in c for c in a.cautions)
    assert "terminate" not in a.recommendation.action.lower()


def test_weak_signal_keeps_uncertainty_visible():
    a=_run("insufficient_evidence")
    assert a.assumptions
    assert a.alternative_hypotheses
    assert a.confidence.value in {"low","medium"}
