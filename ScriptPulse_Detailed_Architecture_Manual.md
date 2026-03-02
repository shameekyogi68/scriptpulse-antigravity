# ScriptPulse: Exhaustive System Architecture Manual

*A complete, step-by-step technical decomposition of the ScriptPulse cognitive simulation pipeline (v14.0).*

---

## Introduction

ScriptPulse is a multi-agent architectural framework designed to simulate the cognitive load ("attentional demand") a human reader experiences when reading a screenplay. It operates deterministically, processing plain text or XML (FDX) inputs through a series of specialized agents to quantify structural effort, semantic density, and emotional engagement. The final output is a JSON payload of mathematically derived "experiences," not subjective evaluations of quality.

This document traces the exact execution path of ScriptPulse, from the moment a script is ingested to the final construction of the JSON report. It covers every formula, normalization step, and variable mutation exactly as implemented in the source code.

---

## Phase 1: Ingestion and Orchestration (`runner.py`)

The pipeline execution begins in `scriptpulse.pipeline.runner.py` via the `run_pipeline()` function.

### 1.1 Input Normalization & Security
When a script is passed to `run_pipeline(script_content, ...)`, two immediate steps occur:
1.  **Governance Check**: The script passes through `validate_request()`. If an `ImportError` occurs (e.g., in a local test environment without the governance module), it silently falls back and continues.
2.  **Normalization**: `normalizer.normalize_script(script_content)` converts the text into a unified format, handling character encodings and line breaks.

### 1.2 Agent Instantiation (The Cache)
To optimize performance, ScriptPulse uses a module-level singleton cache (`_AGENT_CACHE`). Agents are instantiated only on their first call and reused.
*   **Structure Agents**: `ParsingAgent`, `SegmentationAgent`, `BeatAgent`
*   **Perception Agents**: `EncodingAgent`, `SemanticAgent`, `ImageryAgent`, `SocialAgent`, `SyntaxAgent`, `VoiceAgent`, `ValenceAgent`, `CoherenceAgent`
*   **Dynamics & Interpretation**: `DynamicsAgent`, `InterpretationAgent`, `EthicsAgent`

---

## Phase 2: Structural Parsing & Segmentation (`structure_agent.py`)

Before cognitive analysis begins, the raw text must be converted into structured data.

### 2.1 Parsing Line by Line (`ParsingAgent`)
The `ParsingAgent.run()` method splits the normalized text by newline (`\n`). It cleans em-dashes (`—` to `-`) and iterates through every line, passing it to `predict_line()`.

Each line is assigned a specific tag:
*   `S` : Scene Heading
*   `A` : Action
*   `C` : Character Name
*   `D` : Dialogue
*   `T` : Transition
*   `M` : Metadata / Parenthetical

**The Parsing Heuristic Chain:**
1.  **Scene Headings**: Evaluated by `is_scene_heading()`. It checks if the line starts with standard prefixes (`INT.`, `EXT.`, `I/E.`, `SCENE`) or matches regex patterns for time-of-day suffixes (`[A-Z\s]+ - DAY`). If true, it returns `S`.
2.  **Transitions/Metadata**: If the line ends with `TO:` or matches standard transition strings (`FADE IN`, `CUT TO`), it returns `T` or `M`.
3.  **Contextual Dialogue**: If the *previous* line tag was `C` (Character), the current line is evaluated. If it starts with `(`, it's tagged `M` (Parenthetical), otherwise `D` (Dialogue).
4.  **Character Names**: If the line is entirely uppercase, less than 40 characters, does not end with punctuation (`.?!`), and the *next* line is *not* uppercase, it is tagged `C`.
5.  **Fallback**: Anything failing these conditions defaults to `A` (Action).

*Output Variable*: `parsed` (List of dictionaries: `[{'line_index': int, 'text': str, 'tag': str, 'confidence': float}]`).

### 2.2 Scene Segmentation (`SegmentationAgent`)
With lines tagged, `SegmentationAgent.run(parsed)` groups them into discrete scenes.

