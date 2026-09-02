from __future__ import annotations

import os
from pathlib import Path
from alina.models import PatternReport, SituationAnalysis, SituationInput
from alina.patterns import build_pattern_report
from alina.providers.heuristic import HeuristicProvider
from alina.storage import SituationRepository
from alina.validator import validate_analysis


def get_provider(name: str = "auto", model: str | None = None):
    name = name.lower().strip()
    if name == "auto":
        name = "openai" if os.getenv("OPENAI_API_KEY") else "heuristic"
    if name == "heuristic":
        return HeuristicProvider()
    if name == "openai":
        from alina.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=model)
    raise ValueError(f"Unknown provider: {name}")


def analyze_situation(situation: SituationInput, provider: str = "auto", model: str | None = None, save: bool = True, db: str | Path | None = None) -> tuple[SituationAnalysis, str | None]:
    impl = get_provider(provider, model=model)
    analysis = validate_analysis(impl.analyze(situation), situation)
    sid = SituationRepository(db).save(situation, analysis) if save else None
    return analysis, sid


def pattern_report(db: str | Path | None = None, days: int | None = 30, limit: int = 500) -> PatternReport:
    repo=SituationRepository(db)
    return build_pattern_report(repo.list(limit=limit, days=days), window_days=days)
