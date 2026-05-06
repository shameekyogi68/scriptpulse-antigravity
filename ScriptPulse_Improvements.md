# ScriptPulse — Full Product Improvement Plan
**Source Review:** Complete codebase audit (v15.0 Gold)
**Purpose:** Prompt-ready improvement list for AI-IDE implementation
**Format:** Each item has a Priority, File reference, exact Problem, and concrete Fix instruction.

---

## HOW TO USE THIS FILE IN YOUR AI IDE

> Paste a section (e.g., "SECTION A — Critical Bugs") into your IDE prompt and say:
> _"Implement all improvements in this section exactly as described."_
> Work section by section. Sections are ordered from most critical to lowest priority.

---

## SECTION A — CRITICAL BUGS (Ship-Blockers)

### A1 · `NoneType` Crash in `_build_location_profile`
**File:** `scriptpulse/agents/writer_agent.py` → `_build_location_profile()`
**Problem:** When a scene has no scene heading (e.g., pure-dialogue or parenthetical-only scripts), `location_data` is `None`. Calling `.get()` on `None` raises `AttributeError: 'NoneType' object has no attribute 'get'`. This crashes the entire pipeline for scripts that don't use standard INT./EXT. formatting — confirmed by the failing tests `test_no_scene_headings` and `test_only_parentheticals`.
**Fix:**
```python
# In _build_location_profile(), guard every loc_data access:
loc_data = s.get('location_data') or {}
interior = loc_data.get('interior', '') or ''
interior = interior.strip().upper() if interior else ''
location = loc_data.get('location', 'UNKNOWN') or 'UNKNOWN'
```
Apply the same `or {}` guard anywhere in the file that reads `location_data`.

---

### A2 · Missing `run_id` and `agent_timings` in `meta` block
**File:** `scriptpulse/pipeline/runner.py` → final `report` dict assembly
**Problem:** Test `test_meta_block_present_and_typed` fails because `meta` dict is missing `run_id` (UUID) and `agent_timings` (per-agent millisecond breakdown). These fields are expected by downstream systems and the test suite.
**Fix:** Add to the `report['meta']` dict:
```python
import uuid
report['meta']['run_id'] = str(uuid.uuid4())
report['meta']['agent_timings'] = telemetry['stages']  # already collected
```

---

### A3 · `standard_output_keys` test failure — missing pipeline contract keys
**File:** `scriptpulse/pipeline/runner.py`
**Problem:** Test `test_standard_output_keys_always_present` fails. The pipeline must always return a fixed set of top-level keys regardless of input. Currently some keys like `parsed_lines` and `patterns` are absent from the returned `report` dict (defined in `schemas/models.py` as `PipelineOutput` but not populated by `runner.py`).
**Fix:** Ensure these keys are always present in the returned `report`, even as empty defaults:
```python
report.setdefault('parsed_lines', [])
report.setdefault('patterns', [])
report.setdefault('features', report.get('perceptual_features', []))
report.setdefault('trace', report.get('temporal_trace', []))
report.setdefault('agency_analysis', {})
```

---

### A4 · Violence Override Is Too Aggressive — Kills Positive Scenes
**File:** `scriptpulse/agents/perception_agent.py` → `_extract_affective_load()`
**Problem:** Any scene containing words like `"trigger"`, `"weapon"`, `"knife"`, or `"blood"` (even metaphorical uses like "it triggered a memory" or "a knife of guilt") forces `compound = -0.99` and `neg = 0.98`. This makes genre-appropriate action or thriller scenes report as uniformly negative, destroying score accuracy.
**Fix:** Apply violence override **only when 3+ violence keywords co-occur**, OR when violence keywords appear in `'A'` (action) lines specifically, OR when a death-verb (`killed`, `murdered`, `shot dead`) is present. Reduce the override to a softer penalty (`compound = -0.65`) rather than clamping to maximum negative.
```python
violence_triggers_hard = ['killed', 'murdered', 'shot dead', 'execution', 'massacre', 'slaughter']
violence_triggers_soft = ['shot', 'blood', 'body', 'weapon', 'knife', 'grenade', 'trigger']

hard_match = any(w in all_text for w in violence_triggers_hard)
soft_count = sum(1 for w in violence_triggers_soft if w in all_text)

if hard_match or soft_count >= 3:
    penalty = -0.99 if hard_match else -0.65
    return {'pos': 0.00, 'neg': abs(penalty), 'neu': 1 - abs(penalty), 'compound': penalty}
```

---

### A5 · Scene Turn Sentiment Forced Override Conflicts with Perception Layer
**File:** `scriptpulse/pipeline/runner.py` → Stage 5 (Scene Turns block)
**Problem:** The scene-turn post-processing loop in `runner.py` directly overwrites `s['sentiment']` for any scene containing violence keywords — even if the `perception_agent` correctly calculated a nuanced negative score. This creates double-penalization and makes the `temporal_trace` inconsistent with `perceptual_features`, breaking chart accuracy.
**Fix:** Remove the direct `s['sentiment'] = min(...)` assignment. Instead, record the forced label separately and let the downstream `InterpretationAgent` consume it:
```python
# Replace this:
s['sentiment'] = min(s.get('sentiment', 0), -0.7)

# With this:
s['scene_turn']['violence_override'] = True  # flag only, don't mutate sentiment
```

---

### A6 · FDX Importer Is Unreachable (Wrong Import Path)
**File:** `app/streamlit_app.py`
**Problem:** The FDX upload handler does `from scriptpulse.agents import importers` then calls `importers.run(...)`. But the `ImporterAgent` class lives in `scriptpulse/agents/structure_agent.py`, not in any file called `importers.py`. This means `.fdx` files **always fail silently** with the generic error message even for valid FDX files.
**Fix:**
```python
# Change in app/streamlit_app.py, FDX branch:
from scriptpulse.agents.structure_agent import ImporterAgent
importer = ImporterAgent()
parsed_lines = importer.run(uploaded_file.getvalue().decode("utf-8"))
if isinstance(parsed_lines, list):
    script_input = "\n".join([l['text'] for l in parsed_lines])
```

---

