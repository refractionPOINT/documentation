"""
LimaCharlie Reporting Library

Ultra-simple library for serving HTML reports on localhost.

Usage:
    from limacharlie_reporting import create_and_serve_report

    html = "<h1>My Report</h1><p>Some content</p>"
    url = create_and_serve_report(html, title="My Report")
    print(f"Report at: {url}")
"""

from .server import get_server
from .template import wrap_html
from typing import Optional


def create_and_serve_report(
    html_content: str,
    title: str = "Report",
    filename: Optional[str] = None,
    wrap: bool = True,
    include_chart_js: bool = False
) -> str:
    """
    Create and serve an HTML report on localhost.

    Args:
        html_content: HTML content to serve
        title: Page title (used if wrap=True)
        filename: Optional custom filename
        wrap: If True, wraps content in minimal HTML template. If False, uses content as-is.
        include_chart_js: If True (and wrap=True), includes Chart.js from CDN

    Returns:
        URL where the report can be accessed (e.g., http://localhost:8080/report-abc123.html)

    Example:
        # Simple usage - let the wrapper add HTML structure
        html = "<h1>Sales Report</h1><table>...</table>"
        url = create_and_serve_report(html, title="Q4 Sales")

        # Advanced usage - provide complete HTML document
        full_html = "<!DOCTYPE html><html>...</html>"
        url = create_and_serve_report(full_html, wrap=False)
    """
    if wrap:
        html_content = wrap_html(html_content, title=title, include_chart_js=include_chart_js)

    server = get_server()
    return server.serve_html(html_content, filename=filename)


__all__ = [
    'create_and_serve_report',
    'wrap_html',
    'get_server',
]

__version__ = '2.0.0'
