"""Tests for analyze module."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Page
from lib.analyze import _extract_keywords, _assess_complexity, _extract_rest_endpoints


def test_extract_keywords():
    page = Page(
        url="http://test.com",
        slug="test",
        title="Detection and Response",
        category="test",
    )
    page.markdown = """# Detection and Response

This page covers detection rules and response actions.

## Using LCQL

Query your events with LCQL."""

    keywords = _extract_keywords(page)
    assert 'detection' in keywords
    assert 'response' in keywords
    assert 'lcql' in keywords


def test_assess_complexity_beginner():
    page = Page(
        url="http://test.com",
        slug="quickstart",
        title="Quickstart",
        category="test",
    )
    page.markdown = "# Quickstart\n\nGetting started with LimaCharlie is easy."

    complexity = _assess_complexity(page)
    assert complexity == 'beginner'


def test_extract_rest_endpoints():
    content = """
GET /api/v1/orgs/{oid}/sensors
POST /api/v1/orgs/{oid}/rules
"""

    endpoints = _extract_rest_endpoints(content)
    assert len(endpoints) == 2
    assert endpoints[0]['method'] == 'GET'
    assert '/sensors' in endpoints[0]['path']
