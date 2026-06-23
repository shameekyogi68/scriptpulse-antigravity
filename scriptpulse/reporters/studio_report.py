"""
ScriptPulse Studio Reporter (Market Professional Layer)
Gap Solved: "The Screenshot Problem"

Generates a professional "Studio Coverage" style HTML report 
styled to match the dark cinematic obsidian theme.
"""

import base64
import statistics
from scriptpulse.disclaimers import FULL_DISCLAIMER_HTML, engagement_signal_label

def generate_report(report_data, script_title="Untitled Script", user_notes="", lens="Story Editor"):
    """
    Generate a standalone HTML string for the report.
    """
    
    # 1. Extract Key Metrics
    trace = report_data.get('temporal_trace', [])
    try:
        avg_effort = statistics.mean([t.get('attentional_signal', 0.5) for t in trace]) if trace else 0.5
    except Exception:
        avg_effort = 0.5
    
    writer_intel = report_data.get('writer_intelligence', {})
    diagnoses = writer_intel.get('narrative_diagnosis', [])
    priorities = writer_intel.get('rewrite_priorities', [])
    genre = writer_intel.get('genre_context', 'general')

    # ── Pull lens configuration from the master lens registry ──────────────
    try:
        from ..pipeline.lenses import get_lens
        lens_cfg = get_lens(lens)
    except Exception:
        lens_cfg = {'color': '#9B51E0', 'priority_icons': [], 'priority_keywords': [], 'description': ''}

    accent_color   = lens_cfg.get('color', '#9B51E0')
    priority_icons = set(lens_cfg.get('priority_icons', []))
    priority_kws   = lens_cfg.get('priority_keywords', [])
    lens_desc      = lens_cfg.get('description', '')
    # Studio Executive gets 5-column stat grid; others get 3
    stat_cols      = '5' if lens == 'Studio Executive' else '3'

    # --- Perspective-Aware Diagnostic Filtering ---
    filtered_diags = []
    for text in diagnoses:
        if not priority_icons:  # Story Editor sees all
            filtered_diags.append(text)
        elif any(icon in text for icon in priority_icons):
            filtered_diags.append(text)

    # Force-override special cases that all perspectives should share
    for text in diagnoses:
        if "Same Voice" in text and text not in filtered_diags:
            filtered_diags.append(text)
        if "Engagement Drop" in text and lens == "Studio Executive" and text not in filtered_diags:
            filtered_diags.append(text)

    if not filtered_diags and diagnoses:
        filtered_diags = [d for d in diagnoses if any(i in d for i in ['✅', '✨', '🟢'])] or diagnoses[:1]

    # --- Perspective-Aware Priority Filtering ---
    filtered_pris = []
    for p in priorities:
        if isinstance(p, str):
            filtered_pris.append({'action': p, 'leverage': 'Medium', 'root_cause': ''})
            continue
        if not isinstance(p, dict):
            continue
        txt = f"{p.get('action', '')} {p.get('root_cause', '')}".lower()
        if not priority_kws:  # Story Editor sees all priorities
            filtered_pris.append(p)
        elif any(k in txt for k in priority_kws):
            filtered_pris.append(p)

    if not filtered_pris and priorities:
        filtered_pris = priorities[:3]

    # Experience framing
    rec = "STABLE FLOW — No major attentional strain spikes detected in this version"
    if avg_effort < 0.35:
        rec = "LOW ENGAGEMENT SIGNAL — Consider strengthening hooks where attention dips"
    elif avg_effort > 0.75:
        rec = "HIGH INTENSITY — Sustained engagement load; review recovery beats for balance"

    confidence_pct = report_data.get('meta', {}).get('confidence', 0.85)
    if isinstance(confidence_pct, float) and confidence_pct <= 1:
        confidence_pct = int(confidence_pct * 100)
    else:
        confidence_pct = int(confidence_pct or 85)
    confidence_level = report_data.get('meta', {}).get('confidence_level', 'MEDIUM')
    
    # --- Additional Data Extraction ---
    loc_profile = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('location_profile', {})
    char_arcs = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('character_arcs', {})
    cast_size = len(char_arcs) if char_arcs else len(report_data.get('voice_fingerprints', {}))
    economy_map = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('scene_economy_map', {}).get('map', [])

    # ── Act Structure html ──────────────────
    act = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('act_structure', {})
    act_html = ""
    if act and act.get('act1_pct', 0) > 0:
        act_html = f"""
        <div class="section">
            <h3>🎬 Act Structure Balance</h3>
            <div style="display: flex; gap: 4px; height: 26px; border-radius: 6px; overflow: hidden; margin-bottom: 12px; margin-top: 10px;">
                <div style="width: {act['act1_pct']}%; background: var(--warning); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white;">Act I · {act['act1_pct']}%</div>
                <div style="width: {act['act2_pct']}%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white;">Act II · {act['act2_pct']}%</div>
                <div style="width: {act['act3_pct']}%; background: var(--success); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #121212;">Act III · {act['act3_pct']}%</div>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin: 0;">
                Act I: {act.get('act1', 0)} scenes · Act II: {act.get('act2', 0)} scenes · Act III: {act.get('act3', 0)} scenes | Balance: <b>{act.get('balance', 'N/A')}</b>
            </p>
        </div>
        """

    # ── Dialogue vs Action html ──────────────
    dar = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('dialogue_action_ratio', {})
    dar_html = ""
    if isinstance(dar, dict) and dar.get('global_dialogue_ratio') is not None:
        d_pct = round(dar.get('global_dialogue_ratio', 0.5) * 100)
        a_pct = 100 - d_pct
        bench = round(dar.get('genre_benchmark', 0.5) * 100) if isinstance(dar.get('genre_benchmark'), float) else dar.get('genre_benchmark', 50)
        dar_html = f"""
        <div class="section">
            <h3>💬 Dialogue vs Action split</h3>
            <div style="display: flex; gap: 4px; height: 26px; border-radius: 6px; overflow: hidden; margin-bottom: 12px; margin-top: 10px;">
                <div style="width: {d_pct}%; background: #8EC5E9; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #121212;">💬 Dialogue {d_pct}%</div>
                <div style="width: {a_pct}%; background: var(--warning); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white;">🎬 Action {a_pct}%</div>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin: 0;">
                Genre range: {bench - 10}%–{bench + 10}% dialogue | Script split: <b>{d_pct}%</b> dialogue ({dar.get('assessment', '')}).
            </p>
        </div>
        """

    # ── Stakes Distribution html ─────────────
    stakes_data = report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('stakes_profile', {})
    stakes_html = ""
    if stakes_data:
        valid_stakes = {'Physical', 'Emotional', 'Social', 'Moral', 'Existential'}
        stakes = {k: v for k, v in stakes_data.items() if k in valid_stakes and isinstance(v, (int, float)) and v > 0}
        if stakes:
            sorted_stakes = sorted(stakes.items(), key=lambda x: x[1], reverse=True)
            total_st_scenes = sum(stakes.values())
            
            color_map = {
                'Physical': 'var(--danger)',
                'Emotional': 'var(--warning)',
                'Social': 'var(--success)',
                'Moral': 'var(--accent)',
                'Existential': '#A56DFF'
            }
            
            shadow_map = {
                'Physical': 'rgba(255, 51, 102, 0.3)',
                'Emotional': 'rgba(255, 112, 67, 0.3)',
                'Social': 'rgba(0, 200, 83, 0.3)',
                'Moral': 'rgba(106, 72, 187, 0.3)',
                'Existential': 'rgba(165, 109, 255, 0.3)'
            }
            
            rows_html = ""
            for label, val in sorted_stakes:
                pct = (val / total_st_scenes) * 100
                color = color_map.get(label, '#8EC5E9')
                glow = shadow_map.get(label, 'rgba(85, 224, 255, 0.3)')
                
                rows_html += f"""
                <div style="display:flex; align-items:center; gap:16px; margin-bottom:12px;">
                    <div style="width:110px; font-size:12px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; text-align:left;">{label}</div>
                    <div style="flex:1; height:8px; border-radius:4px; background:rgba(255,255,255,0.05); position:relative;">
                        <div style="position:absolute; top:0; left:0; width:{pct:.1f}%; height:100%; border-radius:4px; background:{color}; box-shadow:0 0 6px {glow};"></div>
                    </div>
                    <div style="width:130px; font-size:12px; font-weight:700; color:white; text-align:right; opacity:0.9;">
                        <b>{val}</b> {"scenes" if val > 1 else "scene"} ({pct:.0f}%)
                    </div>
                </div>
                """
                
            stakes_html = f"""
            <div class="section">
                <h3>🎯 Stakes Distribution</h3>
                <div style="margin-top: 15px;">
                    {rows_html}
                </div>
            </div>
            """

    # ── Narrative Heatmap html ───────────────
    heatmap_html = ""
    if trace:
        boxes_html = ""
        for i, s in enumerate(trace):
            val = s.get('attentional_signal', 0.5)
            if val < 0.25:
                color = "#2F48B9" # cool blue
                title = f"Scene {i+1}: {val:.0%} (Breather)"
            elif val < 0.50:
                color = "#00D2A0" # mint green
                title = f"Scene {i+1}: {val:.0%} (Moderate)"
            elif val < 0.75:
                color = "#F57946" # amber orange
                title = f"Scene {i+1}: {val:.0%} (Suspense)"
            else:
                color = "#D92987" # rose-crimson
                title = f"Scene {i+1}: {val:.0%} (Peak Climax)"
                
            boxes_html += f'<span title="{title}" style="display:inline-block; width:12px; height:12px; background:{color}; margin:2px; border-radius:2px; box-shadow:0 0 4px {color}33;"></span>'
            
        heatmap_html = f"""
        <div class="section">
            <h3>🌡️ Attentional Flow Map</h3>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 15px;">Visual scene-by-scene tension map across the narrative:</p>
            <div style="display:flex; flex-wrap:wrap; margin-bottom:14px; background: rgba(0,0,0,0.15); padding:16px; border-radius:8px; border: 1px solid var(--glass-border);">
                {boxes_html}
            </div>
            <div style="display:flex; gap:16px; font-size:11px; color:var(--text-muted); flex-wrap:wrap;">
                <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#2F48B9; border-radius:2px;"></span> Breather (&lt;25%)</div>
                <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#00D2A0; border-radius:2px;"></span> Moderate (25-50%)</div>
                <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#F57946; border-radius:2px;"></span> High (50-75%)</div>
                <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; background:#D92987; border-radius:2px;"></span> Peak Climax (&gt;75%)</div>
            </div>
        </div>
        """

    # 2. Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Script Intelligence Coverage ({lens}): {script_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #1E1E1E;
                --accent: {accent_color};
                --success: #00C853;
                --warning: #FF7043;
                --danger: #FF3366;
                --bg: #121212;
                --card-bg: rgba(255, 255, 255, 0.03);
                --text: #E0E0E0;
                --text-muted: #9E9E9E;
                --glass-border: rgba(255, 255, 255, 0.08);
            }}
            
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                line-height: 1.65; 
                color: var(--text); 
                background-color: var(--bg);
                margin: 0; 
                padding: 0;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            @media print {{
                body {{
                    zoom: 95%;
                }}
                tr, .section, .stat-card, .verdict {{
                    page-break-inside: avoid;
                    break-inside: avoid;
                }}
            }}
            
            .container {{
                max-width: 940px;
                margin: 40px auto;
                padding: 0 20px;
            }}
            
            .header {{ 
                text-align: left; 
                margin-bottom: 40px; 
                background: var(--primary);
                color: white;
                padding: 40px;
                border-radius: 16px;
                border: 1px solid var(--glass-border);
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                background: linear-gradient(90deg, #9B51E0, #A56DFF, #FF3366);
            }}
            
            .header h1 {{ margin: 0; font-family: 'Outfit', sans-serif; font-size: 14px; text-transform: uppercase; letter-spacing: 0.25em; color: var(--accent); font-weight: 700; }}
            .header h2 {{ margin: 12px 0 16px 0; font-family: 'Outfit', sans-serif; font-size: 38px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; }}
            .header .meta {{ font-family: 'Inter', sans-serif; font-size: 13px; color: var(--text-muted); }}
            
            .verdict {{ 
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 24px;
                border-radius: 12px;
                margin-bottom: 30px;
                border: 1px solid var(--glass-border);
                border-left: 5px solid var(--accent);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }}
            
            .verdict-label {{ font-family: 'Outfit', sans-serif; font-size: 12px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.1em; }}
            .verdict-value {{ font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; color: white; margin-top: 4px; }}
            
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat({stat_cols}, 1fr); 
                gap: 20px; 
                margin-bottom: 40px; 
            }}
            
            .stat-card {{ 
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 20px 15px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid var(--glass-border);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }}
            
            .stat-card h4 {{ margin: 0 0 8px 0; font-family: 'Outfit', sans-serif; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.12em; }}
            .stat-card p {{ margin: 0; font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 700; color: white; }}
            
            .section {{
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                padding: 32px;
                border-radius: 16px;
                margin-bottom: 30px;
                border: 1px solid var(--glass-border);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }}
            
            .section h3 {{ 
                margin-top: 0; 
                font-family: 'Outfit', sans-serif;
                font-size: 20px; 
                font-weight: 700;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08); 
                padding-bottom: 14px; 
                margin-bottom: 22px;
                color: white;
                letter-spacing: -0.02em;
            }}
            
            .priority-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .priority-table th {{ text-align: left; padding: 12px; background: rgba(0,0,0,0.25); font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em; }}
            .priority-table td {{ padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px; color: var(--text); }}
            .tag {{ 
                display: inline-block; 
                padding: 4px 10px; 
                border-radius: 20px; 
                font-size: 10px; 
                font-weight: 700; 
                text-transform: uppercase;
                letter-spacing: 0.05em;
                background: rgba(255, 255, 255, 0.08);
                color: var(--text-muted);
            }}
            .tag-high {{ background: rgba(217, 41, 135, 0.15); color: var(--danger); border: 1px solid rgba(217, 41, 135, 0.3); }}
            .tag-medium {{ background: rgba(245, 121, 70, 0.15); color: var(--warning); border: 1px solid rgba(245, 121, 70, 0.3); }}
            
            .footer {{ 
                margin-top: 60px; 
                padding: 40px 0;
                text-align: center; 
                font-size: 12px; 
                color: var(--text-muted); 
                border-top: 1px solid rgba(255, 255, 255, 0.06); 
                font-family: 'JetBrains Mono', monospace;
                line-height: 1.8;
            }}
            
            ul {{ padding-left: 20px; margin: 0; }}
            li {{ margin-bottom: 14px; font-size: 14.5px; color: rgba(244, 246, 251, 0.9); }}
            
            .confidence-pill {{
                background: rgba(255,255,255,0.04);
                border: 1px solid var(--glass-border);
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                color: var(--text-muted);
            }}
            
            .economy-item {{
                background: rgba(0,0,0,0.15);
                padding: 14px;
                border-radius: 8px;
                margin-bottom: 10px;
                font-size: 13px;
                border-left: 4px solid rgba(255, 255, 255, 0.15);
                color: white;
            }}
            .economy-bloated {{ border-left-color: var(--danger); background: rgba(217, 41, 135, 0.04); border-top: 1px solid rgba(217, 41, 135, 0.1); border-bottom: 1px solid rgba(217, 41, 135, 0.1); }}
            .economy-tight {{ border-left-color: var(--success); background: rgba(0, 200, 83, 0.04); border-top: 1px solid rgba(0, 200, 83, 0.1); border-bottom: 1px solid rgba(0, 200, 83, 0.1); }}
        </style>
    </head>
    <body>
    
    <div class="container">
        <div class="header">
            <h1>Intelligence Coverage ({lens})</h1>
            <h2>{script_title}</h2>
            <div class="meta" style="opacity: 0.9; margin-top: 12px; font-size: 14px; font-weight: 500;">
                📌 {lens_desc}
            </div>
            <div class="meta" style="margin-top: 10px; font-size: 12px; opacity: 0.6; font-family: 'JetBrains Mono', monospace;">
                ENGINE: ScriptPulse v1.0 | PERSPECTIVE: {lens}
            </div>
        </div>
        
        <div class="verdict">
            <div>
                <div class="verdict-label">Experience Summary</div>
                <div class="verdict-value">{rec}</div>
            </div>
            <div class="confidence-pill">
                Confidence: {confidence_pct}% ({confidence_level})
            </div>
        </div>
        
        <div class="section" style="background: rgba(255, 51, 102, 0.03); border: 1px solid rgba(255, 51, 102, 0.15); font-size: 13.5px; color: var(--text-muted);">
            <h3 style="margin-top: 0; border-bottom-color: rgba(255,51,102,0.15); color: white;">Important — How To Read This Report</h3>
            {FULL_DISCLAIMER_HTML}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h4>Avg Engagement</h4>
                <p>{avg_effort:.2f}</p>
            </div>
            <div class="stat-card">
                <h4>Pacing Units</h4>
                <p>{len(trace)}</p>
            </div>
            <div class="stat-card">
                <h4>Est. Runtime</h4>
                <p>{writer_intel.get('structural_dashboard', {}).get('runtime_estimate', {}).get('estimated_minutes', len(trace)*2)}m</p>
            </div>
            {f'''
            <div class="stat-card">
                <h4>📍 Locations</h4>
                <p>{loc_profile.get('unique_locations', '—')}</p>
            </div>
            <div class="stat-card">
                <h4>🎭 Cast Size</h4>
                <p>{cast_size if cast_size else '—'}</p>
            </div>
            ''' if lens == 'Studio Executive' else ""}
        </div>

        {heatmap_html}

        {stakes_html}

        {act_html}

        {dar_html}
        
        <div class="section">
            <h3>Narrative Insights</h3>
            <ul>
                {''.join([f"<li>{item}</li>" for item in filtered_diags]) if filtered_diags else '<li>No major attentional strain alerts in this version. This does not mean the script is approved or complete — only that no high-risk patterns were flagged.</li>'}
            </ul>
        </div>
        
        {f'''
        <div class="section">
            <h3>Scene Economy Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 15px;">Targeting scenes for page efficiency and production speed:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.05em;">✂️ Trim Candidates</h4>
                    {''.join([f'<div class="economy-item economy-bloated"><b>Scene {s["scene"]}</b>: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) < 35][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">None detected.</p>'}
                </div>
                <div>
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.05em;">💎 Lean Scenes</h4>
                    {''.join([f'<div class="economy-item economy-tight"><b>Scene {s["scene"]}</b>: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) > 75][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">No high-efficiency scenes.</p>'}
                </div>
            </div>
        </div>
        ''' if lens == "Script Coordinator" and economy_map else ""}

        <div class="section">
            <h3>Growth Opportunities</h3>
            <table class="priority-table">
                <thead>
                    <tr>
                        <th>Recommended Action</th>
                        <th style="width: 140px; text-align: right;">Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{edit['action']}</td><td style='text-align: right;'><span class='tag tag-{'high' if edit['leverage'] == 'High' else 'medium'}'>{edit['leverage']} Impact</span></td></tr>" for edit in filtered_pris[:5]]) if filtered_pris else '<tr><td colspan="2">No high-priority reflection points surfaced for this version.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        {f'<div class="section" style="background: rgba(245, 121, 70, 0.03); border: 1px solid rgba(245, 121, 70, 0.15);"><h3 style="border-bottom-color: rgba(245, 121, 70, 0.15);">Reader Perspectives</h3><p style="font-size: 14.5px; line-height: 1.7; margin: 0; color: rgba(244,246,251,0.95);">{user_notes}</p></div>' if user_notes else ''}
        
        <div class="section">
            <h3>Character Voice Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">Distinctiveness check for lead roles:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                {''.join([f"<div style='background: rgba(0,0,0,0.25); padding: 18px; border-radius: 10px; border: 1px solid var(--glass-border);'><div style='font-family: \\'Outfit\\', sans-serif; font-weight: 700; color: white; font-size: 16px; margin-bottom: 6px;'>{char}</div><div style='font-size: 12.5px; color: var(--text-muted);'>Agency (Action): <span style='color: white; font-weight: 600;'>{metrics.get('agency', 0):.2f}</span> | Sentiment: <span style='color: white; font-weight: 600;'>{metrics.get('sentiment', 0):.2f}</span></div></div>" for char, metrics in list(report_data.get('voice_fingerprints', {}).items())[:6]]) if report_data.get('voice_fingerprints') else '<p style="font-size: 13px; color: var(--text-muted);">Voice analysis unavailable for this script.</p>'}
            </div>
        </div>
        
        <div class="footer">
            GEN-SPEC: v{report_data.get('meta', {}).get('metric_version', '1.3')} | PROFILE: v{report_data.get('meta', {}).get('genre_profile_version', '1.0')}<br>
            SECURE HASH: {report_data.get('meta', {}).get('constants_hash', 'N/A')}<br>
            &copy; 2026 ScriptPulse Analytics Engine. Confidential & Proprietary.
        </div>
    </div>
    
    </body>
    </html>
    """
    
    return html
