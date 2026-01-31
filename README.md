# ScriptPulse vNext.5 (Antigravity)

**A deterministic, non-evaluative screenplay analysis engine modeling first-pass audience cognitive experience.**

---

## 🚀 Overview

ScriptPulse is a sophisticated tool designed to simulate the *cognitive load*, *fatigue*, and *attentional demand* experienced by a first-time viewer of a screenplay.

**It does NOT:**
*   Evaluate quality ("good/bad")
*   Infer semantic meaning or emotion
*   Offer suggestions or "fixes"
*   Judge writer intent

**It DOES:**
*   Track structural density and pacing
*   Model attentional resources over time
*   Detect persistent patterns (e.g., continuous strain, lack of recovery)
*   Reflect observations back to the writer using experiential, question-first language

---

## 🛠️ Installation

ScriptPulse is built with standard Python 3 libraries to ensure stability and reproducibility. No external heavy dependencies are required.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/scriptpulse-antigravity.git
    cd scriptpulse-antigravity
    ```

2.  **Verify environment:**
    ```bash
    python3 --version  # Requires Python 3.8+
    ```

3.  **Set PYTHONPATH (Runtime):**
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ```

---

## 🚦 Usage

### 1. Basic Execution (Pipeline)
The core runner processes a script string and returns a JSON report.

```python
from scriptpulse import runner

# Load your screenplay
with open("my_script.txt", "r") as f:
    script_text = f.read()

# Run the pipeline
report = runner.run_pipeline(script_text)

# View results
print(report['mediated_output'])
```

### 2. With Writer Intent (Authority)
You can explicitly declare intent for specific scene ranges. The system will **suppress** alerts that match your intent, honoring your authority.

```python
intent = [
    {
        'scene_range': [10, 20], 
        'intent': 'intentionally exhausting'
    }
]

report = runner.run_pipeline(script_text, writer_intent=intent)
```

### 3. Running Validation
To verify system integrity and determinism:
```bash
python3 final_validation.py
```

---

## 🧩 System Architecture (The "Antigravity" Pipeline)

The system operates as a linear, deterministic pipeline of 7 specialized agents:

1.  **Structural Parsing (E-1):** Classifies lines by format (Scene, Action, Dialogue) – *No semantics.*
2.  **Scene Segmentation (E-2):** Groups lines into scenes using conservative boundaries.
3.  **Structural Encoding (E-3):** Converts scenes into numerical feature vectors based on observable data (counts, lengths).
4.  **Temporal Dynamics (E-4):** Models fatigue `S(t)` using the canonical equation: `S_i = E_i + λ*S_{i-1} - R_i`.
5.  **Pattern Detection (E-5):** Identifies persistent multi-scene trends (e.g., "sustained demand").
6.  **Intent Immunity (E-6):** Checks patterns against writer intent; suppresses matches.
7.  **Experience Mediation (E-7):** Translates raw patterns into writer-safe, question-based reflections (e.g., "The audience may feel tired here. Is that intended?").

---

## ⚖️ Ethical Safeguards

This system adheres to strict ethical boundaries defined in `docs/ScriptPulse_Misuse_Prevention_and_Ethics.md`.

*   **No Evaluation:** Words like "good", "bad", "fix", "improve" are hard-banned.
*   **Writer Authority:** Writer declarations override system signals 100% of the time.
*   **Determinism:** Identical inputs yield identical outputs.
*   **Misuse Resistance:** The system refuses to rank scripts or offer comparative scores.

---

## 📂 Project Structure

*   `scriptpulse/` - Core source code
    *   `agents/` - Individual agent implementations
    *   `runner.py` - Pipeline orchestrator
*   `tests/` - Unit tests for each agent
*   `docs/` - Authoritative specifications and contracts
*   `final_validation.py` - End-to-end system verification script

---

*Verified Compliance Audit: 2026-01-25*
