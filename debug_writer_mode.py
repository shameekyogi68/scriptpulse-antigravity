
import sys
import os
# Add current dir to path
sys.path.append(os.getcwd())

from scriptpulse.agents.writer_agent import WriterAgent
from scriptpulse.reporters.studio_report import generate_report

def run_writer_stress_test():
    print("🎬 MOCKING 'BROKEN THRILLER' SCRIPT...")
    
    # 1. Create a Synthetic Trace with Specific Flaws
    # Flaw A: Sustained Intensity (Fatigue) from Scene 10-18
    # Flaw B: Confusion Spike (Strain) at Scene 25
    
    trace = []
    
    for i in range(40):
        # Default: Healthy
        signal = 0.5
        fatigue = 0.2
        strain = 0.1
        
        # Mock Subtext/Irony/Nuance Signals
        action_density = 0.5
        dialogue_density = 0.5
        sentiment = 0.0
        conflict = 0.0
        stakes = 0.5
        agency = 0.8
        
        # Inject Sustained Fatigue (Scenes 10-18)
        if 10 <= i <= 18:
            signal = 0.9
            fatigue = 0.95 
            
        # Inject Confusion (Scene 25)
        if i == 25:
            strain = 0.95
            
        # Inject Tense Silence (Scene 20-22): Low signal, high stakes
        if 20 <= i <= 22:
            signal = 0.05
            stakes = 0.9
            
        # Inject Accidental Passivity (Scene 2-4): Low agency, low conflict
        if 2 <= i <= 4:
            agency = 0.1
            conflict = 0.2
            
        # Inject Thematic Passivity (Scene 32-34): Low agency, high conflict, low sentiment
        if 32 <= i <= 34:
            agency = 0.1
            conflict = 0.9
            sentiment = -0.8
            
        # Inject Boredom (Scenes 30-31)
        if 30 <= i <= 31:
            signal = 0.05 
            stakes = 0.2
            
        # Inject Subtext (High Action, Low Dialogue) - Scene 5
        if i == 5:
            action_density = 0.9
            dialogue_density = 0.1
            
        # Inject Irony (Positive Sentiment, High Conflict) - Scene 38
        if i == 38:
            sentiment = 0.8
            conflict = 0.9

        trace.append({
            'scene_index': i + 1,
            'attentional_signal': signal,
            'fatigue_state': fatigue,
            'expectation_strain': strain,
            'instantaneous_effort': signal,
            'action_density': action_density,
            'dialogue_density': dialogue_density,
            'sentiment': sentiment,
            'conflict': conflict,
            'stakes': stakes,
            'agency': agency
        })
        
    # 2. Mock Suggestions
    suggestions = {
        'structural_repair_strategies': [
            "Cut dialogue in Scene 12 to reduce load.",
            "Consider splitting Scene 15 to break fatigue.",
        ]
    }
    
    # 3. Analyze with WriterAgent (Test Genre: Horror)
    print("🎥 TESTING GENRE: HORROR (Expects slower pacing to be OK)")
    final_output = {
        'temporal_trace': trace,
        'suggestions': suggestions,
        'meta': {'confidence_score': {'level': 'HIGH', 'score': 0.85}}
    }
    
    agent = WriterAgent()
    enriched = agent.analyze(final_output, genre="Horror")
    
    # 4. Extract Writer Intelligence
    wi = enriched['writer_intelligence']
    
    print("\n📝 EXECUTIVE SUMMARY (Writer's View)")
    print("====================================")
    print(f"Genre Context: {wi.get('genre_context')}")
    
    print("\n🔍 MAIN STORY ISSUES:")
    for item in wi['narrative_diagnosis']:
        print(f"  - {item}")
        
    print("\n🛠️ REWRITE PRIORITIES (High Leverage):")
    for edit in wi['rewrite_priorities']:
        print(f"  [{edit['leverage']}] {edit['action']}")
        
    print("\n📊 STRUCTURAL HEALTH:")
    dash = wi['structural_dashboard']
    print(f"  Midpoint Status: {dash['midpoint_status']}")
    print(f"  Act 1 Energy: {dash['act1_energy']}")
    
    # 5. Review
    print("\n--- CRITIQUE ---")
    print("Does this help me? If I see 'Sustained Intensity scenes 10-18', I know exactly where to cut.")
    print("If I see 'Split Scene 15', that is a concrete action.")

if __name__ == "__main__":
    run_writer_stress_test()
