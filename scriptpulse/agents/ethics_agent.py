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
        
        # 3. Analyze "Decision Verbs"
        agency_verbs = ["decide", "choose", "will", "must", "order", "stop", "save", "kill", "fight"]
        passive_verbs = ["wait", "watch", "listen", "see", "hear", "feel", "think", "wonder"]
        verb_counts = collections.defaultdict(lambda: {"active": 0, "passive": 0})
        
        for scene in scenes:
            current_char = None
            for line in scene['lines']:
                if line['tag'] == 'C':
                    current_char = line['text'].split('(')[0].strip()
                elif line['tag'] == 'D' and current_char:
                    text = line['text'].lower()
                    for v in agency_verbs:
                        if v in text: verb_counts[current_char]["active"] += 1
                    for v in passive_verbs:
                        if v in text: verb_counts[current_char]["passive"] += 1
        
        report = []
        for char in nodes:
            stats = verb_counts[char]
            total = stats["active"] + stats["passive"]
            verb_ratio = stats["active"] / (total if total > 0 else 1)
            norm_cent = centrality_map.get(char, 0.0)
            
            agency_score = (norm_cent * 0.6) + (verb_ratio * 0.4)
            
            report.append({
                'character': char,
                'agency_score': round(agency_score, 3),
                'centrality': round(norm_cent, 3),
                'active_verb_ratio': round(verb_ratio, 2),
                'classification': "High Agency" if agency_score > 0.4 else "Passive"
            })
            
        report.sort(key=lambda x: x['agency_score'], reverse=True)
        return {'agency_metrics': report}

    # =========================================================================
    # FAIRNESS LOGIC (formerly fairness.py)
    # =========================================================================

    def audit_fairness(self, input_data, context=None, genre='drama'):
        """Audit character portrayals for potential bias."""
        scenes = input_data.get('scenes', [])
        valence_scores = input_data.get('valence_scores', [])
        char_context = context or {}
        
        # Genre Thresholds
        g_lower = genre.lower()
        neg_thresh = -0.3 if g_lower in ['horror', 'thriller'] else (-0.05 if g_lower == 'comedy' else -0.15)
        pos_thresh = 0.2 if g_lower == 'comedy' else None
        
        if not scenes: return {}
        
        char_valence = collections.defaultdict(list)
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
            role = char_context.get(char, 'Unknown')
            
            if avg_val < neg_thresh:
                if role not in ['Antagonist', 'Villain']:
                    report['stereotyping_risks'].append(
                        f"Character '{char}' ({role}) is associated with Negative Sentiment (Avg: {avg_val:.2f}). Check for 'Villain Coding'."
                    )
            
            if pos_thresh and avg_val < pos_thresh:
                report['stereotyping_risks'].append(f"Character '{char}' seems too negative for a Comedy.")
                
            report['representation_stats'][char] = {
                'scene_count': len(vals),
                'avg_sentiment': round(avg_val, 3),
                'role': role
            }
            
        return report
