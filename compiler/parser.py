"""HiveSpeak Parser — transforms token list into AST.

AST nodes are tagged tuples: ("TYPE", ...fields)
Pure functional — parse(tokens) -> ast_nodes list.
"""

from .lexer import (
    T_INT, T_FLOAT, T_STRING, T_BOOL, T_NULL, T_SYM, T_KW, T_HASH,
    T_LPAREN, T_RPAREN, T_LBRACK, T_RBRACK, T_LBRACE, T_RBRACE,
    T_QUOTE, T_UNQUOTE, T_SPLICE, T_PIPE, T_EOF,
)

# AST node constructors — tuples with optional source location (line, col)
def n_int(v, loc=None):    return ("INT", v, loc)
def n_float(v, loc=None):  return ("FLOAT", v, loc)
def n_str(v, loc=None):    return ("STR", v, loc)
def n_bool(v, loc=None):   return ("BOOL", v, loc)
def n_null(loc=None):      return ("NULL", None, loc)
def n_sym(v, loc=None):    return ("SYM", v, loc)
def n_kw(v, loc=None):     return ("KW", v, loc)
def n_hash(v, loc=None):   return ("HASH", v, loc)
def n_list(v, loc=None):   return ("LIST", v, loc)
def n_map(v, loc=None):    return ("MAP", v, loc)
def n_sexpr(v, loc=None):  return ("SEXPR", v, loc)
def n_quote(v, loc=None):  return ("QUOTE", v, loc)
def n_unquote(v, loc=None): return ("UNQUOTE", v, loc)
def n_splice(v, loc=None): return ("SPLICE", v, loc)

def node_loc(n):
    """Extract source location from AST node. Returns (line, col) or None."""
    if len(n) > 2:
        return n[2]
    return None


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
    T_INT:    n_int,
    T_FLOAT:  n_float,
    T_STRING: n_str,
    T_BOOL:   n_bool,
    T_NULL:   lambda v, loc=None: n_null(loc),
    T_SYM:    n_sym,
    T_KW:     n_kw,
    T_HASH:   n_hash,
}


def _parse_expr(tokens, pos):
    """Parse one expression. Returns (ast_node, new_pos)."""
    tt = _tok_type(tokens, pos)
    loc = _tok_loc(tokens, pos)

    # Atoms — direct lookup
    if tt in _ATOM_MAP:
        return _ATOM_MAP[tt](_tok_val(tokens, pos), loc), pos + 1

    # S-expression: (...)
    if tt == T_LPAREN:
        return _parse_delimited(tokens, pos + 1, T_RPAREN, n_sexpr, loc)

    # List literal: [...]
    if tt == T_LBRACK:
        return _parse_delimited(tokens, pos + 1, T_RBRACK, n_list, loc)

    # Map literal: {...}
    if tt == T_LBRACE:
        return _parse_delimited(tokens, pos + 1, T_RBRACE, n_map, loc)

    # Quote: 'expr
    if tt == T_QUOTE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_quote(inner, loc), pos

    # Unquote: ~expr
    if tt == T_UNQUOTE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_unquote(inner, loc), pos

    # Splice: ~@expr
    if tt == T_SPLICE:
        inner, pos = _parse_expr(tokens, pos + 1)
        return n_splice(inner, loc), pos

    # Pipe operator |> (treat as symbol in expression position)
    if tt == T_PIPE:
        return n_sym("|>", loc), pos + 1

    raise _err(f"Unexpected token {tt}({_tok_val(tokens, pos)})", tokens, pos)


def _parse_delimited(tokens, pos, end_token, wrapper_fn, loc=None):
    """Parse expressions until end_token. Returns (wrapped_node, new_pos)."""
    elements = []
    while _tok_type(tokens, pos) != end_token:
        if _tok_type(tokens, pos) == T_EOF:
            raise _err(f"Expected {end_token}, got EOF", tokens, pos)
        node, pos = _parse_expr(tokens, pos)
        elements.append(node)
    return wrapper_fn(elements, loc), pos + 1  # skip closing delimiter


def parse(tokens):
    """Parse a token list into a list of AST nodes (top-level expressions)."""
    nodes = []
    pos = 0
    while _tok_type(tokens, pos) != T_EOF:
        node, pos = _parse_expr(tokens, pos)
        nodes.append(node)
    return nodes