1.  **Boundary Detection (`detect_boundaries`)**: Iterates through `parsed`. If a line is tagged `S` (Scene), it assigns a boundary confidence of `0.9`. If `M` (Transition), confidence is `0.4`. It records the `line_index` of all boundaries with confidence > 0.3.
2.  **Scene Creation (`create_scenes`)**: Slices the `parsed` list between the detected boundaries to create initial scene blocks.
3.  **Minimum Length Enforcement (`enforce_minimum_length`)**: Scans scenes. If a scene's length (`end_line - start_line + 1`) is less than `MIN_SCENE_LENGTH` (3 lines), it merges that scene with the *next* scene, taking the minimum `boundary_confidence` of the two.
4.  **Headless Fragment Merge (`merge_headless_fragments`)**: Looks for scenes that do *not* contain an `S` tag. If a headless scene is ≤ 5 lines (`max_orphan_lines`), it is appended to the *previous* scene.
5.  **Low Confidence Merge (`merge_low_confidence`)**: If a scene's boundary confidence is below `LOW_CONFIDENCE_THRESHOLD` (0.6), it is merged forward into the next scene.
6.  **Extraction & Hydration**: Finally, it extracts the actual `S` text to use as the `heading`, grabs the first two non-heading lines as a `preview`, and hydrates the scene object with the actual line dictionaries (`scene['lines']`).

*Output Variable*: `segmented` (List of scene dicts).

---

## Phase 3: Perceptual Encoding (`perception_agent.py`)

The `EncodingAgent.run()` method analyzes every scene in `segmented` to extract mathematical features (`feature_vectors`).

### 3.1 Linguistic Load (`extract_linguistic_load`)
Concatenates all text in the scene. Splits into sentences by punctuation (`.!?`).
*   **Flesch-Kincaid Grade (`readability_grade`)**:
    $$ \text{FK} = 0.39 \times \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) + 11.8 \times \left(\frac{\text{Total Syllables}}{\text{Total Words}}\right) - 15.59 $$
    *(Clamped to a minimum of 0.0)*
*   **Idea Density (`idea_density`)**: Acts as a proxy for propositional density.
    $$ \text{Density} = \frac{\text{Unique Words} + \text{Preposition Count}}{\text{Total Words}} $$
*   **Novelty Score**: `idea_density * (sentence_length_variance / 10.0)`

### 3.2 Dialogue Dynamics (`extract_dialogue_dynamics`)
Counts lines tagged `D` and `C`.
*   **Speaker Switches**: Iterates through `C` lines; increments if $C_i \neq C_{i-1}$.
*   **Turn Velocity =** $\frac{\text{Dialogue Count}}{\text{Total Scene Lines}}$
*   **Monologue Runs**: Contiguous blocks where $C_i = C_{i-1}$.

### 3.3 Visual Abstraction (`extract_visual_abstraction`)
Counts lines tagged `A`.
*   **Continuous Runs**: Number of unbroken blocks of `A` tags without intervening dialogue.

### 3.4 Referential Load & Entity Churn (`extract_referential_load`)
Tracks the cognitive burden of remembering "who is doing what."
*   **Active Characters**: Cardinality of the unique set of text from `C` tags.
*   **Entity Churn**: Compares current scene characters against `prev_characters` (from the previous scene loop).
    $$ \text{Churn} = \frac{\text{Added} + \text{Removed}}{\text{Total Unique Characters across both scenes}} $$
*   **Unresolved References (Ghost Mentions)**: Tracks uppercase words (length > 2) in Action/Dialogue that do *not* match the active character set.

### 3.5 Structural Change (`extract_structural_change`)
*   **Event Boundary Score**: $\frac{\text{Current Start Line} - \text{Previous End Line}}{\text{Total Lines in Script}} \times 100$. (A normalized distance metric).

### 3.6 Ambient Signals (`extract_ambient_signals`)
Calculates a weighted stillness modifier:
$$ \text{Ambient Score} = 0.35 \times (\text{Stillness}) + 0.30 \times (\text{Sparse Dialogue}) + 0.20 \times (\text{Low Complexity}) + 0.15 \times (\text{Short Sentences}) $$

### 3.7 Masterclass Extractions (Phases 23-30)
The encoding agent applies dozens of specialized heuristic scans:
*   **On The Nose (`extract_on_the_nose`)**: Ratio of dialogue containing literal emotional phrases (e.g., "I feel", "I am angry", "I want to").
*   **Shoe Leather (`extract_shoe_leather`)**: Checks the first 3 and last 3 dialogue lines for filler words ("hello", "goodbye", "okay").
*   **Stichomythia (`extract_stichomythia`)**: Flags `True` if there are $\ge 4$ consecutive dialogue exchanges of $\le$ 6 words each.
*   **Payoff Density (`extract_payoff_density`)**: Ratio of lines containing high-impact valence/action words ("blood", "truth", "love") to total lines.

