"""Integration tests — run example .ht files and verify output."""

import subprocess
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_ht(filename):
    """Run a .ht file and return (stdout, stderr, returncode)."""
    path = os.path.join(PROJECT_ROOT, "examples", filename)
    result = subprocess.run(
        ["python3", "-m", "compiler.htc", "run", path],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return result.stdout, result.stderr, result.returncode


def run_cmd(cmd_args):
    """Run an htc command and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        ["python3", "-m", "compiler.htc"] + cmd_args,
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return result.stdout, result.stderr, result.returncode


# ─── Example files run without error ─────────────────────────────────────

def test_basics_runs():
    out, err, rc = run_ht("basics.ht")
    assert rc == 0, f"basics.ht failed: {err}"
    assert "42" in out
    assert "hello HiveSpeak" in out
    assert "3628800" in out  # factorial

def test_fibonacci_runs():
    out, err, rc = run_ht("fibonacci.ht")
    assert rc == 0, f"fibonacci.ht failed: {err}"
    assert "fib-naive(10) = 55" in out
    assert "fib(10) = 55" in out
    assert "fib(20) = 6765" in out
    assert "fib(30) = 832040" in out

def test_conversation_runs():
    out, err, rc = run_ht("conversation.ht")
    assert rc == 0, f"conversation.ht failed: {err}"
    assert "Agent A:" in out
    assert "Agent B:" in out
    assert "Conversation complete" in out

def test_planning_runs():
    out, err, rc = run_ht("planning.ht")
    assert rc == 0, f"planning.ht failed: {err}"
    assert "Dev proposes:" in out
    assert "QA rejects:" in out
    assert "Final plan packet:" in out

def test_calculator_runs():
    out, err, rc = run_ht("calculator.ht")
    assert rc == 0, f"calculator.ht failed: {err}"
    assert "10 + 5 = 15" in out
    assert "10 / 0 = Error: divide by zero" in out


# ─── Specific output verification ────────────────────────────────────────

def test_basics_arithmetic_output():
    out, _, _ = run_ht("basics.ht")
    lines = out.strip().split("\n")
    assert lines[0] == "42"
    assert lines[1] == "3.14"
    assert lines[2] == "hello HiveSpeak"
    assert lines[3] == "T"
    assert lines[4] == "F"
    assert lines[5] == "N"
    assert lines[6] == "5"       # + 2 3
    assert lines[7] == "20"      # * 4 5
    assert lines[8] == "7"       # - 10 3

def test_fibonacci_sequence():
    out, _, _ = run_ht("fibonacci.ht")
    assert "First 15: [0 1 1 2 3 5 8 13 21 34 55 89 144 233 377]" in out


# ─── CLI commands ────────────────────────────────────────────────────────

def test_tokenize_command():
    path = os.path.join(PROJECT_ROOT, "examples", "basics.ht")
    out, err, rc = run_cmd(["tokenize", path])
    assert rc == 0
    assert "SYM" in out or "INT" in out

def test_parse_command():
    path = os.path.join(PROJECT_ROOT, "examples", "basics.ht")
    out, err, rc = run_cmd(["parse", path])
    assert rc == 0
    assert "SEXPR" in out

def test_compile_python():
    path = os.path.join(PROJECT_ROOT, "examples", "fibonacci.ht")
    out, err, rc = run_cmd(["compile", path, "python"])
    assert rc == 0
    assert "def " in out or "print" in out

def test_compile_js():
    path = os.path.join(PROJECT_ROOT, "examples", "fibonacci.ht")
    out, err, rc = run_cmd(["compile", path, "js"])
    assert rc == 0
    assert "function" in out or "console" in out

def test_no_args_shows_usage():
    out, err, rc = run_cmd([])
    assert rc == 1
