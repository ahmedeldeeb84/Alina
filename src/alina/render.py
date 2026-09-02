from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from alina.models import PatternReport, SituationAnalysis


def render_analysis(a: SituationAnalysis, console: Console | None = None) -> None:
    c=console or Console()
    c.print(Panel(a.summary, title="ALINA · Situation Map", subtitle=f"{a.provider}{' / '+a.model if a.model else ''} · confidence: {a.confidence.value}"))
    _evidence(c, "Stated facts", a.facts)
    _evidence(c, "Assumptions / interpretations", a.assumptions)
    _evidence(c, "Unknowns that could change the decision", a.unknowns)

    if a.tensions:
        t=Table(title="Core tensions", show_lines=False); t.add_column("Tension", style="bold"); t.add_column("Why it matters")
        for x in a.tensions: t.add_row(x.name, x.description)
        c.print(t)
    if a.alternative_hypotheses:
        c.print("[bold]Alternative hypotheses[/bold]")
        for x in a.alternative_hypotheses: c.print(f" • {x.hypothesis}")

    opt=Table(title="Options", show_lines=True); opt.add_column("Option", style="bold"); opt.add_column("Action"); opt.add_column("Reversibility")
    for x in a.options: opt.add_row(x.name, x.action, x.reversibility.value)
    c.print(opt)

    c.print(Panel(f"[bold]Action[/bold]  {a.recommendation.action}\n\n[bold]Why[/bold]  {a.recommendation.rationale}\n\n[bold]First step[/bold]  {a.recommendation.first_step}", title="Recommended next move"))
    f=a.conversation_framing
    c.print(Panel(f"[bold]Opening[/bold]  {f.opening}\n\n[bold]Clear ask[/bold]  {f.clear_ask}\n\n[bold]Questions[/bold]\n" + "\n".join(f" • {q}" for q in f.questions_to_ask), title="Stakeholder framing"))
    if a.cautions:
        c.print("[bold yellow]Cautions[/bold yellow]")
        for x in a.cautions: c.print(f" • {x}")


def _evidence(c: Console, title: str, items) -> None:
    if not items: return
    c.print(f"[bold]{title}[/bold]")
    for x in items: c.print(f" [dim]{x.id}[/dim]  {x.statement}")


def render_patterns(p: PatternReport, console: Console | None = None) -> None:
    c=console or Console(); c.print(Panel(f"{p.total_situations} situation(s) analyzed", title="ALINA · Pattern Report"))
    for title, items in (("Recurring tensions",p.recurring_tensions),("Recurring unknowns",p.recurring_unknowns),("Recurring stakeholders",p.recurring_stakeholders)):
        c.print(f"[bold]{title}[/bold]")
        if not items: c.print(" • No recurrence above threshold yet."); continue
        for x in items: c.print(f" • {x.label}: {x.count}/{p.total_situations} ({x.share:.0%})")
    for n in p.notes: c.print(f"[dim]Note: {n}[/dim]")
