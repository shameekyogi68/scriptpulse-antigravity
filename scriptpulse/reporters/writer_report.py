"""
ScriptPulse Writer Report Generator
====================================
Converts the full writer_intelligence output into a clean, human-readable
Markdown report styled to match the dark cinematic obsidian theme.

Usage:
    from scriptpulse.reporters.writer_report import generate_writer_report
    md = generate_writer_report(pipeline_output, title="MY SCRIPT")
    with open("my_script_report.md", "w") as f:
        f.write(md)
"""

import re
import statistics as _stats
from datetime import datetime
from scriptpulse.disclaimers import (
    FULL_DISCLAIMER_MARKDOWN,
    engagement_signal_label,
    get_engine_mode_note,
)

# ---------------------------------------------------------------------------
# Genre benchmark table for all core signals
# ---------------------------------------------------------------------------
GENRE_BENCHMARKS = {
    'drama':    {'conflict': (0.35, 0.70), 'energy': (0.40, 0.75), 'entropy': (0.30, 0.60), 'payoff_density': (0.25, 0.65)},
    'thriller': {'conflict': (0.55, 0.85), 'energy': (0.55, 0.85), 'entropy': (0.40, 0.75), 'payoff_density': (0.45, 0.80)},
    'comedy':   {'conflict': (0.20, 0.55), 'energy': (0.35, 0.70), 'entropy': (0.25, 0.55), 'payoff_density': (0.20, 0.55)},
    'horror':   {'conflict': (0.50, 0.85), 'energy': (0.45, 0.80), 'entropy': (0.45, 0.80), 'payoff_density': (0.40, 0.80)},
    'action':   {'conflict': (0.60, 0.90), 'energy': (0.60, 0.90), 'entropy': (0.40, 0.75), 'payoff_density': (0.45, 0.85)},
    'romance':  {'conflict': (0.20, 0.55), 'energy': (0.30, 0.65), 'entropy': (0.20, 0.50), 'payoff_density': (0.20, 0.55)},
    'sci-fi':   {'conflict': (0.40, 0.80), 'energy': (0.45, 0.80), 'entropy': (0.45, 0.80), 'payoff_density': (0.35, 0.75)},
    'avant-garde': {'conflict': (0.10, 0.90), 'energy': (0.10, 0.90), 'entropy': (0.60, 0.95), 'payoff_density': (0.10, 0.90)},
    'crime drama': {'conflict': (0.45, 0.80), 'energy': (0.45, 0.80), 'entropy': (0.35, 0.70), 'payoff_density': (0.35, 0.75)},
    'feature':  {'conflict': (0.35, 0.75), 'energy': (0.40, 0.75), 'entropy': (0.30, 0.65), 'payoff_density': (0.30, 0.70)},
    'general':  {'conflict': (0.30, 0.75), 'energy': (0.35, 0.75), 'entropy': (0.30, 0.70), 'payoff_density': (0.25, 0.70)},
}

def _benchmark_tag(value, genre, signal):
    """Return a tag string showing value vs genre benchmark."""
    benchmarks = GENRE_BENCHMARKS.get(genre.lower(), GENRE_BENCHMARKS['general'])
    if signal not in benchmarks:
        return f"{value:.2f}"
    
    low, high = benchmarks[signal]
    
    if value < low:
        return f"🔴 **{value:.2f}** *(below {genre} target: {low:.2f}-{high:.2f})*"
    elif value > high:
        return f"🟡 **{value:.2f}** *(above {genre} target: {low:.2f}-{high:.2f})*"
    else:
        return f"🟢 **{value:.2f}** *(on target: {low:.2f}-{high:.2f} for {genre})*"

def _stars(value, max_val=1.0, n=5):
    """Return a visual star bar for a 0..max_val value."""
    filled = round((value / max_val) * n)
    filled = max(0, min(n, filled))
    return "★" * filled + "☆" * (n - filled)

def _genre_key(genre):
    key = (genre or "general").lower().replace("_", "-")
    return {
        "sci fi": "sci-fi",
        "science fiction": "sci-fi",
        "crime-thriller": "thriller",
        "avant garde": "avant-garde",
    }.get(key, key)

