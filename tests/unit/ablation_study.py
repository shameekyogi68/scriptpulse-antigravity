#!/usr/bin/env python3
"""
ScriptPulse Ablation Runner (IEEE Validation Protocol compliance)
Systematically disables core theoretical layers to measure their contribution to the final signal.
Aligns with layers defined in docs/IEEE_Validation_Protocol.md
"""

import copy
import statistics
import time

from scriptpulse.agents.structure_agent import ParsingAgent, SegmentationAgent
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.dynamics_agent import DynamicsAgent, ReaderProfile
from scriptpulse.agents.interpretation_agent import InterpretationAgent

class AblationRunner:
    def __init__(self, script_content):
        self.script_content = script_content
        self.results = {}
        
        # Pre-compute structure and perception to save time across ablations
        print("Parsing and encoding baseline features...")
        parser = ParsingAgent()
        segmenter = SegmentationAgent()
        
        parsed = parser.run(script_content)['lines']
        self.segmented = segmenter.run(parsed)
        for scene in self.segmented:
            start = scene['start_line']
            end = scene['end_line']
            scene['lines'] = parsed[start:end+1]
            
        self.encoder = EncodingAgent()
        self.baseline_features = self.encoder.run({'scenes': self.segmented})
        
    def run_study(self):
        # 1. Run Baseline (Full Model)
        print("Running Baseline...")
        baseline_metrics = self._run_pipeline(ablation_config={})
        self.results['Baseline (Full System)'] = baseline_metrics
        
        # 2. Define IEEE Protocol Ablations
        ablations = {
            'Layer 1: No TAM (Microdynamics)': {'disable_tam': True},
            'Layer 2: No ACD (Collapse/Drift)': {'disable_acd': True},
            'Layer 3: No SSF (Silence as Signal)': {'disable_ssf': True},
            'Layer 4: No LRF (Long-Range Fatigue)': {'disable_lrf': True}
        }
        
        # 3. Run Ablations
        for name, config in ablations.items():
            print(f"Running Ablation: {name}...")
            metrics = self._run_pipeline(ablation_config=config)
            self.results[name] = self._calculate_drop(baseline_metrics, metrics)
            
        return self.results
        
    def _run_pipeline(self, ablation_config):
        dynamics = DynamicsAgent()
        interpretation = InterpretationAgent()
        
        # Deep copy features so ablations don't mutate baseline
        features = copy.deepcopy(self.baseline_features)
        
        # Ablate TAM (Layer 1): Erase micro-structure
        if ablation_config.get('disable_tam'):
            for f in features:
                f['micro_structure'] = []
                
        profile = ReaderProfile().get_params()
        
        # Run Temporal Simulation
        signals = dynamics.run_simulation(
            {
                'features': features,
                'semantic_scores': [],
                'syntax_scores': [],
                'visual_scores': [],
                'social_scores': [],
                'valence_scores': [],
                'coherence_scores': [],
                'ml_tension_scores': [None]*len(features)
            },
            profile_params=profile
        )
        
        # Ablate LRF (Layer 4): Skip Long-Range Fatigue integration
        if not ablation_config.get('disable_lrf'):
            signals = dynamics.apply_long_range_fatigue({
                'temporal_signals': signals,
                'features': features
            })
            
        # Ablate ACD (Layer 2): Skip Collapse/Drift
        acd_states = []
        if not ablation_config.get('disable_acd'):
            acd_states = dynamics.calculate_acd_states({
                'temporal_signals': signals,
                'features': features
            })
            
        # Ablate SSF (Layer 3): Skip Silence Analysis
        ssf_output = {}
        if not ablation_config.get('disable_ssf'):
            ssf_output = interpretation.analyze_silence({
                'temporal_signals': signals,
                'acd_states': acd_states,
                'surfaced_patterns': []
            })
            
        # Compute summary metrics for this pass
        avg_effort = statistics.mean([s['instantaneous_effort'] for s in signals]) if signals else 0
        avg_recovery = statistics.mean([s['recovery_credit'] for s in signals]) if signals else 0
        
        # Proxy metrics for SSF/ACD that affect writer confidence
        total_collapse_warnings = len([s for s in acd_states if s.get('state') == 'Collapse'])
        ssf_confidence = ssf_output.get('global_silence_confidence', 0) if ssf_output else 0.0
        
        return {
            'avg_effort': avg_effort,
            'avg_recovery': avg_recovery,
            'collapse_warnings': total_collapse_warnings,
            'silence_confidence': ssf_confidence
        }
        
    def _calculate_drop(self, baseline, current):
        drops = {}
        for key in baseline:
            base_val = baseline[key]
            curr_val = current[key]
            pct_drop = ((base_val - curr_val) / base_val * 100) if base_val != 0 else 0.0
            drops[key] = {
                'baseline_val': round(base_val, 4),
                'ablated_val': round(curr_val, 4),
                'percent_drop': round(pct_drop, 2)
            }
        return drops
        
    def generate_report(self):
        md = "### IEEE Protocol Ablation Study Results\n\n"
        md += "| Ablation Layer | Effort Drop (%) | Recovery Drop (%) | Collapse Warnings | SSF Confidence |\n"
        md += "|---|---|---|---|---|\n"
        
        for name, data in self.results.items():
            if name == 'Baseline (Full System)':
                md += f"| **{name}** | - | - | {round(data['collapse_warnings'], 2)} | {round(data['silence_confidence'], 2)} |\n"
                continue
                
            effort_drop = data['avg_effort']['percent_drop']
            recovery_drop = data['avg_recovery']['percent_drop']
            col_drop = data['collapse_warnings']['ablated_val']
            ssf_abs = data['silence_confidence']['ablated_val']
            
            md += f"| **{name}** | {effort_drop}% | {recovery_drop}% | {col_drop} | {ssf_abs} |\n"
            
        return md

if __name__ == "__main__":
    mock_script = "INT. ROOM - DAY\nA character walks in.\nCHARACTER\nHello."
    print("Initializing IEEE Ablation Study Harness...")
    runner = AblationRunner(mock_script)
    results = runner.run_study()
    print("\n" + runner.generate_report())
