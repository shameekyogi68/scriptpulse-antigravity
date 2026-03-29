# ScriptPulse — Corrective Patches (Run 4 → Final)
# Apply all 5 of these. They are the last remaining issues.

---

## FIX 1 — `writer_agent.py` ~line 1662
**Score dropped 81→67 because Production Risk (70) now penalises writing quality**
**Remove production risk from ScriptPulse score. Redistribute its 15% weight.**

```python
# REPLACE the entire _calculate_scriptpulse_score method:

def _calculate_scriptpulse_score(self, dashboard, diagnostics):
    """
    Weighs NARRATIVE CRAFT only — not production budget.
    Page-Turner (30%), Pacing Balance (20%), Dialogue Harmony (20%),
    Stakes Diversity (15%), Health Penalty (15%).
    Production Risk lives in the Producer panel only.
    """
    pti = dashboard.get('page_turner_index', 50)

    # Dialogue Harmony (20%): reward hitting genre benchmarks
    dr = dashboard.get('dialogue_action_ratio', {})
    d_ratio = dr.get('global_dialogue_ratio', 0.55)
    d_bench = dr.get('genre_benchmark', 0.55)
    d_harmony = max(0, 100 - abs(d_ratio - d_bench) * 200)

    # Pacing balance (20%): penalise extreme act imbalance
    act_struct = dashboard.get('act_structure', {})
    balance_label = act_struct.get('balance', 'Unknown')
    pacing_score = 85 if balance_label == 'Balanced' else 50

    # Stakes diversity (15%): multi-layered jeopardy
    stakes = dashboard.get('stakes_profile', {})
    unique_stakes = len([
        v for k in sorted(stakes.keys())
        if (v := stakes[k]) and isinstance(v, (int, float)) and v > 0
    ])
    stakes_score = min(100, unique_stakes * 20)

    # Market readiness (15%): structural viability signal
    mr = dashboard.get('market_readiness', 50)

    # Diagnostic health penalty (up to -30): fewer critical issues = higher score
    critical_count = sum(
        1 for d in diagnostics
        if isinstance(d, str) and any(x in d for x in ['🔴', '🚫'])
    )
    warning_count = sum(
        1 for d in diagnostics
        if isinstance(d, str) and any(x in d for x in ['🟠', '🟡', '⬜'])
    )
    health_penalty = min(30, (critical_count * 8) + (warning_count * 3))

    raw = (
        (pti        * 0.30) +
        (pacing_score * 0.20) +
        (d_harmony  * 0.20) +
        (stakes_score * 0.15) +
        (mr         * 0.15)
    )

    return max(0, min(100, round(raw - health_penalty)))
```

---

## FIX 2 — `structure_agent.py` lines 120–123
**Scene count stuck at 226 — time-of-day fallback creates false scene boundaries**
**Delete the fallback entirely. Standard screenplays always use INT./EXT.**

```python
# FIND this block (lines 120–123) and DELETE it completely:

    # 3. Time of Day suffix pattern (Implicit heading)
    # e.g. "KITCHEN - DAY"
    time_pattern = r'^[A-Z][A-Z\s]+\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)'
    if re.match(time_pattern, line, re.IGNORECASE): return True

# The function should end at line 125: return False
# No replacement needed — just remove those 4 lines.
```

---

## FIX 3 — `writer_agent.py` ~line 430
**Michael's arc stays "Steadfast" — per-character sentiment uses word-count proxy (±0.1 per yes/no)**
**Use scene-level sentiment windows for arc calculation instead.**

