#!/usr/bin/env python3
"""Validate the release-note feeds in a built site.

``hooks/release_feed.py`` fails the build when the SOURCE page stops making
sense. This checks the other end: that the bytes actually published are a feed
a reader can consume. It runs against ``site/`` after ``mkdocs build``, so it
sees the output of the full MkDocs extension pipeline rather than a test
fixture.

What it enforces
----------------
* Every feed is well-formed XML / JSON. Release note bodies are prose written
  by hand, so an unescaped sequence reaching the feed is a live possibility.
* Every item carries the fields a reader dedupes and sorts on: title, link,
  guid, an RFC 822 pubDate.
* Guids are unique within a feed. A duplicate makes a reader drop items.
* No link or image in an item body is left relative. Item bodies are rendered
  detached from the site, so a relative URL resolves against the reader's own
  origin and 404s.
* `feed.json` describes the same item set as `feed.xml`.

Usage
-----
    python scripts/check-release-feeds.py site --site-url https://docs.limacharlie.io/

Exit code is 1 when a feed is broken, 2 when there is nothing to check, else 0.
"""

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_DIR = "10-release-notes"
REQUIRED_CHANNEL_FIELDS = ("title", "link", "description", "lastBuildDate")
REQUIRED_ITEM_FIELDS = ("title", "link", "guid", "pubDate", "description")
URL_ATTR_RE = re.compile(r'\b(?:href|src)="([^"]*)"')
ABSOLUTE_RE = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|//)")

# The all-entries feed is the one the page and the <link rel="alternate"> tags
# advertise; a build that silently stops emitting it is a regression.
REQUIRED_FEEDS = ("feed.xml", "feed.json", "breaking-changes.xml")


def check_rss(path, site_url, errors):
    """Validate one RSS file. Returns the list of (guid, link) it published."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        errors.append(f"{path}: not well-formed XML: {exc}")
        return []

    if root.tag != "rss" or root.get("version") != "2.0":
        errors.append(f"{path}: root element is not <rss version=\"2.0\">")
        return []

    channel = root.find("channel")
    if channel is None:
        errors.append(f"{path}: no <channel>")
        return []

    for field in REQUIRED_CHANNEL_FIELDS:
        if not (channel.findtext(field) or "").strip():
            errors.append(f"{path}: channel is missing <{field}>")

    self_link = channel.find("{http://www.w3.org/2005/Atom}link")
    if self_link is None or self_link.get("rel") != "self":
        errors.append(f"{path}: channel is missing its <atom:link rel=\"self\">")

    items = []
    seen_guids = {}
    for index, item in enumerate(channel.findall("item")):
        label = f"{path}: item {index}"
        for field in REQUIRED_ITEM_FIELDS:
            if not (item.findtext(field) or "").strip():
                errors.append(f"{label} is missing <{field}>")

        guid = (item.findtext("guid") or "").strip()
        title = (item.findtext("title") or "").strip()
        if guid:
            if guid in seen_guids:
                errors.append(
                    f"{label} ({title!r}) reuses the guid of {seen_guids[guid]!r}"
                )
            seen_guids[guid] = title

        pub_date = (item.findtext("pubDate") or "").strip()
        if pub_date:
            try:
                parsedate_to_datetime(pub_date)
            except (TypeError, ValueError) as exc:
                errors.append(f"{label}: unparseable pubDate {pub_date!r}: {exc}")

        link = (item.findtext("link") or "").strip()
        if link and not link.startswith(site_url):
            errors.append(f"{label}: link {link!r} is not under {site_url!r}")

        for url in URL_ATTR_RE.findall(item.findtext("description") or ""):
            if url and not ABSOLUTE_RE.match(url):
                errors.append(
                    f"{label} ({title!r}) has a relative URL in its body: {url!r}"
                )

        items.append((guid, link))

    return items


def check_json_feed(path, site_url, errors):
    try:
        with open(path, encoding="utf-8") as handle:
            feed = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: not valid JSON: {exc}")
        return []

    if not str(feed.get("version", "")).startswith("https://jsonfeed.org/version/1"):
        errors.append(f"{path}: unexpected JSON Feed version {feed.get('version')!r}")
    if not feed.get("title"):
        errors.append(f"{path}: missing title")

    items = []
    for index, item in enumerate(feed.get("items", [])):
        label = f"{path}: item {index}"
        for field in ("id", "url", "title", "date_published"):
            if not item.get(field):
                errors.append(f"{label} is missing {field}")
        url = item.get("url", "")
        if url and not url.startswith(site_url):
            errors.append(f"{label}: url {url!r} is not under {site_url!r}")
        items.append((item.get("id", ""), url))
    return items


def main(argv):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("site", nargs="?", default="site")
    parser.add_argument("--site-url", default="https://docs.limacharlie.io/")
    args = parser.parse_args(argv[1:])

    feed_dir = os.path.join(args.site, FEED_DIR)
    if not os.path.isdir(feed_dir):
        print(
            f"error: {feed_dir} not found. Run `mkdocs build` first.", file=sys.stderr
        )
        return 2

    missing = [
        name for name in REQUIRED_FEEDS if not os.path.exists(os.path.join(feed_dir, name))
    ]
    if missing:
        print(
            f"error: missing feed(s) in {feed_dir}: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    errors = []
    rss_paths = sorted(glob.glob(os.path.join(feed_dir, "*.xml")))
    checked = {}
    for path in rss_paths:
        checked[path] = check_rss(path, args.site_url, errors)

    json_path = os.path.join(feed_dir, "feed.json")
    json_items = check_json_feed(json_path, args.site_url, errors)

    all_xml = checked.get(os.path.join(feed_dir, "feed.xml"), [])
    if len(all_xml) != len(json_items):
        errors.append(
            f"feed.xml publishes {len(all_xml)} item(s) but feed.json publishes "
            f"{len(json_items)}"
        )
    elif {guid for guid, _ in all_xml} != {guid for guid, _ in json_items}:
        errors.append("feed.xml and feed.json disagree on item ids")

    for path in rss_paths:
        print(f"{os.path.relpath(path)}: {len(checked[path])} item(s)")
    print(f"{os.path.relpath(json_path)}: {len(json_items)} item(s)")

    if errors:
        print(f"\n=== {len(errors)} feed problem(s) ===", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"\n=== {len(rss_paths) + 1} feed(s) OK ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
