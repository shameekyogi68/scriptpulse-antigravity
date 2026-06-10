# ScriptPulse — AI Architecture & Model Specifications

This document outlines the specific Artificial Intelligence models, Transformer architectures, and Large Language Models (LLMs) used within the ScriptPulse system to analyze screenplays and generate diagnostic reports.

---

## 1. Local Diagnostic Stack (Transformer Models)
These models run locally on the host machine to ensure privacy, reduce latency, and minimize API costs for granular structural analysis.

### A. **spaCy (Model: `en_core_web_sm`)**
*   **Role**: Linguistic Pre-processor.
*   **Why it's used**: 
    *   **Tokenization**: Breaks script text into words and sentences for statistical density analysis.
    *   **POS Tagging**: Identifies parts-of-speech (verbs, nouns) to detect passive voice and dialogue-to-action ratios.
    *   **Named Entity Recognition (NER)**: Identifies character names and locations to facilitate scene segmentation.

### B. **DeBERTa-v3 (Model: `DeBERTa-v3-xsmall-mnli-alnli`)**
*   **Role**: Zero-Shot NLU (Natural Language Understanding).
*   **Why it's used**: 
    *   **Thematic Labeling**: Categorizes the "Stakes" of scenes (e.g., Physical Survival vs. Social Status) without specific training on the script.
    *   **Sentiment Inference**: Detects emotional polarity in character exchanges to map the script's "Pulse" (emotional intensity).

### C. **Jina Embeddings v2 (Model: `jina-embeddings-v2-small-en`)**
*   **Role**: Semantic Vectorization.
*   **Why it's used**: 
    *   **Subtext Analysis**: Converts text into mathematical vectors to measure "Information Entropy" (how much new story value each page provides).
    *   **Repetition Detection**: Identifies circular or redundant pacing by comparing the semantic "meaning" of distant script segments.

---

## 2. Generative Reporting Stack (Large Language Models)
These models are accessed via external APIs to translate mathematical data into professional narrative feedback.

### D. **Gemini 1.5 Flash (Google)**
*   **Role**: Lead Persona Analyst.
*   **Why it's used**: 
    *   **Long-Context Reasoning**: Best-in-class at synthesizing 100+ pages of structural data into a cohesive story report.
    *   **Creative Translation**: Maps technical "math points" to human feelings like "Audience Boredom" or "Rising Tension."

### E. **Llama-3 via Groq (Models: `llama-3.3-70b`, `llama-3.1-8b`)**
*   **Role**: High-Speed Real-time Insights.
*   **Why it's used**: 
    *   **Inference Speed**: Groq's LPU (Language Processing Unit) architecture allows for near-instant "Visceral Reactions" in the UI.
    *   **Dashboard Logic**: Powers the quick-hit diagnostic insights for Pacing and Dialogue texture.

### F. **Hugging Face Inference (Model: `Kimi-K2-Instruct`)**
*   **Role**: Global Redundancy & Specialization.
*   **Why it's used**: 
    *   **Infrastructure Uptime**: Acts as a critical fallback if specialized hardware (Groq) or standard cloud providers (Google) experience downtime.

---

## 3. Core Frameworks
*   **Transformers (Hugging Face)**: The primary engine for loading and running DeBERTa and Jina.
*   **Sentence-Transformers (SBERT)**: Optimizes the Jina model for efficient scene-by-scene comparisons.
*   **PyTorch**: The underlying mathematical framework used to execute neural network calculations locally.
