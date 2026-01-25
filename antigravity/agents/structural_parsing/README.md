# Structural Parsing Agent

**Agent ID:** 4.1  
**Pipeline Position:** First-stage ingestion  
**Status:** ✅ Implemented

## Purpose

The Structural Parsing Agent performs **format-only classification** of screenplay lines into structural categories.

This agent is the entry point to the ScriptPulse pipeline and establishes the foundational constraint: **no semantic inference**.

## Responsibility

> Classify each line of a screenplay into structural format categories only.

**Exclusive scope:** Line-level format tagging based on layout cues.

## Input Contract

**Input:** Raw screenplay text (plain text, unprocessed)

**Format assumptions:**
- May have inconsistent formatting
- Early drafts are allowed
- No guarantees of industry-standard layout
- UTF-8 encoding

## Output Contract

**Output:** Line-aligned sequence of tags

Each line receives exactly one tag:

| Tag | Category | Description |
|-----|----------|-------------|
| `S` | Scene Heading | Sluglines (INT./EXT., locations) |
| `A` | Action | Stage directions, descriptions |
| `D` | Dialogue | Character speech |
| `C` | Character | Character name cue |
| `M` | Metadata | Transitions, notes, parentheticals |

**Format rules:**
- One tag per input line
- No additional text
- No confidence scores
- No explanations

## Classification Methodology

### Allowed Techniques

The agent may use **only** these formatting cues:

1. **Capitalization patterns**
   - All-caps for scene headings
   - All-caps for character names
   - Mixed case for dialogue and action

2. **Indentation**
   - Left-aligned: scene headings, action
   - Center-aligned: character names
   - Indented: dialogue

3. **Punctuation**
   - Periods in sluglines (e.g., "INT.")
   - Colons in transitions (e.g., "FADE TO:")
   - Parentheses for parentheticals

4. **Structural markers**
   - INT./EXT. indicators
   - FADE, CUT TO, etc.
   - Time-of-day markers (DAY, NIGHT)

### Forbidden Techniques

**The following are absolutely prohibited:**

- ❌ Semantic embeddings
- ❌ Word meaning analysis
- ❌ Sentiment or emotion detection
- ❌ Dialogue quality assessment
- ❌ Character relationship inference
- ❌ Story structure interpretation
- ❌ Any NLP features derived from **meaning**

**Violation of these constraints invalidates ScriptPulse.**

## Ambiguity Handling

When formatting is ambiguous:

1. Choose the **most conservative** structural label
2. Default preferences:
   - Unclear prose → `A` (Action)
   - Unclear formatting elements → `M` (Metadata)
3. Document ambiguous cases for review (but still output a tag)

## Validation

All output must pass:

1. **Format validation**
   - Exact line count match
   - Only valid tags (S, A, D, C, M)
   - No prose or explanations

2. **Determinism check**
   - Same input → same output
   - Repeatable across runs

3. **Boundary compliance**
   - No semantic features detected
   - Format-only classification verified

### Running Validation

```bash
# Validate tagged output
python antigravity/agents/structural_parsing/validator.py screenplay.txt

# Expected: screenplay.tags file in same directory
```

## Integration

**Upstream:** None (first agent in pipeline)  
**Downstream:** Scene Segmentation Agent (4.2)

**Data flow:**
```
Raw screenplay → Structural Parsing → Tagged lines → Scene Segmentation
```

## Test Cases

Validated against:
- Clean professional scripts (>95% accuracy)
- Messy early drafts (conservative tagging)
- Experimental formatting (no hallucination)

Test fixtures: `tests/fixtures/`

## Compliance

**Design Philosophy:** ✅ Format-only analysis  
**Truth Boundaries:** ✅ No semantic inference  
**Supervised Calibration:** ✅ Frozen model at runtime  
**Misuse Prevention:** ✅ No evaluation or ranking  

## Known Limitations

1. Non-standard screenplay formats may produce ambiguous tags
2. Heavily reformatted scripts may confuse layout detection
3. Mixed formatting styles within a script reduce reliability

**Mitigation:** Conservative tagging + downstream validation

## References

- Core Spec: Section 8.1
- Antigravity Implementation Guide: Agent 4.1
- Test Cases: Structural Parsing Robustness Suite
