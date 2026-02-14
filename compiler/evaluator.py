"""HiveSpeak Evaluator — interprets AST nodes in an environment.

Architecture: data-driven dispatch via dicts.
- Special forms: dict mapping name -> handler(args_ast, env)
- Built-in ops: dict mapping name -> handler(evaluated_args)
- Environment: dict with {"__parent__": parent_env, ...bindings}

No OOP. Pure functions + lookup tables.
"""

import hashlib
import json
import sys
import time

# ─── Environment ───────────────────────────────────────────────────────────

def make_env(parent=None, bindings=None):
    env = {"__parent__": parent}
    if bindings:
        env.update(bindings)
    return env


def env_get(env, name):
    if name in env and name != "__parent__":
        return env[name]
    if env.get("__parent__"):
        return env_get(env["__parent__"], name)
    raise NameError(f"Undefined symbol: {name}")


def env_set(env, name, value):
    env[name] = value
    return value


def env_find(env, name):
    """Find the env frame that contains name (for mutation)."""
    if name in env and name != "__parent__":
        return env
    if env.get("__parent__"):
        return env_find(env["__parent__"], name)
    return None


# ─── AST helpers ───────────────────────────────────────────────────────────

def node_type(n):  return n[0]
def node_val(n):   return n[1] if len(n) > 1 else None


# ─── Eval dispatch ─────────────────────────────────────────────────────────

def evaluate(node, env):
    """Evaluate an AST node in an environment. Returns a value."""
    nt = node_type(node)

    # Literals — return value directly
    if nt in _LITERAL_TYPES:
        return _LITERAL_TYPES[nt](node)

    # Symbol — env lookup
    if nt == "SYM":
        return env_get(env, node[1])

    # Keyword — self-evaluating
    if nt == "KW":
        return ("KW", node[1])

    # Hash ref — self-evaluating
    if nt == "HASH":
        return ("HASH", node[1])

    # List literal — evaluate all elements
    if nt == "LIST":
        return [evaluate(el, env) for el in node[1]]

    # Map literal — evaluate alternating key/value pairs
    if nt == "MAP":
        elements = node[1]
        result = {}
        i = 0
        while i < len(elements) - 1:
            k = evaluate(elements[i], env)
            v = evaluate(elements[i + 1], env)
            # Normalize keyword keys to strings
            key = k[1] if isinstance(k, tuple) and k[0] == "KW" else k
            result[key] = v
            i += 2
        return result

    # Quote — return unevaluated
    if nt == "QUOTE":
        return _ast_to_data(node[1])

    # S-expression — function call or special form
    if nt == "SEXPR":
        return _eval_sexpr(node[1], env)

    raise RuntimeError(f"Cannot evaluate node type: {nt}")


_LITERAL_TYPES = {
    "INT":   lambda n: n[1],
    "FLOAT": lambda n: n[1],
    "STR":   lambda n: n[1],
    "BOOL":  lambda n: n[1],
    "NULL":  lambda n: None,
}


def _eval_sexpr(elements, env):
    """Evaluate an s-expression (operator args...)."""
    if not elements:
        return None

    head = elements[0]
    args = elements[1:]

    # Check if head is a special form symbol
    if node_type(head) == "SYM" and head[1] in _SPECIAL_FORMS:
        return _SPECIAL_FORMS[head[1]](args, env)

    # Otherwise, evaluate head and all args, then apply
    fn_val = evaluate(head, env)
    evaled_args = [evaluate(a, env) for a in args]
    return apply_fn(fn_val, evaled_args, env)


