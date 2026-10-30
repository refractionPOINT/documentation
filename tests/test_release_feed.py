"""Tests for the release-notes feed generator (``hooks/release_feed.py``).

The feed is a published interface with two properties worth guarding:

* **Identity is stable.** A feed reader dedupes on ``<guid>``. Anchors on the
  page are position-dependent (Python-Markdown appends ``_1`` to the second
  heading with the same text, in document order) and new entries are prepended,
  so guids are deliberately built from (date, heading text) instead. The tests
  below pin that difference down with a real Markdown render.
* **Items survive leaving the site.** Bodies are read in a feed reader, where a
  relative link resolves against the reader's origin, and inside XML, where an
  unescaped sequence breaks the document for every item after it.

The end-to-end tests run against the repository's real release notes page, so
they fail if the page's structure drifts away from what the generator expects.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

import markdown
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

import release_feed  # noqa: E402
from release_feed import (  # noqa: E402
    CANONICAL_FEED_BASE,
    COMPONENTS,
    OVERVIEW_FILENAME,
    RELEASE_PAGES,
    PLATFORM_SLUG,
    PluginError,
    Entry,
    absolutize_html_urls,
    absolutize_markdown_links,
    classify_heading,
    extract_html_entries,
    guid_slug,
    iter_markdown_headings,
    normalize_name,
    on_config,
    on_page_markdown,
    parse_markdown_entries,
    render_json_feed,
    render_rss,
    rfc822,
    sort_entries,
)

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
RELEASE_NOTES_DIR = os.path.join(REPO_ROOT, "docs", "10-release-notes")
SITE_URL = "https://docs.limacharlie.io/"
PAGE_URL = f"{SITE_URL}10-release-notes/"


def render_page(text):
    """Render Markdown the way MkDocs does for heading ids (mkdocs.yml `toc`)."""
    converter = markdown.Markdown(
        extensions=["toc"],
        extension_configs={"toc": {"permalink": True, "toc_depth": 3}},
    )
    return converter.convert(text)


@pytest.fixture(scope="module")
def release_notes_text():
    """`{filename: Markdown}` for every page in the repository, overview included."""
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(Path(RELEASE_NOTES_DIR).glob("*.md"))
    }


@pytest.fixture(scope="module")
def release_notes_entries(release_notes_text):
    entries = []
    for filename, text in release_notes_text.items():
        page_url = f"{PAGE_URL}{filename[: -len('.md')]}/"
        if filename == OVERVIEW_FILENAME:
            page_url = PAGE_URL
        entries += extract_html_entries(render_page(text), page_url)
    return entries


# ---------------------------------------------------------------------------
# Component registry and heading classification
# ---------------------------------------------------------------------------


def test_component_aliases_are_stored_normalized():
    """An alias that is not already normalized can never be looked up."""
    for component in COMPONENTS:
        for alias in component.aliases:
            assert normalize_name(alias) == alias, (
                f"{component.slug} alias {alias!r} must be stored in normalized form"
            )


def test_component_slugs_are_unique():
    slugs = [component.slug for component in COMPONENTS]
    assert len(slugs) == len(set(slugs))


@pytest.mark.parametrize(
    ("title", "slugs", "version"),
    [
        ("Endpoint Agent 5.3.5", ("endpoint-agent",), "5.3.5"),
        ("Web App v3.8.10", ("web-app",), "v3.8.10"),
        # Historical spellings must reach the same feed as the current one.
        ("EDR Sensor v4.31.1", ("endpoint-agent",), "v4.31.1"),
        ("EDR Agent v4.33.2", ("endpoint-agent",), "v4.33.2"),
        ("EDR Endpoint Agent v4.33.1", ("endpoint-agent",), "v4.33.1"),
        ("LC Adapters v1.30.11", ("adapters",), "v1.30.11"),
        ("Adapter v1.27.2", ("adapters",), "v1.27.2"),
        # A dual release keeps both versions in one item.
        ("Endpoint Agent 4.33.13 and 4.33.10.3", ("endpoint-agent",),
         "4.33.13 and 4.33.10.3"),
        # One entry can legitimately cover two components.
        ("Extensions and Adapters", ("extensions", "adapters"), None),
        ("Add-Ons and Adapters", ("extensions", "adapters"), None),
        # Extensions are titled by their extension id.
        ("ext-usage-alerts v1.0.0", ("extensions",), "v1.0.0"),
        # Anything unrecognized still reaches the all-entries feed.
        ("New MITRE Report API", (PLATFORM_SLUG,), None),
        ("LimaCharlie Labs", (PLATFORM_SLUG,), None),
    ],
)
def test_classify_heading(title, slugs, version):
    heading = classify_heading(title)
    assert heading.components == slugs
    assert heading.version == version


@pytest.mark.parametrize(
    ("title", "canonical"),
    [
        ("Endpoint Agent 5.3.5", True),
        ("Web App 6.1.0", True),
        ("Web App v6.1.0", True),
        ("Platform: New MITRE Report API", True),
        # Legacy spellings map to the right feed but are not the canonical form.
        ("EDR Sensor v4.31.1", False),
        # A version-less component heading collides with the next one like it.
        ("Endpoint Agent", False),
        # "Platform" is the catch-all bucket; it has no versions.
        ("Platform 1.0", False),
        # A colon form naming something that is not a component.
        ("Something: else entirely", False),
    ],
)
def test_heading_canonical_form(title, canonical):
    assert classify_heading(title).is_canonical is canonical


def test_an_announcement_ending_in_a_number_is_not_read_as_a_version():
    """"Platform: Support for Windows 11" must not publish as version 11."""
    heading = classify_heading("Platform: Support for Windows 11")
    assert heading.components == (PLATFORM_SLUG,)
    assert heading.version is None
    assert heading.announcement == "Support for Windows 11"
    assert heading.is_canonical


def test_entities_in_a_heading_resolve_the_same_way_the_source_reads():
    """The heading text is what the guid is built from, so it must round-trip."""
    page = "# Release Notes\n\n## 2026-01-05\n\n### Web App 1.0.0 & friends\n\nBody.\n"
    html_entry = extract_html_entries(render_page(page), PAGE_URL)[0]
    markdown_entry = parse_markdown_entries(page)[0]
    assert html_entry.title == "Web App 1.0.0 & friends"
    assert html_entry.guid("docs.limacharlie.io") == markdown_entry.guid(
        "docs.limacharlie.io"
    )


def test_announcement_form_keeps_component_and_text():
    heading = classify_heading("Endpoint Agent: Windows ARM64 is generally available")
    assert heading.components == ("endpoint-agent",)
    assert heading.version is None
    assert heading.announcement == "Windows ARM64 is generally available"


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


DUPLICATE_HEADING_PAGE = """# Release Notes

