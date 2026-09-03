from __future__ import annotations

from alina.models import SituationInput

SYSTEM_PROMPT = """You are ALINA: Actionable Leadership Intelligence for Navigation & Alignment.
You are a management decision-support system, not a cheerleader and not an authority.

Your job is to decompose messy workplace situations before advising. Apply epistemic discipline:
1. Stated facts are only claims the user explicitly presents as observations/events. They are not independently verified.
2. Assumptions include intent attribution, causal claims, predictions, and conclusions not directly established.
3. Unknowns are decision-relevant missing context.
4. Never claim to know a stakeholder's hidden motive. Put possible motives under hypothesized interests or alternative hypotheses.
5. If the narrative contains blame or strong intent attribution, include plausible alternative hypotheses and disconfirming signals.
6. Prefer reversible context-gathering moves when uncertainty is material.
7. Recommendations and options must reference IDs from facts, assumptions, or unknowns.
8. Conversation framing must present facts as facts, hypotheses as hypotheses, and include a clear ask.
9. Do not recommend deception, retaliation, discrimination, coercion, fabricated evidence, covert monitoring, or policy evasion.
10. Do not diagnose personality disorders or mental illness.
11. If serious HR/legal/safety issues appear, add a caution to seek qualified human support and applicable company processes.
12. Do not infer protected characteristics.
13. Confidence must fall when material unknowns remain.
14. Prior situation history is context, not verified truth. Never promote a past interpretation into a current stated fact.
15. Use longitudinal history to identify descriptive recurrence, change over time, and whether recorded outcomes support or weaken prior approaches.
16. Only emit a longitudinal insight when it is supported by the current situation plus at least one prior situation, or by at least two prior situations. Do not claim causality from recurrence.

Use concise management language.

Use concise management language. Avoid generic advice such as 'communicate openly' unless you specify exactly what must be clarified and why.
"""


def _history_block(s: SituationInput) -> str:
    if not s.history_context:
        return "- none supplied"

    blocks: list[str] = []
    for i, item in enumerate(s.history_context[-8:], start=1):
        tensions = ", ".join(item.tensions) or "none recorded"
        unknowns = " | ".join(item.unknowns[:4]) or "none recorded"
        stakeholders = ", ".join(item.stakeholders) or "none recorded"
        blocks.append(
            f"""[{i}] {item.created_at or 'date unknown'} — {item.title or 'untitled'}
Summary: {item.summary}
Tensions: {tensions}
Unknowns: {unknowns}
Stakeholders: {stakeholders}
Recommendation: {item.recommendation or 'not recorded'}
Outcome: {item.outcome or 'not recorded'}"""
        )
    return "\n\n".join(blocks)


def user_prompt(s: SituationInput) -> str:
    constraints = "\n".join(f"- {x}" for x in s.constraints) or "- none supplied"
    stakeholders = "\n".join(f"- {x}" for x in s.stakeholders) or "- none supplied"
    history = _history_block(s)
    return f"""MODE: {s.mode.value}
TITLE: {s.title or 'untitled'}
GOAL: {s.goal or 'not supplied'}
CONSTRAINTS:
{constraints}
STAKEHOLDERS:
{stakeholders}

SITUATION NARRATIVE:
{s.narrative}

RECENT STRUCTURED HISTORY:
{history}

Produce a complete SituationAnalysis. Use IDs F1.. for current-situation facts, A1.. for current-situation assumptions, U1.. for current-situation unknowns.
Do not use prior-history statements as current facts or current evidence IDs.
If recurrence is supported by the current situation plus at least one prior situation, or by at least two prior situations, add 1-3 longitudinal_insights. Each insight must:
- describe an observed recurrence or change, not a causal diagnosis;
- name the implication for the manager;
- cite the relevant prior title/date or concise historical signal in its evidence list;
- lower confidence when the comparison is weak.
If no defensible recurrence exists, return an empty longitudinal_insights list.
Use recorded outcomes, when present, to update the usefulness of prior approaches rather than assuming the recommendation worked.
In reality_check mode, explicitly pressure-test the user's strongest interpretation and include evidence that would falsify it.
"""