def apply_fn(fn_val, args, env):
    """Apply a function value to evaluated arguments."""
    # Built-in function
    if callable(fn_val):
        return fn_val(*args)

    # User-defined function: ("FN", params, body, closure_env)
    if isinstance(fn_val, tuple) and fn_val[0] == "FN":
        _, params, body_nodes, closure_env = fn_val
        fn_env = make_env(closure_env)
        _bind_params(params, args, fn_env)
        result = None
        for node in body_nodes:
            result = evaluate(node, fn_env)
        return result

    # Macro (shouldn't be applied directly after eval, but handle gracefully)
    if isinstance(fn_val, tuple) and fn_val[0] == "MACRO":
        raise RuntimeError("Macros cannot be applied as values — they transform code at expansion time")

    raise RuntimeError(f"Not callable: {fn_val}")


def _bind_params(params, args, env):
    """Bind parameter names to argument values in env. Handles & rest params."""
    i = 0
    while i < len(params):
        if params[i] == "&":
            # Rest param: bind remaining args as list
            if i + 1 < len(params):
                env_set(env, params[i + 1], list(args[i:]))
            return
        if i < len(args):
            env_set(env, params[i], args[i])
        else:
            env_set(env, params[i], None)
        i += 1


# ─── Special Forms ─────────────────────────────────────────────────────────

def _sf_def(args, env):
    """(def name value) or (def (name params...) body...)"""
    if node_type(args[0]) == "SEXPR":
        # Function shorthand: (def (name params...) body...)
        parts = args[0][1]
        name = parts[0][1]
        params = [p[1] for p in parts[1:]]
        body = args[1:]
        fn_val = ("FN", params, body, env)
        return env_set(env, name, fn_val)
    # Simple binding: (def name value)
    name = args[0][1]
    value = evaluate(args[1], env)
    return env_set(env, name, value)


def _sf_let(args, env):
    """(let [bindings...] body...)"""
    bindings_node = args[0]
    body = args[1:]
    let_env = make_env(env)
    pairs = bindings_node[1]  # LIST elements
    i = 0
    while i < len(pairs) - 1:
        name = pairs[i][1]
        val = evaluate(pairs[i + 1], let_env)
        env_set(let_env, name, val)
        i += 2
    result = None
    for node in body:
        result = evaluate(node, let_env)
    return result


def _sf_fn(args, env):
    """(fn [params...] body...)"""
    params_node = args[0]
    params = [p[1] for p in params_node[1]]
    body = args[1:]
    return ("FN", params, body, env)


def _sf_if(args, env):
    """(if cond then else?)"""
    cond = evaluate(args[0], env)
    if _truthy(cond):
        return evaluate(args[1], env)
    if len(args) > 2:
        return evaluate(args[2], env)
    return None


def _sf_do(args, env):
    """(do expr1 expr2 ... exprN) — returns last"""
    result = None
    for node in args:
        result = evaluate(node, env)
    return result


def _sf_match(args, env):
    """(match val pat1 res1 pat2 res2 ... _ default)"""
    val = evaluate(args[0], env)
    i = 1
    while i < len(args) - 1:
        pat = args[i]
        res = args[i + 1]
        if _match_pattern(pat, val, env):
            return evaluate(res, env)
        i += 2
    return None


def _match_pattern(pat, val, env):
    """Check if val matches pattern. _ matches anything."""
    if node_type(pat) == "SYM" and pat[1] == "_":
        return True
    pat_val = evaluate(pat, env)
    return pat_val == val


def _sf_loop(args, env):
    """(loop [bindings...] body) — loop with recur"""
    bindings_node = args[0]
    body = args[1:]
    pairs = bindings_node[1]
    names = []
    vals = []
    loop_env = make_env(env)
    i = 0
    while i < len(pairs) - 1:
        names.append(pairs[i][1])
        vals.append(evaluate(pairs[i + 1], loop_env))
        i += 2
    for n, v in zip(names, vals):
        env_set(loop_env, n, v)
    while True:
        try:
            result = None
            for node in body:
                result = evaluate(node, loop_env)
            return result
        except _Recur as r:
            for n, v in zip(names, r.values):
                env_set(loop_env, n, v)


def _sf_recur(args, env):
    """(recur val1 val2 ...) — jump back to enclosing loop"""
    values = [evaluate(a, env) for a in args]
    raise _Recur(values)


