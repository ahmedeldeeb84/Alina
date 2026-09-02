from __future__ import annotations

import re
from collections import Counter, defaultdict
from alina.models import PatternFinding, PatternReport, StoredSituation

_UNKNOWN_CATEGORIES = [
    ("decision ownership", ("owner", "decision right", "responsib")),
    ("explicit expectations", ("explicit", "leadership", "expect")),
    ("scope/date trade-off", ("scope", "date", "deadline", "constraint")),
    ("recurrence/root cause", ("recurr", "one-off", "failure mode", "mechanism")),
    ("stakeholder intent evidence", ("intent", "evidence", "interpretation")),
    ("manager intervention load", ("after-hours", "late", "intervention", "durable mechanism")),
]


def _cat_unknown(text: str) -> str:
    low = text.lower()
    for label, keys in _UNKNOWN_CATEGORIES:
        if any(k in low for k in keys):
            return label
    return "other context gap"


def _findings(counter: Counter[str], examples: dict[str, list[str]], total: int, min_count: int = 2) -> list[PatternFinding]:
    out=[]
    for label, count in counter.most_common():
        if count < min_count:
            continue
        out.append(PatternFinding(label=label, count=count, share=(count/total if total else 0), examples=examples[label][:3]))
    return out


def build_pattern_report(items: list[StoredSituation], window_days: int | None = None) -> PatternReport:
    total=len(items)
    tensions=Counter(); tension_examples=defaultdict(list)
    unknowns=Counter(); unknown_examples=defaultdict(list)
    stakeholders=Counter(); stakeholder_examples=defaultdict(list)
    confidence=Counter()
    for item in items:
        a=item.analysis
        confidence[a.confidence.value]+=1
        for t in {x.name.lower() for x in a.tensions}:
            tensions[t]+=1; tension_examples[t].append(item.input.title or item.id[:8])
        unknown_categories = {_cat_unknown(u.statement) for u in a.unknowns}
        for cat in unknown_categories:
            unknowns[cat] += 1
            unknown_examples[cat].append(item.input.title or item.id[:8])
        for s in {x.stakeholder.strip().lower() for x in a.stakeholders if x.stakeholder.strip()}:
            stakeholders[s]+=1; stakeholder_examples[s].append(item.input.title or item.id[:8])
    notes=[]
    if total < 3:
        notes.append("Pattern confidence is limited with fewer than three saved situations.")
    notes.append("Recurrence is descriptive, not proof of causality. Review the underlying situations before changing an operating mechanism.")
    return PatternReport(
        total_situations=total, window_days=window_days,
        recurring_tensions=_findings(tensions,tension_examples,total),
        recurring_unknowns=_findings(unknowns,unknown_examples,total),
        recurring_stakeholders=_findings(stakeholders,stakeholder_examples,total),
        confidence_distribution=dict(confidence), notes=notes,
    )
