
import json
import hashlib
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.validation.human_alignment import HumanAligner
from scriptpulse.validation.ablation_study import AblationRunner
from scriptpulse.validation.human_alignment import HumanAligner
from scriptpulse.validation.ablation_study import AblationRunner
from scriptpulse.validation.blind_validation import BlindValidator
from scriptpulse.validation.temporal_consistency import TemporalConsistencyTester
from scriptpulse.validation.threshold_derivation import ThresholdDeriver
from scriptpulse.validation.profiler import ResourceProfiler
from scriptpulse.validation.baselines import BaselineComparator
from scriptpulse.validation.significance import SignificanceTester
from scriptpulse.validation.real_study_loader import RealReaderLoader
from scriptpulse.validation.boundary_report import BoundaryReporter

class ResearchReproducer:
    """
    Ensures full reproducibility of research results by enforcing locked configuration.
    """
    
    def __init__(self, config_path='config/reproducibility.lock'):
        self.config = self._load_config(config_path)
        
    def _load_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)
            
    def run_pipeline(self, script_path, output_dir='output/research_run'):
        print(f"Starting Reproducible Run (v{self.config['version']})...")
        
        # 1. Load Data
        mock_script = {
            'scenes': [
                {'scene_index': 1, 'lines': [{'tag': 'S', 'text': 'EXT. FIELD', 'line_index': 1}, {'tag': 'A', 'text': 'Wind blows.', 'line_index': 2}]},
                {'scene_index': 2, 'lines': [{'tag': 'S', 'text': 'INT. LAB', 'line_index': 3}, {'tag': 'D', 'text': 'Eureka!', 'line_index': 4}]}
            ]
        }
        
        # 2. Run Core Analysis
        perception = EncodingAgent()
        dynamics = DynamicsAgent()
        
        from scriptpulse.agents.interpretation_agent import InterpretationAgent
        interpreter = InterpretationAgent()
        
        # Load params from config
        dyn_params = self.config['parameters']['dynamics']
        
        features = perception.run(mock_script)
        input_data = {'features': features, 'profile_params': dyn_params}
        signals = dynamics.run_simulation(input_data, genre='drama')
        
        # Calculate Uncertainty
        uncertainty_data = interpreter.calculate_uncertainty({'temporal_signals': signals, 'features': features})
        
        # 3. Validation Layers
        # Human Alignment (Multi-Rater)
        aligner = HumanAligner('data/ground_truth/mock_human_ratings_multi_rater.csv', multi_rater=True)
        
        # Mocking system output format for aligner (including confidence)
        sys_output = []
        for i, sig in enumerate(signals):
            # Derive confidence from sigma (max sigma ~0.25 -> min conf ~0.5)
            # Simple linear map: 1.0 - (sigma * 2)
            sigma = uncertainty_data[i]['sigma'] if i < len(uncertainty_data) else 0.1
            conf = max(0.0, min(1.0, 1.0 - (sigma * 2.0)))
            
            sys_output.append({
                'scene_index': i + 1,
                'effort_score': sig['instantaneous_effort'],
                'tension_score': sig.get('tension', 0.5),
                'confidence_score': conf 
            })
            
        alignment_results = aligner.calculate_alignment('script_001', sys_output)
        agreement_metrics = aligner.calculate_agreement()
        
        # Ablation Study
        ablation_runner = AblationRunner(mock_script)
        ablation_results = ablation_runner.run_study()
        
        # Phase 8: Research Defensibility Layers
        blind_val = BlindValidator()
        blind_results = blind_val.run_validation()
        
        temp_tester = TemporalConsistencyTester()
        temp_metrics = temp_tester.run_test(mock_script)
        
        threshold_deriver = ThresholdDeriver()
        thresholds = threshold_deriver.derive_thresholds()
        
        profiler = ResourceProfiler()
        profile_metrics = profiler.profile_run(mock_script)
        
        # Phase 9: Publication Readiness Layers
        baseline_comp = BaselineComparator()
        # Mock data passthrough for baseline (real system would share aligned_data object)
        # Assuming alignment_results structure roughly matches what we need or we pass raw aligned_data if we had it exposed
        # Re-mocking aligned data for demonstration
        aligned_data_mock = [
            {'human_val': 0.5, 'system_val': 0.8, 'error': 0.3},
            {'human_val': 0.6, 'system_val': 0.7, 'error': 0.1},
            {'human_val': 0.2, 'system_val': 0.2, 'error': 0.0}
        ]
        baseline_metrics = baseline_comp.compare_baselines(aligned_data_mock)
        
        sig_tester = SignificanceTester()
        sig_metrics = sig_tester.calculate_significance(aligned_data_mock)
        
        real_loader = RealReaderLoader()
        real_loader.generate_template_files() # Prepare infra
        
        reporter = BoundaryReporter()
        boundaries = reporter.analyze_boundaries(aligned_data_mock)
        
        # 4. Generate Report
        report = f"# ScriptPulse Research Report (v{self.config['version']})\n"
        report += f"**Timestamp**: {os.popen('date').read().strip()}\n**System**: {os.popen('uname -sr').read().strip()}\n\n"
        
        report += aligner.generate_report(alignment_results, agreement_metrics)
        report += "\n"
        report += sig_tester.generate_report(sig_metrics)
        report += "\n"
        report += baseline_metrics_report(baseline_metrics) # Helper below
        report += "\n"
        report += ablation_runner.generate_report()
        report += "\n"
        report += blind_val.generate_report()
        report += "\n"
        report += temp_tester.generate_report(temp_metrics)
        report += "\n"
        report += threshold_deriver.generate_report(thresholds)
        report += "\n"
        report += reporter.generate_report(boundaries)
        report += "\n"
        report += real_loader.generate_report()
        report += "\n"
        report += profiler.generate_report(profile_metrics)
        
        # New Feature Stats (v1.3)
        report += "\n## 📈 Perceptual Feature Distributions (v1.3)\n"
        if features:
            novs = [f.get('novelty_score', 0) for f in features]
            clars = [f.get('clarity_score', 0) for f in features]
            avg_nov = sum(novs)/len(novs) if novs else 0
            avg_clar = sum(clars)/len(clars) if clars else 0
            report += f"*   **Average Novelty**: {avg_nov:.2f} (Target: >0.4)\n"
            report += f"*   **Average Clarity**: {avg_clar:.2f} (Target: >0.7)\n"
            report += f"*   **Genre Mode**: {self.config.get('parameters', {}).get('genre', 'Universal')}\n"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        params_hash = hashlib.md5(json.dumps(self.config['parameters'], sort_keys=True).encode()).hexdigest()
        filename = f"report_{params_hash}.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(report)
            
        # Write Log
        with open(os.path.join(output_dir, 'reproducibility.log'), 'w') as f:
            f.write(f"Hash: {params_hash}\nModules: {sys.modules.keys()}")
            
        print(f"Run Complete. Report saved to {filepath}")
        print(f"Config Hash: {params_hash}")

def baseline_metrics_report(metrics):
    comp = BaselineComparator()
    return comp.generate_report(metrics)
        
if __name__ == "__main__":
    try:
        repro = ResearchReproducer()
        repro.run_pipeline('dummy_path.txt')
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
