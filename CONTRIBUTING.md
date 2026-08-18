# Contributing to LimaCharlie Documentation

This documentation is maintained by the LimaCharlie team. We do not accept external contributions at this time.

If you find an error or have a suggestion, please [open an issue](https://github.com/refractionPOINT/documentation/issues).

## Writing release notes

Release notes live in a single page, `docs/10-release-notes/index.md`, newest first. That page is also the source of the published RSS and JSON feeds (`hooks/release_feed.py` generates them into the built site; they are never committed), and of the announcements posted to the community forum. A few things follow from that.

### Heading form

Every release is an `###` entry under a `## YYYY-MM-DD` date heading, and takes one of two forms:

```markdown
## 2026-08-11

### Endpoint Agent 5.3.5          <- a versioned release

### Platform: Query Console is faster   <- a versionless announcement
```

Use the canonical component name so the entry reaches the right per-component feed: **Endpoint Agent**, **Web App**, **Adapters**, **Extensions**, **CLI**, **SDKs**. Anything that is not tied to one component is a **Platform** announcement. The full list, with the historical spellings that map onto it, is in `hooks/release_feed.py`.

Always include the version. A heading without one collides with the next release of the same component, and Python-Markdown resolves that collision by renumbering anchors in document order - which silently moves the anchor of the older entry that people have already linked to.

Never edit or renumber an existing entry's heading. Its anchor is linked to from outside the docs, and its text is the identity feed readers dedupe on, so a change re-announces an old release to every subscriber. Historical entries that predate this convention are recorded in `scripts/release-note-headings-baseline.json` and are intentionally left as they are.

### Flagging breaking and schema changes

An entry that changes an event schema or breaks an existing integration gets its own section:

```markdown
#### Breaking Changes

- ...

#### Schema Changes

- ...
```

Either section puts the entry on the dedicated `breaking-changes.xml` feed, which is what integrators subscribe to when they only want to hear about changes that can break them. Ordinary `#### New Features`, `#### Bug Fixes` and `#### Improvements` sections are unaffected.

### Checking your work

```bash
mkdocs build --strict
python scripts/check-release-note-headings.py --baseline scripts/release-note-headings-baseline.json
python scripts/check-release-feeds.py site
pytest tests/
```

The build itself fails if the page stops parsing into entries. The heading check fails on a new heading that would break naming or anchor stability, and the feed check validates the feeds that were just generated. All three run in CI.
