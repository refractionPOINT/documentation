"""Tests for the llms.txt hook: pages with a front-matter description list it."""

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, "hooks"))

from llms_txt import render  # noqa: E402

SITE_URL = "https://docs.limacharlie.io/"


def _render(tmp_path, pages):
    for rel, body in pages.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    nav = [{"Guides": [{label: rel} for label, rel in (
        ("Plain", "plain.md"),
        ("Described", "described.md"),
        ("Broken front matter", "broken.md"),
    )]}]
    return render("Docs", SITE_URL, "A site", nav, tmp_path)


def test_description_is_listed_and_plain_pages_are_unchanged(tmp_path):
    out = _render(tmp_path, {
        "plain.md": "# Plain page\n\nBody.\n",
        "described.md": (
            "---\ndescription: >-\n  Set up with an assistant.\n  Two lines folded.\n---\n\n"
            "# Described page\n"
        ),
        "broken.md": "---\ndescription: [unclosed\n---\n\n# Broken page\n",
    })
    assert f"- [Plain]({SITE_URL}plain/): Plain page" in out
    assert f"- [Described]({SITE_URL}described/): Set up with an assistant. Two lines folded." in out
    # A front matter block that is not valid YAML falls back to the H1.
    assert f"- [Broken front matter]({SITE_URL}broken/): Broken page" in out
