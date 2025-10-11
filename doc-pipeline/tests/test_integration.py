"""Integration tests for full pipeline."""
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_pipeline_dry_run():
    """Test that pipeline can discover structure."""
    from lib import fetch
    from config import Config

    config = Config()
    structure = fetch.discover_documentation_structure(config)

    assert structure is not None
    assert len(structure.categories) > 0

    total_pages = sum(len(pages) for pages in structure.categories.values())
    assert total_pages > 0

    print(f"Discovered {total_pages} pages in {len(structure.categories)} categories")


def test_pipeline_phases_independent():
    """Test that each phase can run independently."""
    from models import Page, DocumentStructure
    from lib import convert, analyze, enhance
    from config import Config

    config = Config()

    # Create minimal test page
    page = Page(
        url="http://test.com",
        slug="test-page",
        title="Test Page",
        category="test",
        raw_html="<html><body><h1>Test</h1><p>Content</p><pre>code</pre></body></html>",
    )

    structure = DocumentStructure()
    structure.categories["test"] = [page]

    # Test convert phase
    assert convert.convert_page(page, config)
    assert page.markdown != ""

    # Test analyze phase
    metadata = analyze.extract_metadata(page, config)
    assert metadata is not None

    # Test enhance phase
    enhance.optimize_heading_hierarchy(page, config)
    assert page.markdown.startswith("# ")


def test_verification_catches_issues():
    """Test that verification catches problems."""
    from models import Page
    from lib.verify import verify_content_completeness

    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )

    # Simulate content loss
    page.raw_html = "<html><body>" + "word " * 100 + "</body></html>"
    page.markdown = "# Test\n\nOnly a few words"

    issues = verify_content_completeness(page)
    critical = [i for i in issues if i.severity == "critical"]

    assert len(critical) > 0
    assert any("content_loss" in i.issue_type for i in critical)
