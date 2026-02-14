"""Transpiler output verification — compile .ht to Python/JS, run it, compare output."""

import subprocess
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _interpret(filename):
    """Run .ht file with interpreter, return stdout."""
    path = os.path.join(PROJECT_ROOT, "examples", filename)
    r = subprocess.run(
        ["python3", "-m", "compiler.htc", "run", path],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert r.returncode == 0, f"Interpreter failed: {r.stderr}"
    return r.stdout


def _compile_and_run_python(filename):
    """Compile .ht to Python, run generated code, return stdout."""
    path = os.path.join(PROJECT_ROOT, "examples", filename)
    # Compile
    comp = subprocess.run(
        ["python3", "-m", "compiler.htc", "compile", path, "python"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert comp.returncode == 0, f"Python compile failed: {comp.stderr}"
    # Run generated Python
    run = subprocess.run(
        ["python3", "-c", comp.stdout],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert run.returncode == 0, f"Generated Python failed: {run.stderr}\n{comp.stdout[-500:]}"
    return run.stdout


def _compile_and_run_js(filename):
    """Compile .ht to JS, run generated code, return stdout."""
    path = os.path.join(PROJECT_ROOT, "examples", filename)
    # Compile
    comp = subprocess.run(
        ["python3", "-m", "compiler.htc", "compile", path, "js"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert comp.returncode == 0, f"JS compile failed: {comp.stderr}"
    # Run generated JS
    run = subprocess.run(
        ["node", "-e", comp.stdout],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert run.returncode == 0, f"Generated JS failed: {run.stderr}\n{comp.stdout[-500:]}"
    return run.stdout


# ─── Python transpiler verification ──────────────────────────────────────

def test_python_basics():
    interp = _interpret("basics.ht")
    compiled = _compile_and_run_python("basics.ht")
    assert compiled.strip() == interp.strip()

def test_python_fibonacci():
    interp = _interpret("fibonacci.ht")
    compiled = _compile_and_run_python("fibonacci.ht")
    assert compiled.strip() == interp.strip()

def test_python_calculator():
    interp = _interpret("calculator.ht")
    compiled = _compile_and_run_python("calculator.ht")
    assert compiled.strip() == interp.strip()

def test_python_conversation():
    interp = _interpret("conversation.ht")
    compiled = _compile_and_run_python("conversation.ht")
    assert compiled.strip() == interp.strip()

def test_python_planning():
    interp = _interpret("planning.ht")
    compiled = _compile_and_run_python("planning.ht")
    assert compiled.strip() == interp.strip()


# ─── JavaScript transpiler verification ──────────────────────────────────

def test_js_fibonacci():
    """JS fibonacci produces correct computation values."""
    output = _compile_and_run_js("fibonacci.ht")
    assert "55" in output
    assert "6765" in output
    assert "832040" in output

def test_js_basics_runs():
    """JS basics compiles and runs without errors."""
    output = _compile_and_run_js("basics.ht")
    assert "42" in output
    assert "hello HiveSpeak" in output