```python
# REPLACE _build_character_arcs method's timeline builder and arc classifier:

def _build_character_arcs(self, trace):
    char_timeline = {}
    for s in trace:
        for char, data in s.get('character_scene_vectors', {}).items():
            if char not in char_timeline:
                char_timeline[char] = []
            char_timeline[char].append({
                'scene': s['scene_index'],
                # Use scene-level compound sentiment — much more meaningful than
                # the per-character ±0.1 word-count proxy
                'sentiment': s.get('sentiment', data.get('sentiment', 0.0)),
                'agency': data.get('agency', 0.0),
                'lines': data.get('line_count', 0),
                'resolved': s.get('narrative_closure', False)
            })

    arc_summary = {}
    total_scenes = max([s.get('scene_index', 0) for s in trace]) if trace else 100

    for char, timeline in sorted(char_timeline.items()):
        if len(timeline) < 3:
            continue
        total_lines = sum(t['lines'] for t in timeline)
        if total_lines < 8:
            continue

        # Use 3-scene windows at start and end for stability
        window = max(1, min(3, len(timeline) // 4))
        start_sentiment = sum(t['sentiment'] for t in timeline[:window]) / window
        end_sentiment   = sum(t['sentiment'] for t in timeline[-window:]) / window
        start_agency    = sum(t['agency']    for t in timeline[:window]) / window
        end_agency      = sum(t['agency']    for t in timeline[-window:]) / window

        sentiment_delta = round(end_sentiment - start_sentiment, 3)
        agency_delta    = round(end_agency    - start_agency,    3)

        is_near_end = timeline[-1].get('scene', 0) > (total_scenes * 0.9)
        has_resolved_signal = (
            timeline[-1].get('resolved', False) or
            (len(timeline) > 1 and timeline[-2].get('resolved', False))
        )

        # Arc classification
        if sentiment_delta < -0.2 and agency_delta > 0.05:
            arc_label = "Classic Tragedy 🎭"
            arc_note  = "Gains agency but loses emotional soul — the dominant dramatic arc."
        elif sentiment_delta < -0.35:
            # Strong negative journey even without agency gain (e.g. pure descent)
            arc_label = "Classic Tragedy 🎭"
            arc_note  = "Significant negative emotional arc — character's moral world collapses."
        elif sentiment_delta > 0.2 and agency_delta > 0.05:
            arc_label = "Hero's Journey ⭐"
            arc_note  = "Positive transformation in both sentiment and agency."
        elif agency_delta < -0.2:
            if sentiment_delta > -0.1:
                arc_label = "Steadfast / Supportive 🛡️"
                arc_note  = "Loses agency but maintains emotional core. Loyal advisor archetype."
            else:
                arc_label = "Descent 📉"
                arc_note  = "Negative movement in both power and emotional outlook."
        elif abs(sentiment_delta) < 0.08 and abs(agency_delta) < 0.08:
            if has_resolved_signal and not is_near_end:
                arc_label = "Resolved (Narrative Exit) 💀"
                arc_note  = "Character's thread reached a definitive conclusion."
            else:
                arc_label = "Flat Arc ⚠️"
                arc_note  = "No measurable emotional or agency change. Intentional?"
        else:
            if has_resolved_signal:
                arc_label = "Resolved / Conclusive 🏁" if is_near_end else "Resolved (Narrative Exit) 💀"
                arc_note  = "Character's narrative purpose reached a structural conclusion."
            else:
                arc_label = "Developing Arc 📈"
                arc_note  = "Consistent development across story beats."

        arc_summary[char] = {
            'arc_type':        arc_label,
            'note':            arc_note,
            'sentiment_start': round(start_sentiment, 3),
            'sentiment_end':   round(end_sentiment, 3),
            'sentiment_delta': sentiment_delta,
            'agency_start':    round(start_agency, 3),
            'agency_end':      round(end_agency, 3),
            'agency_delta':    agency_delta,
            'scenes_present':  len(timeline)
        }

    return arc_summary
```

---

## FIX 4 — `writer_agent.py` ~line 1570
**Market Readiness always 100 — base floor of 20 + balanced structure + good dialogue = 100 regardless**
**Remove base floor and fix production polish calculation.**

