#!/usr/bin/env python3
"""
MITRE ATT&CK Coverage Report
Analyzes detection coverage across MITRE ATT&CK framework
"""

from limacharlie import Manager
from collections import defaultdict
import requests
from utils.base_report import BaseReport
from utils.constants import MITRE_CTI_URL, MITRE_TOTAL_TECHNIQUES
from utils.cli import simple_cli


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


class MITRECoverageReport(BaseReport):
    """
    MITRE ATT&CK coverage analysis report.

    Provides comprehensive MITRE coverage including:
    - Covered vs uncovered techniques
    - Coverage by tactic
    - Rule-to-technique mapping
    - Coverage percentage and gaps
    - Technique descriptions from MITRE CTI
    """

    def get_template_name(self):
        """Return Jinja2 template name."""
        return 'mitre_coverage.j2'

    def get_report_type(self):
        """Return report type name."""
        return 'MITRE ATT&CK Coverage Report'

    def collect_data(self):
        """
        Collect MITRE ATT&CK coverage data.

        Returns:
            Dictionary with coverage stats, techniques, and tactics
        """
        print("Generating MITRE ATT&CK Coverage Report...")

        m = Manager(oid=self.oid)

        data = {}

        # 1. Organization info
        print("Collecting organization info...")
        data['org_info'] = m.getOrgInfo()

        # 2. Fetch MITRE technique names/descriptions
        technique_names = self._fetch_mitre_technique_names()

        # 3. Get MITRE coverage from LimaCharlie
        print("Fetching MITRE ATT&CK coverage...")
        mitre_report = m.getMITREReport()

        # 4. Process coverage data
        data['mitre_coverage'] = self._process_coverage(mitre_report, technique_names)

        # 5. Add tactics information
        data['mitre_tactics'] = MITRE_TACTICS

        return data

    def _fetch_mitre_technique_names(self):
        """Fetch MITRE ATT&CK technique names from official CTI repository."""
        print("Fetching MITRE ATT&CK technique descriptions...")
        try:
            response = requests.get(MITRE_CTI_URL, timeout=10)
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

    def _process_coverage(self, mitre_report, technique_names):
        """Process MITRE coverage report data."""
        # Process covered techniques
        covered_techniques = {}
        for technique in mitre_report.get('techniques', []):
            tech_id = technique.get('techniqueID')
            if tech_id:
                covered_techniques[tech_id] = {
                    'id': tech_id,
                    'name': technique_names.get(tech_id, 'Unknown Technique'),
                    'tactics': technique.get('tactics', []),
                    'rules': technique.get('rulesUsed', [])
                }

        # Calculate coverage by tactic
        coverage_by_tactic = defaultdict(lambda: {'covered': 0, 'total': 0})

        for technique in mitre_report.get('techniques', []):
            for tactic_id in technique.get('tactics', []):
                if tactic_id in MITRE_TACTICS:
                    coverage_by_tactic[tactic_id]['covered'] += 1

        # Total techniques count (approximate - MITRE has ~600 techniques)
        total_techniques = MITRE_TOTAL_TECHNIQUES
        covered_count = len(covered_techniques)
        coverage_percentage = round((covered_count / total_techniques) * 100, 1)

        # Identify coverage gaps (tactics with low coverage)
        coverage_gaps = []
        for tactic_id, tactic_info in MITRE_TACTICS.items():
            tactic_coverage = coverage_by_tactic.get(tactic_id, {'covered': 0, 'total': 0})
            if tactic_coverage['covered'] < 5:  # Less than 5 techniques covered
                coverage_gaps.append({
                    'tactic': tactic_info['name'],
                    'tactic_id': tactic_id,
                    'techniques_covered': tactic_coverage['covered']
                })

        # Get top covered tactics
        top_tactics = sorted(
            [(tactic_id, stats['covered']) for tactic_id, stats in coverage_by_tactic.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        top_tactics_list = [
            {
                'tactic': MITRE_TACTICS[tactic_id]['name'],
                'tactic_id': tactic_id,
                'techniques_covered': count
            }
            for tactic_id, count in top_tactics
        ]

        return {
            'total_techniques': total_techniques,
            'covered_count': covered_count,
            'uncovered_count': total_techniques - covered_count,
            'coverage_percentage': coverage_percentage,
            'covered_techniques': dict(sorted(covered_techniques.items())),
            'coverage_by_tactic': dict(coverage_by_tactic),
            'coverage_gaps': coverage_gaps,
            'top_tactics': top_tactics_list,
            'total_rules': sum(len(t['rules']) for t in covered_techniques.values())
        }


# CLI Entry Point
if __name__ == '__main__':
    simple_cli(
        MITRECoverageReport,
        description='Generate MITRE ATT&CK coverage analysis report',
        require_oid=True
    )
