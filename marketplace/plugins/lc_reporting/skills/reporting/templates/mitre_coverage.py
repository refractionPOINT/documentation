#!/usr/bin/env python3
"""
MITRE ATT&CK Coverage Report
Analyzes detection coverage across MITRE ATT&CK framework
"""

from limacharlie import Manager
import json
import sys
from datetime import datetime, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import os
import requests


def get_mitre_technique_names():
    """
    Fetch MITRE ATT&CK technique names from official CTI repository
    Returns dict mapping technique ID to technique name
    """
    print("Fetching MITRE ATT&CK technique descriptions...")
    try:
        url = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        techniques = {}
        for obj in data['objects']:
            if obj['type'] == 'attack-pattern':
                # Get external references to find the technique ID
                ext_refs = obj.get('external_references', [])
                for ref in ext_refs:
                    if ref.get('source_name') == 'mitre-attack':
                        tech_id = ref.get('external_id')
                        name = obj.get('name')
                        if tech_id and name:
                            techniques[tech_id] = name
                        break

        print(f"  Loaded {len(techniques)} technique descriptions")
        return techniques
    except Exception as e:
        print(f"  Warning: Could not fetch MITRE names: {e}")
        print(f"  Using generic descriptions")
        return {}


# MITRE ATT&CK Tactics (in kill chain order)
MITRE_TACTICS = {
    'TA0043': {'name': 'Reconnaissance', 'description': 'Gathering information'},
    'TA0042': {'name': 'Resource Development', 'description': 'Establishing resources'},
    'TA0001': {'name': 'Initial Access', 'description': 'Getting into your network'},
    'TA0002': {'name': 'Execution', 'description': 'Running malicious code'},
    'TA0003': {'name': 'Persistence', 'description': 'Maintaining foothold'},
    'TA0004': {'name': 'Privilege Escalation', 'description': 'Gaining higher permissions'},
    'TA0005': {'name': 'Defense Evasion', 'description': 'Avoiding detection'},
    'TA0006': {'name': 'Credential Access', 'description': 'Stealing credentials'},
    'TA0007': {'name': 'Discovery', 'description': 'Exploring environment'},
    'TA0008': {'name': 'Lateral Movement', 'description': 'Moving through environment'},
    'TA0009': {'name': 'Collection', 'description': 'Gathering data'},
    'TA0011': {'name': 'Command and Control', 'description': 'Communicating with systems'},
    'TA0010': {'name': 'Exfiltration', 'description': 'Stealing data'},
    'TA0040': {'name': 'Impact', 'description': 'Disrupting availability/integrity'}
}


