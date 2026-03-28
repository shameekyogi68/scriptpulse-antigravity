"""
ScriptPulse Writer Report Generator
====================================
Converts the full writer_intelligence output into a clean, human-readable
Markdown report that a screenwriter can print, annotate, and work from.

Usage:
    from scriptpulse.reporters.writer_report import generate_writer_report
    md = generate_writer_report(pipeline_output, title="MY SCRIPT")
    with open("my_script_report.md", "w") as f:
        f.write(md)
"""

from datetime import datetime


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
    return "*" * filled + "-" * (n - filled)


def _section(title):
    return f"\n---\n\n## {title}\n"


def generate_writer_report(pipeline_output, title="Untitled Script", genre=None):
    """
    Generate a complete Markdown writer's report from ScriptPulse pipeline output.

    Args:
        pipeline_output: dict — full output from scriptpulse.runner.run_pipeline()
        title: str — script title for the report header
        genre: str — override genre (defaults to what the pipeline detected)

    Returns:
        str — formatted Markdown report
    """
    wi = pipeline_output.get('writer_intelligence', {})
    trace = pipeline_output.get('temporal_trace', [])
    genre = (genre or wi.get('genre_context', 'general')).lower()
    dashboard = wi.get('structural_dashboard', {})
    diagnosis = wi.get('narrative_diagnosis', [])
    priorities = wi.get('rewrite_priorities', [])
    summary_data = wi.get('narrative_summary', {})

    lines = []

    # -------------------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------------------
    analysis_date = pipeline_output.get('meta', {}).get('timestamp')
    if not analysis_date:
        analysis_date = datetime.now().strftime('%B % d, %Y (%H:%M)')
        
    era = wi.get('script_era', 'contemporary').upper()
    fmt = wi.get('intended_format', 'spec').upper()
    is_ref = wi.get('is_reference', False)
    mode_str = "💎 MASTERWORK / REFERENCE MODE" if is_ref else "🛠️ PRESCRIPTIVE / DEVELOPMENT MODE"
        
    lines.append(f"# 🖋️ Script<span style='color: #0052FF;'>Pulse</span> Intelligence Report")
    lines.append(f"**PROJECT:** `{title.upper()}`")
    lines.append(f"**GENRE PROFILE:** `{genre.upper()}`")
    lines.append(f"**SCRIPT ERA:** `{era}` | **FORMAT:** `{fmt}`")
    lines.append(f"**ANALYSIS MODE:** `{mode_str}`")
    lines.append(f"**ANALYSIS DATE:** {analysis_date}")
    lines.append(f"**ENGINE VERSION:** `v15.0 Gold`  ")
    lines.append("\n" + "---" * 10 + "\n")

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    lines.append("## 📌 Executive Summary")
    if isinstance(summary_data, dict):
        summary_text = summary_data.get('summary', '')
    else:
        summary_text = str(summary_data)

    if summary_text:
        lines.append(f"{summary_text}")
    else:
        lines.append("*No narrative summary available for this analysis.*")

    # -------------------------------------------------------------------------
    # RUNTIME & FORMAT SNAPSHOT
    # -------------------------------------------------------------------------
    lines.append("\n## 📊 Script Snapshot")
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
    # SIGNAL DASHBOARD (Genre-benchmarked)
    # -------------------------------------------------------------------------
    lines.append("\n## 📈 Signal Dashboard")
    lines.append("*Biological engagement signals calibrated against **" + genre.title() + "** standards.*\n")

    if trace:
        import statistics as _stats

        def avg_signal(key, sub=None):
            vals = []
            for s in trace:
                v = s.get(key, 0.0)
                if sub:
                    v = s.get(key, {}).get(sub, 0.0) if isinstance(s.get(key), dict) else 0.0
                if isinstance(v, (int, float)):
                    vals.append(v)
            return _stats.mean(vals) if vals else 0.0

        conflict_avg = avg_signal('conflict')
        energy_avg = avg_signal('attentional_signal')
        entropy_avg = avg_signal('entropy_score')
        payoff_avg = avg_signal('payoff_density', 'payoff_density')
        sentiment_avg = avg_signal('sentiment')

        lines.append(f"| Core Signal | Intensity | Benchmark Status |")
        lines.append(f"|:------------|:----------|:-----------------|")
        lines.append(f"| **Conflict** | `{_stars(conflict_avg)}` | {_benchmark_tag(conflict_avg, genre, 'conflict')} |")
        lines.append(f"| **Energy** | `{_stars(energy_avg)}` | {_benchmark_tag(energy_avg, genre, 'energy')} |")
        lines.append(f"| **Entropy** | `{_stars(entropy_avg)}` | {_benchmark_tag(entropy_avg, genre, 'entropy')} |")
        lines.append(f"| **Payoff** | `{_stars(payoff_avg)}` | {_benchmark_tag(payoff_avg, genre, 'payoff_density')} |")
        lines.append(f"| **Sentiment** | `{_stars((sentiment_avg + 1) / 2)}` | {sentiment_avg:+.2f} *(Dark → Bright)* |")
    else:
        lines.append("*[!] No temporal data found.*")

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
            warning = beat_data.get('warning', '')
            bar = _stars(min(strength, 1.0))
            lines.append(f"- **{label}**: Scene {scene} ` {bar} ` ({strength:.2f})")
            if warning:
                lines.append(f"  > [!WARNING] {warning}")

    # -------------------------------------------------------------------------
    # SCENE HEATMAP
    # -------------------------------------------------------------------------
    if trace:
        lines.append("\n## 🌡️ Narrative Heatmap")
        lines.append("*Visual intensity flow (░ = lower, ▓ = higher):*\n")
        heatmap = ""
        for i, s in enumerate(trace):
            val = s.get('attentional_signal', 0.5)
            if val < 0.2: char = "░"
            elif val < 0.4: char = "▒"
            elif val < 0.7: char = "▓"
            else: char = "█"
            heatmap += char
            if (i + 1) % 50 == 0: heatmap += "\n"
        lines.append(f"```\n{heatmap}\n```")

    # -------------------------------------------------------------------------
    # NARRATIVE DIAGNOSIS
    # -------------------------------------------------------------------------
    lines.append("\n## 🩺 Narrative Diagnosis")
    lines.append("*Multi-dimensional structural health check:*\n")
    if diagnosis:
        for item in diagnosis:
            lines.append(f" - {item}")
    else:
        lines.append("*Status: Clear. No structural anomalies detected.*")

    # -------------------------------------------------------------------------
    # CREATIVE PROVOCATIONS
    # -------------------------------------------------------------------------
    provocations = wi.get('creative_provocations', [])
    if provocations:
        lines.append("\n## 💡 Creative Provocations")
        lines.append("*Inquiry-based perspectives on the current draft:*\n")
        for p in provocations:
            lines.append(f"> **{p}**")

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
        lines.append(f"> [!IMPORTANT]\n> Found **{low_count} Efficiency Gaps**. Narrative flow shows signs of potential deceleration in: Scenes {', '.join(str(s) for s in cut_candidates)}")
    
    if high_scenes:
        lines.append(f"🌟 **Load-Bearing Scenes:** {', '.join(str(s) for s in high_scenes[:5])}")

    econ_table = econ_map.get('map', [])
    if econ_table:
        lines.append(f"\n| Scene | Efficiency | Delta |")
        lines.append(f"|:------|:-----------|:------|")
        for e in econ_table[:10]:
            icon = "🟢" if e['label'] == 'High Economy' else ("🟡" if e['label'] == 'Moderate Economy' else "🔴")
            lines.append(f"| {e['scene']} | {icon} {e['label']} | `{e['score']}` |")
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
    lines.append("*Created with Script<span style='color: #0052FF;'>Pulse</span> v15.0 · Private Intellectual Property · Confidential*")

    return "\n".join(lines)
