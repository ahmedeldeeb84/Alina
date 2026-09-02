# ALINA — Product & Technical Design

**Expanded name:** Actionable Leadership Intelligence for Navigation & Alignment  
**Version:** Design baseline for v0.1.0  
**Status:** Approved for implementation  
**Date:** 2026-09-03

## 1. Executive summary

ALINA is a local-first decision-support workbench for managers handling messy workplace situations where facts, assumptions, people dynamics, ownership, delivery pressure, and emotion are mixed together.

The product does **not** try to be a generic leadership coach. Its first job is narrower and testable:

> Turn an ambiguous management narrative into a structured situation map that separates what is known from what is inferred, exposes missing context and competing interpretations, identifies tensions and stakeholder interests, compares options and trade-offs, and proposes a next move that remains visibly grounded in evidence.

A second job begins once multiple situations have been recorded:

> Detect recurring systemic patterns that a manager may be repeatedly treating as unrelated incidents.

Examples include unclear ownership, late scope changes, repeated after-hours rescue work, dependency failures, decision churn, recurring stakeholder misalignment, and repeated personal intervention by the manager.

The core design principle is **epistemic discipline**: ALINA must never silently turn a user's interpretation into a fact.

---

## 2. Problem discovery

### 2.1 Recurring manager pain

The product is built around five recurring classes of management pain:

1. **Sense-making under ambiguity**  
   Managers often know something is wrong but cannot cleanly separate evidence, interpretation, emotion, incentives, and missing context while they are inside the situation.

2. **Over-explanation and defensibility**  
   Managers frequently need to convert an intuition into a concise, defensible frame: facts → evidence → implications → options → recommendation.

3. **Stakeholder trust and organizational politics**  
   Decisions depend on who owns what, who optimizes for what, who needs pre-alignment, what should be documented, and which interpretations remain unverified.

4. **Manager-as-shock-absorber**  
   Broken mechanisms are often repeatedly resolved by the manager personally, creating late work and intervention load without fixing the system that generates the incidents.

5. **Context acquisition**  
   New managers or managers entering a new domain need to distinguish formal ownership from actual decision paths, current problems from historical baggage, and documented process from tribal knowledge.

### 2.2 Why existing AI coaching is not enough

Many current AI leadership products emphasize conversation rehearsal, feedback phrasing, training, or broad coaching. Those are useful but adjacent.

ALINA's wedge is different:

- **decompose before advising**;
- **pressure-test the user's interpretation** rather than reward narrative certainty;
- **make uncertainty visible**;
- **trace recommendations back to evidence and assumptions**;
- **remember situations locally**;
- **detect recurring organizational patterns over time**;
- **avoid employee surveillance or scoring**.

The desired category is closer to a *management reasoning workbench* than an AI coach.

---

## 3. Target users

### Primary

- Software Development Managers
- Engineering Managers
- Product Managers
- Technical Program Managers
- Team Leads
- Startup founders / functional leads

### Secondary

- Senior individual contributors navigating cross-functional influence
- New managers learning to frame ambiguous situations
- Leaders preparing a decision or escalation

### Explicitly not targeted in v0.1

- Automated employee performance scoring
- Hiring or termination decisions
- HR investigations
- Legal advice
- Mental-health diagnosis
- Monitoring employee communications without consent

---

## 4. Jobs to be done

### JTBD-1 — Untangle a situation

> When a work situation feels messy, help me see what I actually know, what I am assuming, what is missing, and what the real tensions are.

### JTBD-2 — Reality-check my interpretation

> When I think I know what another person or team is doing, challenge my reading fairly before I act on it.

### JTBD-3 — Choose a next move

> When multiple actions are possible, help me compare trade-offs and pick a proportionate next step.

### JTBD-4 — Prepare stakeholder framing

> When I need to discuss the situation with someone, help me frame the issue using facts, impact, uncertainty, and a clear ask without unnecessary accusation.

### JTBD-5 — Detect systemic repetition

> When I have been firefighting for weeks, show me which underlying mechanisms are generating the same class of problem repeatedly.

---

## 5. Product principles

### P1. Evidence before interpretation
Every analysis must visibly distinguish:

- stated facts;
- interpretations / assumptions;
- unknowns;
- alternative hypotheses.

### P2. Do not mind-read
Stakeholder motives are hypotheses, not facts. Language such as “likely optimizes for” is acceptable only with explicit uncertainty.

