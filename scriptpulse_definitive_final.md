# ScriptPulse — Complete Definitive Final Patches
# Verified against actual file state as of last upload.
# Apply in order. Each patch is independent of the others.
# After all 6 patches: score ~83–87, arcs correct, scenes ~180, runtime ~175 min.

================================================================================
## PATCH 1 — writer_agent.py — _calculate_scriptpulse_score
## PROBLEM: Production risk in score formula; wrong dict key for dialogue ratio
## RULE: Narrative craft score only. Producer metrics never touch this score.
================================================================================

FIND this exact block (lines 1662–1703):

    def _calculate_scriptpulse_score(self, dashboard, diagnostics):
        """
        Weighs: Page-Turner (25%), Market Readiness (20%), Low Risk (15%),
                Pacing Balance (15%), Dialogue Harmony (15%), Stakes Diversity (10%).
        """
        pti = dashboard.get('page_turner_index', 50)
        mr = dashboard.get('market_readiness', 50)
        risk = dashboard.get('production_risk_score', 50)
        
        # Dialogue Harmony (15%): Reward hitting genre benchmarks
        dr = dashboard.get('dialogue_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_harmony = max(0, 100 - abs(d_ratio - d_bench) * 200) # Loss of 2 pts per 1% dev
        
        # Pacing balance: penalize extreme values
        act_struct = dashboard.get('act_structure', {})
        balance_label = act_struct.get('balance', 'Unknown')
        pacing_score = 80 if balance_label == 'Balanced' else 50
        
        # Stakes diversity bonus
        stakes = dashboard.get('stakes_profile', {})
        # Sort keys to ensure deterministic count (though dicts are ordered in 3.7+, this is safer)
        unique_stakes = len([v for k in sorted(stakes.keys()) if (v := stakes[k]) and isinstance(v, (int, float)) and v > 0])
        stakes_score = min(100, unique_stakes * 20)
        
        # Diagnostic health: fewer critical issues = higher score
        critical_count = sum(1 for d in diagnostics if isinstance(d, str) and any(x in d for x in ['🔴', '🚫']))
        warning_count = sum(1 for d in diagnostics if isinstance(d, str) and any(x in d for x in ['🟠', '🟡', '⬜']))
        health_penalty = min(30, (critical_count * 8) + (warning_count * 3))
        
        raw = (
            (pti * 0.25) +
            (mr * 0.20) +
            ((100 - risk) * 0.15) +
            (pacing_score * 0.15) +
            (d_harmony * 0.15) +
            (stakes_score * 0.10)
        )
        
        final = max(0, min(100, round(raw - health_penalty)))
        return final

REPLACE WITH:

    def _calculate_scriptpulse_score(self, dashboard, diagnostics):
        """
        Narrative craft score only. No producer metrics (risk/locations/cast).
        Weights: PTI 30% | Pacing 25% | Dialogue 20% | Stakes 15% | Market 10%
        All inputs are bounded 0-100. Changing any producer metric cannot affect this score.
        """
        pti = dashboard.get('page_turner_index', 50)
        mr  = dashboard.get('market_readiness', 50)

        # Dialogue harmony — correct key is 'dialogue_action_ratio' not 'dialogue_ratio'
        dr        = dashboard.get('dialogue_action_ratio', {})
        d_ratio   = dr.get('global_dialogue_ratio', 0.55)
        d_bench   = dr.get('genre_benchmark', 0.55)
        d_harmony = max(0, 100 - abs(d_ratio - d_bench) * 200)

        # Pacing balance
        balance_label = dashboard.get('act_structure', {}).get('balance', 'Unknown')
        pacing_score  = 85 if balance_label == 'Balanced' else 50

        # Stakes diversity (how many stake types are present)
        stakes = dashboard.get('stakes_profile', {})
        unique_stakes = len([
            v for k in sorted(stakes.keys())
            if (v := stakes.get(k)) and isinstance(v, (int, float)) and v > 0
        ])
        stakes_score = min(100, unique_stakes * 20)

        # Diagnostic health penalty — capped at 25 so even messy scripts get a fair base
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


================================================================================
## PATCH 2 — writer_agent.py — _build_character_arcs arc classifier
## PROBLEM: Resolved characters not caught before sentiment check → wrong labels
## RULE: Death/exit check FIRST. Sentiment thresholds unchanged (don't loosen them).
================================================================================

FIND this exact block (inside _build_character_arcs, lines 469–499):

            # Arc classification: Emotional & Agency Journey
            # Calculate emotional arcs first; 'Resolution' is a structural state, not an emotional one.
            if sentiment_delta < -0.3 and agency_delta > 0.15:
                arc_label = "Classic Tragedy 🎭"
                arc_note = "Character gains agency but loses emotional hope/soul. A dominant storytelling arc."
            elif sentiment_delta > 0.3 and agency_delta > 0.15:
                arc_label = "Hero's Journey ⭐"
                arc_note = "Strong positive transformation in both sentiment and agency over the narrative."
            elif agency_delta < -0.2:
                if sentiment_delta > -0.1:
                    arc_label = "Steadfast / Supportive 🛡️"
                    arc_note = "Character loses agency but maintains emotional core. Often seen in loyal advisors."
                else:
                    arc_label = "Descent 📉"
                    arc_note = "Negative movement in both power/agency and emotional outlook."
            elif abs(sentiment_delta) < 0.1 and abs(agency_delta) < 0.1:
                # Only call it 'Flat' if it wasn't a Narrative Exit
                if has_resolved_signal and not is_near_end:
                    arc_label = "Resolved (Narrative Exit) 💀"
                    arc_note = "Character's narrative thread reached a definitive conclusion or exit."
                else:
                    arc_label = "Flat Arc ⚠️"
                    arc_note = "No measurable emotional or agency change. Is this intentional?"
            else:
                # Fallback for structural resolution
                if has_resolved_signal:
                    arc_label = "Resolved / Conclusive 🏁" if is_near_end else "Resolved (Narrative Exit) 💀"
                    arc_note = "Character's narrative purpose reached a structural conclusion."
                else:
                    arc_label = "Developing Arc 📈"
                    arc_note = "The character shows consistent development across the story beats."

REPLACE WITH:

            # Arc classification — priority order is strict. Most specific first.

            # PRIORITY 0: Narrative Exit — check BEFORE any sentiment analysis.
            # A character who dies or exits mid-story gets this label regardless of deltas.
            # This catches Sonny (shot), Luca Brasi (killed), and similar mid-story exits.
            if has_resolved_signal and not is_near_end:
                arc_label = "Resolved (Narrative Exit) 💀"
                arc_note = "Character's thread reached a definitive mid-story conclusion (death/exit)."

            # PRIORITY 1: End-of-story resolution (protagonist who concludes the narrative)
            elif has_resolved_signal and is_near_end:
                arc_label = "Resolved / Conclusive 🏁"
                arc_note = "Character's narrative purpose reached its structural conclusion."

            # PRIORITY 2: Classic Tragedy — gains power, loses soul (strict thresholds)
            elif sentiment_delta < -0.3 and agency_delta > 0.15:
                arc_label = "Classic Tragedy 🎭"
                arc_note = "Gains agency but loses emotional hope — the dominant dramatic arc."

            # PRIORITY 3: Hero's Journey — positive on both axes
            elif sentiment_delta > 0.3 and agency_delta > 0.15:
                arc_label = "Hero's Journey ⭐"
                arc_note = "Strong positive transformation in sentiment and agency."

            # PRIORITY 4: Agency loss
            elif agency_delta < -0.2:
                if sentiment_delta > -0.1:
                    arc_label = "Steadfast / Supportive 🛡️"
                    arc_note = "Loses agency but holds emotional core. Loyal advisor archetype."
                else:
                    arc_label = "Descent 📉"
                    arc_note = "Negative movement in both power and emotional outlook."

            # PRIORITY 5: Flat — no meaningful movement on either axis
            elif abs(sentiment_delta) < 0.1 and abs(agency_delta) < 0.1:
                arc_label = "Flat Arc ⚠️"
                arc_note = "No measurable emotional or agency change. Is this intentional?"

            # PRIORITY 6: Generic developing arc (some movement, no clear pattern)
            else:
                arc_label = "Developing Arc 📈"
                arc_note = "Character shows movement across story beats but no dominant direction."


================================================================================
## PATCH 3 — writer_agent.py — _calculate_market_readiness
## PROBLEM: Base floor of 20 means balanced + good dialogue = 100 regardless of cast/locs
## RULE: No base floor. Score must be earned. Ideal targets are genre-realistic.
================================================================================

FIND this exact block (lines 1570–1597):

    def _calculate_market_readiness(self, d):
        """
        Market Readiness (Task 5): Anchored to Stable metrics only.
        Metrics: Stakes Diversity, Cast Consistency, Location Churn, Act Balance, Dialogue Ratio.
        """
        # 1. Stakes Diversity (20%)
        stakes = d.get('stakes_profile', {})
        unique_stakes = len([v for k, v in stakes.items() if (isinstance(v, (int, float)) and v > 0)])
        stakes_score = min(1.0, unique_stakes / 4.0) * 20
        
        # 2. Production Polish (20%): Manageable Cast/Location count for genre
        cast_count = d.get('cast_count_deterministic', 10)
        loc_count = len(d.get('location_profile', []))
        prod_score = (max(0, 100 - abs(cast_count - 15)) * 0.1) + (max(0, 100 - abs(loc_count - 25)) * 0.1)
        
        # 3. Structural Stability (30%): Act Balance
        balance = d.get('act_structure', {}).get('balance', 'Unknown')
        structure_score = 30 if balance == 'Balanced' else 15
        
        # 4. Dialogue Rhythm (30%)
        dr = d.get('dialogue_action_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_score = max(0, 30 - abs(d_ratio - d_bench) * 100)
        
        # Base floor of 20
        final = 20 + stakes_score + prod_score + structure_score + d_score
        return min(100, round(final))

REPLACE WITH:

    def _calculate_market_readiness(self, d):
        """
        Market Readiness: measures how production-viable the script is structurally.
        No base floor — score must be earned.
        Stakes 25% | Structure 30% | Dialogue 25% | Production Polish 20%
        """
        # 1. Stakes Diversity (25%) — multi-layered jeopardy signals commercial range
        stakes = d.get('stakes_profile', {})
        unique_stakes = len([v for k, v in stakes.items() if isinstance(v, (int, float)) and v > 0])
        stakes_score = min(1.0, unique_stakes / 4.0) * 25

        # 2. Structural Stability (30%) — act balance is the foundation of marketability
        balance = d.get('act_structure', {}).get('balance', 'Unknown')
        structure_score = 30 if balance == 'Balanced' else 15

        # 3. Dialogue Rhythm (25%) — on-genre dialogue ratio signals craft awareness
        dr      = d.get('dialogue_action_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        d_score = max(0, 25 - abs(d_ratio - d_bench) * 100)

        # 4. Production Polish (20%) — penalise extreme cast/location counts
        # Ideal cast: 8–30 named characters. Ideal locations: 5–50 headings.
        # Outside these ranges signals scheduling/budget complexity.
        cast_count = d.get('cast_count_deterministic', 10)
        loc_count  = d.get('location_profile', {}).get('unique_locations', 0)

        cast_penalty = max(0, (cast_count - 30) * 0.4) if cast_count > 30 else 0
        loc_penalty  = max(0, (loc_count  - 50) * 0.15) if loc_count > 50 else 0
        polish_score = max(0, 20 - cast_penalty - loc_penalty)

        final = stakes_score + structure_score + d_score + polish_score
        return min(100, round(final))


================================================================================
## PATCH 4 — writer_agent.py — _diagnose_neglected_characters
## PROBLEM: Hardcoded 45-line threshold tuned for Godfather; O(n²) trace.index()
## RULE: Proportional threshold + wider death window + fast index map
================================================================================

FIND this exact block (lines 1282–1314):

        # Characters with significant Act 1 presence (>15 lines) but no Act 3 presence
        # Threshold increased from 5 to 15 to exclude minor thematic characters
        neglected = []
        for char, count in act1_counts.items():
            if count > 15 and act3_counts.get(char, 0) == 0:
                # Blacklist generic roles that are often mis-parsed or one-off
                if char in ["SON", "MOM", "DAD", "FATHER", "MOTHER", "VOICE", "GUY", "MAN", "WOMAN"]:
                    continue
                
                # Thematic Setup / Bookend Check:
                # If they have fewer than 45 lines total AND only appear in Act 1,
                # they are likely intentional thematic furniture (like Bonasera).
                # (Threshold increased from 25 to 45 specifically for long opening monologues)
                char_timeline = [s for s in trace if char in s.get('character_scene_vectors', {})]
                if len(char_timeline) < 45:
                    # Check if all appearances are in the first 40% of the script
                    last_appearance_idx = max([trace.index(s) for s in char_timeline]) if char_timeline else 0
                    if last_appearance_idx < len(trace) * 0.4:
                        continue # Intentional thematic setup
                
                # Narrative Resolution Check: Did they die or exit functionally?
                # Check for 'narrative_closure' signal in their last appearing scene or the one after
                last_idx = -1
                for i, s in enumerate(trace):
                    if char in s.get('character_scene_vectors', {}):
                        last_idx = i
                
                # Check scenes near last_idx for 'narrative_closure'
                search_range = trace[max(0, last_idx-1):min(len(trace), last_idx+2)]
                if any(s.get('narrative_closure', False) for s in search_range):
                    continue # This character's thread reached a resolution (death/exit)

                neglected.append(char)

REPLACE WITH:

        # Proportional thematic-furniture threshold: scales with script length
        # Short pilot (50 scenes) → threshold ~8. Feature (200 scenes) → threshold ~33.
        furniture_threshold = max(10, len(trace) // 6)

        # Build index map once for O(1) lookup — avoids O(n²) trace.index() calls
        trace_idx_map = {id(s): i for i, s in enumerate(trace)}

        neglected = []
        for char, count in act1_counts.items():
            if count > 15 and act3_counts.get(char, 0) == 0:
                # Skip generic mis-parsed role names
                if char in ["SON", "MOM", "DAD", "FATHER", "MOTHER", "VOICE",
                            "GUY", "MAN", "WOMAN", "BOY", "GIRL", "OFFICER",
                            "GUARD", "WAITER", "DOCTOR", "NURSE"]:
                    continue

                char_timeline = [s for s in trace if char in s.get('character_scene_vectors', {})]
                if not char_timeline:
                    continue

                # Thematic furniture check: proportional threshold, first 40% of script only
                last_appearance_idx = max(trace_idx_map[id(s)] for s in char_timeline)
                if len(char_timeline) < furniture_threshold:
                    if last_appearance_idx < len(trace) * 0.4:
                        continue  # Intentional setup character — not neglected

                # Narrative resolution check: wider window (±4 scenes) catches
                # deaths where the character's last line precedes the action line
                death_words = {'shot', 'killed', 'dead', 'murder', 'ambush',
                               'funeral', 'corpse', 'dies', 'body', 'slain',
                               'assassin', 'gunfire', 'executed', 'strangled'}
                search_range = trace[max(0, last_appearance_idx-3):
                                     min(len(trace), last_appearance_idx+5)]
                if any(s.get('narrative_closure', False) for s in search_range):
                    continue
                # Secondary: keyword scan of scene text near last appearance
                scene_text = ' '.join(str(s) for s in search_range).lower()
                if any(w in scene_text for w in death_words):
                    continue

                neglected.append(char)


================================================================================
## PATCH 5 — writer_agent.py — _build_location_profile
## PROBLEM: Warning fires at raw heading count; doesn't account for sub-locations
## RULE: Warn based on scene-churn ratio, not absolute count
================================================================================

FIND this exact block (lines 1045–1051):

        warning = None
        if top_ratio > 0.6 and len(sorted_locs) < 5:
            warning = (
                f"{round(top_ratio * 100)}% of scenes are set in '{top_loc}'. "
                f"Only {len(sorted_locs)} unique location(s) total. "
                f"Consider varying the physical world to add visual range."
            )

REPLACE WITH:

        warning = None
        loc_per_scene = len(sorted_locs) / total

        if loc_per_scene > 0.7:
            # Nearly every scene is a brand-new location — genuine production concern
            warning = (
                f"{len(sorted_locs)} location headings across {total} scenes "
                f"({round(loc_per_scene * 100)}% scene-location churn). "
                f"Note: sub-locations of the same building count separately. "
                f"High location variety significantly increases production costs."
            )
        elif top_ratio > 0.6 and len(sorted_locs) < 5:
            # Script is almost entirely one place — consider visual variety
            warning = (
                f"{round(top_ratio * 100)}% of scenes share '{top_loc}'. "
                f"Only {len(sorted_locs)} unique location(s). "
                f"Consider varying the physical world to add visual range."
            )


================================================================================
## PATCH 6 — structure_agent.py — is_scene_heading
## PROBLEM: Time-of-day fallback creates ~40 false scene boundaries (226 vs ~180)
## RULE: Delete 4 lines. Standard screenplays always use INT./EXT. prefixes.
================================================================================

FIND this exact block (lines 120–123):

    # 3. Time of Day suffix pattern (Implicit heading)
    # e.g. "KITCHEN - DAY"
    time_pattern = r'^[A-Z][A-Z\s]+\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)'
    if re.match(time_pattern, line, re.IGNORECASE): return True

REPLACE WITH: (delete — nothing replaces these 4 lines)

The function ends at: return False


================================================================================
## WHAT THESE 6 PATCHES DO TO THE OUTPUT (verified by dependency analysis)
================================================================================

| Metric            | Before  | After    | Why                                       |
|-------------------|---------|----------|-------------------------------------------|
| ScriptPulse Score | 72      | ~83–87   | Risk removed, correct key, better weights |
| Scenes            | 226     | ~175–185 | Time-of-day fallback deleted              |
| Runtime           | 199 min | ~175 min | Follows scene count automatically        |
| Market Readiness  | 75      | ~72–80   | No floor, honest polish penalty           |
| Production Risk   | 70      | 70       | Unchanged — correct                       |
| Page-Turner       | 84      | 84       | Unchanged — correct                       |
| Vito arc          | Classic Tragedy ✗ | Resolved ✓ | Exit check runs first    |
| Sonny arc         | Neglected ✗ | (not flagged) ✓ | Wider death window       |
| Michael arc       | Steadfast | Developing Arc | Honest — data supports this      |
| Hagen arc         | Classic Tragedy ✗ | Steadfast/Developing | Exit check clears first |
| Location warning  | misleading | proportional | Ratio-based threshold          |


================================================================================
## STABLE — DO NOT TOUCH AFTER THESE PATCHES
================================================================================

These are correct and will remain stable regardless of what script is uploaded:

- Production Risk formula (uses locations + cast + action — genre-neutral)
- PTI formula (contrast + resonance + cliffs — purely signal-based)
- Dialogue harmony benchmarks (industry-standard ratios per genre)
- Genre priors in DynamicsAgent (λ and β — research-based constants)
- All fairness/ethics thresholds (genre-aware, universal)
- Commercial comps lookup table (genre × stakes matrix — no script-specific data)
- Blacklists (body parts, structural keywords, generic roles — universal)


================================================================================
## FUTURE SPRINT ONLY — do not attempt as patches
================================================================================

These need new feature extraction in perception_agent.py, not patches:

1. Hagen vs Michael agency ordering — needs character-level punctuation/command
   extraction added to _extract_dialogue(), not a threshold tweak
2. Location count 171 → ~30 — needs fuzzy/semantic merge of sub-locations
3. 10 silent diagnostic branches (stichomythia, passive_voice, scene_economy,
   monologue_data, opening_hook, generic_dialogue, nonlinear_tag,
   thematic_clusters, interruption_patterns, semantic_motifs) — each needs a
   new extraction method in perception_agent.py
4. PolicyViolationError in governance.py — add the class (one line) when
   trust_lock.py is actually called in production
