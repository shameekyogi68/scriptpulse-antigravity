"""
Role-Aware Access Control (RAAC)
vNext.5 Enterprise Upgrade

Defines strict permission sets for system access.
Structural protection against misuse by authority figures.
"""

from enum import Enum

class Role(Enum):
    WRITER = "writer"      # Full analysis, intent checking
    READER = "reader"      # View-only experiential output
    ADMIN = "admin"        # System health only, no content access
    RESEARCHER = "researcher" # Anonymized telemetry only

class PermissionError(Exception):
    pass

PERMISSIONS = {
    Role.WRITER: {
        'can_analyze': True,
        'can_view_reflection': True,
        'can_declare_intent': True,
        'can_view_metrics': False, # NEVER (Core philosophy)
    },
    Role.READER: {
        'can_analyze': True,
        'can_view_reflection': True,
        'can_declare_intent': False, # Readers cannot override writer intent
        'can_view_metrics': False,
    },
    Role.ADMIN: {
        'can_analyze': False, # Admins cannot read scripts
        'can_view_reflection': False,
        'can_view_telemetry': True, # System health
    },
    Role.RESEARCHER: {
        'can_analyze': False,
        'can_view_reflection': False,
        'can_view_aggregate_data': True, # Anonymized only
    }
}

def check_permission(role: Role, action: str):
    """
    Verify if a role allows a specific action.
    Raises PermissionError or returns True.
    """
    # 1. Universal Prohibitions (The "Constitution")
    if action in ['view_score', 'view_ranking', 'view_comparison', 'train_model']:
        raise PermissionError(f"Action '{action}' is UNIVERSALLY BANNED for all roles.")
        
    # 2. Role-Specific Checks
    perms = PERMISSIONS.get(role)
    if not perms:
        raise PermissionError(f"Unknown Role: {role}")
        
    if not perms.get(action, False):
        raise PermissionError(f"Role '{role.value}' denied permission for '{action}'.")
        
    return True