# Recur signal — not a real exception, just a control flow mechanism
class _Recur(Exception):
    def __init__(self, values):
        self.values = values


def _sf_quote(args, _env):
    """(quote expr) — return unevaluated"""
    return _ast_to_data(args[0])


def _sf_eval(args, env):
    """(eval data) — evaluate data as code"""
    data = evaluate(args[0], env)
    ast = _data_to_ast(data)
    return evaluate(ast, env)


def _sf_macro(args, env):
    """(macro (name params...) body)"""
    parts = args[0][1]
    name = parts[0][1]
    params = [p[1] for p in parts[1:]]
    body = args[1]  # The template (usually quoted)
    macro_val = ("MACRO", params, body, env)
    return env_set(env, name, macro_val)


def _sf_try(args, env):
    """(try body (catch e handler))"""
    try:
        return evaluate(args[0], env)
    except _HiveSpeakError as e:
        if len(args) > 1 and node_type(args[1]) == "SEXPR":
            catch_form = args[1][1]
            if node_type(catch_form[0]) == "SYM" and catch_form[0][1] == "catch":
                err_name = catch_form[1][1]
                handler = catch_form[2:]
                catch_env = make_env(env, {err_name: e.value})
                result = None
                for node in handler:
                    result = evaluate(node, catch_env)
                return result
        raise


def _sf_throw(args, env):
    """(throw value)"""
    raise _HiveSpeakError(evaluate(args[0], env))


class _HiveSpeakError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(str(value))


def _sf_pipe(args, env):
    """(|> val fn1 fn2 fn3...) — thread value through functions"""
    val = evaluate(args[0], env)
    for step in args[1:]:
        if node_type(step) == "SEXPR":
            # Insert val as last arg: (f a b) -> (f a b val)
            fn_val = evaluate(step[1][0], env)
            step_args = [evaluate(a, env) for a in step[1][1:]]
            step_args.append(val)
            val = apply_fn(fn_val, step_args, env)
        elif node_type(step) == "SYM":
            fn_val = evaluate(step, env)
            val = apply_fn(fn_val, [val], env)
        else:
            fn_val = evaluate(step, env)
            val = apply_fn(fn_val, [val], env)
    return val


def _sf_mod(args, env):
    """(mod name body...) — define module"""
    name = args[0][1]
    mod_env = make_env(env)
    for node in args[1:]:
        evaluate(node, mod_env)
    # Extract public bindings (exclude __parent__ and _ prefixed)
    mod = {k: v for k, v in mod_env.items()
           if k != "__parent__" and not k.startswith("_")}
    return env_set(env, name, mod)


def _sf_use(args, env):
    """(use module) or (use module name1 name2...)"""
    mod_name = args[0][1]
    mod = env_get(env, mod_name)
    if not isinstance(mod, dict):
        raise RuntimeError(f"{mod_name} is not a module")
    if len(args) == 1:
        # Import all
        for k, v in mod.items():
            env_set(env, k, v)
    else:
        # Import specific
        for a in args[1:]:
            name = a[1]
            if name not in mod:
                raise RuntimeError(f"{name} not found in module {mod_name}")
            env_set(env, name, mod[name])
    return None


# ─── Hive Primitives ──────────────────────────────────────────────────────

# Global packet store (simulated)
_PACKET_STORE = {}


def _sf_cell(args, env):
    """(cell state-map) — create a cell"""
    state = evaluate(args[0], env)
    cell_id = hashlib.sha256(json.dumps(str(state)).encode()).hexdigest()[:12]
    return {"__type__": "cell", "id": cell_id, "state": state, "inbox": []}


