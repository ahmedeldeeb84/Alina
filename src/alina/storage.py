from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

from alina.models import SituationAnalysis, SituationInput, StoredSituation
from alina.privacy import secure_parent


def default_db_path() -> Path:
    env = os.getenv("ALINA_DB")
    return Path(env).expanduser() if env else Path.home() / ".alina" / "alina.db"


class SituationRepository:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path else default_db_path()
        secure_parent(self.path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS situations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    title TEXT,
                    input_json TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT,
                    analysis_json TEXT NOT NULL
                )
            """)
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def save(self, situation: SituationInput, analysis: SituationAnalysis) -> str:
        sid = str(uuid.uuid4())
        created = datetime.now(timezone.utc).isoformat()
        with self._connect() as con:
            con.execute(
                "INSERT INTO situations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (sid, created, situation.title, situation.model_dump_json(), situation.mode.value, json.dumps(situation.tags), analysis.provider, analysis.model, analysis.model_dump_json()),
            )
        return sid

    def get(self, sid: str) -> StoredSituation | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM situations WHERE id=?", (sid,)).fetchone()
        return self._row(row) if row else None

    def list(self, limit: int = 50, days: int | None = None) -> list[StoredSituation]:
        sql = "SELECT * FROM situations"
        params: list[object] = []
        if days is not None:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            sql += " WHERE created_at >= ?"
            params.append(cutoff)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as con:
            rows = con.execute(sql, params).fetchall()
        return [self._row(r) for r in rows]

    def _row(self, row: sqlite3.Row) -> StoredSituation:
        return StoredSituation(
            id=row["id"],
            created_at=row["created_at"],
            input=SituationInput.model_validate_json(row["input_json"]),
            analysis=SituationAnalysis.model_validate_json(row["analysis_json"]),
        )
