"""Tests for the LCQL Pygments lexer (``hooks/lcql_lexer.py``).

The token vocabulary asserted here mirrors the LimaCharlie Query Language
(LCQL). The categories covered are:

* Comparison operators: ``==``/``is``, ``!=``/``is not``, ``contains``,
  ``matches``, ``starts with``, ``ends with``, ``cidr``, ``<``/``is lower than``,
  ``>``/``is greater than`` (and their ``not`` variants)
* Valueless operators: ``exists``, ``scope``, ``is public address`` /
  ``is private address`` (and ipv4/ipv6 variants)
* Platform and tag operators: ``is platform``, ``is tagged``
* Stateful operators: ``with child``, ``with descendant``, ``with events``
* Boolean operators: ``and`` (``&&``), ``or`` (``||``), ``not`` (``!``)
* Aggregation functions: ``COUNT``, ``COUNT_UNIQUE``
* Projection / sorting / limiting: ``AS``, ``GROUP BY``, ``ORDER BY``,
  ``LIMIT``, ``asc``, ``desc``
* Bounded time ranges: ``to``

Keep the lists below in sync with the query language: when LCQL gains an
operator or keyword, add it here so the lexer is verified to highlight it. The
lexer is cosmetic, so these tests guard highlighting coverage, not query
semantics.
"""

import os
import sys

import pytest
from pygments.token import Error, Keyword, Name, Number, Operator, String

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from lcql_lexer import LCQLLexer  # noqa: E402


# Word-form operators and keywords (multi-word operators such as "starts with"
# are tokenized word by word). Note: "in" comes from the sensor-selector
# expression syntax and "to" from the time-range syntax; both still appear in
# real LCQL queries.
GRAMMAR_KEYWORDS = [
    "and", "or", "not", "with", "child", "descendant", "events",
    "contains", "starts", "ends", "matches", "is", "cidr", "exists",
    "public", "private", "address", "ipv4", "ipv6", "platform", "tagged",
    "scope", "in", "to", "greater", "lower", "than",
]
# Projection / sorting / limiting keywords.
GRAMMAR_PROJECTION = ["AS", "GROUP", "BY", "ORDER", "LIMIT", "asc", "desc"]
# Aggregation functions.
GRAMMAR_AGGREGATIONS = ["COUNT", "COUNT_UNIQUE"]
# Symbolic operators: comparison (==, !=, >, <) and boolean (&&, ||, !).
GRAMMAR_SYMBOLIC_OPERATORS = ["==", "!=", ">", "<", "&&", "||", "!"]

# Representative queries drawn from the documentation. They must tokenize
# cleanly (no Error tokens) to prove the lexer covers real LCQL.
EXAMPLE_QUERIES = [
    "-24h | plat == windows | * | event/* contains 'psexec'",
    "-24h | plat == windows | WEL | event/EVENT/EventData/* contains \"administrator\"",
    "-1h | * | NETWORK_CONNECTIONS | event/IP_ADDRESS is public address and "
    "event/PORT > 1024 | event/IP_ADDRESS as IP COUNT(event) as c "
    "GROUP BY(IP) ORDER BY(c desc) LIMIT 50",
    "-6h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with \"cmd.exe\" "
    "with child (event/FILE_PATH ends with \"calc.exe\")",
    "-24h to -12h | 1a2b3c4d-1111-2222-3333-444455556666 | NEW_PROCESS | "
    "event/FILE_PATH ends with \".exe\"",
]


def _first_significant_token(text):
    """Return the (token_type, value) of the first non-whitespace token."""
    for tok, val in LCQLLexer().get_tokens(text):
        if val.strip():
            return tok, val
    raise AssertionError(f"no significant token produced for {text!r}")


@pytest.mark.parametrize("keyword", GRAMMAR_KEYWORDS)
def test_grammar_keyword_is_highlighted(keyword):
    tok, _ = _first_significant_token(keyword)
    assert tok in Keyword, f"{keyword!r} tokenized as {tok}, expected a Keyword"


@pytest.mark.parametrize("keyword", GRAMMAR_PROJECTION)
def test_projection_keyword_is_highlighted(keyword):
    tok, _ = _first_significant_token(keyword)
    assert tok in Keyword, f"{keyword!r} tokenized as {tok}, expected a Keyword"


@pytest.mark.parametrize("agg", GRAMMAR_AGGREGATIONS)
def test_aggregation_function_is_highlighted(agg):
    # Only recognized in call position, e.g. COUNT(event).
    tok, val = _first_significant_token(f"{agg}(event)")
    assert tok in Name.Function, f"{agg!r} tokenized as {tok}, expected Name.Function"
    assert val == agg, f"aggregation split: got {val!r}, expected {agg!r}"


@pytest.mark.parametrize("op", GRAMMAR_SYMBOLIC_OPERATORS)
def test_symbolic_operator_is_highlighted(op):
    tok, _ = _first_significant_token(op)
    assert tok in Operator, f"{op!r} tokenized as {tok}, expected Operator"


def test_field_path_is_name_variable():
    tok, val = _first_significant_token("event/EVENT/EventData/TargetUserName")
    assert tok in Name.Variable
    assert val == "event/EVENT/EventData/TargetUserName"


def test_subtree_wildcard_path():
    tok, val = _first_significant_token("event/EVENT/EventData/*")
    assert tok in Name.Variable
    assert val == "event/EVENT/EventData/*"


def test_double_quoted_string_is_case_insensitive_literal():
    tok, _ = _first_significant_token('"temp"')
    assert tok in String


def test_single_quoted_string_is_case_sensitive_literal():
    tok, _ = _first_significant_token("'Temp'")
    assert tok in String


@pytest.mark.parametrize("duration", ["-24h", "-90m", "-1h30m", "-168h"])
def test_relative_duration_is_number(duration):
    tok, _ = _first_significant_token(duration)
    assert tok in Number


def test_sensor_id_stays_a_single_token():
    uuid = "1a2b3c4d-1111-2222-3333-444455556666"
    tok, val = _first_significant_token(uuid)
    assert tok in Name.Constant
    assert val == uuid


@pytest.mark.parametrize("query", EXAMPLE_QUERIES)
def test_example_queries_have_no_error_tokens(query):
    tokens = list(LCQLLexer().get_tokens(query))
    assert all(tok is not Error for tok, _ in tokens), (
        f"query produced Error tokens: {query!r}"
    )
