# ScriptPulse: Research Methodology & System Architecture
**Version 15.0 - MCA Defensible Architecture (Consolidated Pipelines)**

## 1. Abstract
ScriptPulse is a **computational narrative analysis system** designed to simulate the **cognitive experience** of a human reader. The core research focuses on a **Temporal Dynamics Model** that process a screenplay linearly, scene-by-scene, to calculate **Attentional Signal**—a measure of reader engagement, fatigue, and interest.

---

## 2. Theoretical Framework: The Cognitive Simulation
The system is built on **Information Theory** and **Linguistic Analysis**. It rests on three core pillars:
1.  **Parsing (Structural)**: Converting unstructured screenplay text into a predictable data stream (JSON).
2.  **Perception (Senses)**: Extracting linguistic features (Entropy, Complexity, Syntax) that affect mental processing time.
3.  **Dynamics (Simulation)**: Using a mathematical **First-Order Autoregressive Process** to model how attention accumulates and decays over time.

---

## 3. System Architecture: The 3-Stage Pipeline
The system is designed as a linear pipeline, ensuring high reliability and modularity.

### Stage 1: The Perception Engine (`perception_agent.py`)
This stage extracts the "Vital Signs" of every scene. It focus on 5 core pillars:
*   **Linguistic Load**: Measures sentence length variance (using **Standard Deviation**) to estimate syntactic complexity.
*   **Dialogue Rhythm**: Calculates "Turn Velocity" (Interactions per scene) to estimate conversational tempo.
*   **Visual Intensity**: Monitors action-to-dialogue ratios to determine "Cinematic Weight."
*   **Referential Load**: Tracks character introductions and "Character Churn" to measure cognitive tracking effort.
*   **Information Entropy**: Uses **Shannon’s Entropy** (Word-Frequency Distribution) to measure narrative novelty and surprise.

### Stage 2: The Dynamics Engine (`dynamics_agent.py`)
The heart of the research. It takes the "Signals" from Stage 1 and runs a **Temporal Simulation**.

**The Core Equation:**
The system calculates the **Attentional Signal ($S$)** at time $t$ using:
$$S_t = E_t + (\lambda \cdot S_{t-1}) - R_t$$

*   **Effort ($E_t$)**: The sum of Complexity, Rhythm, and Intensity (Mental Work).
*   **Decay rate ($\lambda$)**: The "Memory Factor"—how much interest $S$ carries over from the previous scene.
*   **Recovery ($R_t$)**: The "Breather"—how much mental energy is restored during quiet or transitional scenes.

### Stage 3: The Interpretation Agent (`interpretation_agent.py`)
Translates the mathematical signals into **Natural Language Feedback**. It maps the trajectory into recognized acts (Act 1, Act 2, Act 3) and identifies structurally significant moments (Inciting Incident, Midpoint, Climax).

---

## 4. Key Algorithms
*   **SHANNON ENTROPY**: Used to quantify how much information and surprise is packed into the dialogue.
*   **AUTOREGRESSION (AR-1)**: Predicts the next state of attention based on current input and past history.

---

## 5. Defense Summary (For Viva)
*   **Innovation**: Instead of just "summarizing" text like ChatGPT, ScriptPulse analyzes the **Structural Pulse**—the pacing and rhythm that makes a script "filmable."
*   **Explainability**: Every diagnosis is backed by data. If the system says "Scene 10 is slow," it provides the **Turn Velocity** and **Action Density** as evidence.
