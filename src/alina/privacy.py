from __future__ import annotations

import re
from pathlib import Path

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_TICKET = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d{1,8}\b")
_UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)


def redact_text(text: str, names: list[str] | None = None) -> str:
    redacted = _EMAIL.sub("[EMAIL]", text)
    redacted = _TICKET.sub("[TICKET]", redacted)
    redacted = _UUID.sub("[ID]", redacted)
    for idx, name in enumerate(names or [], start=1):
        name = name.strip()
        if name:
            redacted = re.sub(re.escape(name), f"[NAME_{idx}]", redacted, flags=re.I)
    return redacted


def secure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
