
import unittest
import json
import statistics
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scriptpulse.agents.dynamics_agent import DynamicsAgent, ReaderProfile
from scriptpulse.agents.perception_agent import EncodingAgent
from scriptpulse.agents.experimental_agent import MultiLabelEmotionAgent, StakesDetector
from scriptpulse.agents.ethics_agent import EthicsAgent

class TestScriptPulseUpgrades(unittest.TestCase):
    
    def setUp(self):
        self.dynamics = DynamicsAgent()
        self.perception = EncodingAgent()
        self.emotion = MultiLabelEmotionAgent()
        self.stakes = StakesDetector()
        self.ethics = EthicsAgent()
        
        # Mock Data
        self.action_scene = {
            'scene_index': 1,
            'lines': [
                {'text': 'EXT. BATTLEFIELD - DAY', 'tag': 'S', 'line_index': 1},
                {'text': 'The tank CRASHES through the wall.', 'tag': 'A', 'line_index': 2},
                {'text': 'Soldiers RUN and DIVE for cover.', 'tag': 'A', 'line_index': 3},
                {'text': 'EXPLOSIONS rock the ground.', 'tag': 'A', 'line_index': 4},
                {'text': 'SARGE', 'tag': 'C', 'line_index': 5},
                {'text': 'Go! Go! Move it!', 'tag': 'D', 'line_index': 6}
            ]
        }
        
        self.dialogue_scene = {
            'scene_index': 2,
            'lines': [
                {'text': 'INT. CAFE - DAY', 'tag': 'S', 'line_index': 10},
                {'text': 'ALICE', 'tag': 'C', 'line_index': 11},
                {'text': 'I cannot believe you did that to me. It is over.', 'tag': 'D', 'line_index': 12},
                {'text': 'BOB', 'tag': 'C', 'line_index': 13},
                {'text': 'Please, let me explain. It was a misunderstanding.', 'tag': 'D', 'line_index': 14}
            ]
        }
        
        self.complex_scene = {
            'scene_index': 3,
            'lines': [
                {'text': 'INT. LIBRARY - NIGHT', 'tag': 'S', 'line_index': 20},
                {'text': 'The ancient manuscript lies on the mahogany table, its edges curler with age and the smell of rot pervading the room.', 'tag': 'A', 'line_index': 21},
                {'text': 'PROFESSOR', 'tag': 'C', 'line_index': 22},
                {'text': 'The epistemological implications of this discovery are paradigmatic, shifting the very ontology of our understanding.', 'tag': 'D', 'line_index': 23}
            ]
        }

    def test_readability_metrics(self):
        print("\n[Perception] Testing Readability metrics...")
        input_data = {'scenes': [self.complex_scene], 'lines': self.complex_scene['lines']}
        features = self.perception.run(input_data)[0]
        
        ling = features['linguistic_load']
        print(f"  Flesch-Kincaid: {ling.get('readability_grade')}")
        print(f"  Idea Density: {ling.get('idea_density')}")
        
        self.assertIn('readability_grade', ling)
        self.assertIn('idea_density', ling)
        self.assertGreater(ling['readability_grade'], 5.0, "Complex text should have high grade level")

    def test_dynamics_reader_profile(self):
        print("\n[Dynamics] Testing ReaderProfile impact...")
        # Use a low-effort scene to ensure recovery is possible (Effort < R_MAX)
        boring_scene = {
            'scene_index': 99,
            'lines': [
                {'text': 'INT. ROOM - DAY', 'tag': 'S', 'line_index': 1},
                {'text': 'A chair sits in the corner.', 'tag': 'A', 'line_index': 2},
                {'text': 'It is quiet.', 'tag': 'A', 'line_index': 3}
            ]
        }
        feats = [self.perception.run({'scenes': [boring_scene]})[0]]
        
        # Profile 1: Novice (Low Tolerance)
        prof_novice = ReaderProfile(familiarity=0.1, tolerance=0.1).get_params()
        res_novice = self.dynamics.run_simulation({'features': feats}, profile_params=prof_novice)
        
        # Profile 2: Expert (High Tolerance)
        prof_expert = ReaderProfile(familiarity=0.9, tolerance=0.9).get_params()
        res_expert = self.dynamics.run_simulation({'features': feats}, profile_params=prof_expert)
        
        rec_novice = res_novice[0]['recovery_credit']
        rec_expert = res_expert[0]['recovery_credit']
        
        print(f"  Recovery (Novice): {rec_novice}")
        print(f"  Recovery (Expert): {rec_expert}")
        
        self.assertGreater(rec_expert, rec_novice, "Expert should recover faster")

    def test_emotion_and_stakes(self):
        print("\n[Experimental] Testing Emotion and Stakes...")
        text = "The bomb is going to explode! Run for your lives! I am so scared!"
        
        emo = self.emotion.run(text)
        stakes = self.stakes.run(text)
        
        print(f"  Emotions: {emo['emotions']}")
        print(f"  Compounds: {emo['compounds']}")
        print(f"  Stakes: {stakes}")
        
        self.assertGreater(emo['emotions']['fear'], 0.1, "Should detect fear")
        self.assertEqual(stakes['stakes'], 'High', "Should detect high stakes (bomb, run)")

    def test_role_classification(self):
        print("\n[Ethics] Testing Role Classifier...")
        # Mock scenes with clear protagonist
        scenes = []
        # Hero speaks 10 times
        for i in range(10):
            scenes.append({'lines': [{'tag': 'C', 'text': 'HERO'}, {'tag': 'D', 'text': 'I am the hero.'}]})
        # Villain speaks 2 times
        for i in range(2):
            scenes.append({'lines': [{'tag': 'C', 'text': 'VILLAIN'}, {'tag': 'D', 'text': 'I am bad.'}]})
            
        input_data = {'scenes': scenes}
        roles = self.ethics.classify_roles(input_data)
        
        print(f"  Roles: {roles}")
        
        self.assertEqual(roles['HERO'], 'Protagonist')
        self.assertIn(roles['VILLAIN'], ['Supporting', 'Minor', 'Major Support']) # Depends on ratio

    def test_counterfactuals(self):
        print("\n[Interpretation] Testing Counterfactuals (Static Check)...")
        # Just verifying the class exists and imports logic (Integration test would require InterpretationAgent instance)
        from scriptpulse.agents.interpretation_agent import CounterfactualExplainer
        cf = CounterfactualExplainer()
        self.assertIsNotNone(cf.dynamics)

if __name__ == '__main__':
    unittest.main()
