"""Content verification and correctness checking."""
import re
from typing import List
from bs4 import BeautifulSoup

# Import from parent package
try:
    from ..models import Page, VerificationIssue, VerificationReport
    from ..config import Config
except ImportError:
    # Fallback for direct execution or testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page, VerificationIssue, VerificationReport
    from config import Config


def verify_content_completeness(page: Page) -> List[VerificationIssue]:
    """
    Verify markdown content is complete compared to source HTML.

    Checks:
    - Word count shouldn't drop significantly
    - All code blocks preserved
    - Heading count matches
    - Links still present
    """
    issues = []

    if not page.raw_html or not page.markdown:
        return issues

    # Parse HTML for comparison
    soup = BeautifulSoup(page.raw_html, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()

    html_text = soup.get_text()
    html_words = len(html_text.split())
    md_words = len(page.markdown.split())

    # Check word count (allow 10% loss for removed UI elements)
    if html_words > 0:
        ratio = md_words / html_words
        if ratio < 0.85:
            issues.append(VerificationIssue(
                severity="critical",
                page_slug=page.slug,
                issue_type="content_loss",
                message=f"Significant word count loss: {html_words} → {md_words} ({ratio:.1%})",
                details={'html_words': html_words, 'md_words': md_words}
            ))

    # Check code blocks
    html_code_blocks = len(soup.find_all(['pre', 'code']))
    md_code_blocks = len(re.findall(r'```', page.markdown)) // 2

    if html_code_blocks > md_code_blocks:
        issues.append(VerificationIssue(
            severity="critical",
            page_slug=page.slug,
            issue_type="missing_code_blocks",
            message=f"Missing code blocks: {html_code_blocks} in HTML, {md_code_blocks} in markdown",
            details={'html_blocks': html_code_blocks, 'md_blocks': md_code_blocks}
        ))

    # Check headings
    html_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    md_headings = len(re.findall(r'^#{1,6}\s', page.markdown, re.MULTILINE))

    if abs(html_headings - md_headings) > 2:  # Allow small variance
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="heading_mismatch",
            message=f"Heading count differs: {html_headings} in HTML, {md_headings} in markdown",
            details={'html_headings': html_headings, 'md_headings': md_headings}
        ))

    # Check links
    html_links = len(soup.find_all('a', href=True))
    md_links = len(re.findall(r'\[.+?\]\(.+?\)', page.markdown))

    if html_links > md_links + 3:  # Allow for nav links removed
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="missing_links",
            message=f"Possible missing links: {html_links} in HTML, {md_links} in markdown",
            details={'html_links': html_links, 'md_links': md_links}
        ))

    return issues


def verify_api_extraction(page: Page) -> List[VerificationIssue]:
    """
    Verify extracted APIs match source content.

    Re-parse HTML and compare against extracted api_elements.
    Flag hallucinated or missed APIs.
    """
    issues = []

    if not page.raw_html or not page.api_elements:
        return issues

    # Re-extract APIs from HTML
    soup = BeautifulSoup(page.raw_html, 'html.parser')
    code_blocks = soup.find_all(['pre', 'code'])

    html_api_patterns = set()
    for block in code_blocks:
        text = block.get_text()

        # Find REST endpoints
        endpoints = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-\{\}]+)', text, re.IGNORECASE)
        for method, path in endpoints:
            html_api_patterns.add(f"{method}:{path}")

    # Compare with extracted APIs
    extracted_patterns = set()
    for api in page.api_elements:
        if api['type'] == 'rest_endpoint':
            extracted_patterns.add(f"{api['method']}:{api['path']}")

    # Check for hallucinated APIs (in extracted but not in HTML)
    hallucinated = extracted_patterns - html_api_patterns
    if hallucinated:
        issues.append(VerificationIssue(
            severity="critical",
            page_slug=page.slug,
            issue_type="hallucinated_api",
            message=f"Extracted APIs not found in source: {hallucinated}",
            details={'hallucinated': list(hallucinated)}
        ))

    # Check for missed APIs (in HTML but not extracted)
    missed = html_api_patterns - extracted_patterns
    if missed and len(missed) > len(extracted_patterns) * 0.3:  # More than 30% missed
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="missed_api",
            message=f"Possibly missed APIs: {missed}",
            details={'missed': list(missed)}
        ))

    return issues


