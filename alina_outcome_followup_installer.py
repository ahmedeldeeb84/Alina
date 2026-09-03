from pathlib import Path

path = Path("src/alina/web/index.html")
text = path.read_text()

old = '''            <section class="conversation-card" id="outcome-memory">
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
      </section>'''

new = '''      <details class="conversation-card" id="outcome-memory">
        <summary class="conversation-head">
          <span class="conversation-icon" aria-hidden="true">↺</span>
          <span><span class="card-label">Outcome memory</span><br /><strong>Update this situation later</strong></span>
        </summary>
        <div class="spacing-top">
          <h3>What happened?</h3>
          <p class="confidence-reason">When you know how this played out, add the outcome. ALINA will keep it in this browser and use it to pressure-test future recommendations.</p>
          <label class="field spacing-top">
            <span class="field-label">Outcome <em>optional</em></span>
            <textarea id="outcome-note" rows="3" maxlength="1500" placeholder="e.g. We clarified ownership, reduced scope, and the launch went ahead on Friday."></textarea>
          </label>
          <div class="form-actions spacing-top">
            <button class="button button-quiet" id="save-outcome" type="button">Save outcome</button>
            <span id="outcome-status" class="field-help"></span>
          </div>
        </div>
      </details>'''

if old not in text:
    raise SystemExit("Expected outcome block was not found. No file changed.")

text = text.replace(old, new, 1)
path.write_text(text)

print("Outcome memory UX updated.")
print("Now run:")
print("  pytest")
print("  git diff --check")
print("  git add src/alina/web/index.html")
print('  git commit -m "Make outcome memory a later follow-up"')
print("  git push")
