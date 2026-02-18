# ScriptPulse Ground Truth Dataset Specification (v1.0)

## Overview
This dataset represents human emotional and cognitive reactions to screenplay scenes. It is used to validate the ScriptPulse `DynamicsAgent` and `ExperimentalAgent`.

**Status**: MOCK DATA (Simulated for Pipeline Validation)

## Schema
File: `data/ground_truth/mock_human_ratings_multi_rater.csv`

| Column | Type | Description | Range |
|---|---|---|---|
| `script_id` | String | Unique identifier for the script | n/a |
| `scene_index` | Integer | 1-based index of the scene | 1+ |
| `reader_id` | String | Unique identifier for the human rater | n/a |
| `effort_rating` | Float | Perceived cognitive effort to read | 0.0 (Easy) - 1.0 (Hard) |
| `tension_rating` | Float | Perceived narrative tension/suspense | 0.0 (Bored) - 1.0 (Edge of Seat) |

## Aggregation Logic
For system alignment:
*   **Mean**: Average of all `reader_id` ratings for a given scene.
*   **Std Dev**: Standard deviation representing subjective variance.

## (Planned) Recruitment Protocol
*   **Target N**: 30 unique readers per script.
*   **Demographics**:
    *   50% "General Audience" (Reads <5 scripts/year)
    *   30% "Industry Readers" (Reads >50 scripts/year)
    *   20% "Genre Fans" (Self-identified affinity for script genre)
*   **Conditions**:
    *   Read in one sitting.
    *   Rate after every scene (pop-up modal).