def verify_metadata_accuracy(page: Page) -> List[VerificationIssue]:
    """
    Verify metadata reflects actual content.

    Checks:
    - Keywords appear in content
    - Summary reflects actual content
    - Related pages exist
    """
    issues = []

    if not page.metadata:
        return issues

    content_lower = page.markdown.lower()

    # Verify keywords
    keywords = page.metadata.get('keywords', [])
    missing_keywords = []
    for keyword in keywords:
        if keyword.lower() not in content_lower:
            missing_keywords.append(keyword)

    if missing_keywords and len(missing_keywords) > len(keywords) * 0.3:
        issues.append(VerificationIssue(
            severity="warning",
            page_slug=page.slug,
            issue_type="invalid_keyword",
            message=f"Keywords not found in content: {missing_keywords}",
            details={'missing_keywords': missing_keywords}
        ))

    # Verify summary isn't empty
    summary = page.metadata.get('summary', '')
    if not summary or len(summary) < 20:
        issues.append(VerificationIssue(
            severity="info",
            page_slug=page.slug,
            issue_type="poor_summary",
            message="Summary is empty or too short",
            details={'summary': summary}
        ))

    return issues


def verify_cross_references(structure) -> List[VerificationIssue]:
    """
    Verify all cross-references point to real pages.

    Checks internal links and related_pages metadata.
    """
    issues = []

    # Build set of valid slugs
    valid_slugs = set()
    for category, pages in structure.categories.items():
        for page in pages:
            valid_slugs.add(page.slug)

    # Check each page's references
    for category, pages in structure.categories.items():
        for page in pages:
            # Check related_pages in metadata
            related = page.metadata.get('related_pages', [])
            for ref in related:
                if ref['slug'] not in valid_slugs:
                    issues.append(VerificationIssue(
                        severity="warning",
                        page_slug=page.slug,
                        issue_type="broken_reference",
                        message=f"Related page not found: {ref['slug']}",
                        details={'referenced_slug': ref['slug']}
                    ))

            # Check internal links in markdown
            internal_links = re.findall(r'\[.+?\]\((/docs/[^\)]+)\)', page.markdown)
            for link in internal_links:
                # Extract slug from link
                slug = link.replace('/docs/', '').strip('/')
                if slug and slug not in valid_slugs:
                    issues.append(VerificationIssue(
                        severity="warning",
                        page_slug=page.slug,
                        issue_type="broken_link",
                        message=f"Internal link may be broken: {link}",
                        details={'link': link}
                    ))

    return issues


def verify_all_pages(structure, config: Config) -> VerificationReport:
    """
    Run all verification checks and generate report.

    Returns VerificationReport with all issues found.
    """
    print("\nVerifying content correctness...")

    report = VerificationReport()

    for category, pages in structure.categories.items():
        for page in pages:
            report.total_pages += 1
            page_issues = []

            # Run all verification checks
            if config.verify_content:
                page_issues.extend(verify_content_completeness(page))

            if config.verify_apis:
                page_issues.extend(verify_api_extraction(page))

            if config.verify_metadata:
                page_issues.extend(verify_metadata_accuracy(page))

            # Add issues to report
            for issue in page_issues:
                report.add_issue(issue)

            # Count as passed if no critical issues
            if not any(i.severity == "critical" for i in page_issues):
                report.passed += 1

    # Check cross-references
    ref_issues = verify_cross_references(structure)
    for issue in ref_issues:
        report.add_issue(issue)

    # Print summary
    print(f"\n✓ Verified {report.total_pages} pages")
    print(f"  Passed: {report.passed}")
    print(f"  Warnings: {report.warnings}")
    print(f"  Critical: {report.critical}")

    if report.critical > 0 and config.fail_on_critical:
        print("\n✗ CRITICAL ISSUES FOUND - Pipeline halted")
        return report

    return report
