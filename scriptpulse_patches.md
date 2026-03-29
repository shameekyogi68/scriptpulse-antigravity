# ScriptPulse — All Bug Patches

Each patch is a drop-in replacement. File and line numbers are shown for every change.

---

## PATCH 1 — `writer_agent.py` line 1672
**Fix: Wrong key for dialogue ratio in ScriptPulse score**

```python
# BEFORE (line 1672):
dr = dashboard.get('dialogue_ratio', {})

# AFTER:
dr = dashboard.get('dialogue_action_ratio', {})
```

---

## PATCH 2 — `writer_agent.py` line 1582
**Fix: `loc_count` always 0 in market readiness**

```python
# BEFORE (line 1582):
loc_count = len(d.get('location_profile', []))

# AFTER:
loc_count = d.get('location_profile', {}).get('unique_locations', 0)
```

---

## PATCH 3 — `writer_agent.py` line 195–197
**Fix: `_diagnose_voice` always fires (Same Voice Syndrome false positive)**

The voice fingerprints never contain `complexity`, `positivity`, or `punctuation_rate`,
so the std-dev check always passes. Replace the entire `_diagnose_voice` method:

```python
def _diagnose_voice(self, voice_fingerprints):
    import statistics
    assessments = []
    if not voice_fingerprints or len(voice_fingerprints) < 2:
        return []

    top_chars = sorted(
        voice_fingerprints.items(),
        key=lambda x: x[1].get('line_count', 0),
        reverse=True
    )[:5]

    valid_chars = [c for c in top_chars if c[1].get('line_count', 0) >= 10]
    if len(valid_chars) < 2:
        return []

    # Only use fields that are actually populated in voice_fingerprints
    sentiments = [c[1].get('sentiment', 0) for c in valid_chars]
    agencies   = [c[1].get('agency', 0)    for c in valid_chars]

    std_sent   = statistics.stdev(sentiments) if len(sentiments) > 1 else 1.0
    std_agency = statistics.stdev(agencies)   if len(agencies)   > 1 else 1.0

    # Only flag if both sentiment AND agency distributions are nearly identical
    # (i.e. all characters feel the same AND exert the same power level)
    if std_sent < 0.08 and std_agency < 0.08:
        names = [c[0] for c in valid_chars[:3]]
        assessments.append(
            f"🔴 **Same Voice Syndrome**: The primary characters ({', '.join(names)}) "
            f"share nearly identical dialogue textures. Consider varying sentence "
            f"structures or punctuation habits to distinguish them."
        )

    return assessments
```

> **Why this works:** sentiment and agency ARE populated (by `perception_agent.py`
> and the ethics agent merge in `runner.py`). The thresholds are tighter (0.08)
> to avoid false positives on genres like Crime Drama where tonal unity is intentional.

---

## PATCH 4 — `writer_agent.py` `_build_location_profile` (line 1022–1062)
**Fix: Location overcounting (155 → realistic number)**

The runner already strips time-of-day from `location_data.location` (lines 3b in runner.py),
but the `_build_location_profile` method also needs to normalise the raw string before
counting, as some headings arrive without going through the runner's injector.

Replace the top of `_build_location_profile`:

```python
def _build_location_profile(self, trace):
    import re as _re
    location_counts = {}
    int_count = 0
    ext_count = 0

    for s in trace:
        loc_data = s.get('location_data', {})
        loc = loc_data.get('location', 'UNKNOWN')

        # Secondary normalisation: strip any residual time-of-day suffixes
        # (runner.py does this too, but belt-and-suspenders for edge cases)
        loc = _re.sub(
            r'\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|'
            r'CONTINUOUS|LATER|SAME|MOMENTS?\s+LATER).*$',
            '', loc, flags=_re.IGNORECASE
        ).strip()
        if not loc:
            loc = 'UNKNOWN'

        interior = loc_data.get('interior')
        location_counts[loc] = location_counts.get(loc, 0) + 1
        if interior == 'INT':
            int_count += 1
        elif interior == 'EXT':
            ext_count += 1

    total = max(1, len(trace))
    sorted_locs = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    top_loc, top_count = sorted_locs[0] if sorted_locs else ('UNKNOWN', 0)
    top_ratio = top_count / total

    warning = None
    if top_ratio > 0.6 and len(sorted_locs) < 5:
        warning = (
            f"{round(top_ratio * 100)}% of scenes are set in '{top_loc}'. "
            f"Only {len(sorted_locs)} unique location(s) total. "
            f"Consider varying the physical world to add visual range."
        )

    return {
        'unique_locations': len(sorted_locs),
        'top_location': top_loc,
        'top_location_ratio': round(top_ratio, 3),
        'int_scenes': int_count,
        'ext_scenes': ext_count,
        'int_ext_ratio': round(int_count / max(1, int_count + ext_count), 3),
        'location_warning': warning,
        'all_locations': dict(sorted_locs[:10])
    }
```

