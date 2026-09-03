from __future__ import annotations

import os
from pathlib import Path

from alina.models import PatternReport, SituationAnalysis, SituationInput, StoredSituation
from alina.patterns import build_pattern_report
from alina.service import analyze_situation
from alina.storage import SituationRepository


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:
        raise RuntimeError("Install API dependencies with: pip install 'alina-leadership[api]'") from exc

    app = FastAPI(
        title="ALINA",
        version="0.1.0",
        description="Actionable Leadership Intelligence for Navigation & Alignment",
    )
    db = os.getenv("ALINA_DB")

    # The frontend ships with the Python package so a single `alina serve`
    # process exposes both the workbench and the API. This keeps deployment
    # intentionally simple and avoids a separate Node build/runtime.
    web_dir = Path(__file__).resolve().parent.parent / "web"
    if web_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(web_dir)), name="assets")

        @app.get("/", include_in_schema=False)
        def web_workbench():
            return FileResponse(web_dir / "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.post("/v1/analyze", response_model=SituationAnalysis)
    def analyze(payload: SituationInput, provider: str = "auto", model: str | None = None, save: bool = True):
        try:
            analysis, _ = analyze_situation(payload, provider=provider, model=model, save=save, db=db)
            return analysis
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/v1/situations", response_model=list[StoredSituation])
    def situations(limit: int = Query(50, ge=1, le=200)):
        return SituationRepository(db).list(limit=limit)

    @app.get("/v1/situations/{sid}", response_model=StoredSituation)
    def get_situation(sid: str):
        item = SituationRepository(db).get(sid)
        if item is None:
            raise HTTPException(status_code=404, detail="Situation not found")
        return item

    @app.get("/v1/patterns", response_model=PatternReport)
    def patterns(days: int = Query(30, ge=1, le=3650)):
        repo = SituationRepository(db)
        return build_pattern_report(repo.list(limit=500, days=days), window_days=days)

    return app
