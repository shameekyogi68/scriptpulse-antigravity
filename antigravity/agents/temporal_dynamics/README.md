# Temporal Dynamics Agent

**Agent ID:** 4.4  
**Pipeline Position:** Fourth-stage  
**Status:** ✅ Implemented

## Purpose

The Temporal Dynamics Agent models how attentional demand accumulates and recovers over time, transforming per-scene instantaneous effort into a time-evolving attentional signal.

This agent implements experiential modeling, NOT evaluation of pacing quality.

## Responsibility

> Transform per-scene feature vectors into a time-evolving attentional signal representing first-pass audience demand accumulation.

**Exclusive scope:** Temporal accumulation with fatigue carryover and recovery dynamics.

## Input Contract

**Input:**
- Encoded scene features (Vᵢ) from Structural Encoding Agent
- Scene sequence and count

## Output Contract

**Output:** JSON with temporal signals per scene

```json
{
  "temporal_signals": [
    {
      "scene_index": 1,
      "instantaneous_effort": 0.75,
      "attentional_signal": 0.75,
      "recovery_credit": 0.0,
      "fatigue_state": "normal"
    }
  ]
}
```

## Canonical Temporal Equation

```
S[0] = E[0]
S[i] = E[i] + λ·S[i-1] - R[i]  for i > 0
```

Where:
- **E[i]**: Instantaneous effort (from feature vector)
- **λ = 0.85**: Fatigue carryover (fixed)
- **S[i-1]**: Previous attentional signal
- **R[i]**: Recovery credit

## Model Components

### 1. Instantaneous Effort (E[i])

Computed from normalized features using fixed weights:

```
E[i] = 0.25·linguistic + 0.20·dialogue + 0.30·visual + 
       0.15·referential + 0.10·structural
```

Weights based on cognitive load research, not ML-learned.

### 2. Fatigue Carryover (λ)

**Fixed: λ = 0.85**

85% of previous load carries forward. Ensures persistence without accumulation.

**Opening Buffer** (first 10 scenes):
```
λ_effective = λ · min(1.0, scene_index / 10)
```

**Ending Buffer** (last 5% of scenes):
```
λ_effective = λ · (1 - 0.5 · proportional_reduction)
```

### 3. Recovery Credit (R[i])

Earned from:
- **Low-effort scenes**: `R += 0.3 · (0.4 - E[i])` when E < 0.4
- **Structural boundaries**: `R += 0.2 · event_boundary_score`
- **Compression**: `R += 0.1` for sparse/short scenes

Capped at R_max = 0.5

### 4. Nonlinear Fatigue Wall

When S > 2.0:
```
S = S + 0.05 · (S - 2.0)²
```

Models attentional collapse, not linear accumulation.

### 5. Fatigue State Classification

Descriptive (not evaluative):
- **normal**: S < 1.5
- **elevated**: 1.5 ≤ S < 2.0
- **high**: 2.0 ≤ S < 3.0
- **extreme**: S ≥ 3.0

## Implementation

See [temporal_engine.py](file:///Users/shameekyogi/Desktop/scriptpulse-antigravity/antigravity/agents/temporal_dynamics/temporal_engine.py)

### Key Classes

- **`TemporalSignal`**: Data class for scene temporal dynamics
- **`TemporalEngine`**: Main computation engine with:
  - Feature normalization (per-script)
  - Effort calculation
  - Recovery computation
  - Buffer-adjusted carryover
  - Fatigue wall application

## Non-Evaluative Framing

**CRITICAL:** S(t) does NOT evaluate pacing quality.

- High S(t) ≠ bad pacing
- Low S(t) ≠ good pacing
- S(t) = experiential demand only

All output is internal numeric values, never user-facing with evaluative language.

## Forbidden Techniques

❌ **Absolutely prohibited:**
- Judging pacing quality
- Inferring emotional response
- Escalating alerts
- Cross-script normalization
- Optimizing S(t)
- Using ML for parameters

## Validation

All output validated for:
- Bounded signals (no runaway)
- No single-scene dominance
- Determinism (no NaN/Inf)
- Proper buffer effects
- Recovery bounds

### Running Validation

```bash
# Compute temporal dynamics
python antigravity/agents/temporal_dynamics/temporal_engine.py \
  features.json > temporal.json

# Validate
python antigravity/agents/temporal_dynamics/validator.py temporal.json
```

## Integration

**Upstream:** Structural Encoding Agent (4.3)  
**Downstream:** Pattern Detection & Experience Translation (4.5+)

**Data flow:**
```
Feature vectors → Temporal Dynamics → Attentional signals → Pattern detection
```

## Example Output

Clean script (2 scenes):
- Scene 1: E=0.75, S=0.75, R=0.0, state=normal
- Scene 2: E=0.25, S=0.72, R=0.17, state=normal

Carryover: 0.85 × 0.75 = 0.64  
With effort: 0.25 + 0.64 = 0.89  
With recovery: 0.89 - 0.17 = 0.72

## Compliance

**Design Philosophy:** ✅ Experiential modeling only  
**Truth Boundaries:** ✅ No evaluation  
**Determinism:** ✅ Fixed parameters, reproducible  
**Stability:** ✅ Bounded accumulation  

## References

- Core Spec: Section 11
- Antigravity Implementation Guide: Agent 4.4
- Temporal Dynamics Schema
