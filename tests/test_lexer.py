"""Tests for the HiveSpeak lexer."""

import pytest
from compiler.lexer import tokenize, T_INT, T_FLOAT, T_STRING, T_BOOL, T_NULL
from compiler.lexer import T_SYM, T_KW, T_HASH, T_LPAREN, T_RPAREN
from compiler.lexer import T_LBRACK, T_RBRACK, T_LBRACE, T_RBRACE
from compiler.lexer import T_QUOTE, T_UNQUOTE, T_SPLICE, T_PIPE, T_EOF


def toks(src):
    """Tokenize and strip EOF for easier assertions."""
    return [(t, v) for t, v, _l, _c in tokenize(src) if t != T_EOF]


def tok_types(src):
    return [t for t, v in toks(src)]


# ─── Literals ─────────────────────────────────────────────────────────────

def test_integer():
    assert toks("42") == [(T_INT, 42)]

def test_negative_integer():
    assert toks("-7") == [(T_INT, -7)]

def test_float():
    assert toks("3.14") == [(T_FLOAT, 3.14)]

def test_negative_float():
    assert toks("-2.5") == [(T_FLOAT, -2.5)]

def test_string():
    assert toks('"hello"') == [(T_STRING, "hello")]

def test_string_escapes():
    assert toks(r'"a\nb"') == [(T_STRING, "a\nb")]
    assert toks(r'"a\tb"') == [(T_STRING, "a\tb")]
    assert toks(r'"a\"b"') == [(T_STRING, 'a"b')]

def test_bool_true():
    assert toks("T") == [(T_BOOL, True)]

def test_bool_false():
    assert toks("F") == [(T_BOOL, False)]

def test_null():
    assert toks("N") == [(T_NULL, None)]


# ─── Symbols & Keywords ──────────────────────────────────────────────────

def test_symbol():
    assert toks("foo") == [(T_SYM, "foo")]

def test_symbol_with_special_chars():
    assert toks("fn?") == [(T_SYM, "fn?")]
    assert toks("assert!") == [(T_SYM, "assert!")]
    assert toks("|>") == [(T_PIPE, "|>")]

def test_keyword():
    assert toks(":name") == [(T_KW, "name")]
    assert toks(":age") == [(T_KW, "age")]

def test_hash():
    assert toks("#abc123") == [(T_HASH, "abc123")]


# ─── Delimiters ──────────────────────────────────────────────────────────

def test_parens():
    assert tok_types("()") == [T_LPAREN, T_RPAREN]

def test_brackets():
    assert tok_types("[]") == [T_LBRACK, T_RBRACK]

def test_braces():
    assert tok_types("{}") == [T_LBRACE, T_RBRACE]

def test_quote():
    assert tok_types("'x") == [T_QUOTE, T_SYM]

def test_unquote():
    assert tok_types(",x") == [T_UNQUOTE, T_SYM]

def test_splice():
    assert tok_types(",@x") == [T_SPLICE, T_SYM]

def test_tilde_as_symbol():
    assert toks("~") == [(T_SYM, "~")]
    # ~ inside an s-expression
    result = toks("(~ :temp 68)")
    assert result[1] == (T_SYM, "~")


# ─── Whitespace & Comments ───────────────────────────────────────────────

def test_whitespace_ignored():
    assert toks("  42  ") == [(T_INT, 42)]

def test_comments_ignored():
    assert toks("; this is a comment\n42") == [(T_INT, 42)]

def test_inline_comment():
    assert toks("42 ; the answer") == [(T_INT, 42)]


# ─── Composite ───────────────────────────────────────────────────────────

def test_sexpr():
    result = toks("(add 1 2)")
    assert result == [
        (T_LPAREN, "("), (T_SYM, "add"), (T_INT, 1), (T_INT, 2), (T_RPAREN, ")")
    ]

def test_nested_sexpr():
    result = toks("(add (* 2 3) 4)")
    assert len(result) == 9

def test_list_literal():
    result = toks("[1 2 3]")
    assert result == [
        (T_LBRACK, "["), (T_INT, 1), (T_INT, 2), (T_INT, 3), (T_RBRACK, "]")
    ]

def test_map_literal():
    result = toks("{:a 1}")
    assert result == [
        (T_LBRACE, "{"), (T_KW, "a"), (T_INT, 1), (T_RBRACE, "}")
    ]


# ─── Source Location Tracking ────────────────────────────────────────────

def test_line_col_tracking():
    tokens = tokenize("42\n(+ 1 2)")
    assert tokens[0] == (T_INT, 42, 1, 1)
    assert tokens[1] == (T_LPAREN, "(", 2, 1)
    assert tokens[2] == (T_SYM, "+", 2, 2)
    assert tokens[3] == (T_INT, 1, 2, 4)
    assert tokens[4] == (T_INT, 2, 2, 6)


# ─── Errors ──────────────────────────────────────────────────────────────

def test_unterminated_string():
    with pytest.raises(SyntaxError, match="Unterminated string"):
        tokenize('"oops')

def test_unexpected_char():
    with pytest.raises(SyntaxError, match="Unexpected character"):
        tokenize("@")


# ─── Edge Cases ──────────────────────────────────────────────────────────

def test_empty_source():
    assert toks("") == []

def test_only_comments():
    assert toks("; nothing here") == []

def test_pipe_operator():
    assert toks("|>") == [(T_PIPE, "|>")]

def test_multiple_expressions():
    result = toks("42 \"hi\" T")
    assert result == [(T_INT, 42), (T_STRING, "hi"), (T_BOOL, True)]
