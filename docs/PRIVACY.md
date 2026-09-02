# Privacy model

ALINA is local-first because workplace narratives can be sensitive.

- SQLite history stays on the user's machine.
- Heuristic mode performs no network calls.
- Cloud providers are opt-in and receive submitted narrative/context.
- API keys are never written to the database.
- `--no-save` disables local history.
- `alina redact` is a best-effort helper, not formal anonymization.
- Public examples and tests use synthetic scenarios only.

Users remain responsible for their employer's policies, confidentiality duties, and provider configuration.
