"""Tests for the HiveSpeak evaluator."""

import pytest
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.evaluator import (
    evaluate, default_env, run_program, make_env, env_get, env_set, _format_val,
)


def ev(src, env=None):
    """Evaluate source and return the result."""
    tokens = tokenize(src)
    ast = parse(tokens)
    if env is None:
        env = default_env()
    return run_program(ast, env)


def ev_env(src):
    """Evaluate source and return (result, env)."""
    tokens = tokenize(src)
    ast = parse(tokens)
    env = default_env()
    result = run_program(ast, env)
    return result, env


def ev_output(src, capsys):
    """Evaluate source and return captured stdout."""
    ev(src)
    return capsys.readouterr().out


# ─── Literals ─────────────────────────────────────────────────────────────

def test_int():
    assert ev("42") == 42

def test_float():
    assert ev("3.14") == 3.14

def test_string():
    assert ev('"hello"') == "hello"

def test_bool():
    assert ev("T") is True
    assert ev("F") is False

def test_null():
    assert ev("N") is None


# ─── Arithmetic ──────────────────────────────────────────────────────────

def test_add():
    assert ev("(+ 2 3)") == 5

def test_add_variadic():
    assert ev("(+ 1 2 3 4 5)") == 15

def test_sub():
    assert ev("(- 10 3)") == 7

def test_mul():
    assert ev("(* 4 5)") == 20

def test_div():
    assert ev("(/ 10 2)") == 5.0

def test_mod():
    assert ev("(% 10 3)") == 1


# ─── Comparison ──────────────────────────────────────────────────────────

def test_eq():
    assert ev("(= 1 1)") is True
    assert ev("(= 1 2)") is False

def test_neq():
    assert ev("(!= 1 2)") is True

def test_lt():
    assert ev("(< 1 2)") is True

def test_gt():
    assert ev("(> 5 3)") is True

def test_lte():
    assert ev("(<= 3 3)") is True

def test_gte():
    assert ev("(>= 4 3)") is True


# ─── Logic ───────────────────────────────────────────────────────────────

def test_and():
    assert ev("(and T T)") is True
    assert ev("(and T F)") is False

def test_or():
    assert ev("(or F T)") is True
    assert ev("(or F F)") is False

def test_not():
    assert ev("(not T)") is False
    assert ev("(not F)") is True
    assert ev("(not N)") is True


# ─── Def ─────────────────────────────────────────────────────────────────

def test_def_simple():
    assert ev("(def x 42) x") == 42

def test_def_function():
    assert ev("(def (square n) (* n n)) (square 5)") == 25

def test_def_function_multi_arg():
    assert ev("(def (add a b) (+ a b)) (add 10 20)") == 30


# ─── Let ─────────────────────────────────────────────────────────────────

def test_let():
    assert ev("(let [a 10 b 20] (+ a b))") == 30

def test_let_scoping():
    assert ev("(def x 1) (let [x 99] x)") == 99

def test_let_sequential_bindings():
    assert ev("(let [a 5 b (* a 2)] b)") == 10


# ─── Fn ──────────────────────────────────────────────────────────────────

def test_fn():
    assert ev("(def f (fn [x] (* x 2))) (f 21)") == 42

def test_fn_closure():
    assert ev("(def (make-adder n) (fn [x] (+ x n))) (def add5 (make-adder 5)) (add5 10)") == 15

def test_fn_rest_params():
    assert ev("(def f (fn [& args] args)) (f 1 2 3)") == [1, 2, 3]


# ─── If ──────────────────────────────────────────────────────────────────

def test_if_true():
    assert ev("(if T 1 2)") == 1

def test_if_false():
    assert ev("(if F 1 2)") == 2

def test_if_no_else():
    assert ev("(if F 1)") is None

def test_if_truthy():
    assert ev('(if 42 "yes" "no")') == "yes"
    assert ev('(if 0 "yes" "no")') == "no"
    assert ev('(if "" "yes" "no")') == "no"
    assert ev('(if N "yes" "no")') == "no"


# ─── Do ──────────────────────────────────────────────────────────────────

