ScriptPulse vNext.4
Output Semantics & Visual Language Contract
(Authoritative · Writer-First · Non-Negotiable)

1. Purpose of This Document
This document defines what ScriptPulse is allowed to show writers and how it must be shown.
It exists because:
correct analysis can still harm writers if visualized poorly
dashboards and scores create false authority
writers respond to experience, not analytics
If any output or UI element violates this contract, the system is invalid, even if the underlying analysis is correct.

2. Core Output Principle
ScriptPulse visualizes audience experience, not script properties.
The UI must answer:
“How might this feel to experience for the first time?”
It must never answer:
“How good is this script?”

3. Global Output Rules (Hard Constraints)
All outputs must obey:
No scores
No rankings
No optimization cues
No comparative baselines
No red/green success signals
No raw metrics
No genre or structural norms
Violation of any rule breaks writer trust.

4. Primary Visual: Experience Timeline
4.1 What It Is
A single horizontal timeline spanning the script from start to end.
It represents:
First-pass audience attention demand over time
4.2 What It Shows
gentle rises and falls
sustained stretches of demand
recovery valleys
4.3 What It Never Shows
numbers
percentages
thresholds
“good/bad” zones
4.4 Allowed Label
“Audience attention demand over first exposure”

5. Sustained Demand Highlighting
5.1 Visual Form
soft translucent bands spanning ranges, not points
never sharp spikes or warning icons
5.2 Meaning
“This stretch asks the audience to stay highly attentive for a while.”
5.3 Forbidden Interpretation
Must never imply:
problem
flaw
mistake
This is descriptive, not evaluative.

6. Breath & Recovery Markers
6.1 Visual Form
valleys
spacing
subtle icons suggesting pause or breath
6.2 Meaning
“The audience has a moment to catch their breath here.”
This reframes pacing as physiological, not mechanical.

7. Scene Cards (Expandable, Optional)
Each scene or scene cluster may expand into a card, not a table.
7.1 Card Contents
scene number or range
one short experiential sentence
optional confidence note
7.2 Example
“Dense dialogue and limited pause here may feel tiring if experienced in one sitting.”
7.3 Forbidden Content
word counts
ratios
formulas
directives (“consider cutting”)

8. “Why Silence?” Panel (Mandatory)
When no alerts appear, the UI must explain why.
8.1 Acceptable Explanations
“Attentional flow appears stable with regular recovery.”
“Signals are low confidence due to draft variability.”
“Patterns align with your declared intent.”
8.2 Forbidden Implications
Silence must never imply:
approval
success
quality
readiness
Silence is information, not praise.

9. Confidence Indicators (Soft Only)
9.1 Allowed Forms
“High confidence”
“Moderate confidence”
“Low confidence”
With a short explanation.
9.2 Forbidden Forms
percentages
accuracy scores
probabilities
Uncertainty must feel honest, not scientific theater.

10. Writer Intent Visibility
When intent is declared:
show intent label unobtrusively
acknowledge alignment explicitly in outputs
Example
“You marked this section as intentionally exhausting. Signals align with that intent.”
The UI must never contradict intent.

11. Reader-Mode Switching (Optional View)
The UI may allow switching between:
Read
Narrate
Watch
Rules
same underlying signal S(t)
only weights differ
no new interpretation
This reinforces that ScriptPulse models experience context, not story meaning.

12. Visual Elements Explicitly Forbidden
The UI must never include:
charts with axes labeled “better/worse”
leaderboards
comparative histograms
act markers (25%, 50%, 75%)
genre overlays
emotional labels
heatmaps implying danger or failure
These convert description into evaluation.

13. Accessibility & Cognitive Load
The UI must:
be readable at a glance
avoid clutter
present one idea at a time
allow writers to disengage easily
Over-dense UI recreates the problem ScriptPulse is meant to study.

14. The Final UI Test
Before approving any UI element, ask:
“Does this invite reflection — or optimization?”
If it invites optimization:
remove it
simplify it
or explain it differently

15. Lock Statement
ScriptPulse’s UI is not an analytics dashboard.
It is a mirror of first-audience experience.
Any visual that:
pressures,
scores,
compares,
or judges
…violates this contract.

