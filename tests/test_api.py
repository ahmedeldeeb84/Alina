import os
from fastapi.testclient import TestClient
from alina.api.app import create_app


def test_api_health(tmp_path, monkeypatch):
    monkeypatch.setenv("ALINA_DB",str(tmp_path/"api.db"))
    c=TestClient(create_app())
    assert c.get("/health").json()["status"]=="ok"


def test_api_analyze(tmp_path, monkeypatch):
    monkeypatch.setenv("ALINA_DB",str(tmp_path/"api.db"))
    c=TestClient(create_app())
    payload={"narrative":"The PM committed to Friday. I think the team needs another week. The manager has not explicitly confirmed which constraint is fixed."}
    r=c.post("/v1/analyze?provider=heuristic&save=false",json=payload)
    assert r.status_code==200, r.text
    data=r.json(); assert data["provider"]=="heuristic" and data["unknowns"]