### A7 · HTML Injection in Error Message (XSS Risk + UX Bug)
**File:** `scriptpulse/pipeline/runner.py` → `run_pipeline()`, line near `raise ValueError`
**Problem:** The minimum-length error message contains a raw `<span style='color: #0052FF;...'>Pulse</span>` HTML tag in a `ValueError` string. When this exception is caught by Streamlit's `st.error()`, the HTML is displayed as raw text to the user. This is both ugly and a latent XSS risk if the error path ever changes.
**Fix:** Remove the HTML from the exception string. Use plain text in exceptions; apply branding only in the UI layer:
```python
raise ValueError(
    "ScriptPulse requires more text to analyze. "
    "Please upload a full script or a longer scene (minimum ~50 words)."
)
```

---

## SECTION B — ACCURACY & RELIABILITY IMPROVEMENTS

### B1 · ScriptPulse Score Formula Uses Wrong Dict Key
**File:** `scriptpulse/agents/writer_agent.py` → `_calculate_scriptpulse_score()`
**Problem:** The `definitive_final.md` patch document confirms that an old version of this function used `dialogue_ratio` as the key, but the actual data uses `dialogue_action_ratio`. If the patched version was not applied cleanly, scores will silently use a `0.55` default instead of real dialogue data, producing inaccurate scores that do not reflect the actual script.
**Fix:** Verify the key is correct in the live code:
```python
dr = dashboard.get('dialogue_action_ratio', {})  # NOT 'dialogue_ratio'
d_ratio = dr.get('global_dialogue_ratio', 0.55)
d_bench = dr.get('genre_benchmark', 0.55)
```
Add an assertion or log warning if `dr` is empty to catch future regressions.

---

### B2 · Confidence Score in `meta` Is Hard-Coded, Not Calculated
**File:** `scriptpulse/pipeline/runner.py`
**Problem:** `'confidence': 0.98 if len(segmented_scenes) > 5 else 0.85` is a hardcoded binary. The project has a fully-featured `ConfidenceScorer` class in `scriptpulse/utils/confidence_scorer.py` that factors in signal flatline, scene count, and fatigue ratio — but it is **never called** by `runner.py`.
**Fix:**
```python
from scriptpulse.utils.confidence_scorer import ConfidenceScorer
scorer = ConfidenceScorer()
confidence_result = scorer.calculate(temporal_trace)
report['meta']['confidence'] = confidence_result['score']
report['meta']['confidence_level'] = confidence_result['level']
report['meta']['confidence_reasons'] = confidence_result['reasons']
```

---

### B3 · Duplicate Feature-Number Comment in `perception_agent.py`
**File:** `scriptpulse/agents/perception_agent.py` → `run()` method
**Problem:** The loop has two blocks both labeled `# 6.` (one for `_extract_affective_load`, one for `_extract_narrative_metadata`). This is a copy-paste error that creates developer confusion and may indicate one of the two blocks was added without proper review of its interaction with the other.
**Fix:** Re-number correctly: affective load = `# 6.`, narrative metadata = `# 7.`. Verify the `features` dict uses the correct keys from each block (no cross-contamination).

---

### B4 · Character Name Normalization Misses Multi-Word Names
**File:** `scriptpulse/agents/perception_agent.py` → `normalize_character_name()`
**Problem:** The regex `re.sub(r'[^A-Z0-9\s#]', '', stemmed)` strips hyphens, causing names like `MARY-ANNE` to become `MARY ANNE`, treating them as two different characters. Similarly `DR.SMITH` becomes `DRSMITH`. This inflates character counts and produces split arcs for hyphenated names.
**Fix:**
```python
# Preserve hyphens as word separators, then collapse:
clean = re.sub(r'[^A-Z0-9\s\-]', '', stemmed).strip()
clean = re.sub(r'-+', ' ', clean).strip()  # normalize hyphens to spaces
```
Also add `MR`, `MS`, `DR`, `MRS`, `PROF` to a prefix-strip list rather than the blacklist, so `DR. SMITH` normalizes to `SMITH` rather than being dropped.

---

### B5 · Act Structure Is Fixed at 25%/50%/75% — Not Dynamically Detected
**File:** `scriptpulse/agents/interpretation_agent.py` → `map_to_structure()`
**Problem:** Act boundaries are hardcoded at `25%` and `75%` of scene count. This makes every script look "3-act balanced" regardless of actual dramatic structure. A real 2-act play, a 5-act structure, or a non-linear script will be misrepresented. The `balance` label in `_build_act_structure()` of `writer_agent.py` then reports "Balanced" for scripts that are structurally broken.
**Fix:** Detect act boundaries dynamically using attentional signal valleys as structural markers:
```python
def _find_act_boundary(signals, search_range):
    """Find the lowest attentional signal in a range = likely act break."""
    segment = signals[search_range[0]:search_range[1]]
    if not segment:
        return search_range[0]
    min_idx = segment.index(min(segment, key=lambda s: s['attentional_signal']))
    return search_range[0] + min_idx
```
Search for Act 1 boundary between 20%–30%, Act 2 boundary between 60%–80%.

---

### B6 · Entropy Score Is Raw Shannon Entropy — Not Normalized Per-Scene
**File:** `scriptpulse/agents/perception_agent.py` → `_extract_entropy()`
**Problem:** Shannon entropy of a scene's word frequency is returned raw. Longer scenes naturally produce higher entropy because they contain more unique words. This means "information density" scores are actually scene-length scores, making short scenes appear flat and long scenes appear complex regardless of actual content novelty.
**Fix:** Normalize entropy by scene word count:
```python
def _extract_entropy(self, lines):
    text = " ".join([l['text'] for l in lines]).lower()
    words = re.findall(r'\b\w+\b', text)
    if len(words) < 5:
        return 0.0
    counts = Counter(words)
    total = len(words)
    raw_entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
    # Normalize: divide by log2(unique_words) so max entropy = 1.0
    max_possible = math.log2(len(counts)) if len(counts) > 1 else 1.0
    return round(raw_entropy / max_possible, 3)
```

---