def _format_markdown_card(text):
    """Formats a diagnostic item into a styled HTML card for Markdown rendering."""
    clean_text = text
    for emoji in ['🔴', '🚫', '🟠', '⚠️', '🟡', '✂️', '⬜', '🟢', '✅', '💎', '⭐', '🔵']:
        clean_text = clean_text.replace(emoji, '')
    clean_text = clean_text.strip()
    
    # Determine severity
    if any(x in text for x in ['🔴', 'CRITICAL', '🚫']):
        color = '#D92987' # Rose-Crimson
        bg = 'rgba(217, 41, 135, 0.04)'
        border = 'rgba(217, 41, 135, 0.2)'
        label = 'CRITICAL'
    elif any(x in text for x in ['🟠', 'WARNING', '⚠️', '🟡', '✂️', '⬜', '🔵']):
        color = '#F57946' # Warm Amber
        bg = 'rgba(245, 121, 70, 0.04)'
        border = 'rgba(245, 121, 70, 0.2)'
        label = 'WARNING'
    elif any(x in text for x in ['✨', '🟢', '✅', '💎', '⭐']):
        color = '#00D2A0' # Mint Green
        bg = 'rgba(0, 210, 160, 0.04)'
        border = 'rgba(0, 210, 160, 0.2)'
        label = 'HEALTHY'
    else:
        color = '#9B51E0' # Amethyst Purple
        bg = 'rgba(155, 81, 224, 0.04)'
        border = 'rgba(155, 81, 224, 0.2)'
        label = 'INFO'
        
    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
    text_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_html)
    
    parts = text_html.split(':', 1)
    if len(parts) == 2:
        title = f"<b style='color:white;font-size:0.95rem;display:block;margin-bottom:4px;'>{parts[0].strip()}</b>"
        body = parts[1].strip()
    else:
        title = ""
        body = text_html
        
    return f"""
<div style="background:{bg}; border:1px solid {border}; border-left:4px solid {color}; border-radius:8px; padding:16px 20px; margin-bottom:12px; font-family:'Inter',sans-serif; color:#F4F6FB;">
    <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:0.7rem; font-weight:700; color:{color}; letter-spacing:0.08em; text-transform:uppercase;">
        <span>🩺 Health Alert</span>
        <span>{label}</span>
    </div>
    {title}{body}
</div>
"""

def _format_provocation_card(text):
    """Formats a provocation card."""
    clean_text = text.replace('💡', '').strip()
    text_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
    
    return f"""
<div style="background:rgba(142,197,233,0.04); border:1px solid rgba(142,197,233,0.2); border-left:4px solid #8EC5E9; border-radius:8px; padding:16px 20px; margin-bottom:12px; font-family:'Inter',sans-serif; color:#F4F6FB; font-style:italic;">
    <div style="font-size:0.7rem; font-weight:700; color:#8EC5E9; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:6px; font-style:normal;">💡 Creative Inquiry</div>
    "{text_html}"
</div>
"""

