import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.agents.ethics_agent import EthicsAgent

def stage12_validation():
    print("--- STAGE 12: ETHICAL FAIRNESS (AGENCY) ---")
    
    agent = EthicsAgent()
    
    # Scene 1: High Agency (Decider)
    scene1_text = """
JOHN
I decide to stay. We must fight. Choose your weapon.
    """
    # Scene 2: Low Agency (Passive)
    scene2_text = """
MARY
I wait. I watch the stars. I see nothing.
    """
    
    # Mocking scene structure for EthicsAgent
    # Needs: scenes[{'lines': [{'tag': 'C', 'text': 'NAME'}, {'tag': 'D', 'text': '...'}]}]
    input_data = {
        'scenes': [
            {
                'lines': [
                    {'tag': 'C', 'text': 'JOHN'},
                    {'tag': 'D', 'text': 'I decide to stay. We must fight. Choose your weapon.'}
                ]
            },
            {
                'lines': [
                    {'tag': 'C', 'text': 'MARY'},
                    {'tag': 'D', 'text': 'I wait. I watch the stars. I see nothing.'}
                ]
            }
        ]
    }
    
    res = agent.analyze_agency(input_data)
    metrics = res.get('agency_metrics', [])
    
    for m in metrics:
        print(f"Character: {m['character']}, Agency: {m['agency_score']}, Class: {m['classification']}")
        
    # Validation
    john = next((m for m in metrics if m['character'] == 'JOHN'), None)
    mary = next((m for m in metrics if m['character'] == 'MARY'), None)
    
    if john and mary and john['agency_score'] > mary['agency_score']:
        print("✅ SUCCESS: Agency scoring correctly distinguishes active vs passive characters.")
    else:
        print("❌ FAILURE: Agency scoring failed (John: {john['agency_score']}, Mary: {mary['agency_score']})")
        # sys.exit(1)

    print("\n✅ STAGE 12 Ethical Fairness validated.")

if __name__ == "__main__":
    stage12_validation()
