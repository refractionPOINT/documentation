#!/usr/bin/env python3
"""Announce newly published release notes in the community forum.

RSS answers "let me subscribe"; it does not answer "tell me". This script
closes that half: when a commit adds entries to
``docs/10-release-notes/index.md``, each new entry is posted to the forum's
Platform Updates category, where members can watch the category and receive
email. It is driven by ``.github/workflows/notify-release-notes.yml``.

What counts as new
------------------
The entry identity is the same ``tag:`` guid the feeds use (see
``hooks/release_feed.py``), computed from the release date and the heading
text. An entry is new when its guid is present in the after-image of the page
and absent from the before-image. Editing an existing entry's body therefore
announces nothing; editing its heading announces it again, which is the same
tradeoff feed readers make.

Not posting is always the safe failure
--------------------------------------
* No API key in the environment -> exit 0 without posting, so the workflow is
  inert until someone deliberately configures the credentials.
* More than ``--max-posts`` new entries (a backfill, a reorganization, a first
  run with no before-image) -> post nothing and say so. A human can post a
  summary; a bot dumping 75 topics into a category cannot be undone.
* A topic with the same title already exists in the category -> skip it, so a
  re-run of the same workflow does not double post.
* A Discourse duplicate-title rejection -> treated as already posted, not as a
  failure.

Usage
-----
    python scripts/notify-release-notes.py \\
        --before /tmp/before.md \\
        --after docs/10-release-notes/index.md \\
        --dry-run

Environment: ``DISCOURSE_API_KEY`` and ``DISCOURSE_API_USERNAME``.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlsplit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from release_feed import (  # noqa: E402
    absolutize_markdown_links,
    parse_markdown_entries,
)

DEFAULT_FORUM_URL = "https://community.limacharlie.com"
DEFAULT_CATEGORY_ID = 5
DEFAULT_CATEGORY_SLUG = "platform-updates"
DEFAULT_DOCS_URL = "https://docs.limacharlie.io/10-release-notes/"

# A backfill or a re-organization can make dozens of entries look new at once.
# Above this many, post nothing rather than flood the category.
DEFAULT_MAX_POSTS = 5

HTTP_TIMEOUT = 30


class ForumError(Exception):
    """A Discourse request failed in a way the caller should see."""


def read_text(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def new_entries(before_text, after_text, host):
    """Entries present in `after_text` but not in `before_text`, oldest first.

    Returns `(entries, has_baseline)`. Without a before-image every entry looks
    new, and the caller refuses to post rather than announce the entire archive.
    """
    after = parse_markdown_entries(after_text)
    if before_text is None:
        return list(reversed(after)), False
    known = {entry.guid(host) for entry in parse_markdown_entries(before_text)}
    fresh = [entry for entry in after if entry.guid(host) not in known]
    # The page is newest-first; announce in release order.
    return list(reversed(fresh)), True


def topic_title(entry):
    """Forum topic title for an entry.

    The date suffix keeps titles unique across re-releases of the same version
    and clears Discourse's minimum title length for short headings ("CLI 5.0").
    """
    return f"{entry.title} ({entry.date})"


def topic_body(entry, docs_url):
    """Forum post body: the release note itself plus a link back to the docs."""
    body = absolutize_markdown_links(entry.body_markdown, docs_url).strip()
    link = f"{docs_url}#{entry.date}"
    parts = [f"**{entry.title}** was released on {entry.date}."]
    if body:
        parts.append(body)
    parts.append(f"[Full release notes]({link})")
    return "\n\n".join(parts)


class DiscourseClient:
    """Minimal Discourse client over stdlib urllib (no third-party deps)."""

    def __init__(self, base_url, api_key, api_username, opener=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_username = api_username
        self._opener = opener or urllib.request.urlopen

    def existing_titles(self, category_slug, category_id):
        """Recent topic titles in a category, lowercased. Empty set on failure.

        Used only to avoid double posting, so a failure here must not stop the
        announcement: Discourse's own duplicate-title rejection is the backstop.
        """
        url = f"{self.base_url}/c/{category_slug}/{category_id}.json"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with self._opener(request, timeout=HTTP_TIMEOUT) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, ValueError, OSError) as exc:
            print(f"warning: could not list existing topics: {exc}", file=sys.stderr)
            return set()
        topics = payload.get("topic_list", {}).get("topics", [])
        return {topic.get("title", "").strip().lower() for topic in topics}

    def create_topic(self, title, raw, category_id):
        """Create a topic. Returns True when posted, False when already present."""
        data = urllib.parse.urlencode(
            {"title": title, "raw": raw, "category": str(category_id)}
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/posts.json",
            data=data,
            headers={
                "Api-Key": self.api_key,
                "Api-Username": self.api_username,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        try:
            with self._opener(request, timeout=HTTP_TIMEOUT) as response:
                response.read()
            return True
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code == 422 and "has already been used" in body:
                return False
            raise ForumError(f"POST /posts.json failed ({exc.code}): {body}") from exc
        except (urllib.error.URLError, OSError) as exc:
            raise ForumError(f"POST /posts.json failed: {exc}") from exc


def main(argv):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--after", required=True, help="release notes Markdown after the change"
    )
    parser.add_argument(
        "--before", help="release notes Markdown before the change (optional)"
    )
    parser.add_argument("--forum-url", default=DEFAULT_FORUM_URL)
    parser.add_argument("--category-id", type=int, default=DEFAULT_CATEGORY_ID)
    parser.add_argument("--category-slug", default=DEFAULT_CATEGORY_SLUG)
    parser.add_argument("--docs-url", default=DEFAULT_DOCS_URL)
    parser.add_argument("--max-posts", type=int, default=DEFAULT_MAX_POSTS)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would be posted and exit without calling the forum",
    )
    args = parser.parse_args(argv[1:])

    after_text = read_text(args.after)
    if after_text is None:
        print(f"error: --after file not found: {args.after}", file=sys.stderr)
        return 2

    host = urlsplit(args.docs_url).hostname or "docs.limacharlie.io"
    entries, has_baseline = new_entries(read_text(args.before), after_text, host)

    if not entries:
        print("no new release notes to announce")
        return 0

    if not has_baseline:
        print(
            f"refusing to announce {len(entries)} entr(y/ies): no before-image was "
            "supplied, so the whole archive looks new. Pass --before, or post "
            "manually.",
            file=sys.stderr,
        )
        return 0

    if len(entries) > args.max_posts:
        print(
            f"refusing to announce {len(entries)} entr(y/ies) at once (limit "
            f"{args.max_posts}). This looks like a backfill; post a summary "
            "manually instead.",
            file=sys.stderr,
        )
        return 0

    if args.dry_run:
        for entry in entries:
            print(f"--- would post: {topic_title(entry)}")
            print(topic_body(entry, args.docs_url))
            print()
        return 0

    api_key = os.environ.get("DISCOURSE_API_KEY", "")
    api_username = os.environ.get("DISCOURSE_API_USERNAME", "")
    if not api_key or not api_username:
        print(
            "DISCOURSE_API_KEY / DISCOURSE_API_USERNAME are not set; skipping the "
            f"announcement of {len(entries)} entr(y/ies). Configure the secrets to "
            "enable forum notifications."
        )
        return 0

    client = DiscourseClient(args.forum_url, api_key, api_username)
    already = client.existing_titles(args.category_slug, args.category_id)

    posted = skipped = 0
    for entry in entries:
        title = topic_title(entry)
        if title.strip().lower() in already:
            print(f"skipping (topic already exists): {title}")
            skipped += 1
            continue
        try:
            created = client.create_topic(
                title, topic_body(entry, args.docs_url), args.category_id
            )
        except ForumError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if created:
            print(f"posted: {title}")
            posted += 1
        else:
            print(f"skipping (title rejected as duplicate): {title}")
            skipped += 1

    print(f"=== announced {posted} entr(y/ies), skipped {skipped} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
