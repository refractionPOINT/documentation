"""Git-based change detection and reporting."""
import subprocess
from typing import Dict, List, Tuple
from pathlib import Path
from ..config import Config


def commit_changes(output_dir: Path, config: Config) -> bool:
    """
    Commit generated documentation to git.

    Returns True if committed successfully.
    """
    if not config.git_commit_changes:
        print("\nSkipping git commit (disabled in config)")
        return False

    try:
        # Stage all changes in output directory
        subprocess.run(
            ['git', 'add', str(output_dir)],
            check=True,
            capture_output=True
        )

        # Check if there are changes to commit
        status = subprocess.run(
            ['git', 'status', '--porcelain', str(output_dir)],
            capture_output=True,
            text=True,
            check=True
        )

        if not status.stdout.strip():
            print("\nNo changes to commit")
            return False

        # Commit
        subprocess.run(
            ['git', 'commit', '-m', config.git_commit_message],
            check=True,
            capture_output=True
        )

        print(f"\n✓ Committed changes: {config.git_commit_message}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Git commit failed: {e}")
        return False


def generate_change_report(output_dir: Path, config: Config) -> Dict:
    """
    Generate report of changes from git diff.

    Returns dictionary with:
    - structural_changes: Added/removed files
    - content_changes: Modified files with details
    - significant_changes: Major changes requiring review
    """
    report = {
        'structural_changes': {
            'added': [],
            'removed': [],
        },
        'content_changes': [],
        'significant_changes': [],
        'total_files_changed': 0,
    }

    try:
        # Get diff stats
        diff_stats = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--numstat', '--', str(output_dir)],
            capture_output=True,
            text=True,
            check=True
        )

        for line in diff_stats.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) != 3:
                continue

            added, removed, filepath = parts

            # Skip if binary or no changes
            if added == '-' or removed == '-':
                continue

            report['total_files_changed'] += 1

            # Categorize change
            change_info = {
                'file': filepath,
                'lines_added': int(added),
                'lines_removed': int(removed),
            }

            # Check for structural changes
            if int(added) > 0 and int(removed) == 0:
                report['structural_changes']['added'].append(filepath)
            elif int(removed) > 0 and int(added) == 0:
                report['structural_changes']['removed'].append(filepath)
            else:
                report['content_changes'].append(change_info)

            # Flag significant changes (large diffs)
            if int(added) + int(removed) > 100:
                report['significant_changes'].append(change_info)

        # Get detailed diff for significant changes
        for change in report['significant_changes']:
            diff_detail = subprocess.run(
                ['git', 'diff', 'HEAD~1', 'HEAD', '--', change['file']],
                capture_output=True,
                text=True,
                check=True
            )
            change['diff'] = _summarize_diff(diff_detail.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not generate git diff: {e}")
        report['error'] = str(e)

    return report


def _summarize_diff(diff: str) -> Dict:
    """Summarize a git diff into key changes."""
    summary = {
        'added_sections': [],
        'removed_sections': [],
        'modified_headings': [],
    }

    lines = diff.split('\n')
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            # Added line
            text = line[1:].strip()
            if text.startswith('#'):
                summary['added_sections'].append(text)
        elif line.startswith('-') and not line.startswith('---'):
            # Removed line
            text = line[1:].strip()
            if text.startswith('#'):
                summary['removed_sections'].append(text)

    return summary


def categorize_changes(report: Dict) -> Dict:
    """
    Categorize changes into types.

    Returns categories:
    - structural: New/removed pages
    - significant_content: Major updates
    - minor_content: Small edits
    - noise: Timestamps, formatting
    """
    categories = {
        'structural': {
            'count': len(report['structural_changes']['added']) +
                     len(report['structural_changes']['removed']),
            'details': report['structural_changes'],
        },
        'significant_content': {
            'count': len(report['significant_changes']),
            'details': report['significant_changes'],
        },
        'minor_content': {
            'count': len(report['content_changes']) - len(report['significant_changes']),
            'details': [c for c in report['content_changes']
                       if c not in report['significant_changes']],
        },
    }

    return categories


def print_change_report(report: Dict, categories: Dict):
    """Print human-readable change report."""
    print("\n" + "="*60)
    print("DOCUMENTATION CHANGE REPORT")
    print("="*60)

    print(f"\nTotal files changed: {report['total_files_changed']}")

    # Structural changes
    if categories['structural']['count'] > 0:
        print(f"\n📁 STRUCTURAL CHANGES ({categories['structural']['count']})")
        added = report['structural_changes']['added']
        removed = report['structural_changes']['removed']

        if added:
            print(f"\n  Added ({len(added)}):")
            for file in added[:10]:  # Show first 10
                print(f"    + {file}")
            if len(added) > 10:
                print(f"    ... and {len(added) - 10} more")

        if removed:
            print(f"\n  Removed ({len(removed)}):")
            for file in removed[:10]:
                print(f"    - {file}")
            if len(removed) > 10:
                print(f"    ... and {len(removed) - 10} more")

    # Significant changes
    if categories['significant_content']['count'] > 0:
        print(f"\n⚠️  SIGNIFICANT CONTENT CHANGES ({categories['significant_content']['count']})")
        print("\n  These pages have major updates requiring review:\n")

        for change in report['significant_changes'][:5]:  # Show first 5
            print(f"    {change['file']}")
            print(f"      +{change['lines_added']} -{change['lines_removed']} lines")

            if 'diff' in change:
                if change['diff'].get('added_sections'):
                    print(f"      Added: {len(change['diff']['added_sections'])} sections")
                if change['diff'].get('removed_sections'):
                    print(f"      Removed: {len(change['diff']['removed_sections'])} sections")
            print()

        if len(report['significant_changes']) > 5:
            print(f"    ... and {len(report['significant_changes']) - 5} more")

    # Minor changes
    if categories['minor_content']['count'] > 0:
        print(f"\n📝 Minor content changes: {categories['minor_content']['count']} files")

    print("\n" + "="*60)


def detect_and_report(output_dir: Path, config: Config) -> Dict:
    """
    Full change detection workflow.

    1. Commit changes to git
    2. Generate change report
    3. Categorize changes
    4. Print report

    Returns full report dictionary.
    """
    print("\n" + "="*60)
    print("CHANGE DETECTION")
    print("="*60)

    # Commit changes
    committed = commit_changes(output_dir, config)

    if not committed:
        print("\nNo changes detected or commit failed")
        return {}

    # Generate report
    report = generate_change_report(output_dir, config)

    if report.get('error'):
        print(f"\nError generating report: {report['error']}")
        return report

    # Categorize and print
    categories = categorize_changes(report)
    print_change_report(report, categories)

    return report