*Output Variable*: `encoded` (List of dense feature dictionaries, one per scene).

---

## Phase 4: Temporal Dynamics Simulation (`dynamics_agent.py`)

This is the core mathematical engine. The `DynamicsAgent.run_simulation()` models how a human brain fatigues over time based on the sequence of scenes.

### 4.1 Configuration and Reader Profile
ScriptPulse loads a `ReaderProfile` based on the specified `genre` (e.g., Drama, Thriller). This defines parameters:
*   `lambda_base` (Fatigue Carryover/Decay): Usually ~0.85. Higher tolerance = slower decay.
*   `beta_recovery` (Recovery Capability): Usually ~0.3.
*   `fatigue_threshold`: Usually 1.0.

### 4.2 Instantaneous Effort Calculation ($E_i$) (Per Scene Loop)
For every scene $i$, it calculates the raw cognitive energy required to read it.

1.  **Density Normalization**: "Long but simple scenes still trigger overload flags." It fixes this by calculating a `density_factor`.
    $$ \text{Density Factor} = 0.5 + (\frac{\text{Entropy}}{6.0}) $$
2.  **Cognitive Load**:
    $$ \text{CogLoad} = ( \text{StructLoad} \times 0.6 ) + ( \text{SemanticLoad} \times 0.2 ) + ( \text{SyntacticLoad} \times 0.2 ) $$
3.  **Emotional Load** (Scaled by Density):
    $$ \text{EmoLoad} = ( \text{DialogueEng} \times 0.35 ) + ( \text{VisualInt} \times \text{Density} \times 0.30 ) + ( \text{LingVol} \times \text{Density} \times 0.20 ) - ( \text{Stillness} \times 0.15 ) $$
    *(Clamped between 0.0 and 1.0)*
4.  **Confusion Penalty**:
    $$ \text{Penalty} = (\text{Entity Churn} \times 0.2) + (\text{Ghost Mentions} \times 0.1) + (\text{Coherence Score} \times 0.15) $$
5.  **Base Effort** ($E_i$):
    $$ E_i = ( \text{CogLoad} \times 0.55 ) + ( \text{EmoLoad} \times 0.45 ) + \text{Penalty} $$

### 4.3 Scene Type & Adaptive Decay Modifier ($\lambda_{mod}$)
The algorithm shifts the decay rate based on the *type* of scene:
*   If `Action Lines` > `Dialogue Lines` $\times 1.5$: It is an **Action** scene. $\lambda_{mod} = -0.05$ (Faster decay; action requires constant stimulation to sustain attention).
*   If `Dialogue Lines` > `Action Lines` $\times 2.0$: It is a **Dialogue** scene. $\lambda_{mod} = +0.05$ (Slower decay; thread tracking sustains attention longer).

### 4.4 Recovery Calculation ($R_i$)
Recovery happens when the instantaneous effort ($E_i$) falls below a maximum recovery threshold (`R_MAX`, default 0.5).
$$ R_i = \max(0, (\text{R\_MAX} - E_i)) \times \text{beta\_rec} \times \text{TAM\_Rec\_Mod} $$

### 4.5 The Canonical Attentional Signal State Update ($S_i$)
This autoregressive equation tracks accumulating fatigue. The signal for scene $i$ relies on the signal from the previous scene ($S_{i-1}$).

$$ \lambda_{current} = \max(0.1, \min(0.99, \lambda_{base} + \lambda_{mod})) $$
$$ S_i = E_i + (\lambda_{current} \times S_{i-1}) - R_i $$
*(Clamped between 0.0 and 1.0)*

### 4.6 Long Range Fatigue (LRF) Update
After generating the `temporal_signals` list, `apply_long_range_fatigue()` runs.
If a reader is subjected to high effort ($E_i \ge 0.4$) for multiple consecutive scenes, "latent fatigue" accumulates in a separate `fatigue_reserve`.
If recovery $R_i > 0.3$, this reserve "discharges" back into the main signal $S_i$, causing a delayed spike in stress.
If consecutive high-effort scenes exceed `SUSTAINED_ONSET` (3 scenes), a `sustained_penalty` is applied to $S_i$, simulating the reader "tuning out."