### B7 · Genre Key Case Mismatch in `DynamicsAgent`
**File:** `scriptpulse/agents/dynamics_agent.py` → `run_simulation()`
**Problem:** The `GENRE_PRIORS` dict uses lowercase keys (`'sci-fi'`, `'romance'`) but the UI passes genre as title-case (`"Sci-Fi"`, `"Romance"`). The `.lower()` call normalizes the incoming genre, but `"Sci-Fi".lower()` becomes `"sci-fi"` while the key is `'sci-fi'` — this one works. However `"Avant-Garde".lower()` = `"avant-garde"` which is NOT in `GENRE_PRIORS`. The code silently falls back to Drama priors for Avant-Garde scripts, producing incorrect simulation.
**Fix:** Add all genres offered in the UI to `GENRE_PRIORS`:
```python
'avant-garde': {'lambda': 0.60, 'beta': 0.15},  # Low decay, minimal recovery — intentional
'fantasy':     {'lambda': 0.78, 'beta': 0.35},   # (already present)
```
Also handle `"sci-fi"` and `"science fiction"` as aliases for the same prior.

---

### B8 · `_extract_structural()` Always Returns `location_change: False`
**File:** `scriptpulse/agents/perception_agent.py` → `_extract_structural()`
**Problem:** The `StructuralChange` schema declares `location_change: bool` and `time_change: bool`, but the heuristic implementation always returns `False` for both because it compares `scene.get('location')` which is never populated at the time `EncodingAgent.run()` is called (location extraction happens later in `runner.py` Stage 3b). This means "location change" is always missing from features, which corrupts the `structural_change` sub-score used in attentional signal calculation.
**Fix:** In `_extract_structural()`, compare the current scene's heading string directly against the previous scene's heading:
```python
def _extract_structural(self, scene, all_scenes, idx):
    prev_heading = all_scenes[idx-1].get('heading', '') if idx > 0 else ''
    curr_heading = scene.get('heading', '')
    # Extract location (text before ' - DAY/NIGHT') from heading
    def extract_loc(h): return re.sub(r'\s*-\s*(DAY|NIGHT|.*?)$', '', h).strip()
    location_change = extract_loc(prev_heading) != extract_loc(curr_heading) if idx > 0 else False
    return {'location_change': location_change, 'event_boundary_score': 1.0 if location_change else 0.0}
```

---

