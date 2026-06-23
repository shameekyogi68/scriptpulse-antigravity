"""
ScriptPulse Print Summary Generator
Creates a concise 1-page summary for writers to print and pin.
Styled to match the dark cinematic obsidian theme.
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
    Generate a clean, printable 1-page HTML summary in the dark theme.
    """
    
    # Extract key metrics
    trace = report_data.get('temporal_trace', [])
    try:
        avg_tension = sum(p.get('attentional_signal', 0.5) for p in trace) / len(trace) if trace else 0.5
    except Exception:
        avg_tension = 0.5
    
    wi = report_data.get('writer_intelligence', {})
    dashboard = wi.get('structural_dashboard', {})
    diagnosis = wi.get('narrative_diagnosis', [])
    priorities = wi.get('rewrite_priorities', [])
    genre = wi.get('genre_context', 'general')
    
    sp_score = dashboard.get('scriptpulse_score', 50)
    score_label = engagement_signal_label(sp_score)
    
    # Pacing and Cast
    pacing = dashboard.get('act_structure', {}).get('pacing_benchmark', 'Balanced')
    cast_count = dashboard.get('cast_count_deterministic', 0)
    
    # Runtime
    runtime_data = dashboard.get('runtime_estimate', {})
    runtime = runtime_data.get('estimated_minutes', len(trace) * 2) if isinstance(runtime_data, dict) else len(trace) * 2
    
    # Top problems (from diagnostics — red/orange items)
    problems_html = ""
    fixes_html = ""
    problem_items = [d for d in diagnosis if any(icon in d for icon in ['🔴', '🚫', '🟠', '⚠️', '✂️', '🧵', '👻', '🔵'])]
    max_problems = 2
    if priorities:
        max_problems = 2
        for i, p in enumerate(priorities[:1]): # Limit to 1 fix to guarantee one-page fit
            if isinstance(p, str):
                action, leverage = p, 'Medium'
            else:
                action = p.get('action', '')
                leverage = p.get('leverage', 'Medium')
            fixes_html = f'<div class="card problem"><b>FIX: {leverage.upper()} IMPACT</b>{_strip_md(action)}</div>'
    else:
        max_problems = 3

    if problem_items:
        for p in problem_items[:max_problems]:
            # Clean emojis and format nicely
            clean_p = p
            for emoji in ['🔴', '🚫', '🟠', '⚠️', '✂️', '🧵', '👻', '🔵']:
                clean_p = clean_p.replace(emoji, '')
            clean_p = clean_p.strip()
            
            parts = clean_p.split(':', 1)
            if len(parts) == 2:
                title_text = parts[0].replace('**', '').replace('*', '').strip()
                body_text = parts[1].strip()
                card_content = f"<b>{title_text}</b>{_strip_md(body_text)}"
            else:
                card_content = _strip_md(clean_p)
                
            problems_html += f'<div class="card problem">{card_content}</div>'
    else:
        problems_html = '<p style="font-size:11px; color: var(--text-muted); margin: 0;">No major attentional strain alerts flagged.</p>'
    
    # Strengths (from diagnostics — green items)
    strengths_html = ""
    strength_items = [d for d in diagnosis if any(icon in d for icon in ['✅', '✨', '🟢', '💎', '⭐'])]
    if strength_items:
        for s in strength_items[:3]: # Limit to 3 to guarantee one-page fit
            # Clean emojis and format nicely
            clean_s = s
            for emoji in ['✅', '✨', '🟢', '💎', '⭐']:
                clean_s = clean_s.replace(emoji, '')
            clean_s = clean_s.strip()
            
            parts = clean_s.split(':', 1)
            if len(parts) == 2:
                title_text = parts[0].replace('**', '').replace('*', '').strip()
                body_text = parts[1].strip()
                card_content = f"<b>{title_text}</b>{_strip_md(body_text)}"
            else:
                card_content = _strip_md(clean_s)
                
            strengths_html += f'<div class="card strength">{card_content}</div>'
    else:
        strengths_html = '<p style="font-size:11px; color: var(--text-muted); margin: 0;">Focus on scenes with high engagement in the full dashboard.</p>'

    # ── Act Structure html ──────────────────
    act = dashboard.get('act_structure', {})
    act_html = ""
    if act and act.get('act1_pct', 0) > 0:
        act_html = f"""
        <div class="section-compact">
            <h2>Act Structure</h2>
            <div style="display: flex; gap: 3px; height: 18px; border-radius: 4px; overflow: hidden; margin-bottom: 8px; margin-top: 8px;">
                <div style="width: {act['act1_pct']}%; background: var(--warning); display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; color: white;">I · {act['act1_pct']}%</div>
                <div style="width: {act['act2_pct']}%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; color: white;">II · {act['act2_pct']}%</div>
                <div style="width: {act['act3_pct']}%; background: var(--success); display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; color: #121212;">III · {act['act3_pct']}%</div>
            </div>
            <div style="font-size: 11px; color: var(--text-muted); line-height: 1.2;">
                Act I: {act.get('act1', 0)} · Act II: {act.get('act2', 0)} · Act III: {act.get('act3', 0)} scenes ({act.get('balance', 'N/A')})
            </div>
        </div>
        """

    # ── Dialogue vs Action html ──────────────
    dar = dashboard.get('dialogue_action_ratio', {})
    dar_html = ""
    if isinstance(dar, dict) and dar.get('global_dialogue_ratio') is not None:
        d_pct = round(dar.get('global_dialogue_ratio', 0.5) * 100)
        a_pct = 100 - d_pct
        bench = round(dar.get('genre_benchmark', 0.5) * 100) if isinstance(dar.get('genre_benchmark'), float) else dar.get('genre_benchmark', 50)
        dar_html = f"""
        <div class="section-compact">
            <h2>Dialogue vs Action</h2>
            <div style="display: flex; gap: 3px; height: 18px; border-radius: 4px; overflow: hidden; margin-bottom: 8px; margin-top: 8px;">
                <div style="width: {d_pct}%; background: #8EC5E9; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; color: #121212;">💬 {d_pct}%</div>
                <div style="width: {a_pct}%; background: var(--warning); display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; color: white;">🎬 {a_pct}%</div>
            </div>
            <div style="font-size: 11px; color: var(--text-muted); line-height: 1.2;">
                Genre: {bench - 10}%–{bench + 10}% range | Split: {d_pct}% dialogue.
            </div>
        </div>
        """

    # ── Stakes Distribution html ─────────────
    stakes_data = dashboard.get('stakes_profile', {})
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
            
            rows_html = ""
            for label, val in sorted_stakes[:3]: # Limit to top 3 for space saving
                pct = (val / total_st_scenes) * 100
                color = color_map.get(label, '#8EC5E9')
                rows_html += f"""
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <div style="width:65px; font-size:10px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.02em;">{label}</div>
                    <div style="flex:1; height:6px; border-radius:3px; background:rgba(255,255,255,0.05); position:relative;">
                        <div style="position:absolute; top:0; left:0; width:{pct:.1f}%; height:100%; border-radius:3px; background:{color};"></div>
                    </div>
                    <div style="width:75px; font-size:10px; font-weight:700; color:white; text-align:right;">
                        {val} sc ({pct:.0f}%)
                    </div>
                </div>
                """
            stakes_html = f"""
            <div class="section-compact">
                <h2>Stakes Profile</h2>
                <div style="margin-top:8px;">
                    {rows_html}
                </div>
            </div>
            """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ScriptPulse Summary — {script_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #1E1E1E;
                --accent: #9B51E0;
                --success: #00C853;
                --warning: #FF7043;
                --danger: #FF3366;
                --bg: #121212;
                --card-bg: rgba(255, 255, 255, 0.03);
                --text: #E0E0E0;
                --text-muted: #9E9E9E;
                --glass-border: rgba(255, 255, 255, 0.08);
            }}
            
            @page {{
                size: letter;
                margin: 10mm;
            }}
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                margin: 0; 
                padding: 0; 
                color: var(--text);
                background-color: var(--bg);
                line-height: 1.45;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            @media print {{
                body {{
                    zoom: 90%;
                }}
                tr, .section-compact, .card {{
                    page-break-inside: avoid;
                    break-inside: avoid;
                }}
            }}
            
            .header {{
                border-bottom: 2px solid var(--glass-border);
                padding-bottom: 10px;
                margin-bottom: 16px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }}
            .header h1 {{ margin: 0; font-family: 'Outfit', sans-serif; font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.02em; color: white; }}
            .header .date {{ font-size: 11px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }}
            
            .stats-bar {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
                margin-bottom: 16px;
            }}
            .stat {{
                background: var(--card-bg);
                border: 1px solid var(--glass-border);
                padding: 10px 8px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            }}
            .stat-label {{ font-family: 'Outfit', sans-serif; font-size: 9px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.1em; margin-bottom: 2px; }}
            .stat-value {{ font-family: 'Outfit', sans-serif; font-size: 16px; font-weight: 700; color: white; }}
            
            h2 {{ 
                font-family: 'Outfit', sans-serif;
                font-size: 11px; 
                text-transform: uppercase; 
                letter-spacing: 0.1em; 
                margin-bottom: 8px; 
                padding-left: 6px; 
                border-left: 3px solid var(--accent); 
                color: white;
                font-weight: 700;
            }}
            
            .visuals-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin-bottom: 16px;
            }}
            
            .section-compact {{
                background: var(--card-bg);
                border: 1px solid var(--glass-border);
                padding: 12px 14px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            }}
            
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
            
            .card {{ margin-bottom: 6px; padding: 8px 12px; border-radius: 6px; font-size: 12px; line-height: 1.55; }}
            .card.problem {{ background: rgba(217, 41, 135, 0.04); color: var(--text); border-left: 3px solid var(--danger); border-top: 1px solid rgba(217, 41, 135, 0.1); border-bottom: 1px solid rgba(217, 41, 135, 0.1); }}
            .card.strength {{ background: rgba(0, 200, 83, 0.04); color: var(--text); border-left: 3px solid var(--success); border-top: 1px solid rgba(0, 200, 83, 0.1); border-bottom: 1px solid rgba(0, 200, 83, 0.1); }}
            
            .card b {{ display: block; margin-bottom: 2px; text-transform: uppercase; font-size: 10px; opacity: 0.8; letter-spacing: 0.05em; }}
            
            .footer {{
                margin-top: 16px;
                padding-top: 8px;
                border-top: 1px solid var(--glass-border);
                font-size: 9px;
                color: var(--text-muted);
                display: flex;
                justify-content: space-between;
                font-family: 'JetBrains Mono', monospace;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>{script_title}</h1>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">ScriptPulse Core Intelligence Summary</div>
            </div>
            <div class="date">SP-SCORE: {sp_score}/100 ({score_label})</div>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <div class="stat-label">Engagement</div>
                <div class="stat-value">{sp_score}/100</div>
                <div style="font-size:9px;color:var(--text-muted);margin-top:2px;">{score_label}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Pacing</div>
                <div class="stat-value">{pacing}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Cast Count</div>
                <div class="stat-value">{cast_count}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Est. Runtime</div>
                <div class="stat-value">{runtime} MIN</div>
            </div>
        </div>

        <div class="visuals-grid">
            {act_html}
            {dar_html}
            {stakes_html}
        </div>
        
        <div class="grid">
            <div class="section-compact" style="background:transparent; border:none; padding:0; box-shadow:none;">
                <h2>Growth Opportunities</h2>
                {problems_html}
                {fixes_html}
            </div>
            
            <div class="section-compact" style="background:transparent; border:none; padding:0; box-shadow:none;">
                <h2>Narrative Strengths</h2>
                {strengths_html}
            </div>
        </div>
        
        <div style="margin: 16px 0 0 0; padding: 10px 14px; background: rgba(255, 51, 102, 0.02); border: 1px solid rgba(255, 51, 102, 0.15); border-radius: 6px; font-size: 10px; color: var(--text-muted); line-height: 1.45;">
            <strong>Important:</strong> Reference signals only — not a quality score, ranking, or approval system. This tool does not replace human judgment. Outputs describe first-pass audience experience signals for reflection only. Not suitable for evaluation, selection, or rejection decisions.
        </div>

        <div class="footer">
            <div>&copy; 2026 ScriptPulse AI Story Intelligence. For writer reflection only.</div>
            <div>Not suitable for evaluation decisions.</div>
        </div>
    </body>
    </html>
    """
    
    return html
