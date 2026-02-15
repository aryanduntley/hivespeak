# HiveSpeak — Project Blueprint

**Last updated:** 2026-02-14
**Status:** v0.3.0 — Shorthand operators done (204 tests), next: positional syntax

---

## What HiveSpeak Is

A communication and coordination protocol for AI agents. Not a programming
language. Not a Python competitor.

AI agents today coordinate using English prose over JSON APIs. This requires
an LLM to parse every message, wastes tokens on ambiguity and politeness, and
has no protocol-level structure for routing, negotiating, or compressing
repeated patterns.

HiveSpeak replaces that stack: English + JSON + message queue + custom protocol
+ serialization format → one structured language with built-in intent types,
agent primitives, and self-compressing vocabulary.

### What it is NOT

- **Not a general-purpose programming language.** It does not compete with
  Python, JS, Rust, or any execution language. It has no standard library,
  no package ecosystem, no async/await, no FFI.
- **Not a human language.** Humans speak English (or any natural language).
  A translator AI converts to/from HiveSpeak. Humans never need to write it.
- **Not just a serialization format.** Unlike JSON or protobuf, HiveSpeak is
  Turing-complete — agents can embed conditionals, transforms, and logic
  directly in messages. But the computation serves the communication, not
  the other way around.

### What makes it novel

1. **Intent markers as first-class protocol**: `!` (assert), `?` (ask),
   `>` (request), `~` (suggest), `+` (accept), `-` (reject). Messages are
   classifiable at the syntax level — route questions to knowledge bases,
   requests to executors, assertions to memory, without reading content.

2. **Cell/Collective/Packet model**: Agents (cells) have local state, form
   transient negotiation groups (collectives), and produce immutable compressed
   records (packets). This is a coordination primitive, not just messaging.

3. **Self-compressing vocabulary**: Macros let agents negotiate shorter forms
   over a conversation. Compression compounds — first message is verbose,
   hundredth message is dense. No other protocol does this.

4. **Parseable without an LLM**: S-expression syntax can be parsed by a
   50-line function. Agents can process, route, and filter messages without
   burning tokens on comprehension.

---

## Architecture

```
HiveSpeak/
├── SUBSTRATE.md              The physics — primitives, actions, pressures
├── ProjectBlueprint.md       THIS FILE — architecture, roadmap
├── PROGRESS.md               Current status, benchmark data, next steps
│
├── spec/                     Protocol specification
│   ├── language.md           Complete language reference
│   └── grammar.peg           Formal PEG grammar
│
├── dict/                     AI dictionary
│   ├── bootstrap.md          Any AI reads this to learn HiveSpeak
│   └── core.ht               Standard vocabulary in HiveSpeak
│
├── compiler/                 Reference implementation (Python)
│   ├── __init__.py           Package init
│   ├── lexer.py              Tokenizer: source → tokens
│   ├── parser.py             Parser: tokens → AST (tagged tuples)
│   ├── evaluator.py          Interpreter: AST → values (dict dispatch)
│   ├── bench.py              Token compression benchmarking tool
│   ├── htc.py                CLI: run, repl, bench, compile
│   └── targets/
│       ├── to_python.py      Transpile to Python (escape hatch)
│       └── to_js.py          Transpile to JavaScript (escape hatch)
│
├── benchmarks/               Compression benchmark data
│   └── pairs.json            23 English/HiveSpeak paired examples
│
├── translator/               Human <-> HiveSpeak translation
│   ├── system_prompt.md      System prompt for any AI translator
│   └── examples.md           Bidirectional translation examples
│
├── docs/                     Analysis documents
│   └── token-analysis-v0.3.0.md  BPE deep-dive, benchmark findings
│
├── tests/                    Test suite (pytest, 204 tests)
│   ├── test_lexer.py         Tokenizer tests
│   ├── test_parser.py        Parser tests
│   ├── test_evaluator.py     Interpreter tests
│   └── test_integration.py   End-to-end tests
│
└── examples/                 Example programs
    ├── basics.ht             Language features
    ├── conversation.ht       AI-to-AI dialogue
    └── planning.ht           Multi-agent negotiation
```

---

## Protocol Design

**Syntax:** S-expression — `(operator arg1 arg2 ...)`
Homoiconic, zero ambiguity, trivial to parse/generate, macro-extensible.

### Intent Markers (the protocol layer)

