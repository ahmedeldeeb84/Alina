from pathlib import Path
from alina.models import SituationInput
from alina.providers.heuristic import HeuristicProvider
from alina.storage import SituationRepository
from alina.patterns import build_pattern_report
from alina.validator import validate_analysis


def _save(repo, text, title):
    s=SituationInput(title=title,narrative=text)
    a=validate_analysis(HeuristicProvider().analyze(s),s)
    return repo.save(s,a)


def test_storage_round_trip(tmp_path: Path):
    repo=SituationRepository(tmp_path/"a.db")
    sid=_save(repo,"My team missed another dependency and I stayed late to fix it. This happened again this month.","handoff")
    item=repo.get(sid)
    assert item and item.input.title=="handoff" and item.analysis.provider=="heuristic"


def test_pattern_report_finds_recurrence(tmp_path: Path):
    repo=SituationRepository(tmp_path/"a.db")
    _save(repo,"My team missed another deadline and I stayed late to fix it. The owner is unclear.","one")
    _save(repo,"Another team missed the handoff again and I stayed late. Ownership is unclear.","two")
    _save(repo,"We missed again and I had to coordinate after hours because responsibility was unclear.","three")
    report=build_pattern_report(repo.list(limit=20),window_days=30)
    assert report.total_situations==3
    assert any(x.label in {"execution reliability","ownership","capacity"} for x in report.recurring_tensions)