*Output Variable*: `temporal_output` (List of dictionaries detailing $E_i$, $S_i$, $R_i$, and trace metrics for every scene).

---

## Phase 5: Pattern Detection & Intent Immunity (`dynamics_agent.py` & `interpretation_agent.py`)

### 5.1 Detecting Experiential Patterns
`DynamicsAgent.detect_patterns()` scans the `temporal_output` arrays for persistent shapes (requiring a minimum of 3 consecutive scenes).
*   **Sustained Attentional Demand**: Triggered if $S_i > 0.6$ continuously.
*   **Limited Recovery**: Triggered if $R_i < 0.05$ continuously.
*   **Repetition**: Triggered if the variance of $E_i$ is very low (< 0.1) across the window.
*   **Constructive Strain**: Triggered if $E_i$ is rising steadily while $S_i$ remains manageable.

### 5.2 Writer Intent Immunity
`InterpretationAgent.apply_writer_intent()` intersects detected patterns with user-defined tags (e.g., `<intent: intentionally exhausting>`).
If a "Sustained Demand" pattern overlaps fully with an "intentionally exhausting" intent range, the pattern is moved from `surfaced_patterns` to `suppressed_patterns`. The mathematical fatigue is preserved, but the system will not issue an alert.

---

## Phase 6: Mediation and Output Construction (`runner.py` & `interpretation_agent.py`)

ScriptPulse fundamentally refuses to use evaluative logic. It translates pure mathematical shapes into non-judgmental "experience" labels.

### 6.1 Semantic Labeling
`InterpretationAgent.apply_semantic_labels()` maps the $S_i$ and $E_i$ coordinates to creative labels:
*   High Strain ($S > 0.75$) + High Effort ($E > 0.6$) $\rightarrow$ **"Action Climax / Intense Conflict"**
*   High Strain ($S > 0.75$) + Low Effort ($E \le 0.6$) $\rightarrow$ **"Suspenseful Build-Up"**
*   Low Strain ($S < 0.35$) + High Effort ($E > 0.6$) $\rightarrow$ **"Dense Exposition / World-Building"**
*   Low Strain ($S < 0.35$) + Low Effort ($E \le 0.6$) $\rightarrow$ **"Quiet Reflection / Breathing Room"**

### 6.2 The Final JSON Assembly
Back in `runner.py`, all outputs from the various agents are aggregated into a massive `final_output` dictionary.

1.  **`meta`**: Injects `run_id`, `version`, `content_fingerprint`, and exact `agent_timings`.
2.  **`scene_info`**: Lightweight mapping of `scene_index`, `heading`, and `preview`.
3.  **`temporal_trace`**: The complete array of $S_i$, $E_i$, $R_i$, expectation strains, and writer analytics (conflict, stakes, agency) per scene.
4.  **`semantic_beats`**: The translated creative labels from 6.1.
5.  **`narrative_intelligence`**: Warnings, such as "Dropped Threads" (items mentioned early but never again) or "Thematic Drift".
6.  **`conflict_typology`**: Broad classification of whether scenes lean External, Social, or Internal.
7.  **`interaction_networks`**: Graph logic of which characters generate the highest `social_score` tension together.

Finally, `runner.py` executes `json.dumps(result, indent=2)` and prints the exhaustive mathematical portrait of the reading experience to stdout.

---

## Phase 7: The Brutal Truth — Utility for the Writer

Let’s be ruthlessly honest: **This is a mathematical mirror, not a creative oracle.** 

If a writer receives this JSON output and expects it to tell them if their script is "good" or "bad," they will be violently disappointed. The tool cannot evaluate subtext, heart, thematic resonance, or the quality of a joke. It is fundamentally blind to art.

However, as a **structural diagnostic tool**, the output is lethal if the writer knows how to read it. Here is exactly what a writer can *actually do* with this data:

### 1. Identify Unintentional Flatlines (The "Boring" Risk)
Writers often think a scene is gripping because it’s gripping in their head. If the `temporal_trace` shows a $S_i$ (Strain) score flatlining below 0.3 for 10 scenes, and `dominant_driver` flags `low_engagement`, the tool is stating a mathematical fact: *Nothing structurally taxing is happening.* The writer can use this to ask: "Did I intend for this 15-page stretch to be a complete breather, or did I accidentally put the audience to sleep?"

