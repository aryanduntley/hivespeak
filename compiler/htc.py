#!/usr/bin/env python3
"""HiveSpeak CLI — interpret, compile, or REPL.

Usage:
    python -m compiler.htc run <file.ht>     Interpret a file
    python -m compiler.htc repl              Interactive REPL
    python -m compiler.htc compile <file.ht> <target>  Compile to target (python|js)
    python -m compiler.htc tokenize <file.ht>          Show tokens
    python -m compiler.htc parse <file.ht>             Show AST
"""

import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.evaluator import (
    default_env, run_program, evaluate, _format_val,
    _SPECIAL_FORMS, _BUILTINS,
)


def run_file(path):
    """Read and execute a .ht file."""
    with open(path, "r") as f:
        source = f.read()
    return run_source(source)


def run_source(source, env=None):
    """Tokenize, parse, and evaluate a source string."""
    tokens = tokenize(source)
    ast = parse(tokens)
    if env is None:
        env = default_env()
    return run_program(ast, env), env


def _setup_readline(env):
    """Configure readline for history and tab completion. Returns history path or None."""
    try:
        import readline
    except ImportError:
        return None

    # History file
    history_dir = os.path.expanduser("~/.hivespeak")
    os.makedirs(history_dir, exist_ok=True)
    history_path = os.path.join(history_dir, "repl_history")

    try:
        readline.read_history_file(history_path)
    except FileNotFoundError:
        pass

    readline.set_history_length(1000)

    # Tab completion
    builtins = set(_SPECIAL_FORMS.keys()) | set(_BUILTINS.keys())
    repl_cmds = {":q", ":env", ":reset", ":help"}

    def completer(text, state):
        # Gather completable symbols: builtins + user env bindings + repl commands
        user_syms = {k for k in env if k != "__parent__"}
        candidates = builtins | user_syms | repl_cmds
        matches = [s for s in sorted(candidates) if s.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    readline.set_completer_delims(" \t\n()[]{}\"';")
    readline.parse_and_bind("tab: complete")

    return history_path


def repl():
    """Interactive Read-Eval-Print Loop."""
    print("HiveSpeak v0.2.0 REPL")
    print("Type expressions, or :q to quit. Tab for completion.\n")
    env = default_env()
    buf = ""

    history_path = _setup_readline(env)

    while True:
        try:
            prompt = "ht> " if not buf else "... "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if line.strip() == ":q":
            break

        if line.strip() == ":help":
            print("  :q      quit")
            print("  :env    show user-defined bindings")
            print("  :reset  reset environment")
            print("  Tab     auto-complete symbols")
            continue

        if line.strip() == ":env":
            for k, v in sorted(env.items()):
                if k != "__parent__" and not callable(v):
                    print(f"  {k} = {_format_val(v)}")
            continue

        if line.strip() == ":reset":
            env = default_env()
            print("Environment reset.")
            continue

        buf += line + "\n"

        # Check if parens are balanced before evaluating
        if not _balanced(buf):
            continue

        try:
            result, env = run_source(buf.strip(), env)
            if result is not None:
                print(_format_val(result))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

        buf = ""

    # Save history on exit
    if history_path:
        try:
            import readline
            readline.write_history_file(history_path)
        except Exception:
            pass


def compile_file(path, target):
    """Compile a .ht file to a target language."""
    with open(path, "r") as f:
        source = f.read()
    tokens = tokenize(source)
    ast = parse(tokens)

    if target == "python":
        from compiler.targets.to_python import compile_to_python
        return compile_to_python(ast)
    elif target == "js":
        from compiler.targets.to_js import compile_to_js
        return compile_to_js(ast)
    else:
        print(f"Unknown target: {target}. Supported: python, js", file=sys.stderr)
        sys.exit(1)


def show_tokens(path):
    """Print token list for a file."""
    with open(path, "r") as f:
        source = f.read()
    for tok in tokenize(source):
        if tok[0] != "EOF":
            print(f"  {tok[0]:8s} {repr(tok[1]):20s} L{tok[2]}:{tok[3]}")


def show_ast(path):
    """Print AST for a file."""
    with open(path, "r") as f:
        source = f.read()
    tokens = tokenize(source)
    ast = parse(tokens)
    for node in ast:
        _print_ast(node, 0)


def _print_ast(node, depth):
    """Pretty-print an AST node."""
    indent = "  " * depth
    if node[0] in ("INT", "FLOAT", "STR", "BOOL", "NULL", "SYM", "KW", "HASH"):
        val = node[1] if len(node) > 1 else "nil"
        print(f"{indent}{node[0]}: {val}")
    elif node[0] in ("SEXPR", "LIST", "MAP"):
        print(f"{indent}{node[0]}:")
        for child in node[1]:
            _print_ast(child, depth + 1)
    elif node[0] in ("QUOTE", "UNQUOTE", "SPLICE"):
        print(f"{indent}{node[0]}:")
        _print_ast(node[1], depth + 1)
    else:
        print(f"{indent}{node}")


def _balanced(text):
    """Check if parens/brackets/braces are balanced."""
    depth = 0
    in_string = False
    for i, c in enumerate(text):
        if c == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        if in_string:
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
    return depth <= 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "repl":
        repl()
    elif cmd == "run" and len(sys.argv) >= 3:
        result, _ = run_file(sys.argv[2])
        # Only print if not None and not already printed by print calls
    elif cmd == "compile" and len(sys.argv) >= 4:
        output = compile_file(sys.argv[2], sys.argv[3])
        print(output)
    elif cmd == "tokenize" and len(sys.argv) >= 3:
        show_tokens(sys.argv[2])
    elif cmd == "parse" and len(sys.argv) >= 3:
        show_ast(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
