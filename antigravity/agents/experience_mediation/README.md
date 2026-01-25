# Audience-Experience Mediation Agent

**Agent ID:** 4.7  
**Pipeline Position:** Final-stage (writer-facing)  
**Status:** ✅ Implemented

## Purpose

Translate internal signals into **writer-safe, experiential language** without judgment, prescription, or authority.

**If this agent fails, the entire system fails.**

## Core Rules

### 1. Question-First Framing
All output must be questions, never declarative statements.

### 2. Experiential Translation
| Pattern | Translation |
|---------|------------|
| sustained_demand | "The audience may feel mentally tired here." |
| limited_recovery | "There's little chance to catch their breath." |
| surprise_cluster | "The shifts may feel sudden." |

### 3. Uncertainty Required
- High confidence → "may"
- Medium → "might"
- Low → "could"

### 4. Silence Handling
If no patterns, explain why (never imply approval).

### 5. Intent Acknowledgment
When patterns suppressed by intent, acknowledge alignment.

## Forbidden Language

❌ good/bad, improve/fix, too long/short, problem/issue, should/must

## Usage

```bash
python antigravity/agents/experience_mediation/mediator.py filtered.json
```
