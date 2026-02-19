
import os
import sys
import json
import csv
from datetime import datetime

# Import Validation Modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scriptpulse.validation.ranking_experiment import RankingExperiment
from scriptpulse.validation.inter_rater import InterRaterReliability
from scriptpulse.agents.dynamics_agent import DynamicsAgent

def run_full_validation():
    print("==========================================")
    print("      SCRIPTPULSE VALIDATION SUITE        ")
    print("      (Research Readiness Protocol)       ")
    print("==========================================")
    
    report_md = "# ScriptPulse External Validation Report\n"
    report_md += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    
    # 0. Integrity Checksum
    # ---------------------
    import hashlib
    # Hash the Genre Priors to prove version lock
    priors_path = os.path.join(os.path.dirname(__file__), 'scriptpulse/schemas/genre_priors.json')
    if os.path.exists(priors_path):
        with open(priors_path, 'rb') as f:
            config_hash = hashlib.md5(f.read()).hexdigest()[:8]
    else:
        config_hash = "UNKNOWN"
        
    report_md += f"**Engine Version**: 1.3 (Gold Master)\n"
    report_md += f"**Config Hash**: `{config_hash}`\n"
    report_md += f"**Random Seed**: 42 (Locked)\n"
    report_md += "**Status**: PRE-REGISTRATION / MOCK DATA\n\n"
    
    # 1. Blind Ranking Experiment
    # ---------------------------
    print("Running Blind Ranking Experiment...")
    # TODO: Load REAL Data here when available
    # For now, we use the Mock Data from verify_calibration.py to prove the report structure
    
    # Generate Mock Data (Same as verify_calibration.py)
    # Ideally this should be a separate loader.
    features_map = {}
    gt_ranks = {}
    rank_ptr = 1
    
    # Simple Mock: 4 scripts
    for i in range(4):
        sid = f"script_{i}"
        # Dummy features (flat structure for speed, only length matters for mocked agent?? 
        # No, actual agent runs. So we need real structure.)
        # We will skip actual generation here and Mock the RESULT structure if we lack data.
        # But for the report to be meaningful, let's assume we pass in a result object or run a tiny test.
        pass
        
    # Since we don't have real data, we will output a TEMPLATE report section
    # declaring the protocols.
    report_md += "## 1. Blind Ranking Experiment\n"
    report_md += "> **Protocol**: Spearman Rank Correlation ($\rho$) on N scripts.\n"
    report_md += "> **Pre-Registered Criteria**: $\rho > 0.5$ and $p < 0.05$.\n\n"
    report_md += "*(Awaiting Real Corpus Data)*\n\n"
    
    # 2. Inter-Rater Reliability
    # --------------------------
    print("Checking Inter-Rater Reliability Tools...")
    report_md += "## 2. Inter-Rater Reliability\n"
    report_md += "> **Protocol**: Krippendorff's $\alpha$ on Human Annotations.\n"
    report_md += "> **Pre-Registered Criteria**: $\alpha > 0.7$.\n\n"
    try:
        import krippendorff
        report_md += "✅ Tooling: `krippendorff` library detected.\n"
    except ImportError:
        report_md += "⚠️ Tooling: `krippendorff` library MISSING.\n"
        
    report_md += "\n"
    
    # 3. Error Analysis Definition
    # ----------------------------
    report_md += "## 3. Error Analysis Protocol\n"
    report_md += "The following failure cases will be reported for every validation run:\n"
    report_md += "1.  **Top 3 Disagreements**: Scripts with highest $|Rank_{sys} - Rank_{human}|$.\n"
    report_md += "2.  **Mean Absolute Rank Error (MARE)**: Global accuracy metric.\n"
    report_md += "3.  **CI Reporting**: 95% Bootstrap Confidence Intervals for all metrics.\n"
    
    # Write to File
    with open('VALIDATION_SUMMARY.md', 'w') as f:
        f.write(report_md)
        
    print("Report generated: VALIDATION_SUMMARY.md")

if __name__ == "__main__":
    run_full_validation()
