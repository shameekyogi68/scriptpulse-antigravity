# ScriptPulse Executable Implementation

Runnable implementation of ScriptPulse vNext.4.

## Structure

```
scriptpulse/
├── agents/          # Seven agent modules
├── prompts/         # Prompt templates (TBD)
├── runner.py        # Pipeline executor
└── validate.py      # Sanity test harness
```

## Usage

Run the pipeline on a screenplay:

```bash
cd scriptpulse
python runner.py screenplay.txt
```

Run validation:

```bash
cd scriptpulse
python validate.py
```

## Status

- **E-1**: Scaffold complete (stubs only)
- **E-2**: TBD - StructuralParsingAgent implementation
- **E-3+**: TBD
