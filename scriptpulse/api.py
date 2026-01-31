"""
Production API Boundary Layer (PABL)
vNext.5 Enterprise Upgrade

The ONLY authorized entry point for ScriptPulse.
Enforces:
1. Roles (RAAC)
2. Governance (GPBL)
3. Privacy (SPIL)
4. Auditability (CLDL)
"""

import time
from . import runner, governance, roles, security

class APIContext:
    def __init__(self, tenant_id, user_role: roles.Role, user_id):
        self.tenant_id = tenant_id
        self.role = user_role
        self.user_id = user_id

class ScriptPulseAPI:
    """
    Public Facade for the ScriptPulse Engine.
    """
    
    @staticmethod
    def analyze_script(screenplay_text, context: APIContext, writer_intent=None, lens='viewer'):
        """
        Execute a single-script analysis under strict enterprise constraints.
        """
        start_time = time.time()
        
        # 1. RAAC: Permission Check
        roles.check_permission(context.role, 'can_analyze')
        
        # 2. GPBL: Policy Check (Anti-Misuse)
        governance.validate_request(screenplay_text)
        
        # 3. SPIL: Privacy Isolation (Pre-run)
        # (In a real system, we'd verify tenant encryption keys here)
        
        try:
            # 4. ENGINE: Run the Pipeline
            # This is the "Black Box" allowed step
            report = runner.run_pipeline(screenplay_text, writer_intent, lens)
            
            # 5. TWOS: Telemetry Capture (Anonymized)
            # We capture metrics BEFORE returning, but NEVER store text
            elapsed = (time.time() - start_time) * 1000
            if 'meta' in report:
                report['meta']['elapsed_ms'] = elapsed
                
            telemetry = security.AnonymousTelemetry.capture_metrics(report)
            # (Ship telemetry in background)
            
            # 6. CLDL: Compliance Log
            # Record that this was a non-decisional run
            run_id = report.get('meta', {}).get('run_id', 'unknown')
            security.ComplianceLog.log_run(run_id, context.role, "success")
            
            return report
            
        except Exception as e:
            # Failure logging
            security.ComplianceLog.log_run("failed_run", context.role, "error")
            raise e
            
        finally:
            # 7. SPIL: Memory Scrubbing
            # Ensure raw text is not lingering in frame
            # (Python strings are immutable, but we clear large containers)
            if 'screenplay_text' in locals():
                del screenplay_text
            security.scrub_memory([]) # Trigger GC