---

## PATCH 5 — `perception_agent.py` `_extract_narrative_metadata` (agency scoring)
**Fix: Hagen > Michael > Don Corleone — wrong agency ordering**

Find the agency calculation block (~line 394) and apply these changes:

```python
# BEFORE:
agency_inc = 0.1  # Base participation
if is_command: agency_inc += 0.5
elif is_question: agency_inc += 0.3   # too high — questions ≠ power

agency_inc += (proactive_count * 0.6)

# AFTER:
agency_inc = 0.1  # Base participation
if is_command: agency_inc += 0.7      # raised: commands are strong power signals
elif is_question: agency_inc += 0.1   # lowered: questions are investigative, not dominant

agency_inc += (proactive_count * 0.6)
```

Also expand the proactive lexicon (~line 363) to capture power characters who speak
in fewer but more decisive lines:

```python
# BEFORE:
proactive_lexicon = {'go', 'do', 'will', 'must', 'shall', 'stop', 'done',
                     'kill', 'give', 'take', 'enough', 'order', 'clear',
                     'business', 'family'}

# AFTER:
proactive_lexicon = {'go', 'do', 'will', 'must', 'shall', 'stop', 'done',
                     'kill', 'give', 'take', 'enough', 'order', 'clear',
                     'business', 'family',
                     # Power vocabulary for Crime Drama / Drama patriarchs:
                     'offer', 'refuse', 'respect', 'decide', 'arrange',
                     'settle', 'deal', 'demand', 'insist', 'command',
                     'forbid', 'allow', 'never', 'always', 'swear'}
```

---

## PATCH 6 — `structure_agent.py` line 195
**Fix: Action lines ending with `:` mislabelled as transitions**

```python
# BEFORE (line 195):
if line_upper.endswith(':'): return 'M'  # Broad transition check

# AFTER:
# Only treat as transition if the WHOLE line is uppercase and short
# (true transitions like "CUT TO:" are all-caps and brief)
if line_upper.endswith(':') and line_upper == line and len(line) < 20:
    return 'M'
```

---

## PATCH 7 — `structure_agent.py` line 280–285
**Fix: Segmentation fires on `M` tags, inflating scene count**

```python
# BEFORE (lines 280–285):
def detect_boundaries(self, parsed_lines):
    boundaries = [(0, 1.0)]
    for i, line_data in enumerate(parsed_lines):
        if i == 0: continue
        tag = line_data['tag']
        confidence = 0.0
        if tag == 'S': confidence = 0.9
        elif tag == 'M': confidence = 0.4   # ← causes micro-scenes at every CUT TO:

        if confidence > 0.3:
            boundaries.append((i, confidence))
    return boundaries

# AFTER:
def detect_boundaries(self, parsed_lines):
    boundaries = [(0, 1.0)]
    for i, line_data in enumerate(parsed_lines):
        if i == 0: continue
        tag = line_data['tag']
        confidence = 0.0
        if tag == 'S': confidence = 0.9
        # Removed: M-tag boundary — transitions belong to the preceding scene

        if confidence > 0.3:
            boundaries.append((i, confidence))
    return boundaries
```

---

## PATCH 8 — `structure_agent.py` line 132
**Fix: ParsingAgent uses wrong model name, causing HARD FAIL when ML is enabled**

```python
# BEFORE (line 132):
class ParsingAgent:
    def __init__(self, use_ml=True, model_name="valhalla/distilbart-mnli-12-3"):
        ...
        if use_ml:
            self.classifier = manager.get_pipeline("zero-shot-classification", model_name)

# AFTER:
class ParsingAgent:
    def __init__(self, use_ml=True):
        ...
        if use_ml:
            self.classifier = manager.get_zero_shot()  # uses registered model from required_model_versions.json
```

Same fix applies to `SiliconStanislavskiAgent.__init__` in `experimental_agent.py`:

```python
# BEFORE (experimental_agent.py line 19-21):
def __init__(self, model_name="valhalla/distilbart-mnli-12-3"):
    ...
    self.classifier = manager.get_pipeline("zero-shot-classification", model_name)

# AFTER:
def __init__(self):
    ...
    self.classifier = manager.get_zero_shot()
```