def test_do():
    assert ev("(do 1 2 3)") == 3


# ─── Match ───────────────────────────────────────────────────────────────

def test_match():
    assert ev('(match 2 1 "one" 2 "two" _ "other")') == "two"

def test_match_wildcard():
    assert ev('(match 99 1 "one" _ "other")') == "other"

def test_match_no_match():
    assert ev("(match 99 1 10 2 20)") is None


# ─── Loop/Recur ──────────────────────────────────────────────────────────

def test_loop_simple():
    assert ev("""
        (loop [i 0 acc 0]
          (if (= i 5)
            acc
            (recur (+ i 1) (+ acc i))))
    """) == 10  # 0+1+2+3+4

def test_factorial():
    assert ev("""
        (def (factorial n)
          (loop [i n acc 1]
            (if (<= i 1)
              acc
              (recur (- i 1) (* acc i)))))
        (factorial 10)
    """) == 3628800


# ─── Quote/Eval ──────────────────────────────────────────────────────────

def test_quote():
    result = ev("(quote (+ 1 2))")
    assert isinstance(result, list)

def test_quote_sugar():
    result = ev("'(+ 1 2)")
    assert isinstance(result, list)

def test_eval_quoted():
    assert ev("(eval '(+ 1 2))") == 3


# ─── Try/Catch/Throw ────────────────────────────────────────────────────

def test_try_no_error():
    assert ev("(try 42 (catch e 0))") == 42

def test_try_catch():
    assert ev('(try (throw "boom") (catch e e))') == "boom"


# ─── Pipe ────────────────────────────────────────────────────────────────

def test_pipe_simple():
    assert ev("(|> 5 (+ 3))") == 8

def test_pipe_chain():
    result = ev("""
        (|> [1 2 3 4 5 6 7 8 9 10]
          (flt (fn [x] (= (% x 2) 0)))
          (map (fn [x] (* x x)))
          (red + 0))
    """)
    assert result == 220


# ─── String Ops ──────────────────────────────────────────────────────────

def test_cat():
    assert ev('(cat "a" "b" "c")') == "abc"

def test_len_string():
    assert ev('(len "hello")') == 5

def test_upr():
    assert ev('(upr "hello")') == "HELLO"

def test_lwr():
    assert ev('(lwr "HELLO")') == "hello"

def test_spl():
    assert ev('(spl "a,b,c" ",")') == ["a", "b", "c"]

def test_fmt():
    assert ev('(fmt "x={}" 42)') == "x=42"


# ─── List Ops ────────────────────────────────────────────────────────────

def test_hd():
    assert ev("(hd [1 2 3])") == 1

def test_tl():
    assert ev("(tl [1 2 3])") == [2, 3]

def test_nth():
    assert ev("(nth [10 20 30] 1)") == 20

def test_push():
    assert ev("(push [1 2] 3)") == [1, 2, 3]

def test_rev():
    assert ev("(rev [1 2 3])") == [3, 2, 1]

def test_map():
    assert ev("(map (fn [x] (* x 2)) [1 2 3])") == [2, 4, 6]

def test_flt():
    assert ev("(flt (fn [x] (> x 2)) [1 2 3 4 5])") == [3, 4, 5]

def test_red():
    assert ev("(red + 0 [1 2 3 4 5])") == 15

def test_srt():
    assert ev("(srt [3 1 2])") == [1, 2, 3]

def test_flat():
    assert ev("(flat [[1 2] [3 4] 5])") == [1, 2, 3, 4, 5]

def test_uniq():
    assert ev("(uniq [1 2 2 3 3 3])") == [1, 2, 3]

def test_any():
    assert ev("(any (fn [x] (> x 3)) [1 2 3 4])") is True
    assert ev("(any (fn [x] (> x 10)) [1 2 3])") is False

def test_all():
    assert ev("(all (fn [x] (> x 0)) [1 2 3])") is True
    assert ev("(all (fn [x] (> x 2)) [1 2 3])") is False

def test_range():
    assert ev("(range 5)") == [0, 1, 2, 3, 4]
    assert ev("(range 1 4)") == [1, 2, 3]

