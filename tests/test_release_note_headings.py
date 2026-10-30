"""Tests for the heading lint (``scripts/check-release-note-headings.py``).

The lint exists to protect two published things at once: which feed a release
lands in (component naming) and the anchor people have already linked to
(slug uniqueness). Its baseline is what lets it do that without rewriting
history, so the baseline itself is tested here too: an entry left in it that no
longer matches a real finding would silently excuse a future regression.
"""

import importlib.util
import json
import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(REPO_ROOT, "scripts", "check-release-note-headings.py")
BASELINE = os.path.join(REPO_ROOT, "scripts", "release-note-headings-baseline.json")
DOCS = os.path.join(REPO_ROOT, "docs")

sys.path.insert(0, os.path.join(REPO_ROOT, "hooks"))

from release_feed import classify_heading  # noqa: E402


def load_script(path, name):
    """Import a hyphenated script file as a module."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = load_script(SCRIPT, "check_release_note_headings")


def write_page(tmp_path, body, filename="web-app.md"):
    docs = tmp_path / "docs" / "10-release-notes"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / filename).write_text(body, encoding="utf-8")
    return str(tmp_path / "docs")


def run(docs_dir, *args):
    return check.main(["check-release-note-headings.py", "--docs", docs_dir, *args])


CANONICAL_PAGE = """# Web App Release Notes

## 2026-01-05

### Web App 6.1.0

Content.

### Web App 6.0.9

Content.

## 2025-12-01

### Web App 6.0.0

Content.
"""


def test_canonical_page_passes(tmp_path):
    assert run(write_page(tmp_path, CANONICAL_PAGE)) == 0


def test_non_canonical_component_is_reported(tmp_path, capsys):
    page = CANONICAL_PAGE.replace("### Web App 6.1.0", "### WebApp v6.1.0")
    assert run(write_page(tmp_path, page)) == 1
    out = capsys.readouterr().out
    assert "[naming]" in out
    assert "WebApp v6.1.0" in out


def test_versionless_component_heading_is_reported(tmp_path, capsys):
    page = CANONICAL_PAGE.replace("### Web App 6.0.9", "### Web App")
    assert run(write_page(tmp_path, page)) == 1
    assert "[naming]" in capsys.readouterr().out


def test_colliding_headings_are_reported(tmp_path, capsys):
    """The failure mode this exists for: a new heading stealing an old anchor."""
    page = CANONICAL_PAGE.replace("### Web App 6.0.0", "### Web App 6.1.0")
    assert run(write_page(tmp_path, page)) == 1
    out = capsys.readouterr().out
    assert out.count("[slug-collision]") == 2
    assert "#web-app-610" in out


def test_headings_inside_code_fences_are_ignored(tmp_path):
    page = CANONICAL_PAGE + """
```markdown
### Not An Entry
## not-a-date
```
"""
    assert run(write_page(tmp_path, page)) == 0


def test_entry_outside_a_date_group_is_a_structural_error(tmp_path, capsys):
    page = """# Web App Release Notes

### Web App 6.1.0

Orphaned.
"""
    assert run(write_page(tmp_path, page)) == 2
    assert "not under" in capsys.readouterr().err


def test_non_date_section_heading_is_a_structural_error(tmp_path, capsys):
    page = """# Web App Release Notes

## Highlights

### Web App 6.1.0

Content.
"""
    assert run(write_page(tmp_path, page)) == 2
    assert "date heading" in capsys.readouterr().err


def test_baseline_suppresses_known_findings_only(tmp_path):
    page = CANONICAL_PAGE.replace("### Web App 6.1.0", "### WebApp v6.1.0")
    docs = write_page(tmp_path, page)
    baseline = tmp_path / "baseline.json"

    assert run(docs, "--update-baseline", str(baseline)) == 0
    assert run(docs, "--baseline", str(baseline)) == 0

    # A second, different offender is not covered by the baseline.
    (tmp_path / "docs" / "10-release-notes" / "web-app.md").write_text(
        page.replace("### Web App 6.0.9", "### Webapp v6.0.9"),
        encoding="utf-8",
    )
    assert run(docs, "--baseline", str(baseline)) == 1


def test_repository_release_notes_pass_with_the_committed_baseline():
    assert check.main(
        ["check-release-note-headings.py", "--docs", DOCS, "--baseline", BASELINE]
    ) == 0


def test_committed_baseline_has_no_stale_entries():
    """A baseline entry with no matching finding would excuse a future one."""
    with open(BASELINE, encoding="utf-8") as handle:
        baseline = set(json.load(handle))
    findings = set(check.as_baseline_keys(check.collect(DOCS)))
    assert baseline == findings, (
        "regenerate with: python scripts/check-release-note-headings.py "
        "--update-baseline scripts/release-note-headings-baseline.json"
    )


def test_missing_release_notes_directory_is_reported(tmp_path, capsys):
    (tmp_path / "docs").mkdir()
    assert run(str(tmp_path / "docs")) == 2
    assert "not found" in capsys.readouterr().err


@pytest.mark.parametrize(
    "heading",
    [
        "### Web App 6.1.0",
        "### Adapters 1.30.11",
        "### Extensions 1.0.0",
        "### CLI 5.0.0",
        "### SDKs 5.0.0",
        "### Platform: Something newsworthy happened",
    ],
)
def test_accepted_heading_forms(tmp_path, heading):
    page = f"""# Release Notes

## 2026-01-05

{heading}

Content.
"""
    filename = classify_heading(heading[len("### "):]).page.filename
    assert run(write_page(tmp_path, page, filename)) == 0


def test_an_entry_on_another_component_s_page_is_a_structural_error(tmp_path, capsys):
    page = CANONICAL_PAGE.replace("### Web App 6.0.9", "### Endpoint Agent 5.3.5")
    assert run(write_page(tmp_path, page)) == 2
    assert "belongs on 10-release-notes/endpoint-agent.md" in capsys.readouterr().err


def test_components_without_a_page_of_their_own_share_the_platform_page(tmp_path):
    page = """# Platform, CLI & SDKs Release Notes

## 2026-01-05

### CLI 5.0.0

Content.

### SDKs 5.0.0

Content.

### Platform: Something newsworthy happened

Content.
"""
    assert run(write_page(tmp_path, page, "platform.md")) == 0


OVERVIEW = """# Release Notes

## Latest releases

<!-- release-notes:latest -->

## Subscribe

Feeds.
"""


def test_the_overview_may_have_sections_of_its_own(tmp_path):
    write_page(tmp_path, CANONICAL_PAGE)
    assert run(write_page(tmp_path, OVERVIEW, "index.md")) == 0


@pytest.mark.parametrize(
    "heading", ["## 2026-01-05", "### Web App 6.1.0", "### Highlights"]
)
def test_the_overview_holds_no_entries(tmp_path, capsys, heading):
    page = OVERVIEW.replace("## Subscribe", heading)
    assert run(write_page(tmp_path, page, "index.md")) == 2
    assert "the overview holds no release entries" in capsys.readouterr().err


def test_a_page_for_no_known_component_is_a_structural_error(tmp_path, capsys):
    assert run(write_page(tmp_path, CANONICAL_PAGE, "2025.md")) == 2
    assert "not a release notes page" in capsys.readouterr().err
