import random
import re
import statistics

class WriterAgent:
    """
    The 'Collaborator' Layer (v2.0 Phase 1).
    Translates raw engine signals into actionable writer feedback.
    Does not run simulations; interprets existing trace data.
    """
    
    def analyze(self, final_output, genre="General", script_era="contemporary", intended_format="spec", is_reference=False, **kwargs):
        """
        Enhances the final_output with a 'writer_intelligence' block.
        Applies Strict Constraints and Genre Nuance.
        """
        trace = final_output.get('temporal_trace', [])
        suggestions = final_output.get('suggestions', {})
        
        # Determine script era (Rule 1: Auto-detect or user-input)
        if not script_era or script_era == 'auto':
            # Search for keyword markers of historical or period settings
            # We'll use a broad 'classic' catch-all for anything clearly non-contemporary
            classic_markers = ['horse', 'carriage', 'castle', 'sword', 'throne', 'kingdom', 'century', 'historical', 'period']
            found_classic = False
            for s in trace:
                 heading = s.get('location_data', {}).get('raw_heading', '').lower()
                 if any(w in heading for w in classic_markers):
                      found_classic = True
                      break
            script_era = 'classic' if found_classic else 'contemporary'

        # Determine budget tier
        budget_tier = kwargs.get('budget_tier')
        if not budget_tier:
             budget_tier = self._calculate_budget_impact(trace).split()[0].lower()

        # Contextual metadata for deterministic diagnostic tuning
        self.context = {
            'genre': genre,
            'era': script_era,
            'format': intended_format,
            'is_reference': is_reference,
            'budget_tier': budget_tier,
            'scene_info': final_output.get('scene_info', []),
            'trace': trace,
            'themes': self._analyze_thematic_coherence(trace) # Rule 1
        }
        
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
        
        # Elite Rule 2: Moral Paradox (The 'Tragic Alpha' Signature)
        arc_data = self._build_character_arcs(trace)
        for char, data in arc_data.items():
            if data['arc_type'] == "Moral Descent 🩸":
                new_diagnostics.append(f"🌗 **Moral Paradox ({char})**: Character achieves ultimate power (+{data['agency_delta']} agency) but collapses morally ({data['moral_journey']} sentiment). Masterclass structural ambiguity.")
            elif data['transformation_depth'] > 0.6:
                new_diagnostics.append(f"🌔 **Deep Transformation ({char})**: A massive journey across {round(data['transformation_depth']*100)}% of the agency spectrum. Highly immersive development.")
        
        # Determine unique items and sort EVERYTHING for absolute score determinism
        # This ensures the penalty calculation always sees the exact same input order.
        all_diagnostics = sorted(list(set(narrative_health + new_diagnostics + self._diagnose_representation_risks(final_output.get('fairness_audit', {})))))
        
        # Reference Script Mode Transformation:Analytical vs Prescriptive (Task 4)
        if is_reference:
            all_diagnostics = [
                f"💎 **Masterwork Insight**: {d.replace('🔴', '✨').replace('🟠', '✨').replace('🟡', '✨').replace('Consider', 'Intentional use of').replace('Fix', 'Analytical study of')}"
                for d in all_diagnostics
            ]

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
        # Page Turner Index (Task 1) - Rule 4 Signature
        pti_result = self._calculate_page_turner_index(trace)
        dashboard['page_turner_index'] = pti_result['index']
        dashboard['tension_signature'] = pti_result['signature']
        
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
            'thematic_coherence': self.context.get('themes', {}),
            'genre_context': genre,
            'script_era': script_era,
            'intended_format': intended_format,
            'is_reference': is_reference
        }
        
        # Add Story Editor Coverage (Rule 6: Placeholder)
        final_output['story_editor_coverage'] = "PREMIUM FEATURE: Narrative logic audit and scene-by-scene structural proofing are currently being calculated in the Background Agent."
        
        return final_output

    def _format_scene_ref(self, start_idx, end_idx=None):
        """Standardized scene reference with page numbers and headers."""
        scene_info = self.context.get('scene_info', [])
        heading = ""
        if start_idx < len(scene_info):
            raw_h = scene_info[start_idx].get('heading', 'SCENE')
            # Extract basic identifier (INT. LOCATION)
            heading = f" ({raw_h.split(' - ')[0]})"

        if end_idx is None or end_idx == start_idx:
            p_start = max(1, round(start_idx * 0.85))
            return f"Scene {start_idx}{heading} [p. {p_start}]"
        else:
            p_start = max(1, round(start_idx * 0.85))
            p_end = max(p_start, round(end_idx * 0.85))
            return f"Scenes {start_idx}-{end_idx}{heading} [pp. {p_start}-{p_end}]"

    def _diagnose_health(self, trace, genre):
        """
        Converts math signals to story terms.
        Clusters consecutive issues.
        Adapts thresholds based on Genre, Era and Format.
        """
        assessments = []
        era = self.context.get('era', 'contemporary')
        
        # Genre & Era Thresholds
        boredom_thresh = 0.2
        if genre in ["Horror", "Drama", "Art House", "Avant-Garde", "Non-Linear"]:
            boredom_thresh = 0.1 # Tolerate slower pacing
            
        if era == "classic":
            boredom_thresh -= 0.05 # Classic films allow much slower setup
            
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
                    ref = self._format_scene_ref(start, end)
                    assessments.append(
                        f"🔴 **Sustained Intensity ({ref})**: Consistently high attentional demand for ~{duration_mins} mins. May lead to audience fatigue."
                    )

        # 2. Confusion Clustering
        strain_ranges = self._find_ranges(trace, lambda s: s.get('expectation_strain', 0) > 0.8)
        for start, end in strain_ranges:
             ref = self._format_scene_ref(start, end)
             assessments.append(
                 f"🟠 **Information Density ({ref})**: High volume of new narrative elements. May increase cognitive load for the reader."
             )
            
        # 3. Boredom vs Tense Silence
        # Tightened for slow-burn masters: only flag if valley is too long (5+ scenes)
        true_boredom_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) <= 0.5)
        for start, end in true_boredom_ranges:
            if (end - start + 1) >= 5: # Reward 2-4 scene valleys as 'effective recovery'
                 ref = self._format_scene_ref(start, end)
                 assessments.append(
                     f"🔵 **Engagement Drop ({ref})**: Attentional signals are low for an extended duration. Consider tightening the pacing or adding a 'hook' to keep the audience locked in."
                 )

        tense_silence_ranges = self._find_ranges(trace, lambda s: s['attentional_signal'] < boredom_thresh and max(s.get('conflict', 0), s.get('stakes', 0)) > 0.6)
        for start, end in tense_silence_ranges:
            if (end - start + 1) >= 2:
                 ref = self._format_scene_ref(start, end)
                 assessments.append(
                     f"🤫 **Tense Silence ({ref})**: Low dialogue density but high conflict. Effective subtextual tension."
                 )

        # 4. Exposition Clustering
        expo_ranges = self._find_ranges(trace, lambda s: s.get('exposition_score', 0) > 0.7)
        for start, end in expo_ranges:
            ref = self._format_scene_ref(start, end)
            assessments.append(
                f"💬 **Exposition Heavy ({ref})**: Characters are explaining details explicitly rather than through action."
            )

        # 5. Pacing Volatility (The 'Avant-Garde' Special)
        volatility_ranges = self._find_ranges(trace, lambda s: s.get('pacing_volatility', 0) > 0.8)
        for start, end in volatility_ranges:
            ref = self._format_scene_ref(start, end)
            assessments.append(
                f"🎢 **Erratic Pacing ({ref})**: Extreme shifts in rhythm. Use sparingly for effect."
            )

        # 6. Irony / Dissonance
        irony_ranges = self._find_ranges(trace, lambda s: s.get('sentiment', 0) > 0.6 and s.get('conflict', 0) > 0.7)
        for start, end in irony_ranges:
             ref = self._format_scene_ref(start, end)
             assessments.append(
                f"🎭 **Irony Detected ({ref})**: Positive tone matches high conflict. Unsettling and effective."
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
        words_per_turn = [c[1].get('words_per_turn', 0) for c in valid_chars]
        registers = [c[1].get('register', 'neutral') for c in valid_chars]
        agencies = [c[1].get('agency', 0) for c in valid_chars]
        
        std_wpt = statistics.stdev(words_per_turn) if len(words_per_turn) > 1 else 0.0
        std_agency = statistics.stdev(agencies) if len(agencies) > 1 else 0.0
        
        # "Same Voice Syndrome" Universal Rule (Rule 2)
        # Must trigger ONLY if ALL THREE are true: Register, WPT within 10%, and similar Power Dynamics
        unique_registers = len(set(registers))
        avg_wpt = sum(words_per_turn) / len(words_per_turn) if words_per_turn else 1
        wpt_similarity = std_wpt / avg_wpt < 0.10
        agency_similarity = std_agency < 0.15
        
        if unique_registers == 1 and wpt_similarity and agency_similarity:
            names = [c[0] for c in valid_chars[:3]]
            assessments.append(f"🔴 **Same Voice Syndrome**: Character speech patterns ({', '.join(names)}) lack distinct registers, word-per-turn variation, and power dynamic differentiation. Consider heightening their unique status or backgrounds to separate their voices.")
        
        # Power Dynamics Visualization
        top_char = valid_chars[0]
        if top_char[1].get('agency', 0) > 0.8:
            assessments.append(f"⚖️ **Vocal Dominance ({top_char[0]})**: Maintains tactical control over exchanges. This character serves as the vocal 'alpha' in the current scene context.")

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
                ref_first = self._format_scene_ref(data['first'])
                ref_last = self._format_scene_ref(data['last'])
                if data['first'] < total_scenes * 0.3 and data['last'] > total_scenes * 0.7:
                    assessments.append(f"✨ **Successful Motif Payoff**: The object '{m}' was introduced early ({ref_first}) and paid off late ({ref_last}). Strong thematic resonance.")
                elif data['first'] < total_scenes * 0.3 and spread < total_scenes * 0.1:
                    assessments.append(f"🟡 **Abandoned Motif**: The object '{m}' was introduced in {ref_first} but never reappears after {ref_last}. Consider paying it off or cutting it.")
        
        # Sort so we only show the best ones
        # Prioritize payoffs over abandoned
        assessments.sort(key=lambda x: 'Abandoned' in x)
        return assessments[:2] # Limit to 2

    def _diagnose_tell_vs_show(self, trace):
        """Analyze 'Tell, Don't Show' traps."""
        assessments = []
        tell_trap_ranges = self._find_ranges(trace, lambda s: s.get('tell_vs_show', {}).get('tell_ratio', 0.0) > 0.6 and s.get('tell_vs_show', {}).get('literal_emotions', 0) >= 2)
        for start, end in tell_trap_ranges:
            ref = self._format_scene_ref(start, end)
            assessments.append(f"🟠 **'Tell, Don't Show' Trap ({ref})**: Relying heavily on literal emotion words (e.g. 'sad', 'angry') in action lines rather than physical blocking/behavior.")
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
            
            # SCENE 98 FIX: If this is a reference script, do not flag OTN (universal rule)
            if self.context.get('is_reference'):
                continue

            # Universal Rule 5: Contradiction Check (Subtext vs On-The-Nose)
            # Threshold lowered to 0.4 to catch high-tension but visually static scenes
            conflict = s.get('conflict', 0)
            visual_int = s.get('visual_intensity', 0)
            
            if otn.get('on_the_nose_ratio', 0) > 0.25:
                # If they are stating subtext but the scene is physically active or high-conflict
                if conflict > 0.4 or visual_int > 0.4: 
                    continue 
                
                quote = f" (e.g., \"{rep[:60]}...\")" if rep else ""
                ref = self._format_scene_ref(idx)
                assessments.append(
                    f"🗣️ **On-The-Nose Dialogue ({ref})**: Characters are stating their internal subtext as text{quote}. "
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
                ref = self._format_scene_ref(idx)
                assessments.append(
                    f"✂️ **Shoe-Leather Detected ({ref})**: "
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

            # Elite Rule 3: Transformation Absolute Depth
            # Michael Corleone: 0.1 (Outsider) -> 0.9 (Don) is a 0.8 depth journey.
            # We track the max span between any two points in the timeline.
            all_agencies = [t['agency'] for t in timeline]
            max_depth = round(max(all_agencies) - min(all_agencies), 3) if all_agencies else 0
            
            # Elite Rule 2: Plot Success vs Moral Well-being
            # Michael starts high well-being (idealist) and ends low well-being (cold).
            # But starts low plot success (outsider) and ends high success (Don).
            moral_start = start['sentiment']
            moral_end = end['sentiment']
            moral_delta = round(moral_end - moral_start, 3)

            # Dimension 1: Power Trajectory (Agency Delta)
            power_traj = "stable"
            if agency_delta > 0.15: power_traj = "UP"
            elif agency_delta < -0.15: power_traj = "DOWN"
            
            # Dimension 2: Moral Trajectory (Moral Delta)
            moral_traj = "stable"
            if moral_delta > 0.15: moral_traj = "UP"
            elif moral_delta < -0.15: moral_traj = "DOWN"
            
            # Dimension 3: Agency Score (Current End Level)
            agency_level = "Medium"
            if abs_agency < 0.5: agency_level = "Low"
            elif abs_agency > 0.7: agency_level = "High"

            # Arc Classification (Rule 7)
            arc_label = "Character Evolution"
            arc_note = "A standard narrative trajectory based on agency and moral shift."
            
            if power_traj == "UP" and moral_traj == "DOWN" and agency_level == "High":
                arc_label = "Corrupted Victor 🩸"
                arc_note = "Character achieves ultimate plot success but suffers total moral collapse. A 'tragic victory' signature."
            elif power_traj == "DOWN" and moral_traj == "stable" and agency_level == "Low":
                arc_label = "Tragic Decline 📉"
                arc_note = "A significant loss of power and status while maintaining moral consistency. A fall from grace."
            elif power_traj == "stable" and moral_traj == "stable":
                if agency_level == "High":
                    arc_label = "Steadfast Pillar 🛡️"
                    arc_note = "Character remains an unwavering core of the story, maintaining high agency and constant morality."
                elif agency_level == "Medium":
                    arc_label = "Supportive Anchor ⚓"
                    arc_note = "A reliable secondary presence that maintains stability throughout the narrative."
            elif power_traj == "UP" and moral_traj == "UP":
                arc_label = "Heroic Transformation 🌔"
                arc_note = "Character rises in both influence and moral character. A classic heroic journey."
            elif power_traj == "DOWN" and moral_traj == "UP" and agency_level == "Low":
                arc_label = "Redemptive Fall ✨"
                arc_note = "Character loses worldly power but achieves moral or spiritual redemption."
            elif power_traj == "UP" and moral_traj == "stable" and agency_level == "High":
                arc_label = "Pragmatic Ascent ⛰️"
                arc_note = "Character gains significant influence without a major moral shift (either upwards or downwards)."

            # Dominance Qualifiers: Check if we already have this label with significant agency difference
            curr_agency = end.get('agency', 0.5)
            for existing_char, existing_data in arc_summary.items():
                if existing_data.get('arc_type') == arc_label:
                    other_agency = existing_data.get('agency_score', 0.5)
                    if abs(curr_agency - other_agency) > 0.2:
                        # Append qualifiers if agency diff > 20 points
                        if curr_agency > other_agency:
                            arc_label = f"Dominant {arc_label}"
                            existing_data['arc_type'] = f"Passive {existing_data['arc_type']}"
                        else:
                            arc_label = f"Passive {arc_label}"
                            existing_data['arc_type'] = f"Dominant {existing_data['arc_type']}"

            arc_summary[char] = {
                'arc_type': arc_label,
                'note': arc_note,
                'agency_score': curr_agency,
                'agency_delta': agency_delta,
                'moral_journey': moral_delta,
                'transformation_depth': max_depth,
                'scenes_present': len(timeline)
            }

        return arc_summary

    def _analyze_thematic_coherence(self, trace):
        """Elite Rule 5: Detect thematic motifs (Power, Family, Corruption) and track their Sentiment Migration."""
        themes = {
            'Family/Loyalty': ['family', 'brother', 'father', 'son', 'honor', 'loyalty', 'betrayal', 'blood'],
            'Power/The Cost': ['business', 'money', 'power', 'control', 'order', 'respect', 'america', 'don', 'offer', 'refuse'],
            'Morality/Corruption': ['soul', 'church', 'prayer', 'sin', 'guilt', 'kill', 'murder', 'innocent', 'corrupt', 'lie', 'dead']
        }
        
        n = len(trace)
        if n < 3: return {}
        third = max(1, n // 3)
        
        results = {}
        for t_name, keywords in themes.items():
            act_counts = [0, 0, 0]
            act_sentiments = [[], [], []]
            
            for i, s in enumerate(trace):
                text = str(s).lower()
                # Use a combined text check for all keywords in this theme
                found = sum(text.count(kw) for kw in keywords)
                if found > 0:
                    act_idx = min(2, i // third)
                    act_counts[act_idx] += found
                    act_sentiments[act_idx].append(s.get('sentiment', 0.0))
            
            # Migration: Calculating the shift in 'Moral Temperature' for this motif
            # If the sentiment of 'Family' drops from Act 1 (+0.2) to Act 3 (-0.5), it signifies CORRUPTION.
            start_temp = statistics.mean(act_sentiments[0]) if act_sentiments[0] else 0
            end_temp = statistics.mean(act_sentiments[2]) if act_sentiments[2] else 0
            migration_delta = round(end_temp - start_temp, 3)
            
            coherence = round(min(1.0, (sum(1 for c in act_counts if c > 0) / 3.0)), 2)
            
            migration_label = "Neutral"
            if migration_delta < -0.3: migration_label = "Corrupted / Decay 🖤"
            elif migration_delta > 0.3: migration_label = "Uplifting / Growth 🌱"
            elif abs(migration_delta) < 0.1 and act_counts[2] > 0: migration_label = "Steadfast ⚓"
            
            results[t_name] = {
                'act_frequency': act_counts,
                'coherence': coherence,
                'migration_delta': migration_delta,
                'thematic_arc': migration_label
            }
            
        return results

        return results


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
            ref = self._format_scene_ref(idx)
            assessments.append(
                f"💬 **Generic Dialogue ({ref})**: {count} interchangeable cliché line(s) detected{eg_str}. "
                f"Rewrite these to be hyper-specific to THIS character in THIS moment."
            )
        return assessments[:2]

    def _diagnose_flat_scene_turns(self, trace):
        """Flag consecutive scenes where the scene turn is flat — no dramatic movement."""
        assessments = []
        flat_ranges = self._find_ranges(trace, lambda s: s.get('scene_turn', {}).get('turn_label') == 'Flat')
        for start, end in flat_ranges:
            # Universal Rule 8: Slow Opening Detection Override
            # Flat turns in scenes 1-3 are only a problem if no spike follows within 3 scenes.
            if start <= 2:
                followed_by_spike = False
                for j in range(end + 1, min(len(trace), end + 4)):
                    turn = trace[j].get('scene_turn', {}).get('turn_label')
                    if turn in ['Negative to Positive', 'Positive to Negative', 'High Energy']:
                        followed_by_spike = True
                        break
                if followed_by_spike:
                     continue 

            if (end - start + 1) >= 2:
                ref = self._format_scene_ref(start, end)
                assessments.append(
                    f"⬜ **Flat Scene Turns ({ref})**: Emotional trajectory remains stagnant. These scenes end in the same relative position they began."
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
            ref = self._format_scene_ref(idx)
            assessments.append(
                f"✍️ **Passive Action Lines ({ref})**: {count} passive construction(s) detected{eg_str}. "
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
                    ref = self._format_scene_ref(idx_a, idx_b)
                    assessments.append(
                        f"♻️ **Possible Redundancy ({ref})**: Both are '{purpose_a}' "
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

        a1_pct = round(a1 * 100)
        a3_pct = round(a3 * 100)
        
        delta = a3 - a1
        if delta < -0.15:
            assessments.append(
                f"📉 **Protagonist Regression ({protagonist})**: Agency drops from "
                f"{a1_pct}% (Act 1) to {a3_pct}% (Act 3). Your protagonist ends the story "
                f"MORE passive than they started."
            )
        elif delta > 0.3:
            assessments.append(f"🔥 **Proactive Hero ({protagonist})**: Agency grows from {a1_pct}% in Act 1 to {a3_pct}% in Act 3.")
        elif abs(delta) < 0.015:
            assessments.append(
                f"⬜ **Protagonist Flat Arc ({protagonist})**: Agency stays flat "
                f"({a1_pct}% → {a3_pct}%) across the script."
            )
        else:
            assessments.append(
                f"✅ **Protagonist Growth ({protagonist})**: Agency rises from "
                f"{a1_pct}% → {a3_pct}%. Standard reactive-to-active transformation."
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
        Aggregate unique locations and INT/EXT balance across the script (Rule 6).
        Warn if location count exceeds threshold for detected budget tier.
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
        unique_count = len(sorted_locs)

        # Rule 6 thresholds (Budget-Aware Location Guard)
        budget = self.context.get('budget_tier', 'indie').lower()
        thresholds = {
            'micro': 15,
            'indie': 40,
            'mid': 80,
            'studio': 150,
            'blockbuster': 250
        }
        thresh = thresholds.get(budget, thresholds['indie'])

        warning = None
        if unique_count > thresh:
            warning = f"Location count ({unique_count}) exceeds standard {budget.upper()} threshold ({thresh}). Consider consolidation if budget is a constraint."
        else:
            # Rule: Replace warning with neutral observation if within appropriate range
            warning = f"{unique_count} locations — consistent with {budget} scope."

        # Special visual variety check (secondary)
        if top_ratio > 0.6 and unique_count < 5 and not warning.startswith("Location count"):
            # We keep this as a separate note if it doesn't conflict
            warning += f" Note: {round(top_ratio * 100)}% of scenes are set in '{top_loc}'. Consider physical variety."

        return {
            'unique_locations': unique_count,
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
                    ref = self._format_scene_ref(s['scene_index'])
                    assessments.append(
                        f"🎙️ **Monologue Risk ({ref}, {char})**: "
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
        """Rule 10/11: Synthesizes all elite diagnostic markers into a compelling executive narrative."""
        if not trace: return "Analysis pending."
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
            specifics.append("The dialogue shows high phonetic overlap, suggesting speech rhythms across characters.")
        if "Passive Protagonist" in diag_str:
            specifics.append("The protagonist currently faces high narrative resistance, making their journey reactive.")
        if "Moral Paradox" in diag_str or "Pyrrhic" in diag_str:
            specifics.append("The script utilizes a sophisticated moral arc, achieving a complex 'tragic victory' signature.")
        if "Tonal Whiplash" in diag_str:
            specifics.append("The script undergoes rapid emotional shifts that challenge the reader's cognitive framing.")

        # 4. Closing / Payoff (NEW Dual-Layer Intelligence)
        ending_note = self._analyze_ending_complexity(trace)
        closing = f"Ultimately, the story concludes in a {ending_note}"

        # Aggregate summary
        summary = f"{opening} {spike_text} " + " ".join(specifics[:2]) + f" {closing}"
        return {'summary': summary.strip()}
        
    def _analyze_ending_complexity(self, trace):
        """Rule 11: Dual-layer Ending Analysis (Plot vs Moral/Emotional Outcome)."""
        if not trace: return "A narrative conclusion reached."
        
        last_scene = trace[-1]
        char_arcs = last_scene.get('narrative_arcs', {})
        
        # Identify protagonist (highest overall agency)
        all_arcs = self.context.get('char_arcs', {})
        if not all_arcs: return "A conclusion reached with moderate narrative closure."
        
        # Find protag by highest avg agency_score across all scenes
        protag_candidates = sorted(all_arcs.items(), key=lambda x: x[1].get('agency_score', 0), reverse=True)
        if not protag_candidates: return "The story resolves with an evocative final beat."
        protagonist = protag_candidates[0][0]
        
        # 1. Plot Outcome (Final Agency)
        protag_end = char_arcs.get(protagonist, {})
        agency_final = protag_end.get('agency', 0.5)
        plot_status = "WIN" if agency_final > 0.7 else ("LOSS" if agency_final < 0.4 else "AMBIGUOUS")
        
        # 2. Moral/Emotional Outcome (Moral Journey Delta)
        moral_delta = all_arcs.get(protagonist, {}).get('moral_journey', 0.0)
        moral_status = "WIN" if moral_delta > 0.3 else ("LOSS" if moral_delta < -0.3 else "AMBIGUOUS")
        
        # Ending Complexity Labels
        label = "Resolution"
        note = ""
        
        if plot_status == "WIN" and moral_status == "LOSS":
            label = "Pyrrhic Victory 🌓"
            note = "the protagonist achieves their worldly goal but suffers total moral or emotional collapse."
        elif plot_status == "LOSS" and moral_status == "WIN":
            label = "Redemptive Defeat ✨"
            note = "material/plot failure is overshadowed by ultimate moral growth or spiritual redemption."
        elif plot_status == "WIN" and moral_status == "AMBIGUOUS":
            label = "Hollow Victory 🧥"
            note = "narrative goals are met, but the personal resonance remains hauntingly uncertain."
        elif plot_status == "AMBIGUOUS" and moral_status == "LOSS":
            label = "Quiet Tragedy 🕯️"
            note = "the plot resolution is left hanging, but the protagonist's moral decline is definitive."
        elif plot_status == "WIN" and moral_status == "WIN":
            label = "Triumphant Resolution 🏆"
            note = "a complete alignment of material success and profound personal growth."
        elif plot_status == "LOSS" and moral_status == "LOSS":
            label = "Unmitigated Tragedy 🌑"
            note = "total loss across both the physical and moral spectrums of the story."
        else:
            label = "Complex Ambiguity ☁️"
            note = "the script concludes with a sophisticated refusal of simple narrative closure."

        # 3. Weighted Reaction Rule (The 'Witness' POV)
        others = {k: v for k, v in char_arcs.items() if k != protagonist}
        if others:
            # Find the most emotionally active secondary character in the final scene
            loudest_other = max(others.items(), key=lambda x: abs(x[1].get('sentiment', 0)))[0]
            other_sent = others[loudest_other].get('sentiment', 0.0)
            if abs(other_sent) > 0.6:
                # If a witness's reaction is huge, it defines the final sentiment
                note += f" | Final focus is on {loudest_other}'s reaction, which anchors the script's emotional result."

        return f"**{label}**: {note}"


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
                ref = self._format_scene_ref(idx)
                assessments.append(
                    f"🚫 **Action Line Modifiers ({ref})**: Action lines contain descriptors defining internal states. "
                    f"e.g. \"{eg}\""
                )

        # Name crowding
        for s in trace:
            rf = s.get('reader_frustration', {})
            if rf.get('name_crowding'):
                n = rf.get('unique_char_count', 4)
                ref = self._format_scene_ref(s['scene_index'])
                assessments.append(
                    f"👥 **Character Density ({ref})**: {n} distinct characters are active simultaneously. "
                    f"This creates a high referential load for the audience."
                )
                break

        # Similar name pairs
        for s in trace:
            rf = s.get('reader_frustration', {})
            pairs = rf.get('similar_name_pairs', [])
            if pairs:
                ref = self._format_scene_ref(s['scene_index'])
                assessments.append(
                    f"🔤 **Orthographic Proximity ({ref})**: Character names {pairs[0]} are lexically or phonetically similar. "
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
        """Rule 1 Integration: Surface identifying themes and coherence status."""
        themes = self.context.get('themes', {})
        assessments = []
        for name, data in themes.items():
            if data['coherence_score'] >= 0.9:
                assessments.append(f"🛡️ **Thematic Core ({name})**: Dominant presence across all three Acts. Strong structural coherence.")
            elif data['coherence_score'] <= 0.3:
                 assessments.append(f"🌫️ **Thematic Ghost ({name})**: Found in one Act but abandoned elsewhere. Suggests a 'dangling' thematic promise.")
        return assessments

    def _generate_creative_provocations(self, diagnosis, genre):
        """Rule 6 Variety: Different thematic provocations every time, no direct flag echoes."""
        pool = {
            'drama': [
                "What would happen if your protagonist couldn't rely on their primary 'safety net' in the second act?",
                "Is there a secondary conflict that could mirror the internal struggle of the lead?",
                "Could the antagonist's motive be framed as a 'twisted virtue' to add complexity?",
                "What is the one thing your protagonist wants so badly they would burn their life down to get it?"
            ],
            'thriller': [
                "What is the one piece of information that, if revealed too early, would break the story?",
                "Is the ticking clock physical, or can it be psychological to increase pressure?",
                "Which character has the most to lose if the truth is never revealed?",
                "If the antagonist achieved their goal tomorrow, what would their life look like?"
            ],
            'general': [
                "If you removed the most expensive scene, would the story still function?",
                "What is the subtext of the silence between your two main leads?",
                "Is the central theme being challenged by the supporting cast, or just supported?",
                "In your quietest scene, what is the 'Invisible Conflict' that keeps the audience leaning in?"
            ]
        }
        
        options = pool.get(genre.lower(), pool['general'])
        # Simplified selection for variety
        import random
        return random.sample(options, min(2, len(options)))



        






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
        
        # Elite Rule 4: Tension Signature Pattern Recognition
        # 'Slow Burn (Operatic)' vs 'Classic Rising' vs 'Uniform High Octane'
        diffs = [abs(signals[i] - signals[i-1]) for i in range(1, len(signals))]
        avg_jump = sum(diffs) / len(diffs) if diffs else 0
        peaks = sum(1 for s in signals if s > 0.8)
        n_scenes = len(trace)
        
        # Operatic signature: High volatility (big jumps) but relatively infrequent peaks
        # This captures the 'valleys of silence + spikes of violence' pattern.
        if avg_jump > 0.15 and peaks < (n_scenes * 0.15):
            signature = "Operatic / Slow Burn 🎭" 
        elif avg_jump < 0.10:
            signature = "Constant Pressure / Minimalist 🏔️"
        elif signals[-1] > max(signals[:n_scenes//2]):
            signature = "Classical Rising Action 📈"
        else:
            signature = "Procedural / Rhythmic ⏱️"
            
        return {
            'index': min(100, round(20 + (contrast_score + resonance_score + cliffhangers) * 0.8)),
            'signature': signature,
            'volatility': round(avg_jump, 2)
        }

    def _diagnose_writing_texture(self, trace):
        """Identifies if the script is 'Cinematic' (lean) or 'Novelistic' (dense)."""
        action_densities = [s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace]
        avg_action = sum(action_densities) / len(trace) if trace else 0
        
        if avg_action > 10: return "Novelistic / Literary"
        if avg_action < 4: return "Sparse / Minimalist"
        return "Cinematic / Visual"

    def _calculate_tone_score(self, trace):
        """Rule 1: Detect Tone Score (1-10) from action intensity and conflict."""
        if not trace: return 5
        action = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        conflict = sum(s.get('conflict', 0) for s in trace) / len(trace)
        # Epic/High Intensity (10) vs Intimate/Low Action (1)
        score = (action * 0.6) + (conflict * 10 * 0.4)
        return round(max(1, min(10, score)))

    def _calculate_scale_score(self, trace):
        """Rule 2: Detect Scale Score (1-10) from locations and budget."""
        if not trace: return 5
        locs = self._build_location_profile(trace).get('unique_locations', 0)
        budget = self.context.get('budget_tier', 'indie')
        b_map = {'micro': 1, 'indie': 3, 'mid': 6, 'blockbuster': 10}
        b_val = b_map.get(budget.lower(), 4)
        
        # Scale weighted by loc count (normalized to 1-10 via ~50 locs = max)
        score = (min(locs, 50) / 5) + (b_val * 0.5)
        return round(max(1, min(10, score)))

    def _detect_subgenre(self, trace):
        """Rule 1: Detect specific subgenre from plot mechanics and dynamics."""
        if not trace: return "Character Study"
        
        # Conflict types & Stakes markers
        locations = self._build_location_profile(trace).get('unique_locations', 0)
        action_density = sum(s.get('visual_abstraction', {}).get('action_lines', 0) for s in trace) / len(trace)
        dialogue_density = 1 - action_density / 20 # Normalized relative to avg
        conflict_std = self._calculate_tension_map(trace).get('volatility', 0)
        stakes = self.context.get('stakes', 'Personal')

        # Logic for subgenre categorization
        if "Political" in stakes or "Global" in stakes: return "Political Thriller"
        if "Crime" in stakes or "Power" in stakes:
            if locations > 25: return "Crime Epic"
            if action_density > 8: return "Heist"
            return "Crime Drama"
        if "Family" in stakes or "Social" in stakes:
            if dialogue_density > 0.7: return "Domestic Drama"
            return "Coming of Age"
        if conflict_std > 0.2: return "Revenge Tragedy"
        
        return "Character Study"

    def _find_commercial_comps(self, genre, dominant_stakes='Social'):
        """Rule 4 & 5: Multi-dimensional Comp Selection (Subgenre + Tone + Scale + Era)."""
        trace = self.context.get('trace', [])
        subgenre = self._detect_subgenre(trace)
        tone = self._calculate_tone_score(trace)
        scale = self._calculate_scale_score(trace)
        
        current_year = 2024
        # Setting Era detection
        era_label = str(self.context.get('era', 'contemporary')).lower()
        if "1970" in era_label: script_year = 1975
        elif "1980" in era_label: script_year = 1985
        elif "1990" in era_label: script_year = 1995
        elif "period" in era_label or "history" in era_label: script_year = 1950
        else: script_year = current_year

        # Comp DB: [Name, Subgenre, Tone(1-10), Scale(1-10), Year]
        db = [
            ("The Godfather", "Crime Epic", 8, 9, 1972),
            ("Heat", "Crime Epic", 9, 8, 1995),
            ("Chinatown", "Crime Drama", 7, 7, 1974),
            ("The Departed", "Crime Drama", 9, 7, 2006),
            ("Scarface", "Crime Epic", 10, 9, 1983),
            ("Marriage Story", "Domestic Drama", 3, 2, 2019),
            ("Kramer vs Kramer", "Domestic Drama", 3, 2, 1979),
            ("Blue Valentine", "Domestic Drama", 4, 2, 2010),
            ("Manchester by the Sea", "Domestic Drama", 2, 3, 2016),
            ("Michael Clayton", "Political Thriller", 6, 6, 2007),
            ("All the President's Men", "Political Thriller", 5, 7, 1976),
            ("The Ides of March", "Political Thriller", 6, 5, 2011),
            ("Lady Bird", "Coming of Age", 4, 3, 2017),
            ("The Graduate", "Coming of Age", 5, 4, 1967),
            ("Boyhood", "Coming of Age", 4, 4, 2014),
            ("Heat", "Heist", 10, 8, 1995),
            ("Ocean's Eleven", "Heist", 6, 8, 2001),
            ("The Town", "Heist", 8, 6, 2010),
            ("Oldboy", "Revenge Tragedy", 9, 5, 2003),
            ("Gladiator", "Revenge Tragedy", 10, 10, 2000),
            ("John Wick", "Revenge Tragedy", 9, 6, 2014),
            ("Parasite", "Social Thriller", 7, 5, 2019),
            ("Taxi Driver", "Character Study", 8, 4, 1976),
            ("Moonlight", "Character Study", 3, 3, 2016),
            ("Joker", "Character Study", 9, 7, 2019)
        ]
        
        matches = []
        for name, sub, t, s, y in db:
            # Score each dimension (5 points for subgenre, 3 for others)
            sub_pass = (sub == subgenre)
            tone_pass = (abs(t - tone) <= 2)
            scale_pass = (abs(s - scale) <= 2)
            era_pass = (abs(y - script_year) <= 20)
            
            passes = sum([sub_pass, tone_pass, scale_pass, era_pass])
            
            # Rejection Logic: Reject if fails > 1 dimension (needs at least 3 passes)
            if passes >= 3:
                total_score = (5 if sub_pass else 0) + (3 if tone_pass else 0) + (3 if scale_pass else 0) + (3 if era_pass else 0)
                matches.append((name, total_score))
        
        # Rank by total score
        matches.sort(key=lambda x: x[1], reverse=True)
        # Return exactly 3 rank-ordered comps
        return [m[0] for m in matches[:3]] if len(matches) >= 3 else [m[0] for m in matches] + ["Generic Industry Comp"]*(3-len(matches))

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
        
        # 2. Production Polish (20%): Manageable Cast/Location count for budget tier
        budget = self.context.get('budget_tier', 'indie').lower()
        # Thresholds matching the Budget-Aware Location Guard
        loc_thresholds = {'micro': 15, 'indie': 40, 'mid': 80, 'studio': 150, 'blockbuster': 250}
        cast_thresholds = {'micro': 8, 'indie': 20, 'mid': 45, 'studio': 80, 'blockbuster': 150}
        
        loc_thresh = loc_thresholds.get(budget, 40)
        cast_thresh = cast_thresholds.get(budget, 20)
        
        cast_count = d.get('cast_count_deterministic', 10)
        loc_count = d.get('location_data', {}).get('unique_locations', 25) # Use pre-calculated unique count
        
        # Scoring: Full points if under threshold, scaling deduction if over
        loc_penalty = max(0, (loc_count - loc_thresh) / loc_thresh) * 10
        cast_penalty = max(0, (cast_count - cast_thresh) / cast_thresh) * 10
        prod_score = max(0, 20 - loc_penalty - cast_penalty)
        
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
        
        # Task 1: Era & Format-aware Scoring adjustments
        era = self.context.get('era', 'contemporary')
        i_format = self.context.get('format', 'spec')
        
        # Dialogue Harmony (15%): Reward hitting genre benchmarks
        dr = dashboard.get('dialogue_ratio', {})
        d_ratio = dr.get('global_dialogue_ratio', 0.55)
        d_bench = dr.get('genre_benchmark', 0.55)
        
        if era == 'classic':
             # Classic films are more talky, ease the penalty for high dialogue ratio
             d_harmony = max(0, 100 - abs(d_ratio - (d_bench + 0.1)) * 150)
        else:
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
        
        # Masterwork Mode: Reference scripts aren't penalized for 'flaws' (Task 4)
        if self.context.get('is_reference'):
             health_penalty = 0
        else:
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
        
        # Universal Rule 4: Master Score Floor Logic
        # If Top 3 sub-scores (Market, PTI, Risk) are all high-performing (90+),
        # the final score cannot be more than 5 pts below their average.
        top_3_avg = (mr + pti + (100 - risk)) / 3
        if mr >= 90 and pti >= 90 and (100 - risk) >= 90:
            floor = round(top_3_avg - 5)
            final = max(final, floor)
            
        return final
