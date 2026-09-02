from __future__ import annotations

from typing import Protocol
from alina.models import SituationAnalysis, SituationInput


class AnalysisProvider(Protocol):
    name: str
    model_name: str | None

    def analyze(self, situation: SituationInput) -> SituationAnalysis:
        ...