### 2. Spot Premature Climax Exhaustion
If the `pattern` array flags `sustained_attentional_demand` around Scene 20 (out of 100), the reader is exhausted in Act 1. The writer doesn't need to rewrite the plot; they need to inject a scene with high $R_i$ (Recovery)—a joke (detected via `extract_humor_signal`), a quiet visual beat, or a simple transition—to reset the reader's brain before hitting them again.

### 3. Diagnose "Talky" Scenes (The "Shoe Leather" Risk)
If a scene has high `shoe_leather` metrics (too many "hellos" and "goodbyes"), the writer can literally just cut the first 3 and last 3 lines of dialogue in that scene. The tool provides the exact scene index. This is a direct, executable architectural fix.

### 4. Catch "On-The-Nose" Dialogue Blind Spots
When writers are rushing, they use literal dialogue ("I'm so angry at you!"). The `extract_on_the_nose` ratio flags these scenes. The writer can go to that specific scene, look at the Dialogue (`D`) tags, and rewrite the emotion into an Action (`A`) kinetic verb, instantly elevating the subtext. 

### 5. Validate Intended Pacing (The Master Map)
The greatest utility is simply looking at the line graph of $S_i$ across all scenes. 
*   Does it look like a staircase culminating at the end? (Good for Thrillers).
*   Does it look like a rollercoaster with deep valleys? (Good for Comedy).
*   Does it look like a brick wall? (The writer is overwhelming the reader). 

---

## Phase 8: The Immediate User Experience (How to use it)

Where does all this math actually go, and what does the writer physically look at?

ScriptPulse does not force writers to read raw JSON. The JSON output (`final_output`) is injested by a **Streamlit Web Application** (`streamlit_app.py`) which translates the data into a premium, writer-centric visual dashboard.

Here is the exact journey of a writer using the tool:

### 1. The Experience Timeline (The "Master Map")
The first thing the writer sees is the **Experience Timeline**. This is a smooth, color-coded line graph (rendered via Plotly) representing the $S_i$ (Attentional Strain) curve across the entire script. 
*   **What they do:** The writer looks at this graph to instantly verify if the emotional shape of the script matches their intent. If they wrote a slow-burn thriller but the line spikes in Scene 3 and flatlines, they instantly know their pacing is structurally broken.
*   **How it helps:** It prevents "writer blindness." You can't argue with the math of sentence length and entity churn. The visual graph proves pacing without bias.

### 2. The Core Insights Panel (The "Warnings")
Beneath the graph, the UI parses the `system_patterns` array from the JSON and displays them as plain-English alert cards.
*   **What they do:** The writer reads translated warnings like: *"Sustained Demand detected (Scenes 40-45). Dominant Driver: Syntactic Load."* 
*   **How it helps:** Because the tool surfaces the `dominant_driver`, the writer isn't just told "it's too dense." They are told *why*. If the driver is "Syntactic Load," they know to go chop up their long sentences. If it's "Entity Churn," they know to remove a few minor characters from that sequence. 

### 3. Scene-by-Scene X-Ray 
The UI features a sidebar where the writer can click on any individual Scene. 
*   **What they do:** When clicked, the UI opens a detailed breakdown of that specific scene. This displays the raw metrics: `story_leather`, `on_the_nose` ratios, and `dialogue_velocity`. 
*   **How it helps:** This is where the surgical rewriting happens. If the UI flags Scene 12 for high `shoe_leather` (meaningless filler like "hello/goodbye"), the writer mechanically deletes those specific filler lines from their screenplay software.

### 4. The System Limitations Disclaimer
At the bottom of the dashboard, the UI renders the `SYSTEM_LIMITATIONS` array from the JSON `meta` block. 
*   **What they do:** The writer is forced to acknowledge that the system only models a "first-time read" and cannot judge humor quality or subtext.
*   **How it helps:** It builds trust. By admitting what it *cannot* do, the writer is more likely to trust the structural math that it *can* do.

**Conclusion:** ScriptPulse is a structural Geiger counter delivered through a beautiful dashboard. It clicks when the cognitive radiation gets too high or drops too low. It is up to the writer to open their Final Draft file and decide if that radiation is coming from a brilliant climax or a broken scene.
