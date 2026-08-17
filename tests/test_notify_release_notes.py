"""Tests for the forum announcer (``scripts/notify-release-notes.py``).

The announcer writes to a public forum, so every test here is about the ways it
must decline to write: no baseline to diff against, too many entries at once,
a topic that already exists, missing credentials. The happy path is one post
per genuinely new entry, carrying a body whose links still work off-site.

No test touches the network; the Discourse client takes its URL opener as a
parameter and `main` is exercised against a recording double.
"""

import importlib.util
import io
import os
import sys
import urllib.error

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(REPO_ROOT, "scripts", "notify-release-notes.py")

sys.path.insert(0, os.path.join(REPO_ROOT, "hooks"))


def load_script(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


notify = load_script(SCRIPT, "notify_release_notes")

HOST = "docs.limacharlie.io"
DOCS_URL = "https://docs.limacharlie.io/10-release-notes/"

BEFORE = """# Release Notes

## 2026-01-05

### Web App 6.1.0

Older release.
"""

AFTER = """# Release Notes

## 2026-02-09

### Endpoint Agent 5.3.5

#### Bug Fixes

- Fixed a thing. See [asset tags](../2-sensors-deployment/asset-tags.md).

## 2026-01-05

### Web App 6.1.0

Older release.
"""

AFTER_TWO_NEW = AFTER.replace(
    "## 2026-01-05",
    """## 2026-02-08

### Web App 6.2.0

Another new release.

## 2026-01-05""",
)


class FakeResponse:
    def __init__(self, payload=b"{}"):
        self._payload = payload

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class FakeOpener:
    """Records requests and replays queued responses or errors."""

    def __init__(self, responses=None):
        self.requests = []
        self.responses = list(responses or [])

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        if not self.responses:
            return FakeResponse()
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def http_error(code, body):
    return urllib.error.HTTPError(
        "https://forum.example/posts.json", code, "err", {}, io.BytesIO(body)
    )


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# Which entries count as new
# ---------------------------------------------------------------------------


def test_only_added_entries_are_announced():
    entries, has_baseline = notify.new_entries(BEFORE, AFTER, HOST)
    assert has_baseline is True
    assert [entry.title for entry in entries] == ["Endpoint Agent 5.3.5"]


def test_entries_are_announced_oldest_first():
    entries, _ = notify.new_entries(BEFORE, AFTER_TWO_NEW, HOST)
    assert [entry.date for entry in entries] == ["2026-02-08", "2026-02-09"]


def test_editing_a_body_announces_nothing():
    edited = AFTER.replace("Older release.", "Older release, reworded.")
    entries, _ = notify.new_entries(AFTER, edited, HOST)
    assert entries == []


def test_a_missing_before_image_is_reported_as_no_baseline():
    entries, has_baseline = notify.new_entries(None, AFTER, HOST)
    assert has_baseline is False
    assert len(entries) == 2


# ---------------------------------------------------------------------------
# Post content
# ---------------------------------------------------------------------------


def test_topic_title_carries_the_release_date():
    entry = notify.new_entries(BEFORE, AFTER, HOST)[0][0]
    assert notify.topic_title(entry) == "Endpoint Agent 5.3.5 (2026-02-09)"


def test_topic_body_absolutizes_links_and_links_back_to_the_docs():
    entry = notify.new_entries(BEFORE, AFTER, HOST)[0][0]
    body = notify.topic_body(entry, DOCS_URL)
    assert "https://docs.limacharlie.io/2-sensors-deployment/asset-tags/" in body
    assert "../2-sensors-deployment" not in body
    assert f"[Full release notes]({DOCS_URL}#2026-02-09)" in body
    assert "#### Bug Fixes" in body


# ---------------------------------------------------------------------------
# Discourse client
# ---------------------------------------------------------------------------


def test_create_topic_posts_the_entry():
    opener = FakeOpener()
    client = notify.DiscourseClient("https://forum.example", "key", "bot", opener)
    assert client.create_topic("Title", "Body", 5) is True

    request = opener.requests[0]
    assert request.full_url == "https://forum.example/posts.json"
    assert request.get_header("Api-key") == "key"
    assert b"category=5" in request.data


def test_duplicate_title_rejection_is_not_an_error():
    opener = FakeOpener([http_error(422, b'{"errors":["Title has already been used"]}')])
    client = notify.DiscourseClient("https://forum.example", "key", "bot", opener)
    assert client.create_topic("Title", "Body", 5) is False


def test_other_http_errors_surface():
    opener = FakeOpener([http_error(403, b"forbidden")])
    client = notify.DiscourseClient("https://forum.example", "key", "bot", opener)
    with pytest.raises(notify.ForumError, match="403"):
        client.create_topic("Title", "Body", 5)


def test_listing_existing_titles_tolerates_a_failure():
    """A failed lookup must not stop the announcement; it only weakens dedupe."""
    opener = FakeOpener([urllib.error.URLError("boom")])
    client = notify.DiscourseClient("https://forum.example", "key", "bot", opener)
    assert client.existing_titles("platform-updates", 5) == set()


def test_existing_titles_are_lowercased_for_comparison():
    opener = FakeOpener(
        [FakeResponse(b'{"topic_list":{"topics":[{"title":"Endpoint Agent 5.3.5 (2026-02-09)"}]}}')]
    )
    client = notify.DiscourseClient("https://forum.example", "key", "bot", opener)
    assert client.existing_titles("platform-updates", 5) == {
        "endpoint agent 5.3.5 (2026-02-09)"
    }


# ---------------------------------------------------------------------------
# End to end through main()
# ---------------------------------------------------------------------------


class RecordingClient:
    posted = []
    existing = set()

    def __init__(self, *args, **kwargs):
        pass

    def existing_titles(self, slug, category_id):
        return set(RecordingClient.existing)

    def create_topic(self, title, raw, category_id):
        RecordingClient.posted.append(title)
        return True


@pytest.fixture
def recorder(monkeypatch):
    RecordingClient.posted = []
    RecordingClient.existing = set()
    monkeypatch.setattr(notify, "DiscourseClient", RecordingClient)
    monkeypatch.setenv("DISCOURSE_API_KEY", "key")
    monkeypatch.setenv("DISCOURSE_API_USERNAME", "bot")
    return RecordingClient


def run(tmp_path, after, before=None, *args):
    argv = ["notify-release-notes.py", "--after", write(tmp_path, "after.md", after)]
    if before is not None:
        argv += ["--before", write(tmp_path, "before.md", before)]
    else:
        argv += ["--before", str(tmp_path / "missing.md")]
    return notify.main(argv + list(args))


def test_new_entry_is_posted(tmp_path, recorder):
    assert run(tmp_path, AFTER, BEFORE) == 0
    assert recorder.posted == ["Endpoint Agent 5.3.5 (2026-02-09)"]


def test_nothing_new_posts_nothing(tmp_path, recorder):
    assert run(tmp_path, AFTER, AFTER) == 0
    assert recorder.posted == []


def test_a_backfill_is_refused(tmp_path, recorder, capsys):
    assert run(tmp_path, AFTER_TWO_NEW, BEFORE, "--max-posts", "1") == 0
    assert recorder.posted == []
    assert "refusing to announce" in capsys.readouterr().err


def test_a_missing_before_image_refuses_to_announce_the_archive(
    tmp_path, recorder, capsys
):
    assert run(tmp_path, AFTER) == 0
    assert recorder.posted == []
    assert "no before-image" in capsys.readouterr().err


def test_an_existing_topic_is_skipped(tmp_path, recorder):
    recorder.existing = {"endpoint agent 5.3.5 (2026-02-09)"}
    assert run(tmp_path, AFTER, BEFORE) == 0
    assert recorder.posted == []


def test_dry_run_posts_nothing(tmp_path, recorder, capsys):
    assert run(tmp_path, AFTER, BEFORE, "--dry-run") == 0
    assert recorder.posted == []
    assert "would post: Endpoint Agent 5.3.5" in capsys.readouterr().out


def test_missing_credentials_is_a_no_op(tmp_path, recorder, monkeypatch, capsys):
    monkeypatch.delenv("DISCOURSE_API_KEY", raising=False)
    assert run(tmp_path, AFTER, BEFORE) == 0
    assert recorder.posted == []
    assert "skipping the announcement" in capsys.readouterr().out


def test_a_missing_after_file_is_an_error(tmp_path, capsys):
    assert notify.main(
        ["notify-release-notes.py", "--after", str(tmp_path / "nope.md")]
    ) == 2
    assert "not found" in capsys.readouterr().err