## 2025-10-24

### Endpoint Agent

Older entry.
"""

DUPLICATE_HEADING_PAGE_WITH_NEW_ENTRY = """# Release Notes

## 2026-01-05

### Endpoint Agent

Newer entry with the same heading.

## 2025-10-24

### Endpoint Agent

Older entry.
"""


def test_guid_survives_an_anchor_renumbering():
    """Prepending a same-titled entry must not change the older entry's identity.

    This is the reason guids are not anchors: Python-Markdown hands the bare id
    to whichever heading comes first in the document, so the older entry's
    anchor moves to `_1` while its guid stays put.
    """
    before = extract_html_entries(render_page(DUPLICATE_HEADING_PAGE), PAGE_URL)
    after = extract_html_entries(
        render_page(DUPLICATE_HEADING_PAGE_WITH_NEW_ENTRY), PAGE_URL
    )

    older_before = before[0]
    older_after = next(entry for entry in after if entry.date == "2025-10-24")

    assert older_before.anchor == "endpoint-agent"
    assert older_after.anchor == "endpoint-agent_1", "anchor is expected to move"
    assert older_before.guid("docs.limacharlie.io") == older_after.guid(
        "docs.limacharlie.io"
    ), "guid must not move with the anchor"


def test_guid_is_unique_per_date_and_heading():
    entries = parse_markdown_entries(DUPLICATE_HEADING_PAGE_WITH_NEW_ENTRY)
    guids = [entry.guid("docs.limacharlie.io") for entry in entries]
    assert len(set(guids)) == len(guids)
    assert guids[0] == "tag:docs.limacharlie.io,2026-01-05:release/endpoint-agent"


def test_guid_slug_shape():
    """Pinned: changing this re-announces every entry to every subscriber."""
    assert guid_slug("Endpoint Agent 5.3.5") == "endpoint-agent-5-3-5"
    assert guid_slug("  Web App  v6.1.0 ") == "web-app-v6-1-0"
    assert guid_slug("Add-Ons and Adapters") == "add-ons-and-adapters"


def test_real_page_guids_are_unique(release_notes_entries):
    guids = [entry.guid("docs.limacharlie.io") for entry in release_notes_entries]
    assert len(set(guids)) == len(guids)


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------


def test_markdown_parser_skips_headings_inside_code_fences():
    page = """# Release Notes

