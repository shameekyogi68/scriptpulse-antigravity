"""
Interpretation Agent - Simplified & MCA-Defensible Version
Translates raw mathematical signals into human-readable feedback.
Focuses on: Act Detection, Story Beats, and Strategic Advice.
"""

import statistics

class InterpretationAgent:
    """Translation Layer - From Data to Story Insight"""

    def __init__(self):
        # Creative Beat Labels for UI
        self.LABELS = {
            'High': "High Intensity / Conflict",
            'Medium': "Balanced Narrative Flow",
            'Low': "Quiet / Transitional Moment"
        }

    def run(self, temporal_trace):
        """Main entry point for interpretation"""
        if not temporal_trace: return {}
        
        # 1. Structure Analysis
        structure = self.map_to_structure(temporal_trace)
        
        # 2. Pattern Diagnosis
        diagnosis = self.diagnose_patterns(temporal_trace)
        
        # 3. Strategic Advice
        suggestions = self.generate_suggestions(temporal_trace)
        
        return {
            'structure': structure,
            'diagnosis': diagnosis,
            'suggestions': suggestions
        }

    def map_to_structure(self, temporal_trace):
        """Identifies Act boundaries using the 1/4 - 1/2 - 1/4 heuristic."""
        total = len(temporal_trace)
        if total < 5: return {'acts': [], 'beats': []}
        
        # ACT 1 ends around 25%
        a1_end = int(total * 0.25)
        # ACT 2 ends around 75%
        a2_end = int(total * 0.75)
        
        acts = [
            {'name': 'Act 1: Setup', 'range': [0, a1_end]},
            {'name': 'Act 2: Confrontation', 'range': [a1_end + 1, a2_end]},
            {'name': 'Act 3: Resolution', 'range': [a2_end + 1, total - 1]}
        ]
        
        # Find local peaks for Beats
        signals = [s['attentional_signal'] for s in temporal_trace]
        
        try:
            ii_idx = signals.index(max(signals[:a1_end+1]))
        except ValueError: ii_idx = 0
            
        try:
            mid_idx = a1_end + signals[a1_end:a2_end].index(max(signals[a1_end:a2_end]))
        except ValueError: mid_idx = int(total/2)
            
        try:
            climax_idx = a2_end + signals[a2_end:].index(max(signals[a2_end:]))
        except ValueError: climax_idx = total - 1
            
        beats = [
            {'name': 'Inciting Incident', 'scene_index': ii_idx},
            {'name': 'Midpoint', 'scene_index': mid_idx},
            {'name': 'Climax', 'scene_index': climax_idx}
        ]
        
        return {'acts': acts, 'beats': beats}

    def diagnose_patterns(self, temporal_trace):
        """Identifies simple diagnostic flags based on attention signals."""
        diagnosis = []
        signals = [s['attentional_signal'] for s in temporal_trace]
        if not signals: return diagnosis
        
        # 1. Start check
        if signals[0] < 0.3:
            diagnosis.append({'type': 'Warning', 'issue': 'Slow Opening', 'advice': 'Consider a stronger hook in Scene 1.'})
            
        # 2. Middle check
        mid_slice = signals[int(len(signals)*0.4):int(len(signals)*0.6)]
        if mid_slice:
            mid_avg = statistics.mean(mid_slice)
            if mid_avg < 0.4:
                diagnosis.append({'type': 'Critical', 'issue': 'Sagging Middle', 'advice': 'Raise the stakes at the midpoint to keep the reader engaged.'})
            
        # 3. Fatigue check
        high_runs = 0
        for s in signals:
            if s > 0.7: high_runs += 1
            else: high_runs = 0
            if high_runs >= 4:
                diagnosis.append({'type': 'Warning', 'issue': 'Reader Fatigue', 'advice': 'Too many high-intensity scenes in a row. Needs a breather.'})
                break
                
        return diagnosis

    def generate_suggestions(self, temporal_trace):
        """Generic repair strategies based on script profile."""
        if not temporal_trace: return []
        
        avg_s = statistics.mean([s['attentional_signal'] for s in temporal_trace])
        
        if avg_s > 0.6:
            return {
                'structural_repair_strategies': [
                    {'issue': 'High Cognitive Load', 'advice': 'Simplify complex subplots.'},
                    {'issue': 'Pacing', 'advice': 'Add quiet character moments between action beats.'}
                ]
            }
        elif avg_s < 0.3:
            return {
                'structural_repair_strategies': [
                    {'issue': 'Low Tension', 'advice': 'Increase the turn velocity of your dialogue.'},
                    {'issue': 'Pacing', 'advice': 'Introduce a major complication earlier.'}
                ]
            }
        else:
            return {
                'structural_repair_strategies': [
                    {'issue': 'Maintenance', 'advice': 'Maintain the current structural balance.'}
                ]
            }

    def generate_scene_notes(self, input_data):
        """Placeholder for scene-specific notes component."""
        return {}

    def apply_semantic_labels(self, temporal_trace, valence_trace=None):
        """Used by charts to label points on the graph."""
        labels = []
        for pt in temporal_trace:
            s = pt['attentional_signal']
            label = "Steady Flow"
            if s > 0.7: label = "High Conflict"
            elif s < 0.3: label = "Quiet Moment"
            labels.append({'scene_index': pt['scene_index'], 'primary_label': label, 'composite_beat': label})
        return labels

    def map_archetypes(self, voice_map): return {}
    def audit_subtext(self, encoded, voice_map): return []
    def map_to_custom_framework(self, trace, framework_type='3_act'): return self.map_to_structure(trace)
    def audit_narrative_intelligence(self, scenes, trace): return []
    def calculate_conflict_typology(self, encoded, valence): return []
    def track_thematic_recurrence(self, encoded): return []
    def map_interaction_networks(self, scenes, typologies): return {'edges': [], 'triangles': []}
    def audit_timeline_continuity(self, scenes): return []
    def audit_narrative_causality(self, encoded, scenes): return []
    def calculate_dialogue_authenticity(self, encoded): return []
