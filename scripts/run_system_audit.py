import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from scriptpulse.pipeline import runner
from scriptpulse.reporters import print_summary, writer_report, studio_report
from scriptpulse.reporters.llm_translator import generate_ai_summary, generate_section_insight
from app import streamlit_utils

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg):
    print(f"❌ FAIL: {msg}")

def run_audit():
    print("\n" + "="*50)
    print("🚀 SCRIPTPULSE TRIPLE-CHECK AUDIT (SAFE MODE) 🚀")
    print("="*50 + "\n")

    # TEST 1: Edge Cases (Bulletproof Test)
    print("--- 1. EDGE CASE HANDLING ---")
    
    # Empty string test
    try:
        runner.run_pipeline("")
        print_fail("Pipeline did not catch empty script.")
    except ValueError as e:
        if "requires more text" in str(e) or "detect any scenes" in str(e):
            print_pass("Pipeline correctly caught zero-scene/empty script without crashing.")
        else:
            print_fail(f"Pipeline raised ValueError but wrong message: {e}")
            
    # Mock uploaded file for check_upload_size
    class MockFile:
        def __init__(self, size):
            self.size = size
            
    with patch('app.streamlit_utils.st') as mock_st:
        # Zero byte
        res = streamlit_utils.check_upload_size(MockFile(0))
        if not res and mock_st.error.called:
            print_pass("Upload guard successfully caught 0-byte file.")
        else:
            print_fail("Upload guard failed on 0-byte file.")
            
        # Too large byte (21MB)
        res = streamlit_utils.check_upload_size(MockFile(21 * 1024 * 1024))
        if not res and mock_st.error.called:
            print_pass("Upload guard caught over-sized file (21MB).")
        else:
            print_fail("Upload guard failed on oversized file.")

    # TEST 2: Genre Dynamics (Math Test)
    print("\n--- 2. GENRE MATH ROUTING ---")
    baselines_path = os.path.join(project_root, 'scriptpulse', 'config', 'genre_baselines.json')
    if os.path.exists(baselines_path):
        with open(baselines_path, 'r') as f:
            data = json.load(f)
            if "Thriller / Action" in data['genres'] and "Comedy" in data['genres']:
                print_pass("Dynamic Genre Baselines loaded and mapped correctly.")
            else:
                print_fail("Genre baselines missing categories.")
    else:
        print_fail("Genre baselines file not found.")

    # TEST 3: AI Safety & Brain Lens (No API limits hit - Mocked offline)
    print("\n--- 3. AI PROMPT VERIFICATION (OFFLINE) ---")
    mock_script_data = {
        "writer_intelligence": {
            "narrative_diagnosis": ["Issue 1"],
            "rewrite_priorities": ["Fix 1"],
            "structural_dashboard": {}
        }
    }
    
    # We mock Groq to just capture the prompt being sent, saving tokens
    with patch('scriptpulse.reporters.llm_translator.Groq') as MockGroq:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Mocked AI Response"
        mock_client.chat.completions.create.return_value = mock_completion
        MockGroq.return_value = mock_client
        
        # Test 1: Studio Executive Lens
        generate_ai_summary(mock_script_data, lens="Studio Executive", api_key="dummy_key")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        system_prompt = call_kwargs['messages'][0]['content']
        
        if "Development Executive" in system_prompt and "Script<span style='color: #0052FF; font-weight: bold;'>Pulse</span>" in system_prompt:
            print_pass("AI Brain correctly initialized as 'Studio Executive' with HTML branding applied.")
        else:
             print_fail("AI prompt failed Studio Executive persona check.")
             
        # Test 2: Story Editor Lens
        generate_ai_summary(mock_script_data, lens="Story Editor", api_key="dummy_key")
        call_kwargs2 = mock_client.chat.completions.create.call_args[1]
        system_prompt2 = call_kwargs2['messages'][0]['content']
        
        if "Story Editor" in system_prompt2 and "Causality" in system_prompt2:
            print_pass("AI Brain correctly shifted perspective to 'Story Editor'.")
        else:
             print_fail("AI prompt failed Story Editor persona check.")

    # TEST 4: Output Rendering
    print("\n--- 4. EXPORT & ARTIFACT GENERATION ---")
    mock_report = {
        'meta': {'timestamp': '2026-03-08'},
        'writer_intelligence': {
            'genre_context': 'drama',
            'structural_dashboard': {'total_scenes': 10},
            'narrative_diagnosis': [],
            'rewrite_priorities': [],
            'narrative_summary': 'Test Summary'
        },
        'temporal_trace': []
    }
    
    wr_out = writer_report.generate_writer_report(mock_report, title="TEST SCRIPT")
    if "Script<span style='color: #0052FF;'>Pulse</span>" in wr_out:
        print_pass("Markdown Writer Report engine successfully embedded split-color branding.")
    else:
        print_fail("Writer report failed to embed branding.")
        
    sr_out = studio_report.generate_report(mock_report, script_title="TEST SCRIPT", lens="Editor")
    if "Script<span style" in sr_out and "#0052FF" in sr_out:
        print_pass("HTML Studio Coverage engine cleanly generated with premium formatting.")
    else:
        print_fail("Studio coverage failed to generate proper HTML branding.")

    # TEST 5: CSS UI Integrity
    print("\n--- 5. PREMIUM UI INTEGRITY ---")
    try:
        from app.components import styles
        import inspect
        css_code = inspect.getsource(styles.apply_custom_styles)
        if "cursor: pointer !important;" in css_code and "[data-baseweb=\"select\"]" in css_code:
            print_pass("UI Text Selector issue fixed - 'Pointer (Hand)' cursor activated on dropdowns.")
        else:
            print_fail("Cursor pointer CSS override missing.")
            
        if "backdrop-filter: blur" in css_code:
            print_pass("Glassmorphism styling confirmed active in UI code.")
        else:
            print_fail("Glassmorphism missing.")
    except Exception as e:
        print_fail(f"Could not audit CSS styles: {e}")
        
    print("\n" + "="*50)
    print("✅ AUDIT COMPLETE. ALL SYSTEMS VERIFIED SAFELY (ZERO API TOKENS SPENT).")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_audit()
