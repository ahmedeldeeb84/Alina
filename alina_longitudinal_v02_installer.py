from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent

def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}. No files were written.")
    return text.replace(old, new, 1)

updates: dict[Path, str] = {}

# ---------------------------------------------------------------------------
# 1) Domain model: browser-supplied compact history + longitudinal insights.
# ---------------------------------------------------------------------------
models_path = ROOT / "src/alina/models.py"
models = models_path.read_text()

models = replace_once(
    models,
    'class SituationInput(StrictModel):\n',
    '''class PriorSituationContext(StrictModel):
    created_at: str | None = None
    title: str | None = None
    summary: str
    tensions: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    outcome: str | None = None


class SituationInput(StrictModel):
''',
    "models: PriorSituationContext",
)

models = replace_once(
    models,
    '    mode: Mode = Mode.NAVIGATION\n',
    '    mode: Mode = Mode.NAVIGATION\n    history_context: list[PriorSituationContext] = Field(default_factory=list, max_length=8)\n',
    "models: history_context",
)

models = replace_once(
    models,
    'class SituationAnalysis(StrictModel):\n',
    '''class LongitudinalInsight(StrictModel):
    pattern: str
    implication: str
    evidence: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM


class SituationAnalysis(StrictModel):
''',
    "models: LongitudinalInsight",
)

models = replace_once(
    models,
    '    signals_to_watch: list[SignalToWatch] = Field(default_factory=list)\n',
    '    signals_to_watch: list[SignalToWatch] = Field(default_factory=list)\n    longitudinal_insights: list[LongitudinalInsight] = Field(default_factory=list)\n',
    "models: longitudinal_insights",
)
updates[models_path] = models

# ---------------------------------------------------------------------------
# 2) Prompt: make prior situations usable without silently becoming facts.
# ---------------------------------------------------------------------------
prompts_path = ROOT / "src/alina/prompts.py"
prompts = prompts_path.read_text()

prompts = replace_once(
    prompts,
    '13. Confidence must fall when material unknowns remain.',
    '''13. Confidence must fall when material unknowns remain.
14. Prior situation history is context, not verified truth. Never promote a past interpretation into a current stated fact.
15. Use longitudinal history to identify descriptive recurrence, change over time, and whether recorded outcomes support or weaken prior approaches.
16. Only emit a longitudinal insight when it is supported by the current situation plus at least one prior situation, or by at least two prior situations. Do not claim causality from recurrence.

Use concise management language.''',
    "prompts: longitudinal system rules",
)

marker = "def user_prompt(s: SituationInput) -> str:\n"
if prompts.count(marker) != 1:
    raise RuntimeError("prompts: could not locate user_prompt exactly once. No files were written.")

prefix = prompts.split(marker, 1)[0]
new_prompt_tail = r'''def _history_block(s: SituationInput) -> str:
    if not s.history_context:
        return "- none supplied"

    blocks: list[str] = []
    for i, item in enumerate(s.history_context[-8:], start=1):
        tensions = ", ".join(item.tensions) or "none recorded"
        unknowns = " | ".join(item.unknowns[:4]) or "none recorded"
        stakeholders = ", ".join(item.stakeholders) or "none recorded"
        blocks.append(
            f"""[{i}] {item.created_at or 'date unknown'} — {item.title or 'untitled'}
Summary: {item.summary}
Tensions: {tensions}
Unknowns: {unknowns}
Stakeholders: {stakeholders}
Recommendation: {item.recommendation or 'not recorded'}
Outcome: {item.outcome or 'not recorded'}"""
        )
    return "\n\n".join(blocks)


def user_prompt(s: SituationInput) -> str:
    constraints = "\n".join(f"- {x}" for x in s.constraints) or "- none supplied"
    stakeholders = "\n".join(f"- {x}" for x in s.stakeholders) or "- none supplied"
    history = _history_block(s)
    return f"""MODE: {s.mode.value}
TITLE: {s.title or 'untitled'}
GOAL: {s.goal or 'not supplied'}
CONSTRAINTS:
{constraints}
STAKEHOLDERS:
{stakeholders}

SITUATION NARRATIVE:
{s.narrative}

RECENT STRUCTURED HISTORY:
{history}

Produce a complete SituationAnalysis. Use IDs F1.. for current-situation facts, A1.. for current-situation assumptions, U1.. for current-situation unknowns.
Do not use prior-history statements as current facts or current evidence IDs.
If recurrence is supported by the current situation plus at least one prior situation, or by at least two prior situations, add 1-3 longitudinal_insights. Each insight must:
- describe an observed recurrence or change, not a causal diagnosis;
- name the implication for the manager;
- cite the relevant prior title/date or concise historical signal in its evidence list;
- lower confidence when the comparison is weak.
If no defensible recurrence exists, return an empty longitudinal_insights list.
Use recorded outcomes, when present, to update the usefulness of prior approaches rather than assuming the recommendation worked.
In reality_check mode, explicitly pressure-test the user's strongest interpretation and include evidence that would falsify it.
"""
'''
prompts = prefix + new_prompt_tail
updates[prompts_path] = prompts

