# ALINA

**Actionable Leadership Intelligence for Navigation & Alignment**

> Separate signal from story. Pressure-test your interpretation. Choose a proportionate next move. Notice when the same organizational problem keeps coming back.

ALINA is an open-source, local-first decision-support workbench for managers navigating ambiguous workplace situations. It is designed for SDMs, engineering managers, product managers, TPMs, team leads, founders, and senior ICs operating across people, delivery, ownership, and stakeholder boundaries.

## Why ALINA exists

A manager often receives a situation as one tangled narrative:

- what happened;
- what someone probably meant;
- what is missing;
- what the team can actually do;
- what politics or incentives may matter;
- what needs escalation;
- what can be clarified first.

Generic AI coaching often jumps straight to advice. ALINA **decomposes before advising**.

Its central rule is simple: **an interpretation must not silently become a fact.**

## What v0.1 does

Given a management situation, ALINA produces a structured **Situation Map**:

- stated facts
- assumptions / interpretations
- material unknowns
- core tensions
- stakeholder lenses
- alternative hypotheses
- risks of acting / not acting
- options and trade-offs
- a recommended next move
- stakeholder conversation framing
- signals to watch
- explicit confidence and cautions

It also stores situations locally and can surface recurring patterns across them.

## Quick start

```bash
git clone https://github.com/ahmedeldeeb84/alina.git
cd alina
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

Analyze offline with the conservative built-in provider:

```bash
alina analyze examples/date-commitment.txt --provider heuristic --no-save
```

Pressure-test your interpretation:

```bash
alina reality-check examples/intent-attribution.txt --provider heuristic --no-save
```

### Rich AI analysis with OpenAI

Install the optional provider:

```bash
pip install -e '.[openai]'
export OPENAI_API_KEY='...'
alina analyze examples/date-commitment.txt --provider openai
```

`auto` uses OpenAI when `OPENAI_API_KEY` is present; otherwise it uses the offline provider. The model can be changed with `--model` or `ALINA_OPENAI_MODEL`.

**Privacy note:** cloud providers receive the narrative you submit. ALINA never sends cloud requests in heuristic mode. Use `alina redact` and your organization's policies when handling confidential information.

## Example

Input:

> My PM committed us to a date without speaking to engineering. One engineer says the full scope is impossible. My manager seems to expect me to make the original date anyway. We already slipped twice.

ALINA will explicitly separate a statement such as “the PM committed to a date” from an interpretation such as “my manager expects the original date” unless that expectation was actually stated. It then asks which constraint is fixed, maps the scope/date/ownership tensions, compares moves, and proposes a bounded next step.

## Longitudinal patterns

After saving several situations:

```bash
alina patterns --days 30
```

ALINA can surface descriptive recurrence such as:

> decision ownership appeared in 4/6 situations

or

> manager intervention load appeared as a repeated context gap

This is **not causal diagnosis**. It is a prompt to inspect whether a manager is repeatedly solving an incident that should become an operating mechanism.

## Local HTTP API

```bash
pip install -e '.[api]'
alina serve
```

Then use:

- `GET /health`
- `POST /v1/analyze`
- `GET /v1/situations`
- `GET /v1/situations/{id}`
- `GET /v1/patterns`

The v0.1 server is intended for local use. Do not expose it directly to the internet without authentication and TLS.

## Privacy by default

- history is stored in local SQLite
- no telemetry
- no network in heuristic mode
- API keys are read from environment and never persisted
- `--no-save` disables history
- `alina redact` can remove emails, ticket IDs, UUIDs, and names you specify

Redaction is best-effort, not a guarantee of anonymization.

## Responsible-use boundaries

ALINA is decision support, not an authority. It is not designed to:

- score employees
- infer protected characteristics
- diagnose personalities or mental illness
- recommend retaliation or covert manipulation
- perform legal or HR investigations
- automate hiring, firing, or disciplinary decisions
- monitor employee communications without consent

Serious HR, legal, safety, discrimination, harassment, or conduct matters require qualified human support and applicable organizational processes.

## Product design

The full product and technical design is in [`DESIGN.md`](DESIGN.md), including the analysis contract, privacy model, validation rules, architecture, evaluation plan, and roadmap.

## Development

```bash
pip install -e '.[dev,api]'
pytest
```

## Status

`v0.1.0` is an alpha release: production-engineered as a small open-source tool, but not yet validated by large-scale real-world manager usage. The output should be reviewed with human judgment.

## License

MIT
