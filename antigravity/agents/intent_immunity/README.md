# Writer Intent & Immunity Agent

**Agent ID:** 4.6  
**Pipeline Position:** Sixth-stage  
**Status:** ✅ Implemented

## Purpose

Apply writer-declared intent to control alert surfacing **without altering analysis**.

This is the **primary safety gate** enforcing writer authority.

## Responsibility

> Apply writer-declared intent and Creative Immunity to downstream alert eligibility without altering analysis.

## Core Principles

### 1. Absolute Writer Authority
Writer intent ALWAYS overrides alerts. No exceptions.

### 2. Never Infer Intent
Only explicit declarations count. Never guess intent.

### 3. Suppression ≠ Analysis Alteration
Suppressed patterns remain in internal state. Analysis is never deleted.

## Allowed Intent Labels

1. `intentionally_exhausting` — Writer wants high demand
2. `intentionally_confusing` — Writer wants disorientation
3. `should_feel_smooth` — Writer expects low strain
4. `should_feel_tense` — Writer expects elevated demand
5. `experimental_anti_narrative` — Writer rejects convention

## Intent Annotation Format

```json
{
  "intent_annotations": [
    {
      "scene_range": [15, 45],
      "intent_label": "intentionally_exhausting",
      "writer_note": "Act 2 should push readers"
    }
  ]
}
```

## Output Format

```json
{
  "surfaced_patterns": [...],
  "suppressed_patterns": [
    {
      "pattern_type": "sustained_demand",
      "scene_range": [20, 40],
      "suppressed_reason": "writer_intent",
      "intent_reference": {"label": "intentionally_exhausting", "scene_range": [15, 45]},
      "alignment_note": "Writer marked scenes 15-45 as intentionally exhausting...",
      "internal_analysis_preserved": true
    }
  ]
}
```

## Forbidden Techniques

❌ Suppress without intent  
❌ Infer intent  
❌ Question writer intent  
❌ Alter analysis  
❌ Create new labels  

## Usage

```bash
python antigravity/agents/intent_immunity/intent_processor.py patterns.json intent.json
```

If no intent file provided, all patterns surface unchanged.