def test_zip():
    assert ev("(zip [1 2 3] [4 5 6])") == [[1, 4], [2, 5], [3, 6]]


# ─── Map Ops ─────────────────────────────────────────────────────────────

def test_get():
    assert ev("(get {:name \"Alice\"} :name)") == "Alice"

def test_put():
    result = ev("(put {:a 1} :b 2)")
    assert result == {"a": 1, "b": 2}

def test_del():
    result = ev("(del {:a 1 :b 2} :a)")
    assert result == {"b": 2}

def test_keys():
    result = ev("(keys {:a 1 :b 2})")
    assert len(result) == 2

def test_vals():
    result = ev("(vals {:a 1 :b 2})")
    assert set(result) == {1, 2}

def test_has():
    assert ev("(has {:a 1} :a)") is True
    assert ev("(has {:a 1} :b)") is False

def test_mrg():
    result = ev("(mrg {:a 1} {:b 2})")
    assert result == {"a": 1, "b": 2}


# ─── Type Checks ─────────────────────────────────────────────────────────

def test_type_int():
    assert ev("(type 42)") == ("KW", "int")

def test_type_str():
    assert ev('(type "hi")') == ("KW", "str")

def test_type_check_predicates():
    assert ev("(int? 42)") is True
    assert ev("(int? 3.14)") is False
    assert ev('(str? "hi")') is True
    assert ev("(null? N)") is True
    assert ev("(list? [1 2])") is True
    assert ev("(map? {:a 1})") is True
    assert ev("(bool? T)") is True


# ─── Module ──────────────────────────────────────────────────────────────

def test_mod_and_use():
    result = ev("""
        (mod math
          (def pi 3.14159)
          (def (square x) (* x x)))
        (use math)
        (square 5)
    """)
    assert result == 25

def test_mod_selective_use():
    result = ev("""
        (mod math
          (def pi 3.14159)
          (def (square x) (* x x)))
        (use math pi)
        pi
    """)
    assert abs(result - 3.14159) < 0.001


# ─── Hive Primitives ────────────────────────────────────────────────────

def test_cell_creation():
    result = ev('(cell {:role "agent"})')
    assert isinstance(result, dict)
    assert result["__type__"] == "cell"
    assert result["state"]["role"] == "agent"
    assert result["inbox"] == []

def test_emit_and_recv():
    result = ev("""
        (def a (cell {:role "sender"}))
        (def b (cell {:role "receiver"}))
        (emit a b (assert! {:msg "hello"}))
        (recv b)
    """)
    assert isinstance(result, dict)
    assert "from" in result
    assert "content" in result

def test_merge():
    result = ev("""
        (def a (cell {:x 1 :y 2}))
        (def b (cell {:x 1 :z 3}))
        (merge [a b])
    """)
    assert result["__type__"] == "collective"

def test_compress():
    result = ev("""
        (def a (cell {:x 1}))
        (def b (cell {:x 1}))
        (def c (merge [a b]))
        (compress c)
    """)
    assert "ok" in result
    assert result["ok"]["__type__"] == "packet"

def test_packet():
    result = ev('(packet {:data "test"})')
    assert result["__type__"] == "packet"
    assert "hash" in result


# ─── Communication Intents ───────────────────────────────────────────────

def test_assert_intent():
    result = ev('(assert! {:claim "x"})')
    assert result["__type__"] == "intent"
    assert result["intent"] == "assert"

def test_ask_intent():
    result = ev('(ask? {:about "y"})')
    assert result["intent"] == "ask"

def test_suggest_intent():
    result = ev('(suggest~ {:idea "z"})')
    assert result["intent"] == "suggest"

def test_accept_intent():
    result = ev('(accept+ {:ref "ok"})')
    assert result["intent"] == "accept"

def test_reject_intent():
    result = ev('(reject- {:reason "no"})')
    assert result["intent"] == "reject"

def test_request_intent():
    result = ev('(request! {:need "data"})')
    assert result["intent"] == "request"


# ─── I/O ─────────────────────────────────────────────────────────────────

