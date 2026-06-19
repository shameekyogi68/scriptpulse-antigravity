# ScriptPulse: AI Story Intelligence Engine
**Version:** v1.0 Production  
**Status:** Market Release  
**Engine:** Hybrid Cognitive Simulation + Optional Transformer NLP

---

## Overview
ScriptPulse is a professional-grade platform for analyzing screenplay narratives. Unlike formatting checkers, ScriptPulse simulates **first-pass reader cognitive load** and **attentional flow** — giving writers constructive, data-grounded signals to reflect on their drafts.

The system combines a **multi-agent architecture** with optional transformer models (Jina embeddings & DeBERTa zero-shot). When ML dependencies are unavailable, the same pipeline runs in **heuristic mode** with identical output structure.

---

## Key Capabilities

### 1. Attentional Dynamics Simulation
Models audience interest over time using:
- **Linguistic load**: syntactic complexity and idea density
- **Narrative momentum**: turn velocity and action density
- **Recovery potential**: genre-aware pacing resets

### 2. Narrative Feature Extraction
- Scene parsing and segmentation (INT./EXT. headings)
- Dialogue dynamics, stakes markers, and structural signals
- Optional transformer augmentation when ML stack is installed

### 3. Persona-Responsive Presentation
The dashboard adapts to three industry perspectives (presentation and report filtering):
- **Story Editor** — structure and narrative logic
- **Studio Executive** — commercial and production complexity signals
- **Script Coordinator** — craft, prose economy, and scene rhythm

Core analysis signals are consistent across perspectives.

### 4. Constructive, Non-Judgmental Guidance
ScriptPulse is a **reflection tool, not a gatekeeper**. All numeric indices are **reference signals** — not quality scores, rankings, or approval verdicts.

### 5. Professional Export Suite
- **Writer Report** — detailed markdown analysis
- **Studio Coverage** — HTML coverage-style memo
- **One-Page Summary** — printable overview

Every export includes mandatory truth-boundary disclaimers.

---

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Optional ML Stack (recommended for full precision)
```bash
pip install torch transformers sentence-transformers spacy
python -m spacy download en_core_web_sm
```

Set `SCRIPTPULSE_HEURISTICS_ONLY=1` to force heuristic mode.

### Environment Variables
Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
```

API keys are only required for optional AI coverage memos. Core analysis runs offline.

### Run the Dashboard
```bash
streamlit run streamlit_app.py
```

### CLI
```bash
PYTHONPATH=. python scriptpulse/pipeline/runner.py path/to/script.txt
```

---

## Repository Structure
- `scriptpulse/` — Core multi-agent engine
- `app/` — Streamlit dashboard
- `scripts/` — Automation and validation tools
- `docs/` — Theory, ethics, and validation
- `config/` — Model version pins and genre priors
- `tests/` — Unit, integration, and verification suites

---

## Truth Boundaries (Read Before Using Results)
ScriptPulse:
- **Does not** rank, grade, or approve scripts
- **Does not** predict commercial success
- **Does not** replace human coverage or writer judgment
- **Does** describe where a first-time reader may strain, drift, or recover

---

## Privacy
Scripts are processed in-memory during your session. ScriptPulse does not persist screenplay content to its own storage. When deployed on Streamlit Cloud or similar hosts, session data follows the host provider's policies.

## License
Proprietary. Confidentiality and Intellectual Property protections apply.  
© 2026 ScriptPulse. All rights reserved.
