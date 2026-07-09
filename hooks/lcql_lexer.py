"""MkDocs hook: register a Pygments lexer for LimaCharlie Query Language (LCQL).

This enables ```lcql fenced code blocks to be syntax-highlighted by
``pymdownx.highlight`` (which resolves languages through
``pygments.lexers.get_lexer_by_name``).

The lexer is injected directly into Pygments' in-process registry rather than
shipped as an installed entry-point package: we pre-populate the lexer cache
under the class name and add a matching entry to the alias mapping, so
``get_lexer_by_name("lcql")`` returns it without importing anything. Registration
runs both at import time and in ``on_config`` so it is in place before any page
is rendered, regardless of hook-loading order.

Contract: highlighting is purely cosmetic. If registration ever fails,
``pymdownx.highlight`` falls back to plain (unhighlighted) text, so a ```lcql
block never breaks the build.
"""

from pygments.lexer import RegexLexer, words
from pygments.token import (
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)


class LCQLLexer(RegexLexer):
    """Pygments lexer for LimaCharlie Query Language (LCQL).

    Tokenizes the five-part pipe structure (time | sensor selector | event
    types | filter | projection): field paths (``event/...``, ``routing/...``),
    string/number literals, comparison and stateful operators, boolean
    keywords, aggregation functions, and the projection keywords. The final
    catch-all rule guarantees the lexer never emits an error token.
    """

    name = "LCQL"
    aliases = ["lcql"]
    filenames: list[str] = []

    # Word-form operators and keywords from the filter, boolean, and stateful
    # grammar, plus "in" (bexpr sensor selector) and "to" (time range). Multi-word
    # operators such as "starts with" are matched as individual words.
    _keywords = (
        "and", "or", "not", "with", "child", "descendant", "events",
        "contains", "starts", "ends", "matches", "is", "cidr", "exists",
        "public", "private", "address", "ipv4", "ipv6", "platform",
        "tagged", "scope", "in", "to", "greater", "lower", "than",
    )
    # Projection / sorting / limiting keywords.
    _projection = ("AS", "GROUP", "BY", "ORDER", "LIMIT", "asc", "desc")
    # Aggregation functions (longest first so COUNT_UNIQUE wins over COUNT).
    _aggregations = ("COUNT_UNIQUE", "COUNT")

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"\|\|", Operator),
            (r"\|", Punctuation),
            (r"[()]", Punctuation),
            (r'"[^"]*"', String.Double),
            (r"'[^']*'", String.Single),
            # Sensor IDs (UUIDs) before the number rule so they stay intact.
            (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
             Name.Constant),
            (words(_aggregations, suffix=r"(?=\()"), Name.Function),
            (words(_projection, prefix=r"\b", suffix=r"\b"), Keyword.Declaration),
            (words(_keywords, prefix=r"\b", suffix=r"\b"), Keyword),
            (r"==|!=|>|<|&&|!|\*", Operator),
            # Relative time durations, including compound Go durations, e.g.
            # -24h, -10m, -1h30m, -1h30m45s. (Bare integers are matched below.)
            (r"-?(?:\d+(?:\.\d+)?(?:ns|us|ms|[smhdwy]))+", Number),
            # Field paths containing at least one slash segment.
            (r"[A-Za-z_][A-Za-z0-9_]*(?:/[A-Za-z0-9_*?]+(?:\[\d+\])?)+",
             Name.Variable),
            # Bare identifiers: event types, platform values, aliases.
            (r"[A-Za-z_][A-Za-z0-9_.]*", Name),
            (r"\d+", Number),
            # Catch-all so an unexpected character never produces an error token.
            (r".", Text),
        ],
    }


def _register() -> None:
    """Make ``get_lexer_by_name("lcql")`` resolve to :class:`LCQLLexer`."""
    from pygments.lexers import LEXERS, _lexer_cache

    _lexer_cache["LCQL"] = LCQLLexer
    # (module, class display name, aliases, filename globs, mimetypes). The
    # module is empty because the class is already cached, so no import occurs.
    LEXERS["LCQLLexer"] = ("", "LCQL", ("lcql",), (), ())


_register()


def on_config(config):
    """MkDocs hook entry point; re-register defensively before pages render."""
    _register()
    return config
