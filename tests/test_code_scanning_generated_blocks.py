"""Guards the generated D&R rule blocks on docs/cloud-security/code-security/pull-requests.md.

The three webhook recipe rules quoted on this page (the push-rescan rule, the
pull-request check, and the base-branch retarget) used to be typed by hand,
copied from a rule definition that lives in a separate, private repository.
Nothing kept the two in sync, and they drifted at least once before (a
templated pull-request number that a downstream integer schema silently
refused). The blocks are now generated from that canonical definition and
pasted in between HTML-comment markers that carry a sha256 of the exact YAML
they wrap:

    <!-- generated from ...; rule=<name>; sha256=<hex>; do not edit -->
    ```yaml
    ...
    ```
    <!-- end generated: <name> -->

WHAT THIS TEST CAN AND CANNOT DO. This repository cannot reach into the
private repository that owns the canonical definition at test time -- doing
so would mean either a long-lived credential granting a public repository's
CI read access to private source, or fetching that source into a public
build, and neither is an acceptable trade for this. So this test cannot tell
you the block below still matches the canonical rule today. What it CAN do,
entirely from this file's own committed text: prove nobody hand-edited the
fenced YAML without regenerating it, since an edit changes the content but
leaves the recorded hash exactly where it was. Pair a change to any of these
blocks with actually re-running the generator that produced it.
"""

import hashlib
import os
import re
import textwrap

DOC_PATH = os.path.join(
    os.path.dirname(__file__), "..", "docs", "cloud-security", "code-security", "pull-requests.md"
)

# The marker line may be indented (these blocks sit inside numbered list items in the
# rendered markdown), so the indentation is captured and stripped from every line inside
# the block before hashing -- the hash was computed over the UNINDENTED YAML.
MARKER_RE = re.compile(
    r"^(?P<indent>[ \t]*)<!-- generated from [^;]+; rule=(?P<rule>[a-z0-9-]+); "
    r"sha256=(?P<hash>[0-9a-f]{64}); do not edit -->$"
)

EXPECTED_RULES = [
    "cloudsec-code-push-rescan",
    "cloudsec-code-pr-check",
    "cloudsec-code-pr-retarget",
]


def _read_doc():
    with open(DOC_PATH, encoding="utf-8") as f:
        return f.read()


def _find_generated_blocks(doc_text):
    """Parses every generated block out of the doc, returning a list of
    (rule, recorded_hash, yaml_text) tuples. Raises AssertionError on any block that does
    not match the expected shape -- a malformed marker is exactly the kind of accidental
    edit this guard exists to catch, so it must fail loudly rather than being skipped.
    """
    lines = doc_text.split("\n")
    blocks = []

    i = 0
    while i < len(lines):
        m = MARKER_RE.match(lines[i])
        if not m:
            i += 1
            continue

        rule = m.group("rule")
        recorded_hash = m.group("hash")
        indent = m.group("indent")

        # A single blank line is REQUIRED between the marker and the fence, and between the
        # closing fence and the end marker -- not just permitted. Inside a numbered-list
        # continuation, `md_in_html` + `pymdownx.superfences` treat an HTML comment directly
        # adjacent to a fenced block as inline content of the same paragraph, which fuses the
        # rendered `<div>`/`<pre>` into a `<p>` (illegal nesting, confirmed against a real
        # `mkdocs build` of this site). The blank line is what keeps the fence a block-level
        # sibling instead. Still tolerate zero blank lines when parsing, rather than only
        # accepting the one required shape, so a malformed doc fails with THIS test's own
        # assertion message instead of an opaque list-index error.
        fence_open = indent + "```yaml"
        after_marker = i + 1
        if after_marker < len(lines) and lines[after_marker] == "":
            after_marker += 1
        assert after_marker < len(lines) and lines[after_marker] == fence_open, (
            f"rule {rule}: marker at line {i + 1} is not followed (directly, or after one "
            f"blank line) by {fence_open!r}"
        )
        yaml_start = after_marker + 1

        fence_close = indent + "```"
        yaml_end = None
        for j in range(yaml_start, len(lines)):
            if lines[j] == fence_close:
                yaml_end = j
                break
        assert yaml_end is not None, (
            f"rule {rule}: no closing fence ({fence_close!r}) found for the block opened "
            f"at line {yaml_start + 1}"
        )

        end_marker = indent + f"<!-- end generated: {rule} -->"
        after_fence = yaml_end + 1
        if after_fence < len(lines) and lines[after_fence] == "":
            after_fence += 1
        assert after_fence < len(lines) and lines[after_fence] == end_marker, (
            f"rule {rule}: expected {end_marker!r} on the line after the closing fence "
            f"(directly, or after one blank line, starting at line {yaml_end + 2})"
        )

        yaml_lines = lines[yaml_start:yaml_end]
        for k, line in enumerate(yaml_lines):
            assert line == "" or line.startswith(indent), (
                f"rule {rule}: line {yaml_start + k + 1} is indented less than the "
                f"marker ({indent!r}) -- the block's indentation must be uniform"
            )
        # dedent, not lstrip: only remove exactly the marker's own indent, so an
        # intentionally-indented YAML value nested further in is preserved.
        dedented = [line[len(indent):] if line.startswith(indent) else line for line in yaml_lines]
        yaml_text = "\n".join(dedented)

        blocks.append((rule, recorded_hash, yaml_text))
        i = after_fence + 1

    return blocks


