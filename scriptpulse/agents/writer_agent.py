import random
import re
import statistics

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
        
        # 1. Narrative Diagnosis (Start with existing cognitive insights from InterpretationAgent)
        narrative_health = final_output.get('narrative_diagnosis', [])
        
        # Phase 22-30 diagnostics (Collected and sorted for score determinism)
        new_diagnostics = []
        new_diagnostics.extend(self._diagnose_health(trace, genre))
        new_diagnostics.extend(self._diagnose_voice(final_output.get('voice_fingerprints', {})))
        new_diagnostics.extend(self._diagnose_motifs(trace))
        new_diagnostics.extend(self._diagnose_tell_vs_show(trace))
        new_diagnostics.extend(self._diagnose_on_the_nose(trace))
        new_diagnostics.extend(self._diagnose_shoe_leather(trace))
        new_diagnostics.extend(self._diagnose_semantic_motifs(trace))
        new_diagnostics.extend(self._diagnose_stakes_diversity(trace))
        new_diagnostics.extend(self._diagnose_stichomythia(trace))
        new_diagnostics.extend(self._diagnose_payoff_density(trace))
        new_diagnostics.extend(self._diagnose_opening_hook(trace))
        new_diagnostics.extend(self._diagnose_generic_dialogue(trace))
        new_diagnostics.extend(self._diagnose_flat_scene_turns(trace))
        new_diagnostics.extend(self._diagnose_passive_voice(trace))
        new_diagnostics.extend(self._diagnose_tonal_whiplash(trace))
        new_diagnostics.extend(self._diagnose_redundant_scenes(trace))
        new_diagnostics.extend(self._diagnose_dangling_threads(trace))
        new_diagnostics.extend(self._diagnose_protagonist_arc(trace))
        new_diagnostics.extend(self._diagnose_interruption_dynamics(trace))
        new_diagnostics.extend(self._diagnose_monologues(trace))
        new_diagnostics.extend(self._diagnose_reader_frustration(trace))
        new_diagnostics.extend(self._diagnose_neglected_characters(trace))
        new_diagnostics.extend(self._diagnose_nonlinear_structure(trace))
        new_diagnostics.extend(self._diagnose_theme_coherence(trace))
        
        # Determine unique items and sort EVERYTHING for absolute score determinism
        # This ensures the penalty calculation always sees the exact same input order.
        all_diagnostics = sorted(list(set(narrative_health + new_diagnostics + self._diagnose_representation_risks(final_output.get('fairness_audit', {})))))
        
        # 2. Structural Dashboard with Arc Vectors + Scene Map
        dashboard = self._build_dashboard(trace, genre, final_output)
        dashboard['character_arcs'] = self._build_character_arcs(trace)
        dashboard['scene_purpose_map'] = self._build_scene_purpose_map(trace)
        dashboard['stakes_profile'] = self._build_stakes_profile(trace)
        dashboard['scene_turn_map'] = self._build_scene_turn_map(trace)
        dashboard['dialogue_action_ratio'] = self._build_global_dialogue_ratio(trace, genre)
        
        # Phase 27-28 additions
        dashboard['runtime_estimate'] = self._build_runtime_estimate(trace, genre)
        dashboard['location_profile'] = self._build_location_profile(trace)
        dashboard['structural_turning_points'] = self._find_structural_turning_points(trace)
        dashboard['scene_economy_map'] = self._build_scene_economy_map(trace)
        dashboard['page_turner_index'] = self._calculate_page_turner_index(trace)
        dashboard['writing_texture'] = self._diagnose_writing_texture(trace)
        dashboard['act_structure'] = self._build_act_structure(trace)
        dashboard['commercial_comps'] = self._find_commercial_comps(genre, dashboard.get('stakes_profile', {}).get('dominant', 'Social'))
        # Merge character fragments (e.g. MICHAEL vs MICHAEL CORLEONE) for accurate thresholding
        v_fingerprints = final_output.get('voice_fingerprints', {})
        merged_casts = {}
        generic_roles = {'MAN', 'WOMAN', 'VOICE', 'GUARD', 'SOLDIER', 'WAITER', 'DRIVER', 'OFFICER', 'COP', 'GUEST'}
        
        # Sort names by number of words (longest name first) to find parent personae
        sorted_names = sorted(v_fingerprints.keys(), key=lambda x: len(x.split()), reverse=True)
        for name in sorted_names:
            line_count = v_fingerprints[name].get('line_count', 0)
            if not name: continue
            
            found_parent = False
            name_parts = set(name.split())
            
            # If it's a generic role with a number (MAN 1), don't merge based on 'MAN'
            is_generic = any(g in name_parts for g in generic_roles)
            
            for existing in merged_casts:
                existing_parts = set(existing.split())
                overlap = name_parts.intersection(existing_parts)
                
                # Merge if they share a non-generic word, or if one is a signature word
                if overlap and not (is_generic and len(overlap) == 1):
                    merged_casts[existing] += line_count
                    found_parent = True
                    break
            
            if not found_parent:
                merged_casts[name] = line_count
                
        dashboard['cast_count_deterministic'] = len([c for c, count in merged_casts.items() if count >= 5])

        # Market Readiness (Task 5)
        dashboard['market_readiness'] = self._calculate_market_readiness(dashboard)

        # Composite ScriptPulse Score (0-100) using the truly sorted diagnostics
        dashboard['scriptpulse_score'] = self._calculate_scriptpulse_score(dashboard, all_diagnostics)
        
        # Inject into output (Removing prescriptive 'rewrite_priorities')
        final_output['writer_intelligence'] = {
            'narrative_diagnosis': all_diagnostics[:15],
            'structural_dashboard': dashboard,
            'narrative_summary': self._build_narrative_summary(trace, genre, all_diagnostics),
            'creative_provocations': self._generate_creative_provocations(all_diagnostics, genre),
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
                    assessments.append(
                        f"🔴 **Sustained Intensity (Scenes {start}-{end})**: Consistently high attentional demand for ~{duration_mins} mins. May lead to audience fatigue."
                    )

        # 2. Confusion Clustering
        strain_ranges = self._find_ranges(trace, lambda s: s.get('expectation_strain', 0) > 0.8)
        for start, end in strain_ranges:
             assessments.append(
                 f"🟠 **Information Density (Scenes {start}-{end})**: High volume of new narrative elements. May increase cognitive load for the reader."
             )
            
        # 3. Boredom vs Tense Silence
        # Tightened for slow-burn masters: only flag if valley is too long (5+ scenes)
        true_boredom_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) <= 0.5)
        for start, end in true_boredom_ranges:
            if (end - start + 1) >= 5: # Reward 2-4 scene valleys as 'effective recovery'
                 assessments.append(
                     f"🔵 **Engagement Drop (Scenes {start}-{end})**: Attentional signals are low for an extended duration. Consider tightening the pacing or adding a 'hook' to keep the audience locked in."
                 )

        tense_silence_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) > 0.6)
        for start, end in tense_silence_ranges:
            if (end - start + 1) >= 2:
                 assessments.append(
                     f"🤫 **Tense Silence (Scenes {start}-{end})**: Low dialogue density but high conflict. Effective subtextual tension."
                 )

        # 4. Exposition Clustering
        expo_ranges = self._find_ranges(trace, lambda s: s.get('exposition_score', 0) > 0.7)
        for start, end in expo_ranges:
            assessments.append(
                f"💬 **Exposition Heavy (Scenes {start}-{end})**: Characters are explaining details explicitly rather than through action."
            )

        # 5. Pacing Volatility (The 'Avant-Garde' Special)
        volatility_ranges = self._find_ranges(trace, lambda s: s.get('pacing_volatility', 0) > 0.8)
        for start, end in volatility_ranges:
            assessments.append(
                f"🎢 **Erratic Pacing (Scenes {start}-{end})**: Extreme shifts in rhythm. Use sparingly for effect."
            )

        # 6. Irony / Dissonance
        irony_ranges = self._find_ranges(trace, lambda s: s.get('sentiment', 0) > 0.6 and s.get('conflict', 0) > 0.7)
        for start, end in irony_ranges:
             assessments.append(
                f"🎭 **Irony Detected (Scenes {start}-{end})**: Positive tone matches high conflict. Unsettling and effective."
            )
            
        # 7. Final Polish
        if not assessments:
            assessments.append("🟢 **Good Flow**: The story moves well.")
            
        return assessments

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
        if isinstance(suggestions, list):
            raw_list = suggestions
        else:
            raw_list = suggestions.get('structural_repair_strategies', [])
        prioritized = []
        
        for item in raw_list:
            # Heuristic Ranking
            score = 1
            impact_label = "Low"
            
            if "Cut" in item or "Shorten" in item: 
                score += 2
                impact_label = "Medium"

            # v2.0 Fix: Robustly extract text from both string and dict suggestions
            if isinstance(item, dict):
                suggestion_text = item.get('strategy', item.get('diagnosis', 'Unknown Suggestion'))
                # Also check tactics
                tactics = item.get('tactics', [])
                if tactics: suggestion_text += f": {', '.join(tactics)}"
            else:
                suggestion_text = str(item)

            clean_action = suggestion_text.split(":")[0] if ":" in suggestion_text else suggestion_text
            item_str = suggestion_text.lower()

            if "fatigue" in item_str: 
                score += 3
                impact_label = "High" 
            if "confusion" in item_str: 
                score += 3
                impact_label = "High"
            # Root-Cause Contextualization (Use clean_action which is now guaranteed to be a string)
            match = re.search(r'Scene (\d+)', clean_action)
            if match:
                scene_idx_str = match.group(1)
                try:
                    scene_idx = int(scene_idx_str)
                except ValueError:
                    scene_idx = -1
                    
                if scene_idx >= 0:
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

    def _build_dashboard(self, trace, genre, report=None):
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
            'total_scenes': len(trace),
            'production_risk_score': self._calculate_production_risks(trace),
            'budget_impact': self._calculate_budget_impact(trace, report)
        }

    # =========================================================================
    # PHASE 23: MASTERCLASS DIAGNOSTIC METHODS
    # =========================================================================

    def _diagnose_on_the_nose(self, trace):
        """
        Identify scenes where characters say exactly what they are thinking/feeling.
        Threshold: >25% on-the-nose dialogue hits.
        """
        assessments = []
        for s in trace:
            otn = s.get('on_the_nose', {})
            idx = s['scene_index']
            rep = s.get('representative_dialogue', '')
            if otn.get('on_the_nose_ratio', 0) > 0.25:
                quote = f" (e.g., \"{rep[:60]}...\")" if rep else ""
                assessments.append(
                    f"🗣️ **On-The-Nose Dialogue (Scene {idx})**: Characters are stating their internal subtext as text{quote}. "
                    f"Subvert the lines to hide the real emotion behind a defensive or tactical goal."
                )
        return assessments[:2]

    def _diagnose_shoe_leather(self, trace):
        """
        Flag scenes where too many dialogue lines at the start or end are meaningless filler.
        """
        assessments = []
        for s in trace:
            sl = s.get('shoe_leather', {})
            idx = s['scene_index']
            rep = s.get('representative_dialogue', '')
            if sl.get('has_shoe_leather', False):
                quote = f" (e.g., \"{rep[:60]}...\")" if rep else ""
                assessments.append(
                    f"✂️ **Shoe-Leather Detected (Scene {idx})**: "
                    f"Filler dialogue at the start or end of the scene{quote}. "
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
        char_timeline = {}
        for s in trace:
            for char, data in s.get('character_scene_vectors', {}).items():
                if char not in char_timeline:
                    char_timeline[char] = []
                char_timeline[char].append({
                    'scene': s['scene_index'],
                    'sentiment': data.get('sentiment', 0.0),
                    'agency': data.get('agency', 0.0),
                    'lines': data.get('line_count', 0),
                    'resolved': s.get('narrative_closure', False) # Track if the scene resolved them
                })

        arc_summary = {}
        total_scenes = max([s.get('scene_index', 0) for s in trace]) if trace else 100
        
        for char, timeline in sorted(char_timeline.items()):
            if len(timeline) < 3:
                continue  # Need at least 3 appearances to track an arc

            total_lines = sum(t['lines'] for t in timeline)
            if total_lines < 8:
                continue  # Ignore minor characters

            start = timeline[0]
            end = timeline[-1]
            sentiment_delta = round(end['sentiment'] - start['sentiment'], 3)
            agency_delta = round(end['agency'] - start['agency'], 3)

            # High Fidelity Resolution Logic
            # (New logic: must be before final 10% of script to be an 'Exit')
            is_near_end = end.get('scene', 0) > (total_scenes * 0.9)
            has_resolved_signal = timeline[-1].get('resolved', False) or (len(timeline) > 1 and timeline[-2].get('resolved', False))

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
                    f"⚠️ **Stakes Concentration ({stype})**: {round(ratio * 100)}% of the narrative relies on "
                    f"{stype} stakes. This pattern limits layered jeopardy across Physical, Emotional, Social, and Moral domains."
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
        flat_ranges = self._find_ranges(trace, lambda s: s.get('scene_turn', {}).get('turn_label') == 'Flat')
        for start, end in flat_ranges:
            if (end - start + 1) >= 2:
                assessments.append(
                    f"⬜ **Flat Scene Turns (Scenes {start}–{end})**: Emotional trajectory remains stagnant. These scenes end in the same relative position they began."
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
            'action':      0.40, 'thriller':    0.45, 'horror':      0.42,
            'drama':       0.60, 'crime drama': 0.58, 'comedy':      0.65, 
            'romance':     0.65, 'sci-fi':      0.50, 'avant-garde': 0.55, 
            'general':     0.55
        }
        total_d = sum(s.get('dialogue_action_ratio', {}).get('dialogue_lines', 0) for s in trace)
        total_a = sum(s.get('dialogue_action_ratio', {}).get('action_lines', 0) for s in trace)
        total = max(1, total_d + total_a)
        global_ratio = round(total_d / total, 3)

        benchmark = benchmarks.get(genre.lower(), 0.55)
        diff = global_ratio - benchmark

        if diff > 0.12:
            note = f"Script is {round(diff * 100)}% more dialogue-heavy than genre expectations for {genre}."
        elif diff < -0.15:
            note = f"Script is {round(abs(diff) * 100)}% more action-heavy than genre expectations for {genre}."
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
                f"Active voice typically increases cinematic energy."
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
        rest_individual_chars = set()
        rest_pairs = set()
        for s in rest:
            chars = list(get_characters(s))
            rest_individual_chars.update(chars)
            for i in range(len(chars)):
                for j in range(i + 1, len(chars)):
                    rest_pairs.add(tuple(sorted([chars[i], chars[j]])))

        # Detect character 'exits' (deaths/departures)
        last_appearance = {}
        for s in trace:
            for char in get_characters(s):
                last_appearance[char] = s['scene_index']
        
        total_scenes = len(trace)

        for pair, count in act1_pairs.items():
            if count >= 3 and pair not in rest_pairs:
                a, b = pair
                # Only flag if both characters remain in the script well after their last interaction
                # If one character stops appearing shortly after, it's a resolution (death/exit).
                a_exit = last_appearance.get(a, 0)
                b_exit = last_appearance.get(b, 0)
                
                # If both characters are still around 15% of the script later but haven't interacted, it's dangling
                if a in rest_individual_chars and b in rest_individual_chars:
                    # Threshold for 'still around' - if they both appear in the final act
                    if a_exit > total_scenes * 0.8 and b_exit > total_scenes * 0.8:
                        assessments.append(
                            f"🧵 **Dangling Thread ({a} & {b})**: These characters share {count} scene(s) together "
                            f"in Act 1 but never interact again despite both being present in the finale. "
                            f"The audience is waiting for their story to resolve."
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
        if delta < -0.15:
            assessments.append(
                f"📉 **Protagonist Regression ({protagonist})**: Agency drops from "
                f"{a1:.2f} (Act 1) to {a3:.2f} (Act 3). Your protagonist ends the story "
                f"MORE passive than they started."
            )
        elif delta > 0.3:
             assessments.append(
                f"📈 **Protagonist Ascension ({protagonist})**: Agency spikes from "
                f"{a1:.2f} → {a3:.2f}. A powerful transformation from reactive to total command."
            )
        elif abs(delta) < 0.015:
            assessments.append(
                f"⬜ **Protagonist Flat Arc ({protagonist})**: Agency stays flat "
                f"({a1:.2f} → {a3:.2f}) across the script."
            )
        else:
            assessments.append(
                f"✅ **Protagonist Growth ({protagonist})**: Agency rises from "
                f"{a1:.2f} → {a3:.2f}. Standard reactive-to-active transformation."
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
            'feature': (85, 130), 
            'drama': (90, 150),       # Expanded for prestige drama
            'crime drama': (100, 180), # Epic crime dramas like The Godfather
            'comedy': (85, 110),
            'thriller': (90, 130), 
            'horror': (80, 105), 
            'action': (95, 140),
            'short': (5, 30), 
            'pilot': (22, 65), 
            'general': (85, 130),
            'avant-garde': (70, 100) 
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

    def _build_narrative_summary(self, trace, genre, diagnostics):
        """
        Synthesize all signals into a dynamic narrative of the reader's emotional journey.
        Builds 8–10 conditional sentence templates that activate based on script-specific spikes.
        """
        if not trace: return "Unable to generate summary."
        diag_str = " ".join(diagnostics) if diagnostics else ""
        
        # 1. Opening Intelligence
        hook = trace[0].get('opening_hook', {})
        if hook.get('hook_label') == 'Strong Hook':
            opening = "Your opening establishes immediate dominance — the audience is engaged from the first beat."
        elif "slow" in diag_str.lower():
            opening = "The script opens with a measured, intentional focus on atmosphere before the primary conflict ignites."
        else:
            opening = "The opening takes its time to establish character stakes, which fits the genre rhythm."

        # 2. Dynamic Spike Intelligence (Look for highest tension scene)
        max_t = max([s.get('attentional_signal', 0) for s in trace])
        peak_idx = next(i for i, s in enumerate(trace) if s.get('attentional_signal', 0) == max_t)
        spike_text = f"The narrative reaches an intense cognitive peak around Scene {peak_idx+1}, a moment of critical audience payoff."

        # 3. Dynamic Flag Intelligence
        specifics = []
        if "Same Voice Syndrome" in diag_str:
            specifics.append("The dialogue shows high phonetic overlap, suggesting your characters share similar speech rhythms.")
        if "Passive Protagonist" in diag_str:
            specifics.append("The protagonist currently faces high narrative resistance, making their journey reactive in the second act.")
        if "On-The-Nose" in diag_str:
            specifics.append("There are moments where characters state their interior subtext directly, potentially diluting the dramatic irony.")
        if "Tonal Whiplash" in diag_str:
            specifics.append("The script undergoes rapid emotional shifts that challenge the reader's cognitive framing.")
        
        # 4. Closing / Payoff
        s3 = sum([s.get('sentiment', 0) for s in trace[-(len(trace)//3):]]) / (len(trace)//3 or 1)
        if s3 < -0.3:
            closing = "The journey concludes with a definitive tragic descent, delivering a soul-crushing emotional payoff."
        elif s3 > 0.3:
            closing = "The story resolves with a hard-earned sense of triumph and narrative closure."
        else:
            closing = "The resolution maintains an ambiguous emotional tone, consistent with complex prestige dramas."

        # Aggregate summary
        summary = f"{opening} {spike_text} " + " ".join(specifics[:2]) + f" {closing}"
        return {'summary': summary.strip()}

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
                    f"🚫 **Action Line Modifiers (Scene {idx})**: Action lines contain descriptors defining internal states. "
                    f"e.g. \"{eg}\""
                )

        # Name crowding
        for s in trace:
            rf = s.get('reader_frustration', {})
            if rf.get('name_crowding'):
                n = rf.get('unique_char_count', 4)
                assessments.append(
                    f"👥 **Character Density (Scene {s['scene_index']})**: {n} distinct characters are active simultaneously. "
                    f"This creates a high referential load for the audience."
                )
                break

        # Similar name pairs
        for s in trace:
            rf = s.get('reader_frustration', {})
            pairs = rf.get('similar_name_pairs', [])
            if pairs:
                assessments.append(
                    f"🔤 **Orthographic Proximity (Scene {s['scene_index']})**: Character names {pairs[0]} are lexically or phonetically similar. "
                    f"This pattern frequently correlates with reader confusion tracking dialogue tags."
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
        
        # Sort for determinism
        neglected.sort()
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
    def _generate_creative_provocations(self, diagnosis, genre):
        """Generates mentor-like questions to push the writer's craft further."""
        provocations = []
        diag_str = " ".join(diagnosis) if diagnosis else ""
        
        # Mapping Flags to Masterclass Questions (Task 6)
        mapping = {
            'Same Voice Syndrome': "Your leads share similar dialogue rhythms. What is one specific verbal habit you could give your protagonist that their rival would *never* use?",
            'Flat Arc': "This character remains emotionally static. If they don't change, is the *world* changing around them to highlight their refusal to adapt?",
            'On-The-Nose': "In your most intense scene, a character states exactly what they feel. What could they say instead that hides their true intent but reveals their desperation?",
            'Attentional Valley': "Engagement dips over multiple scenes here. Who is winning the 'Invisible Power Struggle' while no one is shouting?",
            'Passive Protagonist': "The story is pushing the hero. What decision can they make right now that would burn their bridges and force the plot to follow them?",
            'Similar Names': "The reader may confuse your leads. Can you give one a specific physical vocal quirk or a recurring linguistic motif to differentiate them?",
            'Tonal Whiplash': "The script undergoes an extreme shifts. Is this a deliberate subversion of audience expectations, or is it breaking the story's reality?",
            'Redundant Scenes': "These scenes serve the same purpose. Which one has more 'Cinematic Economy'? Combine them into a single high-impact sequence.",
            'Tell vs Show': "You're describing internal thoughts in action lines. How can you translate that feeling into a purely visual piece of behavior?"
        }
        
        for flag, question in mapping.items():
            if flag in diag_str:
                provocations.append(question)
                
        # Fillers if no flags
        if not provocations:
            provocations = [
                "What is the one thing your protagonist wants so badly they would burn their life down to get it?",
                "In your quietest scene, what is the 'Invisible Conflict' that keeps the audience leaning in?"
            ]
            
        return list(set(provocations))[:3]



        






    def _calculate_page_turner_index(self, trace):
        """
        Calculates PTI (0-100) based on Dramatic Contrast and Resonance.
        A 'Page-Turner' isn't just constant shouting; it's the rhythm of tension and relief.
        """
        if not trace: return 50
        
        # 1. Emotional Contrast: The standard deviation of the signal
        # High contrast means the writer is using the 'Valley' effect correctly.
        # Threshold: 0.18 is a strong delta for a normalized 0-1 signal.
        signals = [s.get('attentional_signal', 0) for s in trace]
        contrast = statistics.stdev(signals) if len(signals) > 1 else 0
        contrast_score = min(1.0, contrast / 0.18) * 35 # 35 pts for contrast
        
        # 2. Hook Density: Use Cognitive Resonance (Impact vs just Volume)
        # Average resonance of 0.35 is quite high for a script with breathers.
        resonance = sum(s.get('cognitive_resonance', 0) for s in trace) / len(trace)
        resonance_score = min(1.0, resonance / 0.35) * 45 # 45 pts for impact
        
        # 3. Cliffhangers: Scenes ending on high-intensity signals
        cliff_count = sum(1 for s in trace if s.get('attentional_signal', 0) > 0.82)
        cliffhangers = (min(cliff_count, 4) * 5) # 20 pts for peaks
        
        # Base completion bonus (20%) + Metrics
        return min(100, round(20 + (contrast_score + resonance_score + cliffhangers) * 0.8))

    def _diagnose_writing_texture(self, trace):
        """Identifies if the script is 'Cinematic' (lean) or 'Novelistic' (dense)."""
        action_densities = [s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace]
        avg_action = sum(action_densities) / len(trace) if trace else 0
        
        if avg_action > 10: return "Novelistic / Literary"
        if avg_action < 4: return "Sparse / Minimalist"
        return "Cinematic / Visual"

    def _find_commercial_comps(self, genre, dominant_stakes='Social'):
        """Task 3: Subgenre-aware matching for feature films only."""
        # Map Dominant Stakes to specialized 'Subgenres'
        stakes_to_sub = {
            'Social': 'Political/Mob/Society',
            'Moral': 'Psychological/Moral',
            'Emotional': 'Personal/Relational',
            'Physical': 'Visceral/Action',
            'Existential': 'Philosophical/Surreal'
        }
        subgenre = stakes_to_sub.get(dominant_stakes, 'General')
        
        lookup = {
            ('Crime', 'Political/Mob/Society'): ["The Godfather", "The Departed", "The Irishman"],
            ('Crime', 'Psychological/Moral'): ["Chinatown", "No Country for Old Men", "Heat"],
            ('Drama', 'Personal/Relational'): ["Marriage Story", "Ordinary People", "Lady Bird"],
            ('Drama', 'Political/Mob/Society'): ["The Social Network", "Parasite", "The Big Short"],
            ('Action', 'Visceral/Action'): ["Mad Max: Fury Road", "Die Hard", "John Wick"],
            ('Action', 'Personal/Relational'): ["Logan", "The Dark Knight", "Gladiator"],
            ('Horror', 'Philosophical/Surreal'): ["Hereditary", "The Shining", "Midsommar"],
            ('Horror', 'Visceral/Action'): ["Halloween", "A Quiet Place", "The Conjuring"],
            ('Sci-Fi', 'Philosophical/Surreal'): ["2001: A Space Odyssey", "Arrival", "Blade Runner 2049"],
            ('Sci-Fi', 'Psychological/Moral'): ["Gattaca", "Children of Men", "Ex Machina"],
            ('Thriller', 'Political/Mob/Society'): ["Gone Girl", "Seven", "Prisoners"],
            ('Comedy', 'Political/Mob/Society'): ["Knives Out", "Glass Onion", "The Favorite"],
            ('Comedy', 'Personal/Relational'): ["Little Miss Sunshine", "The Holdovers", "Planes, Trains and Automobiles"],
            ('Romance', 'Personal/Relational'): ["Before Sunrise", "Normal People", "The Notebook"]
        }
        
        g = genre.replace('-', ' ').split()[0].title() 
        if 'Sci' in g: g = 'Sci-Fi'
        
        # Primary Match: Genre + Subgenre
        key = (g, subgenre)
        if key in lookup: return lookup[key]
        
        # Secondary Match: Just Genre + any stake
        for k_g, k_s in lookup.keys():
            if k_g == g: return lookup[(k_g, k_s)]
            
        return ["The Social Network", "Parasite", "Pulp Fiction"] # Ultimate fallbacks

    def _calculate_production_risks(self, trace):
        """
        Calculates Risk Radar (Complexity vs Impact).
        Payoff is now determined by PEAK Intensity (Memorial moments) rather than average flow.
        """
        if not trace: return 50
        
        # Payoff is the top 20% of engagement moments — do the highs justify the costs?
        sorted_signals = sorted([s.get('attentional_signal', 0) for s in trace], reverse=True)
        top_n = max(1, len(sorted_signals) // 5)
        peak_payoff = sum(sorted_signals[:top_n]) / top_n
        
        # Complexity is raw action density
        complexity = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        
        # Risk is high if we have expensive complexity but the 'Peaks' are underwhelming
        risk_score = (complexity * 65) + ((1.0 - peak_payoff) * 35)
        return round(min(100, max(0, risk_score)))

    def _calculate_budget_impact(self, trace, report=None):
        """Estimates relative budget intensity based on location churn, cast size, and action density."""
        if not trace: return "Low"
        # Fix: Look into location_data which was injected in runner.py
        locs = set()
        for s in trace:
            loc = s.get('location_data', {}).get('location') or s.get('location', 'Unknown')
            if loc != 'Unknown':
                locs.add(loc)
        
        unique_locs = len(locs)
        avg_action = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        
        # Cast size factor
        cast_size = 0
        if report and 'voice_fingerprints' in report:
            cast_size = len(report['voice_fingerprints'])
            
        score = (unique_locs * 1.5) + (avg_action * 4) + (cast_size * 0.5)
        
        if score > 100 or unique_locs > 50 or cast_size > 40: return "Blockbuster / High"
        if score > 35: return "Medium / Standard"
        return "Lean / Indie"

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

    def _diagnose_representation_risks(self, fairness_audit):
        """Surfaces critical representation risks from the Ethics Agent."""
        assessments = []
        risks = fairness_audit.get('stereotyping_risks', [])
        for risk in risks:
            if "punching down" in risk.lower():
                assessments.append(f"⚖️ **Representation Risk**: {risk}")
            else:
                assessments.append(f"👥 **Character Dynamic**: {risk}")
        return assessments[:2]

    # =========================================================================
    # SCRIPTPULSE SCORE & ACT STRUCTURE
    # =========================================================================

    def _build_act_structure(self, trace):
        """Calculates act-by-act distribution and Violence Weighting (Task 4)."""
        n = len(trace)
        if n == 0:
            return {'act1': 0, 'act2': 0, 'act3': 0, 'act1_pct': 0, 'act2_pct': 0, 'act3_pct': 0, 'balance': 'Unknown', 'violence_count': [0,0,0]}
        
        # Boundaries
        act1_end = max(1, n // 4)
        act3_start = max(act1_end + 1, n - (n // 4))
        
        # Violence Counting: shootings, deaths, confrontations
        v_triggers = ['shot', 'killed', 'blood', 'gun', 'attack', 'dead', 'murder', 'fight', 'trap', 'ambush']
        violence = [0, 0, 0]
        
        for i, s in enumerate(trace):
            is_violent = s.get('sentiment', 0) < -0.8 and any(w in str(s).lower() for w in v_triggers)
            if i < act1_end: violence[0] += 1 if is_violent else 0
            elif i < act3_start: violence[1] += 1 if is_violent else 0
            else: violence[2] += 1 if is_violent else 0

        act1_count = act1_end
        act2_count = act3_start - act1_end
        act3_count = n - act3_start
        
        act1_pct = round(act1_count / n * 100)
        act2_pct = round(act2_count / n * 100)
        act3_pct = round(act3_count / n * 100)
        
        balance = "Balanced"
        if act1_pct > 35: balance = "Extended Act 1 Setup"
        elif act3_pct > 35: balance = "Extended Act 3 Resolution"
        elif act2_pct > 65: balance = "Extended Act 2 Middle"
        
        # Violence Floor (Task 4): If Act 1 has 3+ violent events, it cannot be 'Slow Burn'
        pacing = "Balanced"
        if violence[0] >= 3: pacing = "High Octane"
        # Propulsive: High conflict/moves quickly - generalized for all drama (Task 4)
        elif violence[0] >= 1 and (act1_pct < 28 or act2_pct < 45): pacing = "Propulsive" 
        elif sum(violence) == 0 and act1_pct > 30: pacing = "Slow Burn"
        
        return {
            'act1': act1_count, 'act2': act2_count, 'act3': act3_count,
            'act1_pct': act1_pct, 'act2_pct': act2_pct, 'act3_pct': act3_pct,
            'balance': balance,
            'violence_count': violence,
            'pacing_benchmark': pacing
        }

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
