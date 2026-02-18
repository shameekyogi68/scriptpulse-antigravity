
import copy
import statistics
import time
from scriptpulse.agents.dynamics_agent import DynamicsAgent, ReaderProfile
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.experimental_agent import MultiLabelEmotionAgent, StakesDetector

class AblationRunner:
    """
    Systematically disables modules to measure their contribution to the final signal.
    """
    
    def __init__(self, baseline_script):
        self.baseline_script = baseline_script
        self.results = {}
        
    def run_study(self):
        # 1. Run Baseline (Full Model)
        print("Running Baseline...")
        baseline_metrics = self._run_pipeline(ablation_config={})
        self.results['baseline'] = baseline_metrics
        
        # 2. Define Ablations
        ablations = {
            'no_reader_profile': {'disable_reader_profile': True},
            'no_readability': {'disable_readability': True},
            'no_stakes': {'disable_stakes': True},
            'no_emotion': {'disable_emotion': True}
        }
        
        # 3. Run Ablations
        for name, config in ablations.items():
            print(f"Running Ablation: {name}...")
            metrics = self._run_pipeline(ablation_config=config)
            self.results[name] = self._calculate_drop(baseline_metrics, metrics)
            
        return self.results
        
    def _run_pipeline(self, ablation_config):
        # Initialize Agents (Fresh for each run to avoid state leak)
        perception = EncodingAgent()
        dynamics = DynamicsAgent()
        emotion = MultiLabelEmotionAgent()
        stakes = StakesDetector()
        
        # Run Perception
        features = perception.run(self.baseline_script)
        
        # Apply Ablations to Features
        if ablation_config.get('disable_readability'):
            for f in features:
                if 'linguistic_load' in f:
                    f['linguistic_load']['readability_grade'] = 0.0
                    f['linguistic_load']['idea_density'] = 0.0
                    
        # Apply Ablations to Dynamics Input
        profile = None
        if not ablation_config.get('disable_reader_profile'):
            profile = ReaderProfile(familiarity=0.5, tolerance=0.5).get_params()
            
        # Run Dynamics
        signals = dynamics.run_simulation({'features': features}, profile_params=profile)
        
        # Calculate Aggregate Metrics
        avg_effort = statistics.mean([s['instantaneous_effort'] for s in signals])
        avg_recovery = statistics.mean([s['recovery_credit'] for s in signals])
        
        return {
            'avg_effort': avg_effort,
            'avg_recovery': avg_recovery
        }
        
    def _calculate_drop(self, baseline, current):
        drops = {}
        for key in baseline:
            base_val = baseline[key]
            curr_val = current[key]
            if base_val == 0:
                pct_drop = 0.0
            else:
                pct_drop = (base_val - curr_val) / base_val * 100
            drops[key] = {
                'absolute_change': round(curr_val - base_val, 4),
                'percent_drop': round(pct_drop, 2)
            }
        return drops
        
    def generate_report(self):
        md = "### Ablation Study Results\n\n"
        md += "| Ablation | Avg Effort Drop (%) | Avg Recovery Drop (%) |\n"
        md += "|---|---|---|\n"
        
        for name, data in self.results.items():
            if name == 'baseline': continue
            effort_drop = data['avg_effort']['percent_drop']
            recovery_drop = data['avg_recovery']['percent_drop']
            md += f"| **{name}** | {effort_drop}% | {recovery_drop}% |\n"
            
        return md

if __name__ == "__main__":
    # Mock Script for standalone testing
    mock_data = {
        'scenes': [
            {'scene_index': 1, 'lines': [{'tag': 'S', 'text': 'EXT. PARK'}, {'tag': 'A', 'text': 'Run.'}]},
            {'scene_index': 2, 'lines': [{'tag': 'S', 'text': 'INT. LAB'}, {'tag': 'D', 'text': 'Science.'}]}
        ]
    }
    runner = AblationRunner(mock_data)
    results = runner.run_study()
    print(runner.generate_report())
