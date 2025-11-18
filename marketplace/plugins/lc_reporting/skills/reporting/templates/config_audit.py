#!/usr/bin/env python3
"""
Configuration Audit Report Template
Provides comprehensive inventory and audit of organization configuration
"""

from limacharlie import Manager
import time
import json
import os
from datetime import datetime, timezone
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader


def generate_config_audit_report(oid, output_format='html'):
    """
    Generate a configuration audit report for a LimaCharlie organization

    Args:
        oid: Organization ID
        output_format: 'html' or 'markdown' or 'json'

    Returns:
        Formatted report as string
    """
    m = Manager(oid=oid)

    print(f"Generating configuration audit report...")

    # Collect data
    data = {}

    # 1. Organization metadata
    print("Collecting organization info...")
    data['org_info'] = m.getOrgInfo()

    # 2. D&R Rules Analysis
    print("Analyzing D&R rules...")
    try:
        # m.rules() returns a list of rule names (strings)
        rule_names = list(m.rules())

        # For detailed analysis, we'd need to fetch each rule individually
        # For now, provide summary statistics
        rules_by_namespace = defaultdict(int)

        # Extract namespace from rule names (format: "namespace.rulename")
        for rule_name in rule_names:
            if '.' in rule_name:
                namespace = rule_name.split('.')[0]
            else:
                namespace = 'general'
            rules_by_namespace[namespace] += 1

        data['dr_rules'] = {
            'total': len(rule_names),
            'by_namespace': dict(sorted(rules_by_namespace.items(), key=lambda x: x[1], reverse=True)),
            'sample_rules': rule_names[:20]  # First 20 rule names
        }
    except Exception as e:
        print(f"  Error collecting D&R rules: {e}")
        data['dr_rules'] = {
            'total': 0,
            'by_namespace': {},
            'sample_rules': []
        }

    # 3. Outputs Analysis
    print("Analyzing outputs...")
    try:
        # m.outputs() returns a list of output names (strings)
        output_names = list(m.outputs())

        data['outputs'] = {
            'total': len(output_names),
            'list': output_names  # List of output names
        }
    except Exception as e:
        print(f"  Error collecting outputs: {e}")
        data['outputs'] = {
            'total': 0,
            'list': []
        }

    # 4. Tags Analysis
    print("Analyzing tags...")
    try:
        tags = list(m.getAllTags())

        # Build tag usage count efficiently (single sensor iteration)
        print("  Counting tag usage across sensors...")
        tag_counts = defaultdict(int)

        # Get all sensors once and count tags
        sensor_count = 0
        for sensor in m.sensors():
            sensor_count += 1
            if sensor_count % 100 == 0:
                print(f"    Processed {sensor_count} sensors...")
            try:
                sensor_tags = sensor.getTags()
                for tag in sensor_tags:
                    tag_counts[tag] += 1
            except:
                pass

        # Build tag list with counts
        tag_list = []
        for tag_name in tags:
            tag_list.append({
                'name': tag_name,
                'sensor_count': tag_counts.get(tag_name, 0)
            })

        # Sort by sensor count
        tag_list.sort(key=lambda x: x['sensor_count'], reverse=True)

        data['tags'] = {
            'total': len(tags),
            'list': tag_list[:30]  # Top 30 tags by usage
        }
    except Exception as e:
        print(f"  Error collecting tags: {e}")
        data['tags'] = {
            'total': 0,
            'list': []
        }

    # 5. Installation Keys Analysis
    print("Analyzing installation keys...")
    try:
        # Use get_installation_keys() (with underscore)
        installation_keys = m.get_installation_keys()

        # Returns a dict with key IDs as keys
        data['installation_keys'] = {
            'total': len(installation_keys) if isinstance(installation_keys, dict) else 0,
            'list': list(installation_keys.keys())[:20] if isinstance(installation_keys, dict) else []
        }
    except Exception as e:
        print(f"  Error collecting installation keys: {e}")
        data['installation_keys'] = {
            'total': 0,
            'list': []
        }

    # 6. API Keys Analysis
    print("Analyzing API keys...")
    try:
        # getApiKeys() returns a dict where keys are API key IDs and values are dicts
        api_keys_dict = m.getApiKeys()

        key_list = []
        for key_id, key_info in api_keys_dict.items():
            key_list.append({
                'id': key_id[:16] + '...',  # Truncate for display
                'name': key_info.get('name', 'unnamed'),
                'permissions': key_info.get('priv', [])
            })

        data['api_keys'] = {
            'total': len(api_keys_dict),
            'list': key_list
        }
    except Exception as e:
        print(f"  Error collecting API keys: {e}")
        data['api_keys'] = {
            'total': 0,
            'list': []
        }

    # 7. Users Analysis
    print("Analyzing users...")
    try:
        # getUsers() returns a list of user email addresses (strings)
        user_emails = m.getUsers()

        # Sort alphabetically
        if isinstance(user_emails, list):
            user_emails.sort()

        data['users'] = {
            'total': len(user_emails) if isinstance(user_emails, list) else 0,
            'list': user_emails if isinstance(user_emails, list) else []
        }
    except Exception as e:
        print(f"  Error collecting users: {e}")
        data['users'] = {
            'total': 0,
            'list': []
        }

    # 8. Extensions/Add-ons (if available)
    print("Checking extensions...")
    try:
        # Try to get extension/add-on information
        # This may vary based on SDK version
        org_info = data['org_info']
        extensions = []

        # Check for common extension indicators in org info
        if 'extensions' in org_info:
            extensions = org_info['extensions']

        data['extensions'] = {
            'total': len(extensions),
            'list': extensions
        }
    except Exception as e:
        print(f"  No extension data available: {e}")
        data['extensions'] = {
            'total': 0,
            'list': []
        }

    # Add metadata
    data['report_metadata'] = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'report_type': 'Configuration Audit'
    }

    # Format output
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    elif output_format == 'markdown':
        return format_markdown(data)
    else:  # html
        return render_report(data)


