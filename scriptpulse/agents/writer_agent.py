
class WriterAgent:
    """
    The 'Collaborator' Layer (v2.0 Phase 1).
    Translates raw engine signals into actionable writer feedback.
    Does not run simulations; interprets existing trace data.
    """
    
    def analyze(self, final_output, genre="General"):
        """
        Enhances the final_output with a 'writer_intelligence' block.
        Applies Strict Constraints and Genre Nuance.
        """
        trace = final_output.get('temporal_trace', [])
        suggestions = final_output.get('suggestions', {})
        
        if not trace: return final_output
        
        # 1. Narrative Diagnosis (Clustered & Ranked)
        narrative_health = self._diagnose_health(trace, genre)
        
        # Phase 22: Voice, Motif, and Tell/Show extra diagnostics
        narrative_health.extend(self._diagnose_voice(final_output.get('voice_fingerprints', {})))
        narrative_health.extend(self._diagnose_motifs(trace))
        narrative_health.extend(self._diagnose_tell_vs_show(trace))
        
        # Phase 23: Masterclass diagnostics
        narrative_health.extend(self._diagnose_on_the_nose(trace))
        narrative_health.extend(self._diagnose_shoe_leather(trace))
        narrative_health.extend(self._diagnose_semantic_motifs(trace))
        
        # Phase 24: Narrative Intelligence
        narrative_health.extend(self._diagnose_stakes_diversity(trace))
        narrative_health.extend(self._diagnose_stichomythia(trace))
        narrative_health.extend(self._diagnose_payoff_density(trace))
        
        # Phase 25: Scene-Level Micro-Drama
        narrative_health.extend(self._diagnose_opening_hook(trace))
        narrative_health.extend(self._diagnose_generic_dialogue(trace))
        narrative_health.extend(self._diagnose_flat_scene_turns(trace))
        
        # Phase 26: Macro-Consistency & Craft
        narrative_health.extend(self._diagnose_passive_voice(trace))
        narrative_health.extend(self._diagnose_tonal_whiplash(trace))
        narrative_health.extend(self._diagnose_redundant_scenes(trace))
        narrative_health.extend(self._diagnose_dangling_threads(trace))
        
        # Phase 27: Producer's View
        narrative_health.extend(self._diagnose_protagonist_arc(trace))
        narrative_health.extend(self._diagnose_interruption_dynamics(trace))
        
        # Phase 28: Synthesis & Structure
        narrative_health.extend(self._diagnose_monologues(trace))
        
        # Phase 29: Reader Experience & Thematic Depth
        narrative_health.extend(self._diagnose_reader_frustration(trace))
        narrative_health.extend(self._diagnose_neglected_characters(trace))
        narrative_health.extend(self._diagnose_nonlinear_structure(trace))
        narrative_health.extend(self._diagnose_theme_coherence(trace))

        # 2. Rewrite Priorities (Leveled & Limited)
        ranked_edits = self._rank_edits(suggestions, trace)
        
        # 3. Structural Dashboard with Arc Vectors + Scene Map
        dashboard = self._build_dashboard(trace, genre)
        dashboard['character_arcs'] = self._build_character_arcs(trace)
        dashboard['scene_purpose_map'] = self._build_scene_purpose_map(trace)
        dashboard['stakes_profile'] = self._build_stakes_profile(trace)
        dashboard['scene_turn_map'] = self._build_scene_turn_map(trace)
        dashboard['dialogue_action_ratio'] = self._build_global_dialogue_ratio(trace, genre)
        # Phase 27 dashboard additions
        dashboard['runtime_estimate'] = self._build_runtime_estimate(trace, genre)
        dashboard['location_profile'] = self._build_location_profile(trace)
        # Phase 28 dashboard additions
        dashboard['structural_turning_points'] = self._find_structural_turning_points(trace)
        dashboard['scene_economy_map'] = self._build_scene_economy_map(trace)
        
        # Inject into output
        final_output['writer_intelligence'] = {
            'narrative_diagnosis': narrative_health[:12],  # Up to 12 covering all layers
            'rewrite_priorities': ranked_edits[:5],
            'structural_dashboard': dashboard,
            'narrative_summary': self._build_narrative_summary(trace, genre),
            'genre_context': genre
        }
        
        return final_output

    def _diagnose_health(self, trace, genre):
        """
        Converts math signals to story terms.
        Clusters consecutive issues.
        Adapts thresholds based on Genre.
        """
        assessments = []
        
        # Genre Thresholds
        boredom_thresh = 0.2
        if genre in ["Horror", "Drama", "Art House", "Avant-Garde", "Non-Linear"]:
            boredom_thresh = 0.1 # Tolerate slower pacing
            
        fatigue_thresh = 0.8
        if genre in ["Action", "Thriller"]:
            fatigue_thresh = 0.85 # Tolerate higher intensity
            
        is_avant_garde = genre in ["Avant-Garde", "Non-Linear"]
        
        # 1. Fatigue Clustering (Skipped for Avant-Garde which intentionally fatigues/overwhelms)
        if not is_avant_garde:
            fatigue_ranges = self._find_ranges(trace, lambda s: s['fatigue_state'] > fatigue_thresh)
            for start, end in fatigue_ranges:
                length = end - start + 1
                if length > 3:
                    duration_mins = length * 2
                    assessments.append({
                        'type': 'CRITICAL',
                        'text': f"🔴 **Too Intense (Scenes {start}-{end})**: Action is non-stop for ~{duration_mins} mins. Readers may get tired."
                    })

        # 2. Confusion Clustering
        strain_ranges = self._find_ranges(trace, lambda s: s.get('expectation_strain', 0) > 0.8)
        for start, end in strain_ranges:
             assessments.append({
                 'type': 'WARNING',
                 'text': f"🟠 **Too Complex (Scenes {start}-{end})**: Too much happening at once. Readers may get confused."
             })
            
        # 3. Boredom vs Tense Silence
        true_boredom_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) <= 0.6)
        for start, end in true_boredom_ranges:
            if (end - start + 1) >= 2:
                 assessments.append({
                     'type': 'WARNING',
                     'text': f"🔵 **Too Slow (Scenes {start}-{end})**: Nothing important is happening. Readers may get bored."
                 })

        tense_silence_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) > 0.6)
        for start, end in tense_silence_ranges:
            if (end - start + 1) >= 2:
                 assessments.append({
                     'type': 'GOOD',
                     'text': f"🤫 **Tense Silence (Scenes {start}-{end})**: Low action, but stakes are high. Great build-up of dread."
                 })

        # 4. Passivity Analysis (Thematic vs Accidental)
        accidental_passivity = self._find_ranges(trace, lambda s: s.get('agency', 1.0) < 0.3 and not (s.get('conflict', 0) > 0.6 and s.get('sentiment', 0) < -0.2))
        for start, end in accidental_passivity:
            assessments.append({
                'type': 'WARNING',
                'text': f"🧍 **Accidental Passivity (Scenes {start}-{end})**: Protagonist is not making choices. They are watching the plot happen."
            })

        thematic_passivity = self._find_ranges(trace, lambda s: s.get('agency', 1.0) < 0.3 and (s.get('conflict', 0) > 0.6 and s.get('sentiment', 0) < -0.2))
        for start, end in thematic_passivity:
            assessments.append({
                'type': 'GOOD',
                'text': f"⛓️ **Thematic Passivity (Scenes {start}-{end})**: Protagonist is trapped or overwhelmed. Effective loss of agency."
            })

        # 5. Subtext / Tension
        subtext_ranges = self._find_ranges(trace, lambda s: s.get('action_density', 0) > 0.7 and s.get('dialogue_density', 1) < 0.3)
        for start, end in subtext_ranges:
            assessments.append({
                'type': 'GOOD',
                'text': f"✨ **High Tension (Scenes {start}-{end})**: Strong visual storytelling with minimal dialogue. Great subtext."
            })

        # 6. Irony / Dissonance
        irony_ranges = self._find_ranges(trace, lambda s: s.get('sentiment', 0) > 0.6 and s.get('conflict', 0) > 0.7)
        for start, end in irony_ranges:
             assessments.append({
                'type': 'GOOD',
                'text': f"🎭 **Irony Detected (Scenes {start}-{end})**: Positive tone matches high conflict. Unsettling and effective."
            })
            
        # Sort by Severity
        # Critical first, then longest ranges
        assessments.sort(key=lambda x: (x['type'] != 'CRITICAL', x['type'] != 'WARNING', -len(x['text'])))
        
        if len(assessments) == 0:
            assessments.append({'type': 'GOOD', 'text': "🟢 **Good Flow**: The story moves well."})
            
        return [a['text'] for a in assessments]

    def _diagnose_voice(self, voice_fingerprints):
        import statistics
        assessments = []
        if not voice_fingerprints or len(voice_fingerprints) < 2: return []
        
        # Get top speakers by line count
        top_chars = sorted(voice_fingerprints.items(), key=lambda x: x[1].get('line_count', 0), reverse=True)[:5]
        if len(top_chars) < 2: return []
        
        # We need at least 10 lines to reliably judge a voice
        valid_chars = [c for c in top_chars if c[1].get('line_count', 0) >= 10]
        if len(valid_chars) < 2: return []
        
        complexities = [c[1].get('complexity', 0) for c in valid_chars]
        positivities = [c[1].get('positivity', 0) for c in valid_chars]
        puncts = [c[1].get('punctuation_rate', 0) for c in valid_chars]
        
        std_comp = statistics.stdev(complexities) if len(complexities) > 1 else 0.0
        std_pos = statistics.stdev(positivities) if len(positivities) > 1 else 0.0
        std_punct = statistics.stdev(puncts) if len(puncts) > 1 else 0.0
        
        if std_comp < 0.1 and std_pos < 0.1 and std_punct < 0.05:
            names = [c[0] for c in valid_chars[:3]]
            assessments.append(f"🔴 **Same Voice Syndrome**: The primary characters ({', '.join(names)}) share nearly identical dialogue textures. Consider varying sentence structures or punctuation habits to distinguish them.")
            
        return assessments

    def _diagnose_motifs(self, trace):
        assessments = []
        motif_tracker = {}
        for s in trace:
            motifs = s.get('motifs', [])
            idx = s['scene_index']
            for m in motifs:
                if m not in motif_tracker:
                    motif_tracker[m] = {'first': idx, 'last': idx, 'count': 0}
                motif_tracker[m]['last'] = idx
                motif_tracker[m]['count'] += 1
                
        total_scenes = len(trace)
        if total_scenes < 10: return []
        
        for m, data in motif_tracker.items():
            if data['count'] > 1:
                spread = data['last'] - data['first']
                if data['first'] < total_scenes * 0.3 and data['last'] > total_scenes * 0.7:
                    assessments.append(f"✨ **Successful Motif Payoff**: The object '{m}' was introduced early (Scene {data['first']}) and paid off late (Scene {data['last']}). Strong thematic resonance.")
                elif data['first'] < total_scenes * 0.3 and spread < total_scenes * 0.1:
                    assessments.append(f"🟡 **Abandoned Motif**: The object '{m}' was introduced in Scene {data['first']} but never reappears after Scene {data['last']}. Consider paying it off or cutting it.")
        
        # Sort so we only show the best ones
        # Prioritize payoffs over abandoned
        assessments.sort(key=lambda x: 'Abandoned' in x)
        return assessments[:2] # Limit to 2

    def _diagnose_tell_vs_show(self, trace):
        assessments = []
        tell_trap_ranges = self._find_ranges(trace, lambda s: s.get('tell_vs_show', {}).get('tell_ratio', 0.0) > 0.6 and s.get('tell_vs_show', {}).get('literal_emotions', 0) >= 2)
        for start, end in tell_trap_ranges:
            assessments.append(f"🟠 **'Tell, Don't Show' Trap (Scenes {start}-{end})**: Relying heavily on literal emotion words (e.g. 'sad', 'angry') in action lines rather than physical blocking/behavior.")
        return assessments[:1]

    def _find_ranges(self, trace, condition_fn):
        """Helper to find consecutive ranges where condition is true."""
        ranges = []
        in_range = False
        start_idx = -1
        
        for i, s in enumerate(trace):
            if condition_fn(s):
                if not in_range:
                    in_range = True
                    start_idx = s['scene_index']
            else:
                if in_range:
                    in_range = False
                    end_idx = trace[i-1]['scene_index']
                    ranges.append((start_idx, end_idx))
        
        # Close open range
        if in_range:
             ranges.append((start_idx, trace[-1]['scene_index']))
             
        return ranges

    def _rank_edits(self, suggestions, trace):
        """
        Sorts suggestions by estimated leverage.
        Adds root-cause context to avoid generic band-aids.
        """
        import re
        # Extract raw text suggestions
        raw_list = suggestions.get('structural_repair_strategies', [])
        prioritized = []
        
        for item in raw_list:
            # Heuristic Ranking
            score = 1
            impact_label = "Low"
            
            if "Cut" in item or "Shorten" in item: 
                score += 2
                impact_label = "Medium"
            if "fatigue" in item.lower(): 
                score += 3
                impact_label = "High" 
            if "confusion" in item.lower(): 
                score += 3
                impact_label = "High"
            
            # Formulate Actionable Advice
            clean_action = item.split(":")[0] if ":" in item else item

            # Root-Cause Contextualization
            match = re.search(r'Scene (\d+)', clean_action)
            if match:
                scene_idx = int(match.group(1))
                if "Increase stakes" in clean_action:
                    prior_stakes = [s.get('stakes', 0) for s in trace if s['scene_index'] < scene_idx and s['scene_index'] >= max(1, scene_idx - 10)]
                    if prior_stakes and max(prior_stakes) < 0.5:
                        clean_action += " (Root Cause: Stakes were never properly established in preceding scenes)"
                
                if "Cut" in clean_action or "Shorten" in clean_action:
                    clean_action += " OR insert a quiet recovery beat in the preceding scene"
            
            prioritized.append({'action': clean_action, 'leverage': impact_label, 'score': score})
            
        # Sort desc
        prioritized.sort(key=lambda x: x['score'], reverse=True)
        return prioritized

    def _build_dashboard(self, trace, genre):
        """
        Key structural checkpoints.
        """
        # Midpoint Check (Scene ~50% of length)
        mid_idx = len(trace) // 2
        midpoint_energy = trace[mid_idx]['attentional_signal'] if trace else 0
        
        # Act 1 Break (~25%)
        act1_idx = len(trace) // 4
        act1_energy = trace[act1_idx]['attentional_signal'] if trace else 0
        
        if genre in ["Avant-Garde", "Non-Linear"]:
            return {
                'midpoint_energy': round(midpoint_energy, 2),
                'midpoint_status': "Intentional Subversion",
                'act1_energy': round(act1_energy, 2),
                'total_scenes': len(trace),
                'structural_note': "Standard Hollywood pacing milestones are ignored for this genre."
            }
            
        return {
            'midpoint_energy': round(midpoint_energy, 2),
            'midpoint_status': "Healthy" if midpoint_energy > 0.5 else "Sagging",
            'act1_energy': round(act1_energy, 2),
            'total_scenes': len(trace)
        }

    # =========================================================================
    # PHASE 23: MASTERCLASS DIAGNOSTIC METHODS
    # =========================================================================

    def _diagnose_on_the_nose(self, trace):
        """
        Flag scenes where literal, on-the-nose dialogue occurs in high-tension context.
        Best subtext: characters say the OPPOSITE of what they feel under pressure.
        """
        assessments = []
        otn_ranges = self._find_ranges(trace, lambda s:
            s.get('on_the_nose', {}).get('on_the_nose_ratio', 0.0) > 0.4
            and s.get('conflict', 0) > 0.55
        )
        for start, end in otn_ranges:
            assessments.append(
                f"🔴 **On-the-Nose Dialogue (Scenes {start}-{end})**: "
                f"Characters are stating their feelings/intentions directly in a high-tension scene. "
                f"Great tension needs subtext — what are they NOT saying?"
            )
        return assessments[:1]  # Surface top hit only

    def _diagnose_shoe_leather(self, trace):
        """
        Flag scenes where too many dialogue lines at the start or end are meaningless filler.
        """
        assessments = []
        for s in trace:
            sl = s.get('shoe_leather', {})
            idx = s['scene_index']
            if sl.get('has_shoe_leather', False):
                start_filler = sl.get('scene_start_filler', 0)
                end_filler = sl.get('scene_end_filler', 0)
                loc = []
                if start_filler >= 2: loc.append("start")
                if end_filler >= 2: loc.append("end")
                assessments.append(
                    f"✂️ **Shoe-Leather Detected (Scene {idx})**: "
                    f"Filler dialogue at the {' & '.join(loc)} of the scene. "
                    f"Arrive late, leave early — cut the pleasantries."
                )
        return assessments[:2]  # Top 2 worst offenders

    def _diagnose_semantic_motifs(self, trace):
        """
        Evaluate recurring thematic terms extracted semantically (not just caps).
        Cross-reference first and last ¼ of the script to detect structural resonance.
        """
        assessments = []
        total = len(trace)
        if total < 10:
            return []

        act1_scenes = trace[:total // 4]
        act3_scenes = trace[total * 3 // 4:]

        # Collect terms from Act 1 and Act 3
        act1_terms = set()
        act3_terms = set()
        for s in act1_scenes:
            act1_terms.update(s.get('semantic_motifs', []))
        for s in act3_scenes:
            act3_terms.update(s.get('semantic_motifs', []))

        # Successful semantic payoffs
        payoffs = act1_terms.intersection(act3_terms)
        orphaned = act1_terms - act3_terms

        for term in list(payoffs)[:2]:
            assessments.append(
                f"✨ **Semantic Echo ('{term}')**: This theme/object recurs from Act 1 into Act 3. "
                f"Strong subconscious resonance for the audience."
            )
        for term in list(orphaned)[:1]:
            assessments.append(
                f"🟡 **Thematic Orphan ('{term}')**: Introduced early but never revisited. "
                f"Consider weaving it back in or cutting it."
            )
        return assessments[:2]

    def _build_character_arcs(self, trace):
        """
        Build per-character arc vector by comparing their sentiment/agency at start vs end.
        Returns a summary dict for the structural dashboard.
        """
        # Accumulate per-character data scene by scene
        char_timeline = {}  # char -> list of (scene_idx, sentiment, agency)

        for s in trace:
            vectors = s.get('character_scene_vectors', {})
            for char, data in vectors.items():
                if char not in char_timeline:
                    char_timeline[char] = []
                char_timeline[char].append({
                    'scene': s['scene_index'],
                    'sentiment': data.get('sentiment', 0.0),
                    'agency': data.get('agency', 0.0),
                    'lines': data.get('line_count', 0)
                })

        arc_summary = {}
        for char, timeline in char_timeline.items():
            if len(timeline) < 3:
                continue  # Need at least 3 appearances to track an arc

            total_lines = sum(t['lines'] for t in timeline)
            if total_lines < 8:
                continue  # Ignore minor characters

            start = timeline[0]
            end = timeline[-1]
            sentiment_delta = round(end['sentiment'] - start['sentiment'], 3)
            agency_delta = round(end['agency'] - start['agency'], 3)

            # Arc classification
            if abs(sentiment_delta) < 0.1 and abs(agency_delta) < 0.1:
                arc_label = "Flat Arc ⚠️"
                arc_note = "No measurable emotional or agency change. Is this intentional?"
            elif sentiment_delta < -0.3 and agency_delta > 0.2:
                arc_label = "Classic Tragedy 🎭"
                arc_note = "Character gains agency but loses emotional hope. Powerful arc."
            elif sentiment_delta > 0.3 and agency_delta > 0.2:
                arc_label = "Hero's Journey ⭐"
                arc_note = "Strong positive transformation in both sentiment and agency."
            elif agency_delta < -0.3:
                arc_label = "Descent 📉"
                arc_note = "Character progressively loses their ability to act. Heavy."
            else:
                arc_label = "Complex Arc 🌀"
                arc_note = "Non-standard but meaningful change detected."

            arc_summary[char] = {
                'arc_type': arc_label,
                'note': arc_note,
                'sentiment_start': start['sentiment'],
                'sentiment_end': end['sentiment'],
                'sentiment_delta': sentiment_delta,
                'agency_start': start['agency'],
                'agency_end': end['agency'],
                'agency_delta': agency_delta,
                'scenes_present': len(timeline)
            }

        return arc_summary

    # =========================================================================
    # PHASE 24: NARRATIVE INTELLIGENCE DIAGNOSTIC METHODS
    # =========================================================================

    def _diagnose_stakes_diversity(self, trace):
        """
        Warn if the entire script uses only one type of stakes (e.g., only Physical).
        A rich story layers multiple stakes types.
        """
        assessments = []
        all_dominants = [s.get('stakes_taxonomy', {}).get('dominant', 'None') for s in trace]
        unique_types = set(d for d in all_dominants if d != 'None')
        total = len([d for d in all_dominants if d != 'None'])
        if total == 0: return []

        # Find over-reliance: any single type covering >70% of scenes
        for stype in unique_types:
            count = all_dominants.count(stype)
            ratio = count / total if total > 0 else 0
            if ratio > 0.7:
                assessments.append(
                    f"⚠️ **Stakes Monoculture ({stype})**:  {round(ratio * 100)}% of your scenes rely on "
                    f"{stype} stakes only. Great scripts layer Physical, Emotional, Social, and Moral stakes. "
                    f"Consider adding a different type of risk to deepen the story."
                )
                break  # Only report the worst offender

        if len(unique_types) >= 4:
            assessments.append(
                f"✅ **Rich Stakes Ecology**: Your script uses {len(unique_types)} types of stakes "
                f"({', '.join(sorted(unique_types))}). Multi-layered jeopardy — excellent."
            )
        return assessments[:1]

    def _diagnose_stichomythia(self, trace):
        """
        Note scenes with stichomythia as a technique insight.
        """
        assessments = []
        sticho_scenes = [s['scene_index'] for s in trace if s.get('stichomythia', {}).get('has_stichomythia', False)]
        if sticho_scenes:
            n = len(sticho_scenes)
            s_list = ', '.join(str(x) for x in sticho_scenes[:3])
            assessments.append(
                f"⚡ **Stichomythia Detected (Scene{'s' if n > 1 else ''} {s_list})**: "
                f"Rapid-fire single-line exchanges — a high-energy confrontation technique. "
                f"If intentional: powerful. If accidental: check that both characters are getting full thoughts in."
            )
        return assessments[:1]

    def _diagnose_payoff_density(self, trace):
        """
        Surface scenes with Diluted Impact and credit scenes with Powerful Compression.
        """
        assessments = []
        diluted = [s['scene_index'] for s in trace if s.get('payoff_density', {}).get('label') == 'Diluted Impact']
        compressed = [s['scene_index'] for s in trace if s.get('payoff_density', {}).get('label') == 'Powerful Compression']

        if diluted:
            d_list = ', '.join(str(x) for x in diluted[:3])
            assessments.append(
                f"🔵 **Diluted Impact (Scene{'s' if len(diluted) > 1 else ''} {d_list})**: "
                f"Long scenes with low emotional density. Trim or escalate — every line should earn its keep."
            )
        if compressed:
            c_list = ', '.join(str(x) for x in compressed[:2])
            assessments.append(
                f"💎 **Powerful Compression (Scene{'s' if len(compressed) > 1 else ''} {c_list})**: "
                f"Short, dense scenes with high emotional impact. Master-class efficiency."
            )
        return assessments[:2]

    def _build_scene_purpose_map(self, trace):
        """
        Returns a scene-by-scene list of narrative purposes for the dashboard.
        Also warns if there are too many consecutive Transition scenes.
        """
        purpose_map = []
        for s in trace:
            purpose = s.get('scene_purpose', {}).get('purpose', 'Unknown')
            purpose_map.append({'scene': s['scene_index'], 'purpose': purpose})

        # Warn about too many consecutive Transition scenes
        warnings = []
        consecutive_transitions = 0
        for entry in purpose_map:
            if entry['purpose'] == 'Transition':
                consecutive_transitions += 1
                if consecutive_transitions >= 3:
                    warnings.append(f"Scene {entry['scene']}: 3+ consecutive Transition scenes — consider consolidating.")
            else:
                consecutive_transitions = 0

        return {
            'map': purpose_map,
            'transition_warnings': warnings[:2]
        }

    def _build_stakes_profile(self, trace):
        """
        Aggregate the stakes taxonomy across the whole script.
        Returns a high-level count of Physical/Emotional/Social/Moral/Existential scenes.
        """
        profile = {'Physical': 0, 'Emotional': 0, 'Social': 0, 'Moral': 0, 'Existential': 0, 'None': 0}
        for s in trace:
            dominant = s.get('stakes_taxonomy', {}).get('dominant', 'None')
            if dominant in profile:
                profile[dominant] += 1
            else:
                profile['None'] += 1
        return profile

    # =========================================================================
    # PHASE 25: SCENE-LEVEL MICRO-DRAMA METHODS
    # =========================================================================

    def _diagnose_opening_hook(self, trace):
        """Report the quality of the opening hook from Scene 0."""
        assessments = []
        if not trace: return []
        hook = trace[0].get('opening_hook', None)
        if not hook: return []

        label = hook.get('hook_label', 'Unknown')
        lines_before = hook.get('lines_before_conflict', 0)

        if label == 'Strong Hook':
            assessments.append(
                f"🎣 **Strong Opening Hook**: Conflict or tension arrives within the first few lines. "
                f"Excellent — the reader is immediately engaged."
            )
        elif label == 'Moderate Hook':
            assessments.append(
                f"🟡 **Moderate Opening Hook**: The central tension takes {lines_before} lines to appear. "
                f"Consider moving the first conflict beat earlier to grab the reader immediately."
            )
        elif label in ('Weak Hook', 'No Hook Detected'):
            assessments.append(
                f"🔴 **Weak Opening Hook**: {lines_before} lines pass before any conflict or dramatic question. "
                f"Readers and executives judge scripts on the first page. Open stronger."
            )
        return assessments[:1]

    def _diagnose_generic_dialogue(self, trace):
        """Flag the top scenes with the highest cliché dialogue ratios."""
        assessments = []
        cliche_scenes = [
            (s['scene_index'], s.get('generic_dialogue', {}))
            for s in trace
            if s.get('generic_dialogue', {}).get('cliche_ratio', 0) > 0.2
        ]
        cliche_scenes.sort(key=lambda x: x[1].get('cliche_ratio', 0), reverse=True)

        for idx, gd in cliche_scenes[:2]:
            examples = gd.get('examples', [])
            count = gd.get('cliche_count', 0)
            eg_str = f' (e.g. "{examples[0]}")' if examples else ''
            assessments.append(
                f"💬 **Generic Dialogue (Scene {idx})**: {count} interchangeable cliché line(s) detected{eg_str}. "
                f"Rewrite these to be hyper-specific to THIS character in THIS moment."
            )
        return assessments[:2]

    def _diagnose_flat_scene_turns(self, trace):
        """Flag consecutive scenes where the scene turn is flat — no dramatic movement."""
        assessments = []
        flat_ranges = self._find_ranges(trace, lambda s: s.get('scene_turn', {}).get('turn_label') == 'Flat Turn')
        for start, end in flat_ranges:
            if (end - start + 1) >= 2:
                assessments.append(
                    f"⬜ **Flat Scene Turns (Scenes {start}–{end})**: These scenes end in the same "
                    f"emotional position they began. Add a reversal, revelation, or decision to turn each scene."
                )
        return assessments[:1]

    def _build_scene_turn_map(self, trace):
        """Scene-by-scene turn type for the structural dashboard."""
        return [
            {
                'scene': s['scene_index'],
                'turn': s.get('scene_turn', {}).get('turn_label', 'Unknown'),
                'sentiment_delta': s.get('scene_turn', {}).get('sentiment_delta', 0.0)
            }
            for s in trace
        ]

    def _build_global_dialogue_ratio(self, trace, genre):
        """
        Aggregate dialogue/action ratios across all scenes.
        Compare against genre benchmarks and surface an insight.
        """
        benchmarks = {
            'action':     0.40, 'thriller':   0.45, 'horror':     0.42,
            'drama':      0.60, 'comedy':      0.65, 'romance':    0.65,
            'sci-fi':     0.50, 'avant-garde': 0.55, 'general':    0.55
        }
        total_d = sum(s.get('dialogue_action_ratio', {}).get('dialogue_lines', 0) for s in trace)
        total_a = sum(s.get('dialogue_action_ratio', {}).get('action_lines', 0) for s in trace)
        total = max(1, total_d + total_a)
        global_ratio = round(total_d / total, 3)

        benchmark = benchmarks.get(genre.lower(), 0.55)
        diff = global_ratio - benchmark

        if diff > 0.15:
            note = f"Script is {round(diff * 100)}% more dialogue-heavy than expected for {genre}. Consider adding visual storytelling."
        elif diff < -0.15:
            note = f"Script is {round(abs(diff) * 100)}% more action-heavy than expected for {genre}. Consider giving characters more voice."
        else:
            note = f"Dialogue/Action balance is within the expected range for {genre}."

        return {
            'global_dialogue_ratio': global_ratio,
            'genre_benchmark': benchmark,
            'assessment': note
        }

    # =========================================================================
    # PHASE 26: MACRO-CONSISTENCY & CRAFT QUALITY METHODS
    # =========================================================================

    def _diagnose_passive_voice(self, trace):
        """
        Flag scenes with a high ratio of passive voice in action lines.
        Passive action lines kill visual energy and slow the read.
        """
        assessments = []
        passive_scenes = [
            (s['scene_index'], s.get('passive_voice', {}))
            for s in trace
            if s.get('passive_voice', {}).get('passive_ratio', 0.0) > 0.35
        ]
        passive_scenes.sort(key=lambda x: x[1].get('passive_ratio', 0), reverse=True)

        for idx, pv in passive_scenes[:2]:
            eg = pv.get('examples', [])
            count = pv.get('passive_count', 0)
            eg_str = f' (e.g. "{eg[0][:55]}...")' if eg else ''
            assessments.append(
                f"✍️ **Passive Action Lines (Scene {idx})**: {count} passive construction(s) detected{eg_str}. "
                f"Rewrite as active: 'John opens the door' not 'The door is opened by John.'"
            )
        return assessments[:1]

    def _diagnose_tonal_whiplash(self, trace):
        """
        Compare the macro-level sentiment average of each Act.
        If Act 2 is dramatically more positive/negative than Act 1 and Act 3, flag Tonal Whiplash.
        """
        assessments = []
        if len(trace) < 9:
            return []

        third = len(trace) // 3
        act1 = trace[:third]
        act2 = trace[third:third * 2]
        act3 = trace[third * 2:]

        def avg_sentiment(scenes):
            vals = [s.get('sentiment', 0.0) for s in scenes]
            return sum(vals) / len(vals) if vals else 0.0

        s1, s2, s3 = avg_sentiment(act1), avg_sentiment(act2), avg_sentiment(act3)

        # Whiplash: Act 2 is a significant outlier from both Act 1 and Act 3
        diff_1_2 = abs(s2 - s1)
        diff_2_3 = abs(s2 - s3)

        if diff_1_2 > 0.3 and diff_2_3 > 0.3:
            direction = "significantly more positive" if s2 > s1 else "significantly darker"
            assessments.append(
                f"🎢 **Tonal Whiplash**: Act 2 (avg sentiment: {s2:.2f}) is {direction} than "
                f"Act 1 ({s1:.2f}) and Act 3 ({s3:.2f}). This tonal inconsistency may feel jarring. "
                f"Aim for a coherent emotional register across the script."
            )
        return assessments[:1]

    def _diagnose_redundant_scenes(self, trace):
        """
        Compare scene vocabulary fingerprints to flag pairs of scenes that may be
        covering the same narrative ground (same purpose + high vocabulary overlap).
        """
        assessments = []
        if len(trace) < 4:
            return []

        # Build a list of (scene_index, purpose, vocab_set) tuples
        scene_data = []
        for s in trace:
            purpose = s.get('scene_purpose', {}).get('purpose', 'Unknown')
            vocab = set(s.get('scene_vocabulary', []))
            scene_data.append((s['scene_index'], purpose, vocab))

        flagged = set()
        for i in range(len(scene_data)):
            for j in range(i + 1, len(scene_data)):
                idx_a, purpose_a, vocab_a = scene_data[i]
                idx_b, purpose_b, vocab_b = scene_data[j]

                if not vocab_a or not vocab_b:
                    continue
                if purpose_a != purpose_b:
                    continue  # Only compare same-purpose scenes

                # Jaccard similarity
                intersection = len(vocab_a & vocab_b)
                union = len(vocab_a | vocab_b)
                similarity = intersection / union if union > 0 else 0.0

                if similarity > 0.55 and (idx_a, idx_b) not in flagged:
                    flagged.add((idx_a, idx_b))
                    assessments.append(
                        f"♻️ **Possible Redundancy (Scenes {idx_a} & {idx_b})**: Both are '{purpose_a}' "
                        f"scenes with {round(similarity * 100)}% vocabulary overlap. "
                        f"They may be covering the same ground — consider merging or differentiating."
                    )

        return assessments[:2]

    def _diagnose_dangling_threads(self, trace):
        """
        Detect character pairs who interact heavily in Act 1 but never share a scene
        again in Act 2/3 — potential unresolved relationship threads.
        Uses 'character_scene_vectors' presence as a proxy for 'in this scene'.
        """
        assessments = []
        if len(trace) < 8:
            return []

        third = len(trace) // 3
        act1 = trace[:third]
        rest = trace[third:]

        # Build co-occurrence: which pairs appear together → proxy: both have vectors in same scene
        def get_characters(scene):
            return set(scene.get('character_scene_vectors', {}).keys())

        act1_pairs = {}
        for s in act1:
            chars = list(get_characters(s))
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    pair = tuple(sorted([chars[i], chars[j]]))
                    act1_pairs[pair] = act1_pairs.get(pair, 0) + 1

        # Find pairs that shared scenes in Act 1 but have zero co-occurrence after that
        rest_pairs = set()
        for s in rest:
            chars = list(get_characters(s))
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    rest_pairs.add(tuple(sorted([chars[i], chars[j]])))

        for pair, count in act1_pairs.items():
            if count >= 2 and pair not in rest_pairs:
                a, b = pair
                assessments.append(
                    f"🧵 **Dangling Thread ({a} & {b})**: These characters share {count} scene(s) together "
                    f"in Act 1 but never interact again. The audience is waiting for their story to resolve."
                )

        return assessments[:2]

    # =========================================================================
    # PHASE 27: PRODUCER'S VIEW METHODS
    # =========================================================================

    def _diagnose_protagonist_arc(self, trace):
        """
        Identify the protagonist (highest total line count) and check if their
        agency grows from Act 1 to Act 3. Flag if the hero never gains control.
        """
        assessments = []
        if len(trace) < 6: return []

        # Aggregate line counts per character across the full trace
        char_lines = {}
        for s in trace:
            for char, data in s.get('character_scene_vectors', {}).items():
                char_lines[char] = char_lines.get(char, 0) + data.get('line_count', 0)

        if not char_lines: return []
        protagonist = max(char_lines, key=char_lines.get)

        # Build protagonist's agency through each act
        third = len(trace) // 3
        def avg_agency(scenes):
            vals = [s.get('character_scene_vectors', {}).get(protagonist, {}).get('agency', None) for s in scenes]
            vals = [v for v in vals if v is not None]
            return sum(vals) / len(vals) if vals else None

        a1 = avg_agency(trace[:third])
        a3 = avg_agency(trace[third * 2:])

        if a1 is None or a3 is None: return []

        delta = a3 - a1
        if delta < -0.1:
            assessments.append(
                f"📉 **Protagonist Regression ({protagonist})**: Agency drops from "
                f"{a1:.2f} (Act 1) to {a3:.2f} (Act 3). Your protagonist ends the story "
                f"MORE passive than they started. The fundamental arc must be reactive → active."
            )
        elif abs(delta) < 0.05:
            assessments.append(
                f"⬜ **Protagonist Flat Arc ({protagonist})**: Agency stays flat "
                f"({a1:.2f} → {a3:.2f}) across the script. Is this a deliberate choice, "
                f"or does your hero need more moments of decision?"
            )
        else:
            assessments.append(
                f"✅ **Protagonist Growth ({protagonist})**: Agency rises from "
                f"{a1:.2f} → {a3:.2f}. Solid reactive-to-active transformation."
            )
        return assessments[:1]

    def _diagnose_interruption_dynamics(self, trace):
        """
        Surface the biggest interrupter and the most interrupted character.
        Insight: interruptions encode power dynamics.
        """
        assessments = []
        global_chars = {}
        for s in trace:
            per_char = s.get('interruption_patterns', {}).get('per_character', {})
            for char, data in per_char.items():
                if char not in global_chars:
                    global_chars[char] = {'interrupts': 0, 'interrupted': 0}
                global_chars[char]['interrupts'] += data.get('interrupts', 0)
                global_chars[char]['interrupted'] += data.get('interrupted', 0)

        if not global_chars: return []

        total_ints = sum(v['interrupted'] for v in global_chars.values())
        if total_ints < 3: return []

        top_interrupter = max(global_chars, key=lambda c: global_chars[c]['interrupts'])
        most_interrupted = max(global_chars, key=lambda c: global_chars[c]['interrupted'])

        if global_chars[top_interrupter]['interrupts'] > 2:
            assessments.append(
                f"⚡ **Interruption Power Dynamic**: **{top_interrupter}** dominates conversations "
                f"({global_chars[top_interrupter]['interrupts']} cut-offs). "
                f"**{most_interrupted}** rarely finishes a thought "
                f"({global_chars[most_interrupted]['interrupted']} interruptions received). "
                f"Use this intentionally — it's a strong power signal."
            )
        return assessments[:1]

    def _build_runtime_estimate(self, trace, genre):
        """
        Sum runtime contributions from all scenes to estimate total script runtime.
        Compare against genre benchmarks and flag if out of range.
        """
        total_seconds = sum(s.get('runtime_contribution', {}).get('estimated_seconds', 0) for s in trace)
        total_minutes = round(total_seconds / 60, 1)

        benchmarks = {
            'feature': (85, 125), 'drama': (90, 120), 'comedy': (85, 110),
            'thriller': (90, 120), 'horror': (80, 105), 'action': (95, 130),
            'short': (5, 30), 'pilot': (22, 65), 'general': (85, 125)
        }
        low, high = benchmarks.get(genre.lower(), (85, 125))

        if total_minutes < low:
            status = f"Under — {total_minutes} min (target: {low}–{high} min for {genre}). Script may be too short."
        elif total_minutes > high:
            status = f"Over — {total_minutes} min (target: {low}–{high} min for {genre}). Script may be too long."
        else:
            status = f"On Target — {total_minutes} min (target: {low}–{high} min for {genre})."

        return {
            'estimated_minutes': total_minutes,
            'estimated_seconds': round(total_seconds),
            'genre_target_min': low,
            'genre_target_max': high,
            'status': status
        }

    def _build_location_profile(self, trace):
        """
        Aggregate unique locations and INT/EXT balance across the script.
        Warn if >60% of scenes share the same top location.
        """
        location_counts = {}
        int_count = 0
        ext_count = 0

        for s in trace:
            loc_data = s.get('location_data', {})
            loc = loc_data.get('location', 'UNKNOWN')
            interior = loc_data.get('interior')

            location_counts[loc] = location_counts.get(loc, 0) + 1
            if interior == 'INT': int_count += 1
            elif interior == 'EXT': ext_count += 1

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

    # =========================================================================
    # PHASE 28: SYNTHESIS & STRUCTURE INTELLIGENCE METHODS
    # =========================================================================

    def _diagnose_monologues(self, trace):
        """
        Flag scenes where any character delivers a long solo speech (8+ dialogue lines).
        """
        assessments = []
        for s in trace:
            mdata = s.get('monologue_data', {})
            if mdata.get('has_monologue'):
                for m in mdata.get('monologues', []):
                    char = m.get('character', 'Unknown')
                    length = m.get('length', 0)
                    assessments.append(
                        f"🎙️ **Monologue Risk (Scene {s['scene_index']}, {char})**: "
                        f"{length}-line uninterrupted solo. Long monologues are high-risk — "
                        f"can stop a film cold if not earned. Ensure every line reveals character or advances plot."
                    )
        return assessments[:2]

    def _find_structural_turning_points(self, trace):
        """
        Identify the 4 load-bearing structural moments by peak-finding in the signal
        (conflict + stakes + sentiment_delta combined). Returns best candidate scenes.
        """
        if len(trace) < 6:
            return {'note': 'Script too short for structural analysis'}

        n = len(trace)
        third = n // 3

        def composite_signal(s):
            conflict = s.get('conflict', 0.0)
            stakes = s.get('stakes', 0.0)
            turn_delta = abs(s.get('scene_turn', {}).get('sentiment_delta', 0.0))
            economy = s.get('scene_economy', {}).get('economy_score', 0) / 10.0
            return conflict + stakes + turn_delta + economy

        # Inciting Incident: first peak in Act 1 (first 25%)
        act1_end = n // 4
        act1_signals = [(i, composite_signal(trace[i])) for i in range(act1_end)]
        inciting = max(act1_signals, key=lambda x: x[1]) if act1_signals else (0, 0)

        # Act 1 Break: peak signal in last 10% of Act 1
        a1b_start = third - n // 8
        a1b_end = third + n // 8
        a1b_signals = [(i, composite_signal(trace[i])) for i in range(max(0, a1b_start), min(n, a1b_end))]
        act1_break = max(a1b_signals, key=lambda x: x[1]) if a1b_signals else (third, 0)

        # Midpoint: peak in scenes around the script's centre
        mid = n // 2
        mid_signals = [(i, composite_signal(trace[i])) for i in range(max(0, mid - n // 8), min(n, mid + n // 8))]
        midpoint = max(mid_signals, key=lambda x: x[1]) if mid_signals else (mid, 0)

        # Darkest Moment / Act 2 Break: peak in last quarter of Act 2
        a2b_start = third * 2 - n // 8
        a2b_end = third * 2 + n // 8
        a2b_signals = [(i, composite_signal(trace[i])) for i in range(max(0, a2b_start), min(n, a2b_end))]
        act2_break = max(a2b_signals, key=lambda x: x[1]) if a2b_signals else (third * 2, 0)

        result = {
            'inciting_incident': {'scene': inciting[0], 'strength': round(inciting[1], 3)},
            'act1_break': {'scene': act1_break[0], 'strength': round(act1_break[1], 3)},
            'midpoint': {'scene': midpoint[0], 'strength': round(midpoint[1], 3)},
            'act2_break': {'scene': act2_break[0], 'strength': round(act2_break[1], 3)}
        }

        # Warn if any turning point has very low strength (flat, undramatic)
        for label, tp in result.items():
            if isinstance(tp, dict) and tp.get('strength', 1) < 0.1:
                tp['warning'] = f"This turning point is very weak — the {label.replace('_', ' ')} may be missing or underwritten."

        return result

    def _build_scene_economy_map(self, trace):
        """
        Scene-by-scene economy labels for the dashboard.
        Also surfaces a summary of low-economy scenes that may be candidates for cutting.
        """
        economy_map = [
            {
                'scene': s['scene_index'],
                'label': s.get('scene_economy', {}).get('economy_label', 'Unknown'),
                'score': s.get('scene_economy', {}).get('economy_score', 0)
            }
            for s in trace
        ]

        low_economy_scenes = [e['scene'] for e in economy_map if e['label'] == 'Low Economy']
        high_economy_scenes = [e['scene'] for e in economy_map if e['label'] == 'High Economy']

        return {
            'map': economy_map,
            'low_economy_scenes': low_economy_scenes,
            'high_economy_scenes': high_economy_scenes,
            'low_economy_count': len(low_economy_scenes),
            'cut_candidates': low_economy_scenes[:5]
        }

    def _build_narrative_summary(self, trace, genre):
        """
        Synthesize all signals into a plain-English narrative of the reader's emotional journey.
        This is the 'creative collaborator' voice — what a script editor would say to the writer.
        """
        if not trace:
            return "Unable to generate narrative summary — no scenes found."

        n = len(trace)
        third = max(1, n // 3)

        # Act-level sentiment
        def avg(scenes, key, sub=None):
            vals = []
            for s in scenes:
                v = s.get(key, 0.0)
                if sub: v = s.get(key, {}).get(sub, 0.0)
                if isinstance(v, (int, float)): vals.append(v)
            return sum(vals) / len(vals) if vals else 0.0

        s1 = avg(trace[:third], 'sentiment')
        s2 = avg(trace[third:third*2], 'sentiment')
        s3 = avg(trace[third*2:], 'sentiment')
        attention = avg(trace, 'attention')
        mid_conflict = avg(trace[third:third*2], 'conflict')

        # Opening assessment
        opening = trace[0]
        hook = opening.get('opening_hook', {})
        hook_label = hook.get('hook_label', 'Unknown') if hook else 'Unknown'

        if hook_label == 'Strong Hook':
            opening_sentence = "The script opens with immediate urgency — the reader is grabbed from the first line."
        elif hook_label == 'Moderate Hook':
            opening_sentence = "The script takes a few lines to establish tension — the opening could hit harder."
        else:
            opening_sentence = "The script's opening is slow to establish conflict — first-page urgency is missing."

        # Act 2 characterization
        if mid_conflict > 0.6:
            mid_sentence = "Act 2 is dense with conflict and escalation, keeping the pressure high."
        elif mid_conflict > 0.3:
            mid_sentence = "Act 2 maintains moderate tension but may benefit from additional escalation beats."
        else:
            mid_sentence = "Act 2 has low conflict intensity — the middle of the script risks losing the reader's engagement."

        # Ending assessment
        final_sentiment = s3
        if final_sentiment > 0.2:
            ending_sentence = "The script resolves on a relatively positive emotional note."
        elif final_sentiment < -0.2:
            ending_sentence = "The script ends on a dark or tragic note — ensure this is the intended emotional payoff."
        else:
            ending_sentence = "The script's ending is tonally ambiguous — verify this serves the story's theme."

        # Overall attention
        if attention > 0.65:
            attention_sentence = "Overall cognitive demand is high throughout, which may fatigue readers — consider strategic recovery scenes."
        elif attention > 0.4:
            attention_sentence = "Cognitive load is well-balanced, giving readers space to breathe while maintaining engagement."
        else:
            attention_sentence = "The script is low in cognitive demand — it may feel too predictable or linear in places."

        summary = f"{opening_sentence} {mid_sentence} {ending_sentence} {attention_sentence}"

        return {
            'summary': summary,
            'act1_sentiment': round(s1, 3),
            'act2_sentiment': round(s2, 3),
            'act3_sentiment': round(s3, 3),
            'overall_attention': round(attention, 3)
        }

    # =========================================================================
    # PHASE 29: READER EXPERIENCE & THEMATIC DEPTH METHODS
    # =========================================================================

    def _diagnose_reader_frustration(self, trace):
        """
        Flag the top reader-frustration scenes — unfilmable action lines,
        name crowding, or similar-sounding character names.
        """
        assessments = []

        # Internal state verbs (unfilmable)
        worst_unfilmable = sorted(
            [(s['scene_index'], s.get('reader_frustration', {})) for s in trace],
            key=lambda x: len(x[1].get('internal_state_hits', [])),
            reverse=True
        )
        for idx, rf in worst_unfilmable[:1]:
            hits = rf.get('internal_state_hits', [])
            if hits:
                eg = hits[0]
                assessments.append(
                    f"🚫 **Unfilmable Action (Scene {idx})**: Action lines describe internal states a camera cannot capture. "
                    f"e.g. *\"{eg}\"* — Show this through behaviour, not narration."
                )

        # Name crowding
        for s in trace:
            rf = s.get('reader_frustration', {})
            if rf.get('name_crowding'):
                n = rf.get('unique_char_count', 4)
                assessments.append(
                    f"👥 **Name Flood (Scene {s['scene_index']})**: {n} characters introduced in one scene. "
                    f"Readers struggle to track more than 2-3 new names at once. Stagger introductions."
                )
                break

        # Similar name pairs
        for s in trace:
            rf = s.get('reader_frustration', {})
            pairs = rf.get('similar_name_pairs', [])
            if pairs:
                assessments.append(
                    f"🔤 **Confusing Names (Scene {s['scene_index']})**: {pairs[0]} sound too similar. "
                    f"Readers will mix them up. One rename is worth 10 clarifying rewrites."
                )
                break

        return assessments[:2]

    def _diagnose_neglected_characters(self, trace):
        """
        Find characters with significant Act 1 presence who disappear in Act 3.
        """
        assessments = []
        if len(trace) < 8: return []

        third = len(trace) // 3
        act1 = trace[:third]
        act3 = trace[third * 2:]

        def char_lines(scenes):
            counts = {}
            for s in scenes:
                for char, data in s.get('character_scene_vectors', {}).items():
                    counts[char] = counts.get(char, 0) + data.get('line_count', 0)
            return counts

        act1_counts = char_lines(act1)
        act3_counts = char_lines(act3)

        # Characters with significant Act 1 presence (>5 lines) but no Act 3 presence
        neglected = [
            char for char, count in act1_counts.items()
            if count > 5 and act3_counts.get(char, 0) == 0
        ]

        for char in neglected[:2]:
            assessments.append(
                f"👻 **Neglected Character ({char})**: Present in Act 1 ({act1_counts[char]} lines) "
                f"but completely absent in Act 3. The audience will notice and feel cheated. "
                f"Either pay them off or reduce their Act 1 presence."
            )
        return assessments[:2]

    def _diagnose_nonlinear_structure(self, trace):
        """
        Report on any non-linear scenes (flashback, dream, flash forward).
        Alert the writer if non-linear scenes are structurally misplaced.
        """
        assessments = []
        nonlinear_scenes = [
            (s['scene_index'], s.get('nonlinear_tag', {}).get('type'))
            for s in trace
            if s.get('nonlinear_tag', {}).get('is_nonlinear')
        ]

        if not nonlinear_scenes:
            return []

        types = list(set(t for _, t in nonlinear_scenes))
        count = len(nonlinear_scenes)

        if count > 5:
            assessments.append(
                f"⏳ **Non-linear Heavy Script**: {count} non-linear scenes detected "
                f"({', '.join(types)}). Heavy non-linearity fragments narrative momentum — "
                f"ensure each flashback delivers information unavailable any other way."
            )
        elif count > 0:
            locs = ', '.join(f"Scene {i}" for i, _ in nonlinear_scenes[:3])
            assessments.append(
                f"⏳ **Non-linear Scenes Detected** ({locs}): {types[0]} used. "
                f"Non-linear scenes are excluded from standard structural expectations. "
                f"Confirm each one is load-bearing — if you can cut it, cut it."
            )
        return assessments[:1]

    def _diagnose_theme_coherence(self, trace):
        """
        Aggregate thematic clusters across the full script and check Act-level consistency.
        Flag if the dominant theme shifts significantly between Acts.
        """
        assessments = []
        if len(trace) < 4: return []

        third = max(1, len(trace) // 3)

        def dominant_theme(scenes):
            agg = {}
            for s in scenes:
                for theme, score in s.get('thematic_clusters', {}).get('theme_scores', {}).items():
                    agg[theme] = agg.get(theme, 0) + score
            if not agg: return None
            return max(agg, key=agg.get)

        t1 = dominant_theme(trace[:third])
        t2 = dominant_theme(trace[third:third*2])
        t3 = dominant_theme(trace[third*2:])

        # Script-wide dominant theme
        all_themes = {}
        for s in trace:
            for theme, score in s.get('thematic_clusters', {}).get('theme_scores', {}).items():
                all_themes[theme] = all_themes.get(theme, 0) + score

        if not all_themes:
            return []

        top_global = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:2]
        global_themes = [t for t, _ in top_global]

        # Check for thematic drift between acts
        themes = [t for t in [t1, t2, t3] if t]
        if len(set(themes)) == len(themes) and len(themes) == 3:
            assessments.append(
                f"🎭 **Thematic Drift**: Dominant theme shifts each Act "
                f"({t1} → {t2} → {t3}). Strong scripts stay anchored to 1-2 core themes. "
                f"Your script appears to be exploring '{global_themes[0]}' overall — "
                f"consider threading it more consistently across all 3 Acts."
            )
        else:
            if global_themes:
                assessments.append(
                    f"✅ **Thematic Coherence**: Core themes are "
                    f"**{global_themes[0]}**{(' & **' + global_themes[1] + '**') if len(global_themes) > 1 else ''} "
                    f"— consistent across Acts. Strong thematic spine."
                )
        return assessments[:1]