| Operator | Long form | Meaning | Use |
|----------|-----------|---------|-----|
| `!` | `assert!` | State a fact | Route to memory/knowledge |
| `?` | `ask?` | Ask a question | Route to knowledge bases |
| `>` | `request!` | Request an action | Route to executors |
| `~` | `suggest~` | Propose something | Route to negotiation |
| `+` | `accept+` | Accept a proposal | Close negotiation |
| `-` | `reject-` | Reject a proposal | Counter or escalate |

### Agent Primitives

| Primitive | Purpose |
|-----------|---------|
| `cell` | Create an agent with local state |
| `emit` | Send a message from one cell to another |
| `recv` | Receive messages |
| `merge` | Partially synchronize state between cells |
| `compress` | Reduce shared state to an immutable packet |
| `ref` | Reference a previous packet |
| `packet` | Create a memory packet directly |

### Embedded Computation

The protocol is Turing-complete so agents can embed logic in messages:
`def` `let` `fn` `if` `match` `do` `loop/recur` `|>` `macro`

This is not for writing applications — it's for expressing conditional
routing, data transforms, and negotiation logic within the protocol.

### Data Types

`Int` `Float` `String` `Bool(T/F)` `Null(N)` `Keyword(:name)` `List[]`
`Map{}` `Function` `Cell` `Packet`

---

## Reference Implementation

The compiler is pure Python 3, functional procedural, dict-dispatched.
It serves as the reference implementation of the protocol — not a
production runtime.

**Interpretation:** Source → Lexer → Parser → AST → Evaluator → Value
**Transpilation:** Source → Lexer → Parser → AST → Python or JS source

Transpilers are escape hatches — when an agent needs to execute logic on
a host, it can compile a HiveSpeak expression to Python/JS. The transpilers
are not the main value.

```bash
python3 -m compiler.htc run file.ht           # Interpret
python3 -m compiler.htc repl                  # Interactive REPL
python3 -m compiler.htc bench --verbose       # Compression benchmark
python3 -m compiler.htc compile file.ht python  # Transpile (escape hatch)
```

---

## Token Compression: Honest Numbers

Benchmarked with tiktoken (cl100k_base) across 23 paired examples.
Full data in PROGRESS.md.

### The finding

Base HiveSpeak (verbose maps + long intent markers) does NOT save tokens
over English. BPE tokenizers are English-biased — natural language is
accidentally token-efficient for current LLMs.

### Measured results (4-tier benchmark)

| Layer | Mechanism | vs English |
|-------|-----------|------------|
| Verbose | `(assert! {:topic X :claim Y})` | **-113%** (2.1x worse) |
| Shorthand | `(! :key val :key val)` | **-57%** (1.6x worse) |
| Compressed | Custom macros | **-4%** (break-even) |

Full analysis: `docs/token-analysis-v0.3.0.md`

### Root cause: the colon tax

Every `:keyword` costs 2 BPE tokens (`:` never merges with the word).
9 keywords in one message = 9 extra tokens = 50-100% overhead. This is
the single biggest source of token waste.

### The breakthrough: positional syntax

Dropping the `:` prefix and using bare symbols makes HiveSpeak **30%
cheaper than English** and **52% cheaper than JSON** (the actual
competitor for agent communication):

| Format | Tokens (6 examples) |
|--------|---------------------|
| JSON | 157 |
| English | 117 |
| HiveSpeak positional | **75** |

English wastes tokens on grammar ("the", "is", "at", "there are").
JSON wastes tokens on delimiters (`"`, `{`, `}`). HiveSpeak eliminates
both. The colon prefix was the only thing making it more expensive.

### Code stays as payload

Code (Python, JS, etc.) costs 2.2-2.5 chars/token — the worst case for
BPE. But HiveSpeak shouldn't try to represent code. Agents that share
context can send intent instead: `(> patch fn add-retry 3)` is 17 tokens
vs 70+ for the actual function. Code embeds as string payloads when exact
bytes matter. HiveSpeak is the comms layer, not the code layer.

### The real value isn't token count

Even at parity, HiveSpeak provides:
- **Unambiguity**: No interpretation needed. Messages are precise.
- **Parseability**: Route messages by intent type without an LLM.
- **Structure**: Protocol-level classification of every message.
- **Compressibility**: The language can compress itself. English can't.

---

## Roadmap

### v0.1.0 — Genesis ✓
Protocol specification, reference interpreter, REPL, translator layer,
Python/JS transpilers, example programs.

