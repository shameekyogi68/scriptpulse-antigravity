"""
ScriptPulse Studio Reporter (Market Professional Layer)
Gap Solved: "The Screenshot Problem"

Generates a professional "Studio Coverage" style HTML report 
that can be printed to PDF.
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

    # ── Pull lens configuration from the master lens registry ──────────────
    try:
        from ..pipeline.lenses import get_lens
        lens_cfg = get_lens(lens)
    except Exception:
        lens_cfg = {'color': '#3b82f6', 'priority_icons': [], 'priority_keywords': [], 'description': ''}

    accent_color   = lens_cfg.get('color', '#3b82f6')
    priority_icons = set(lens_cfg.get('priority_icons', []))
    priority_kws   = lens_cfg.get('priority_keywords', [])
    lens_desc      = lens_cfg.get('description', '')
    # Studio Executive gets 5-column stat grid; others get 3
    stat_cols      = '5' if lens == 'Studio Executive' else '3'

    # --- Perspective-Aware Diagnostic Filtering ---
    # Each perspective has its own priority icon set — filter accordingly.
    # If a lens has NO priority_icons defined, it sees everything (Story Editor).
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

    # Experience framing — not pass/fail coverage verdicts
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

    # 2. Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Script Intelligence Coverage ({lens}): {script_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #0f172a;
                --accent: {accent_color};
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #1e293b;
                --text-muted: #64748b;
            }}
            
            body {{ 
                font-family: 'Outfit', sans-serif; 
                line-height: 1.6; 
                color: var(--text); 
                background-color: var(--bg);
                margin: 0; 
                padding: 0;
            }}
            
            .container {{
                max-width: 900px;
                margin: 40px auto;
                padding: 0 20px;
            }}
            
            .header {{ 
                text-align: left; 
                margin-bottom: 40px; 
                background: var(--primary);
                color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .header::after {{
                content: "";
                position: absolute;
                top: -50%;
                right: -10%;
                width: 300px;
                height: 300px;
                background: rgba(59, 130, 246, 0.1);
                border-radius: 50%;
                z-index: 0;
            }}
            
            .header h1 {{ margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.2em; opacity: 0.8; position: relative; z-index: 1; }}
            .header h2 {{ margin: 10px 0 20px 0; font-size: 36px; font-weight: 700; position: relative; z-index: 1; }}
            .header .meta {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; opacity: 0.7; position: relative; z-index: 1; }}
            
            .verdict {{ 
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: var(--card-bg);
                padding: 24px;
                border-radius: 12px;
                margin-bottom: 30px;
                border-left: 8px solid var(--accent);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .verdict-label {{ font-size: 14px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; float: left;}}
            .verdict-value {{ font-size: 24px; font-weight: 700; color: var(--primary); }}
            
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat({stat_cols}, 1fr); 
                gap: 20px; 
                margin-bottom: 40px; 
            }}
            
            .stat-card {{ 
                background: var(--card-bg);
                padding: 20px 15px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .stat-card h4 {{ margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.1em; }}
            .stat-card p {{ margin: 0; font-size: 22px; font-weight: 700; color: var(--primary); }}
            
            .section {{
                background: var(--card-bg);
                padding: 32px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }}
            
            .section h3 {{ 
                margin-top: 0; 
                font-size: 18px; 
                border-bottom: 2px solid #f1f5f9; 
                padding-bottom: 15px; 
                margin-bottom: 20px;
                color: var(--primary);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .priority-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .priority-table th {{ text-align: left; padding: 12px; background: #f1f5f9; font-size: 12px; text-transform: uppercase; color: var(--text-muted); }}
            .priority-table td {{ padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            .tag {{ 
                display: inline-block; 
                padding: 2px 8px; 
                border-radius: 4px; 
                font-size: 11px; 
                font-weight: 700; 
                text-transform: uppercase;
                background: #e2e8f0;
            }}
            .tag-high {{ background: #fee2e2; color: #b91c1c; }}
            
            .footer {{ 
                margin-top: 60px; 
                padding: 40px 0;
                text-align: center; 
                font-size: 12px; 
                color: var(--text-muted); 
                border-top: 1px solid #e2e8f0; 
                font-family: 'JetBrains Mono', monospace;
            }}
            
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 12px; }}
            
            .confidence-pill {{
                background: #f1f5f9;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            
            .economy-item {{
                background: #f8fafc;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 8px;
                font-size: 13px;
                border-left: 4px solid #e2e8f0;
            }}
            .economy-bloated {{ border-left-color: var(--danger); background: #fff1f2; }}
            .economy-tight {{ border-left-color: var(--success); background: #f0fdf4; }}

            .indicator {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--success);
            }}
        </style>
    </head>
    <body>
    
    <div class="container">
        <div class="header">
            <h1>Intelligence Coverage ({lens})</h1>
            <h2>{script_title}</h2>
            <div class="meta" style="opacity: 0.85; margin-top: 6px; font-size: 13px; letter-spacing: 0.05em;">
                📌 {lens_desc}
            </div>
            <div class="meta" style="margin-top: 8px;">
                ENGINE: Script<span style="color: #0052FF; font-weight: bold;">Pulse</span> v1.0 | PERSPECTIVE: {lens}
            </div>
        </div>
        
        <div class="verdict">
            <div>
                <div class="verdict-label">Experience Summary</div><br>
                <div class="verdict-value">{rec}</div>
            </div>
            <div class="confidence-pill">
                Confidence: {confidence_pct}% ({confidence_level})
            </div>
        </div>
        
        <div class="section" style="background: #f8fafc; border: 1px solid #e2e8f0; font-size: 13px; color: #475569;">
            <h3 style="margin-top: 0;">Important — How To Read This Report</h3>
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
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">✂️ Trim Candidates</h4>
                    {''.join([f'<div class="economy-item economy-bloated">Scene {s["scene"]}: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) < 35][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">None detected.</p>'}
                </div>
                <div>
                    <h4 style="font-size: 12px; text-transform: uppercase; margin-bottom: 10px;">💎 Lean Scenes</h4>
                    {''.join([f'<div class="economy-item economy-tight">Scene {s["scene"]}: {s["label"]} ({s["score"]}%)</div>' for s in economy_map if s.get('score', 0) > 75][:4]) or '<p style="font-size: 12px; color: var(--text-muted);">No high-efficiency scenes.</p>'}
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
                        <th>Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{edit['action']}</td><td><span class='tag tag-high'>{edit['leverage']}</span></td></tr>" for edit in filtered_pris[:5]]) if filtered_pris else '<tr><td colspan="2">No high-priority reflection points surfaced for this version.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        {f'<div class="section" style="background: #fffbeb; border: 1px solid #fef3c7;"><h3>Reader Perspectives</h3><p>{user_notes}</p></div>' if user_notes else ''}
        
        <div class="section">
            <h3>Character Voice Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">Distinctiveness check for lead roles:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                {''.join([f"<div style='background: #f8fafc; padding: 15px; border-radius: 8px;'><div style='font-weight: 700; color: var(--primary);'>{char}</div><div style='font-size: 13px;'>Agency (Action): {metrics.get('agency', 0):.2f} | Sentiment: {metrics.get('sentiment', 0):.2f}</div></div>" for char, metrics in list(report_data.get('voice_fingerprints', {}).items())[:6]]) if report_data.get('voice_fingerprints') else '<p style="font-size: 13px; color: var(--text-muted);">Voice analysis unavailable for this script.</p>'}
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
