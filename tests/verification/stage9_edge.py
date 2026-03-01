import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from scriptpulse.pipeline import runner

def stage9_validation():
    print("--- STAGE 9: FEATURE EDGE CASES (STABILITY) ---")
    
    # Define extreme edge cases
    scripts = [
        ("Empty String", ""),
        ("Single Word", "HELLO"),
        ("Single Huge Scene", "INT. VOID - NEVER\n" + ("Action line here.\n" * 1000)),
        ("Emoji Only", "😀 😂 🤣 😃 😄 😅 😆 😉 😊 😋 😎 😍"),
        ("Non-Latin Script", "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ? ಇದು ಒಂದು ಕನ್ನಡ ಸ್ಕ್ರಿಪ್ಟ್."),
        ("Binary-ish Junk", "\x00\x01\x02\x03\x04\x05 JUNK BOX DATA"),
        ("Huge Word", "A" * 1000),
    ]
    
    # Ensure heuristics
    os.environ["SCRIPTPULSE_HEURISTICS_ONLY"] = "1"
    
    success_count = 0
    for name, text in scripts:
        try:
            print(f"Processing Edge Case: {name}...")
            runner.run_pipeline(text)
            success_count += 1
            print(f"✅ {name} Resilience Success.")
        except ValueError as ve:
            if "Binary payload" in str(ve):
                 success_count += 1
                 print(f"✅ {name} Resilience Success (Safe Rejection).")
            else:
                 print(f"❌ {name} Crashed: {ve}")
        except Exception as e:
            print(f"❌ {name} Crashed: {e}")
            import traceback
            traceback.print_exc()
            
    if success_count == len(scripts):
        print("\n🏆 STAGE 9 PASSED: All extreme edge cases survived without crash.")
    else:
        print(f"\n⚠️ STAGE 9 FAILED: {len(scripts)-success_count} edge cases caused a crash.")
        sys.exit(1)

if __name__ == "__main__":
    stage9_validation()
