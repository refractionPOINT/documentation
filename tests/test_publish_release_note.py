"""Tests for the release-note publisher (``scripts/publish-release-note.py``).

The publisher is fed by ``repository_dispatch``, so its input is machine
supplied and only loosely trusted, and its output has to land in the one page
the feeds are generated from - in the right chronological slot, under a heading
the feed generator and the heading lint both accept. The round-trip tests below
assert exactly that: after an insert, the page still parses into entries and the
new one is canonical.
"""

import importlib.util
import os
import sys
from datetime import datetime

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(REPO_ROOT, "scripts", "publish-release-note.py")

sys.path.insert(0, os.path.join(REPO_ROOT, "hooks"))

from release_feed import classify_heading, parse_markdown_entries  # noqa: E402


def load_script(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publish = load_script(SCRIPT, "publish_release_note")

PAGE = """# Release Notes

Release notes for LimaCharlie platform components, organized by date.

## 2026-02-09

### Endpoint Agent 5.3.5

Newest.

---

## 2026-01-05

### Web App 6.1.0

Older.
"""


def insert(tmp_path, component, version, date, url="", body="", page=PAGE):
    """Insert one entry the way ``main`` does: canonicalize, then place."""
    path = tmp_path / "index.md"
    path.write_text(page, encoding="utf-8")
    publish.insert_entry(
        str(path),
        publish.canonical_component(component),
        version,
        datetime.strptime(date, "%Y-%m-%d"),
        url,
        body,
    )
    return path.read_text(encoding="utf-8")


def titles(text):
    return [(entry.date, entry.title) for entry in parse_markdown_entries(text)]


# ---------------------------------------------------------------------------
# Component canonicalization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("slug", "expected"),
    [
        ("sensor", "Endpoint Agent"),
        ("endpoint-agent", "Endpoint Agent"),
        ("web-app", "Web App"),
        ("webapp", "Web App"),
        ("cli", "CLI"),
        ("python-sdk", "SDKs"),
    ],
)
def test_component_slugs_resolve_to_canonical_headings(slug, expected):
    assert publish.canonical_component(slug) == expected


def test_an_unknown_component_is_refused(capsys):
    """Better to fail the publish than to write an entry no feed claims."""
    with pytest.raises(SystemExit) as exc:
        publish.canonical_component("mystery-service")
    assert exc.value.code == 1
    assert "Unknown component" in capsys.readouterr().err


def test_the_catch_all_bucket_cannot_be_published_directly(capsys):
    with pytest.raises(SystemExit):
        publish.canonical_component("platform")
    assert "Unknown component" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Placement
# ---------------------------------------------------------------------------


def test_an_entry_for_an_existing_date_becomes_that_day_s_first_entry(tmp_path):
    text = insert(tmp_path, "Web App", "6.2.0", "2026-02-09")
    assert titles(text) == [
        ("2026-02-09", "Web App 6.2.0"),
        ("2026-02-09", "Endpoint Agent 5.3.5"),
        ("2026-01-05", "Web App 6.1.0"),
    ]


def test_a_newer_date_goes_to_the_top(tmp_path):
    text = insert(tmp_path, "Web App", "6.2.0", "2026-03-01")
    assert titles(text)[0] == ("2026-03-01", "Web App 6.2.0")
    assert text.index("## 2026-03-01") < text.index("## 2026-02-09")


def test_an_intermediate_date_keeps_the_page_ordered(tmp_path):
    text = insert(tmp_path, "Web App", "6.2.0", "2026-01-20")
    assert [date for date, _ in titles(text)] == [
        "2026-02-09",
        "2026-01-20",
        "2026-01-05",
    ]


def test_the_oldest_date_is_appended_without_a_trailing_rule(tmp_path):
    text = insert(tmp_path, "Web App", "6.2.0", "2025-12-01")
    assert [date for date, _ in titles(text)][-1] == "2025-12-01"
    assert not text.rstrip().endswith("---")


def test_the_page_intro_is_preserved(tmp_path):
    text = insert(tmp_path, "Web App", "6.2.0", "2026-03-01")
    assert text.startswith("# Release Notes\n")
    assert "organized by date." in text


# ---------------------------------------------------------------------------
# Round trip: what is written must be readable by everything downstream
# ---------------------------------------------------------------------------


def test_the_inserted_entry_is_canonical_and_carries_its_body(tmp_path):
    body = "#### Bug Fixes\n\n- Fixed a thing."
    text = insert(
        tmp_path,
        "sensor",
        "5.4.0",
        "2026-03-01",
        url="https://github.com/refractionPOINT/example/releases/tag/v5.4.0",
        body=body,
    )
    entry = parse_markdown_entries(text)[0]

    assert entry.title == "Endpoint Agent 5.4.0"
    assert classify_heading(entry.title).is_canonical
    assert entry.categories == ("endpoint-agent",)
    assert "#### Bug Fixes" in entry.body_markdown
    assert "[GitHub Release](https://github.com/" in entry.body_markdown


def test_a_breaking_section_survives_the_insert(tmp_path):
    text = insert(
        tmp_path,
        "web-app",
        "6.2.0",
        "2026-03-01",
        body="#### Breaking Changes\n\n- A field was removed.",
    )
    assert parse_markdown_entries(text)[0].is_breaking is True


def test_two_publishes_on_the_same_day_both_survive(tmp_path):
    first = insert(tmp_path, "web-app", "6.2.0", "2026-03-01")
    second = insert(tmp_path, "sensor", "5.4.0", "2026-03-01", page=first)
    assert titles(second)[:2] == [
        ("2026-03-01", "Endpoint Agent 5.4.0"),
        ("2026-03-01", "Web App 6.2.0"),
    ]


# ---------------------------------------------------------------------------
# Untrusted input
# ---------------------------------------------------------------------------


def test_a_body_heading_that_would_forge_an_entry_is_refused(capsys):
    """A "###" in the body would create a feed item under someone else's date."""
    with pytest.raises(SystemExit) as exc:
        publish.sanitize_body("### Endpoint Agent 9.9.9\n\nNot really.")
    assert exc.value.code == 1
    assert "must not contain h1-h3 headings" in capsys.readouterr().err


def test_a_body_section_heading_is_allowed():
    assert "#### New Features" in publish.sanitize_body("#### New Features\n\n- Thing.")


def test_raw_html_in_a_body_is_neutralized():
    assert publish.sanitize_body("<script>alert(1)</script>") == (
        "&lt;script&gt;alert(1)&lt;/script&gt;"
    )


def test_a_dangerous_link_scheme_is_refused(capsys):
    with pytest.raises(SystemExit):
        publish.sanitize_body("[click](javascript:alert(1))")
    assert "Disallowed URL scheme" in capsys.readouterr().err


def test_an_off_allowlist_release_url_is_refused(capsys):
    with pytest.raises(SystemExit):
        publish.validate_url("https://evilgithub.com/x")
    assert "not in allowlist" in capsys.readouterr().err


def test_a_component_with_a_path_traversal_is_refused(capsys):
    with pytest.raises(SystemExit):
        publish.validate_inputs("../../etc/passwd", "1.0.0")
    assert "Invalid component name" in capsys.readouterr().err
