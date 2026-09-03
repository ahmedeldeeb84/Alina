# ALINA web frontend patch

This patch adds a zero-build, responsive web workbench that is served by the existing FastAPI process.

## Files added
- `src/alina/web/index.html`
- `src/alina/web/styles.css`
- `src/alina/web/app.js`
- `src/alina/web/manifest.webmanifest`
- `src/alina/web/icon.svg`

## Files replaced
- `src/alina/api/app.py` — serves `/` and `/assets/*` while keeping all existing API routes.
- `pyproject.toml` — packages web assets inside the Python distribution.
- `tests/test_api.py` — adds smoke tests for the workbench and static assets.

## Behavior
- Responsive landing page and analysis workbench.
- Navigation and Reality Check modes.
- Calls the existing `/v1/analyze` endpoint with `provider=auto&save=false`.
- Renders facts, assumptions, unknowns, tensions, recommendation, options, alternative hypotheses, stakeholder lenses, conversation framing, signals, risks, and cautions.
- PWA manifest and icon included so the deployed web app can be added to a phone home screen.
- No Node/npm build step. `alina serve` is still the only server process required.

## Run
```bash
pip install -e '.[api]'
alina serve
```
Then open `http://localhost:8787/`.
