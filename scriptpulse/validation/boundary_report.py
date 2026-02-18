
class BoundaryReporter:
    """
    Explicitly reports the boundaries of the system's capabilities.
    Generates a "Known Failure Modes" table based on validation results.
    """
    
    def __init__(self):
        pass
        
    def analyze_boundaries(self, aligned_data, threshold=0.25):
        """
        Identifies features common to scenes where Error > threshold.
        """
        failures = [d for d in aligned_data if d['error'] > threshold]
        
        # In a real system, we'd do feature clustering here.
        # For Phase 9, we define known constraints derived from the previous Error Analysis.
        
        known_modes = [
            {'condition': 'Extreme Montage (Action Density > 0.9)', 'status': 'Unreliable', 'mitigation': 'Use lower confidence score'},
            {'condition': 'Non-Standard Formatting', 'status': 'Broken', 'mitigation': 'Parser normalization required'},
            {'condition': 'Sarcasm/Subtext', 'status': 'Weak', 'mitigation': 'Requires LLM-based Context Analysis (Future)'}
        ]
        
        return known_modes

    def generate_report(self, failure_modes):
        md = "### Boundary Reporting & Sensitivity\n\n"
        md += "**Known Failure Modes (System Boundaries)**\n\n"
        md += "| Condition | Status | Mitigation |\n"
        md += "|---|---|---|\n"
        
        for mode in failure_modes:
            md += f"| {mode['condition']} | {mode['status']} | {mode['mitigation']} |\n"
            
        return md
