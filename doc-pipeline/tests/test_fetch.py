"""Tests for fetch module."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.fetch import _categorize_page


def test_categorize_page_getting_started():
    assert _categorize_page("quickstart") == "01-getting-started"
    assert _categorize_page("what-is-limacharlie") == "01-getting-started"


def test_categorize_page_sensors():
    assert _categorize_page("sensor-installation") == "02-sensors"
    assert _categorize_page("agent-configuration") == "02-sensors"


def test_categorize_page_other():
    assert _categorize_page("random-page") == "12-other"
