# Markdown Linting

This repo's CI runs [`markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2)
against every file under `docs/` (see `.github/workflows/link-checker.yml`,
job `check-markdown`). The job is currently `continue-on-error: true`, so
violations are reported but do not block merges.

This doc explains how to run the linter locally, interpret the output, and
make progress on the backlog so the check can eventually be enforced.

## Prerequisites

You need `node` / `npx` available (any modern version). Nothing else needs
to be installed — `npx` will fetch `markdownlint-cli2` on demand.

## Run the linter

From the repo root:

```bash
# Lint everything under docs/
npx --yes markdownlint-cli2 \
  --config .markdownlint.json \
  "docs/**/*.md"
```

If `.markdownlint.json` does not exist yet, use the same config the CI job
uses inline:

```bash
npx --yes markdownlint-cli2 \
  --config <(echo '{"default": true, "MD013": false, "MD033": false, "MD041": false}') \
  "docs/**/*.md"
```

Lint a single file or subtree:

```bash
npx --yes markdownlint-cli2 "docs/3-detection-response/**/*.md"
npx --yes markdownlint-cli2 "docs/index.md"
```

### Auto-fix what's mechanical

A large fraction of violations (bullet style, table alignment, blank lines
around fences, etc.) are stylistic and can be fixed automatically:

```bash
npx --yes markdownlint-cli2 --fix "docs/**/*.md"
```

Always review the diff before committing — `--fix` is safe in practice but
it will touch a lot of files.

## Reading the output

Each line looks like:

```
docs/path/to/file.md:42:1 MD040/fenced-code-language Fenced code blocks should have a language specified
```

- `docs/path/to/file.md:42:1` — file, line, column
- `MD040/fenced-code-language` — rule ID and slug
- The rest is the human-readable description

Rule documentation: <https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md>.

## Categories of violations

When triaging the backlog, group violations into two buckets:

**Cosmetic (auto-fixable)** — `--fix` resolves these without content
changes. Examples:

- `MD004` (bullet style consistency)
- `MD031` / `MD032` (blank lines around fences/lists)
- `MD046` (code block style)
- `MD060` (table column alignment)
- `MD029` (ordered list prefix)

**Substantive (manual)** — these need editorial judgment and meaningfully
improve doc quality and AI / LLM readability. Prioritize these:

- `MD040` — code blocks must declare a language (helps highlighting and
  helps LLMs parse examples correctly)
- `MD045` — images must have alt text (accessibility + AI consumers rely
  on alt text)
- `MD051` — anchor links must point to a real heading (catches broken
  intra-page links)
- `MD059` — descriptive link text (avoid "click here")
- `MD024` — no duplicate headings on a page
- `MD036` — don't use bold paragraphs in place of headings
- `MD034` — no bare URLs

## Suggested workflow for the backlog

1. **Land a single mechanical PR** with `--fix`. This typically eliminates
   60–70% of the errors with zero content change.
2. **Pick one substantive rule at a time** and clear it across the repo
   (e.g. add language tags to all fenced blocks for `MD040`). Smaller,
   easier-to-review PRs.
3. **Once a rule is clean, enforce it.** Either drop `continue-on-error`
   from the CI job or add the rule to a stricter `.markdownlint.json` and
   keep the rest disabled until they're cleaned up.

## Using AI to drive this

This work is well-suited to AI assistance — the violations are mechanical,
the fixes are local, and the linter gives unambiguous feedback that the AI
can use to verify its own work. A reasonable workflow:

1. Run `markdownlint-cli2` and save the output to a file:
   ```bash
   npx --yes markdownlint-cli2 "docs/**/*.md" 2> mdlint.out || true
   ```
2. Hand the output to an AI assistant (e.g. Claude Code in this repo) and
   ask it to fix one rule at a time, e.g. *"Fix every `MD040` violation in
   `mdlint.out` by adding the most appropriate language tag to each fenced
   code block. Don't change anything else."*
3. Re-run the linter and confirm the count for that rule has dropped to
   zero before opening a PR.
4. Repeat per rule. Smaller, focused PRs are easier to review than one
   sweeping change.

For the mechanical pass, just running `markdownlint-cli2 --fix` is faster
than involving AI at all — only reach for AI on the substantive rules
that need judgment (alt text, link rewording, anchor fixes, etc.).

## Current state

Run the linter today to see where we stand:

```bash
npx --yes markdownlint-cli2 \
  --config <(echo '{"default": true, "MD013": false, "MD033": false, "MD041": false}') \
  "docs/**/*.md" 2> mdlint.out || true
grep -oE 'MD[0-9]+/[a-z-]+' mdlint.out | sort | uniq -c | sort -rn
```

This gives a sorted breakdown of every rule by violation count and is the
best starting point for prioritizing work.