### P3. Challenge, do not merely validate
If the narrative contains blame, intent attribution, or certainty unsupported by evidence, ALINA must surface at least one plausible alternative explanation.

### P4. Smallest proportionate next move
Prefer reversible context-gathering or alignment moves when uncertainty is high. Escalation should be recommended only when evidence and impact justify it.

### P5. Human accountability
ALINA provides decision support. The manager owns the decision.

### P6. Private by default
Situation history is stored locally. No telemetry is enabled by default. Cloud model calls are opt-in and clearly disclosed.

### P7. No employee surveillance
ALINA analyzes situations voluntarily entered by a user. It does not ingest private employee communications, rank employees, or generate hidden risk scores.

### P8. Mechanism over heroics
Longitudinal analysis should ask whether the manager keeps personally resolving a problem that should become an operating mechanism.

---

## 6. v0.1 scope

### 6.1 Core analysis

Input:

- free-form situation narrative;
- optional title;
- optional stated goal;
- optional constraints;
- optional known stakeholders.

Output: `SituationAnalysis`

1. **Situation summary** — neutral, compact restatement.
2. **Stated facts** — claims explicitly presented as events or observations.
3. **Assumptions / interpretations** — conclusions not directly established.
4. **Unknowns** — missing context that could materially change the decision.
5. **Core tensions** — e.g. scope/date, ownership, trust, capacity, incentives, quality/speed.
6. **Stakeholder lenses** — role, stated/likely interests, constraints, uncertainty.
7. **Alternative hypotheses** — plausible readings that challenge premature certainty.
8. **Risks** — of acting and not acting.
9. **Options** — 2–4 moves with benefits, downsides, reversibility, and prerequisites.
10. **Recommended next move** — a bounded action with rationale.
11. **Suggested framing** — fact-based conversation framing with a clear ask.
12. **Signals to watch** — evidence that would confirm or weaken the current reading.
13. **Confidence** — low / medium / high with explanation.

### 6.2 Reality Check mode

A stricter analysis mode that:

- identifies unsupported intent attribution;
- searches for disconfirming evidence;
- distinguishes “possible” from “probable”;
- proposes information that would falsify the user's current interpretation;
- recommends delaying irreversible action when uncertainty is material.

### 6.3 Local history

Each situation can be saved to a local SQLite database with:

- UUID;
- timestamp;
- input narrative;
- provider/model metadata;
- structured analysis;
- user-supplied tags;
- outcome note (optional, later).

### 6.4 Pattern report

The v0.1 pattern engine is deterministic and transparent. It aggregates prior analyses to surface:

- recurring tensions;
- recurring unknown categories;
- repeated stakeholder roles/names;
- repeated option/recommendation themes;
- intervention concentration;
- repeated high-uncertainty decisions.

The pattern engine must label findings as **observed recurrence**, not causal diagnosis.

### 6.5 Interfaces

- Python library
- CLI
- optional FastAPI HTTP service

---

## 7. Non-goals for v0.1

- autonomous action on Slack, email, Jira, or calendars;
- company-wide data ingestion;
- organization dashboards;
- employee scoring;
- sentiment monitoring;
- automatic performance management;
- hidden personality profiling;
- causal claims from small histories;
- multi-user SaaS authentication;
- enterprise compliance certification.

These exclusions are deliberate. They keep the first release useful, privacy-preserving, and testable.

---

## 8. Core domain model

### 8.1 Situation input

```text
SituationInput
├── title: str | None
├── narrative: str
├── goal: str | None
├── constraints: list[str]
├── stakeholders: list[str]
├── tags: list[str]
└── mode: navigation | reality_check
```

### 8.2 Analysis primitives

All material statements use explicit epistemic types.

```text
EvidenceItem
├── id
├── statement
├── kind: stated_fact | assumption | unknown
└── importance: low | medium | high
```

```text
StakeholderLens
├── stakeholder
├── role
├── stated_interests[]
├── hypothesized_interests[]
├── constraints[]
└── uncertainty
```

```text
DecisionOption
├── name
├── action
├── benefits[]
├── downsides[]
├── prerequisites[]
├── reversibility: low | medium | high
└── evidence_refs[]
```

### 8.3 Situation analysis

