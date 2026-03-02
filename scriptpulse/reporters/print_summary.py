"""
ScriptPulse Print Summary Generator
Creates a concise 1-page summary for writers to print and pin.
"""

def generate_print_summary(report_data, script_title="Untitled Script"):
    """
    Generate a clean, printable 1-page HTML summary.
    """
    
    # Extract key metrics
    trace = report_data.get('temporal_trace', [])
    avg_tension = sum(p['attentional_signal'] for p in trace) / len(trace) if trace else 0
    
    valence_scores = report_data.get('valence_scores', [])
    avg_valence = sum(valence_scores) / len(valence_scores) if valence_scores else 0
    
    runtime = report_data.get('runtime_estimate', {}).get('avg_minutes', 0)
    
    # Get top problems
    scene_feedback = report_data.get('scene_feedback', {})
    all_warnings = []
    for scene_idx, notes in scene_feedback.items():
        warning_notes = [n for n in notes if n['severity'] == 'warning']
        for note in warning_notes[:2]:  # Top 2 per scene
            all_warnings.append({
                'scene': scene_idx + 1,
                'issue': note['issue'],
                'fix': note['suggestion']
            })
    
    top_problems = all_warnings[:5]  # Top 5 overall
    
    # Get strengths (scenes with high tension + positive valence)
    strengths = []
    for i, point in enumerate(trace):
        if point.get('attentional_signal', 0) > 0.7 and i < len(valence_scores) and valence_scores[i] > 0.1:
            strengths.append(f"Scene {i+1}: High energy, positive tone")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{
                --bg: #ffffff;
                --text: #1a1a1a;
                --muted: #666666;
                --issue: #fee2e2;
                --issue-text: #991b1b;
                --strength: #dcfce7;
                --strength-text: #166534;
                --border: #e5e7eb;
            }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                margin: 0; 
                padding: 40px; 
                color: var(--text);
                line-height: 1.5;
            }}
            .header {{
                border-bottom: 3px solid var(--text);
                padding-bottom: 20px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 800; text-transform: uppercase; }}
            .header .date {{ font-size: 12px; color: var(--muted); }}
            
            .stats-bar {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat {{
                border: 1px solid var(--border);
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-label {{ font-size: 11px; text-transform: uppercase; color: var(--muted); letter-spacing: 0.1em; margin-bottom: 5px; }}
            .stat-value {{ font-size: 20px; font-weight: 700; }}
            
            h2 {{ font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; padding-left: 10px; border-left: 4px solid var(--text); }}
            
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
            
            .card {{ margin-bottom: 15px; padding: 12px 15px; border-radius: 6px; font-size: 13px; }}
            .card.problem {{ background: var(--issue); color: var(--issue-text); border-left: 4px solid #ef4444; }}
            .card.strength {{ background: var(--strength); color: var(--strength-text); border-left: 4px solid #22c55e; }}
            
            .card b {{ display: block; margin-bottom: 4px; text-transform: uppercase; font-size: 11px; opacity: 0.8; }}
            
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid var(--border);
                font-size: 10px;
                color: var(--muted);
                display: flex;
                justify-content: space-between;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>{script_title}</h1>
                <div style="font-size: 14px; color: var(--muted); margin-top: 5px;">ScriptPulse Core Intelligence Summary</div>
            </div>
            <div class="date">v14.0 | Phase 32 Output</div>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <div class="stat-label">Intensity Profile</div>
                <div class="stat-value">{int(avg_tension * 100)}%</div>
            </div>
            <div class="stat">
                <div class="stat-label">Emotional Tone</div>
                <div class="stat-value">{"LUMINOUS" if avg_valence > 0.15 else "SHADOW" if avg_valence < -0.15 else "NEUTRAL"}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Est. Screen Time</div>
                <div class="stat-value">{runtime} MIN</div>
            </div>
        </div>
        
        <div class="grid">
            <div>
                <h2>Critical Revisions</h2>
                {''.join([f'<div class="card problem"><b>SCENE {p["scene"]} REVISION</b>{p["issue"]} <br> <i style="opacity: 0.7;">Solution: {p["fix"]}</i></div>' for p in top_problems]) if top_problems else '<p style="font-size:13px;">No critical errors identified.</p>'}
            </div>
            
            <div>
                <h2>Narrative Anchors</h2>
                {''.join([f'<div class="card strength"><b>STRENGTH</b>{s}</div>' for s in strengths[:5]]) if strengths else '<p style="font-size:13px;">Focus on increasing high-engagement beats.</p>'}
            </div>
        </div>
        
        <div class="footer">
            <div>&copy; 2026 ScriptPulse Biometric Systems. For internal writer use only.</div>
            <div>STRIKE TEAM VALIDATED</div>
        </div>
    </body>
    </html>
    """
    
    return html
