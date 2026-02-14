"""HiveSpeak Lexer — tokenizes source into a flat token list.

Tokens are tuples: (type, value, line, col)
Pure functional style — no mutable global state.
"""

# Token type constants
T_INT = "INT"
T_FLOAT = "FLOAT"
T_STRING = "STRING"
T_BOOL = "BOOL"
T_NULL = "NULL"
T_SYM = "SYM"
T_KW = "KW"
T_HASH = "HASH"
T_LPAREN = "LPAREN"
T_RPAREN = "RPAREN"
T_LBRACK = "LBRACK"
T_RBRACK = "RBRACK"
T_LBRACE = "LBRACE"
T_RBRACE = "RBRACE"
T_QUOTE = "QUOTE"
T_UNQUOTE = "UNQUOTE"
T_SPLICE = "SPLICE"
T_PIPE = "PIPE"
T_EOF = "EOF"

DELIMITERS = {"(", ")", "[", "]", "{", "}", " ", "\t", "\n", "\r", ";", '"', "'"}

SYMBOL_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_!?+-*/<>=&|%")
SYMBOL_CONT = SYMBOL_START | set("0123456789.-")


def _is_digit(c):
    return c in "0123456789"


def _skip_whitespace_and_comments(src, pos, line, col):
    """Advance past whitespace and ; comments. Returns (new_pos, new_line, new_col)."""
    n = len(src)
    while pos < n:
        c = src[pos]
        if c == "\n":
            pos += 1
            line += 1
            col = 1
        elif c in " \t\r":
            pos += 1
            col += 1
        elif c == ";":
            while pos < n and src[pos] != "\n":
                pos += 1
        else:
            break
    return pos, line, col


def _read_string(src, pos, line, col):
    """Read a quoted string starting at pos (which points to opening \"). Returns (token, new_pos, col)."""
    start_col = col
    pos += 1  # skip opening "
    col += 1
    buf = []
    n = len(src)
    while pos < n and src[pos] != '"':
        if src[pos] == "\\" and pos + 1 < n:
            esc = src[pos + 1]
            escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}
            buf.append(escape_map.get(esc, esc))
            pos += 2
            col += 2
        else:
            buf.append(src[pos])
            pos += 1
            col += 1
    if pos >= n:
        raise SyntaxError(f"Unterminated string at line {line}, col {start_col}")
    pos += 1  # skip closing "
    col += 1
    return (T_STRING, "".join(buf), line, start_col), pos, col


def _read_number(src, pos, line, col):
    """Read an integer or float. Returns (token, new_pos, col)."""
    start = pos
    start_col = col
    n = len(src)
    if pos < n and src[pos] == "-":
        pos += 1
        col += 1
    while pos < n and _is_digit(src[pos]):
        pos += 1
        col += 1
    if pos < n and src[pos] == "." and pos + 1 < n and _is_digit(src[pos + 1]):
        pos += 1
        col += 1
        while pos < n and _is_digit(src[pos]):
            pos += 1
            col += 1
        return (T_FLOAT, float(src[start:pos]), line, start_col), pos, col
    return (T_INT, int(src[start:pos]), line, start_col), pos, col


def _read_symbol_or_keyword(src, pos, line, col):
    """Read a symbol, keyword, or reserved literal. Returns (token, new_pos, col)."""
    start_col = col
    is_kw = src[pos] == ":"
    if is_kw:
        pos += 1
        col += 1
    start = pos
    n = len(src)
    while pos < n and src[pos] not in DELIMITERS:
        pos += 1
        col += 1
    text = src[start:pos]
    if is_kw:
        return (T_KW, text, line, start_col), pos, col
    if text == "T":
        return (T_BOOL, True, line, start_col), pos, col
    if text == "F":
        return (T_BOOL, False, line, start_col), pos, col
    if text == "N":
        return (T_NULL, None, line, start_col), pos, col
    return (T_SYM, text, line, start_col), pos, col


def _read_hash(src, pos, line, col):
    """Read a #hash reference. Returns (token, new_pos, col)."""
    start_col = col
    pos += 1  # skip #
    col += 1
    start = pos
    n = len(src)
    while pos < n and src[pos] not in DELIMITERS:
        pos += 1
        col += 1
    return (T_HASH, src[start:pos], line, start_col), pos, col


def tokenize(source):
    """Tokenize HiveSpeak source string into a list of tokens.

    Each token is (type, value, line, col).
    """
    tokens = []
    pos = 0
    line = 1
    col = 1
    n = len(source)

    while pos < n:
        pos, line, col = _skip_whitespace_and_comments(source, pos, line, col)
        if pos >= n:
            break

        c = source[pos]

        # Single-char delimiters
        if c == "(":
            tokens.append((T_LPAREN, "(", line, col))
            pos += 1
            col += 1
        elif c == ")":
            tokens.append((T_RPAREN, ")", line, col))
            pos += 1
            col += 1
        elif c == "[":
            tokens.append((T_LBRACK, "[", line, col))
            pos += 1
            col += 1
        elif c == "]":
            tokens.append((T_RBRACK, "]", line, col))
            pos += 1
            col += 1
        elif c == "{":
            tokens.append((T_LBRACE, "{", line, col))
            pos += 1
            col += 1
        elif c == "}":
            tokens.append((T_RBRACE, "}", line, col))
            pos += 1
            col += 1
        elif c == "'":
            tokens.append((T_QUOTE, "'", line, col))
            pos += 1
            col += 1
        elif c == "~":
            if pos + 1 < n and source[pos + 1] == "@":
                tokens.append((T_SPLICE, "~@", line, col))
                pos += 2
                col += 2
            else:
                tokens.append((T_UNQUOTE, "~", line, col))
                pos += 1
                col += 1
        # Pipe operator |>
        elif c == "|" and pos + 1 < n and source[pos + 1] == ">":
            tokens.append((T_PIPE, "|>", line, col))
            pos += 2
            col += 2
        # String
        elif c == '"':
            tok, pos, col = _read_string(source, pos, line, col)
            tokens.append(tok)
        # Hash reference
        elif c == "#":
            tok, pos, col = _read_hash(source, pos, line, col)
            tokens.append(tok)
        # Number (or negative number)
        elif _is_digit(c) or (c == "-" and pos + 1 < n and _is_digit(source[pos + 1])):
            tok, pos, col = _read_number(source, pos, line, col)
            tokens.append(tok)
        # Keyword or symbol
        elif c == ":" or c in SYMBOL_START:
            tok, pos, col = _read_symbol_or_keyword(source, pos, line, col)
            tokens.append(tok)
        else:
            raise SyntaxError(f"Unexpected character '{c}' at line {line}, col {col}")

    tokens.append((T_EOF, None, line, col))
    return tokens
