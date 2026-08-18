#!/usr/bin/env python3
"""Keep release-note headings feed-safe and link-stable.

The release notes are published as RSS/JSON feeds (``hooks/release_feed.py``)
and every entry heading doubles as a permanent anchor on the page, so a heading
is a published interface, not just formatting. This check enforces the two
properties that interface needs.

1. Canonical component naming (``naming``)
   An entry heading must take one of two forms, using a canonical component
   name from ``hooks/release_feed.py``:

       ### Endpoint Agent 5.3.5                  <- a versioned release
       ### Platform: New MITRE Report API        <- a versionless announcement

   Historical entries used several spellings for the same component ("EDR
   Sensor", "EDR Agent", "LC Adapters"); those are mapped onto the right feed
   by the alias table and grandfathered here, and they are deliberately NOT
   rewritten - editing a historical heading would change its anchor and break
   every existing deep link to it.

2. Anchor stability (``slug-collision``)
   Python-Markdown gives the first heading with a given slug the bare id and
   appends ``_1``, ``_2`` to later ones in DOCUMENT order. New entries are
   prepended at the top of the page, so a new heading that collides with an
   existing one steals the bare anchor and silently renumbers the older entry -
   breaking links that already exist in the wild and in already-delivered feed
   items. Including a version in every heading makes collisions impossible.

Structural breakage (an entry that is not under a ``## YYYY-MM-DD`` heading, a
non-date ``##``) is always fatal and cannot be baselined: the feed generator
cannot date such an entry.

Usage
-----
    python scripts/check-release-note-headings.py \\
        --baseline scripts/release-note-headings-baseline.json

Options:
    --docs DIR              Documentation root (default: docs).
    --baseline FILE         Ignore findings listed in FILE (accepted history);
                            exit non-zero only on findings NOT in the baseline.
    --update-baseline FILE  Write the current findings to FILE and exit 0.

Exit code is 1 when a non-baselined finding is present, 2 on bad input, else 0.
"""

import argparse
import json
import os
import sys
from collections import defaultdict

from markdown.extensions.toc import slugify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from release_feed import (  # noqa: E402
    COMPONENTS,
    DATE_RE,
    PLATFORM_SLUG,
    classify_heading,
    iter_markdown_headings,
)

RELEASE_NOTES_DIR = "10-release-notes"


class StructuralError(Exception):
    """A heading the feed generator cannot interpret at all."""


def collect(docs_dir):
    """Return {relative_path: [(kind, date, title, lineno, detail), ...]}."""
    root = os.path.join(docs_dir, RELEASE_NOTES_DIR)
    if not os.path.isdir(root):
        raise StructuralError(f"release notes directory not found: {root}")

    # "Platform" is the catch-all bucket for cross-cutting news; it heads the
    # announcement form only, never a versioned release.
    release_names = sorted(
        component.name for component in COMPONENTS if component.slug != PLATFORM_SLUG
    )
    naming_detail = (
        "expected '### <Component> <version>' (one of: "
        + ", ".join(release_names)
        + ") or '### <Component>: <announcement>' for a versionless entry"
    )
    findings = defaultdict(list)

    for filename in sorted(os.listdir(root)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(root, filename)
        rel = os.path.join(RELEASE_NOTES_DIR, filename)
        with open(path, encoding="utf-8") as handle:
            text = handle.read()

        current_date = None
        # Slug -> first heading that claimed it, over the whole document. This
        # mirrors how Python-Markdown's toc extension allocates ids.
        slug_owner = {}
        collisions = defaultdict(list)
        entries = []

        for level, title, lineno in iter_markdown_headings(text):
            slug = slugify(title, "-")
            if slug in slug_owner:
                collisions[slug].append((level, title, lineno))
            else:
                slug_owner[slug] = (level, title, lineno)

            if level == 2:
                if not DATE_RE.match(title):
                    raise StructuralError(
                        f"{rel}:{lineno}: '## {title}' is not a 'YYYY-MM-DD' date "
                        "heading; the feed generator groups entries by date"
                    )
                current_date = title
            elif level == 3:
                if current_date is None:
                    raise StructuralError(
                        f"{rel}:{lineno}: entry '### {title}' is not under a "
                        "'## YYYY-MM-DD' date heading"
                    )
                entries.append((current_date, title, lineno, slug))

        for date, title, lineno, slug in entries:
            heading = classify_heading(title)
            if not heading.is_canonical:
                findings[rel].append(
                    ("naming", date, title, lineno, naming_detail)
                )
            if slug in collisions:
                owner = slug_owner[slug]
                findings[rel].append(
                    (
                        "slug-collision",
                        date,
                        title,
                        lineno,
                        f"anchor '#{slug}' is claimed by more than one heading "
                        f"(first at line {owner[2]}); later ones render as "
                        f"'#{slug}_1', '#{slug}_2', ...",
                    )
                )

    return findings


def baseline_key(rel, kind, date, title):
    return f"{rel}::{kind}::{date}::{title}"


def as_baseline_keys(findings):
    return sorted(
        baseline_key(rel, kind, date, title)
        for rel, rows in findings.items()
        for kind, date, title, _lineno, _detail in rows
    )


def main(argv):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--docs", default="docs")
    parser.add_argument("--baseline")
    parser.add_argument("--update-baseline")
    args = parser.parse_args(argv[1:])

    try:
        findings = collect(args.docs)
    except StructuralError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.update_baseline:
        keys = as_baseline_keys(findings)
        with open(args.update_baseline, "w", encoding="utf-8") as handle:
            json.dump(keys, handle, indent=2)
            handle.write("\n")
        print(f"wrote baseline with {len(keys)} entr(y/ies) to {args.update_baseline}")
        return 0

    baseline = set()
    if args.baseline and os.path.exists(args.baseline):
        with open(args.baseline, encoding="utf-8") as handle:
            baseline = set(json.load(handle))

    new_count = 0
    total = 0
    for rel in sorted(findings):
        rows = []
        for kind, date, title, lineno, detail in findings[rel]:
            total += 1
            if baseline_key(rel, kind, date, title) in baseline:
                continue
            rows.append((kind, date, title, lineno, detail))
        if not rows:
            continue
        new_count += len(rows)
        print(f"\n{rel}")
        for kind, date, title, lineno, detail in rows:
            print(f"  line {lineno}: [{kind}] '### {title}' ({date})")
            print(f"    {detail}")

    print(
        f"\n=== {new_count} new heading issue(s); {total - new_count} baselined ==="
    )
    if new_count:
        print(
            "Rename the heading to '### <Component> <version>'. Do NOT rename "
            "existing entries to clear a baselined finding: their anchors are "
            "already published in links and in delivered feed items.",
            file=sys.stderr,
        )
    return 1 if new_count else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