def _sf_emit(args, env):
    """(emit cell :target target content) or (emit cell :broadcast content)"""
    cell = evaluate(args[0], env)
    mode = evaluate(args[1], env)
    if isinstance(mode, tuple) and mode[0] == "KW" and mode[1] == "target":
        target = evaluate(args[2], env)
        content = evaluate(args[3], env)
        if isinstance(target, dict) and target.get("__type__") == "cell":
            target["inbox"].append({"from": cell.get("id"), "content": content})
        return content
    if isinstance(mode, tuple) and mode[0] == "KW" and mode[1] == "broadcast":
        content = evaluate(args[2], env)
        return content
    # Simple form: (emit cell target content)
    target = evaluate(args[1], env)
    content = evaluate(args[2], env)
    if isinstance(target, dict) and target.get("__type__") == "cell":
        target["inbox"].append({"from": cell.get("id"), "content": content})
    return content


def _sf_recv(args, env):
    """(recv cell) — pop from inbox"""
    cell = evaluate(args[0], env)
    if isinstance(cell, dict) and cell.get("inbox"):
        return cell["inbox"].pop(0)
    return None


def _sf_merge(args, env):
    """(merge [cells] :on [keys]) — merge cell states"""
    cells = evaluate(args[0], env)
    on_keys = None
    if len(args) > 2:
        on_keys = evaluate(args[2], env)
    merged = {}
    for c in cells:
        if isinstance(c, dict) and c.get("__type__") == "cell":
            state = c.get("state", {})
            for k, v in state.items():
                if on_keys is None or k in [x[1] if isinstance(x, tuple) else x for x in on_keys]:
                    if k not in merged:
                        merged[k] = []
                    merged[k].append(v)
    return {"__type__": "collective", "shared": merged, "cells": cells}


def _sf_compress(args, env):
    """(compress collective) — compress to packet"""
    coll = evaluate(args[0], env)
    if not isinstance(coll, dict) or coll.get("__type__") != "collective":
        return {"fail": "not-collective"}
    shared = coll.get("shared", {})
    # Simple compression: take consensus (most common value per key)
    compressed = {}
    for k, values in shared.items():
        if values:
            # Most frequent value wins
            counts = {}
            for v in values:
                key = str(v)
                counts[key] = counts.get(key, 0) + 1
            winner = max(counts, key=counts.get)
            # Find original value
            for v in values:
                if str(v) == winner:
                    compressed[k] = v
                    break
    pkt_hash = hashlib.sha256(json.dumps(str(compressed)).encode()).hexdigest()[:12]
    packet = {"__type__": "packet", "hash": pkt_hash, "data": compressed}
    _PACKET_STORE[pkt_hash] = packet
    return {"ok": packet}


def _sf_ref(args, env):
    """(ref #hash) — look up packet"""
    h = args[0]
    hash_val = h[1] if node_type(h) == "HASH" else evaluate(h, env)
    if isinstance(hash_val, tuple) and hash_val[0] == "HASH":
        hash_val = hash_val[1]
    return _PACKET_STORE.get(str(hash_val), None)


def _sf_packet(args, env):
    """(packet data) — create packet from data"""
    data = evaluate(args[0], env)
    pkt_hash = hashlib.sha256(json.dumps(str(data)).encode()).hexdigest()[:12]
    packet = {"__type__": "packet", "hash": pkt_hash, "data": data}
    _PACKET_STORE[pkt_hash] = packet
    return packet


# ─── Communication Intents ─────────────────────────────────────────────────

def _sf_intent(intent_type):
    """Factory for communication intent special forms."""
    def handler(args, env):
        content = evaluate(args[0], env) if args else None
        return {"__type__": "intent", "intent": intent_type, "content": content}
    return handler


# ─── Special Form Registry ─────────────────────────────────────────────────