## 2026-01-05

### Web App 1.0.0

```bash
## 2020-01-01
### Not An Entry 9.9.9
```

Real content.
"""
    entries = parse_markdown_entries(page)
    assert [entry.title for entry in entries] == ["Web App 1.0.0"]
    assert "Not An Entry" in entries[0].body_markdown


def test_markdown_parser_rejects_an_entry_with_no_date():
    page = """# Release Notes

### Web App 1.0.0

Orphaned entry.
"""
    with pytest.raises(PluginError, match="not under"):
        parse_markdown_entries(page)


SEPARATED_PAGE = """# Release Notes

## 2026-02-09

### Endpoint Agent 5.3.5

Newest.

---

## 2026-01-05

### Web App 6.1.0

Older.
"""


def test_the_date_separator_is_not_part_of_the_entry_above_it():
    """The "---" rule separates date groups; it is page layout, not content."""
    markdown_entry = parse_markdown_entries(SEPARATED_PAGE)[0]
    assert markdown_entry.body_markdown == "Newest."

    html_entry = extract_html_entries(render_page(SEPARATED_PAGE), PAGE_URL)[0]
    assert "<hr" not in html_entry.body_html
    assert html_entry.body_html.endswith("</p>")


def test_characters_xml_cannot_carry_are_dropped_from_bodies():
    """A stray control character would make the feed unparseable for everyone."""
    page = "# Release Notes\n\n## 2026-01-05\n\n### Web App 1.0.0\n\nBad\x0bchar.\n"
    entry = extract_html_entries(render_page(page), PAGE_URL)[0]
    assert "\x0b" not in entry.body_html
    ET.fromstring(render_one(entry))


def test_iter_markdown_headings_ignores_fenced_content():
    text = "# A\n\n```\n## Not a heading\n```\n\n## B\n"
    assert [(level, title) for level, title, _ in iter_markdown_headings(text)] == [
        (1, "A"),
        (2, "B"),
    ]


def test_markdown_and_html_parsers_agree_on_the_real_page(
    release_notes_text, release_notes_entries
):
    """Both parsers feed guids; a disagreement would split an entry's identity."""
    from_markdown = [
        (entry.date, entry.title)
        for text in release_notes_text.values()
        for entry in parse_markdown_entries(text)
    ]
    from_html = [(entry.date, entry.title) for entry in release_notes_entries]
    assert from_markdown == from_html


# ---------------------------------------------------------------------------
# Breaking-change detection
# ---------------------------------------------------------------------------


BREAKING_PAGE = """# Release Notes

## 2026-01-05

### Web App 1.0.0

#### Breaking Changes

- A field was removed.

### Endpoint Agent 1.0.0

#### Schema Changes

- An event gained a field.

### CLI 1.0.0

#### Bug Fixes

- Nothing breaking here.
"""


def test_breaking_sections_are_detected_in_markdown():
    entries = {entry.title: entry.is_breaking for entry in parse_markdown_entries(BREAKING_PAGE)}
    assert entries == {
        "Web App 1.0.0": True,
        "Endpoint Agent 1.0.0": True,
        "CLI 1.0.0": False,
    }


def test_breaking_sections_are_detected_in_rendered_html():
    entries = {
        entry.title: entry.is_breaking
        for entry in extract_html_entries(render_page(BREAKING_PAGE), PAGE_URL)
    }
    assert entries == {
        "Web App 1.0.0": True,
        "Endpoint Agent 1.0.0": True,
        "CLI 1.0.0": False,
    }


def test_a_breaking_section_of_a_later_entry_does_not_leak_backwards():
    """Bodies are cut at the next heading, so flags cannot bleed between entries."""
    entries = extract_html_entries(render_page(BREAKING_PAGE), PAGE_URL)
    assert entries[-1].title == "CLI 1.0.0"
    assert "Schema Changes" not in entries[-1].body_html


