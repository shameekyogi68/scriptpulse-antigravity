# ScriptPulse vNext.4 - Streamlit Deployment Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r scriptpulse/requirements.txt
```

### 2. Run the Frontend
```bash
streamlit run streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## Usage

1. **Paste Your Script:** Use the large text area to paste your screenplay draft. Formatting does not need to be perfect.

2. **Declare Intent (Optional):** If you have deliberately designed certain sections to create specific effects (e.g., "intentionally exhausting"), declare your intent using the checkbox and form below the script input.

3. **Click "Reflect":** The system will process your script and display experiential reflections.

---

## What You'll See

### Reflections
If the system detects persistent patterns in attentional demand, you'll see:
- **Scene ranges** where patterns were observed
- **Question-first reflections** describing possible first-time audience experience
- **Confidence levels** (high/medium/low)

### Silence
If no patterns are detected, you'll see an explanation of why. This does not indicate quality—it only means no persistent patterns surfaced.

### Intent Acknowledgments
If you declared writer intent, and patterns matched that intent, you'll see acknowledgments that the system respected your authority and suppressed corresponding alerts.

---

## Ethical Guarantees

The frontend strictly adheres to ScriptPulse vNext.4's ethical boundaries:
- ✅ No quality scores
- ✅ No rankings
- ✅ No advice or recommendations
- ✅ No visualizations (charts, graphs, timelines)
- ✅ Writer intent always overrides system observations

---

## Troubleshooting

**Port already in use:**
```bash
streamlit run streamlit_app.py --server.port 8502
```

**Import errors:**
Ensure you're running from the project root directory and that `PYTHONPATH` includes the current directory.
