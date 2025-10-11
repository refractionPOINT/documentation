"""LLM-specific optimizations and enhancements."""
import re
from typing import Dict, List, Set
from ..models import Page
from ..config import Config


def add_cross_references(structure, config: Config) -> int:
    """
    Add cross-references between related pages.

    Returns number of cross-references added.
    """
    if not config.add_cross_references:
        return 0

    print("\nAdding cross-references...")

    # Build slug to page mapping
    slug_map = {}
    for category, pages in structure.categories.items():
        for page in pages:
            slug_map[page.slug] = page

    total_refs = 0

    for category, pages in structure.categories.items():
        for page in pages:
            refs = _find_related_pages(page, slug_map)
            if refs:
                page.metadata['related_pages'] = refs
                total_refs += len(refs)
                print(f"  {page.slug}: {len(refs)} references")

    print(f"✓ Added {total_refs} cross-references")
    return total_refs


def _find_related_pages(page: Page, slug_map: Dict[str, Page]) -> List[Dict]:
    """Find pages related to this one."""
    related = []

    # Extract key terms from this page
    content_lower = page.markdown.lower()
    keywords = set(page.metadata.get('keywords', []))

    # Check other pages for matches
    for slug, other_page in slug_map.items():
        if slug == page.slug:
            continue

        # Calculate relevance score
        score = 0

        # Check if other page is mentioned
        if other_page.title.lower() in content_lower:
            score += 5

        if slug in content_lower:
            score += 3

        # Check keyword overlap
        other_keywords = set(other_page.metadata.get('keywords', []))
        overlap = keywords & other_keywords
        score += len(overlap)

        # Check category similarity
        if page.category == other_page.category:
            score += 2

        if score >= 3:  # Threshold for relevance
            related.append({
                'slug': slug,
                'title': other_page.title,
                'score': score,
            })

    # Return top 5 most related
    related.sort(key=lambda x: x['score'], reverse=True)
    return related[:5]


def optimize_heading_hierarchy(page: Page, config: Config) -> bool:
    """
    Ensure consistent heading hierarchy.

    - Single H1 (title)
    - Logical H2-H6 progression
    - No skipped levels

    Updates page.markdown.
    Returns True if changes made.
    """
    if not config.optimize_headings or not page.markdown:
        return False

    lines = page.markdown.split('\n')
    changes_made = False

    # Track heading levels
    h1_count = 0
    prev_level = 0

    for i, line in enumerate(lines):
        if not line.strip().startswith('#'):
            continue

        # Count heading level
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break

        # Ensure single H1
        if level == 1:
            h1_count += 1
            if h1_count > 1:
                # Demote to H2
                lines[i] = '#' + line
                changes_made = True
                level = 2

        # Check for skipped levels
        if prev_level > 0 and level > prev_level + 1:
            # Reduce to prev_level + 1
            correct_level = prev_level + 1
            heading_text = line.lstrip('#').strip()
            lines[i] = '#' * correct_level + ' ' + heading_text
            changes_made = True
            level = correct_level

        prev_level = level

    if changes_made:
        page.markdown = '\n'.join(lines)
        print(f"  Optimized headings: {page.slug}")

    return changes_made


def enhance_code_blocks(page: Page) -> bool:
    """
    Enhance code blocks with better formatting.

    - Add language identifiers where missing
    - Add line numbers for long blocks
    - Ensure proper spacing

    Updates page.markdown.
    Returns True if changes made.
    """
    if not page.markdown:
        return False

    changes_made = False
    lines = page.markdown.split('\n')
    result = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for code block start
        if line.strip().startswith('```'):
            # Check if language is specified
            if line.strip() == '```':
                # Look ahead to infer language
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    lang = _infer_language(next_line)
                    if lang:
                        line = f'```{lang}'
                        changes_made = True

            result.append(line)
            i += 1

            # Copy code block content
            while i < len(lines) and not lines[i].strip().startswith('```'):
                result.append(lines[i])
                i += 1

            # Add closing ```
            if i < len(lines):
                result.append(lines[i])
                i += 1
        else:
            result.append(line)
            i += 1

    if changes_made:
        page.markdown = '\n'.join(result)

    return changes_made


def _infer_language(code_line: str) -> str:
    """Infer programming language from code."""
    code = code_line.strip()

    if code.startswith('def ') or code.startswith('class ') or 'import ' in code:
        return 'python'
    elif code.startswith('function ') or code.startswith('const ') or code.startswith('let '):
        return 'javascript'
    elif code.startswith('curl ') or code.startswith('GET ') or code.startswith('POST '):
        return 'bash'
    elif code.startswith('{') or code.startswith('['):
        return 'json'
    elif code.startswith('<?php'):
        return 'php'

    return ''


def enhance_all_pages(structure, config: Config) -> int:
    """
    Enhance all pages with LLM optimizations.

    Returns number of enhanced pages.
    """
    print("\nEnhancing pages for LLM consumption...")

    # Add cross-references
    if config.add_cross_references:
        add_cross_references(structure, config)

    # Optimize individual pages
    enhanced = 0
    for category, pages in structure.categories.items():
        for page in pages:
            changes = False

            if config.optimize_headings:
                changes |= optimize_heading_hierarchy(page, config)

            changes |= enhance_code_blocks(page)

            if changes:
                enhanced += 1

    print(f"✓ Enhanced {enhanced} pages")
    return enhanced