# ---------------------------------------------------------------------------
# URL absolutization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("../2-sensors-deployment/asset-tags/",
         "https://docs.limacharlie.io/2-sensors-deployment/asset-tags/"),
        ("#endpoint-agent-535",
         "https://docs.limacharlie.io/10-release-notes/#endpoint-agent-535"),
        ("https://example.com/x", "https://example.com/x"),
        ("mailto:support@limacharlie.io", "mailto:support@limacharlie.io"),
    ],
)
def test_absolutize_html_urls(value, expected):
    out = absolutize_html_urls(f'<a href="{value}">x</a>', PAGE_URL)
    assert out == f'<a href="{expected}">x</a>'


def test_absolutize_html_urls_leaves_empty_destinations_alone():
    assert absolutize_html_urls('<a href="">x</a>', PAGE_URL) == '<a href="">x</a>'


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("../2-sensors-deployment/asset-tags.md",
         "https://docs.limacharlie.io/2-sensors-deployment/asset-tags/"),
        ("../5-integrations/extensions/index.md",
         "https://docs.limacharlie.io/5-integrations/extensions/"),
        ("../8-reference/faq/billing.md#pricing",
         "https://docs.limacharlie.io/8-reference/faq/billing/#pricing"),
        ("#anchor", "https://docs.limacharlie.io/10-release-notes/#anchor"),
        ("https://example.com/x", "https://example.com/x"),
        ("mailto:support@limacharlie.io", "mailto:support@limacharlie.io"),
    ],
)
def test_absolutize_markdown_links(value, expected):
    assert absolutize_markdown_links(f"[x]({value})", PAGE_URL) == f"[x]({expected})"


def test_absolutize_markdown_links_handles_reference_definitions():
    text = "See [asset tags][tags].\n\n[tags]: ../2-sensors-deployment/asset-tags.md\n"
    out = absolutize_markdown_links(text, PAGE_URL)
    assert "[tags]: https://docs.limacharlie.io/2-sensors-deployment/asset-tags/" in out


def test_real_page_bodies_contain_no_relative_urls(release_notes_entries):
    for entry in release_notes_entries:
        for url in re.findall(r'\b(?:href|src)="([^"]*)"', entry.body_html):
            assert re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|//)", url), (
                f"{entry.title}: {url} would not resolve in a feed reader"
            )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def make_entry(title="Web App 1.0.0", date="2026-01-05", body="<p>Body</p>"):
    heading = classify_heading(title)
    return Entry(
        date=date,
        heading=heading,
        body_html=body,
        anchor=guid_slug(title),
        categories=heading.components,
    )


def render_one(entry):
    return render_rss(
        title="Feed",
        description="Feed",
        page_url=PAGE_URL,
        feed_url=f"{PAGE_URL}feed.xml",
        entries=[entry],
        generator="test",
    )


def test_a_body_round_trips_through_the_feed_unchanged():
    """Including the sequences that hand-rolled XML quoting gets wrong."""
    body = '<p>Match on <code>x[0]]&gt;</code> &amp; "quotes" in a rule.</p>'
    root = ET.fromstring(render_one(make_entry(body=body)))
    assert root.findtext("channel/item/description") == body


def test_special_characters_in_a_title_are_escaped():
    root = ET.fromstring(render_one(make_entry(title="Web App 1.0.0 & <friends>")))
    assert root.findtext("channel/item/title") == "Web App 1.0.0 & <friends>"


@pytest.mark.parametrize(
    "hostile",
    [
        "</description></item><item><title>Injected</title><description>x",
        "]]><item><title>Injected</title></item>",
        '"><script>alert(1)</script>',
        "<![CDATA[nested]]>",
    ],
)
def test_a_body_cannot_forge_feed_structure(hostile):
    """Release note text is content, never markup: it cannot invent an item."""
    root = ET.fromstring(render_one(make_entry(body=hostile)))
    items = root.findall("channel/item")
    assert len(items) == 1
    assert items[0].findtext("title") == "Web App 1.0.0"
    assert items[0].findtext("description") == hostile