```python
# REPLACE _calculate_market_readiness:

def _calculate_market_readiness(self, d):
    """
    Market Readiness: Stakes Diversity (25%), Structural Stability (30%),
    Dialogue Rhythm (25%), Production Polish (20%).
    No base floor — score must be earned.
    """
    # 1. Stakes Diversity (25%)
    stakes = d.get('stakes_profile', {})
    unique_stakes = len([v for k, v in stakes.items() if isinstance(v, (int, float)) and v > 0])
    stakes_score = min(1.0, unique_stakes / 4.0) * 25

    # 2. Production Polish (20%): penalise extreme cast/location counts
    cast_count = d.get('cast_count_deterministic', 10)
    loc_count  = d.get('location_profile', {}).get('unique_locations', 0)
    # Ideal: cast 8–25, locations 5–40. Penalise outside those ranges.
    cast_penalty = max(0, (cast_count - 25) * 0.3) if cast_count > 25 else 0
    loc_penalty  = max(0, (loc_count  - 40) * 0.2) if loc_count  > 40 else 0
    polish_score = max(0, 20 - cast_penalty - loc_penalty)

    # 3. Structural Stability (30%): act balance
    balance = d.get('act_structure', {}).get('balance', 'Unknown')
    structure_score = 30 if balance == 'Balanced' else 15

    # 4. Dialogue Rhythm (25%): on-genre benchmark
    dr      = d.get('dialogue_action_ratio', {})
    d_ratio = dr.get('global_dialogue_ratio', 0.55)
    d_bench = dr.get('genre_benchmark', 0.55)
    d_score = max(0, 25 - abs(d_ratio - d_bench) * 100)

    final = stakes_score + polish_score + structure_score + d_score
    return min(100, round(final))
```

For The Godfather: stakes=25, polish≈0 (171 locs heavily penalised), structure=30, dialogue≈25 → ~80.
A tight indie drama with 3 locations and balanced dialogue should score ~95+. ✓

---

## FIX 5 — `writer_agent.py` ~line 1045
**Location warning fires at wrong threshold — 171 raw headings is misleading**
**Warn based on ratio to scene count, not absolute number. Add clarifying note.**

```python
# REPLACE the warning block in _build_location_profile:

    # Warning: only flag if locations-per-scene ratio is extremely high
    # (nearly every scene is a brand-new location — genuinely expensive)
    loc_per_scene_ratio = len(sorted_locs) / total
    warning = None
    if loc_per_scene_ratio > 0.6:
        warning = (
            f"{len(sorted_locs)} unique location headings detected across {total} scenes "
            f"({round(loc_per_scene_ratio * 100)}% scene-location churn). "
            f"Note: sub-locations of the same building count separately. "
            f"High location variety increases production costs — consider consolidating."
        )
    elif top_ratio > 0.6 and len(sorted_locs) < 5:
        warning = (
            f"{round(top_ratio * 100)}% of scenes are set in '{top_loc}'. "
            f"Only {len(sorted_locs)} unique location(s) total. "
            f"Consider varying the physical world to add visual range."
        )
```

---

## Expected results after these 5 fixes

| Metric | Current | After fixes |
|--------|---------|-------------|
| ScriptPulse Score | 67 | ~82–86 |
| Page-Turner | 84 | 84 (correct) |
| Scenes | 226 | ~175–185 |
| Runtime | 199 min | ~170–180 min |
| Market Readiness | 100 | ~75–82 |
| Michael arc | Steadfast ✗ | Classic Tragedy ✓ |
| Locations warning | misleading | proportional |
| Score label | "Needs Work" | "Strong Draft" |

## What will still need a future sprint

- Locations count: 171 → ~30 requires fuzzy/semantic location merging (not a simple dedup)
- Hagen > Michael agency: needs character-level sentiment to use scene compound, not yes/no words
- 10+ silent diagnostic branches (stichomythia, passive voice, scene economy etc.) need new PerceptionAgent extractors
- Page-Turner 84/100: now realistic — verify it doesn't give 100 to weak scripts