_SPECIAL_FORMS = {
    "def":      _sf_def,
    "let":      _sf_let,
    "fn":       _sf_fn,
    "if":       _sf_if,
    "do":       _sf_do,
    "match":    _sf_match,
    "loop":     _sf_loop,
    "recur":    _sf_recur,
    "quote":    _sf_quote,
    "eval":     _sf_eval,
    "macro":    _sf_macro,
    "try":      _sf_try,
    "catch":    lambda a, e: None,  # handled inside try
    "throw":    _sf_throw,
    "|>":       _sf_pipe,
    "mod":      _sf_mod,
    "use":      _sf_use,
    # Hive primitives
    "cell":     _sf_cell,
    "emit":     _sf_emit,
    "recv":     _sf_recv,
    "merge":    _sf_merge,
    "compress": _sf_compress,
    "ref":      _sf_ref,
    "packet":   _sf_packet,
    # Communication intents
    "assert!":  _sf_intent("assert"),
    "ask?":     _sf_intent("ask"),
    "request!": _sf_intent("request"),
    "suggest~": _sf_intent("suggest"),
    "accept+":  _sf_intent("accept"),
    "reject-":  _sf_intent("reject"),
}


# ─── Built-in Functions ────────────────────────────────────────────────────

def _truthy(v):
    """HiveSpeak truthiness: F, N, 0, empty string/list/map are falsy."""
    if v is None or v is False:
        return False
    if v == 0 or v == "" or v == [] or v == {}:
        return False
    return True


def _ht_type(v):
    if v is None:          return ("KW", "null")
    if isinstance(v, bool): return ("KW", "bool")
    if isinstance(v, int):  return ("KW", "int")
    if isinstance(v, float): return ("KW", "float")
    if isinstance(v, str):  return ("KW", "str")
    if isinstance(v, list): return ("KW", "list")
    if isinstance(v, dict):
        t = v.get("__type__")
        if t: return ("KW", t)
        return ("KW", "map")
    if isinstance(v, tuple):
        if v[0] == "FN":  return ("KW", "fn")
        if v[0] == "KW":  return ("KW", "keyword")
        if v[0] == "HASH": return ("KW", "hash")
    if callable(v):        return ("KW", "fn")
    return ("KW", "unknown")


def _ht_print(*args):
    print(*[_format_val(a) for a in args])
    return None


def _format_val(v):
    """Format a HiveSpeak value for display."""
    if v is None:              return "N"
    if v is True:              return "T"
    if v is False:             return "F"
    if isinstance(v, str):     return v
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, list):    return "[" + " ".join(_format_val(x) for x in v) + "]"
    if isinstance(v, dict):
        if v.get("__type__"):
            return f"<{v['__type__']} {v.get('id', v.get('hash', ''))}>"
        pairs = " ".join(f":{k} {_format_val(val)}" for k, val in v.items())
        return "{" + pairs + "}"
    if isinstance(v, tuple):
        if v[0] == "FN":      return "<fn>"
        if v[0] == "MACRO":   return "<macro>"
        if v[0] == "KW":      return f":{v[1]}"
        if v[0] == "HASH":    return f"#{v[1]}"
    if callable(v):            return "<builtin>"
    return str(v)


# Arithmetic — variadic
def _arith(op, identity):
    def handler(*args):
        if len(args) == 1:
            return op(identity, args[0])
        result = args[0]
        for a in args[1:]:
            result = op(result, a)
        return result
    return handler


# Comparison — binary
def _cmp(op):
    def handler(a, b):
        return op(a, b)
    return handler


def _ht_fmt(template, *args):
    result = template
    for a in args:
        result = result.replace("{}", _format_val(a), 1)
    return result


def _ht_map(f, lst):
    return [apply_fn(f, [x], None) for x in lst]


def _ht_flt(f, lst):
    return [x for x in lst if _truthy(apply_fn(f, [x], None))]


def _ht_red(f, init, lst):
    acc = init
    for x in lst:
        acc = apply_fn(f, [acc, x], None)
    return acc


def _ht_any(f, lst):
    return any(_truthy(apply_fn(f, [x], None)) for x in lst)


def _ht_all(f, lst):
    return all(_truthy(apply_fn(f, [x], None)) for x in lst)


def _ht_srt(lst, key=None):
    if key:
        return sorted(lst, key=lambda x: apply_fn(key, [x], None))
    return sorted(lst)


