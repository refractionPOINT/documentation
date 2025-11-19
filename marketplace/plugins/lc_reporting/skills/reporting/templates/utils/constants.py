"""
Centralized Constants for LimaCharlie Reporting
All hardcoded values should be defined here for consistency
"""

# Data Collection Limits
DEFAULT_DETECTION_LIMIT = 5000
MAX_DETECTION_LIMIT = 50000
INCIDENT_INVESTIGATION_LIMIT = 5000

# Progress Reporting
PROGRESS_REPORT_INTERVAL = 100  # Report every N items

# Time Defaults
DEFAULT_TIME_RANGE_DAYS = 7
DEFAULT_TIME_RANGE_HOURS = 24

# MITRE ATT&CK
MITRE_TOTAL_TECHNIQUES = 600  # Approximate, update periodically
MITRE_CTI_URL = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'

# Display Limits
MAX_TABLE_ROWS_BEFORE_COLLAPSE = 10
MAX_CHART_ITEMS = 10
MAX_RULE_DISPLAY = 20
MAX_TAG_DISPLAY = 30

# Severity Mappings
SEVERITY_MAP = {
    0: 'info',
    1: 'low',
    2: 'medium',
    3: 'high',
    4: 'critical'
}

SEVERITY_COLORS = {
    'info': '#17a2b8',
    'low': '#28a745',
    'medium': '#ffc107',
    'high': '#fd7e14',
    'critical': '#dc3545'
}

# Critical Detection Categories (high-risk indicators)
CRITICAL_CATEGORIES = [
    'EXFIL',
    'RANSOMWARE',
    'CRYPTOMINER',
    'EXPLOIT',
    'CREDENTIAL_ACCESS',
    'PRIVILEGE_ESCALATION',
    'LATERAL_MOVEMENT'
]

# Chart Colors (brand-consistent)
CHART_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#4F9EEE',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8'
}

# Output Formats
SUPPORTED_FORMATS = ['html', 'markdown', 'json', 'pdf']
DEFAULT_OUTPUT_FORMAT = 'html'

# File Extensions
FORMAT_EXTENSIONS = {
    'html': 'html',
    'markdown': 'md',
    'json': 'json',
    'pdf': 'pdf'
}