### B9 · Dialogue Ratio Benchmark Is Wrong for Several Genres
**File:** `scriptpulse/agents/writer_agent.py` → `_build_global_dialogue_ratio()`
**Problem:** The genre benchmark for dialogue ratio uses incorrect industry standards. For example, Horror is benchmarked like Drama, but real horror scripts are heavily action-line driven (the monster's actions, environmental description). Comedy is benchmarked too low. These wrong benchmarks cause `d_harmony` to penalize correctly-written scripts.
**Fix:** Update benchmarks based on industry norms:
```python
GENRE_BENCHMARKS = {
    'Drama':     0.60,  # Dialogue-heavy
    'Comedy':    0.65,  # Heavy dialogue, fast exchanges
    'Thriller':  0.45,  # Balanced — tension through action too
    'Horror':    0.35,  # Action-description dominant
    'Action':    0.30,  # Mostly action lines
    'Sci-Fi':    0.50,  # Balanced world-building
    'Romance':   0.65,  # Character-driven, dialogue-heavy
    'Fantasy':   0.45,  # World-building action + dialogue
    'Avant-Garde': 0.40,
}
```

---

### B10 · `_diagnose_patterns()` Ignores Scene Count — Flags 3-Scene Scripts
**File:** `scriptpulse/agents/interpretation_agent.py` → `diagnose_patterns()`
**Problem:** The `diagnose_patterns` function uses `len(signals) < 3` as its only guard, but many of its detection loops reference `signals[i:i+3]` windows. A 4-scene script can still trigger false positives for "sustained attentional demand" that require at least 10+ scenes of evidence to be meaningful.
**Fix:** Add minimum scene thresholds per diagnostic type:
```python
MIN_SCENES_FOR_SAG = 8         # Need 8 scenes before a sag is meaningful
MIN_SCENES_FOR_OVERCROWD = 5   # Need 5 scenes to flag character churn
```
Apply these guards before each diagnostic loop.

---

## SECTION C — USER EXPERIENCE & TRUST IMPROVEMENTS

### C1 · Confidence Level Is Never Shown to the User
**File:** `app/views/writer_view.py` and `app/components/uikit.py`
**Problem:** Despite having a `ConfidenceScorer`, no confidence band (`HIGH / MEDIUM / LOW`) is displayed anywhere in the UI. Users analyzing a 2-scene excerpt see the same score display as users analyzing a 200-scene feature film, with no indication that the 2-scene analysis is unreliable. This fundamentally undermines trustworthiness.
**Fix:** Add a confidence badge next to the ScriptPulse Score in the hero score card:
```python
confidence = report.get('meta', {}).get('confidence_level', 'MEDIUM')
reasons = report.get('meta', {}).get('confidence_reasons', [])
confidence_colors = {'HIGH': '#22C55E', 'MEDIUM': '#F59E0B', 'LOW': '#EF4444'}
st.markdown(f"<span style='color:{confidence_colors[confidence]}'>● {confidence} Confidence</span>", unsafe_allow_html=True)
if reasons:
    st.caption(f"Why: {', '.join(reasons)}")
```

---

### C2 · No Minimum Input Validation on Paste Tab
**File:** `app/streamlit_app.py`
**Problem:** The paste-text tab accepts any text `> 100 characters` and runs it through the full pipeline. A user pasting a 120-character lorem ipsum block will get a full "analysis" with a ScriptPulse Score. This produces junk results that erode trust. The upload tab also doesn't validate that a PDF actually contains extractable text.
**Fix:**
- Minimum: 300 words OR at least 1 scene heading for paste input before enabling the Analyze button.
- PDF validation: check that `script_input.strip()` after extraction is at least 300 words, otherwise show: `"This PDF appears to be image-based (scanned). Please convert to text-based PDF or paste text manually."`
- Add a word count indicator below the paste textarea: `f"📝 {len(pasted.split())} words detected"`

---

### C3 · Progress Bar Jumps from 20% to 70% With No Intermediate Updates
**File:** `app/streamlit_app.py` → analysis button click handler
**Problem:** The progress bar shows: `0% → 20% (parsing) → 70% (report) → 100%`. The entire pipeline computation happens between 20% and 70% with no updates, so for a long script the bar stalls at 20% for 10-30 seconds. Users assume it has frozen.
**Fix:** Pass a callback into `run_pipeline()` that allows stage-by-stage progress updates:
```python
def progress_callback(stage_name, pct):
    bar.progress(pct, text=f"Analyzing: {stage_name}...")

report = runner.run_pipeline(
    script_input, genre=genre, lens=lens,
    progress_callback=progress_callback,  # new param
    ...
)
```
In `runner.py`, call `progress_callback("Parsing structure...", 25)`, `("Extracting features...", 45)`, `("Running simulation...", 60)`, `("Generating insights...", 75)` at each stage.

---

### C4 · Export Buttons Appear Even When Report Is from a Previous Run
**File:** `app/streamlit_app.py`
**Problem:** The export section checks `if report and current_input` but uses the current session's `uploaded_file` variable for the title. If the user navigated away and came back, `uploaded_file` may be from a different session or `None`, causing the download filename to be `"ScriptPulse_Writer_Drama.md"` with no actual script title embedded.
**Fix:** Store the filename in `st.session_state` at analysis time:
```python
st.session_state['last_filename'] = uploaded_file.name if uploaded_file else "PastedScript"
# Then in export:
title = st.session_state.get('last_filename', 'Script')
```

---

### C5 · Error Messages Are Too Technical for End Users
**File:** `app/streamlit_app.py` and `scriptpulse/pipeline/runner.py`
**Problem:** Errors like `"Analysis failed: 'NoneType' object has no attribute 'get'"` or `"Could not detect any scenes"` are shown verbatim to users. Real users don't know what a "scene" means in the technical sense, and raw Python tracebacks are alarming.
**Fix:** Map known exception types to user-friendly messages:
```python
USER_FRIENDLY_ERRORS = {
    "could not detect any scenes": (
        "ScriptPulse couldn't find scene headings in your script. "
        "Make sure scenes start with INT. or EXT. (e.g., 'INT. COFFEE SHOP - DAY'). "
        "You can also try pasting just one scene to test."
    ),
    "requires more text": (
        "Your script is too short for analysis. "
        "Please upload at least 2-3 scenes for meaningful results."
    ),
}
```
Show a collapsible "Technical Details" expander with the raw error for debugging.

---

### C6 · AI Summary Caching Uses Wrong Cache Key
**File:** `app/streamlit_app.py` and `app/views/writer_view.py`
**Problem:** The code clears `ai_summary_cache` and all keys starting with `ai_summary_` on every new analysis. However, `generate_ai_summary()` is called with a `lens` parameter, but the cache key doesn't include `lens`. If a user runs analysis, switches from "Story Editor" to "Studio Executive", and clicks re-analyze, they may see the Story Editor summary under the Studio Executive tab.
**Fix:** Include lens in every AI summary cache key:
```python
cache_key = f"ai_summary_{lens}_{hash(str(report.get('meta', {}).get('run_id', '')))}"
```

---

### C7 · Genre List in UI Doesn't Match `DynamicsAgent` Genre Priors
**File:** `app/streamlit_app.py` → genre selectbox
**Problem:** The UI offers `["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"]`. But `DynamicsAgent.GENRE_PRIORS` is missing `Avant-Garde`. Also the UI uses `"Sci-Fi"` but the prior key is `"sci-fi"` — while `.lower()` handles this, `"Sci-Fi"` sent to `InterpretationAgent` is compared against genre strings like `"drama"` in lowercase checks, creating inconsistency.
**Fix:** Normalize genre to lowercase immediately after selection:
```python
genre_raw = col1.selectbox("Genre", ["Drama", "Action", "Thriller", "Horror", "Comedy", "Sci-Fi", "Romance", "Fantasy", "Avant-Garde"])
genre = genre_raw.lower().replace("-", "-")  # Preserve hyphens, force lowercase
```
And ensure all downstream genre comparisons use lowercase.

---

### C8 · No Loading State When AI Summary Is Being Generated
**File:** `app/views/writer_view.py`
**Problem:** The `generate_ai_summary()` and `generate_section_insight()` calls happen inside rendering functions with no loading indicator. The UI appears frozen for 2-8 seconds while waiting for LLM API responses. Users assume the page has crashed.
**Fix:** Wrap all LLM calls in `st.spinner()`:
```python
with st.spinner("Generating AI insight..."):
    summary, err = generate_ai_summary(report, lens=lens)
```
Also add a timeout: if the API call takes > 10 seconds, show a fallback static message rather than hanging.

---

### C9 · Character Arc Labels Can Show "Flat Arc ⚠️" for Correctly-Written Characters
**File:** `scriptpulse/agents/writer_agent.py` → `_build_character_arcs()`
**Problem:** Characters who appear in only a few scenes (bit parts, one-scene wonders) are labeled "Flat Arc ⚠️" because their delta across the script is minimal. This is misleading — a character in 2 scenes has no arc by definition, not because the writing is bad.
**Fix:** Filter character arcs to only label characters with `line_count >= 10` as having meaningful arcs. For characters with fewer lines, display "Supporting Role" or simply omit them from arc analysis:
```python
if line_count < 10:
    arc_label = "Supporting Role"
    arc_note = "Appears in too few scenes for arc analysis."
```

---

### C10 · Diagnosis Messages Truncated to 15 Items Without Prioritization
**File:** `scriptpulse/agents/writer_agent.py` → `analyze()`
**Problem:** `all_diagnostics[:15]` truncates the diagnostic list arbitrarily. If there are 12 green/positive notes and 10 critical red issues, the red issues may be cut off after position 15. The sorting is alphabetical (for determinism), not by severity. Users miss critical feedback.
**Fix:** Sort diagnostics by severity before truncating:
```python
severity_order = {'🔴': 0, '🟠': 1, '🟡': 2, '🔵': 3, '💡': 4, '🟢': 5, '✨': 6, '🤫': 7}
def severity_key(d):
    for emoji, rank in severity_order.items():
        if emoji in d:
            return rank
    return 99
all_diagnostics_sorted = sorted(all_diagnostics, key=severity_key)
final_output['writer_intelligence']['narrative_diagnosis'] = all_diagnostics_sorted[:15]
```

---

## SECTION D — SECURITY & ROBUSTNESS

### D1 · `.env` File Committed to Repository
**File:** `ScriptPulse Project/.env`
**Problem:** The `.env` file is present in the repository root and appears in the ZIP. If this file contains real API keys (Groq, Gemini, HF tokens), they are exposed to anyone with repo access. The `.gitignore` only lists `.env` — but the file was already committed.
**Fix:**
1. Immediately rotate all API keys in `.env`.
2. Add `.env` to `.gitignore` and run `git rm --cached .env`.
3. Document in `README.md` that users must create their own `.env` from `.env.example`.
4. Create a `.env.example` with placeholder values:
```
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_gemini_key_here
HF_TOKEN=your_huggingface_token_here
```

---

### D2 · XML Parser Is Vulnerable to XXE (Incomplete Mitigation)
**File:** `scriptpulse/agents/structure_agent.py` → `ImporterAgent.parse_fdx()`
**Problem:** The current mitigation checks for `<!DOCTYPE` and `<!ENTITY` in raw string form, but this can be bypassed with whitespace variants (`<!  DOCTYPE`) or encoding tricks. The standard Python `xml.etree.ElementTree` is known to be vulnerable to "Billion Laughs" attacks (exponential entity expansion) despite the string check.
**Fix:** Replace `xml.etree.ElementTree` with `defusedxml`:
```python
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    # Log warning: defusedxml not installed, FDX parsing may be vulnerable
```
Add `defusedxml>=0.7.1` to `requirements.txt`.

---

### D3 · `st.secrets.toml` Contains Placeholder Credentials
**File:** `ScriptPulse Project/.streamlit/secrets.toml`
**Problem:** This file is committed to the repo and should never contain real or placeholder API key patterns. Even placeholder values like `GROQ_API_KEY = "your-key-here"` train bad habits and may accidentally contain real keys if a developer edits in-place.
**Fix:** Replace `secrets.toml` with `secrets.toml.example`. Add real `secrets.toml` to `.gitignore`. Reference Streamlit's official secret management docs in `README.md`.

---

### D4 · No Rate Limiting or Input Sanitization on Script Text
**File:** `app/streamlit_app.py` and `scriptpulse/pipeline/runner.py`
**Problem:** There is no upper bound on the size of pasted text. A malicious user could paste 10MB of text, causing the pipeline to consume massive CPU/memory and timeout or crash the server.
**Fix:**
```python
MAX_CHARS = 500_000  # ~500KB, approx 400-page script
if len(script_input) > MAX_CHARS:
    st.error(f"Script too large ({len(script_input):,} chars). Maximum is {MAX_CHARS:,} characters (~400 pages).")
    st.stop()
```
Also sanitize the input: strip null bytes, replace control characters.

---

### D5 · LLM Prompt Contains Raw Script Diagnostic Data Without Sanitization
**File:** `scriptpulse/reporters/llm_translator.py` → `generate_ai_summary()`
**Problem:** `json.dumps(data_payload)` is sent directly to LLM APIs. If `narrative_diagnosis` contains user-supplied text snippets (which it does — diagnostic messages include `snippet` content from the script), this is a prompt injection vector. A malicious script could include text designed to override the system prompt.
**Fix:** Strip or escape diagnostic message snippets before including in LLM payload:
```python
def _sanitize_for_llm(text):
    """Remove content that could act as prompt injection."""
    # Remove anything that looks like an instruction
    text = re.sub(r'(?i)(ignore (previous|above)|system:|you are|act as)', '[REDACTED]', text)
    return text[:500]  # Hard cap per item

safe_diagnostics = [_sanitize_for_llm(d) for d in data_payload['pacing_issues']]
```

---

## SECTION E — CODE QUALITY & MAINTAINABILITY

### E1 · `PipelineOutput` Pydantic Schema Is Never Validated Against Actual Output
**File:** `scriptpulse/schemas/models.py` and `scriptpulse/pipeline/runner.py`
**Problem:** `PipelineOutput` is a well-designed Pydantic model, but `runner.py` never instantiates it. The pipeline returns a raw `dict`. All the type safety and validation Pydantic provides is completely unused. Bugs like missing keys (A3) would be caught automatically if validation was enforced.
**Fix:** At the end of `run_pipeline()`, validate the report:
```python
from scriptpulse.schemas.models import PipelineOutput
try:
    validated = PipelineOutput(**report)
    return validated.model_dump()
except Exception as e:
    logger.warning(f"Schema validation warning: {e}")
    return report  # Graceful degradation
```

---

### E2 · `health_check()` Always Returns `True` — Not a Real Health Check
**File:** `scriptpulse/pipeline/runner.py` → `health_check()`
**Problem:** The `health_check()` function hardcodes all statuses as `True` and `'healthy'`. It doesn't actually test whether agents can be imported, models loaded, or config files parsed. A broken installation will still return a healthy status.
**Fix:** Make `health_check()` actually test:
```python
def health_check():
    status = {'status': 'healthy', 'agents': {}, 'config_files': {}}
    # Test agent imports
    try:
        from scriptpulse.agents.structure_agent import ParsingAgent
        ParsingAgent()
        status['agents']['ParsingAgent'] = 'healthy'
    except Exception as e:
        status['agents']['ParsingAgent'] = f'ERROR: {e}'
        status['status'] = 'degraded'
    # Test config files
    import os
    for fname in ['config/genre_priors.json', 'config/required_model_versions.json']:
        status['config_files'][fname] = os.path.exists(fname)
    return status
```

---

### E3 · `random` Used in Writer Agent Diagnoses — Results Are Non-Deterministic
**File:** `scriptpulse/agents/writer_agent.py`
**Problem:** `import random` is present, and some diagnostic generation methods use random selection. For a tool claiming "research-grade determinism" (v15.0 Gold), non-deterministic output is a serious credibility problem. Running the same script twice can produce different ScriptPulse Scores.
**Fix:** Remove all `random` usage from production diagnostic paths. If variation is needed for creative provocations, seed with a deterministic value derived from script content:
```python
import hashlib
seed = int(hashlib.md5(script_content[:100].encode()).hexdigest(), 16) % (2**32)
rng = random.Random(seed)  # Seeded, deterministic
```

---

### E4 · `ParsingAgent.predict_line()` ML Path Is Effectively Dead Code
**File:** `scriptpulse/agents/structure_agent.py`
**Problem:** The `predict_line()` method has comment `# 3. ML Inference (Skipped if mock or high confidence in heuristic)` but the ML path is never actually reached — the heuristic paths all `return` before the ML section. The `self.classifier` is loaded but never called for line classification. This means the "Transformer-Augmented" claim in the README is incorrect for line-level parsing — it's purely heuristic.
**Fix:** Either:
1. Wire the ML classifier into the fallback path (when heuristics return `"A"` with ambiguity), OR
2. Remove the ML loading from `ParsingAgent.__init__()` to save memory (the zero-shot classifier is expensive and unused here).

Recommended: Option 2 unless you plan to implement ML-assisted parsing. Update the README to accurately reflect this.

---

### E5 · `model_manager.py` Uses a Mutable Singleton with No Thread Safety
**File:** `scriptpulse/utils/model_manager.py` → `ModelManager`
**Problem:** The singleton pattern (`_instance`) has no thread locking. In a Streamlit Cloud deployment, multiple users triggering analysis simultaneously can cause a race condition on `_initialized` and `_loaded_models`, leading to double-loading of models or partial initialization.
**Fix:**
```python
import threading
_lock = threading.Lock()

def __new__(cls):
    with _lock:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance.init_config()
    return cls._instance
```

---

### E6 · Requirements Are Unpinned — Reproducibility Cannot Be Guaranteed
**File:** `requirements.txt`
**Problem:** All requirements use `>=` version constraints, not pinned versions. The `config/reproducibility.lock` file exists but appears to be a placeholder. A `pip install -r requirements.txt` six months from now may pull breaking changes (e.g., `google-generativeai` breaking API changes, `plotly` chart API changes).
**Fix:** Generate a `requirements-lock.txt` with fully pinned versions:
```bash
pip freeze > requirements-lock.txt
```
Update CI/CD and deployment to use `pip install -r requirements-lock.txt`. Keep `requirements.txt` as the human-readable specification, `requirements-lock.txt` as the deployment spec.

---

### E7 · `interpretation_agent.py` Uses `random` Import but `random` Is Never Used
**File:** `scriptpulse/agents/interpretation_agent.py`
**Problem:** `import random` is at the top of the file but no function in the module calls it. Dead imports slow startup and confuse readers.
**Fix:** Remove `import random` from `interpretation_agent.py`. Run `autoflake` across the codebase to catch all unused imports.

---

## SECTION F — FEATURE GAPS (Missing for Production Readiness)

### F1 · No PDF Text Extraction Fallback When PyPDF2 Returns Empty Strings
**File:** `app/streamlit_app.py`
**Problem:** `PyPDF2.PdfReader` returns empty strings for scanned/image-based PDFs. The current code does `p.extract_text() or ""` which silently produces an empty script, then fails at the minimum-length check with a confusing error. Users have no way to know their PDF is image-based.
**Fix:** After extraction, check total extracted text length. If < 100 chars despite multiple pages, show:
```
"This PDF appears to be scanned (image-based). PyPDF2 cannot read it.
Please export your script as a text-based PDF from your screenwriting software,
or paste the text directly in the 'Paste Text' tab."
```
Optionally add `pdfminer.six` as a fallback extractor (better with complex PDFs).

---

### F2 · No Analysis History / Session Comparison
**File:** `app/streamlit_app.py` and `app/views/writer_view.py`
**Problem:** Every new analysis overwrites `st.session_state['last_report']`. Users cannot compare their current draft against a previous version. Professional script coverage tools always offer version comparison. This is a major missing feature for real writers.
**Fix:** Maintain a list of up to 3 previous analyses in session state:
```python
if 'analysis_history' not in st.session_state:
    st.session_state['analysis_history'] = []

# After successful analysis:
st.session_state['analysis_history'].append({
    'report': report,
    'filename': title,
    'timestamp': time.strftime('%H:%M'),
    'score': report.get('writer_intelligence', {}).get('structural_dashboard', {}).get('scriptpulse_score', 0)
})
st.session_state['analysis_history'] = st.session_state['analysis_history'][-3:]  # Keep last 3
```
Add a sidebar section showing "Previous Analyses" with score and filename.

---

### F3 · No User-Facing Explanation of What Each Score/Metric Means
**File:** `app/views/writer_view.py`
**Problem:** Scores like "Page-Turner Index: 67" and "Market Readiness: 54" are displayed with no explanation of what 67 means, what the scale is, what a good score looks like, or how it's calculated. Professional users won't trust a black-box number. Writers don't know if 67 is good or bad.
**Fix:** Add an expandable `st.expander("ℹ️ How is this calculated?")` below each major metric card with:
- What the metric measures
- The scale (0–100)
- Typical ranges: `< 40 = Needs Work | 40–70 = Average | > 70 = Strong`
- One-line method description: e.g., "Page-Turner Index = momentum of scene-ending tension relative to genre benchmarks"

---

### F4 · No Graceful Degradation When ALL API Keys Are Missing
**File:** `app/streamlit_app.py` and `scriptpulse/reporters/llm_translator.py`
**Problem:** When no API keys are configured, the AI Summary section either shows an error or silently hides. There's no explanation to the user that the core analysis still works and only the LLM-generated commentary is unavailable.
**Fix:** Show a clear info banner when no keys are detected:
```python
keys = _get_api_config()
if not any(keys.values()):
    st.info(
        "💡 **AI Commentary Disabled** — Your structural analysis is complete above. "
        "To enable AI-generated narrative insights, add a Groq or Gemini API key in Settings (sidebar)."
    )
```
Make this check at page load, not only when the user clicks a button.

---

### F5 · Reports Have No Version Stamp or Reproducibility Info
**File:** `scriptpulse/reporters/writer_report.py` and `scriptpulse/reporters/studio_report.py`
**Problem:** Downloaded reports contain analysis results but no metadata: which engine version produced them, what genre/lens was selected, when they were generated. A writer receiving coverage from a colleague can't verify which version of their script was analyzed.
**Fix:** Add a header block to all exported reports:
```markdown
---
**ScriptPulse Analysis Report**
Script: {title}
Analyzed: {datetime}
Engine: v15.0 Gold
Genre: {genre} | Perspective: {lens}
ScriptPulse Score: {score}/100 | Confidence: {confidence_level}
Run ID: {run_id}
---
```

---

### F6 · `BeatAgent` Is Defined but Never Called
**File:** `scriptpulse/agents/structure_agent.py` → `BeatAgent` class
**Problem:** `BeatAgent` contains a complete `subdivide_into_beats()` implementation but is never instantiated or called anywhere in `runner.py` or any agent. This means the "beats" feature advertised in the README is completely absent at runtime.
**Fix:** Either:
1. Wire `BeatAgent` into the pipeline after `SegmentationAgent` (adds beat-level granularity to temporal trace), OR
2. Remove `BeatAgent` from the codebase to reduce confusion, and update README to remove mentions of "beat analysis".

---

### F7 · `experimental_agent.py` Is Empty/Placeholder
**File:** `scriptpulse/agents/experimental_agent.py`
**Problem:** This file exists in the agents directory and is imported or referenced in module init, but contains only a stub or placeholder class. This may cause import errors in some environments and creates confusion about what the system actually does.
**Fix:** Either implement the experimental agent or remove the file and remove it from `scriptpulse/agents/__init__.py`.

---

## SECTION G — TESTING & OBSERVABILITY

### G1 · Tests Reference Different File Paths Than Production Code
**File:** `tests/unit/test_edge_cases.py`
**Problem:** The test traceback shows `runner.run_pipeline(script, cpu_safe_mode=True, **kwargs)` — but the production `runner.run_pipeline()` signature in the current codebase does NOT accept `cpu_safe_mode` as a named parameter. The tests are testing a different version of the API than what ships.
**Fix:** Reconcile the test signature with the current production API. If `cpu_safe_mode` was removed, update tests. If it should still exist, re-add it to `runner.run_pipeline()`:
```python
def run_pipeline(script_content, genre='drama', story_framework='3_act', cpu_safe_mode=False, **kwargs):
    if cpu_safe_mode:
        os.environ['SCRIPTPULSE_HEURISTICS_ONLY'] = '1'
```

---

### G2 · No Smoke Test for the Streamlit App Entry Point
**File:** `tests/` directory
**Problem:** All tests exercise the Python pipeline directly via `runner.run_pipeline()`. None test that the Streamlit app starts without error, that the sidebar renders, or that the upload flow works end-to-end. A broken import in `app/streamlit_app.py` would not be caught by any existing test.
**Fix:** Add a smoke test using `streamlit.testing.v1`:
```python
from streamlit.testing.v1 import AppTest
def test_app_loads():
    at = AppTest.from_file("app/streamlit_app.py")
    at.run(timeout=10)
    assert not at.exception
```

---

### G3 · No Telemetry for Pipeline Stage Failures
**File:** `scriptpulse/pipeline/runner.py`
**Problem:** If `EncodingAgent.run()` partially fails (some scenes error, some succeed), the error is silently swallowed and partial results are returned. Users get analysis with missing data and no indication anything went wrong. The `telemetry` dict only tracks timing, not success/failure per stage.
**Fix:** Add error tracking to telemetry:
```python
telemetry['stages']['feature_extraction_errors'] = []
try:
    perceptual_features = perceptor.run(...)
except Exception as e:
    telemetry['stages']['feature_extraction_errors'].append(str(e))
    perceptual_features = []  # safe fallback
```
Surface any stage errors as warnings in the UI.

---

### G4 · No Regression Test Against Known Scripts
**File:** `tests/integration/calibration/benchmark_scripts/`
**Problem:** The `benchmark_scripts/` directory contains 70+ script samples (short/medium/long across genres), but there's no test that runs the pipeline on these and checks that the output falls within expected score ranges. A regression breaking thriller detection would not be caught.
**Fix:** Add a regression test:
```python
def test_benchmark_scores_within_range():
    for script_file in Path("tests/integration/calibration/benchmark_scripts").glob("*.txt"):
        genre = script_file.stem.split("_")[-1]  # e.g. "thriller"
        text = script_file.read_text()
        result = runner.run_pipeline(text, genre=genre)
        score = result['writer_intelligence']['structural_dashboard']['scriptpulse_score']
        assert 20 <= score <= 95, f"{script_file.name}: score {score} out of expected range"
```

---

## SECTION H — DEPLOYMENT & INFRASTRUCTURE

### H1 · `streamlit_app.py` in Root Is a Stub That Redirects — Confusing
**File:** `ScriptPulse Project/streamlit_app.py` (root level)
**Problem:** There is a `streamlit_app.py` at the project root AND a full `app/streamlit_app.py`. The root-level file is a 5-line stub. Streamlit Cloud and README both reference `streamlit run streamlit_app.py` but this may load the wrong file depending on working directory.
**Fix:** Either consolidate to one entry point, or make the root stub explicitly redirect:
```python
# streamlit_app.py (root) — clean delegation
import subprocess, sys
subprocess.run([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py"])
```
Update `README.md` to clarify `streamlit run app/streamlit_app.py` is the correct command.

---

### H2 · Missing `__init__.py` Not Checked in `scriptpulse/prompts/` and `scriptpulse/reporters/`
**File:** `scriptpulse/prompts/__init__.py` and `scriptpulse/reporters/__init__.py`
**Problem:** These `__init__.py` files exist but are empty. If a new agent tries to import from `scriptpulse.prompts`, it may work locally (Python finds the directory) but fail in some packaging or cloud environments.
**Fix:** Add explicit exports in each `__init__.py`:
```python
# scriptpulse/reporters/__init__.py
from . import writer_report, studio_report, print_summary, llm_translator
__all__ = ['writer_report', 'studio_report', 'print_summary', 'llm_translator']
```

---

### H3 · No `pyproject.toml` or `setup.py` — Package Not Installable
**File:** Project root
**Problem:** The project has no `pyproject.toml` or `setup.py`, meaning `scriptpulse` cannot be installed as a proper Python package. This limits deployment options and forces path-manipulation hacks (`sys.path.append(ROOT_DIR)`) that are already present in the Streamlit app.
**Fix:** Add a minimal `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "scriptpulse"
version = "15.0.0"
requires-python = ">=3.9"

[tool.setuptools.packages.find]
where = ["."]
include = ["scriptpulse*", "app*"]
```

---

## PRIORITY MATRIX (Quick Reference)

| Priority | Issue | Section | Effort |
|----------|-------|---------|--------|
| 🔴 P0 — Ship Blocker | A1: NoneType crash on non-standard scripts | A | 30 min |
| 🔴 P0 — Ship Blocker | A6: FDX files always fail (wrong import path) | A | 15 min |
| 🔴 P0 — Ship Blocker | A7: HTML in ValueError (XSS + broken UX) | A | 10 min |
| 🔴 P0 — Ship Blocker | D1: .env committed to repo (key exposure) | D | 20 min |
| 🟠 P1 — High | A2: Missing run_id/agent_timings (test fail) | A | 20 min |
| 🟠 P1 — High | A3: Missing standard output keys (test fail) | A | 20 min |
| 🟠 P1 — High | A4: Violence override kills positive scenes | A | 45 min |
| 🟠 P1 — High | A5: Sentiment override double-penalizes | A | 20 min |
| 🟠 P1 — High | B1: Score formula may use wrong dict key | B | 10 min |
| 🟠 P1 — High | B2: Confidence scorer never called | B | 15 min |
| 🟠 P1 — High | C1: Confidence level never shown to user | C | 30 min |
| 🟠 P1 — High | D2: XXE vulnerability in FDX parser | D | 20 min |
| 🟡 P2 — Medium | B4: Hyphenated character name splitting | B | 30 min |
| 🟡 P2 — Medium | B5: Hardcoded act structure boundaries | B | 2 hrs |
| 🟡 P2 — Medium | B7: Genre key mismatch (Avant-Garde missing) | B | 15 min |
| 🟡 P2 — Medium | B8: location_change always False | B | 45 min |
| 🟡 P2 — Medium | C2: No input validation on paste/PDF | C | 1 hr |
| 🟡 P2 — Medium | C3: Progress bar stalls at 20% | C | 1 hr |
| 🟡 P2 — Medium | C5: Technical error messages shown to users | C | 1 hr |
| 🟡 P2 — Medium | C10: Diagnostics truncated without severity sort | C | 30 min |
| 🟡 P2 — Medium | D4: No max input size limit | D | 30 min |
| 🟡 P2 — Medium | E3: random usage breaks determinism | E | 1 hr |
| 🟡 P2 — Medium | G1: Tests use different API signature | G | 1 hr |
| 🔵 P3 — Polish | B6: Entropy not normalized by scene length | B | 30 min |
| 🔵 P3 — Polish | B9: Dialogue ratio benchmarks inaccurate | B | 30 min |
| 🔵 P3 — Polish | C6: AI cache key doesn't include lens | C | 15 min |
| 🔵 P3 — Polish | C7: Genre case normalization inconsistent | C | 15 min |
| 🔵 P3 — Polish | C8: No loading state for AI summary | C | 30 min |
| 🔵 P3 — Polish | C9: "Flat Arc" shown for minor characters | C | 30 min |
| 🔵 P3 — Polish | D5: LLM prompt injection from script text | D | 1 hr |
| 🔵 P3 — Polish | E1: Pydantic schema never validated | E | 30 min |
| 🔵 P3 — Polish | E2: health_check() is fake | E | 45 min |
| 🔵 P3 — Polish | E4: ML path dead in ParsingAgent | E | 2 hrs |
| 🔵 P3 — Polish | E6: Unpinned requirements | E | 30 min |
| 🟢 P4 — Future | F1: No PDF fallback for image-based PDFs | F | 2 hrs |
| 🟢 P4 — Future | F2: No analysis history/comparison | F | 4 hrs |
| 🟢 P4 — Future | F3: No metric explanations | F | 2 hrs |
| 🟢 P4 — Future | F4: No graceful API-key-missing state | F | 1 hr |
| 🟢 P4 — Future | F5: Reports have no version stamp | F | 1 hr |
| 🟢 P4 — Future | F6: BeatAgent never called | F | 4 hrs |
| 🟢 P4 — Future | G2: No Streamlit smoke test | G | 2 hrs |
| 🟢 P4 — Future | G3: No per-stage error telemetry | G | 2 hrs |
| 🟢 P4 — Future | G4: No regression tests against benchmarks | G | 3 hrs |
| 🟢 P4 — Future | H1: Dual streamlit_app.py confusion | H | 30 min |
| 🟢 P4 — Future | H3: No pyproject.toml | H | 1 hr |

---

## IMPLEMENTATION ORDER RECOMMENDATION

**Sprint 1 (Day 1–2): Fix Everything That Crashes or Leaks**
→ A1, A2, A3, A6, A7, D1, D2, D3

**Sprint 2 (Day 3–5): Fix Accuracy Problems**
→ A4, A5, B1, B2, B7, B8, B9, C10, E3

**Sprint 3 (Week 2): Fix Trust & UX**
→ C1, C2, C3, C5, C6, C7, C8, C9, B4, B5, B6, D4, D5

**Sprint 4 (Week 3): Add Missing Production Features**
→ F1, F3, F4, F5, G1, G2, G3, E1, E2, E4, E6, H1

**Sprint 5 (Month 2): Major Feature Work**
→ F2, F6, G4, B10, H3

---

*Generated from full codebase review of ScriptPulse v15.0 Gold.*
*Total issues identified: 47 across 8 categories.*
