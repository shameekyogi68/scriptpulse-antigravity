#!/usr/bin/env python3
"""
ScriptPulse Validator - Sanity check for pipeline execution
"""

import sys
sys.path.insert(0, '.')

from runner import run_pipeline


def test_determinism():
    """Test that same input produces identical output"""
    test_script = """INT. OFFICE - DAY

JOHN
Hello, world.

He walks to the door.

FADE OUT."""
    
    # Run twice
    output1 = run_pipeline(test_script)
    output2 = run_pipeline(test_script)
    
    # Assert identical
    assert output1 == output2, "Pipeline is not deterministic!"
    print("✓ Determinism check passed")
    
    return output1


def test_no_exceptions():
    """Test that pipeline completes without error"""
    test_script = """INT. TEST - DAY

This is a test."""
    
    try:
        result = run_pipeline(test_script)
        assert result is not None
        assert isinstance(result, dict)
        print("✓ No exceptions raised")
        return True
    except Exception as e:
        print(f"✗ Exception raised: {e}")
        return False


def main():
    print("Running ScriptPulse validation...")
    print()
    
    # Test 1: No exceptions
    if not test_no_exceptions():
        sys.exit(1)
    
    # Test 2: Determinism
    test_determinism()
    
    print()
    print("✅ All validation checks passed!")


if __name__ == '__main__':
    main()
