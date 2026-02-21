"""
ScriptPulse Studio Reporter (Market Professional Layer)
Gap Solved: "The Screenshot Problem"

Generates a professional "Studio Coverage" style HTML report 
that can be printed to PDF.
"""

import base64
import statistics

def generate_report(report_data, script_title="Untitled Script", user_notes=""):
    """
    Generate a standalone HTML string for the report.
    """
    
    # 1. Extract Key Metrics
    trace = report_data.get('temporal_trace', [])
    avg_effort = statistics.mean([t['attentional_signal'] for t in trace]) if trace else 0
    
    suggestions = report_data.get('suggestions', {}).get('structural_repair_strategies', [])
    
    # Recommendation Logic (Mock Logic based on Engagement)
    # If Avg Effort is between 0.4 and 0.7 -> CONSIDER
    # If Avg Effort < 0.3 (Boring) or > 0.8 (Exhausting) -> PASS
    rec = "CONSIDER"
    if avg_effort < 0.35: rec = "PASS (Low Engagement)"
    elif avg_effort > 0.75: rec = "PASS (High Strain)"
    
    # 2. Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Courier Prime', 'Courier New', monospace; line-height: 1.6; color: #333; max_width: 800px; margin: 0 auto; padding: 40px; }}
            h1, h2, h3 {{ color: #000; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 5px; }}
            .header {{ text-align: center; margin-bottom: 50px; border: 4px solid #000; padding: 20px; }}
            .verdict {{ font-size: 24px; font-weight: bold; padding: 10px; background: #eee; text-align: center; margin: 20px 0; }}
            .metric-box {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .metric {{ text-align: center; width: 30%; border: 1px solid #ccc; padding: 10px; }}
            .metric h4 {{ margin: 0; font-size: 14px; color: #666; border: none; }}
            .metric p {{ font-size: 24px; font-weight: bold; margin: 5px 0; }}
            ul {{ list-style-type: square; }}
            li {{ margin-bottom: 10px; }}
            .footer {{ margin-top: 50px; font-size: 12px; text-align: center; color: #888; border-top: 1px solid #ccc; padding-top: 20px; }}
        </style>
    </head>
    <body>
    
    <div class="header">
        <h1>SCRIPT COVERAGE</h1>
        <h2>{script_title}</h2>
        <p>Analyzed by ScriptPulse v11.0 (Gold Master)</p>
        <p>Date: Today</p>
    </div>
    
    <div class="verdict">
        RECOMMENDATION: {rec}<br>
        <span style="font-size: 14px; color: #666;">Based on Engagement {avg_effort:.2f}</span>
    </div>
    
    <!-- Executive Summary (Writer Mode) -->
    <div style="background-color: #f0f7ff; padding: 25px; border: 2px solid #005a9e; margin-bottom: 40px; border-radius: 5px;">
        <h3 style="margin-top:0; color: #005a9e; border-bottom: none;">🚀 STORY REPORT SUMMARY</h3>
        
        <div style="display: flex; gap: 20px; align-items: flex-start;">
            <div style="flex: 2;">
                <h4 style="margin: 10px 0 5px 0; color: #333;">MAIN STORY ISSUES (Top 3)</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    {''.join([f"<li style='margin-bottom:8px;'>{item}</li>" for item in report_data.get('writer_intelligence', {}).get('narrative_diagnosis', ['No major issues detected.'])])}
                </ul>
            </div>
            
            <div style="flex: 1; background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 4px;">
                <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #eee;">STORY STRUCTURE CHECK</h4>
                <div style="margin-bottom: 8px;">
                    <b>Midpoint:</b> {report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('midpoint_status', 'N/A')}
                </div>
                <div>
                    <b>Act 1 Energy:</b> {report_data.get('writer_intelligence', {}).get('structural_dashboard', {}).get('act1_energy', 'N/A')}
                </div>
            </div>
        </div>

        <h4 style="margin: 20px 0 10px 0; color: #333;">TOP WAYS TO FIX IT (High Impact)</h4>
        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
            <tr style="background:#005a9e; color:white; text-align:left;">
                <th style="padding:8px;">Action (What to do)</th>
                <th style="padding:8px; width: 100px;">Impact</th>
            </tr>
            {''.join([f"<tr><td style='border:1px solid #ccc; padding:8px;'>{edit['action']}</td><td style='border:1px solid #ccc; padding:8px;'><b>{edit['leverage']}</b></td></tr>" for edit in report_data.get('writer_intelligence', {}).get('rewrite_priorities', [])[:5]])}
        </table>
    </div>
            CONFIDENCE: {report_data.get('meta', {}).get('confidence_score', {}).get('level', 'N/A')} 
            ({int(report_data.get('meta', {}).get('confidence_score', {}).get('score', 0)*100)}%)
        </span>
    </div>
    
    {f'<div style="border: 1px dashed #666; padding: 10px; margin: 20px 0; background: #ffffcc;"><strong>READER NOTES:</strong><br>{user_notes}</div>' if user_notes else ''}
    
    <h2>1. Executive Summary</h2>
    <div class="metric-box">
        <div class="metric">
            <h4>Avg Engagement</h4>
            <p>{avg_effort:.2f}</p>
        </div>
        <div class="metric">
            <h4>Pacing Score</h4>
            <p>{len(trace)} Scenes</p>
        </div>
        <div class="metric">
            <h4>Est. Runtime</h4>
            <p>~{len(trace)*2} Mins</p>
        </div>
    </div>
    
    <p><strong>Logline Assessment:</strong> The script demonstrates a { "steady" if avg_effort < 0.5 else "fast-paced" } narrative flow. { "However, engagement lags in Act 2." if avg_effort < 0.4 else "Tension is maintained throughout." }</p>
    
    <h2>2. Key Structural Flaws</h2>
    <ul>
    """
    
    # Add Top 3 Criticisms
    for s in suggestions[:3]:
        html += f"<li><strong>{s}</strong></li>"
        
    if not suggestions:
        html += "<li>No major structural flaws detected.</li>"
        
    html += """
    </ul>
    
    <h2>3. Character Analysis (Voice Map)</h2>
    <p>Voice Distinctiveness Audit:</p>
    <ul>
    """
    
    voice = report_data.get('voice_fingerprints', {})
    for char, metrics in list(voice.items())[:5]:
        html += f"<li><strong>{char}:</strong> Complexity {metrics['complexity']}, Positivity {metrics['positivity']}</li>"
        
    html += """
    </ul>
    
    <div class="footer">
        Generated by ScriptPulse v{report_data.get('meta', {}).get('metric_version', '1.3')} - The Biometric Screenplay Instrument.<br>
        Profile: v{report_data.get('meta', {}).get('genre_profile_version', '1.0')} | Hash: {report_data.get('meta', {}).get('constants_hash', 'N/A')}
    </div>
    
    </body>
    </html>
    """
    
    return html
