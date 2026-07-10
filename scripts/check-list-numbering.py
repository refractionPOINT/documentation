#!/usr/bin/env python3
"""Detect ordered lists whose numbering visibly restarts due to fragmentation.

Python-Markdown (what MkDocs renders with) requires 4-space indentation to keep
content inside a list item. When continuation content (an image, code block, or
paragraph) under an item is indented by less than that, the item ends early and
the list splits into several sibling ``<ol>`` blocks. Python-Markdown emits no
``start=`` attribute, so every fragment restarts at 1 - the visible "wacky
numbering" bug (e.g. a step the author wrote as "6." rendering as a fresh "1.").

Why this check is free of false positives
-----------------------------------------
The hard part is telling an ACCIDENTAL fragmentation from two INTENTIONAL
adjacent ordered lists - both look identical in the rendered HTML. The tie
breaker is the author's own numbering in the Markdown source:

  * intentional second list  -> the author wrote "1." (a deliberate restart)
  * accidental fragmentation -> the author wrote "2." / "3." / ... (renders as 1)

So a fragment is reported ONLY when its first item's text maps back to a source
ordered marker whose number is greater than 1 *everywhere it appears*. An item
the author numbered >1 must never be the first item of its rendered list, so a
hit is unambiguous. Fragments whose first item has no matchable text (it starts
with an image or code block) are skipped rather than guessed - the check would
rather miss an ambiguous case than raise a false alarm.

This deliberately does NOT flag:
  * lists written entirely with "1." markers relying on auto-numbering (genuinely
    ambiguous - could be one list or several intentional ones), or
  * nested lists that merely flatten while keeping sequential numbers.
Those need human judgement; a heuristic for them produces false positives.

Usage
-----
Run after ``mkdocs build`` (it reads the rendered ``site/`` and the ``docs/``
source):

    python scripts/check-list-numbering.py            # docs/ + site/
    python scripts/check-list-numbering.py docs site  # explicit paths

Options:
    --baseline FILE         Ignore findings listed in FILE (known, accepted debt);
                            exit non-zero only on findings NOT in the baseline.
    --update-baseline FILE  Write the current findings to FILE and exit 0.

Exit code is 1 when any non-baselined numbering break is found, else 0.
"""
import argparse
import json
import os
import re
import sys
import glob
from html.parser import HTMLParser

VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'col'}
HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
ORDERED = re.compile(r'^\s*(\d+)[.)]\s+(.*)')


def normalize(text):
    """Reduce item text to a stable key for matching source against rendered."""
    text = text.lower()
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)  # [label](url) -> label
    text = re.sub(r'[`*_~]+', '', text)                    # strip inline marks
    text = re.sub(r'[^a-z0-9 ]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()[:40]


def source_ordinals(md_path):
    """Map normalized item text -> set of source ordinals (outside fenced code)."""
    out = {}
    fence = None
    with open(md_path, encoding='utf-8') as fh:
        for raw in fh:
            line = raw.rstrip('\n')
            if fence is not None:
                s = line.strip()
                if s and set(s) == {fence[0]} and len(s) >= fence[1]:
                    fence = None
                continue
            fm = FENCE.match(line)
            if fm:
                fence = (fm.group(1)[0], len(fm.group(1)))
                continue
            m = ORDERED.match(line)
            if m:
                key = normalize(m.group(2))
                if key:
                    out.setdefault(key, set()).add(int(m.group(1)))
    return out


class Tree(HTMLParser):
    """Tolerant HTML-to-tree parser (only the structure we need)."""

    def __init__(self):
        super().__init__()
        self.root = {'tag': 'root', 'children': [], 'text': ''}
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': [], 'text': ''}
        self.stack[-1]['children'].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1]['children'].append({'tag': tag, 'attrs': dict(attrs), 'children': [], 'text': ''})

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data.strip():
            self.stack[-1]['text'] += ' ' + data.strip()


def find_content(node):
    """Return the page's main content node, ignoring theme nav/TOC lists."""
    if node['tag'] in ('article', 'main'):
        return node
    for child in node['children']:
        found = find_content(child)
        if found:
            return found
    return None


