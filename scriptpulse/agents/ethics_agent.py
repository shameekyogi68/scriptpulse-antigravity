"""
Ethics Agent - Analyzing Bias, Agency, and Fairness
Consolidates: agency.py, fairness.py
"""

import collections
import statistics

# =============================================================================
# AGENCY LOGIC (formerly agency.py)
# =============================================================================

class EthicsAgent:
    """Ethics Agent - Bias, Agency, and Fairness Auditing"""

    def analyze_agency(self, input_data):
        """
        Analyze Character Agency (Power/Influence)
        Objective: Measure Agency rather than just Presence.
        """
        # 1. Construct Interaction Graph
        adjacency = collections.defaultdict(int)
        nodes = set()
        scenes = input_data.get('scenes', [])
        
        if not scenes: return {'error': 'No input scenes'}
        
        for scene in scenes:
            speakers = []
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        speakers.append(name)
                        nodes.add(name)
            
            for k in range(len(speakers) - 1):
                src, dst = speakers[k], speakers[k+1]
                if src != dst: adjacency[(src, dst)] += 1
                
        if not nodes: return {'agency_metrics': []}
        
        # 2. Calculate Centrality Metrics (Degree Centrality as robust fallback)
        degrees = collections.defaultdict(int)
        for (src, dst), weight in adjacency.items():
            degrees[src] += weight
            degrees[dst] += weight
            
        max_degree = max(degrees.values()) if degrees else 1
        centrality_map = {n: degrees[n]/max_degree for n in nodes}
        
        # 3. Analyze Structural Agency (Dialogue Volume & Action Prominence)
        char_metrics = collections.defaultdict(lambda: {"action_subjects": 0, "dialogue_lines": 0, "total_words_spoken": 0, "turn_initiations": 0, "commands": 0})
        
        for scene in scenes:
            current_char = None
            scene_started = False
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        char_metrics[name]["dialogue_lines"] += 1
                        if not scene_started:
                            char_metrics[name]["turn_initiations"] += 1
                            scene_started = True
                        current_char = name
                elif line['tag'] == 'D' and current_char:
                    text = line['text']
                    char_metrics[current_char]["total_words_spoken"] += len(text.split())
                    # Simple Command Heuristic
                    if len(text.split()) < 6 and ('!' in text or text.isupper()):
                        char_metrics[current_char]["commands"] += 1
                elif line['tag'] == 'A':
                    text = line['text']
                    for char in nodes:
                        # If an action line starts with the character's name, they are likely driving the action
                        if text.startswith(char):
                            char_metrics[char]["action_subjects"] += 1
        
        # Calculate maxes for normalization
        max_words = max((m["total_words_spoken"] for m in char_metrics.values()), default=1)
        max_actions = max((m["action_subjects"] for m in char_metrics.values()), default=1)
        max_initiations = max((m["turn_initiations"] for m in char_metrics.values()), default=1)
        max_commands = max((m["commands"] for m in char_metrics.values()), default=1)
        
        report = []
        for char in nodes:
            stats = char_metrics[char]
            norm_words = stats["total_words_spoken"] / max(1, max_words)
            norm_actions = stats["action_subjects"] / max(1, max_actions)
            norm_initiations = stats["turn_initiations"] / max(1, max_initiations)
            norm_commands = stats["commands"] / max(1, max_commands)
            norm_cent = centrality_map.get(char, 0.0)
            
            # Refined narrative agency calculation
            agency_score = (norm_cent * 0.3) + (norm_words * 0.3) + (norm_actions * 0.2) + (norm_initiations * 0.1) + (norm_commands * 0.1)
            
            report.append({
                'character': char,
                'agency_score': round(agency_score, 3),
                'centrality': round(norm_cent, 3),
                'initiative': round(norm_initiations, 2),
                'command_presence': round(norm_commands, 2),
                'classification': "High Agency" if agency_score > 0.4 else "Passive"
            })
            
        report.sort(key=lambda x: (x['agency_score'], x['character']), reverse=True)
        return {'agency_metrics': report}

    # =========================================================================
    # ROLE CLASSIFIER LOGIC (New)
    # =========================================================================

    def classify_roles(self, input_data):
        """Heuristic Role Classification based on presence and agency."""
        scenes = input_data.get('scenes', [])
        if not scenes: return {}
        
        # 1. Count Lines and Scenes
        char_lines = collections.defaultdict(int)
        char_scenes = collections.defaultdict(int)
        
        for scene in scenes:
            seen_in_scene = set()
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name:
                        char_lines[name] += 1
                        seen_in_scene.add(name)
            for name in seen_in_scene:
                char_scenes[name] += 1
                
        if not char_lines: return {}
        
        # 2. Determine Hierarchy
        sorted_chars = sorted(char_lines.items(), key=lambda x: x[1], reverse=True)
        top_char, max_lines = sorted_chars[0]
        
        roles = {}
        roles[top_char] = 'Protagonist'
        
        for char, lines in sorted_chars[1:]:
            ratio = lines / max_lines
            if ratio > 0.6:
                roles[char] = 'Major Support' # Potential Antagonist or Deuteragonist
            elif ratio > 0.2:
                roles[char] = 'Supporting'
            else:
                roles[char] = 'Minor'
                
        return roles

    # =========================================================================
    # FAIRNESS LOGIC (formerly fairness.py)
    # =========================================================================

    def audit_fairness(self, input_data, context=None, genre='drama'):
        """Audit character portrayals for potential bias."""
        scenes = input_data.get('scenes', [])
        valence_scores = input_data.get('valence_scores', [])
        
        # Auto-detect roles if not provided
        roles = context if context else self.classify_roles(input_data)
        
        # Genre Thresholds
        g_lower = genre.lower()
        neg_thresh = -0.3 if g_lower in ['horror', 'thriller'] else (-0.05 if g_lower == 'comedy' else -0.15)
        
        if not scenes: return {}
        
        char_valence = collections.defaultdict(list)
        char_agency = collections.defaultdict(list) # Placeholder for agency integration
        
        # Get Agency Data if available (self-call or passed)
        agency_data = self.analyze_agency(input_data).get('agency_metrics', [])
        agency_map = {item['character']: item['agency_score'] for item in agency_data}
        
        for i, scene in enumerate(scenes):
            val = valence_scores[i] if i < len(valence_scores) else 0.0
            active = set()
            for line in scene['lines']:
                if line['tag'] == 'C':
                    name = line['text'].split('(')[0].strip()
                    if name: active.add(name)
            for char in active:
                char_valence[char].append(val)
                
        report = {'stereotyping_risks': [], 'representation_stats': {}}
        major_chars = [c for c, vals in char_valence.items() if len(vals) > 5]
        
        for char in major_chars:
            vals = char_valence[char]
            avg_val = statistics.mean(vals)
            role = roles.get(char, 'Unknown')
            agency = agency_map.get(char, 0.5)
            
            # Risk 1: The "Inept" Minor Character (Low Agency + Negative Sentiment)
            if role == 'Minor' and agency < 0.2 and avg_val < -0.1:
                 report['stereotyping_risks'].append(
                     f"Minor Character '{char}' is portrayed with Low Agency ({agency:.2f}) and Negative Tone. Check for punching down."
                 )
            
            # Risk 2: Villain Coding (check if Major Support is excessively negative)
            if role in ['Major Support', 'Protagonist'] and avg_val < neg_thresh:
                if role == 'Protagonist':
                     report['stereotyping_risks'].append(f"Protagonist '{char}' has consistently negative sentiment ({avg_val:.2f}). Is this an Anti-Hero?")
                else:
                     report['stereotyping_risks'].append(
                         f"Major Character '{char}' has high negative sentiment ({avg_val:.2f}). Likely Antagonist, but ensure motivation is clear."
                     )

            report['representation_stats'][char] = {
                'scene_count': len(vals),
                'avg_sentiment': round(avg_val, 3),
                'agency': round(agency, 3),
                'role': role
            }
            
        return report
