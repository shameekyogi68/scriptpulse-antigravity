#!/usr/bin/env python3
"""
Schema Compliance Checker (v13.1)

Verifies pipeline output against api_contract_v13_1.json.

Rules:
    - All required keys must be present
    - Types must match
    - Keys may be ADDED (additive-only)
    - Keys may NOT be removed or renamed
    - On violation: exit 1

Usage:
    PYTHONPATH=. python3 tests/schema_compliance.py
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

CONTRACT_PATH = os.path.join(PROJECT_ROOT, 'api_contract_v13_1.json')

TYPE_MAP = {
    'int': int,
    'float': (int, float),
    'string': str,
    'list': list,
    'object': dict,
    'list[object]': list,
    'bool': bool,
}


def load_contract():
    with open(CONTRACT_PATH, 'r') as f:
        return json.load(f)


def check_keys(data, required_keys, context):
    """Check that all required keys are present."""
    errors = []
    if not isinstance(data, dict):
        errors.append(f"{context}: Expected dict, got {type(data).__name__}")
        return errors
    
    for key in required_keys:
        if key not in data:
            errors.append(f"{context}: Missing required key '{key}'")
    return errors


def check_types(data, type_spec, context):
    """Check that values match expected types."""
    errors = []
    if not isinstance(data, dict):
        return errors
    
    for key, expected_type_str in type_spec.items():
        if key not in data:
            continue
        value = data[key]
        if value is None:
            continue  # None allowed for optional values
        
        expected = TYPE_MAP.get(expected_type_str)
        if expected and not isinstance(value, expected):
            errors.append(
                f"{context}.{key}: Expected {expected_type_str}, got {type(value).__name__}"
            )
    return errors


def run_compliance(result, contract):
    """Run full schema compliance check against a pipeline result."""
    all_errors = []
    
    # 1. Pipeline output top-level keys
    spec = contract['pipeline_output']
    all_errors += check_keys(result, spec['required_keys'], 'pipeline_output')
    all_errors += check_types(result, spec.get('types', {}), 'pipeline_output')
    
    # 2. Meta fields
    meta = result.get('meta', {})
    spec = contract['meta_fields']
    all_errors += check_keys(meta, spec['required_keys'], 'meta')
    all_errors += check_types(meta, spec.get('types', {}), 'meta')
    
    # 3. Debug export layout
    debug = result.get('debug_export', {})
    spec = contract['debug_export_layout']
    all_errors += check_keys(debug, spec['required_keys'], 'debug_export')
    
    # Check per_scene items
    per_scene = debug.get('per_scene', [])
    if per_scene and isinstance(per_scene, list):
        item = per_scene[0]
        all_errors += check_keys(item, spec['per_scene_item']['required_keys'], 'debug_export.per_scene[0]')
        vectors = item.get('agent_vectors', {})
        for vk in spec['per_scene_item']['agent_vectors_keys']:
            if vk not in vectors:
                all_errors.append(f"debug_export.per_scene[0].agent_vectors: Missing '{vk}'")
    
    # 4. Uncertainty trace fields
    uncertainty = result.get('uncertainty_quantification', [])
    if uncertainty and isinstance(uncertainty, list):
        spec = contract['uncertainty_trace_fields']
        all_errors += check_keys(uncertainty[0], spec['required_keys'], 'uncertainty[0]')
        all_errors += check_types(uncertainty[0], spec.get('types', {}), 'uncertainty[0]')
    
    # 5. Scene info items
    scene_info = result.get('scene_info', [])
    if scene_info and isinstance(scene_info, list):
        spec = contract['scene_info_item']
        all_errors += check_keys(scene_info[0], spec['required_keys'], 'scene_info[0]')
        all_errors += check_types(scene_info[0], spec.get('types', {}), 'scene_info[0]')
    
    # 6. Temporal trace items
    trace = result.get('temporal_trace', [])
    if trace and isinstance(trace, list):
        spec = contract['temporal_trace_item']
        all_errors += check_keys(trace[0], spec['required_keys'], 'temporal_trace[0]')
        
        # Bounds check
        for i, point in enumerate(trace):
            sig = point.get('attentional_signal')
            if sig is not None:
                if not (0 <= sig <= 1):
                    all_errors.append(f"temporal_trace[{i}].attentional_signal: Out of bounds ({sig})")
    
    return all_errors


def main():
    contract = load_contract()
    
    print("=" * 60)
    print("SCHEMA COMPLIANCE CHECK — api_contract_v13_1.json")
    print("=" * 60)
    
    # Run pipeline on a minimal script
    from scriptpulse import runner
    
    test_script = """INT. OFFICE - DAY

ALEX
(firmly)
We need to talk about the project.

MARIA
I know. It's been difficult.

EXT. STREET - NIGHT

Cars pass in silence. ALEX walks alone."""

    print("\n  Running pipeline on test script...")
    result = runner.run_pipeline(test_script, experimental_mode=True, moonshot_mode=True)
    
    print("  Checking schema compliance...")
    errors = run_compliance(result, contract)
    
    if errors:
        print(f"\n  ❌ SCHEMA VIOLATIONS ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
        print(f"\n❌ SCHEMA CHECK: FAIL")
        sys.exit(1)
    else:
        print(f"\n  ✅ All required keys present")
        print(f"  ✅ All types match")
        print(f"  ✅ Temporal bounds valid")
        print(f"\n✅ SCHEMA CHECK: PASS")
        sys.exit(0)


if __name__ == '__main__':
    main()
