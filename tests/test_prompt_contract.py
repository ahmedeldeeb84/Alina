from alina.prompts import SYSTEM_PROMPT

def test_prompt_contains_core_epistemic_rules():
    low=SYSTEM_PROMPT.lower()
    for phrase in ["never claim to know", "alternative hypotheses", "retaliation", "confidence"]:
        assert phrase in low
