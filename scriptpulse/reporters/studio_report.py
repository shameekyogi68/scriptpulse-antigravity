"""
ScriptPulse Studio Reporter (Market Professional Layer)
Gap Solved: "The Screenshot Problem"

Generates a professional "Studio Coverage" style HTML report 
that can be printed to PDF.
"""

import base64
import statistics

def generate_report(report_data, script_title="Untitled Script", user_notes="", lens="Story Editor"):
    """
    Generate a standalone HTML string for the report.
    """
    
    # 1. Extract Key Metrics
    trace = report_data.get('temporal_trace', [])
    avg_effort = statistics.mean([t['attentional_signal'] for t in trace]) if trace else 0
    
    writer_intel = report_data.get('writer_intelligence', {})
    diagnoses = writer_intel.get('narrative_diagnosis', [])
    priorities = writer_intel.get('rewrite_priorities', [])

    # --- Persona Filtering Logic (Sync with writer_view.py) ---
    EXEC_ICONS = ['🔵', '🔴', '⚖️', '🚫', '👥', '📉', '⚠️', '🎢', '🟠', '✨']
    EDITOR_ICONS = ['🧵', '⬜', '👻', '✅', '🔵', '🔴', '⭐', '✨', '🟡', '🎢', '🟠', '🗣️', '🧠', '💡']
    COORD_ICONS = ['✂️', '🔴', '🟠', '🚫', '💎', '⛓️', '🎭', '👥', '🎙️', '🟢', '🗣️', '🧠', '💡', '✨']
    
    filtered_diags = []
    for text in diagnoses:
        is_exec = any(icon in text for icon in EXEC_ICONS)
        is_editor = any(icon in text for icon in EDITOR_ICONS)
        is_coord = any(icon in text for icon in COORD_ICONS)
        if "Same Voice" in text: is_exec, is_editor, is_coord = False, True, True
        elif "Too Slow" in text: is_exec, is_editor, is_coord = True, True, False
        if (lens == "Studio Executive" and is_exec) or \
           (lens == "Story Editor" and is_editor) or \
           (lens == "Script Coordinator" and is_coord):
            filtered_diags.append(text)
    
    if not filtered_diags and diagnoses:
        filtered_diags = [d for d in diagnoses if any(i in d for i in ['✅', '✨', '🟢'])] or diagnoses[:1]

    filtered_pris = []
    exec_pri_kws = ["boredom", "cut", "engagement", "budget", "unfilmable", "name", "slow"]
    coord_pri_kws = ["dialogue", "show", "unfilmable", "fluff", "prose", "voice", "economy"]
    for p in priorities:
        txt = f"{p.get('action', '')} {p.get('root_cause', '')}".lower()
        if (lens == "Studio Executive" and any(k in txt for k in exec_pri_kws)) or \
           (lens == "Script Coordinator" and any(k in txt for k in coord_pri_kws)) or \
           (lens == "Story Editor"):
            filtered_pris.append(p)
    
    if not filtered_pris and priorities:
        filtered_pris = priorities[:3]

    # Recommendation Logic
    rec = "CONSIDER"
    if avg_effort < 0.35: rec = "PASS (Low Engagement)"
    elif avg_effort > 0.75: rec = "PASS (High Strain)"
    
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
                --accent: {('#3b82f6' if lens == "Story Editor" else '#6366f1' if lens == "Studio Executive" else '#10b981')};
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
                grid-template-columns: repeat({('5' if lens == "Studio Executive" else '3')}, 1fr); 
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
            <div class="meta">
                ENGINE: Script<span style="color: #0052FF; font-weight: bold;">Pulse</span> v15.0 Gold | PERSPECTIVE: {lens}
            </div>
        </div>
        
        <div class="verdict">
            <div>
                <div class="verdict-label">Recommendation</div><br>
                <div class="verdict-value">{rec}</div>
            </div>
            <div class="confidence-pill">
                Confidence: {int(report_data.get('meta', {}).get('confidence_score', {}).get('score', 0)*100)}%
            </div>
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
            ''' if lens == "Studio Executive" else ""}
        </div>
        
        <div class="section">
            <h3>Diagnostic Summary</h3>
            <ul>
                {''.join([f"<li>{item}</li>" for item in filtered_diags]) if filtered_diags else '<li>Analysis clear. No high-risk anomalies.</li>'}
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
            <h3>Rewrite Priorities</h3>
            <table class="priority-table">
                <thead>
                    <tr>
                        <th>Intervention Strategy</th>
                        <th>Leverage</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{edit['action']}</td><td><span class='tag tag-high'>{edit['leverage']}</span></td></tr>" for edit in filtered_pris[:5]]) if filtered_pris else '<tr><td colspan="2">No high-priority revisions required.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        {f'<div class="section" style="background: #fffbeb; border: 1px solid #fef3c7;"><h3>Reader Perspectives</h3><p>{user_notes}</p></div>' if user_notes else ''}
        
        <div class="section">
            <h3>Character Voice Audit</h3>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">Distinctiveness check for lead roles:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                {''.join([f"<div style='background: #f8fafc; padding: 15px; border-radius: 8px;'><div style='font-weight: 700; color: var(--primary);'>{char}</div><div style='font-size: 13px;'>Agency (Action): {metrics['agency']:.2f} | Sentiment: {metrics['sentiment']:.2f}</div></div>" for char, metrics in list(report_data.get('voice_fingerprints', {}).items())[:6]])}
            </div>
        </div>
        
        <div class="footer">
            GEN-SPEC: v{report_data.get('meta', {}).get('metric_version', '1.3')} | PROFILE: v{report_data.get('meta', {}).get('genre_profile_version', '1.0')}<br>
            SECURE HASH: {report_data.get('meta', {}).get('constants_hash', 'N/A')}<br>
            &copy; 2026 ScriptPulse Biometric Systems. Confidential & Proprietary.
        </div>
    </div>
    
    </body>
    </html>
    """
    
    return html