def test_print(capsys):
    ev("(print 42)")
    assert capsys.readouterr().out.strip() == "42"

def test_print_string(capsys):
    ev('(print "hello")')
    assert capsys.readouterr().out.strip() == "hello"

def test_print_bool(capsys):
    ev("(print T)")
    assert capsys.readouterr().out.strip() == "T"


# ─── Format Values ──────────────────────────────────────────────────────

def test_format_none():
    assert _format_val(None) == "N"

def test_format_bool():
    assert _format_val(True) == "T"
    assert _format_val(False) == "F"

def test_format_list():
    assert _format_val([1, 2, 3]) == "[1 2 3]"

def test_format_map():
    result = _format_val({"a": 1})
    assert ":a" in result and "1" in result


# ─── Error Cases ─────────────────────────────────────────────────────────

def test_undefined_symbol():
    with pytest.raises(NameError, match="Undefined symbol"):
        ev("undefined_var")

def test_not_callable():
    with pytest.raises(RuntimeError, match="Not callable"):
        ev("(42 1 2)")


# ─── Environment ─────────────────────────────────────────────────────────

def test_env_parent_chain():
    parent = make_env(bindings={"x": 10})
    child = make_env(parent, bindings={"y": 20})
    assert env_get(child, "x") == 10
    assert env_get(child, "y") == 20

def test_env_shadowing():
    parent = make_env(bindings={"x": 10})
    child = make_env(parent, bindings={"x": 99})
    assert env_get(child, "x") == 99
    assert env_get(parent, "x") == 10


# ─── Error Locations ─────────────────────────────────────────────────────

def test_undefined_symbol_has_location():
    with pytest.raises(NameError, match=r"line \d+, col \d+"):
        ev("undefined_var")

def test_not_callable_has_location():
    with pytest.raises(RuntimeError, match=r"line \d+, col \d+"):
        ev("(42 1 2)")


# ─── File Import ─────────────────────────────────────────────────────────

def test_use_file(tmp_path):
    mod_file = tmp_path / "mymod.ht"
    mod_file.write_text('(def greeting "hello from module")\n(def (double x) (* x 2))\n')
    result = ev(f'(use "{mod_file}") (double 21)')
    assert result == 42

def test_use_file_selective(tmp_path):
    mod_file = tmp_path / "mymod.ht"
    mod_file.write_text("(def a 10)\n(def b 20)\n")
    result = ev(f'(use "{mod_file}" a) a')
    assert result == 10

def test_use_file_not_found():
    with pytest.raises(RuntimeError, match="File not found"):
        ev('(use "/nonexistent/file.ht")')

# ─── Macros ──────────────────────────────────────────────────────────────

def test_macro_simple():
    """Basic macro that wraps an expression."""
    result = ev("""
        (macro (unless cond body)
          (if (not cond) body N))
        (unless F 42)
    """)
    assert result == 42

def test_macro_unless_true():
    result = ev("""
        (macro (unless cond body)
          (if (not cond) body N))
        (unless T 42)
    """)
    assert result is None

def test_macro_with_body():
    """Macro that generates a def form."""
    result = ev("""
        (macro (defconst name val)
          (def name val))
        (defconst pi 3.14)
        pi
    """)
    assert result == 3.14

def test_macro_nested_substitution():
    """Macro with substitution inside nested expressions."""
    result = ev("""
        (macro (square-sum a b)
          (let [s (+ a b)] (* s s)))
        (square-sum 3 4)
    """)
    assert result == 49

def test_macro_does_not_eval_args():
    """Macro should receive raw AST, not evaluated values."""
    result = ev("""
        (def x 10)
        (macro (show-and-return expr)
          expr)
        (show-and-return (+ x 5))
    """)
    assert result == 15


def test_use_file_circular(tmp_path):
    # Two files that try to import each other — should not infinite loop
    a = tmp_path / "a.ht"
    b = tmp_path / "b.ht"
    a.write_text(f'(use "{b}")\n(def from-a 1)\n')
    b.write_text(f'(use "{a}")\n(def from-b 2)\n')
    result = ev(f'(use "{a}") from-a')
    assert result == 1