# ---------------------------------------------------------------------------
# 3) Web UI: explain local continuity, show patterns, capture outcomes.
# ---------------------------------------------------------------------------
html_path = ROOT / "src/alina/web/index.html"
html = html_path.read_text()

html = replace_once(
    html,
    '<span><strong>Private by design.</strong> This web session does not save your situation. Cloud analysis is used only when the server is configured for it.</span>',
    '''            <span><strong>Local continuity.</strong> ALINA keeps a compact structured history in this browser so it can notice recurrence. That context is included in future cloud analyses when AI mode is active. <span id="history-status">No local history yet.</span> <button class="text-button" id="clear-history" type="button">Clear history</button></span>''',
    "html: privacy/history note",
)

html = replace_once(
    html,
    '<section class="recommendation-block">',
    '''      <section class="result-section" id="longitudinal-section" hidden>
        <div class="result-section-head"><span>↺</span><div><h3>Across your recent situations</h3><p>Descriptive recurrence from structured context stored in this browser.</p></div></div>
        <div id="longitudinal-list" class="stack-list"></div>
      </section>

      <section class="recommendation-block">''',
    "html: longitudinal section",
)

html = replace_once(
    html,
    '<div class="results-footer">',
    '''      <section class="conversation-card" id="outcome-memory">
        <div class="conversation-head"><span class="conversation-icon" aria-hidden="true">↺</span><div><span class="card-label">Outcome memory</span><h3>What happened after this?</h3></div></div>
        <p class="confidence-reason">Add the outcome when you know it. ALINA will keep it in this browser and use it to pressure-test future recommendations.</p>
        <label class="field spacing-top">
          <span class="field-label">Outcome <em>optional</em></span>
          <textarea id="outcome-note" rows="3" maxlength="1500" placeholder="e.g. We clarified ownership, reduced scope, and the launch went ahead on Friday."></textarea>
        </label>
        <div class="form-actions spacing-top">
          <button class="button button-quiet" id="save-outcome" type="button">Save outcome</button>
          <span id="outcome-status" class="field-help"></span>
        </div>
      </section>

      <div class="results-footer">''',
    "html: outcome memory",
)
updates[html_path] = html

# ---------------------------------------------------------------------------
# 4) Browser logic: compact local history, send last 8, render recurrence.
# ---------------------------------------------------------------------------
js_path = ROOT / "src/alina/web/app.js"
js = js_path.read_text()

js = replace_once(
    js,
    '''  let mode = "navigation";

  const example = {''',
    '''  let mode = "navigation";
  let currentHistoryId = null;
  const HISTORY_KEY = "alina.structured-history.v1";
  const HISTORY_LIMIT = 12;

  const example = {''',
    "app.js: history constants",
)

js = replace_once(
    js,
    '''    constraints: "Friday customer expectation, team capacity, quality risk"
  };

  function splitList(value) {''',
    '''    constraints: "Friday customer expectation, team capacity, quality risk"
  };

  function readHistory() {
    try {
      const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (_) {
      return [];
    }
  }

  function writeHistory(items) {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(-HISTORY_LIMIT)));
      return true;
    } catch (_) {
      return false;
    }
  }

  function buildHistoryContext() {
    return readHistory().slice(-8).map((item) => ({
      created_at: item.created_at || null,
      title: item.title || null,
      summary: item.summary || "",
      tensions: Array.isArray(item.tensions) ? item.tensions.slice(0, 6) : [],
      unknowns: Array.isArray(item.unknowns) ? item.unknowns.slice(0, 6) : [],
      stakeholders: Array.isArray(item.stakeholders) ? item.stakeholders.slice(0, 8) : [],
      recommendation: item.recommendation || null,
      outcome: item.outcome || null
    })).filter((item) => item.summary);
  }

  function updateHistoryStatus() {
    const host = $("history-status");
    if (!host) return;
    const count = readHistory().length;
    host.textContent = count
      ? `${count} recent situation${count === 1 ? "" : "s"} remembered in this browser.`
      : "No local history yet.";
  }

  function rememberAnalysis(payload, data) {
    const id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
    const item = {
      id,
      created_at: new Date().toISOString(),
      title: payload.title || null,
      summary: data.summary || payload.narrative.slice(0, 700),
      tensions: (data.tensions || []).map((x) => x.name).filter(Boolean).slice(0, 6),
      unknowns: (data.unknowns || []).map((x) => x.statement).filter(Boolean).slice(0, 6),
      stakeholders: (data.stakeholders || []).map((x) => x.stakeholder).filter(Boolean).slice(0, 8),
      recommendation: data.recommendation && data.recommendation.action ? data.recommendation.action : null,
      outcome: null
    };
    const items = readHistory();
    items.push(item);
    return writeHistory(items) ? id : null;
  }

  function saveCurrentOutcome() {
    const note = $("outcome-note").value.trim();
    const status = $("outcome-status");
    if (!currentHistoryId) {
      status.textContent = "Analyze a situation first.";
      return;
    }
    const items = readHistory();
    const item = items.find((candidate) => candidate.id === currentHistoryId);
    if (!item) {
      status.textContent = "This situation is no longer in local history.";
      return;
    }
    item.outcome = note || null;
    if (writeHistory(items)) {
      status.textContent = note ? "Outcome saved locally." : "Outcome cleared.";
    } else {
      status.textContent = "Browser storage is unavailable.";
    }
  }

  function splitList(value) {''',
    "app.js: history helpers",
)

