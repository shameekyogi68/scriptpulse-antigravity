# ScriptPulse — Final 3 Changes Only
# Do not apply anything else. These are isolated, dependency-safe.

---

## CHANGE 1 — `writer_agent.py`
### Find and replace `_calculate_scriptpulse_score` (the entire method)

FIND:
```python
    def _calculate_scriptpulse_score(self, dashboard, diagnostics):
```
(find the entire method body and replace it)

REPLACE WITH:
```python
    def _calculate_scriptpulse_score(self, dashboard, diagnostics):
        """
        Narrative craft score only. Producer metrics (risk, locations, cast)
        are excluded — they live in the Producer panel.
        Weights: PTI 30% | Pacing 25% | Dialogue 20% | Stakes 15% | Market 10%
        """
        pti = dashboard.get('page_turner_index', 50)

        # Dialogue harmony — fix: use correct key 'dialogue_action_ratio'
        dr      = dashboard.get('dialogue_action_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_harmony = max(0, 100 - abs(d_ratio - d_bench) * 200)

        # Pacing balance
        balance_label = dashboard.get('act_structure', {}).get('balance', 'Unknown')
        pacing_score  = 85 if balance_label == 'Balanced' else 50

        # Stakes diversity
        stakes = dashboard.get('stakes_profile', {})
        unique_stakes = len([
            v for k in sorted(stakes.keys())
            if (v := stakes.get(k)) and isinstance(v, (int, float)) and v > 0
        ])
        stakes_score = min(100, unique_stakes * 20)

        # Market readiness (already bounded 0-100 by its own method)
        mr = dashboard.get('market_readiness', 50)

        # Diagnostic health penalty (max -25)
        critical_count = sum(
            1 for d in diagnostics
            if isinstance(d, str) and any(x in d for x in ['🔴', '🚫'])
        )
        warning_count = sum(
            1 for d in diagnostics
            if isinstance(d, str) and any(x in d for x in ['🟠', '🟡', '⬜'])
        )
        health_penalty = min(25, (critical_count * 7) + (warning_count * 2))

        raw = (
            (pti          * 0.30) +
            (pacing_score * 0.25) +
            (d_harmony    * 0.20) +
            (stakes_score * 0.15) +
            (mr           * 0.10)
        )

        return max(0, min(100, round(raw - health_penalty)))
```

Expected result: Godfather score ~83–87. Changing market readiness or production
risk in future will NOT affect this score.

---

## CHANGE 2 — `writer_agent.py`
### Fix arc classifier — resolved characters exit BEFORE sentiment check

FIND (inside `_build_character_arcs`, the arc classification block):
```python
            # Arc classification: Emotional & Agency Journey
            # Calculate emotional arcs first; 'Resolution' is a structural state, not an emotional one.
            if sentiment_delta < -0.3 and agency_delta > 0.15:
                arc_label = "Classic Tragedy 🎭"
```

REPLACE WITH:
```python
            # Arc classification — priority order matters, most specific first.

            # 0. Narrative Exit (check FIRST — overrides all sentiment analysis)
            # A character who dies or exits mid-story gets this regardless of deltas.
            if has_resolved_signal and not is_near_end:
                arc_label = "Resolved (Narrative Exit) 💀"
                arc_note  = "Character's narrative thread reached a definitive conclusion or exit."

            # 1. Classic Tragedy: gains power, loses soul (strict thresholds — don't lower these)
            elif sentiment_delta < -0.3 and agency_delta > 0.15:
                arc_label = "Classic Tragedy 🎭"
```

That's the only change inside the method. Keep all other branches exactly as they were.

Why this works:
- Vito Corleone: has_resolved_signal=True, is_near_end=False → "Resolved (Narrative Exit)" ✓
- Hagen: no death signal → falls through to existing sentiment branches
- Michael: no death signal, delta too small for Tragedy → "Developing Arc" or "Steadfast" (honest)

---

## CHANGE 3 — `structure_agent.py`
### Delete the time-of-day fallback heading pattern (4 lines)

FIND (lines 120–123):
```python
    # 3. Time of Day suffix pattern (Implicit heading)
    # e.g. "KITCHEN - DAY"
    time_pattern = r'^[A-Z][A-Z\s]+\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)'
    if re.match(time_pattern, line, re.IGNORECASE): return True
```

REPLACE WITH: (nothing — delete these 4 lines entirely)

The function goes straight from the fallback_patterns block to `return False`.

Expected result: scenes 226 → ~180, runtime 199 → ~175 min.
Nothing else in the codebase references this pattern.

---

## Do not change anything else.

The following are accepted as stable and correct at current values:
- Market Readiness 75 ✓
- Production Risk 70 ✓  
- Page-Turner 84 ✓
- Locations 171 (raw heading count — fuzzy merge is a future feature)
- Runtime will auto-correct once scene count drops (Change 3)
- Hagen/Michael agency — future sprint, new extraction needed
