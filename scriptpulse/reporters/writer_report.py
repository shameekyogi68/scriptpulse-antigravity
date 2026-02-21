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
        return f"{value:.2f} ⚠️ *(below {genre} target: {low:.2f}–{high:.2f})*"
    elif value > high:
        return f"{value:.2f} 🔴 *(above {genre} target: {low:.2f}–{high:.2f})*"
    else:
        return f"{value:.2f} ✅ *(on target: {low:.2f}–{high:.2f} for {genre})*"


def _stars(value, max_val=1.0, n=5):
    """Return a visual star bar for a 0..max_val value."""
    filled = round((value / max_val) * n)
    filled = max(0, min(n, filled))
    return "★" * filled + "☆" * (n - filled)


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
    lines.append(f"# 📋 ScriptPulse Writer's Report")
    lines.append(f"**Script:** {title.upper()}  ")
    lines.append(f"**Genre:** {genre.title()}  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}  ")
    lines.append(f"**ScriptPulse Version:** v2.0 (Phase 30)  ")

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    lines.append(_section("Executive Summary"))
    if isinstance(summary_data, dict):
        summary_text = summary_data.get('summary', '')
    else:
        summary_text = str(summary_data)

    if summary_text:
        lines.append(f"> {summary_text}")
    else:
        lines.append("> No narrative summary available.")

    # -------------------------------------------------------------------------
    # RUNTIME & FORMAT SNAPSHOT
    # -------------------------------------------------------------------------
    lines.append(_section("Script Snapshot"))
    runtime = dashboard.get('runtime_estimate', {})
    loc_profile = dashboard.get('location_profile', {})
    total_scenes = dashboard.get('total_scenes', len(trace))

    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Scenes | {total_scenes} |")
    lines.append(f"| Estimated Runtime | {runtime.get('estimated_minutes', '?')} min |")
    lines.append(f"| Runtime Status | {runtime.get('status', 'N/A')} |")
    lines.append(f"| Unique Locations | {loc_profile.get('unique_locations', '?')} |")
    lines.append(f"| INT / EXT Split | {loc_profile.get('int_scenes', 0)} INT / {loc_profile.get('ext_scenes', 0)} EXT |")

    if loc_profile.get('location_warning'):
        lines.append(f"\n> ⚠️ {loc_profile['location_warning']}")

    # -------------------------------------------------------------------------
    # SIGNAL DASHBOARD (Genre-benchmarked)
    # -------------------------------------------------------------------------
    lines.append(_section("Signal Dashboard"))
    lines.append("*All signals benchmarked against your genre. ✅ = on target, ⚠️ = below, 🔴 = above.*\n")

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

        lines.append(f"| Signal | Score | Genre Benchmark |")
        lines.append(f"|--------|-------|-----------------|")
        lines.append(f"| Conflict | {_stars(conflict_avg)} | {_benchmark_tag(conflict_avg, genre, 'conflict')} |")
        lines.append(f"| Energy | {_stars(energy_avg)} | {_benchmark_tag(energy_avg, genre, 'energy')} |")
        lines.append(f"| Information Entropy | {_stars(entropy_avg)} | {_benchmark_tag(entropy_avg, genre, 'entropy')} |")
        lines.append(f"| Payoff Density | {_stars(payoff_avg)} | {_benchmark_tag(payoff_avg, genre, 'payoff_density')} |")
        lines.append(f"| Avg Sentiment | {_stars((sentiment_avg + 1) / 2)} | {sentiment_avg:+.2f} *(−1 dark → +1 bright)* |")
    else:
        lines.append("*No trace data available.*")

    # -------------------------------------------------------------------------
    # STRUCTURAL TURNING POINTS
    # -------------------------------------------------------------------------
    lines.append(_section("Structural Turning Points"))
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
            lines.append(f"- **{label}** → Scene {scene} &nbsp; {bar} (strength: {strength:.2f})")
            if warning:
                lines.append(f"  > ⚠️ {warning}")

    # -------------------------------------------------------------------------
    # NARRATIVE DIAGNOSIS
    # -------------------------------------------------------------------------
    lines.append(_section("Narrative Diagnosis"))
    lines.append("*Issues identified across all 29 analytical dimensions:*\n")
    if diagnosis:
        for item in diagnosis:
            lines.append(f"- {item}\n")
    else:
        lines.append("*No issues detected.*")

    # -------------------------------------------------------------------------
    # REWRITE PRIORITIES
    # -------------------------------------------------------------------------
    lines.append(_section("Top Rewrite Priorities"))
    lines.append("*Ranked by impact. Address these first:*\n")
    if priorities:
        for i, item in enumerate(priorities, 1):
            lines.append(f"**{i}.** {item}\n")
    else:
        lines.append("*No rewrite priorities surfaced.*")

    # -------------------------------------------------------------------------
    # CHARACTER ARCS
    # -------------------------------------------------------------------------
    lines.append(_section("Character Arc Summary"))
    char_arcs = dashboard.get('character_arcs', {})
    if char_arcs:
        lines.append(f"| Character | Arc | Trajectory |")
        lines.append(f"|-----------|-----|------------|")
        for char, arc_data in list(char_arcs.items())[:8]:
            arc = arc_data.get('arc', 'Unknown')
            start = arc_data.get('start_agency', 0)
            end = arc_data.get('end_agency', 0)
            traj = f"{start:.2f} → {end:.2f}"
            lines.append(f"| {char} | {arc} | {traj} |")
    else:
        lines.append("*No character arc data available.*")

    # -------------------------------------------------------------------------
    # SCENE ECONOMY MAP
    # -------------------------------------------------------------------------
    lines.append(_section("Scene Economy Map"))
    econ_map = dashboard.get('scene_economy_map', {})
    cut_candidates = econ_map.get('cut_candidates', [])
    low_count = econ_map.get('low_economy_count', 0)
    high_scenes = econ_map.get('high_economy_scenes', [])

    if cut_candidates:
        lines.append(f"⚠️ **{low_count} Low Economy scene(s)** — potential cut candidates: Scenes {', '.join(str(s) for s in cut_candidates)}")
    if high_scenes:
        lines.append(f"✅ **High Economy scenes** (doing the most story work): {', '.join(str(s) for s in high_scenes[:5])}")

    econ_table = econ_map.get('map', [])
    if econ_table:
        lines.append(f"\n| Scene | Economy | Score |")
        lines.append(f"|-------|---------|-------|")
        for e in econ_table[:15]:
            icon = "🟢" if e['label'] == 'High Economy' else ("🟡" if e['label'] == 'Moderate Economy' else "🔴")
            lines.append(f"| {e['scene']} | {icon} {e['label']} | {e['score']} |")
        if len(econ_table) > 15:
            lines.append(f"| ... | *({len(econ_table) - 15} more scenes)* | ... |")

    # -------------------------------------------------------------------------
    # FORMAT COMPLIANCE
    # -------------------------------------------------------------------------
    lines.append(_section("Format Compliance"))
    fmt = dashboard.get('format_compliance', {})
    if fmt:
        issues = fmt.get('issues', [])
        score = fmt.get('compliance_score', 100)
        bar = _stars(score / 100)
        lines.append(f"**Compliance Score:** {score}/100 &nbsp; {bar}\n")
        if issues:
            for issue in issues:
                lines.append(f"- ⚠️ {issue}")
        else:
            lines.append("✅ No format issues detected.")
    else:
        lines.append("*Format compliance check not available for this script.*")

    # -------------------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------------------
    lines.append("\n---\n")
    lines.append("*Generated by ScriptPulse v2.0 · For writer use only · Not for distribution*")

    return "\n".join(lines)