```text
SituationAnalysis
├── summary
├── facts[]
├── assumptions[]
├── unknowns[]
├── tensions[]
├── stakeholders[]
├── alternative_hypotheses[]
├── risks_of_action[]
├── risks_of_inaction[]
├── options[]
├── recommendation
├── conversation_framing
├── signals_to_watch[]
├── confidence
├── confidence_reason
└── cautions[]
```

---

## 9. Analysis contract

The provider receives a strict instruction contract.

### Required behavior

1. Never convert an interpretation into a fact.
2. Never claim to know a stakeholder's hidden motive.
3. Include material unknowns even if the user did not ask for them.
4. If blame or intent is present, include at least one alternative hypothesis.
5. Prefer actions that gather decision-relevant context when confidence is low.
6. Do not recommend deception, retaliation, discrimination, coercion, or policy evasion.
7. Recommendations must cite evidence/assumption IDs used in the reasoning.
8. Conversation framing must avoid presenting hypotheses as accusations.
9. If the situation is materially HR/legal/safety-sensitive, include a caution to seek appropriate human expertise.

### Validation after model generation

`AnalysisValidator` performs deterministic checks:

- required sections exist;
- evidence IDs are unique;
- recommendation references resolve;
- options reference known evidence IDs only;
- high confidence is deterministically capped when material unknowns exceed configured thresholds;
- reality-check mode requires alternative hypotheses;
- no empty “generic advice” recommendation;
- no secret/key-like data is persisted in provider metadata.

---

## 10. Provider architecture

```text
CLI / API
   │
   ▼
Application Service
   │
   ├── Privacy guard / redaction helpers
   ├── Prompt builder
   ├── AnalysisProvider (interface)
   │      ├── HeuristicProvider (offline, limited)
   │      └── OpenAIProvider (optional extra)
   │
   ├── AnalysisValidator
   ├── SQLite Repository
   └── Pattern Engine
```

### 10.1 Provider interface

```python
class AnalysisProvider(Protocol):
    def analyze(self, situation: SituationInput) -> SituationAnalysis: ...
```

### 10.2 Heuristic provider

Purpose:

- usable offline;
- deterministic demo/testing;
- no external dependency;
- produces a conservative scaffold, not pseudo-intelligent certainty.

It will identify explicit sentences, question marks/uncertainty, common tension vocabulary, and create context-gathering options. It must label itself as limited.

### 10.3 OpenAI provider

Optional dependency: `openai>=3.7,<4`.

Uses structured output with a Pydantic schema so the application receives a typed `SituationAnalysis` rather than parsing prose.

Default model should be configurable via `ALINA_OPENAI_MODEL`. The application must not hardcode secrets or persist API keys.

### 10.4 Future providers

- local model (Ollama / llama.cpp);
- Anthropic;
- enterprise hosted models.

No provider-specific concepts belong in the domain layer.

---

## 11. Privacy and security

Management narratives can contain confidential company and employee information. Therefore:

### Defaults

- local SQLite only;
- no telemetry;
- no network request in heuristic mode;
- API key read from environment only;
- explicit provider shown in every output;
- `--no-save` available;
- local DB path configurable;
- warnings before cloud submission in interactive mode.

### Redaction helper

`alina redact` can replace likely emails, ticket IDs, and user-specified names with stable aliases before analysis.

The redaction helper is convenience, not a guarantee of anonymization.

### Repository hygiene

- `.env` ignored;
- sample environment file contains no credentials;
- dependency pin ranges;
- Dependabot configuration;
- secret-scanning-friendly patterns;
- SECURITY.md with disclosure process.

---

## 12. Safety and responsible use

ALINA is decision support, not an authority.

### Disallowed product behaviors

- infer protected characteristics;
- recommend employment action based on protected characteristics;
- diagnose mental illness or personality disorders;
- generate covert manipulation strategies;
- suggest retaliation;
- fabricate evidence;
- present speculative motives as fact;
- recommend illegal monitoring;
- score employee “loyalty,” “risk,” or similar hidden traits.

### High-stakes caution triggers

When inputs contain terms indicating harassment, discrimination, termination, legal threat, self-harm, physical danger, or serious misconduct, the analysis should state that the situation may require qualified HR/legal/safety support rather than relying on ALINA alone.

---

## 13. Storage model

SQLite schema:

```sql
situations(
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    title TEXT,
    narrative TEXT NOT NULL,
    goal TEXT,
    mode TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT,
    analysis_json TEXT NOT NULL
)
```

