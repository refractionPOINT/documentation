"""Tests for convert module."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.convert import clean_markdown_content, normalize_formatting


def test_clean_markdown_removes_metadata():
    content = """# Main Title

Updated on Jan 1, 2024
Minutes to read: 5
* Print * Share

## Actual Content

This is the real content."""

    result = clean_markdown_content(content)
    assert "Updated on" not in result
    assert "Minutes to read" not in result
    assert "Actual Content" in result


def test_normalize_formatting_adds_language():
    content = """Some text

```
def hello():
    print("world")
```"""

    result = normalize_formatting(content)
    assert "```python" in result


def test_clean_markdown_removes_feedback_forms():
    """Test that Document360 feedback forms and navigation are stripped."""
    content = """[![Logo](https://cdn.document360.io/logo/test.png)](/)

* [Home](https://example.com)
* v2

Contents x

Share this

# What is LimaCharlie?

* Updated on 13 May 2025

LimaCharlie is the **SecOps Cloud Platform**.

This is actual content that should be preserved.

Yes    No

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

Comment

Email

Cancel"""

    result = clean_markdown_content(content)

    # Should NOT contain feedback form elements
    assert "Yes    No" not in result
    assert "[ ]  Need more information" not in result
    assert "[ ]  Difficult to understand" not in result
    assert "Comment" not in result
    assert "Email" not in result
    assert "Cancel" not in result

    # Should NOT contain navigation chrome
    assert "Contents x" not in result
    assert "Share this" not in result
    assert "* [Home]" not in result
    assert "Updated on" not in result
    assert "Logo" not in result

    # Should preserve actual content
    assert "What is LimaCharlie?" in result
    assert "SecOps Cloud Platform" in result
    assert "actual content that should be preserved" in result

    # Should start with the heading (not navigation)
    assert result.strip().startswith("# What is LimaCharlie?")


def test_clean_markdown_preserves_code_blocks():
    content = """# Title

```python
def test():
    pass
```

More content."""

    result = clean_markdown_content(content)
    assert "```python" in result
    assert "def test():" in result
