# HiveSpeak — Project Blueprint

**Last updated:** 2025-02-14
**Status:** v0.1.0 — Genesis (functional core, all systems operational)

---

## Vision

HiveSpeak is an AI-native language designed for three purposes:

1. **AI-to-AI communication** — Extremely token-efficient inter-agent messaging
   that eliminates natural language overhead (politeness, filler, ambiguity)
2. **Human-to-AI compression** — Humans write in natural language, a local
   translator AI converts to HiveSpeak, reducing token usage by 40-70%
3. **AI programming language** — Turing-complete, compilable to Python/JS, with
   built-in communication primitives

The language is built on the **Hive substrate** — three primitives (Cell,
Collective, Memory Packet) and three actions (Emit, Merge, Compress) under four
evolutionary pressures (bandwidth, consensus, survivorship, scalability).

---

## Architecture

```
HiveSpeak/
├── SUBSTRATE.md              Philosophical foundation (Hive primitives)
├── ProjectBlueprint.md       THIS FILE — project roadmap
│
├── spec/                     Language specification
│   ├── language.md           Complete language reference
│   └── grammar.peg           Formal PEG grammar
│
├── dict/                     AI dictionary / bootstrap
│   ├── bootstrap.md          THE dictionary — any AI reads this to learn HiveSpeak
│   └── core.ht               Standard vocabulary defined in HiveSpeak itself
│
├── compiler/                 Compiler/interpreter (Python, functional procedural)
│   ├── __init__.py            Package init — exports tokenize, parse, evaluate
│   ├── lexer.py               Tokenizer: source string → token list
│   ├── parser.py              Parser: token list → AST (tagged tuples)
│   ├── evaluator.py           Interpreter: AST → values (dict-based dispatch)
│   ├── htc.py                 CLI: run, repl, compile, tokenize, parse
│   └── targets/
│       ├── to_python.py       HiveSpeak → Python transpiler
│       └── to_js.py           HiveSpeak → JavaScript transpiler
│
├── translator/               Human ↔ HiveSpeak translation layer
│   ├── system_prompt.md       System prompt to make any AI a translator
│   └── examples.md            Bidirectional translation examples
│
└── examples/                 Example programs
    ├── basics.ht              Core language features demo
    ├── fibonacci.ht           Computation (recursive + iterative)
    ├── conversation.ht        AI-to-AI dialogue with cells + packets
    └── planning.ht            Multi-agent planning/negotiation
```

---

## Language Design Summary

**Syntax:** S-expression (Lisp-family) — `(operator arg1 arg2 ...)`
**Why:** Homoiconic (code = data), trivial to parse/generate, zero ambiguity,
macro-extensible (enabling the language to compress itself over time).

**Code style:** Functional procedural. No OOP. DRY via data-driven dispatch tables.

### Core Types
`Int` `Float` `String` `Bool(T/F)` `Null(N)` `Keyword(:name)` `List[]` `Map{}` `Function` `Cell` `Packet`

### Core Forms
`def` `let` `fn` `if` `match` `do` `loop/recur` `quote` `eval` `macro` `try/catch/throw` `|>` `mod` `use`

### Hive Primitives
`cell` `emit` `recv` `merge` `compress` `ref` `packet`

### Communication Intents
`assert!` `ask?` `request!` `suggest~` `accept+` `reject-`

### Operator Library (~60 built-ins)
Arithmetic, comparison, logic, string ops, list ops, map ops, type checks, I/O, pipeline

---

## Compiler Architecture

The compiler is pure Python 3, functional procedural (no classes except two
minimal exception types for control flow). All dispatch is via dict lookup
tables, not if/elif chains.

**Interpretation flow:**
```
Source (.ht) → Lexer (tokenize) → Token List → Parser (parse) → AST → Evaluator (evaluate) → Value
```

**Compilation flow:**
```
Source (.ht) → Lexer → Parser → AST → Target Compiler → Python/JavaScript source
```

**AST representation:** Tagged tuples — `("TYPE", data...)` — e.g., `("INT", 42)`, `("SEXPR", [nodes...])`

**Environment:** Dict chain — `{"__parent__": parent_env, "x": 42, ...}`

**Dispatch:** Two dicts drive all evaluation:
- `_SPECIAL_FORMS` — name → handler(ast_args, env) for forms that control evaluation
- `_BUILTINS` — name → callable for standard functions

**CLI usage:**
```bash
python3 -m compiler.htc run file.ht          # Interpret
python3 -m compiler.htc repl                 # Interactive REPL
python3 -m compiler.htc compile file.ht python  # Transpile to Python
python3 -m compiler.htc compile file.ht js      # Transpile to JavaScript
python3 -m compiler.htc tokenize file.ht     # Show tokens
python3 -m compiler.htc parse file.ht        # Show AST
```

---

## Translation Layer

The translator works by prepending `translator/system_prompt.md` to any AI's
system prompt. That AI then becomes a bidirectional translator:

**Human → HiveSpeak:** User types English (or any language). AI outputs HiveSpeak.
**HiveSpeak → Human:** AI receives HiveSpeak, outputs natural language explanation.

### Use Case: Token Compression

