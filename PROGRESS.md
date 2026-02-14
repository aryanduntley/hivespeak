# HiveSpeak — Progress & Next Steps

**Last updated:** 2026-02-14

---

## Current State: v0.2.0 — Hardening Complete

All v0.2.0 roadmap items are done. The compiler is tested, errors have source
locations, macros work, files can be imported, and transpiler output is verified.

### What was built in this session

| Item | Status | Details |
|------|--------|---------|
| Unit test suite | Done | 192 tests across 5 files (lexer, parser, evaluator, integration, transpiler) |
| Source locations in errors | Done | AST nodes carry `(line, col)`, all NameError/RuntimeError include location |
| Module file loading | Done | `(use "path/to/file.ht")` with circular import guard and selective imports |
| Macro expansion | Done | Template substitution via AST rewriting, rest params supported |
| REPL history + completion | Done | readline-based, persistent history at `~/.hivespeak/repl_history`, tab completes all symbols |
| Python transpiler fixes | Done | Added full stdlib, fixed loop/recur, let scoping, operators-as-values |
| JS transpiler fixes | Done | Fixed loop/recur, added missing stdlib (len, map), operators-as-values |
| Transpiler verification | Done | Python output byte-identical to interpreter on all 5 examples |
| Evolution paths documented | Done | 6 future directions added to ProjectBlueprint.md |

### Test suite breakdown

```
tests/test_lexer.py        — 33 tests  (tokenization, locations, edge cases)
tests/test_parser.py       — 30 tests  (AST structure, source locations)
tests/test_evaluator.py    — 110 tests (every type, form, builtin, macro, file import)
tests/test_integration.py  — 12 tests  (example programs, CLI commands)
tests/test_transpiler.py   — 7 tests   (compile + run + compare output)
```

Run: `python3 -m pytest tests/ -v`

---

## What's Next: v0.3.0 — Compression Layer

This is where HiveSpeak starts demonstrating its core value proposition: token
compression between AI agents.

| Item | Priority | Notes |
|------|----------|-------|
| Vocabulary packet system | High | Define shared abbreviations between agents. Uses macros + `(use)` |
| Token compression benchmarking | High | Measure actual savings with tiktoken. Turn "40-70%" into a tested number |
| Dialect support | Medium | Loadable vocabulary sets for different domains |
| Compression metrics dashboard | Low | Visualize compression ratios |

### Suggested approach for v0.3.0

1. **Vocabulary packets** — A `.ht` file that defines macros for a domain.
   Example: `dict/devops.ht` defines `(deploy!)`, `(rollback!)`, etc. as
   macros that expand to longer intent expressions. Agents load with `(use)`.

2. **Benchmarking tool** — CLI command: `python3 -m compiler.htc bench "english text"`
   that translates via the system prompt, counts tokens both ways, reports ratio.

3. **Dialect loading** — `(use :dialect "devops")` syntactic sugar that looks up
   `dict/<name>.ht` automatically.

---

## What's After That

### v0.4.0 — Concurrency & Networking
- Real cell spawning (async/multiprocess)
- Network emission (cells on different machines)
- Persistent packet store (SQLite)

### v0.5.0 — Self-Hosting
- HiveSpeak compiler written in HiveSpeak
- Self-modifying language protocol

### v1.0.0 — Production
- Bytecode compiler, WebAssembly target, package manager, LSP

---

## Evolution Paths (exploratory, not sequenced)

These are documented in detail in `ProjectBlueprint.md`:

- **Token Compression Benchmarking** — empirical measurement tool
- **Live Translator Interface** — CLI/web demo of human↔HiveSpeak translation
- **Dogfooding** — write HiveSpeak's test cases in HiveSpeak
- **Multi-Agent Runtime** — actual concurrent cells, not simulated
- **Vocabulary Packet Ecosystem** — shared domain-specific macro libraries
- **Language Observatory** — instrument the runtime to observe language evolution

---

## Key Files to Load (for AI context)

1. `ProjectBlueprint.md` — architecture, roadmap, design decisions
2. `PROGRESS.md` — this file, current status and next steps
3. `dict/bootstrap.md` — learn the language
4. `compiler/evaluator.py` — interpreter core
5. `compiler/htc.py` — CLI entry point

---

## Known Limitations

- **JS transpiler**: `match`, `try/catch`, `set-state` not yet compiled.
  JS basics runs partially; calculator/conversation/planning need more JS work.
- **Python transpiler `let`**: Uses nested lambdas — works but generates
  unreadable code for deep bindings. Could use a helper function pattern.
- **Macros**: No hygiene (variable capture possible). Fine for now, revisit
  if it causes real issues.
- **REPL**: Tab completion doesn't complete mid-word inside parentheses
  (readline limitation with custom delimiters).