def _ht_read_file(path):
    with open(path, "r") as f:
        return f.read()


def _ht_write_file(path, data):
    with open(path, "w") as f:
        f.write(str(data))
    return None


# Built-in function registry — flat dict, data-driven
_BUILTINS = {
    # Arithmetic
    "+":    _arith(lambda a, b: a + b, 0),
    "-":    _arith(lambda a, b: a - b, 0),
    "*":    _arith(lambda a, b: a * b, 1),
    "/":    _arith(lambda a, b: a / b if b != 0 else float('inf'), 1),
    "%":    lambda a, b: a % b,

    # Comparison
    "=":    _cmp(lambda a, b: a == b),
    "!=":   _cmp(lambda a, b: a != b),
    "<":    _cmp(lambda a, b: a < b),
    ">":    _cmp(lambda a, b: a > b),
    "<=":   _cmp(lambda a, b: a <= b),
    ">=":   _cmp(lambda a, b: a >= b),

    # Logic
    "and":  lambda a, b: a if not _truthy(a) else b,
    "or":   lambda a, b: a if _truthy(a) else b,
    "not":  lambda a: not _truthy(a),

    # String
    "cat":  lambda *args: "".join(_format_val(a) if not isinstance(a, str) else a for a in args) if args and isinstance(args[0], str) else (list(args[0]) + list(args[1]) if len(args) == 2 and isinstance(args[0], list) else args[0]),
    "len":  lambda a: len(a),
    "slc":  lambda a, start, end=None: a[start:end],
    "idx":  lambda a, b: a.index(b) if b in a else -1,
    "spl":  lambda a, sep: a.split(sep),
    "upr":  lambda a: a.upper(),
    "lwr":  lambda a: a.lower(),
    "fmt":  _ht_fmt,

    # List
    "hd":   lambda a: a[0] if a else None,
    "tl":   lambda a: a[1:] if a else [],
    "nth":  lambda a, i: a[i] if 0 <= i < len(a) else None,
    "push": lambda a, v: a + [v],
    "map":  _ht_map,
    "flt":  _ht_flt,
    "red":  _ht_red,
    "srt":  _ht_srt,
    "rev":  lambda a: list(reversed(a)),
    "zip":  lambda *lists: [list(x) for x in zip(*lists)],
    "flat": lambda a: [x for sub in a for x in (sub if isinstance(sub, list) else [sub])],
    "uniq": lambda a: list(dict.fromkeys(a)),
    "any":  _ht_any,
    "all":  _ht_all,
    "range": lambda *args: list(range(*args)),

    # Map
    "get":  lambda m, k: m.get(k[1] if isinstance(k, tuple) and k[0] == "KW" else k),
    "put":  lambda m, k, v: {**m, **(
        {k[1]: v} if isinstance(k, tuple) and k[0] == "KW" else {k: v}
    )},
    "del":  lambda m, k: {key: val for key, val in m.items() if key != (k[1] if isinstance(k, tuple) and k[0] == "KW" else k)},
    "keys": lambda m: [("KW", k) if isinstance(k, str) else k for k in m.keys() if k != "__type__"],
    "vals": lambda m: [v for k, v in m.items() if k != "__type__"],
    "has":  lambda m, k: (k[1] if isinstance(k, tuple) and k[0] == "KW" else k) in m,
    "mrg":  lambda a, b: {**a, **b},

    # Type
    "type":   _ht_type,
    "int?":   lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float?": lambda v: isinstance(v, float),
    "str?":   lambda v: isinstance(v, str),
    "bool?":  lambda v: isinstance(v, bool),
    "null?":  lambda v: v is None,
    "list?":  lambda v: isinstance(v, list),
    "map?":   lambda v: isinstance(v, dict),
    "fn?":    lambda v: callable(v) or (isinstance(v, tuple) and v[0] == "FN"),
    "cell?":  lambda v: isinstance(v, dict) and v.get("__type__") == "cell",

    # I/O
    "print":      _ht_print,
    "print-err":  lambda *args: print(*[_format_val(a) for a in args], file=sys.stderr),
    "read-line":  lambda: input(),
    "read-file":  _ht_read_file,
    "write-file": _ht_write_file,

    # Utility
    "str":   lambda v: _format_val(v),
    "int":   lambda v: int(v),
    "float": lambda v: float(v),
    "time":  lambda: time.time(),
    "hash":  lambda v: hashlib.sha256(str(v).encode()).hexdigest()[:12],

    # State helpers
    "get-state": lambda c: c.get("state") if isinstance(c, dict) else None,
    "set-state": lambda c, k, v: (c["state"].update({k[1] if isinstance(k, tuple) and k[0] == "KW" else k: v}), c["state"])[-1],
}