def _text_before_nested_list(node):
    # Include the node's own direct text (a tight-list <li> holds its text
    # directly; a loose-list <li> wraps it in a child <p>), then descend into
    # children until the item's nested list begins.
    parts = [node['text']] if node['text'] else []
    for child in node['children']:
        if child['tag'] in ('ol', 'ul'):
            break
        parts.append(_text_before_nested_list(child))
    return ' '.join(p for p in parts if p)


def first_item_text(ol):
    for child in ol['children']:
        if child['tag'] == 'li':
            return normalize(_text_before_nested_list(child))
    return ''


def sibling_ol_runs(node):
    """Yield lists of >=2 <ol> siblings not separated by a heading."""
    run = []
    for child in node['children']:
        if child['tag'] == 'ol':
            run.append(child)
        elif child['tag'] in HEADINGS:
            if len(run) >= 2:
                yield run
            run = []
    if len(run) >= 2:
        yield run
    for child in node['children']:
        yield from sibling_ol_runs(child)


def find_breaks(md_path, html_path):
    """Return [(source_ordinal, item_text), ...] for confirmed numbering breaks."""
    ordinals = source_ordinals(md_path)
    tree = Tree()
    with open(html_path, encoding='utf-8') as fh:
        tree.feed(fh.read())
    content = find_content(tree.root) or tree.root
    breaks = []
    for run in sibling_ol_runs(content):
        for ol in run[1:]:  # the first fragment may legitimately start at 1
            text = first_item_text(ol)
            if not text:
                continue
            nums = ordinals.get(text)
            if nums and min(nums) > 1:  # authored >1 everywhere -> must not be a list start
                breaks.append((min(nums), text))
    return breaks


def html_for(md_relpath, site):
    stem = md_relpath[:-3] if md_relpath.endswith('.md') else md_relpath
    page_dir = os.path.dirname(stem) if os.path.basename(stem) == 'index' else stem
    return os.path.join(site, page_dir, 'index.html')


def collect(docs, site):
    findings = {}
    for md in sorted(glob.glob(os.path.join(docs, '**', '*.md'), recursive=True)):
        rel = os.path.relpath(md, docs)
        html = html_for(rel, site)
        if not os.path.exists(html):
            continue
        breaks = find_breaks(md, html)
        if breaks:
            findings[rel] = breaks
    return findings


def as_baseline_keys(findings):
    return sorted({f"{page}::{num}::{text}" for page, breaks in findings.items() for num, text in breaks})


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('docs', nargs='?', default='docs')
    parser.add_argument('site', nargs='?', default='site')
    parser.add_argument('--baseline')
    parser.add_argument('--update-baseline')
    args = parser.parse_args(argv[1:])

    if not os.path.isdir(args.site):
        print(f"error: rendered site not found at '{args.site}'. Run `mkdocs build` first.", file=sys.stderr)
        return 2

    findings = collect(args.docs, args.site)

    if args.update_baseline:
        with open(args.update_baseline, 'w', encoding='utf-8') as fh:
            json.dump(as_baseline_keys(findings), fh, indent=2)
            fh.write('\n')
        print(f"wrote baseline with {len(as_baseline_keys(findings))} entr(y/ies) to {args.update_baseline}")
        return 0

    baseline = set()
    if args.baseline and os.path.exists(args.baseline):
        with open(args.baseline, encoding='utf-8') as fh:
            baseline = set(json.load(fh))

    new_count = 0
    for page in sorted(findings):
        rows = [(num, text) for num, text in findings[page] if f"{page}::{num}::{text}" not in baseline]
        if not rows:
            continue
        new_count += len(rows)
        print(f"\n{page}")
        for num, text in rows:
            print(f"  numbering break: author wrote #{num} but it renders as a restarted '1.' -> {text!r}")

    baselined = sum(len(b) for b in findings.values()) - new_count
    print(f"\n=== {new_count} new numbering break(s); {baselined} baselined; {len(findings)} affected page(s) ===")
    if new_count:
        print("Fix by indenting the item's continuation content to 4 spaces so the list "
              "stays intact, or (if intentional) restart the source numbering at 1.", file=sys.stderr)
    return 1 if new_count else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
