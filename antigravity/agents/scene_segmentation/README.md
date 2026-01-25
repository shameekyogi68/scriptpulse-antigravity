# Scene Segmentation Agent

**Agent ID:** 4.2  
**Pipeline Position:** Second-stage  
**Status:** ✅ Implemented

## Purpose

The Scene Segmentation Agent groups structurally tagged screenplay lines into scenes using **conservative boundary detection**.

This agent prioritizes avoiding over-segmentation, especially in messy or early-draft screenplays.

## Responsibility

> Group structurally tagged lines into scenes conservatively, minimizing false boundaries.

**Exclusive scope:** Scene boundary detection based on structural tags only.

## Input Contract

**Input:** Line-level tags from Structural Parsing Agent (S, A, D, C, M)

**Format assumptions:**
- Tags are sequential and complete
- Scene headings may be malformed or missing
- Early drafts may have formatting noise
- One tag per line

## Output Contract

**Output:** JSON with scene boundaries

```json
{
  "scenes": [
    {
      "scene_index": 1,
      "start_line": 1,
      "end_line": 25,
      "boundary_confidence": 0.95
    }
  ]
}
```

**Format rules:**
- Sequential scene indexing (1, 2, 3, ...)
- 1-indexed line numbers
- Inclusive end_line
- Confidence score (0.0-1.0, internal only)

## Segmentation Methodology

### Conservative Philosophy

**When uncertain, prefer MERGING over SPLITTING.**

This prevents the primary failure mode: boundary explosion in messy drafts.

### Boundary Detection Algorithm

#### 1. Initial Boundary Detection

Scan for `S` tags (Scene Headings) as primary boundary indicators.

Not all `S` tags create boundaries — confidence must be > 0.3.

#### 2. Confidence Scoring

Calculate `boundary_confidence` based on:

- **Context stability**: Stable tag patterns around `S` → higher confidence
  - Good: `...A S A C D...`
  - Bad: `...M S M M...`

- **Noise indicators**: Reduce confidence for:
  - Multiple consecutive `S` tags (formatting error)
  - Isolated `S` surrounded by metadata
  - Unusual tag transitions

**Confidence levels:**
- 0.9-1.0: Clear boundary, stable pattern
- 0.6-0.8: Reasonable boundary, some irregularity
- 0.3-0.5: Ambiguous boundary
- 0.0-0.2: Very weak signal (should merge)

#### 3. Minimum Scene Length

Scenes must contain ≥3 lines (configurable: `MIN_SCENE_LENGTH`).

Micro-scenes (1-2 lines) are likely formatting errors → merged with adjacent scenes.

#### 4. Post-Merge Heuristics

After initial segmentation:
1. Merge scenes with confidence < 0.6 (configurable: `MERGE_CONFIDENCE_THRESHOLD`)
2. Combine adjacent low-confidence scenes
3. Smooth boundaries to reduce fragmentation

### Allowed Techniques

- **Structural tag analysis**: S, A, D, C, M patterns
- **Positional context**: Surrounding tag sequences
- **Pattern stability**: Tag transition regularity
- **Format cues**: Tag positioning

### Forbidden Techniques

❌ **The following are absolutely prohibited:**

- Time shift inference ("later", "meanwhile")
- Location change inference from content
- Narrative structure analysis
- Semantic content of action/dialogue
- Enforcing industry norms blindly
- Confidence inflation when uncertain
- Using transitions (M tags) as guaranteed boundaries

**Violation invalidates ScriptPulse.**

## Coverage Guarantee

**Every input line belongs to exactly one scene.**

No gaps, no overlaps.

## Implementation

See [segmenter.py](file:///Users/shameekyogi/Desktop/scriptpulse-antigravity/antigravity/agents/scene_segmentation/segmenter.py) for full implementation.

### Key Classes

- **`Scene`**: Data class representing a scene segment
- **`SceneSegmenter`**: Main segmentation engine with:
  - `_detect_boundaries()`: Initial boundary detection
  - `_calculate_boundary_confidence()`: Confidence scoring
  - `_create_scenes()`: Scene object creation
  - `_merge_micro_scenes()`: Minimum length enforcement
  - `_merge_low_confidence()`: Post-merge heuristics

### Configuration

```python
MIN_SCENE_LENGTH = 3  # Minimum lines per scene
LOW_CONFIDENCE_THRESHOLD = 0.5  # Threshold for warnings
MERGE_CONFIDENCE_THRESHOLD = 0.6  # Auto-merge below this
```

## Validation

All output must pass:

1. **Coverage validation**: All lines in exactly one scene
2. **Scene length validation**: No micro-scenes (< 3 lines)
3. **Confidence validation**: Scores in [0.0, 1.0]
4. **Conservative segmentation**: Not too many scenes
5. **Sequential indexing**: scene_index = 1, 2, 3, ...

### Running Validation

```bash
# Segment scenes
python antigravity/agents/scene_segmentation/segmenter.py \
  tests/fixtures/clean_script_sample.tags > scenes.json

# Validate output
python antigravity/agents/scene_segmentation/validator.py scenes.json
```

## Integration

**Upstream:** Structural Parsing Agent (4.1)  
**Downstream:** Structural Encoding Agent (4.3)

**Data flow:**
```
Tagged lines → Scene Segmentation → Scene boundaries → Structural Encoding
```

## Test Cases

Validated against:
- Clean professional scripts (stable boundaries)
- Messy early drafts (conservative, fewer scenes)
- Experimental scripts (ambiguity tolerated)

Test fixtures: `tests/fixtures/`

## Known Limitations

1. **Ambiguous headings**: Malformed scene headings may be missed or merged
2. **Non-standard formats**: Experimental structures may confuse boundary detection
3. **Very short scripts**: May produce single scene if structure is weak

**Mitigation:** Conservative merging ensures under-segmentation over over-segmentation.

## Compliance

**Design Philosophy:** ✅ Structure-only analysis  
**Truth Boundaries:** ✅ No narrative inference  
**Supervised Calibration:** ✅ Deterministic algorithm  
**Misuse Prevention:** ✅ No evaluation or ranking  

## References

- Core Spec: Section 8.2
- Antigravity Implementation Guide: Agent 4.2
- Test Cases: Scene Segmentation Behavior Suite
