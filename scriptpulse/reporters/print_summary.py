"""
ScriptPulse Print Summary Generator
Creates a concise 1-page summary for writers to print and pin.
Uses writer_intelligence data for accurate, persona-aware output.
"""

import re
from scriptpulse.disclaimers import FULL_DISCLAIMER_HTML, engagement_signal_label

def _strip_md(text):
    """Convert markdown bold/italic to HTML for clean rendering."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text


def generate_print_summary(report_data, script_title="Untitled Script"):
    """
    Generate a clean, printable 1-page HTML summary.
    Pulls data from writer_intelligence (the real pipeline output).
    """
    
    # Extract key metrics from the CORRECT keys
    trace = report_data.get('temporal_trace', [])
    try:
        avg_tension = sum(p.get('attentional_signal', 0.5) for p in trace) / len(trace) if trace else 0.5
    except Exception:
        avg_tension = 0.5
    
    wi = report_data.get('writer_intelligence', {})
    dashboard = wi.get('structural_dashboard', {})
    diagnosis = wi.get('narrative_diagnosis', [])
    priorities = wi.get('rewrite_priorities', [])
    
    sp_score = dashboard.get('scriptpulse_score', 50)
    score_label = engagement_signal_label(sp_score)
    
    # Pacing and Cast (Task 3 & 4)
    pacing = dashboard.get('act_structure', {}).get('pacing_benchmark', 'Balanced')
    cast_count = dashboard.get('cast_count_deterministic', 0)
    
    # Runtime
    runtime_data = dashboard.get('runtime_estimate', {})
    runtime = runtime_data.get('estimated_minutes', len(trace) * 2) if isinstance(runtime_data, dict) else len(trace) * 2
    
    # Top problems (from diagnostics — red/orange items)
    problems_html = ""
    problem_items = [d for d in diagnosis if any(icon in d for icon in ['🔴', '🚫', '🟠', '✂️', '🧵', '👻', '🔵'])]
    if problem_items:
        for p in problem_items[:5]:
            problems_html += f'<div class="card problem">{_strip_md(p)}</div>'
    else:
        problems_html = '<p style="font-size:13px;">No major attentional strain alerts flagged. This does not mean the draft is complete — review strengths and optional reflection points below.</p>'
    
    # Strengths (from diagnostics — green items)
    strengths_html = ""
    strength_items = [d for d in diagnosis if any(icon in d for icon in ['✅', '✨', '🟢', '💎', '⭐'])]
    if strength_items:
        for s in strength_items[:5]:
            strengths_html += f'<div class="card strength">{_strip_md(s)}</div>'
    else:
        strengths_html = '<p style="font-size:13px;">No standout positive signals auto-detected. Focus on scenes with high engagement in the full dashboard.</p>'
    
    # Priority Fixes
    fixes_html = ""
    if priorities:
        for i, p in enumerate(priorities[:3]):
            if isinstance(p, str):
                action, leverage = p, 'Medium'
            else:
                action = p.get('action', '')
                leverage = p.get('leverage', 'Medium')
            fixes_html += f'<div class="card problem"><b>FIX {i+1}: {leverage} IMPACT</b>{_strip_md(action)}</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ScriptPulse Summary — {script_title}</title>
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
                grid-template-columns: repeat(4, 1fr);
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
                <div style="font-size: 14px; color: var(--muted); margin-top: 5px;">Script<span style="color: #0052FF;">Pulse</span> Core Intelligence Summary</div>
            </div>
            <div class="date">v1.0 | Script<span style="color: #0052FF;">Pulse</span> Score: {sp_score}/100 ({score_label})</div>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <div class="stat-label">Engagement Index</div>
                <div class="stat-value">{sp_score}/100</div>
                <div style="font-size:11px;color:#666;margin-top:4px;">{score_label}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Pacing Profile</div>
                <div class="stat-value">{pacing}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Cast (5+ Lines)</div>
                <div class="stat-value">{cast_count}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Est. Runtime</div>
                <div class="stat-value">{runtime} MIN</div>
            </div>
        </div>
        
        <div class="grid">
            <div>
                <h2>Growth Opportunities</h2>
                {problems_html}
                {fixes_html}
            </div>
            
            <div>
                <h2>Narrative Strengths</h2>
                {strengths_html}
            </div>
        </div>
        
        <div style="margin: 20px 0; padding: 14px; background: #f8fafc; border: 1px solid #e2e8f0; font-size: 12px; color: #475569;">
            <strong>Important:</strong> Reference signals only — not a quality score, ranking, or approval system.
            {FULL_DISCLAIMER_HTML}
        </div>

        <div class="footer">
            <div>&copy; 2026 ScriptPulse AI Story Intelligence. For writer reflection only.</div>
            <div>Not suitable for evaluation, selection, or rejection decisions.</div>
        </div>
    </body>
    </html>
    """
    
    return html
