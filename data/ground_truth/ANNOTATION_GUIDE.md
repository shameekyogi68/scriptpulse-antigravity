# Annotation Guide for ScriptPulse Ground Truth Corpus

## Purpose
This guide defines the protocol for human annotation of screenplay scenes, creating ground truth data for validating ScriptPulse's cognitive load and tension models.

## Annotation Task
For each scene in a screenplay, rate the following on a 1-5 Likert scale:

### Effort Rating (1-5)
*"How much mental effort does this scene demand from the reader?"*

| Rating | Label | Description |
|---|---|---|
| 1 | Effortless | Simple, clear, easy to follow |
| 2 | Light | Mostly straightforward, minor complexity |
| 3 | Moderate | Some tracking needed (characters, plot threads) |
| 4 | Demanding | Dense with information, multiple story elements |
| 5 | Exhausting | Overwhelming complexity, hard to process |

### Tension Rating (1-5)
*"How much dramatic tension or suspense does this scene create?"*

| Rating | Label | Description |
|---|---|---|
| 1 | Calm | No tension, peaceful or expository |
| 2 | Mild | Slight unease or anticipation |
| 3 | Moderate | Clear stakes or conflict present |
| 4 | High | Strong conflict, uncertainty about outcome |
| 5 | Extreme | Peak crisis, maximum suspense |

## Annotation Procedure
1. Read the entire screenplay first (for context)
2. Re-read scene-by-scene, assigning ratings
3. Do NOT re-read previous ratings until finished
4. Mark any scenes where you are uncertain (add a `?` flag)

## CSV Format
```csv
script_id,scene_index,rater_id,effort_rating,tension_rating
script_001,0,rater_a,3,2
script_001,1,rater_a,4,4
script_001,0,rater_b,2,2
```

## Inter-Rater Reliability Target
- **Krippendorff's α ≥ 0.7** (Acceptable agreement)
- If α < 0.5, re-train raters with calibration examples

## Recommended Script Sources (Public Domain / Open License)
1. BBC Writers' Room scripts (public access)
2. Nicholl Fellowship finalist scripts (often shared)
3. IMSDB.com (Internet Movie Script Database)
4. SimplyScripts.com (public domain screenplays)

## Minimum Corpus Size
- **Development Set**: 20 scripts × ~15 scenes each = ~300 annotations
- **Holdout Set**: 10 scripts (annotated separately, not seen during development)
- **Raters**: Minimum 3 per script for inter-rater reliability

## Pre-Aggregated Format
For single-rater or pre-averaged ground truth:
```csv
script_id,scene_index,human_effort_mean,human_tension_mean,human_satisfaction_mean
script_001,0,2.5,2.0,0
script_001,1,4.0,4.0,0
```
