
import random
import statistics
import math
from ..agents.dynamics_agent import DynamicsAgent
from ..agents.perception_agent import EncodingAgent

class TemporalConsistencyTester:
    """
    Verifies that the model outputs are sequence-dependent.
    Refutes the null hypothesis that the model is just a "Bag of Scenes".
    """
    
    def __init__(self):
        pass
        
    def run_test(self, script_data):
        """
        Runs the model on (1) Original Order and (2) Shuffled Order.
        Calculates the correlation between the two effort curves.
        
        HYPOTHESIS: If the model is temporally aware (accumulating fatigue/tension), 
        the shuffled curve should NOT correlate perfectly with the original curve re-sorted.
        Wait, actually:
        - If we shuffle inputs, the output for Scene X should CHANGE because its context changed.
        - Therefore, Output(Scene X | Context A) should != Output(Scene X | Context B).
        - We compare the *values assigned to the same scene index* across runs.
        """
        
        # 1. Original Run
        perception = EncodingAgent()
        dynamics = DynamicsAgent()
        
        features_orig = perception.run(script_data)
        signals_orig = dynamics.run_simulation({'features': features_orig})
        
        # Map: Scene Index -> Attentional Signal (The stateful variable)
        map_orig = {i+1: s['attentional_signal'] for i, s in enumerate(signals_orig)}
        
        # 2. Shuffled Run
        script_shuffled = self._shuffle_script(script_data)
        features_shuf = perception.run(script_shuffled)
        signals_shuf = dynamics.run_simulation({'features': features_shuf})
        
        # Map: FeatureID (Tracked via content matching or ID) -> New Effort Value
        # Since we just shuffled the list, we need to track which scene went where.
        # Our mock script uses 'scene_index' in the dict.
        
        # Identify scenes by their original index which should be preserved in the object
        map_shuf = {}
        for i, s in enumerate(signals_shuf):
            # We need to look up which original scene this corresponds to.
            # The 'features' list is aligned with 'signals'.
            # The 'features' come from 'perception.run' which processes the shuffled list.
            # We rely on 'scene_index' field being preserved in the scene object if perception passes it through.
            # Perception agent typically returns structural features. Let's assume we can map back.
            
            # Hack for verification: relying on the fact that we can track the shuffle.
            # Actually, let's just compare the *Distribution*.
            # Better Test: Compare the delta.
            
            # Proper Test:
            # For Scene S_k:
            # V_orig = Model(S_k | Sequence_Original)
            # V_shuf = Model(S_k | Sequence_Random)
            # Delta = |V_orig - V_shuf|
            # We want Mean(Delta) > Threshold (proving context matters).
            pass

        # Re-implementation for clarity
        # We need to track the original ID of the shuffled scenes.
        # Let's assume script_shuffled['scenes'] contains dicts with 'scene_index'.
        
        deltas = []
        for i, scene in enumerate(script_shuffled['scenes']):
            orig_idx = scene['scene_index']
            
            val_orig = map_orig[orig_idx]
            val_shuf = signals_shuf[i]['attentional_signal'] # This is the effort for the scene at position i (which is orig_idx)
            
            deltas.append(abs(val_orig - val_shuf))
            
        avg_delta = statistics.mean(deltas)
        
        return {
            'avg_delta': avg_delta,
            'is_consistent': avg_delta > 0.01 # Threshold: Context must change score by at least 1%
        }

    def _shuffle_script(self, script_data):
        import copy
        new_script = copy.deepcopy(script_data)
        random.seed(42) # Fixed seed for reproducibility
        random.shuffle(new_script['scenes'])
        return new_script

    def generate_report(self, metrics):
        md = "### Temporal Consistency (Shuffle Test)\n\n"
        md += "**Hypothesis**: Model should produce different scores for the same scene when context changes.\n\n"
        md += f"- **Avg Score Change (Delta)**: {metrics['avg_delta']:.4f}\n"
        
        if metrics['is_consistent']:
            md += "- **Result**: PASSED. (Model demonstrates temporal awareness)\n"
        else:
            md += "- **Result**: FAILED. (Model appears permutation-invariant / Bag-of-Words)\n"
            
        return md
