from __future__ import annotations

import json
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from alina.models import Mode, SituationInput
from alina.patterns import build_pattern_report
from alina.privacy import redact_text
from alina.render import render_analysis, render_patterns
from alina.service import analyze_situation
from alina.storage import SituationRepository

app = typer.Typer(help="ALINA — management situation navigation and alignment.", no_args_is_help=True)
console=Console()


def _read_input(file: Path | None, text: str | None) -> str:
    if file and text:
        raise typer.BadParameter("Use either FILE or --text, not both.")
    if file:
        return file.read_text(encoding="utf-8")
    if text:
        return text
    if not typer.get_text_stream("stdin").isatty():
        return typer.get_text_stream("stdin").read()
    return typer.prompt("Describe the situation")


@app.command()
def analyze(
    file: Path | None = typer.Argument(None, exists=True, readable=True),
    text: str | None = typer.Option(None, "--text", "-t"),
    title: str | None = typer.Option(None),
    goal: str | None = typer.Option(None),
    stakeholder: list[str] | None = typer.Option(None, "--stakeholder"),
    tag: list[str] | None = typer.Option(None, "--tag"),
    mode: Mode = typer.Option(Mode.NAVIGATION),
    provider: str = typer.Option("auto", help="auto, heuristic, or openai"),
    model: str | None = typer.Option(None),
    no_save: bool = typer.Option(False, "--no-save"),
    json_output: bool = typer.Option(False, "--json"),
    db: Path | None = typer.Option(None),
) -> None:
    """Analyze one management situation."""
    narrative=_read_input(file,text).strip()
    situation=SituationInput(title=title,narrative=narrative,goal=goal,stakeholders=stakeholder or [],tags=tag or [],mode=mode)
    analysis,sid=analyze_situation(situation,provider=provider,model=model,save=not no_save,db=db)
    if json_output:
        console.print_json(analysis.model_dump_json())
    else:
        render_analysis(analysis,console)
        if sid: console.print(f"\n[dim]Saved locally as {sid}[/dim]")


@app.command()
def navigate(provider: str = typer.Option("auto"), model: str | None = typer.Option(None), db: Path | None = typer.Option(None)) -> None:
    """Interactive shortcut for navigation mode."""
    text=typer.prompt("Describe the management situation")
    goal=typer.prompt("What outcome do you need? (optional)", default="", show_default=False)
    situation=SituationInput(narrative=text,goal=goal or None,mode=Mode.NAVIGATION)
    analysis,sid=analyze_situation(situation,provider=provider,model=model,save=True,db=db)
    render_analysis(analysis,console); console.print(f"\n[dim]Saved locally as {sid}[/dim]")


@app.command("reality-check")
def reality_check(file: Path | None = typer.Argument(None, exists=True, readable=True), text: str | None = typer.Option(None,"--text","-t"), provider: str = typer.Option("auto"), model: str | None = typer.Option(None), no_save: bool = typer.Option(False,"--no-save"), db: Path | None = typer.Option(None)) -> None:
    """Pressure-test your current interpretation before acting."""
    situation=SituationInput(narrative=_read_input(file,text).strip(),mode=Mode.REALITY_CHECK)
    analysis,sid=analyze_situation(situation,provider=provider,model=model,save=not no_save,db=db)
    render_analysis(analysis,console)
    if sid: console.print(f"\n[dim]Saved locally as {sid}[/dim]")


@app.command()
def history(limit: int = typer.Option(20,min=1,max=200), db: Path | None = typer.Option(None)) -> None:
    repo=SituationRepository(db); rows=repo.list(limit=limit)
    table=Table(title="ALINA · Local history"); table.add_column("ID"); table.add_column("Created"); table.add_column("Title / summary"); table.add_column("Confidence")
    for x in rows: table.add_row(x.id[:8],x.created_at[:19],x.input.title or x.analysis.summary[:65],x.analysis.confidence.value)
    console.print(table)


@app.command()
def show(situation_id: str, db: Path | None = typer.Option(None)) -> None:
    repo=SituationRepository(db); rows=repo.list(limit=500)
    matches=[x for x in rows if x.id==situation_id or x.id.startswith(situation_id)]
    if len(matches)!=1: raise typer.BadParameter("Situation ID is missing or ambiguous.")
    render_analysis(matches[0].analysis,console)


@app.command()
def patterns(days: int = typer.Option(30,min=1), db: Path | None = typer.Option(None)) -> None:
    repo=SituationRepository(db); report=build_pattern_report(repo.list(limit=500,days=days),window_days=days); render_patterns(report,console)


@app.command()
def redact(file: Path | None = typer.Argument(None, exists=True, readable=True), text: str | None = typer.Option(None,"--text","-t"), name: list[str] | None = typer.Option(None,"--name")) -> None:
    """Best-effort redaction helper before sending context to a cloud model."""
    console.print(redact_text(_read_input(file,text), names=name or []))


@app.command()
def serve(host: str = typer.Option("127.0.0.1"), port: int = typer.Option(8787,min=1,max=65535)) -> None:
    """Run the optional local HTTP API."""
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter("API dependencies missing. Install: pip install 'alina-leadership[api]'") from exc
    uvicorn.run("alina.api.app:create_app", factory=True, host=host, port=port)
