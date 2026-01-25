# Interpretive Pattern Agent

**Agent ID:** 4.5  
**Pipeline Position:** Fifth-stage  
**Status:** ✅ Implemented

## Purpose

The Interpretive Pattern Agent detects persistent experiential patterns in attentional signals **without evaluation or judgment**.

This agent identifies what is happening in the signal, NOT whether it's good or bad.

## Responsibility

> Detect persistent experiential patterns in attentional signals without assigning value, importance, or prescription.

**Exclusive scope:** Pattern detection only. No evaluation, no recommendations.

## Input Contract

**Input:**
- Temporal signals (S(t), R[i]) from Temporal Dynamics Agent
- Encoded features for similarity analysis
- Scene segmentation confidence values

## Output Contract

**Output:** JSON with pattern descriptors

```json
{
  "patterns": [
    {
      "pattern_type": "sustained_demand",
      "scene_range": [15, 28],
      "confidence_band": "high",
      "description": "Attentional signal elevated above 1.5 across 14 consecutive scenes",
      "supporting_metrics": {
        "avg_signal": 1.82,
        "scene_count": 14
      }
    }
  ]
}
```

If no patterns detected: `{"patterns": []}`  
(This is NOT a failure—absence of patterns is valid.)

## Allowed Pattern Types

### 1. Sustained Demand
Signal remains elevated (> 1.5) for ≥ 3 scenes

### 2. Limited Recovery
Low recovery credits (< 0.2) while signal elevated

### 3. Sequence Repetition
Similar structural patterns recur at intervals

### 4. Surprise Cluster
Frequent structural boundary spikes (> 25)

### 5. Constructive Strain
High effort WITH recovery balance  
*Descriptive of signal behavior, NOT quality judgment*

### 6. Degenerative Fatigue
High effort WITHOUT recovery balance  
*Descriptive of signal behavior, NOT quality judgment*

## Detection Requirements

### Persistence (≥ 3 Scenes)
All patterns must span at least 3 consecutive scenes. Single-scene anomalies are ignored.

### Multi-Window Agreement
Patterns verified across multiple temporal window sizes to prevent false positives.

### Confidence Downgrading
Confidence bands: High / Medium / Low

Confidence may ONLY decrease based on:
- Short persistence (3 scenes = low)
- Signal volatility
- Low segmentation confidence

**Never** inflate confidence.

## Non-Evaluative Framing

**CRITICAL:** All output is purely descriptive.

❌ **Forbidden:**
- "Problem," "issue," "flaw"
- "Good," "bad," "better," "worse"
- "Should," "must," "needs to"
- "Exhausting," "boring," "confusing"
- "Too much," "too little"

✅ **Allowed:**
- "Elevated," "sustained," "persistent"
- "Limited," "frequent," "sparse"
- "Pattern detected," "signal behavior"

## Constructive vs Degenerative

These terms describe **signal dynamics**, NOT writing quality.

- **Constructive**: Effort + counterbalance (recovery OR structure)
- **Degenerative**: Effort without counterbalance (accumulation)

Both can be intentional artistic choices. Neither implies success or failure.

## Implementation

See [pattern_detector.py](file:///Users/shameekyogi/Desktop/scriptpulse-antigravity/antigravity/agents/pattern_detection/pattern_detector.py)

### Key Classes

- **`Pattern`**: Data class for pattern descriptor
- **`PatternDetector`**: Main detection engine with methods for each pattern type

## Validation

All output validated for:
- Persistence requirement (≥ 3 scenes)
- No evaluative language
- Proper confidence assignment
- Only allowed pattern types

### Running Validation

```bash
# Detect patterns
python antigravity/agents/pattern_detection/pattern_detector.py \
  temporal.json features.json > patterns.json

# Validate
python antigravity/agents/pattern_detection/validator.py patterns.json
```

## Integration

**Upstream:** Temporal Dynamics Agent (4.4)  
**Downstream:** Experience Translation (later)

**Data flow:**
```
Temporal signals → Pattern Detection → Pattern descriptors → Translation
```

## Compliance

**Design Philosophy:** ✅ Description only, no evaluation  
**Truth Boundaries:** ✅ No judgment, no prescription  
**Forbidden Language:** ✅ Strictly enforced  
**Pattern Equality:** ✅ No ranking or prioritization  

## References

- Core Spec: Sections 12-15
- Antigravity Implementation Guide: Agent 4.5
- Pattern Detection Schema
