# 🚀 ScriptPulse Deployment Checklist

## ✅ PRE-DEPLOYMENT VERIFICATION (Complete)

### Repository Structure
- [x] `streamlit_app.py` at root level
- [x] `requirements.txt` at root level  
- [x] `scriptpulse/` package with all agents
- [x] `scriptpulse/runner.py` with relative imports
- [x] All files committed and pushed to GitHub

### Requirements
- [x] `requirements.txt` contains only: `streamlit>=1.32`
- [x] No unnecessary dependencies
- [x] File is at repo root (not inside scriptpulse/)

### Import Verification
- [x] `from scriptpulse import runner` works
- [x] Runner imports agents using relative syntax
- [x] No hardcoded paths
- [x] No local-only dependencies

### Code Quality
- [x] Streamlit app tested locally
- [x] No evaluative language in UI
- [x] Silence handling implemented
- [x] Misuse resistance active
- [x] All ethical boundaries enforced

---

## 🎯 DEPLOYMENT STEPS (Follow in Order)

### Step 1: GitHub Verification
1. Go to: https://github.com/shameekyogi68/scriptpulse-antigravity
2. Confirm these files are visible:
   - `streamlit_app.py`
   - `requirements.txt`
   - `scriptpulse/` folder
   - `README.md`

### Step 2: Streamlit Cloud Setup
1. Go to: https://share.streamlit.io
2. Click **"Sign in"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your repositories

### Step 3: Deploy App
1. Click **"New app"** (top right)
2. Fill deployment form:
   - **Repository:** `shameekyogi68/scriptpulse-antigravity`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
3. Click **"Deploy!"**

### Step 4: Wait for Build
- First build takes 2-5 minutes
- Watch build logs for errors
- Common first-time issues are listed below

### Step 5: Test Deployed App
Once live, test:
- [ ] App loads without errors
- [ ] Can paste screenplay
- [ ] "Read My Draft" button works
- [ ] Reflections appear correctly
- [ ] Silence explanation shows when appropriate
- [ ] Intent declaration works
- [ ] Misuse guards trigger properly ("Is this good?" → boundary message)

---

## ⚠️ COMMON DEPLOYMENT ISSUES & FIXES

### Error: "No module named 'scriptpulse'"
**Fix:** Check that `scriptpulse/__init__.py` exists and is committed.

### Error: "No module named 'streamlit'"
**Fix:** Verify `requirements.txt` is at repo root and contains `streamlit>=1.32`.

### App loads but shows blank page
**Fix:** Check Streamlit Cloud logs for Python errors. Most likely an import issue.

### Error: "Cannot import name 'runner'"
**Fix:** Verify `scriptpulse/runner.py` uses relative imports: `from .agents import ...`

---

## 📍 YOUR APP URL (After Successful Deploy)

Your app will be available at:
```
https://scriptpulse-antigravity-[random-id].streamlit.app
```

You can customize this URL in Streamlit Cloud settings.

---

## 🔄 UPDATING THE DEPLOYED APP

To push updates:
```bash
git add .
git commit -m "feat: update UI copy"
git push
```

Streamlit Cloud will auto-detect and redeploy (takes ~30 seconds).

---

## 🔐 OPTIONAL: Make App Private

If you want to restrict access:
1. Go to: https://share.streamlit.io
2. Click on your app
3. Settings → Sharing
4. Choose:
   - **"Only specific people"** → Enter email addresses
   - **"Anyone with the link"** (default, public)

---

## ✅ FINAL VALIDATION

Before sharing publicly, confirm:
- [ ] No advice or prescriptive language appears
- [ ] "Is this good?" triggers boundary message (not analysis)
- [ ] Empty input shows gentle guidance
- [ ] Silence is explained clearly
- [ ] Intent suppression works correctly
- [ ] Same input produces same output
- [ ] No charts, graphs, or visualizations
- [ ] UI feels calm and non-judgmental

---

**Status:** Ready for Deployment ✅  
**Next Action:** Follow Step 1 above