def format_markdown(data):
    """Format data as Markdown report"""
    md = []
    md.append("# LimaCharlie Configuration Audit Report\n")

    # Metadata
    meta = data['report_metadata']
    md.append(f"**Generated**: {meta['generated_at']}")

    # Organization
    org = data['org_info']
    md.append(f"**Organization**: {org.get('name', 'N/A')} ({org.get('oid', 'N/A')})\n")

    # D&R Rules
    rules = data['dr_rules']
    md.append("## D&R Rules")
    md.append(f"- **Total Rules**: {rules.get('total', 0)}")
    md.append(f"- **Enabled**: {rules['by_status']['enabled']}")
    md.append(f"- **Disabled**: {rules['by_status']['disabled']}")
    md.append(f"- **Rules Without Tags**: {len(rules['without_tags'])}\n")

    if rules.get('by_namespace'):
        md.append("### Rules by Namespace")
        for namespace, count in list(rules['by_namespace'].items())[:10]:
            md.append(f"- **{namespace}**: {count}")
        md.append("")

    # Outputs
    outputs = data['outputs']
    md.append("## Outputs")
    md.append(f"- **Total Outputs**: {outputs.get('total', 0)}")
    md.append(f"- **Enabled**: {outputs['by_status']['enabled']}")
    md.append(f"- **Disabled**: {outputs['by_status']['disabled']}\n")

    # Tags
    tags = data['tags']
    md.append("## Tags")
    md.append(f"- **Total Tags**: {tags.get('total', 0)}\n")

    # API Keys
    api_keys = data['api_keys']
    md.append("## API Keys")
    md.append(f"- **Total API Keys**: {api_keys.get('total', 0)}\n")

    # Users
    users = data['users']
    md.append("## Users")
    md.append(f"- **Total Users**: {users.get('total', 0)}\n")

    md.append("---")
    md.append("*Generated by LimaCharlie Reporting Skill*")

    return '\n'.join(md)


def render_report(data):
    """Render report using Jinja2 template with Chart.js"""

    # Get template directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'jinja2', 'html')

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load and render template
    template = env.get_template('config_audit.j2')
    return template.render(**data)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python config_audit.py <OID> [format]")
        print("Example: python config_audit.py 8cbe27f4-bfa1-4afb-ba19-138cd51389cd html")
        sys.exit(1)

    oid = sys.argv[1]
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'html'

    report = generate_config_audit_report(oid, fmt)

    # Determine project root and reports directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../../..'))
    reports_dir = os.path.join(project_root, 'reports')

    # Create reports directory if it doesn't exist
    os.makedirs(reports_dir, exist_ok=True)

    # Save to file
    ext = 'html' if fmt == 'html' else 'md' if fmt == 'markdown' else 'json'
    filename = f'config_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {filepath}")
