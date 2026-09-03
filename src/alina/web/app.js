(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const form = $("analysis-form");
  const narrative = $("narrative");
  const results = $("results");
  const errorBox = $("error-box");
  const submitButton = form.querySelector(".analyze-button");
  let mode = "navigation";
  let currentHistoryId = null;
  const HISTORY_KEY = "alina.structured-history.v1";
  const HISTORY_LIMIT = 12;

  const example = {
    title: "Friday launch commitment",
    narrative: "My PM committed us to a Friday launch date before speaking to engineering. One engineer says the full scope needs at least another week. My manager has asked me to find a path to Friday, but has not explicitly said whether scope can change. We already slipped twice, so I think leadership will see any further delay as a failure. The team is tired and I do not want to commit to something we cannot deliver safely.",
    goal: "Decide how to respond to the Friday commitment without creating unnecessary escalation.",
    stakeholders: "PM, my manager, engineering lead, delivery team",
    constraints: "Friday customer expectation, team capacity, quality risk"
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

  function splitList(value) {
    return value.split(",").map((item) => item.trim()).filter(Boolean);
  }

  function setText(id, value, fallback = "—") {
    $(id).textContent = value || fallback;
  }

  function create(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function refs(parent, items = []) {
    if (!items.length) return;
    const row = create("div", "ref-row");
    items.forEach((item) => row.appendChild(create("span", "ref-chip", item)));
    parent.appendChild(row);
  }

  function renderEvidence(id, items = []) {
    const host = $(id);
    clear(host);
    if (!items.length) {
      host.appendChild(create("p", "empty-state", "None surfaced in this analysis."));
      return;
    }
    items.forEach((item) => {
      const card = create("article", "evidence-item");
      card.appendChild(create("span", "evidence-id", `${item.id} · ${item.importance || "medium"}`));
      card.appendChild(create("p", "", item.statement));
      host.appendChild(card);
    });
  }

  function renderTensions(items = []) {
    const host = $("tensions-list");
    clear(host);
    if (!items.length) return host.appendChild(create("p", "empty-state", "No core tensions surfaced."));
    items.forEach((item) => {
      const card = create("article", "tension-card");
      card.appendChild(create("h4", "", item.name));
      card.appendChild(create("p", "", item.description));
      refs(card, item.evidence_refs);
      host.appendChild(card);
    });
  }

  function appendList(host, values, emptyText) {
    clear(host);
    if (!values || !values.length) {
      host.appendChild(create("li", "", emptyText || "None noted."));
      return;
    }
    values.forEach((value) => host.appendChild(create("li", "", value)));
  }

  function renderOptions(items = []) {
    const host = $("options-list");
    clear(host);
    items.forEach((item) => {
      const card = create("article", "option-card");
      const top = create("div", "option-top");
      top.appendChild(create("h4", "", item.name));
      top.appendChild(create("span", "reversibility", `${item.reversibility || "medium"} reversibility`));
      card.appendChild(top);
      card.appendChild(create("p", "option-action", item.action));

      const lists = create("div", "option-lists");
      const benefits = create("div");
      benefits.appendChild(create("span", "", "Benefits"));
      const benefitList = create("ul");
      (item.benefits || []).forEach((v) => benefitList.appendChild(create("li", "", v)));
      if (!benefitList.children.length) benefitList.appendChild(create("li", "", "No explicit benefit listed."));
      benefits.appendChild(benefitList);

      const downsides = create("div");
      downsides.appendChild(create("span", "", "Downsides"));
      const downsideList = create("ul");
      (item.downsides || []).forEach((v) => downsideList.appendChild(create("li", "", v)));
      if (!downsideList.children.length) downsideList.appendChild(create("li", "", "No explicit downside listed."));
      downsides.appendChild(downsideList);

      lists.append(benefits, downsides);
      card.appendChild(lists);
      refs(card, item.evidence_refs);
      host.appendChild(card);
    });
  }

  function renderHypotheses(items = []) {
    const host = $("hypotheses-list");
    clear(host);
    if (!items.length) return host.appendChild(create("p", "empty-state", "No alternatives surfaced."));
    items.forEach((item) => {
      const card = create("article", "stack-card");
      card.appendChild(create("h4", "", item.hypothesis));
      const support = (item.supporting_signals || []).slice(0, 2).join(" · ");
      const weaken = (item.weakening_signals || []).slice(0, 2).join(" · ");
      if (support) card.appendChild(create("p", "", `Supports: ${support}`));
      if (weaken) card.appendChild(create("p", "stack-meta", `Would weaken: ${weaken}`));
      refs(card, item.evidence_refs);
      host.appendChild(card);
    });
  }

  function renderStakeholders(items = []) {
    const host = $("stakeholders-list");
    clear(host);
    if (!items.length) return host.appendChild(create("p", "empty-state", "No stakeholder lenses surfaced."));
    items.forEach((item) => {
      const card = create("article", "stack-card");
      card.appendChild(create("h4", "", `${item.stakeholder}${item.role && item.role !== "unknown" ? ` · ${item.role}` : ""}`));
      const interests = [...(item.stated_interests || []), ...(item.hypothesized_interests || []).map((v) => `${v} (hypothesis)`)].slice(0, 3);
      if (interests.length) card.appendChild(create("p", "", interests.join(" · ")));
      if (item.uncertainty) card.appendChild(create("p", "stack-meta", item.uncertainty));
      host.appendChild(card);
    });
  }

  function renderSignals(items = []) {
    const host = $("signals-list");
    clear(host);
    if (!items.length) return host.appendChild(create("p", "empty-state", "No specific signals listed."));
    items.forEach((item) => {
      const card = create("article", "stack-card");
      card.appendChild(create("h4", "", item.signal));
      card.appendChild(create("p", "", item.meaning));
      host.appendChild(card);
    });
  }

  function renderRisks(data) {
    const host = $("risks-list");
    clear(host);
    const groups = [
      ["If you act", data.risks_of_action || []],
      ["If you do not act", data.risks_of_inaction || []]
    ];
    groups.forEach(([label, items]) => {
      items.slice(0, 3).forEach((item) => {
        const card = create("article", "stack-card");
        card.appendChild(create("h4", "", `${label} · ${item.severity || "medium"}`));
        card.appendChild(create("p", "", item.description));
        refs(card, item.evidence_refs);
        host.appendChild(card);
      });
    });
    (data.cautions || []).slice(0, 3).forEach((caution) => {
      const card = create("article", "stack-card");
      card.appendChild(create("h4", "", "Caution"));
      card.appendChild(create("p", "", caution));
      host.appendChild(card);
    });
    if (!host.children.length) host.appendChild(create("p", "empty-state", "No additional risks or cautions listed."));
  }

  function renderConversation(framing = {}) {
    setText("conversation-objective", framing.objective, "Prepare a grounded conversation");
    setText("conversation-opening", framing.opening, "State the observable facts, name the uncertainty, and ask for the constraint that is actually fixed.");
    setText("conversation-ask", framing.clear_ask, "Clarify the decision that needs to be made.");
    appendList($("conversation-questions"), framing.questions_to_ask || [], "Ask what evidence or constraint would change the decision.");
    appendList($("conversation-avoid"), framing.avoid || [], "Avoid unsupported intent attribution.");
  }

  function renderLongitudinal(items = []) {
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
    setText("result-title", $("title").value.trim() || "Analysis");
    setText("summary-text", data.summary);
    setText("confidence-reason", data.confidence_reason, "Confidence reflects the evidence available in the narrative.");
    $("confidence-badge").textContent = `${data.confidence || "unknown"} confidence`;
    $("provider-badge").textContent = data.provider ? `${data.provider}${data.model ? ` · ${data.model}` : ""}` : "analysis";

    renderEvidence("facts-list", data.facts);
    renderEvidence("assumptions-list", data.assumptions);
    renderEvidence("unknowns-list", data.unknowns);
    renderTensions(data.tensions);
    renderLongitudinal(data.longitudinal_insights || []);

    const recommendation = data.recommendation || {};
    setText("recommendation-action", recommendation.action, "Gather the missing context before taking an irreversible step.");
    setText("recommendation-rationale", recommendation.rationale, "The safest move is the one proportionate to the evidence available.");
    setText("recommendation-first-step", recommendation.first_step, "Clarify the highest-impact unknown.");

    renderOptions(data.options || []);
    renderHypotheses(data.alternative_hypotheses || []);
    renderStakeholders(data.stakeholders || []);
    renderConversation(data.conversation_framing || {});
    renderSignals(data.signals_to_watch || []);
    renderRisks(data);

    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function setLoading(loading) {
    submitButton.classList.toggle("is-loading", loading);
    submitButton.disabled = loading;
    submitButton.querySelector(".button-label").textContent = loading ? "Building map…" : "Build situation map";
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
  }

  function clearError() {
    errorBox.hidden = true;
    errorBox.textContent = "";
  }

  function loadExample(scroll = true) {
    Object.entries(example).forEach(([key, value]) => {
      const input = $(key);
      if (input) input.value = value;
    });
    narrative.dispatchEvent(new Event("input"));
    if (scroll) $("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
    narrative.focus({ preventScroll: true });
  }

  document.querySelectorAll(".mode-button").forEach((button) => {
    button.addEventListener("click", () => {
      mode = button.dataset.mode;
      document.querySelectorAll(".mode-button").forEach((candidate) => {
        const active = candidate === button;
        candidate.classList.toggle("is-active", active);
        candidate.setAttribute("aria-pressed", String(active));
      });
    });
  });

  narrative.addEventListener("input", () => {
    $("char-count").textContent = narrative.value.length.toLocaleString();
  });

  $("load-example").addEventListener("click", () => loadExample(false));
  $("load-example-hero").addEventListener("click", () => loadExample(true));

  $("analyze-another").addEventListener("click", () => {
    results.hidden = true;
    $("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
    narrative.focus({ preventScroll: true });
  });

  $("clear-history").addEventListener("click", () => {
    try { localStorage.removeItem(HISTORY_KEY); } catch (_) {}
    currentHistoryId = null;
    updateHistoryStatus();
    $("outcome-note").value = "";
    $("outcome-status").textContent = "Local history cleared.";
  });

  $("save-outcome").addEventListener("click", saveCurrentOutcome);
  updateHistoryStatus();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    const payload = {
      title: $("title").value.trim() || null,
      narrative: narrative.value.trim(),
      goal: $("goal").value.trim() || null,
      stakeholders: splitList($("stakeholders").value),
      constraints: splitList($("constraints").value),
      tags: [],
      mode,
      history_context: buildHistoryContext()
    };

    if (payload.narrative.length < 20) {
      showError("Please describe the situation in at least 20 characters.");
      narrative.focus();
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/v1/analyze?provider=auto&save=false", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      let data;
      try { data = await response.json(); } catch (_) { data = null; }
      if (!response.ok) {
        const detail = data && data.detail ? data.detail : `Analysis failed (${response.status}).`;
        throw new Error(detail);
      }
      render(data);
      currentHistoryId = rememberAnalysis(payload, data);
      $("outcome-note").value = "";
      $("outcome-status").textContent = currentHistoryId ? "Situation remembered locally." : "Browser storage is unavailable.";
      updateHistoryStatus();
    } catch (error) {
      showError(error instanceof Error ? error.message : "Unable to analyze the situation. Please try again.");
    } finally {
      setLoading(false);
    }
  });
})();
