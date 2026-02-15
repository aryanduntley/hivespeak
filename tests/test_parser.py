"""Tests for the HiveSpeak parser."""

import pytest
from compiler.lexer import tokenize
from compiler.parser import parse, node_loc


def ast(src):
    """Parse source and return AST node list."""
    return parse(tokenize(src))


def ast1(src):
    """Parse source expecting a single expression, return that node."""
    nodes = ast(src)
    assert len(nodes) == 1
    return nodes[0]


def nv(node):
    """Extract (type, value) from an AST node, ignoring source location."""
    return (node[0], node[1])


# ─── Atoms ────────────────────────────────────────────────────────────────

def test_int():
    assert nv(ast1("42")) == ("INT", 42)

def test_float():
    assert nv(ast1("3.14")) == ("FLOAT", 3.14)

def test_string():
    assert nv(ast1('"hello"')) == ("STR", "hello")

def test_bool():
    assert nv(ast1("T")) == ("BOOL", True)
    assert nv(ast1("F")) == ("BOOL", False)

def test_null():
    assert nv(ast1("N")) == ("NULL", None)

def test_symbol():
    assert nv(ast1("foo")) == ("SYM", "foo")

def test_keyword():
    assert nv(ast1(":name")) == ("KW", "name")

def test_hash():
    assert nv(ast1("#abc")) == ("HASH", "abc")


# ─── Source locations on atoms ───────────────────────────────────────────

def test_atom_has_loc():
    node = ast1("42")
    assert node_loc(node) == (1, 1)

def test_multiline_loc():
    nodes = ast("42\n(add 1 2)")
    assert node_loc(nodes[0]) == (1, 1)
    assert node_loc(nodes[1]) == (2, 1)
    # The add symbol inside the sexpr
    add_sym = nodes[1][1][0]
    assert node_loc(add_sym) == (2, 2)


# ─── Compound ────────────────────────────────────────────────────────────

def test_sexpr():
    node = ast1("(add 1 2)")
    assert node[0] == "SEXPR"
    children = node[1]
    assert nv(children[0]) == ("SYM", "add")
    assert nv(children[1]) == ("INT", 1)
    assert nv(children[2]) == ("INT", 2)

def test_nested_sexpr():
    node = ast1("(add (* 2 3) 4)")
    assert node[0] == "SEXPR"
    inner = node[1][1]
    assert inner[0] == "SEXPR"
    assert nv(inner[1][0]) == ("SYM", "*")
    assert nv(inner[1][1]) == ("INT", 2)
    assert nv(inner[1][2]) == ("INT", 3)

def test_list():
    node = ast1("[1 2 3]")
    assert node[0] == "LIST"
    assert [nv(c) for c in node[1]] == [("INT", 1), ("INT", 2), ("INT", 3)]

def test_empty_list():
    node = ast1("[]")
    assert node[0] == "LIST"
    assert node[1] == []

def test_map():
    node = ast1("{:a 1}")
    assert node[0] == "MAP"
    assert nv(node[1][0]) == ("KW", "a")
    assert nv(node[1][1]) == ("INT", 1)

def test_empty_map():
    node = ast1("{}")
    assert node[0] == "MAP"
    assert node[1] == []

def test_quote():
    node = ast1("'x")
    assert node[0] == "QUOTE"
    assert nv(node[1]) == ("SYM", "x")

def test_unquote():
    node = ast1(",x")
    assert node[0] == "UNQUOTE"
    assert nv(node[1]) == ("SYM", "x")

def test_splice():
    node = ast1(",@x")
    assert node[0] == "SPLICE"
    assert nv(node[1]) == ("SYM", "x")

def test_tilde_as_symbol():
    node = ast1("(~ :temp 68)")
    assert node[0] == "SEXPR"
    assert nv(node[1][0]) == ("SYM", "~")


# ─── Multiple expressions ───────────────────────────────────────────────

def test_multiple_top_level():
    nodes = ast("42 (add 1 2)")
    assert len(nodes) == 2
    assert nv(nodes[0]) == ("INT", 42)
    assert nodes[1][0] == "SEXPR"


# ─── Complex forms ───────────────────────────────────────────────────────

def test_def_function():
    node = ast1("(def (square n) (* n n))")
    assert node[0] == "SEXPR"
    assert nv(node[1][0]) == ("SYM", "def")

def test_fn():
    node = ast1("(fn [x] (* x x))")
    assert node[0] == "SEXPR"
    assert nv(node[1][0]) == ("SYM", "fn")
    params = node[1][1]
    assert params[0] == "LIST"
    assert nv(params[1][0]) == ("SYM", "x")

def test_let():
    node = ast1("(let [a 1 b 2] (add a b))")
    assert node[0] == "SEXPR"
    bindings = node[1][1]
    assert bindings[0] == "LIST"
    assert len(bindings[1]) == 4  # a, 1, b, 2

def test_if():
    node = ast1("(if T 1 2)")
    assert node[0] == "SEXPR"
    assert len(node[1]) == 4  # if, T, 1, 2

def test_pipe():
    node = ast1("(|> x f g)")
    assert node[0] == "SEXPR"
    assert nv(node[1][0]) == ("SYM", "|>")


# ─── Errors ──────────────────────────────────────────────────────────────

def test_unmatched_paren():
    with pytest.raises(SyntaxError, match="Expected"):
        ast("(+ 1 2")

def test_unexpected_rparen():
    with pytest.raises(SyntaxError, match="Unexpected token"):
        ast(")")


# ─── Deep nesting ────────────────────────────────────────────────────────

def test_deeply_nested():
    src = "(a (b (c (d 1))))"
    node = ast1(src)
    assert node[0] == "SEXPR"
    level2 = node[1][1]
    assert level2[0] == "SEXPR"
    level3 = level2[1][1]
    assert level3[0] == "SEXPR"
    level4 = level3[1][1]
    assert level4[0] == "SEXPR"
    assert nv(level4[1][1]) == ("INT", 1)