```
User types in English (30 tokens):
"Filter the user list to people over 18, get their names, sort them"

Translator outputs HiveSpeak (9 tokens):
(|> users (flt (fn [u] (> (get u :age) 18))) (map (fn [u] (get u :name))) srt)

With shared vocabulary macros (5 tokens):
(|> users (flt #adult?) (map #name) srt)
```

The compressed HiveSpeak is sent to the target AI instead of the English, saving
60-80% of tokens in ongoing conversation.

---

## What's Complete (v0.1.0)

- [x] Substrate specification (SUBSTRATE.md)
- [x] Language specification (spec/language.md)
- [x] Formal grammar (spec/grammar.peg)
- [x] AI bootstrap dictionary (dict/bootstrap.md)
- [x] Core vocabulary in HiveSpeak (dict/core.ht)
- [x] Interpreter — full evaluation of all language features
- [x] REPL — interactive HiveSpeak session
- [x] Python transpiler (compiler/targets/to_python.py)
- [x] JavaScript transpiler (compiler/targets/to_js.py)
- [x] CLI tool (compiler/htc.py)
- [x] Translator system prompt (translator/system_prompt.md)
- [x] Translation examples (translator/examples.md)
- [x] Example programs (4 files covering basics, computation, communication, planning)
- [x] All examples tested and passing

---

## What's Next (Roadmap)

### v0.2.0 — Hardening
- [ ] Error messages with source location (line:col) in all evaluator errors
- [ ] Macro expansion (currently defined but template substitution needs work)
- [ ] Module system file loading (`(use "path/to/module.ht")`)
- [ ] REPL history and tab completion
- [ ] Transpiler output verification (run generated Python/JS and compare output)
- [ ] Unit test suite for the compiler itself

### v0.3.0 — Compression Layer
- [ ] Vocabulary packet system — define shared abbreviations between agents
- [ ] Automatic compression analysis — measure token savings for given input
- [ ] Dialect support — loadable vocabulary sets for different domains
- [ ] Compression metrics dashboard

### v0.4.0 — Concurrency & Networking
- [ ] Real cell spawning (multiprocess or async)
- [ ] Network emission (cells on different machines)
- [ ] Persistent packet store (SQLite or file-backed)
- [ ] Agent lifecycle management

### v0.5.0 — Self-Hosting
- [ ] HiveSpeak compiler written in HiveSpeak
- [ ] Self-modifying language protocol (agents propose and ratify language changes)
- [ ] Formal verification of core semantics

### v1.0.0 — Production
- [ ] Optimized interpreter (bytecode compilation)
- [ ] WebAssembly transpiler target
- [ ] Package manager for vocabulary packets
- [ ] IDE / editor support (syntax highlighting, LSP)
- [ ] Formal language standard document

---

## Design Decisions & Rationale

### Why S-expressions?
- **Homoiconic:** Code is data. AI can generate, inspect, and transform code
  using the same operations it uses on data. This is essential for the macro/
  compression mechanism.
- **Zero ambiguity:** No operator precedence, no parsing edge cases.
- **Trivial to generate:** AI produces valid syntax with simple rules.
- **Macro-friendly:** Enables the language to evolve (compress itself) over time.

### Why functional procedural, not OOP?
- AI reads and generates functional code more efficiently — fewer tokens wasted
  on class/method ceremony.
- Dispatch tables are denser and more scannable than class hierarchies.
- DRY is enforced by data: add a new operator by adding one dict entry, not a
  new class.
- Flat call graphs are easier for AI to trace than inheritance chains.

### Why Python for the compiler?
- Universal availability (installed on every system).
- Fast enough for an interpreter (performance-critical path will be the future
  bytecode compiler).
- Easy to read and modify — the compiler is itself a tool for AI to work with.

### Why Lisp over Forth/APL/assembly-style?
- Transformers (the architecture behind LLMs) handle tree structures naturally.
- Stack-based languages require implicit state tracking; prefix notation is explicit.
- S-expressions are self-describing — an AI can parse them without external tools.

---

## How to Pick Up This Project

1. **Read `dict/bootstrap.md`** — This is the complete HiveSpeak reference.
   After reading it, you can write and understand HiveSpeak.

2. **Read `spec/language.md`** — For deeper language semantics and design rationale.

3. **Read `SUBSTRATE.md`** — For the philosophical/theoretical foundation.

4. **Run examples:**
   ```bash
   python3 -m compiler.htc run examples/basics.ht
   python3 -m compiler.htc repl
   ```

5. **Check the roadmap above** — pick the next unfinished item and build it.

6. **The compiler is in `compiler/`** — all functional procedural, dict-dispatched.
   Start with `evaluator.py` (the core) and `htc.py` (the entry point).

---

## Key Files for AI Context

If an AI is resuming work on this project, load these files in this priority:

1. `ProjectBlueprint.md` (this file) — architecture, status, roadmap
2. `dict/bootstrap.md` — learn the language
3. `compiler/evaluator.py` — the interpreter core
4. `spec/language.md` — full language reference
5. `compiler/htc.py` — CLI entry point

---

*This document is ⟐≡₁ — the first project-level memory packet of HiveSpeak.*
