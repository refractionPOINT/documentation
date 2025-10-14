#!/usr/bin/env python3
"""
Phase 7: Validation & Quality Checks

Validates synthesized topics for:
- Topic coherence (single focused topic per file)
- No mega-files (files that are too large/unfocused)
- Comprehensive coverage (all cleaned docs represented)
- Technical depth preservation
- Self-containment (no broken references)
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import config
import utils


class TopicValidator:
    """Validates synthesized documentation topics."""

    def __init__(self):
        self.topics_dir = config.TOPICS_DIR
        self.cleaned_dir = config.CLEANED_MARKDOWN_DIR
        self.metadata_dir = config.METADATA_DIR

        self.issues = []
        self.warnings = []
        self.stats = {}

    def load_all_topics(self) -> Dict[str, str]:
        """Load all synthesized topic files."""
        topics = {}

        for category in ['tasks', 'concepts', 'reference']:
            category_dir = self.topics_dir / category
            if not category_dir.exists():
                continue

            for file_path in category_dir.glob("*.md"):
                topic_key = f"{category}/{file_path.stem}"
                try:
                    content = file_path.read_text(encoding='utf-8')
                    topics[topic_key] = content
                except Exception as e:
                    self.issues.append(f"Failed to read {topic_key}: {e}")

        return topics

    def check_topic_coherence(self, topic_key: str, content: str) -> List[str]:
        """
        Check if a topic file contains coherent, related content.

        Returns list of issues found.
        """
        issues = []

        # Count top-level headings (# Title)
        h1_headings = re.findall(r'^# (.+)$', content, re.MULTILINE)

        if len(h1_headings) > 3:
            issues.append(
                f"Multiple topics merged in '{topic_key}': {len(h1_headings)} h1 headings found. "
                f"Topics: {', '.join(h1_headings[:5])}"
            )

        # Check for unrelated topic indicators
        # If we see multiple very different topics, flag it
        topics_mentioned = set()
        topic_indicators = [
            'BinLib', 'Enterprise SOC', 'LCQL', 'Query Language',
            'Detection Rules', 'Adapter', 'Agent', 'Sensor',
            'API', 'SDK', 'CLI', 'Hive', 'Output', 'Extension'
        ]

        for indicator in topic_indicators:
            if indicator.lower() in content[:2000].lower():
                topics_mentioned.add(indicator)

        if len(topics_mentioned) > 4:
            issues.append(
                f"Possible topic mixing in '{topic_key}': {len(topics_mentioned)} different topics detected"
            )

        return issues

    def check_mega_files(self, topic_key: str, content: str) -> List[str]:
        """Check for excessively large files that likely contain merged content."""
        issues = []

        lines = content.count('\n')
        words = len(content.split())

        # Flag files that are suspiciously large
        if lines > 500:
            issues.append(
                f"Mega-file detected '{topic_key}': {lines} lines ({words} words). "
                f"Consider splitting into separate topics."
            )
        elif lines > 300:
            self.warnings.append(
                f"Large file '{topic_key}': {lines} lines. Verify it's a single coherent topic."
            )

        return issues

    def check_technical_depth(self, topic_key: str, content: str) -> List[str]:
        """Check that technical details are preserved."""
        issues = []

        # Look for indicators of technical content
        has_code = bool(re.search(r'```', content))
        has_commands = bool(re.search(r'`[\w-]+\s+[\w-]+`', content))
        has_params = bool(re.search(r'`[A-Z_]+`|`\w+:`', content))
        has_examples = bool(re.search(r'example|sample', content, re.I))

        # Check for vague language
        vague_phrases = [
            'for more information', 'see documentation', 'refer to',
            'click here', 'various', 'multiple options'
        ]
        vague_count = sum(1 for phrase in vague_phrases if phrase in content.lower())

        if vague_count > 5:
            issues.append(
                f"Vague content in '{topic_key}': {vague_count} vague phrases detected"
            )

        # Technical docs should have specific details
        if not (has_code or has_commands or has_params):
            if len(content) > 1000:  # Only flag longer docs
                self.warnings.append(
                    f"Possibly shallow content in '{topic_key}': no code examples or commands found"
                )

        return issues

    def check_self_containment(self, topic_key: str, content: str) -> List[str]:
        """Check that topics are self-contained."""
        issues = []

        # Look for references that might indicate incomplete content
        problematic_refs = [
            r'see (the )?\[.*?\]\(.*?\) for',
            r'refer to (the )?\[.*?\]',
            r'described in \[.*?\]',
            r'for more information, see',
            r'click here for'
        ]

        for pattern in problematic_refs:
            matches = re.findall(pattern, content, re.I)
            if len(matches) > 3:
                issues.append(
                    f"Non-self-contained content in '{topic_key}': {len(matches)} external references"
                )
                break

        return issues

    def check_coverage(self, topics: Dict[str, str]) -> List[str]:
        """Check that all cleaned docs are represented in topics."""
        issues = []

        # Load cleaned docs
        cleaned_docs = set()
        if self.cleaned_dir.exists():
            for file_path in self.cleaned_dir.glob("*.md"):
                cleaned_docs.add(file_path.stem)

        # Load synthesis metadata to see which docs were included
        synthesis_metadata_path = self.metadata_dir / "synthesis_results.json"
        if synthesis_metadata_path.exists():
            metadata = utils.load_json(synthesis_metadata_path)

            # Collect all source slugs
            included_slugs = set()
            for category in ['tasks', 'concepts', 'reference']:
                for topic_info in metadata.get(category, []):
                    included_slugs.update(topic_info.get('source_slugs', []))

            # Find missing docs
            missing = cleaned_docs - included_slugs
            if missing:
                issues.append(
                    f"Missing {len(missing)} cleaned docs in topics: {list(missing)[:10]}..."
                )

        return issues

    def generate_topic_map(self, topics: Dict[str, str]) -> Dict[str, any]:
        """Generate a topic map for LLM retrieval."""
        topic_map = {}

        for topic_key, content in topics.items():
            # Extract metadata
            lines = content.split('\n')
            title = topic_key
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            # Get first paragraph
            description = ""
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    description = line.strip()[:200]
                    break

            # Count content
            word_count = len(content.split())
            has_code = bool(re.search(r'```', content))

            topic_map[topic_key] = {
                'title': title,
                'description': description,
                'word_count': word_count,
                'has_code_examples': has_code,
                'file_path': f"output/topics/{topic_key}.md"
            }

        return topic_map

    def validate_all(self) -> Dict:
        """Run all validation checks."""
        utils.log("="*60)
        utils.log("Phase 7: Topic Validation")
        utils.log("="*60)

        # Load all topics
        utils.log("Loading synthesized topics...")
        topics = self.load_all_topics()
        utils.log_success(f"Loaded {len(topics)} topics")

        if not topics:
            utils.log_error("No topics found to validate")
            return {'success': False, 'error': 'No topics found'}

        # Run validation checks
        utils.log("\nRunning validation checks...")

        for topic_key, content in topics.items():
            # Check coherence
            issues = self.check_topic_coherence(topic_key, content)
            self.issues.extend(issues)

            # Check for mega-files
            issues = self.check_mega_files(topic_key, content)
            self.issues.extend(issues)

            # Check technical depth
            issues = self.check_technical_depth(topic_key, content)
            self.issues.extend(issues)

            # Check self-containment
            issues = self.check_self_containment(topic_key, content)
            self.issues.extend(issues)

        # Check coverage
        coverage_issues = self.check_coverage(topics)
        self.issues.extend(coverage_issues)

        # Generate topic map
        utils.log("\nGenerating topic map for LLM retrieval...")
        topic_map = self.generate_topic_map(topics)
        topic_map_path = self.metadata_dir / "topic_map.json"
        utils.save_json(topic_map, topic_map_path)
        utils.log_success(f"Topic map saved to {topic_map_path}")

        # Compile statistics
        self.stats = {
            'total_topics': len(topics),
            'total_issues': len(self.issues),
            'total_warnings': len(self.warnings),
            'topics_by_category': {
                'tasks': len([k for k in topics if k.startswith('tasks/')]),
                'concepts': len([k for k in topics if k.startswith('concepts/')]),
                'reference': len([k for k in topics if k.startswith('reference/')])
            }
        }

        # Save validation report
        report = {
            'stats': self.stats,
            'issues': self.issues,
            'warnings': self.warnings,
            'topic_map': topic_map
        }
        report_path = self.metadata_dir / "validation_report.json"
        utils.save_json(report, report_path)

        # Print results
        utils.log("\n" + "="*60)
        utils.log("Validation Results")
        utils.log("="*60)

        utils.log(f"Total topics: {self.stats['total_topics']}")
        utils.log(f"  - Tasks: {self.stats['topics_by_category']['tasks']}")
        utils.log(f"  - Concepts: {self.stats['topics_by_category']['concepts']}")
        utils.log(f"  - Reference: {self.stats['topics_by_category']['reference']}")
        utils.log("")

        if self.issues:
            utils.log_error(f"Found {len(self.issues)} issues:")
            for issue in self.issues[:10]:  # Show first 10
                utils.log_error(f"  - {issue}")
            if len(self.issues) > 10:
                utils.log_error(f"  ... and {len(self.issues) - 10} more")
        else:
            utils.log_success("No critical issues found!")

        if self.warnings:
            utils.log_warning(f"\nFound {len(self.warnings)} warnings:")
            for warning in self.warnings[:5]:
                utils.log_warning(f"  - {warning}")
            if len(self.warnings) > 5:
                utils.log_warning(f"  ... and {len(self.warnings) - 5} more")

        utils.log(f"\nValidation report saved to: {report_path}")
        utils.log("="*60)

        return {
            'success': len(self.issues) == 0,
            'stats': self.stats,
            'issues': self.issues,
            'warnings': self.warnings
        }


def main():
    """Run validation."""
    validator = TopicValidator()
    results = validator.validate_all()

    if not results['success']:
        utils.log_error(f"\nValidation failed with {len(results['issues'])} issues")
        return 1

    utils.log_success("\n✓ Validation passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