def test_a_title_cannot_forge_feed_structure():
    hostile = "</title><guid>spoofed</guid><title>x"
    root = ET.fromstring(render_one(make_entry(title=hostile)))
    item = root.find("channel/item")
    assert item.findtext("title") == hostile
    assert item.findtext("guid").startswith("tag:docs.limacharlie.io,")
    assert len(item.findall("guid")) == 1


@pytest.mark.parametrize(
    "hostile",
    [
        '", "id": "spoofed", "junk": "',
        '\\", "id": "spoofed"',
        "line\nbreak\ttab",
    ],
)
def test_a_body_cannot_forge_json_feed_structure(hostile):
    import json

    feed = json.loads(
        render_json_feed(
            title="Feed",
            description="Feed",
            page_url=PAGE_URL,
            feed_url=f"{PAGE_URL}feed.json",
            entries=[make_entry(body=hostile)],
        )
    )
    assert len(feed["items"]) == 1
    assert feed["items"][0]["content_html"] == hostile
    assert feed["items"][0]["id"].startswith("tag:docs.limacharlie.io,")


def test_the_feed_declares_its_encoding_and_namespace():
    xml = render_one(make_entry())
    assert xml.startswith('<?xml version="1.0" encoding="utf-8"?>\n')
    assert 'xmlns:atom="http://www.w3.org/2005/Atom"' in xml


def test_item_carries_link_guid_and_categories():
    root = ET.fromstring(render_one(make_entry(title="Endpoint Agent 5.3.5")))
    item = root.find("channel/item")
    assert item.findtext("link") == f"{PAGE_URL}#endpoint-agent-5-3-5"
    assert item.find("guid").get("isPermaLink") == "false"
    assert item.findtext("guid").startswith("tag:docs.limacharlie.io,2026-01-05:")
    assert [category.text for category in item.findall("category")] == ["endpoint-agent"]


def test_breaking_entries_are_categorized():
    entry = make_entry()
    entry.is_breaking = True
    root = ET.fromstring(render_one(entry))
    categories = [c.text for c in root.findall("channel/item/category")]
    assert "breaking-changes" in categories


def test_empty_feed_is_still_well_formed():
    """The breaking-changes feed ships empty until the first breaking release."""
    xml = render_rss(
        title="Feed",
        description="Feed",
        page_url=PAGE_URL,
        feed_url=f"{PAGE_URL}breaking-changes.xml",
        entries=[],
        generator="test",
    )
    root = ET.fromstring(xml)
    assert root.findall("channel/item") == []
    assert root.findtext("channel/title") == "Feed"


def test_rfc822_dates_are_locale_independent_and_round_trip():
    assert rfc822("2026-08-11") == "Tue, 11 Aug 2026 00:00:00 GMT"
    parsed = parsedate_to_datetime(rfc822("2026-08-11"))
    assert (parsed.year, parsed.month, parsed.day) == (2026, 8, 11)
    assert parsed.utcoffset().total_seconds() == 0


def test_last_build_date_tracks_the_newest_entry_not_the_clock():
    """A rebuild with no content change must produce a byte-identical feed."""
    entries = [make_entry(date="2026-01-05"), make_entry(date="2026-02-09")]
    xml = render_rss(
        title="Feed",
        description="Feed",
        page_url=PAGE_URL,
        feed_url=f"{PAGE_URL}feed.xml",
        entries=entries,
        generator="test",
    )
    assert "<lastBuildDate>Mon, 09 Feb 2026 00:00:00 GMT</lastBuildDate>" in xml


def test_entries_are_sorted_newest_first_and_stable_within_a_date():
    first = make_entry(title="Web App 1.0.0", date="2026-01-05")
    second = make_entry(title="Endpoint Agent 1.0.0", date="2026-01-05")
    older = make_entry(title="CLI 1.0.0", date="2025-12-01")
    ordered = sort_entries([first, second, older])
    assert [entry.title for entry in ordered] == [
        "Web App 1.0.0",
        "Endpoint Agent 1.0.0",
        "CLI 1.0.0",
    ]


