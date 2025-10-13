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