def generate_writer_report(pipeline_output, title="Untitled Script", genre=None):
    """
    Generate a complete, premium styled Markdown writer's report.
    """
    wi = pipeline_output.get('writer_intelligence', {})
    trace = pipeline_output.get('temporal_trace', [])
    genre = _genre_key(genre or wi.get('genre_context', 'general'))
    dashboard = wi.get('structural_dashboard', {})
    diagnosis = wi.get('narrative_diagnosis', [])
    priorities = wi.get('rewrite_priorities', [])
    summary_data = wi.get('narrative_summary', {})
    features = pipeline_output.get('perceptual_features', [])

    lines = []

    # -------------------------------------------------------------------------
    # PREMIUM HEADER (Styled HTML Box)
    # -------------------------------------------------------------------------
    analysis_date = pipeline_output.get('meta', {}).get('timestamp')
    if not analysis_date:
        analysis_date = datetime.now().strftime('%B %d, %Y (%H:%M)')
        
    header_html = f"""
<div style="background:#1E1E1E; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:28px; font-family:'Inter',sans-serif; color:#E0E0E0; box-shadow:0 8px 32px rgba(0,0,0,0.4); margin-bottom:24px; position:relative; overflow:hidden;">
    <div style="position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg, #9B51E0, #A56DFF, #FF3366);"></div>
    <h1 style="font-family:'Outfit',sans-serif; font-size:2.2rem; font-weight:800; margin:0 0 12px 0; color:white; letter-spacing:-0.03em; border:none; padding:0;">🖋️ Script<span style="background:linear-gradient(135deg, #9B51E0, #FF3366); -webkit-background-clip:text; -webkit-text-fill-color:transparent; display:inline-block; font-family:'Outfit',sans-serif; font-weight:800;">Pulse</span></h1>
    <p style="color:#9E9E9E; font-size:0.95rem; margin:0 0 20px 0; font-family:'Inter',sans-serif;">AI Story Intelligence Engine — Attentional Flow Diagnostics</p>
    <div style="font-size:0.85rem; color:#9E9E9E; display:grid; grid-template-columns:repeat(2, 1fr); gap:12px; border-top:1px solid rgba(255,255,255,0.08); padding-top:16px; font-family:'Inter',sans-serif;">
        <div><b>PROJECT:</b> <code style="color:#00D2A0; background:rgba(0,210,160,0.1); padding:2px 6px; border-radius:4px;">{title.upper()}</code></div>
        <div><b>GENRE PROFILE:</b> <code style="color:#8EC5E9; background:rgba(142,197,233,0.1); padding:2px 6px; border-radius:4px;">{genre.upper()}</code></div>
        <div><b>ANALYSIS DATE:</b> <span>{analysis_date}</span></div>
        <div><b>ENGINE VERSION:</b> <code>v1.0</code></div>
    </div>
</div>
"""
    lines.append(header_html)
    lines.append(f"\n*{get_engine_mode_note()}*\n")

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    if isinstance(summary_data, dict):
        summary_text = summary_data.get('summary', '')
    else:
        summary_text = str(summary_data)

    if summary_text:
        summary_html = f"""
<div style="background:rgba(155, 81, 224, 0.04); border:1px solid rgba(155, 81, 224, 0.15); border-left:4px solid #9B51E0; border-radius:10px; padding:20px 24px; color:#E0E0E0; font-family:'Inter',sans-serif; margin-bottom:28px; line-height:1.75;">
    <h3 style="font-family:'Outfit',sans-serif; margin:0 0 10px 0; font-size:1.15rem; color:white; font-weight:700; border:none; padding:0; display:flex; align-items:center; gap:8px;">🧠 Executive Analysis</h3>
    {summary_text}
</div>
"""
        lines.append(summary_html)

    # -------------------------------------------------------------------------
    # RUNTIME & FORMAT SNAPSHOT
    # -------------------------------------------------------------------------
    lines.append("\n## 📊 Script Snapshot\n")
    runtime = dashboard.get('runtime_estimate', {})
    loc_profile = dashboard.get('location_profile', {})
    total_scenes = dashboard.get('total_scenes', len(trace))

    lines.append(f"| Metric | Assessment |")
    lines.append(f"|:-------|:-----------|")
    lines.append(f"| **Total Scenes** | {total_scenes} |")
    lines.append(f"| **Est. Runtime** | {runtime.get('estimated_minutes', '?')} minutes |")
    lines.append(f"| **Runtime Status** | {runtime.get('status', 'N/A')} |")
    lines.append(f"| **Locations** | {loc_profile.get('unique_locations', '?')} unique |")
    lines.append(f"| **INT/EXT Split** | {loc_profile.get('int_scenes', 0)} INT / {loc_profile.get('ext_scenes', 0)} EXT |")

    if loc_profile.get('location_warning'):
        lines.append(f"\n> [!CAUTION]\n> **Location Concentration:** {loc_profile['location_warning']}")

    # -------------------------------------------------------------------------
    # CORE SIGNAL DASHBOARD (Genre-benchmarked)
    # -------------------------------------------------------------------------
    lines.append("\n## 📈 Core Signal Dashboard")
    lines.append("*calibrated against standard **" + genre.title() + "** baselines.*\n")

    if trace:
        conflict_avg = avg_signal = _stats.mean([t.get('conflict', 0.0) for t in trace]) if trace else 0.0
        energy_avg = _stats.mean([t.get('attentional_signal', 0.0) for t in trace]) if trace else 0.0
        entropy_avg = _stats.mean([min(1.0, f.get('entropy_score', 0.0) / 12.0) for f in features]) if features else 0.0
        payoff_avg = _stats.mean([f.get('payoff_density', {}).get('payoff_density', 0.0) if isinstance(f.get('payoff_density'), dict) else 0.0 for f in features]) if features else 0.0
        sentiment_avg = _stats.mean([t.get('sentiment', 0.0) for t in trace]) if trace else 0.0

        lines.append(f"| Core Signal | Strength | Benchmark Status |")
        lines.append(f"|:------------|:----------|:-----------------|")
        lines.append(f"| **Conflict** | `{_stars(conflict_avg)}` | {_benchmark_tag(conflict_avg, genre, 'conflict')} |")
        lines.append(f"| **Attentional Flow (Energy)** | `{_stars(energy_avg)}` | {_benchmark_tag(energy_avg, genre, 'energy')} |")
        lines.append(f"| **Linguistic Texture (Entropy)** | `{_stars(entropy_avg)}` | {entropy_avg:.2f} *(reference signal)* |")
        lines.append(f"| **Stakes Payoff Density** | `{_stars(payoff_avg)}` | {payoff_avg:.2f} *(reference signal)* |")
        lines.append(f"| **Sentiment Baseline** | `{_stars((sentiment_avg + 1) / 2)}` | {sentiment_avg:+.2f} *(Dark → Bright)* |")
    else:
        lines.append("*[!] No temporal trace data found.*")

    # -------------------------------------------------------------------------
    # VISUAL NARRATIVE HEATMAP
    # -------------------------------------------------------------------------
    if trace:
        lines.append("\n## 🌡️ Attentional Flow Heatmap")
        lines.append("*Visual scene-by-scene tension map:*\n")
        
        boxes_html = ""
        for i, s in enumerate(trace):
            val = s.get('attentional_signal', 0.5)
            if val < 0.25:
                color = "#2F48B9" # cool blue (breather)
                title = f"Scene {i+1}: {val:.0%} (Low Tension / Breather)"
            elif val < 0.50:
                color = "#00D2A0" # mint green (moderate)
                title = f"Scene {i+1}: {val:.0%} (Moderate Tension)"
            elif val < 0.75:
                color = "#F57946" # amber orange (high)
                title = f"Scene {i+1}: {val:.0%} (High Tension / Suspense)"
            else:
                color = "#D92987" # rose-crimson (climax)
                title = f"Scene {i+1}: {val:.0%} (Peak Climax)"
                
            boxes_html += f'<span title="{title}" style="display:inline-block; width:12px; height:12px; background:{color}; margin:2px; border-radius:2px; box-shadow:0 0 4px {color}33;"></span>'
            
        heatmap_html = f"""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:20px; font-family:'Inter',sans-serif; line-height:1; margin-bottom:24px;">
    <div style="display:flex; flex-wrap:wrap; margin-bottom:14px;">
        {boxes_html}
    </div>
    <div style="display:flex; gap:16px; font-size:0.72rem; color:#A3A0B3; flex-wrap:wrap;">
        <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#2F48B9; border-radius:2px;"></span> Breather (&lt;25%)</div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#00D2A0; border-radius:2px;"></span> Moderate (25-50%)</div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#F57946; border-radius:2px;"></span> High (50-75%)</div>
        <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#D92987; border-radius:2px;"></span> Peak Climax (&gt;75%)</div>
    </div>
</div>
"""
        lines.append(heatmap_html)

    # -------------------------------------------------------------------------
    # ACT STRUCTURE
    # -------------------------------------------------------------------------
    act = dashboard.get('act_structure', {})
    if act and act.get('act1_pct', 0) > 0:
        lines.append("\n## 🎬 Act Structure Balance")
        act_html = f"""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:20px; font-family:'Inter',sans-serif; margin-bottom:24px;">
    <div style="display:flex; gap:4px; height:24px; border-radius:6px; overflow:hidden; margin-bottom:12px;">
        <div style="width:{act['act1_pct']}%; background:#FF7043; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:white;">Act I · {act['act1_pct']}%</div>
        <div style="width:{act['act2_pct']}%; background:#9B51E0; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:white;">Act II · {act['act2_pct']}%</div>
        <div style="width:{act['act3_pct']}%; background:#00C853; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:#121212;">Act III · {act['act3_pct']}%</div>
    </div>
    <div style="font-size:0.82rem; color:#A3A0B3; line-height:1.4;">
        <b>Scene counts:</b> Act I: {act.get('act1', 0)} · Act II: {act.get('act2', 0)} · Act III: {act.get('act3', 0)} scenes | Balance Status: <b style="color:white;">{act.get('balance', 'N/A')}</b>
    </div>
</div>
"""
        lines.append(act_html)

    # -------------------------------------------------------------------------
    # DIALOGUE VS ACTION
    # -------------------------------------------------------------------------
    dar = dashboard.get('dialogue_action_ratio', {})
    if isinstance(dar, dict) and dar.get('global_dialogue_ratio') is not None:
        lines.append("\n## 💬 Dialogue vs Action split")
        d_pct = round(dar.get('global_dialogue_ratio', 0.5) * 100)
        a_pct = 100 - d_pct
        bench = round(dar.get('genre_benchmark', 0.5) * 100) if isinstance(dar.get('genre_benchmark'), float) else dar.get('genre_benchmark', 50)
        
        dar_html = f"""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:20px; font-family:'Inter',sans-serif; margin-bottom:24px;">
    <div style="display:flex; gap:4px; height:24px; border-radius:6px; overflow:hidden; margin-bottom:12px;">
        <div style="width:{d_pct}%; background:#8EC5E9; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:#121212;">Dialogue · {d_pct}%</div>
        <div style="width:{a_pct}%; background:#FF7043; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; color:white;">Action · {a_pct}%</div>
    </div>
    <div style="font-size:0.82rem; color:#A3A0B3; line-height:1.4;">
        <b>Genre Benchmark ({genre}):</b> {bench - 10}%–{bench + 10}% dialogue | Your script is <b style="color:white;">{d_pct}%</b> dialogue ({dar.get('assessment', '')}).
    </div>
</div>
"""
        lines.append(dar_html)

    # -------------------------------------------------------------------------
    # STAKES DISTRIBUTION
    # -------------------------------------------------------------------------
    stakes_data = dashboard.get('stakes_profile', {})
    if stakes_data:
        valid_stakes = {'Physical', 'Emotional', 'Social', 'Moral', 'Existential'}
        stakes = {k: v for k, v in stakes_data.items() if k in valid_stakes and isinstance(v, (int, float)) and v > 0}
        if stakes:
            lines.append("\n## 🎯 Stakes Distribution Profile")
            sorted_stakes = sorted(stakes.items(), key=lambda x: x[1], reverse=True)
            total_st_scenes = sum(stakes.values())
            
            color_map = {
                'Physical': '#FF3366',
                'Emotional': '#FF7043',
                'Social': '#00C853',
                'Moral': '#9B51E0',
                'Existential': '#A56DFF'
            }
            
            rows_html = ""
            for label, val in sorted_stakes:
                pct = (val / total_st_scenes) * 100
                color = color_map.get(label, '#8EC5E9')
                rows_html += f"""
                <div style="display:flex; align-items:center; gap:16px; margin-bottom:12px; font-family:'Inter', sans-serif;">
                    <div style="width:100px; font-family:'Outfit', sans-serif; font-size:0.8rem; font-weight:700; color:#A3A0B3; text-transform:uppercase; letter-spacing:0.08em; text-align:left;">{label}</div>
                    <div style="flex:1; height:8px; border-radius:4px; background:rgba(255,255,255,0.05); position:relative;">
                        <div style="position:absolute; top:0; left:0; width:{pct:.1f}%; height:100%; border-radius:4px; background:{color}; box-shadow:0 0 6px {color}44;"></div>
                    </div>
                    <div style="width:130px; font-family:'Outfit', sans-serif; font-size:0.8rem; font-weight:700; color:white; text-align:right; opacity:0.95;">
                        <span style="font-weight:800;">{val}</span> {"scenes" if val > 1 else "scene"} ({pct:.0f}%)
                    </div>
                </div>
                """
                
            stakes_html = f"""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:20px; font-family:'Inter',sans-serif; margin-bottom:24px;">
    {rows_html}
</div>
"""
            lines.append(stakes_html)

    # -------------------------------------------------------------------------
    # STRUCTURAL TURNING POINTS
    # -------------------------------------------------------------------------
    lines.append("\n## ⏳ Structural Turning Points")
    turning = dashboard.get('structural_turning_points', {})
    if turning.get('note'):
        lines.append(f"*{turning['note']}*")
    else:
        for beat_name, beat_data in turning.items():
            if not isinstance(beat_data, dict):
                continue
            label = beat_name.replace('_', ' ').title()
            scene = beat_data.get('scene', '?')
            strength = beat_data.get('strength', 0)
            normalized_strength = min(1.0, strength / 12.0) if strength > 1 else strength
            warning = beat_data.get('warning', '')
            bar = _stars(normalized_strength)
            lines.append(f"- **{label}**: Scene {scene} ` {bar} ` (relative strength {normalized_strength:.2f})")
            if warning:
                lines.append(f"  > [!WARNING] {warning}")

    # -------------------------------------------------------------------------
    # NARRATIVE DIAGNOSIS (Styled Cards)
    # -------------------------------------------------------------------------
    lines.append("\n## 🩺 Narrative Health Check\n")
    if diagnosis:
        for item in diagnosis:
            lines.append(_format_markdown_card(item))
    else:
        lines.append("<div style='background:rgba(0, 210, 160, 0.04); border:1px solid rgba(0, 210, 160, 0.2); border-left:4px solid #00D2A0; border-radius:8px; padding:16px 20px; font-family:Inter,sans-serif; color:white;'><b>No structural anomalies detected.</b> Your script pacing holds well.</div>")

    # -------------------------------------------------------------------------
    # CREATIVE PROVOCATIONS
    # -------------------------------------------------------------------------
    provocations = wi.get('creative_provocations', [])
    if provocations:
        lines.append("\n## 💡 Creative Provocations\n")
        for p in provocations:
            lines.append(_format_provocation_card(p))

    # -------------------------------------------------------------------------
    # CHARACTER ARCS
    # -------------------------------------------------------------------------
    lines.append("\n## 🎭 Character Arc Map")
    char_arcs = dashboard.get('character_arcs', {})
    if char_arcs:
        lines.append(f"| Character | Arc Type | Agency Trajectory |")
        lines.append(f"|:----------|:---------|:------------------|")
        for char, arc_data in list(char_arcs.items())[:8]:
            arc_label = arc_data.get('arc_type', arc_data.get('arc', 'Unknown'))
            start = arc_data.get('agency_start', arc_data.get('start_agency', 0))
            end = arc_data.get('agency_end', arc_data.get('end_agency', 0))
            delta = arc_data.get('agency_delta', end - start)
            traj = f"`{start:+.2f}` → `{end:+.2f}` ({delta:+.2f})"
            lines.append(f"| **{char}** | {arc_label} | {traj} |")
    else:
        lines.append("*Character dynamics analysis unavailable.*")

    # -------------------------------------------------------------------------
    # SCENE ECONOMY MAP
    # -------------------------------------------------------------------------
    lines.append("\n## ✂️ Scene Efficiency")
    econ_map = dashboard.get('scene_economy_map', {})
    cut_candidates = econ_map.get('cut_candidates', [])
    low_count = econ_map.get('low_economy_count', 0)
    high_scenes = econ_map.get('high_economy_scenes', [])

    if cut_candidates:
        lines.append(f"\n> [!IMPORTANT]\n> Found **{low_count} Pacing Opportunities**. These scenes could benefit from tighter rhythm: Scenes {', '.join(str(s) for s in cut_candidates)}")
    
    if high_scenes:
        lines.append(f"\n🌟 **Load-Bearing Scenes:** {', '.join(str(s) for s in high_scenes[:5])}")

    econ_table = econ_map.get('map', [])
    if econ_table:
        lines.append(f"\n| Scene | Efficiency | Delta |")
        lines.append(f"|:------|:-----------|:------|")
        for e in econ_table[:10]:
            icon = "🟢" if e['label'] == 'High Economy' else ("🟡" if e['label'] == 'Moderate Economy' else "🔴")
            lines.append(f"| {e['scene']} | {icon} {e['label']} | `{e['score']}%` |")
        if len(econ_table) > 10:
            lines.append(f"| ... | *({len(econ_table) - 10} more)* | |")

    # -------------------------------------------------------------------------
    # FORMAT COMPLIANCE
    # -------------------------------------------------------------------------
    lines.append("\n## 📋 Industry Format Audit")
    fmt = dashboard.get('format_compliance', {})
    if fmt:
        issues = fmt.get('issues', [])
        score = fmt.get('compliance_score', 100)
        bar = _stars(score / 100)
        lines.append(f"**Structural Integrity:** `{score}/100` &nbsp; `{bar}`\n")
        if issues:
            for issue in issues:
                lines.append(f"- [!] {issue}")
        else:
            lines.append("✅ Professional industry standards met.")
    else:
        lines.append("*Format audit not performed.*")

    # -------------------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------------------
    lines.append("\n" + "---" * 10 + "\n")
    lines.append("*Created with ScriptPulse v1.0 · Reference signals for writer reflection · Confidential*")
    lines.append("\n" + FULL_DISCLAIMER_MARKDOWN)

    return "\n".join(lines)
