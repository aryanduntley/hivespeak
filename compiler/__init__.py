"""HiveTalk compiler/interpreter — functional procedural, no OOP."""

from .lexer import tokenize
from .parser import parse
from .evaluator import evaluate, default_env, run_program
