# ScriptPulse Professional Adoption & Onboarding Guide
## vNext.5 Product Layer Specification

This document defines the **Product Layer** mechanics required to ensure ScriptPulse is trusted, understood, and used correctly by professional screenwriters. Unlike the Core Logic users, the Product Layer deals with **perception, framing, and strict boundaries**.

---

### 1. The Core Paradox
ScriptPulse is **non-evaluative** (it effectively "feels" the script without judging it). However, professionals are conditioned to expect judgment (notes, scores, fixes).

**The Soltuion:** We must **train perception** through onboarding and UI constraints.

---

### 2. Mandatory First-Run Orientation
Every user interface must present this specific framing **before** the first analysis:

> "ScriptPulse does not tell you what works.
> It shows where first-pass attention may strain — or doesn’t.
> It acts as a Reader Surrogate, not a Critic."

**Rules:**
*   ❌ No "Bad Writing" examples.
*   ❌ No "Score" promises.
*   ✅ Explicit permission for output to be **Silent**.

---

### 3. Trust-Preserving UI Mechanics

#### 3.1 Silence Visibility (The "Earned Silence" Display)
Silence is not an empty state. It is a positive signal of stability.
if the `SSF` agent returns `is_silent: True`, the UI **MUST**:
1.  **Hide all low-confidence alerts.**
2.  **Display the Silence Explanation** prominently.
    *   *Example:* "Across this draft, the audience experience remains relatively stable, with natural effort and recovery balancing out."
3.  **Avoid generic "No Errors Found" text**, which implies a test was passed. Use "Experience Stable" instead.

#### 3.2 Alert Scarcity
*   **Visual Rule:** Alerts should be rare.
*   **Mechanism:** Only `surfaced_patterns` from the `Mediation` layer should be shown. Never show raw `patterns` that were suppressed.
*   **Confidence as Tone:**
    *   High Confidence -> "Attention is likely straining..."
    *   Medium Confidence -> "Attention may begin to wander..."
    *   **NEVER** display: "78% Confidence", "Strain Level 5".

---

### 4. Misuse Prevention (Gatekeeping)

ScriptPulse is designed for **Writer Reflection**, not **Industrial Filtering**.

#### 4.1 The "No-Comparison" Rule
The UI must **NOT** provide tools to:
*   Compare Script A vs Script B side-by-side.
*   Rank scripts by "Efficiency" or "Strain".
*   Generate a single "Quality Score".

#### 4.2 Explicit Refusal
If a user attempts to use the tool for "Coverage Scoring" or "Hiring Filtering", the documentation must explicitly state:

> "SYSTEM LIMITATION: This tool models subjective first-pass attention for a single specific draft. It does not measure market value, structural competency, or narrative quality. Using it to rank scripts is statistically invalid."

---

### 5. Professional Positioning (The "Pitch")

**"The only tool that models what it feels like to encounter your script for the first time — without telling you what to do about it."**

*   **We don't fix.** (We reflect).
*   **We don't judge.** (We simulate).
*   **We don't know better.** (You do).

---

### 6. Implementation Checklist for UIs
- [ ] Onboarding disclaimer visible?
- [ ] "Score" visualizations removed?
- [ ] Silence creates a specific "Stable" UI state?
- [ ] Comparative dashboards disabled/absent?
- [ ] "How this works" link points to IEEE Validation logic?
