
import statistics
import random
from ..agents.dynamics_agent import DynamicsAgent
from ..agents.perception_agent import EncodingAgent

class ThresholdDeriver:
    """
    Derives alert thresholds from the statistical distribution of simulated runs.
    Replaces arbitrary constants with percentile-based justifications.
    """
    
    def __init__(self, sample_size=100):
        self.sample_size = sample_size
        
    def derive_thresholds(self):
        """
        Runs simulations with randomized inputs to generate a distribution of Effort scores.
        Calculates p75, p90, p95.
        """
        print(f"Deriving thresholds from {self.sample_size} simulations...")
        
        all_efforts = []
        dynamics = DynamicsAgent()
        
        for _ in range(self.sample_size):
            # Create a "Random Scene"
            features = {
                'linguistic_load': {
                    'readability_grade': random.uniform(4, 16), 
                    'idea_density': random.uniform(0.2, 0.8),
                    'sentence_length_variance': random.uniform(10, 50),
                    'sentence_count': random.randint(1, 100)
                },
                'formatting_features': {'action_density': random.random()},
                'referential_load': {
                    'entity_churn': random.random() * 0.5,
                    'active_character_count': random.randint(1, 5),
                    'character_reintroductions': random.randint(0, 2)
                },
                'structural_change': {'event_boundary_score': random.uniform(0, 100)},
                'entropy_score': random.uniform(2.0, 6.0),
                'dialogue_dynamics': {
                    'turn_velocity': random.uniform(0, 10),
                    'dialogue_line_count': random.randint(0, 20)
                },
                'visual_abstraction': {
                    'action_lines': random.randint(0, 20)
                },
                'ambient_signals': {
                    'mood_score': random.random(),
                    'component_scores': {'stillness': random.random()}
                },
                'scene_index': 1
            }
            
            # Run single pass logic (conceptually)
            # We'll just run a 1-scene script
            mock_input = {'features': [features]}
            signals = dynamics.run_simulation(mock_input)
            all_efforts.append(signals[0]['instantaneous_effort'])
            
        all_efforts.sort()
        n = len(all_efforts)
        
        thresholds = {
            'fatigue_p75': all_efforts[int(n*0.75)],
            'fatigue_p90': all_efforts[int(n*0.90)],
            'fatigue_p95': all_efforts[int(n*0.95)]
        }
        
        return thresholds

    def generate_report(self, thresholds):
        md = "### Threshold Justification (Percentile-Based)\n\n"
        md += "| Level | Percentile | Threshold Value | Meaning |\n"
        md += "|---|---|---|---|\n"
        md += f"| Elevated | p75 | >{thresholds['fatigue_p75']:.2f} | Top 25% complexity |\n"
        md += f"| **High** | p90 | >{thresholds['fatigue_p90']:.2f} | Top 10% (Alert logic) |\n"
        md += f"| Extreme | p95 | >{thresholds['fatigue_p95']:.2f} | Rare overload |\n"
        return md
