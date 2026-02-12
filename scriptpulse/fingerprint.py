"""
Structural Fingerprint & Determinism Engine (SFE/DRL)
vNext.5 Market Upgrade - Enterprise Trust

Implements:
1. Structural Fingerprinting (SFE): Unique hash of structural elements only.
2. Deterministic Run Signing (DRL): Traceable RunIDs based on input + config.
"""

import hashlib
import json
import time

# Versioning CONSTANT (VCG)
CALIBRATION_VERSION = "5.0.0-phase3"

def generate_structural_fingerprint(parsed_lines, scenes):
    """
    Generate a hash characterizing the SCRIPT STRUCTURE only.
    Ignores cosmetic text changes (typos, minor dialogue tweaks) unless
    they alter line counts or classifications.
    
    Used for: Detecting meaningful draft changes.
    """
    # 1. Structural Metadata
    structure_data = {
        'total_scenes': len(scenes),
        'total_lines': len(parsed_lines),
        'scene_lengths': [s['end_line'] - s['start_line'] + 1 for s in scenes],
        'line_types': [l['tag'] for l in parsed_lines],
        # We assume scene headings are structural anchors
        'scene_headings': [s['heading'] for s in scenes if s.get('heading')]
    }
    
    # 2. Serialize canonical JSON
    structure_str = json.dumps(structure_data, sort_keys=True)
    
    # 3. Hash
    fingerprint = hashlib.sha256(structure_str.encode('utf-8')).hexdigest()
    
    return fingerprint

def generate_content_fingerprint(parsed_lines):
    """
    v13.1: Generate a content-aware hash that changes on ANY text edit.
    Normalized: lowercase, whitespace collapsed, timestamps removed.
    """
    import re
    combined = " ".join(l.get('text', '') for l in parsed_lines)
    # Normalize
    normalized = combined.lower()
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    normalized = re.sub(r'\d{1,2}:\d{2}(:\d{2})?', '', normalized)  # Remove timestamps
    
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def generate_run_id(fingerprint, lens_config_id, intent_data=None, content_fingerprint=None):
    """
    Generate a Deterministic Run ID (DRL).
    
    v13.1: Now includes content_fingerprint so word-level edits change the run ID.
    
    RunID = hash(Structure + Content + Calibration + Config + Intent)
    
    Guarantees: Same input + Same settings = Same ID.
    """
    intent_str = json.dumps(intent_data, sort_keys=True) if intent_data else "no_intent"
    content_fp = content_fingerprint or "no_content"
    
    payload = f"{fingerprint}|{content_fp}|{CALIBRATION_VERSION}|{lens_config_id}|{intent_str}"
    
    run_id = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    return run_id, CALIBRATION_VERSION
