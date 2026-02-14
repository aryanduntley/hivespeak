"""HiveTalk Parser — transforms token list into AST.

AST nodes are tagged tuples: ("TYPE", ...fields)
Pure functional — parse(tokens) -> ast_nodes list.
"""

from .lexer import (
    T_INT, T_FLOAT, T_STRING, T_BOOL, T_NULL, T_SYM, T_KW, T_HASH,
    T_LPAREN, T_RPAREN, T_LBRACK, T_RBRACK, T_LBRACE, T_RBRACE,
    T_QUOTE, T_UNQUOTE, T_SPLICE, T_PIPE, T_EOF,
)

# AST node constructors — just tuple builders for consistency
def n_int(v):    return ("INT", v)
def n_float(v):  return ("FLOAT", v)
def n_str(v):    return ("STR", v)
def n_bool(v):   return ("BOOL", v)
def n_null():    return ("NULL",)
def n_sym(v):    return ("SYM", v)
def n_kw(v):     return ("KW", v)
def n_hash(v):   return ("HASH", v)
def n_list(v):   return ("LIST", v)
def n_map(v):    return ("MAP", v)
def n_sexpr(v):  return ("SEXPR", v)
def n_quote(v):  return ("QUOTE", v)
def n_unquote(v): return ("UNQUOTE", v)
def n_splice(v): return ("SPLICE", v)


def _tok_type(tokens, pos):
    return tokens[pos][0]


def _tok_val(tokens, pos):
    return tokens[pos][1]


def _tok_loc(tokens, pos):
    return tokens[pos][2], tokens[pos][3]


def _err(msg, tokens, pos):
    line, col = _tok_loc(tokens, pos)
    return SyntaxError(f"{msg} at line {line}, col {col}")


# Atom parsers — one dict lookup to map token type → AST constructor
_ATOM_MAP = {
    T_INT:    lambda v: n_int(v),
    T_FLOAT:  lambda v: n_float(v),
    T_STRING: lambda v: n_str(v),
    T_BOOL:   lambda v: n_bool(v),
    T_NULL:   lambda _: n_null(),
    T_SYM:    lambda v: n_sym(v),
    T_KW:     lambda v: n_kw(v),
    T_HASH:   lambda v: n_hash(v),
}


def _parse_expr(tokens, pos):
    """Parse one expression. Returns (ast_node, new_pos)."""
    tt = _tok_type(tokens, pos)

    # Atoms — direct lookup
    if tt in _ATOM_MAP:
        return _ATOM_MAP[tt](_tok_val(tokens, pos)), pos + 1

    # S-expression: (...)
    if tt == T_LPAREN:
        return _parse_delimited(tokens, pos + 1, T_RPAREN, n_sexpr)

    # List literal: [...]
    if tt == T_LBRACK:
        return _parse_delimited(tokens, pos + 1, T_RBRACK, n_list)

    # Map literal: {...}
    if tt == T_LBRACE:
        return _parse_delimited(tokens, pos + 1, T_RBRACE, n_map)

    # Quote: 'expr
    if tt == T_QUOTE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_quote(inner), pos

    # Unquote: ~expr
    if tt == T_UNQUOTE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_unquote(inner), pos

    # Splice: ~@expr
    if tt == T_SPLICE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_splice(inner), pos

    # Pipe operator |> (treat as symbol in expression position)
    if tt == T_PIPE:
        return n_sym("|>"), pos + 1

    raise _err(f"Unexpected token {tt}({_tok_val(tokens, pos)})", tokens, pos)


def _parse_delimited(tokens, pos, end_token, wrapper_fn):
    """Parse expressions until end_token. Returns (wrapped_node, new_pos)."""
    elements = []
    while _tok_type(tokens, pos) != end_token:
        if _tok_type(tokens, pos) == T_EOF:
            raise _err(f"Expected {end_token}, got EOF", tokens, pos)
        node, pos = _parse_expr(tokens, pos)
        elements.append(node)
    return wrapper_fn(elements), pos + 1  # skip closing delimiter


def parse(tokens):
    """Parse a token list into a list of AST nodes (top-level expressions)."""
    nodes = []
    pos = 0
    while _tok_type(tokens, pos) != T_EOF:
        node, pos = _parse_expr(tokens, pos)
        nodes.append(node)
    return nodes