def test_json_feed_matches_the_rss_feed(release_notes_entries):
    import json

    rss = ET.fromstring(
        render_rss(
            title="Feed",
            description="Feed",
            page_url=PAGE_URL,
            feed_url=f"{PAGE_URL}feed.xml",
            entries=release_notes_entries,
            generator="test",
        )
    )
    feed = json.loads(
        render_json_feed(
            title="Feed",
            description="Feed",
            page_url=PAGE_URL,
            feed_url=f"{PAGE_URL}feed.json",
            entries=release_notes_entries,
        )
    )
    rss_guids = [item.findtext("guid") for item in rss.findall("channel/item")]
    assert [item["id"] for item in feed["items"]] == rss_guids
    assert feed["version"] == "https://jsonfeed.org/version/1.1"


# ---------------------------------------------------------------------------
# The feed and the page source must describe the same entries
# ---------------------------------------------------------------------------


def write_release_notes(tmp_path, body):
    docs = tmp_path / "10-release-notes"
    docs.mkdir(parents=True)
    (docs / "index.md").write_text(body, encoding="utf-8")
    return tmp_path


def test_source_and_rendered_entries_matching_is_accepted(tmp_path):
    page = "# Release Notes\n\n## 2026-01-05\n\n### Web App 1.0.0\n\nBody.\n"
    docs = write_release_notes(tmp_path, page)
    release_feed._assert_matches_source(
        extract_html_entries(render_page(page), PAGE_URL), docs
    )


def test_an_entry_the_source_does_not_declare_fails_the_build(tmp_path):
    """An `###` indented inside an admonition renders as h3 but is not a heading."""
    page = """# Release Notes

## 2026-01-05

### Web App 1.0.0

!!! note "Aside"
    ### Not A Release

    Text.
"""
    docs = write_release_notes(tmp_path, page)
    rendered = markdown.Markdown(
        extensions=["toc", "admonition"],
        extension_configs={"toc": {"permalink": True, "toc_depth": 3}},
    ).convert(page)
    entries = extract_html_entries(rendered, PAGE_URL)

    assert [entry.title for entry in entries] == ["Web App 1.0.0", "Not A Release"]
    with pytest.raises(PluginError, match="disagree on which entries exist"):
        release_feed._assert_matches_source(entries, docs)


def test_the_repository_page_survives_the_cross_check(release_notes_entries):
    release_feed._assert_matches_source(
        release_notes_entries, Path(REPO_ROOT) / "docs"
    )


# ---------------------------------------------------------------------------
# Feed links follow the build they are served from
# ---------------------------------------------------------------------------


@pytest.fixture
def restore_feed_base():
    previous = release_feed._STATE.get("feed_base")
    yield
    release_feed._STATE["feed_base"] = previous


CALLOUT = f"See [RSS]({CANONICAL_FEED_BASE}endpoint-agent.xml) for agent releases.\n"


def config_for(site_url):
    return {
        "site_url": site_url,
        "extra": {
            "social": [
                {"link": "https://github.com/refractionPOINT", "name": "GitHub"},
                {"link": f"{CANONICAL_FEED_BASE}feed.xml", "name": "RSS"},
            ]
        },
    }


def test_a_production_build_leaves_every_feed_link_untouched(restore_feed_base):
    config = config_for("https://docs.limacharlie.io/")
    on_config(config)
    assert config["extra"]["social"][1]["link"] == f"{CANONICAL_FEED_BASE}feed.xml"
    assert on_page_markdown(CALLOUT, None, config) is None


def test_a_local_preview_points_its_feed_links_at_itself(restore_feed_base):
    """Otherwise every link in the callout 404s against production while previewing."""
    config = config_for("http://127.0.0.1:8000/")
    on_config(config)

    assert config["extra"]["social"][1]["link"] == (
        "http://127.0.0.1:8000/10-release-notes/feed.xml"
    )
    assert config["extra"]["social"][0]["link"] == "https://github.com/refractionPOINT"

    rewritten = on_page_markdown(CALLOUT, None, config)
    assert "http://127.0.0.1:8000/10-release-notes/endpoint-agent.xml" in rewritten
    assert CANONICAL_FEED_BASE not in rewritten


def test_a_page_without_feed_links_is_not_rewritten(restore_feed_base):
    config = config_for("http://127.0.0.1:8000/")
    on_config(config)
    assert on_page_markdown("Nothing to see here.\n", None, config) is None


def test_a_build_with_no_site_url_rewrites_nothing(restore_feed_base):
    config = config_for("")
    on_config(config)
    assert config["extra"]["social"][1]["link"] == f"{CANONICAL_FEED_BASE}feed.xml"
    assert on_page_markdown(CALLOUT, None, config) is None


