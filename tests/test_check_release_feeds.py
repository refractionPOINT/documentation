"""Tests for the built-feed validator (``scripts/check-release-feeds.py``).

The validator is the gate that stands between a broken feed and a deploy, so
what matters is that it actually rejects broken feeds. Each test corrupts a
real generated feed in one specific way and asserts the run fails - a validator
that passes everything is worse than no validator, because it reads as a
guarantee.
"""

import importlib.util
import json
import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(REPO_ROOT, "scripts", "check-release-feeds.py")

sys.path.insert(0, os.path.join(REPO_ROOT, "hooks"))

from release_feed import (  # noqa: E402
    Entry,
    classify_heading,
    guid_slug,
    render_json_feed,
    render_rss,
)

SITE_URL = "https://docs.limacharlie.io/"
PAGE_URL = f"{SITE_URL}10-release-notes/"


def load_script(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = load_script(SCRIPT, "check_release_feeds")


def make_entry(title="Endpoint Agent 5.3.5", date="2026-08-11", body="<p>Body</p>"):
    heading = classify_heading(title)
    return Entry(
        date=date,
        heading=heading,
        body_html=body,
        anchor=guid_slug(title),
        categories=heading.components,
    )


def build_site(tmp_path, entries=None, extra_files=None):
    """Write a minimal but genuine built site to validate."""
    entries = entries if entries is not None else [make_entry()]
    feed_dir = tmp_path / "site" / "10-release-notes"
    feed_dir.mkdir(parents=True)

    def rss(filename, subset):
        return render_rss(
            title="LimaCharlie Release Notes",
            description="Releases.",
            page_url=PAGE_URL,
            feed_url=f"{PAGE_URL}{filename}",
            entries=subset,
            generator="test",
        )

    (feed_dir / "feed.xml").write_text(rss("feed.xml", entries), encoding="utf-8")
    (feed_dir / "breaking-changes.xml").write_text(
        rss("breaking-changes.xml", []), encoding="utf-8"
    )
    (feed_dir / "feed.json").write_text(
        render_json_feed(
            title="LimaCharlie Release Notes",
            description="Releases.",
            page_url=PAGE_URL,
            feed_url=f"{PAGE_URL}feed.json",
            entries=entries,
        ),
        encoding="utf-8",
    )
    for name, content in (extra_files or {}).items():
        (feed_dir / name).write_text(content, encoding="utf-8")
    return tmp_path / "site", feed_dir


def run(site):
    return check.main(["check-release-feeds.py", str(site), "--site-url", SITE_URL])


def test_a_generated_site_passes(tmp_path):
    site, _ = build_site(tmp_path)
    assert run(site) == 0


def test_a_missing_site_directory_is_reported(tmp_path, capsys):
    assert run(tmp_path / "nope") == 2
    assert "Run `mkdocs build` first" in capsys.readouterr().err


def test_a_missing_required_feed_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    (feed_dir / "feed.json").unlink()
    assert run(site) == 1
    assert "missing feed" in capsys.readouterr().err


def test_malformed_xml_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    (feed_dir / "feed.xml").write_text("<rss><channel>", encoding="utf-8")
    assert run(site) == 1
    assert "not well-formed XML" in capsys.readouterr().err


def test_a_body_that_reached_the_feed_unescaped_fails(tmp_path, capsys):
    """The artifact-level backstop for an escaping regression in the generator."""
    site, feed_dir = build_site(tmp_path)
    text = (feed_dir / "feed.xml").read_text(encoding="utf-8")
    assert "&lt;p&gt;Body&lt;/p&gt;" in text, "bodies are expected to be escaped"
    (feed_dir / "feed.xml").write_text(
        text.replace("&lt;p&gt;Body&lt;/p&gt;", "<p>Body</p><evil"), encoding="utf-8"
    )
    assert run(site) == 1
    assert "not well-formed XML" in capsys.readouterr().err


def test_duplicate_guids_fail(tmp_path, capsys):
    entry = make_entry()
    site, _ = build_site(tmp_path, entries=[entry, entry])
    assert run(site) == 1
    assert "reuses the guid" in capsys.readouterr().err


def test_a_relative_url_in_a_body_fails(tmp_path, capsys):
    site, _ = build_site(
        tmp_path, entries=[make_entry(body='<a href="../elsewhere/">x</a>')]
    )
    assert run(site) == 1
    assert "relative URL in its body" in capsys.readouterr().err


def test_an_off_site_item_link_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    tampered = (feed_dir / "feed.xml").read_text(encoding="utf-8").replace(
        f"<link>{PAGE_URL}#", "<link>https://example.com/#"
    )
    (feed_dir / "feed.xml").write_text(tampered, encoding="utf-8")
    assert run(site) == 1
    assert "is not under" in capsys.readouterr().err


def test_an_item_missing_a_required_field_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    stripped = (feed_dir / "feed.xml").read_text(encoding="utf-8")
    start = stripped.index("      <pubDate>")
    end = stripped.index("\n", start) + 1
    (feed_dir / "feed.xml").write_text(stripped[:start] + stripped[end:], encoding="utf-8")
    assert run(site) == 1
    assert "missing <pubDate>" in capsys.readouterr().err


def test_an_unparseable_pubdate_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    tampered = (feed_dir / "feed.xml").read_text(encoding="utf-8").replace(
        "Tue, 11 Aug 2026 00:00:00 GMT", "yesterday"
    )
    (feed_dir / "feed.xml").write_text(tampered, encoding="utf-8")
    assert run(site) == 1
    assert "unparseable pubDate" in capsys.readouterr().err


def test_json_and_rss_disagreeing_on_items_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    feed = json.loads((feed_dir / "feed.json").read_text(encoding="utf-8"))
    feed["items"] = []
    (feed_dir / "feed.json").write_text(json.dumps(feed), encoding="utf-8")
    assert run(site) == 1
    assert "feed.json publishes" in capsys.readouterr().err


def test_malformed_json_fails(tmp_path, capsys):
    site, feed_dir = build_site(tmp_path)
    (feed_dir / "feed.json").write_text("{not json", encoding="utf-8")
    assert run(site) == 1
    assert "not valid JSON" in capsys.readouterr().err


@pytest.mark.parametrize("filename", ["feed.xml", "breaking-changes.xml"])
def test_a_feed_missing_its_self_link_fails(tmp_path, capsys, filename):
    site, feed_dir = build_site(tmp_path)
    text = (feed_dir / filename).read_text(encoding="utf-8")
    text = "\n".join(line for line in text.splitlines() if "atom:link" not in line)
    (feed_dir / filename).write_text(text, encoding="utf-8")
    assert run(site) == 1
    assert "atom:link" in capsys.readouterr().err
