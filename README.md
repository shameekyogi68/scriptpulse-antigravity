# ScriptPulse: AI Story Intelligence Engine
**Version:** v1.0 Production  
**Status:** Market Release  
**Engine:** Hybrid Cognitive Simulation + Transformer NLP

---

## 🎯 Overview
ScriptPulse is a professional-grade AI platform for analyzing screenplay narratives. Unlike traditional tools that focus on formatting, ScriptPulse simulates **Reader Cognitive Load** and **Emotional Resonance** — providing writers with constructive, guided insights to strengthen their scripts.

By combining a **Multi-Agent Architecture** with modern Transformers (Jina-v2 & DeBERTa-v3), the system tracks how an audience's attention peaks, valleys, and fatigues over the course of a screenplay.

---

## 🚀 Key Capabilities

### 1. Attentional Dynamics Simulation
The core engine utilizes a linear dynamical system to model audience interest based on:
*   **Linguistic Load**: Syntactic complexity and idea density.
*   **Narrative Momentum**: Turn velocity and action density.
*   **Recovery Potential**: Genre-specific breathers and pacing resets.

### 2. Transformer-Augmented Perception
*   **8k Context Horizon**: Powered by `Jina-v2-small`, the system perceives entire scenes without truncation.
*   **Zero-Shot Emotional Mapping**: `DeBERTa-v3` categorizes conflict, stakes, and sentiment with precision.

### 3. Persona-Responsive Intelligence
The UI adapts automatically to three industry personas:
*   🕵️ **Story Editor**: Structural integrity and narrative logic.
*   🏢 **Studio Executive**: Commercial viability and production risk.
*   ✍️ **Script Coordinator**: Prose economy and craft precision.

### 4. Constructive Guidance
Every insight is framed as a growth opportunity — never harsh, never discouraging. ScriptPulse is a mentor, not a gatekeeper.

### 5. Professional Export Suite
*   📄 **Writer Report** — Detailed markdown analysis
*   🎬 **Studio Coverage** — Professional HTML coverage memo
*   🖨️ **One-Page Summary** — Printable overview

---

## 📊 Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
```

### Run the Dashboard
```bash
streamlit run streamlit_app.py
```

---

## 📂 Repository Structure
*   `scriptpulse/` — **Core Engine.** Multi-agent narrative simulation logic.
*   `app/` — **View Layer.** Streamlit dashboard components and assets.
*   `scripts/` — **Workbench.** Automation and research tools.
*   `docs/` — **Knowledge Base.** Theory, validation, and guides.
*   `config/` — **Environment.** Model version pins and genre priors.
*   `tests/` — **Quality Assurance.** Regression and unit test suites.

---

## 🔒 Privacy
Scripts are processed in-memory only and are **never stored** on any server.

## 🛡️ License
Proprietary. Confidentiality and Intellectual Property protections apply.  
© 2026 ScriptPulse. All rights reserved.
