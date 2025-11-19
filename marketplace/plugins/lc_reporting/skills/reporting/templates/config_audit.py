#!/usr/bin/env python3
"""
Configuration Audit Report Template
Provides comprehensive inventory and audit of organization configuration
"""

from limacharlie import Manager
from collections import defaultdict
from utils.base_report import BaseReport
from utils.report_helpers import progress_reporter
from utils.constants import MAX_TAG_DISPLAY
from utils.cli import simple_cli


class ConfigAuditReport(BaseReport):
    """
    Configuration audit report for organization inventory.

    Provides comprehensive audit of:
    - D&R Rules and namespace distribution
    - Outputs configuration
    - Tag inventory and usage
    - Installation keys
    - API keys and permissions
    - User accounts
    - Extensions/Add-ons
    """

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'config_audit.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'Configuration Audit Report'

    def collect_data(self):
        """
        Collect configuration audit data.

        Returns:
            Dictionary with org_info and all configuration components
        """
        m = Manager(oid=self.oid)

        print("Generating configuration audit report...")

        data = {}

        # 1. Organization metadata
        print("Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. D&R Rules Analysis
        print("Analyzing D&R rules...")
        data['dr_rules'] = self._collect_dr_rules(m)

        # 3. Outputs Analysis
        print("Analyzing outputs...")
        data['outputs'] = self._collect_outputs(m)

        # 4. Tags Analysis
        print("Analyzing tags...")
        data['tags'] = self._collect_tags(m)

        # 5. Installation Keys Analysis
        print("Analyzing installation keys...")
        data['installation_keys'] = self._collect_installation_keys(m)

        # 6. API Keys Analysis
        print("Analyzing API keys...")
        data['api_keys'] = self._collect_api_keys(m)

        # 7. Users Analysis
        print("Analyzing users...")
        data['users'] = self._collect_users(m)

        # 8. Extensions/Add-ons
        print("Checking extensions...")
        data['extensions'] = self._collect_extensions(data['org_info'])

        return data

    def _collect_dr_rules(self, manager):
        """Collect and analyze D&R rules."""
        try:
            rule_names = list(manager.rules())
            rules_by_namespace = defaultdict(int)

            # Extract namespace from rule names (format: "namespace.rulename")
            for rule_name in rule_names:
                if '.' in rule_name:
                    namespace = rule_name.split('.')[0]
                else:
                    namespace = 'general'
                rules_by_namespace[namespace] += 1

            return {
                'total': len(rule_names),
                'by_namespace': dict(sorted(rules_by_namespace.items(), key=lambda x: x[1], reverse=True)),
                'sample_rules': rule_names[:20]  # First 20 rule names
            }
        except Exception as e:
            print(f"  Error collecting D&R rules: {e}")
            return {
                'total': 0,
                'by_namespace': {},
                'sample_rules': []
            }

    def _collect_outputs(self, manager):
        """Collect outputs configuration."""
        try:
            output_names = list(manager.outputs())

            return {
                'total': len(output_names),
                'list': output_names
            }
        except Exception as e:
            print(f"  Error collecting outputs: {e}")
            return {
                'total': 0,
                'list': []
            }

    def _collect_tags(self, manager):
        """Collect tags and their usage across sensors."""
        try:
            tags = list(manager.getAllTags())

            # Build tag usage count efficiently
            print("  Counting tag usage across sensors...")
            tag_counts = defaultdict(int)
            all_sensors = list(manager.sensors())

            with progress_reporter(len(all_sensors), '  Analyzing sensors') as progress:
                for i, sensor in enumerate(all_sensors):
                    progress.update(i + 1)
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

            return {
                'total': len(tags),
                'list': tag_list[:MAX_TAG_DISPLAY]  # Top N tags by usage
            }
        except Exception as e:
            print(f"  Error collecting tags: {e}")
            return {
                'total': 0,
                'list': []
            }

    def _collect_installation_keys(self, manager):
        """Collect installation keys."""
        try:
            installation_keys = manager.get_installation_keys()

            return {
                'total': len(installation_keys) if isinstance(installation_keys, dict) else 0,
                'list': list(installation_keys.keys())[:20] if isinstance(installation_keys, dict) else []
            }
        except Exception as e:
            print(f"  Error collecting installation keys: {e}")
            return {
                'total': 0,
                'list': []
            }

    def _collect_api_keys(self, manager):
        """Collect API keys with permissions."""
        try:
            api_keys_dict = manager.getApiKeys()

            key_list = []
            for key_id, key_info in api_keys_dict.items():
                key_list.append({
                    'id': key_id[:16] + '...',  # Truncate for display
                    'name': key_info.get('name', 'unnamed'),
                    'permissions': key_info.get('priv', [])
                })

            return {
                'total': len(api_keys_dict),
                'list': key_list
            }
        except Exception as e:
            print(f"  Error collecting API keys: {e}")
            return {
                'total': 0,
                'list': []
            }

    def _collect_users(self, manager):
        """Collect user accounts."""
        try:
            user_emails = manager.getUsers()

            # Sort alphabetically
            if isinstance(user_emails, list):
                user_emails.sort()

            return {
                'total': len(user_emails) if isinstance(user_emails, list) else 0,
                'list': user_emails if isinstance(user_emails, list) else []
            }
        except Exception as e:
            print(f"  Error collecting users: {e}")
            return {
                'total': 0,
                'list': []
            }

    def _collect_extensions(self, org_info):
        """Collect extensions/add-ons information."""
        try:
            extensions = []

            # Check for common extension indicators in org info
            if 'extensions' in org_info:
                extensions = org_info['extensions']

            return {
                'total': len(extensions),
                'list': extensions
            }
        except Exception as e:
            print(f"  No extension data available: {e}")
            return {
                'total': 0,
                'list': []
            }


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        ConfigAuditReport,
        description='Generate a configuration audit report for a LimaCharlie organization',
        require_oid=True
    )