def test_real_page_renders_a_usable_feed(release_notes_entries):
    xml = render_rss(
        title="LimaCharlie Release Notes",
        description="Releases and platform updates for LimaCharlie.",
        page_url=PAGE_URL,
        feed_url=f"{PAGE_URL}feed.xml",
        entries=release_notes_entries,
        generator="test",
    )
    root = ET.fromstring(xml)
    items = root.findall("channel/item")

    assert len(items) == len(release_notes_entries) > 0
    for item in items:
        assert item.findtext("title")
        assert item.findtext("link").startswith(PAGE_URL)
        assert item.findtext("description")
        parsedate_to_datetime(item.findtext("pubDate"))


# ---------------------------------------------------------------------------
# One page per component
# ---------------------------------------------------------------------------


def fake_page(filename, url=None):
    from types import SimpleNamespace

    if url is None:
        url = "10-release-notes/" if filename == "index.md" else (
            f"10-release-notes/{filename[: -len('.md')]}/"
        )
    return SimpleNamespace(
        file=SimpleNamespace(src_uri=f"10-release-notes/{filename}"), url=url
    )


@pytest.fixture
def fresh_state():
    saved = dict(release_feed._STATE)
    release_feed.on_pre_build({})
    yield release_feed._STATE
    release_feed._STATE.clear()
    release_feed._STATE.update(saved)


def test_every_component_has_exactly_one_page():
    owners = [slug for page in RELEASE_PAGES for slug in page.slugs]
    assert sorted(owners) == sorted(component.slug for component in COMPONENTS)


@pytest.mark.parametrize(
    ("title", "filename"),
    [
        ("Endpoint Agent 5.3.5", "endpoint-agent.md"),
        ("EDR Sensor v4.31.1", "endpoint-agent.md"),
        ("Web App 6.1.0", "web-app.md"),
        ("LC Adapters v1.30.11", "adapters.md"),
        ("ext-usage-alerts v1.0.0", "extensions.md"),
        ("Extensions and Adapters", "extensions.md"),
        ("CLI 4.9.12", "platform.md"),
        ("SDKs 5.0.0", "platform.md"),
        ("New MITRE Report API", "platform.md"),
    ],
)
def test_an_entry_belongs_on_the_page_of_its_primary_component(title, filename):
    assert classify_heading(title).page.filename == filename


def test_every_repository_entry_is_on_its_component_s_page(release_notes_text):
    for filename, text in release_notes_text.items():
        for entry in parse_markdown_entries(text):
            assert entry.heading.page.filename == filename, entry.title


def test_the_repository_overview_holds_no_entries(release_notes_text):
    assert parse_markdown_entries(release_notes_text[OVERVIEW_FILENAME]) == []
    assert release_feed.LATEST_MARKER in release_notes_text[OVERVIEW_FILENAME]


def test_an_entry_links_to_its_own_page(fresh_state):
    page = "# Web App\n\n## 2026-01-05\n\n### Web App 1.0.0\n\nBody.\n"
    release_feed.on_page_content(
        render_page(page), fake_page("web-app.md"), {"site_url": SITE_URL}
    )
    (entry,) = fresh_state["entries"]
    assert entry.link() == f"{PAGE_URL}web-app/#web-app-100"
    # The channel link handed to the renderer does not override it.
    assert entry.link(PAGE_URL) == f"{PAGE_URL}web-app/#web-app-100"
    assert fresh_state["page_urls"] == {"web-app.md": f"{PAGE_URL}web-app/"}


def test_an_entry_on_another_component_s_page_fails_the_build(fresh_state):
    page = "# Web App\n\n## 2026-01-05\n\n### Endpoint Agent 5.3.5\n\nBody.\n"
    with pytest.raises(PluginError, match="belongs on 10-release-notes/endpoint-agent.md"):
        release_feed.on_page_content(
            render_page(page), fake_page("web-app.md"), {"site_url": SITE_URL}
        )


def test_html_comments_are_left_out_of_entry_bodies():
    page = "## 2026-01-05\n\n### Web App 1.0.0\n\nBody.\n\n<!-- glossary -->\n"
    (entry,) = extract_html_entries(render_page(page), PAGE_URL)
    assert "glossary" not in entry.body_html
    assert "Body." in entry.body_html