def test_finds_exactly_the_expected_generated_blocks():
    blocks = _find_generated_blocks(_read_doc())
    found_rules = [b[0] for b in blocks]
    assert found_rules == EXPECTED_RULES, (
        f"expected generated blocks for {EXPECTED_RULES} in that order, found {found_rules} "
        "-- did a marker get dropped, renamed, or reordered?"
    )


def test_generated_blocks_match_their_recorded_hash():
    blocks = _find_generated_blocks(_read_doc())
    assert blocks, "no generated blocks found in docs/cloud-security/code-security/pull-requests.md"

    for rule, recorded_hash, yaml_text in blocks:
        actual_hash = hashlib.sha256(yaml_text.encode("utf-8")).hexdigest()
        assert actual_hash == recorded_hash, (
            f"rule {rule}: the fenced YAML's sha256 ({actual_hash}) does not match the hash "
            f"recorded in its marker ({recorded_hash}) -- it was hand-edited without "
            "regenerating. Regenerate it from the canonical rule definition and paste the "
            "block back in, markers included."
        )


def test_a_hand_edit_is_actually_detected():
    """The guard for the guard: prove the hash check can fail, not just that it currently
    passes. A one-character edit to a real block's YAML (not the marker) must be caught."""
    doc_text = _read_doc()
    blocks = _find_generated_blocks(doc_text)
    rule, recorded_hash, yaml_text = next(b for b in blocks if b[0] == "cloudsec-code-push-rescan")

    tampered_yaml = yaml_text.replace("refs/heads/", "refs/head/")
    assert tampered_yaml != yaml_text

    tampered_hash = hashlib.sha256(tampered_yaml.encode("utf-8")).hexdigest()
    assert tampered_hash != recorded_hash


def test_the_pull_request_number_is_a_path_not_a_template():
    """The regression class this whole guard exists for: a `{{ }}`-templated pull-request
    number renders to a string, and the endpoint it is sent to declares it as an integer, so
    the request is refused before anything runs -- silently, from the pull request's point
    of view. Assert the fix directly, not just indirectly through the hash."""
    blocks = _find_generated_blocks(_read_doc())
    for rule in ("cloudsec-code-pr-check", "cloudsec-code-pr-retarget"):
        yaml_text = next(b[2] for b in blocks if b[0] == rule)
        assert "pr: event.pull_request.number" in yaml_text, rule
        assert not re.search(r"pr:\s*['\"]\{\{", yaml_text), rule


def test_dedent_example():
    """Documents the indent-handling contract with a tiny, self-contained example, since the
    real blocks' indentation is easy to get wrong silently: three spaces because they sit in
    a numbered list item, zero because one of the three does not."""
    fake_doc = textwrap.dedent(
        """\
        1. Some step.

           <!-- generated from x; rule=cloudsec-code-push-rescan; sha256={hash}; do not edit -->
           ```yaml
           a: b
           ```
           <!-- end generated: cloudsec-code-push-rescan -->
        """
    ).format(hash=hashlib.sha256(b"a: b").hexdigest())

    blocks = _find_generated_blocks(fake_doc)
    assert len(blocks) == 1
    rule, recorded_hash, yaml_text = blocks[0]
    assert yaml_text == "a: b"
    assert hashlib.sha256(yaml_text.encode("utf-8")).hexdigest() == recorded_hash