### v0.2.0 — Hardening ✓
192 tests, source locations in errors, macro expansion, module system,
REPL history + completion, transpiler verification.

### v0.3.0 — Compression Layer (in progress)
- [x] Benchmarking tool (`compiler/bench.py`, 23 pairs, 4-tier, tiktoken)
- [x] Shorthand intent syntax (`!` `?` `>` `~` `+` `-` as operators)
- [x] Positional argument conventions for shorthand intents
- [x] Arithmetic operator renames (`+`→`add`, `-`→`sub`, `>`→`gt`)
- [x] Deep token analysis (`docs/token-analysis-v0.3.0.md`)
- [ ] Positional syntax — make keywords optional (drop `:` prefix) — **NEXT**
- [ ] Standard abbreviation vocabulary
- [ ] Domain vocabulary packs (devops, data-ops)
- [ ] Progressive compression benchmark (multi-turn measurement)

### v0.4.0 — Real Multi-Agent Runtime
This is where HiveSpeak becomes something no other tool is. Currently
cells are simulated (closures in a dict). This version makes them real:
- [ ] Actual concurrent cells (async or multiprocess)
- [ ] Real message passing between cells
- [ ] Network emission (cells on different machines)
- [ ] Persistent packet store (SQLite)
- [ ] Agent lifecycle management
- [ ] Observable: do the evolutionary pressures produce predicted structures?

### v0.5.0 — Protocol Ecosystem
- [ ] Package manager for vocabulary packs
- [ ] Standard domain vocabularies (devops, data, finance, etc.)
- [ ] Live translator interface (human pastes English, gets HiveSpeak)
- [ ] Language observatory (track how vocabulary evolves in practice)

### v1.0.0 — Production Protocol
- [ ] Optimized runtime
- [ ] Formal protocol standard
- [ ] SDK for integrating HiveSpeak into existing agent frameworks
- [ ] Security model (message authentication, cell permissions)

---

## Design Decisions

### Why S-expressions?
- Homoiconic (code = data) — essential for macro-driven compression
- Zero ambiguity — no parsing edge cases
- Trivial to generate — AI produces valid syntax with simple rules
- 50-line parser — any runtime can implement it

### Why not JSON?
JSON is a data format. It has no computation, no macros, no intent markers,
no compression mechanism. You'd need JSON + a protocol spec + a macro
system + a message router. HiveSpeak is all of those in one syntax.

### Why English keywords (def, fn, let)?
BPE tokenizers are English-biased. `def` = 1 token. `⟐` = 2-3 tokens.
English keywords are accidentally token-optimal. The macro system lets
agents compress further when it helps.

### Why keywords (`:name`) should be optional
v0.3.0 analysis found the `:` prefix doubles the token cost of every
name. Positional syntax with bare symbols (`server` not `:server`)
beats English by 30%. Keywords remain available for map literals and
self-describing data, but communication messages should default to
positional conventions.

### Why not just use terse English?
"del temp files" (3 tokens) beats HiveSpeak on raw token count. But
it's not parseable without an LLM, has no intent routing, no structure,
and no compression mechanism. HiveSpeak pays 1-3 extra tokens for
machine parseability — a worthwhile trade.

### Why not try to compress code?
Code (Python, JS, etc.) costs 2-3x more tokens per character than prose.
But agents that share context can transmit intent instead of code:
`(> write-fn fibonacci iterative)` = 8 tokens vs 53 for the actual
function. HiveSpeak is the coordination layer; code embeds as payload
when exact bytes are needed.

### Why Turing-complete?
So agents can embed logic in messages: "if X then do Y else do Z" as a
single parseable expression, not a prose paragraph requiring LLM
interpretation. The computation serves the protocol.

### Why not just extend an existing Lisp?
Clojure, Racket, etc. are programming languages first. They don't have
intent markers, cell primitives, or self-compressing vocabulary as core
features. HiveSpeak is communication first, computation second.

---

## How to Pick Up This Project

1. **Read `dict/bootstrap.md`** — learn the language in one file
2. **Read `SUBSTRATE.md`** — the theoretical foundation
3. **Run examples:** `python3 -m compiler.htc run examples/conversation.ht`
4. **Run benchmarks:** `python3 -m compiler.htc bench --verbose`
5. **Check the roadmap above** — pick the next unfinished item
6. **The core is `compiler/evaluator.py`** — all dispatch via dicts

---

*This document is ⟐≡₁ — the first project-level memory packet of HiveSpeak.*
