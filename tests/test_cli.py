from typer.testing import CliRunner
from alina.cli import app

runner=CliRunner()

def test_cli_analysis_smoke():
    r=runner.invoke(app,["analyze","--text","The PM committed to Friday. I think the full scope may be impossible. Engineering asked for another week.","--provider","heuristic","--no-save","--json"])
    assert r.exit_code==0, r.stdout
    assert '"provider":"heuristic"' in r.stdout.replace(" ","")


def test_cli_reality_check_smoke():
    r=runner.invoke(app,["reality-check","--text","A peer excluded me from two meetings. I think she is deliberately trying to take my scope away. She did not say that.","--provider","heuristic","--no-save"])
    assert r.exit_code==0, r.stdout
    assert "Alternative hypotheses" in r.stdout
