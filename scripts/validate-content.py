#!/usr/bin/env python3
"""
Content Validation Script

Validates documentation content for:
- Consistent formatting
- Required sections (prerequisites, examples, see also)
- Cross-link coverage
- Code block language tags

Usage:
    python scripts/validate-content.py
    python scripts/validate-content.py --fix  # Auto-fix some issues
"""

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


class ContentValidator:
    """Validates documentation content quality."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.issues: Dict[str, List[str]] = defaultdict(list)
        self.stats = {
            'files_checked': 0,
            'files_with_issues': 0,
            'total_issues': 0,
            'files_with_examples': 0,
            'files_with_prerequisites': 0,
            'files_with_see_also': 0,
        }

    def validate_all(self) -> None:
        """Run all validations on all markdown files."""
        for md_file in self.docs_dir.rglob("*.md"):
            # Skip index files for some checks
            is_index = md_file.name == 'index.md'

            self.stats['files_checked'] += 1
            content = md_file.read_text(encoding='utf-8')
            rel_path = md_file.relative_to(self.docs_dir)

            # Run checks
            self._check_code_blocks(rel_path, content)
            self._check_headings(rel_path, content)

            if not is_index:
                self._check_examples(rel_path, content)
                self._check_prerequisites(rel_path, content)
                self._check_see_also(rel_path, content)

            self._check_broken_formatting(rel_path, content)

    def _check_code_blocks(self, path: Path, content: str) -> None:
        """Check that code blocks have language tags."""
        # Find code blocks without language
        pattern = r'^```\s*$'
        matches = re.findall(pattern, content, re.MULTILINE)

        if matches:
            self.issues[str(path)].append(
                f"Found {len(matches)} code block(s) without language tag"
            )

    def _check_headings(self, path: Path, content: str) -> None:
        """Check heading hierarchy."""
        lines = content.split('\n')
        prev_level = 0

        for i, line in enumerate(lines, 1):
            match = re.match(r'^(#{1,6})\s+', line)
            if match:
                level = len(match.group(1))

                # Check for skipped levels (e.g., h1 -> h3)
                if prev_level > 0 and level > prev_level + 1:
                    self.issues[str(path)].append(
                        f"Line {i}: Heading level skipped (h{prev_level} -> h{level})"
                    )

                prev_level = level

    def _check_examples(self, path: Path, content: str) -> None:
        """Check for example sections or code examples."""
        has_example = (
            '## Example' in content or
            '### Example' in content or
            '```yaml' in content or
            '```json' in content or
            '```python' in content or
            '```bash' in content
        )

        if has_example:
            self.stats['files_with_examples'] += 1
        else:
            # Only flag for non-reference content
            if 'reference' not in str(path).lower():
                self.issues[str(path)].append(
                    "No examples found - consider adding code samples"
                )

    def _check_prerequisites(self, path: Path, content: str) -> None:
        """Check for prerequisites section."""
        has_prereq = (
            '## Prerequisites' in content or
            '### Prerequisites' in content or
            '## Before you begin' in content or
            '!!! note' in content and 'before' in content.lower()
        )

        if has_prereq:
            self.stats['files_with_prerequisites'] += 1

    def _check_see_also(self, path: Path, content: str) -> None:
        """Check for cross-linking (See Also section)."""
        has_see_also = (
            '## See Also' in content or
            '## See also' in content or
            '### Related' in content or
            '## Related' in content
        )

        if has_see_also:
            self.stats['files_with_see_also'] += 1
        else:
            # Suggest adding cross-links
            self.issues[str(path)].append(
                "No 'See Also' section - consider adding cross-links"
            )

    def _check_broken_formatting(self, path: Path, content: str) -> None:
        """Check for common formatting issues."""
        # Unclosed bold/italic
        bold_count = content.count('**')
        if bold_count % 2 != 0:
            self.issues[str(path)].append("Unclosed bold formatting (**)")

        # Multiple blank lines
        if '\n\n\n' in content:
            self.issues[str(path)].append("Multiple consecutive blank lines")

        # Trailing whitespace in lines
        if re.search(r'[ \t]+$', content, re.MULTILINE):
            self.issues[str(path)].append("Trailing whitespace detected")

    def report(self) -> None:
        """Print validation report."""
        print("=" * 60)
        print("Documentation Content Validation Report")
        print("=" * 60)
        print()

        # Stats
        print("Statistics:")
        print(f"  Files checked: {self.stats['files_checked']}")
        print(f"  Files with examples: {self.stats['files_with_examples']}")
        print(f"  Files with prerequisites: {self.stats['files_with_prerequisites']}")
        print(f"  Files with cross-links: {self.stats['files_with_see_also']}")
        print()

        # Coverage percentages
        total = self.stats['files_checked']
        if total > 0:
            print("Coverage:")
            print(f"  Examples: {self.stats['files_with_examples']/total*100:.1f}%")
            print(f"  Prerequisites: {self.stats['files_with_prerequisites']/total*100:.1f}%")
            print(f"  Cross-links: {self.stats['files_with_see_also']/total*100:.1f}%")
        print()

        # Issues by file
        files_with_issues = {k: v for k, v in self.issues.items() if v}

        if files_with_issues:
            print(f"Issues found in {len(files_with_issues)} files:")
            print()

            # Group by severity
            critical = []
            warnings = []
            suggestions = []

            for path, issues in files_with_issues.items():
                for issue in issues:
                    if 'Unclosed' in issue or 'skipped' in issue:
                        critical.append((path, issue))
                    elif 'without language' in issue:
                        warnings.append((path, issue))
                    else:
                        suggestions.append((path, issue))

            if critical:
                print("CRITICAL (must fix):")
                for path, issue in critical[:10]:
                    print(f"  {path}: {issue}")
                print()

            if warnings:
                print("WARNINGS (should fix):")
                for path, issue in warnings[:10]:
                    print(f"  {path}: {issue}")
                print()

            if suggestions:
                print(f"SUGGESTIONS ({len(suggestions)} total, showing first 5):")
                for path, issue in suggestions[:5]:
                    print(f"  {path}: {issue}")
        else:
            print("No issues found!")

        print()
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Validate documentation content quality'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix some issues (trailing whitespace, blank lines)'
    )

    args = parser.parse_args()

    validator = ContentValidator(DOCS_DIR)
    validator.validate_all()
    validator.report()


if __name__ == '__main__':
    main()