# ─── AST <-> Data conversion ──────────────────────────────────────────────

def _ast_to_data(node):
    """Convert AST node to runtime data (for quote)."""
    nt = node_type(node)
    if nt in ("INT", "FLOAT", "STR", "BOOL"):
        return node[1]
    if nt == "NULL":
        return None
    if nt == "SYM":
        return ("SYM", node[1])
    if nt == "KW":
        return ("KW", node[1])
    if nt == "HASH":
        return ("HASH", node[1])
    if nt == "LIST":
        return [_ast_to_data(el) for el in node[1]]
    if nt == "MAP":
        result = {}
        i = 0
        els = node[1]
        while i < len(els) - 1:
            k = _ast_to_data(els[i])
            v = _ast_to_data(els[i + 1])
            key = k[1] if isinstance(k, tuple) and k[0] == "KW" else k
            result[key] = v
            i += 2
        return result
    if nt == "SEXPR":
        return [_ast_to_data(el) for el in node[1]]
    if nt == "QUOTE":
        return ["quote", _ast_to_data(node[1])]
    if nt == "UNQUOTE":
        return ["unquote", _ast_to_data(node[1])]
    if nt == "SPLICE":
        return ["splice", _ast_to_data(node[1])]
    return node


def _data_to_ast(data):
    """Convert runtime data back to AST (for eval)."""
    if data is None:
        return ("NULL",)
    if isinstance(data, bool):
        return ("BOOL", data)
    if isinstance(data, int):
        return ("INT", data)
    if isinstance(data, float):
        return ("FLOAT", data)
    if isinstance(data, str):
        return ("STR", data)
    if isinstance(data, tuple):
        if data[0] == "SYM":
            return ("SYM", data[1])
        if data[0] == "KW":
            return ("KW", data[1])
        if data[0] == "HASH":
            return ("HASH", data[1])
    if isinstance(data, list):
        if data and isinstance(data[0], tuple) and data[0][0] == "SYM":
            return ("SEXPR", [_data_to_ast(el) for el in data])
        if data and isinstance(data[0], str):
            # Could be a symbol name as string
            return ("SEXPR", [_data_to_ast(("SYM", el) if isinstance(el, str) and not el.startswith(":") else el) for el in data])
        return ("LIST", [_data_to_ast(el) for el in data])
    if isinstance(data, dict):
        elements = []
        for k, v in data.items():
            elements.append(("KW", k) if isinstance(k, str) else _data_to_ast(k))
            elements.append(_data_to_ast(v))
        return ("MAP", elements)
    return ("STR", str(data))


# ─── Public API ────────────────────────────────────────────────────────────

def default_env():
    """Create the default environment with all builtins."""
    env = make_env()
    env.update(_BUILTINS)
    env_set(env, "T", True)
    env_set(env, "F", False)
    env_set(env, "N", None)
    return env


def run_program(ast_nodes, env=None):
    """Evaluate a list of AST nodes in sequence. Returns last result."""
    if env is None:
        env = default_env()
    result = None
    for node in ast_nodes:
        result = evaluate(node, env)
    return result