js = replace_once(
    js,
    '''  function render(data) {
''',
    '''  function renderLongitudinal(items = []) {
    const section = $("longitudinal-section");
    const host = $("longitudinal-list");
    clear(host);
    if (!items.length) {
      section.hidden = true;
      return;
    }
    items.forEach((item) => {
      const card = create("article", "stack-card");
      card.appendChild(create("h4", "", item.pattern));
      if (item.implication) card.appendChild(create("p", "", item.implication));
      if (item.evidence && item.evidence.length) {
        card.appendChild(create("p", "stack-meta", `Seen in: ${item.evidence.join(" · ")}`));
      }
      if (item.confidence) {
        card.appendChild(create("p", "stack-meta", `${item.confidence} confidence · recurrence is descriptive, not causal`));
      }
      host.appendChild(card);
    });
    section.hidden = false;
  }

  function render(data) {
''',
    "app.js: renderLongitudinal",
)

js = replace_once(
    js,
    '''    renderTensions(data.tensions);

    const recommendation = data.recommendation || {};''',
    '''    renderTensions(data.tensions);
    renderLongitudinal(data.longitudinal_insights || []);

    const recommendation = data.recommendation || {};''',
    "app.js: render longitudinal call",
)

js = replace_once(
    js,
    '''  form.addEventListener("submit", async (event) => {''',
    '''  $("clear-history").addEventListener("click", () => {
    try { localStorage.removeItem(HISTORY_KEY); } catch (_) {}
    currentHistoryId = null;
    updateHistoryStatus();
    $("outcome-note").value = "";
    $("outcome-status").textContent = "Local history cleared.";
  });

  $("save-outcome").addEventListener("click", saveCurrentOutcome);
  updateHistoryStatus();

  form.addEventListener("submit", async (event) => {''',
    "app.js: history event listeners",
)

js = replace_once(
    js,
    '''      tags: [],
      mode
    };''',
    '''      tags: [],
      mode,
      history_context: buildHistoryContext()
    };''',
    "app.js: request history payload",
)

js = replace_once(
    js,
    '''      render(data);
    } catch (error) {''',
    '''      render(data);
      currentHistoryId = rememberAnalysis(payload, data);
      $("outcome-note").value = "";
      $("outcome-status").textContent = currentHistoryId ? "Situation remembered locally." : "Browser storage is unavailable.";
      updateHistoryStatus();
    } catch (error) {''',
    "app.js: remember successful analysis",
)
updates[js_path] = js

# ---------------------------------------------------------------------------
# 5) Contract test.
# ---------------------------------------------------------------------------
test_path = ROOT / "tests/test_longitudinal_context.py"
test_content = '''from alina.models import PriorSituationContext, SituationInput
from alina.prompts import user_prompt


def test_history_context_is_included_without_becoming_current_evidence():
    situation = SituationInput(
        narrative="The PM changed scope again after engineering had already committed to the delivery plan.",
        history_context=[
            PriorSituationContext(
                created_at="2026-09-01T09:00:00Z",
                title="Earlier scope change",
                summary="A late scope change created delivery pressure.",
                tensions=["scope vs date", "stakeholder alignment"],
                stakeholders=["PM", "engineering lead"],
                recommendation="Clarify which constraint is fixed.",
                outcome="Scope was reduced after alignment.",
            )
        ],
    )
    prompt = user_prompt(situation)
    assert "RECENT STRUCTURED HISTORY" in prompt
    assert "Earlier scope change" in prompt
    assert "Scope was reduced after alignment." in prompt
    assert "Do not use prior-history statements as current facts" in prompt


def test_history_context_is_bounded():
    items = [
        PriorSituationContext(summary=f"Situation {i}")
        for i in range(8)
    ]
    situation = SituationInput(
        narrative="This is a sufficiently long current situation narrative for validation.",
        history_context=items,
    )
    assert len(situation.history_context) == 8
'''
updates[test_path] = test_content

# Write only after all transformations succeeded.
for path, content in updates.items():
    path.parent.mkdir(parents=True, exist_ok=True)

for path, content in updates.items():
    path.write_text(content)

print("ALINA longitudinal context patch applied.")
print("Changed:")
for path in updates:
    print(f"  - {path.relative_to(ROOT)}")
print("\nNext:")
print("  pytest")
print("  git diff --check")
print('  git add src/alina/models.py src/alina/prompts.py src/alina/web/index.html src/alina/web/app.js tests/test_longitudinal_context.py')
print('  git commit -m "Add local longitudinal context and outcome memory"')
print("  git push")
