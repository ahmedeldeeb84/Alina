from alina.models import PriorSituationContext, SituationInput
from alina.prompts import user_prompt


def test_history_context_is_included_without_becoming_current_evidence():
    situation = SituationInput(
        narrative="The PM changed scope again after engineering had already committed to the delivery plan.",
        history_context=[
            PriorSituationContext(
                created_at="2026-09-01T09:00:00Z",
                title="Earlier scope change",
                summary="A late scope change created delivery pressure.",
                tensions=["scope vs date", "stakeholder alignment"],
                stakeholders=["PM", "engineering lead"],
                recommendation="Clarify which constraint is fixed.",
                outcome="Scope was reduced after alignment.",
            )
        ],
    )
    prompt = user_prompt(situation)
    assert "RECENT STRUCTURED HISTORY" in prompt
    assert "Earlier scope change" in prompt
    assert "Scope was reduced after alignment." in prompt
    assert "Do not use prior-history statements as current facts" in prompt


def test_history_context_is_bounded():
    items = [
        PriorSituationContext(summary=f"Situation {i}")
        for i in range(8)
    ]
    situation = SituationInput(
        narrative="This is a sufficiently long current situation narrative for validation.",
        history_context=items,
    )
    assert len(situation.history_context) == 8