def page_entry(title, date, filename, anchor=None):
    entry = make_entry(title=title, date=date)
    entry.page_url = f"{PAGE_URL}{filename[: -len('.md')]}/"
    if anchor is not None:
        entry.anchor = anchor
    return entry


def test_the_latest_table_lists_the_newest_releases_with_relative_links():
    entries = [
        page_entry(f"Web App 1.0.{n}", f"2026-01-{n + 1:02d}", "web-app.md")
        for n in range(release_feed.LATEST_COUNT + 3)
    ]
    table = release_feed.render_latest_table(entries, PAGE_URL)
    rows = table.split("<tr>")[2:]

    assert len(rows) == release_feed.LATEST_COUNT
    assert "2026-01-15" in rows[0]
    assert '<a href="web-app/">Web App</a>' in rows[0]
    assert '<a href="web-app/#web-app-1-0-14">Web App 1.0.14</a>' in rows[0]
    assert "https://" not in table


def test_old_anchors_redirect_to_the_page_that_holds_the_entry(monkeypatch, tmp_path):
    legacy = tmp_path / "legacy.json"
    legacy.write_text(
        '{"web-app-610": ["2026-01-05", "Web App 6.1.0"],'
        ' "2026-01-05": ["2026-01-05", null],'
        ' "web-app-600": ["2025-12-01", "Web App 6.0.0"]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(release_feed, "LEGACY_ANCHORS_PATH", legacy)
    entries = [
        page_entry("Endpoint Agent 5.3.5", "2026-01-05", "endpoint-agent.md"),
        page_entry("Web App 6.1.0", "2026-01-05", "web-app.md", anchor="web-app-610"),
    ]

    assert release_feed.legacy_redirects(entries, PAGE_URL) == {
        "web-app-610": "web-app/#web-app-610",
        # A date goes to the page of that date's first entry.
        "2026-01-05": "endpoint-agent/#2026-01-05",
        # "web-app-600" names no entry any more and is dropped.
    }


def test_every_old_anchor_still_leads_somewhere(release_notes_entries):
    """The split must not strand a single link that was already out there."""
    import json

    with open(release_feed.LEGACY_ANCHORS_PATH, encoding="utf-8") as handle:
        legacy = json.load(handle)
    redirects = release_feed.legacy_redirects(release_notes_entries, PAGE_URL)

    assert set(redirects) == set(legacy)
    rendered_ids = {
        (entry.page_url, entry.anchor) for entry in release_notes_entries
    } | {(entry.page_url, entry.date) for entry in release_notes_entries}
    for anchor, target in redirects.items():
        page, _, fragment = target.partition("#")
        assert (PAGE_URL + page, fragment) in rendered_ids, anchor


OVERVIEW_HTML = (
    "<html><body><article><p>Intro</p>"
    f"{release_feed.LATEST_MARKER}</article></body></html>"
)


def test_the_overview_gets_the_latest_releases_and_the_redirects(fresh_state):
    fresh_state["entries"].append(
        page_entry("Endpoint Agent 5.4.2", "2026-10-29", "endpoint-agent.md",
                   anchor="endpoint-agent-542")
    )
    out = release_feed.on_post_page(
        OVERVIEW_HTML, fake_page("index.md"), {"site_url": SITE_URL}
    )
    assert release_feed.LATEST_MARKER not in out
    assert '<a href="endpoint-agent/#endpoint-agent-542">' in out
    assert '"endpoint-agent-542": "endpoint-agent/#endpoint-agent-542"' in out
    assert out.index("<script>") < out.index("</body>")


def test_the_overview_must_say_where_the_latest_releases_go(fresh_state):
    fresh_state["entries"].append(page_entry("Web App 1.0.0", "2026-01-05", "web-app.md"))
    with pytest.raises(PluginError, match="must contain"):
        release_feed.on_post_page(
            "<html><body></body></html>", fake_page("index.md"), {"site_url": SITE_URL}
        )


def test_other_pages_are_left_untouched_after_rendering(fresh_state):
    fresh_state["entries"].append(page_entry("Web App 1.0.0", "2026-01-05", "web-app.md"))
    assert release_feed.on_post_page(
        OVERVIEW_HTML, fake_page("web-app.md"), {"site_url": SITE_URL}
    ) is None