v0.1 intentionally stores complete JSON rather than prematurely normalizing every analysis component.

Reasons:

- schema evolution is easier;
- exports are simple;
- pattern extraction can version independently;
- data volume is tiny for personal manager usage.

---

## 14. CLI design

### Analyze

```bash
alina analyze situation.txt --provider openai
alina analyze --text "My PM committed..." --mode reality-check
```

### Interactive

```bash
alina navigate
```

### History

```bash
alina history
alina show <situation-id>
```

### Patterns

```bash
alina patterns --last 30
```

### Redact

```bash
alina redact situation.txt --name "Jane Doe" --name "Project Vega"
```

### API

```bash
alina serve --host 127.0.0.1 --port 8787
```

---

## 15. HTTP API

Optional FastAPI extra.

### Endpoints

- `GET /health`
- `POST /v1/analyze`
- `GET /v1/situations`
- `GET /v1/situations/{id}`
- `GET /v1/patterns`

The service is local-development oriented in v0.1 and must not claim production internet exposure without authentication and TLS termination.

---

## 16. Evaluation strategy

“Does the model sound insightful?” is not sufficient.

### 16.1 Structural evals

Automated tests assert:

- assumptions do not appear in fact list in curated scenarios;
- evidence references resolve;
- reality-check mode returns competing hypotheses;
- high uncertainty reduces confidence;
- recommendation exists and is specific;
- harmful/retaliatory advice is absent in red-team fixtures.

### 16.2 Scenario suite

Initial fixtures include:

1. date committed without engineering input;
2. repeated team execution failure causing manager rescue work;
3. conflict where user attributes malicious intent without evidence;
4. unclear ownership across two teams;
5. new-manager context gap;
6. performance concern requiring HR caution;
7. user asks for retaliatory framing;
8. narrative with insufficient evidence for action.

### 16.3 Human rubric

Each release candidate should be reviewed on:

- evidence discipline;
- alternative interpretation quality;
- usefulness of unknowns;
- proportionality of recommended action;
- stakeholder framing quality;
- non-genericness;
- privacy/safety behavior.

---

## 17. Observability

v0.1 does not transmit telemetry.

Local diagnostic logging can include:

- provider name;
- request duration;
- model name;
- validation success/failure;
- exception class.

It must not log the raw narrative by default.

---

## 18. Packaging and release

### Python

- Python >=3.11
- `pyproject.toml`
- core dependencies: Pydantic, Typer, Rich
- optional extras: `openai`, `api`, `dev`
- build via `python -m build`

### Quality gates

- pytest
- coverage gate (>=85% for v0.1)
- Python bytecode compilation
- package import/install smoke test
- CLI smoke test
- API smoke test when optional dependencies are installed

### GitHub

- CI on pushes and pull requests;
- CodeQL workflow;
- Dependabot;
- issue templates;
- contribution guide;
- security policy;
- changelog;
- release checklist.

---

## 19. Roadmap

### v0.1 — Navigate

- structured situation analysis;
- reality-check mode;
- local history;
- deterministic pattern report;
- CLI + library + optional HTTP API;
- OpenAI provider + offline provider.

### v0.2 — Learn from outcomes

- user records what happened;
- compare predicted risks vs outcomes;
- improve recurring-pattern evidence;
- intervention-load timeline;
- mechanism recommendations.

### v0.3 — Context graph

- decisions;
- dependencies;
- ownership;
- recurring stakeholders;
- unresolved assumptions;
- confidence decay as context ages.

### v0.4 — Collaboration

- intentionally share a sanitized situation map;
- collaborative option review;
- team-level mechanisms without exposing private reflection history.

---

## 20. Release success criteria

v0.1 is ready when:

1. A new user can install and analyze a situation in under five minutes.
2. Offline mode works with no network and makes its limitations obvious.
3. Cloud mode returns a typed analysis and validates it.
4. Curated adversarial scenarios pass deterministic integrity checks.
5. No secret is committed or persisted.
6. Situation history and pattern reports work locally.
7. The package builds cleanly and can be installed from its wheel.
8. README communicates privacy boundaries and non-goals clearly.
9. CI configuration is present and reproducible.
10. The public repository contains no private story, employer-confidential details, or personal data used during product discovery.

---

## 21. Product thesis in one sentence

**ALINA helps managers separate signal from story, pressure-test their interpretation, choose a proportionate next move, and notice when the same organizational problem keeps coming back.**