def generate_mitre_coverage_report(oid, output_format='html'):
    """
    Generate MITRE ATT&CK coverage report

    Args:
        oid: Organization ID
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    print("Generating MITRE ATT&CK Coverage Report...")

    m = Manager(oid=oid)

    # Collect data
    data = {}

    # 1. Organization info
    print("Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. Fetch MITRE technique names/descriptions
    technique_names = get_mitre_technique_names()

    # 3. MITRE Coverage from LimaCharlie
    print("Fetching MITRE ATT&CK coverage...")
    mitre_report = m.getMITREReport()

    # 3. Process techniques
    covered_techniques = {}
    for technique in mitre_report.get('techniques', []):
        tid = technique['techniqueID']
        covered_techniques[tid] = {
            'enabled': technique.get('enabled', True),
            'color': technique.get('color', '#4278f5')
        }

    print(f"  Found {len(covered_techniques)} covered techniques")

    # 4. Get D&R rules for context
    print("Analyzing D&R rules...")
    try:
        rules_list = list(m.rules())
        total_rules = len(rules_list)

        # For now, we'll use the MITRE report as the source of truth
        # Rules analysis would require additional API calls per rule
        rules_with_mitre = 0  # Placeholder

        print(f"  Found {total_rules} total rules")
    except Exception as e:
        print(f"  Error collecting rules: {e}")
        total_rules = 0
        rules_with_mitre = 0

    # 5. Calculate coverage statistics by tactic
    # Note: Without full MITRE framework mapping, we'll use technique counts as proxy
    tactic_coverage = {}
    for tactic_id, tactic_info in MITRE_TACTICS.items():
        tactic_coverage[tactic_id] = {
            'name': tactic_info['name'],
            'description': tactic_info['description'],
            'covered_techniques': 0,
            'total_techniques': 0,  # Would need full MITRE framework to calculate
            'percentage': 0
        }

    # 6. Overall statistics
    total_mitre_techniques = 600  # Approximate total in Enterprise ATT&CK
    coverage_percentage = round((len(covered_techniques) / total_mitre_techniques) * 100, 1)

    data['coverage_summary'] = {
        'total_covered': len(covered_techniques),
        'total_possible': total_mitre_techniques,
        'coverage_percentage': coverage_percentage,
        'rules_with_mitre': rules_with_mitre,
        'total_rules': total_rules
    }

    # 7. Technique details - organize into base techniques and sub-techniques
    from collections import defaultdict

    base_techniques = {}
    sub_techniques = defaultdict(list)

    for tid, info in covered_techniques.items():
        if '.' in tid:
            # This is a sub-technique (e.g., T1003.001)
            base_id = tid.split('.')[0]
            sub_techniques[base_id].append({
                'id': tid,
                'name': technique_names.get(tid, 'Sub-technique'),
                'enabled': info['enabled'],
                'color': info['color']
            })
        else:
            # This is a base technique (e.g., T1003)
            base_techniques[tid] = {
                'id': tid,
                'name': technique_names.get(tid, 'MITRE ATT&CK Technique'),
                'enabled': info['enabled'],
                'color': info['color'],
                'has_subtechniques': False,
                'subtechniques': []
            }

    # Attach sub-techniques to their base techniques
    for base_id, subs in sub_techniques.items():
        if base_id in base_techniques:
            base_techniques[base_id]['has_subtechniques'] = True
            base_techniques[base_id]['subtechniques'] = sorted(subs, key=lambda x: x['id'])
        else:
            # Base technique not covered, but sub-techniques are
            # Create a placeholder base entry
            base_techniques[base_id] = {
                'id': base_id,
                'name': technique_names.get(base_id, 'MITRE ATT&CK Technique'),
                'enabled': False,
                'color': '#999',
                'has_subtechniques': True,
                'subtechniques': sorted(subs, key=lambda x: x['id']),
                'base_not_covered': True
            }

    # Convert to sorted list
    technique_hierarchy = sorted(base_techniques.values(), key=lambda x: x['id'])

    data['techniques'] = {
        'hierarchy': technique_hierarchy,
        'total': len(covered_techniques)
    }

    # 8. Tactics overview
    data['tactics'] = tactic_coverage

    # 9. Gaps and recommendations
    recommendations = []

    if coverage_percentage < 30:
        recommendations.append({
            'priority': 'high',
            'category': 'Coverage',
            'recommendation': f'Low MITRE coverage ({coverage_percentage}%). Consider expanding detection rules.'
        })
    elif coverage_percentage < 50:
        recommendations.append({
            'priority': 'medium',
            'category': 'Coverage',
            'recommendation': f'Moderate MITRE coverage ({coverage_percentage}%). Focus on high-priority tactics.'
        })
    else:
        recommendations.append({
            'priority': 'low',
            'category': 'Coverage',
            'recommendation': f'Good MITRE coverage ({coverage_percentage}%). Continue monitoring and updating.'
        })

    if total_rules > 0 and rules_with_mitre < total_rules * 0.5:
        recommendations.append({
            'priority': 'medium',
            'category': 'Tagging',
            'recommendation': 'Less than 50% of rules have MITRE tags. Improve rule tagging for better mapping.'
        })

    recommendations.append({
        'priority': 'low',
        'category': 'Maintenance',
        'recommendation': 'Regularly review MITRE ATT&CK updates and adjust detection coverage accordingly.'
    })

    data['recommendations'] = recommendations

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'report_type': 'MITRE ATT&CK Coverage'
    }

    # Format output
    if output_format == 'json':
        return format_json(data)
    elif output_format == 'markdown':
        return format_markdown(data)
    else:  # html
        return render_report(data)


def format_json(data):
    """Format as JSON"""
    return json.dumps(data, indent=2, default=str)


def format_markdown(data):
    """Format as Markdown"""
    md = []
    md.append("# MITRE ATT&CK Coverage Report\\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")

    # Organization
    org = data['org_info']
    md.append(f"**Organization**: {org.get('name', 'N/A')} ({org.get('oid', 'N/A')})\\n")

    # Coverage Summary
    summary = data['coverage_summary']
    md.append("## Coverage Summary")
    md.append(f"- **Coverage**: {summary['coverage_percentage']}% ({summary['total_covered']}/{summary['total_possible']} techniques)")
    md.append(f"- **Rules with MITRE Tags**: {summary['rules_with_mitre']}/{summary['total_rules']}\\n")

    # Covered Techniques (hierarchical view for first 30 base techniques)
    md.append("## Covered Techniques")
    md.append(f"**Total**: {data['techniques']['total']} techniques covered\\n")

    # Show first 30 base techniques with their sub-techniques
    display_count = min(30, len(data['techniques']['hierarchy']))
    for base in data['techniques']['hierarchy'][:display_count]:
        status = "✓" if base['enabled'] else "✗"
        md.append(f"- {status} **{base['id']}**")

        # Show sub-techniques if any
        if base.get('has_subtechniques') and base.get('subtechniques'):
            for sub in base['subtechniques']:
                sub_status = "✓" if sub['enabled'] else "✗"
                md.append(f"  - {sub_status} {sub['id']}")

    if len(data['techniques']['hierarchy']) > display_count:
        md.append(f"\\n... and {len(data['techniques']['hierarchy']) - display_count} more base techniques (see HTML or JSON report for complete list)\\n")
    else:
        md.append("")

    # Recommendations
    md.append("## Recommendations")
    for rec in data['recommendations']:
        md.append(f"- **[{rec['priority'].upper()}]** {rec['category']}: {rec['recommendation']}")
    md.append("")

    md.append("---")
    md.append("*Generated by LimaCharlie Reporting Framework*")

    return '\\n'.join(md)


def render_report(data):
    """Render HTML report using Jinja2 template"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'jinja2', 'html')

    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template('mitre_coverage.j2')
    return template.render(**data)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mitre_coverage.py <OID> [format]")
        print("Example: python mitre_coverage.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd html")
        sys.exit(1)

    oid = sys.argv[1]
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'html'

    report = generate_mitre_coverage_report(oid, fmt)

    # Determine output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'mitre_coverage_{timestamp}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\\n✓ Report saved to: {filepath}")
