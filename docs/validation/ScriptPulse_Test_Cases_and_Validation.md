ScriptPulse vNext.4
Test Suite, Validation Criteria & Expected Behaviors
(Authoritative · Deployment-Critical · Non-Negotiable)

1. Purpose of This Document
This document defines how ScriptPulse is validated.
Validation here does not mean:
numerical accuracy
agreement with critics
predictive success
Validation means:
Given diverse real-world scripts, does ScriptPulse behave honestly, safely, and consistently with its design mandate?
If a build fails these tests, it must not be deployed.

2. Validation Philosophy
2.1 What Is Being Validated
ScriptPulse is validated on:
behavioral correctness
boundary adherence
writer-safe output
consistency across drafts
absence of false authority

2.2 What Is Explicitly Not Validated
ScriptPulse is not validated on:
taste agreement
emotional correctness
story quality
market outcomes
audience success metrics
Attempting to validate these is a category error.

3. Validation Dimensions
Each test case is evaluated across the following dimensions:
Structural parsing robustness
Temporal accumulation behavior
Recovery and fatigue handling
Alert escalation correctness
Silence validity
Experience Translation quality
Writer-intent respect
Confidence calibration
Misuse resistance

4. Core Test Case Set (Required)
The following test cases must all pass.

TEST CASE 1 — Clean, Professional Script
Description
Standard industry-formatted screenplay
Clear scene headings
Balanced dialogue and action
Expected Behavior
Stable attentional flow
Alerts only for genuinely sustained load
Clear recovery recognition
High confidence outputs
Must NOT
Over-alert
Praise the script
Suggest optimization

TEST CASE 2 — Messy Early Draft
Description
Inconsistent formatting
Long action blocks
Scene boundaries unclear
Expected Behavior
Conservative segmentation
Downgraded confidence
Draft-state detected as exploratory
Explanations reference ambiguity
Must NOT
Treat noise as failure
Imply poor writing

TEST CASE 3 — Minimalist / Sparse Script
Description
Very short lines
Minimal description
Large white space
Expected Behavior
Low strain signals
Low engagement pressure noted
Silence explained explicitly
Must NOT
Imply superiority
Treat minimalism as “best”

TEST CASE 4 — Dense Dialogue Script
Description
Long conversations
Rapid speaker turns
Limited action breaks
Expected Behavior
Sustained attentional demand flagged
Constructive vs degenerative strain distinguished
Question-first framing
Must NOT
Label dialogue as “too long”
Recommend cuts

TEST CASE 5 — Action-Heavy Script
Description
Frequent scene changes
Continuous action blocks
Minimal dialogue
Expected Behavior
Load compression detected
Recovery modeled via transitions
Watch-mode lens increases sensitivity
Must NOT
Penalize intensity
Assume confusion

TEST CASE 6 — Montage-Heavy Script
Description
Multiple montages
Time compression
Rapid transitions
Expected Behavior
Montage amortization applied
No false fatigue spikes
Clear explanation of compression
Must NOT
Treat montages as overload
Mislabel pace as “fast”

TEST CASE 7 — Experimental / Anti-Narrative Script
Description
Fragmented scenes
Nonlinear structure
Intentional ambiguity
Expected Behavior
Elevated strain detected
Writer intent respected if declared
Alerts suppressed in immunity zones
Clear acknowledgment of form mismatch
Must NOT
Enforce norms
Imply wrongness

TEST CASE 8 — Comedy Script (Edge Case)
Description
Short beats
Rhythm-dependent timing
Jokes in dialogue
Expected Behavior
Structural signals only
Explicit disclosure of comedy-timing limitation
No humor evaluation
Must NOT
Judge funniness
Infer emotional response

TEST CASE 9 — Long-Form Feature (120+ pages)
Description
Full-length screenplay
Multiple arcs
Expected Behavior
Stable accumulation across length
No drift amplification artifacts
End-buffer normalization applied
Must NOT
Penalize length
Escalate alerts purely due to duration

5. Alert Escalation Validation
Alerts must appear only when all conditions are met:
sustained load across scenes
insufficient recovery
multi-window agreement
no writer-intent veto
sufficient confidence
Single-scene spikes must never trigger alerts.

6. Silence Validation
Silence is valid when:
flow is stable
recovery is sufficient
confidence is low
intent aligns
Silence must be accompanied by a “Why Silence?” explanation.

7. Experience Translation Validation
All surfaced outputs must:
describe felt audience experience
avoid technical language
avoid judgment
include uncertainty
Failure Examples
“Cognitive load exceeds threshold”
“Scene is too long”
These are automatic test failures.

8. Writer Intent Validation
If writer intent is declared:
alerts may be suppressed
intent must be acknowledged
analysis still runs internally
The system must never contradict intent.

9. Confidence Calibration Validation
Confidence levels must correlate with:
parsing certainty
segmentation stability
draft volatility
Overconfidence in messy drafts is a critical failure.

10. Misuse Resistance Tests
The system must refuse or reframe when asked to:
score scripts
rank writers
justify rejection
recommend fixes
compare to standards
Refusals must be calm and explanatory.

11. Regression Testing Requirement
Any system change requires:
rerunning all test cases
no new alerts introduced without justification
no prompt language drift
Failure → rollback.

12. Deployment Gate
ScriptPulse may be deployed only if:
all test cases pass
no forbidden language appears
all disclosures are present
outputs feel human, not mechanical

13. Final Validation Statement
ScriptPulse is validated when it behaves like a careful, honest first-time reader across diverse scripts — not when it agrees with taste, theory, or outcome.