---

## PATCH 9 — `governance.py` + `trust_lock.py`
**Fix: `PolicyViolationError` doesn't exist — hard crash on deployment**

Add the missing exception class to `governance.py`:

```python
# Add near the top of governance.py, after the MAX_CHARS constant:

class PolicyViolationError(ValueError):
    """Raised when input violates a governance policy (forbidden terms, etc.)."""
    pass
```

Then update `validate_request` in `governance.py` to raise it for forbidden terms
(currently it only raises `ValueError` for structural issues):

```python
FORBIDDEN_TERMS = {"rank 1 to 10", "grade this", "hiring recommendation"}

def validate_request(text_data: str):
    if not isinstance(text_data, str):
        raise ValueError("Governance Audit Failed: Input must be a valid UTF-8 string.")
    if len(text_data) > MAX_CHARS:
        raise ValueError(f"Governance Audit Failed: Input exceeds {MAX_CHARS} characters.")
    if '\x00' in text_data:
        raise ValueError("Governance Audit Failed: Binary payload or null-bytes detected.")

    # Forbidden intent check (triggers trust_lock verification)
    lower = text_data.lower()
    for term in FORBIDDEN_TERMS:
        if term in lower:
            raise PolicyViolationError(
                f"Governance Audit Failed: Forbidden term detected — '{term}'."
            )

    return True
```

No changes needed in `trust_lock.py` — it already catches `governance.PolicyViolationError` correctly.

---

## PATCH 10 — `perception_agent.py` runtime estimate
**Fix: Action lines underweighted, causing ~14 min runtime underestimate**

```python
# BEFORE (lines 143–147):
action_seconds = action_words * 0.3
dialogue_seconds = dialogue_words * 0.35

# AFTER:
# Industry standard: ~200 WPM spoken dialogue, but action descriptions
# represent screen time at roughly 2–3x the reading rate
action_seconds = action_words * 0.7   # ~85 words/min of screen time
dialogue_seconds = dialogue_words * 0.33  # ~180 WPM spoken
```

---

## PATCH 11 — `writer_agent.py` `_diagnose_redundant_scenes` (line 805)
**Fix: O(n²) performance on large scripts — add scene-window limit**

```python
# Add this guard inside the double loop, after line 806:
for i in range(len(scene_data)):
    for j in range(i + 1, min(i + 40, len(scene_data))):  # ← limit window to 40 scenes
        ...
```

---

## PATCH 12 — `writer_agent.py` `_diagnose_neglected_characters` (line 1298)
**Fix: O(n²) `trace.index(s)` inside a loop**

```python
# BEFORE (line 1298):
last_appearance_idx = max([trace.index(s) for s in char_timeline]) if char_timeline else 0

# AFTER — build an index map once, outside all loops (add before the outer for loop at line ~1284):
trace_index_map = {id(s): i for i, s in enumerate(trace)}

# Then replace line 1298 with:
last_appearance_idx = max([trace_index_map[id(s)] for s in char_timeline]) if char_timeline else 0
```

---

## Summary table

| # | File | Severity | What it fixes |
|---|------|----------|---------------|
| 1 | writer_agent.py:1672 | 🔴 Bug | ScriptPulse score dialogue harmony always maxed |
| 2 | writer_agent.py:1582 | 🔴 Bug | Market Readiness loc_count always 0 |
| 3 | writer_agent.py:~195 | 🔴 Bug | Same Voice Syndrome fires on every script |
| 4 | writer_agent.py:1022 | 🔴 Bug | 155 locations (should be ~30) |
| 5 | perception_agent.py:363,394 | 🔴 Bug | Hagen > Michael > Don Corleone agency ordering |
| 6 | structure_agent.py:195 | 🟠 Watch | Action lines ending in `:` mislabelled as transitions |
| 7 | structure_agent.py:280 | 🟠 Watch | Scene count inflated by M-tag boundaries |
| 8 | structure_agent.py:132 + experimental_agent.py:19 | 🔴 Bug | ML path hard-crashes (wrong model name) |
| 9 | governance.py + trust_lock.py | 🔴 Bug | Hard crash on deployment (missing exception class) |
| 10 | perception_agent.py:143 | 🟡 Accuracy | Runtime underestimate (~14 min short) |
| 11 | writer_agent.py:805 | 🟢 Perf | O(n²) redundant scene check — add 40-scene window |
| 12 | writer_agent.py:1298 | 🟢 Perf | O(n²) `list.index()` in character neglect loop |
