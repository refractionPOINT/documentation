"""Tests for verify module."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Page
from lib.verify import verify_content_completeness, verify_metadata_accuracy


def test_verify_content_completeness_passes():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )
    page.raw_html = "<html><body><h1>Test</h1><p>Content with many words to test the verification.</p><pre>code</pre></body></html>"
    page.markdown = "# Test\n\nContent with many words to test the verification.\n\n```\ncode\n```"

    issues = verify_content_completeness(page)
    critical = [i for i in issues if i.severity == "critical"]
    assert len(critical) == 0


def test_verify_metadata_invalid_keywords():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Test",
        category="test",
    )
    page.markdown = "# Test\n\nThis is about sensors and detection."
    page.metadata = {
        'keywords': ['sensors', 'detection', 'nonexistent', 'fake', 'hallucinated']
    }

    issues = verify_metadata_accuracy(page)
    keyword_issues = [i for i in issues if i.issue_type == "invalid_keyword"]
    assert len(keyword_issues) > 0
