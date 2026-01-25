# Structural Encoding Agent

**Agent ID:** 4.3  
**Pipeline Position:** Third-stage  
**Status:** ✅ Implemented

## Purpose

The Structural Encoding Agent converts scenes into **interpretable structural feature vectors** using only observable metrics.

This agent provides quantified structural analysis without semantic inference, evaluation, or quality judgment.

## Responsibility

> Convert each scene into an observable, interpretable structural feature vector (Vᵢ).

**Exclusive scope:** Observable feature extraction from structural tags and text patterns.

## Input Contract

**Input:**
- Scene boundaries from Scene Segmentation Agent
- Line-level tags (S, A, D, C, M)
- Original screenplay text

## Output Contract

**Output:** JSON with feature vectors per scene

```json
{
  "encoded_scenes": [
    {
      "scene_index": 1,
      "features": {
        "linguistic_load": {...},
        "dialogue_dynamics": {...},
        "visual_abstraction": {...},
        "referential_memory": {...},
        "structural_change": {...}
      }
    }
  ]
}
```

## Feature Groups

### 1. Linguistic Processing Load

Measures sentence complexity and variation:
- `sentence_count`: Total sentences (period-delimited)
- `mean_sentence_length`: Average words/sentence
- `max_sentence_length`: Longest sentence
- `sentence_length_variance`: Length variance

**Observable:** Sentence boundaries, word counts

### 2. Dialogue Dynamics

Measures dialogue pacing and turn-taking:
- `dialogue_turns`: Count of D tags
- `speaker_switches`: C tag changes
- `turn_velocity`: Turns per estimated page
- `max_monologue_run`: Longest uninterrupted speech

**Observable:** Tag sequences, character transitions

### 3. Visual Abstraction Load

Measures action description density:
- `action_line_count`: Count of A tags
- `continuous_action_runs`: Consecutive A tag sequences
- `fg_bg_action_ratio`: Short vs long action blocks
- `visual_density`: Action lines / total lines
- `vertical_writing_load`: Max consecutive A block height

**Observable:** Tag counts, line lengths, block patterns

### 4. Referential Working-Memory Load

Measures character tracking complexity:
- `active_character_count`: Unique C tags in scene
- `character_reintroductions`: Characters not seen in previous 2 scenes
- `pronoun_density`: Pronouns / total words

**Observable:** Character tags, pronoun counts

### 5. Structural Change

Measures scene-to-scene structural shift:
- `event_boundary_score`: Euclidean distance Δ(Vᵢ, Vᵢ₋₁)

**Observable:** Vector distance calculation

## Interpretability Principle

**Every feature must be explainable as "something a careful human could point to on the page."**

If a feature cannot be described in observable terms, it does not exist in this agent.

## Forbidden Techniques

❌ **Absolutely prohibited:**
- Semantic embeddings or word vectors
- Sentiment/emotion analysis
- Topic modeling
- Importance weighting
- Thematic classification
- Quality/clarity metrics
- Cross-script normalization
- Learned/ML-derived features
- Meaning or intent inference

## Normalization Constraint

**Critical:** Features normalize **within the same script only**.

No cross-script comparison or global baselines allowed.

## Implementation

See [encoder.py](file:///Users/shameekyogi/Desktop/scriptpulse-antigravity/antigravity/agents/structural_encoding/encoder.py)

### Key Classes

- **`SceneFeatures`**: Complete feature vector for a scene
- **`StructuralEncoder`**: Main encoding engine with extractors for each feature group

### Feature Extractors

- `_extract_linguistic_load()`: Sentence analysis
- `_extract_dialogue_dynamics()`: Turn-taking patterns  
- `_extract_visual_abstraction()`: Action density
- `_extract_referential_memory()`: Character tracking
- `_calculate_event_boundary()`: Scene delta

## Validation

All output validated for:
- Complete feature structure
- Valid numeric values (no NaN/infinite)
- Interpretability constraints
- No semantic feature leakage
- First scene boundary = 0.0

### Running Validation

```bash
# Encode screenplay
python antigravity/agents/structural_encoding/encoder.py \
  screenplay.txt tags.txt scenes.json > features.json

# Validate
python antigravity/agents/structural_encoding/validator.py features.json
```

## Integration

**Upstream:** Scene Segmentation Agent (4.2)  
**Downstream:** Temporal Dynamics Agent (4.4)

**Data flow:**
```
Scene boundaries + Tags → Structural Encoding → Feature vectors → Temporal Dynamics
```

## Example Output

Clean script (2 scenes):
- Scene 1: 24 sentences, 7 dialogue turns, 27 action lines, 3 characters
- Scene 2: 6 sentences, 3 turns, 11 action lines, event_boundary = 30.36

## Compliance

**Design Philosophy:** ✅ Observable features only  
**Truth Boundaries:** ✅ No semantic inference  
**Feature Governance:** ✅ Interpretable, auditable  
**Normalization:** ✅ Per-script only  

## References

- Core Spec: Section 9
- Antigravity Implementation Guide: Agent 4.3
- Feature Governance: Interpretability Requirements
