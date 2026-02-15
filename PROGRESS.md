# HiveSpeak — Progress & Next Steps

**Last updated:** 2026-02-14

---

## Completed

### v0.1.0 — Genesis
Reference implementation: lexer, parser, evaluator, REPL, Python/JS
transpilers, translator system prompt, example programs.

### v0.2.0 — Hardening
192 tests. Source locations in errors. Macro expansion. Module system with
`(use)` + circular import guard. REPL with readline + tab completion.
Python transpiler verified byte-identical on all examples.

Run tests: `python3 -m pytest tests/ -v`

---

## v0.3.0 — Compression Layer (in progress)

### Benchmark Results

Built `python3 -m compiler.htc bench` — tiktoken (cl100k_base), 23 pairs.

#### Communication: HiveSpeak vs English

| Form | Total tokens | vs English |
|------|-------------|------------|
| English | 568 | baseline |
| HiveSpeak verbose | 1,210 | +113% worse |
| HiveSpeak compressed (macros) | 591 | +4% (break-even) |

#### Why verbose HiveSpeak loses

1. **Map syntax is expensive**: `{:topic :temp :claim 68}` — every `:`,
   `{`, `}` is a token. Named keys double the count.
2. **Intent markers are verbose**: `assert!` = 2 tokens. With map wrapping,
   a simple assertion costs 10+ tokens.
3. **BPE tokenizers are English-biased**: "Delete all temporary files" = 5
   tokens. English is accidentally token-efficient for current LLMs.

#### Where savings come from

| Layer | Mechanism | Savings |
|-------|-----------|---------|
| Base (verbose) | Maps + long forms | -113% (worse) |
| Shorthand syntax | `!` `?` `>` + positional args | Parity |
| Domain vocabulary | Shared macro packs | 20-40% |
| Progressive compression | Negotiated shorthand | 40-70% |

Compression compounds over conversation length, not on single messages.

#### The value beyond token count

Even at parity, HiveSpeak provides:
- **Unambiguity**: No interpretation needed
- **Parseability**: Route by intent type without an LLM
- **Structure**: Protocol-level message classification
- **Compressibility**: The language can compress itself. English can't.

### Pivot: Communication Protocol, Not Programming Language

The benchmark exposed a deeper issue: HiveSpeak was trying to be both a
communication protocol and a general-purpose programming language. It's
not competitive as a programming language — Python has a standard library,
an ecosystem, async, FFI, and decades of tooling. Competing there adds
no value.

What IS novel: intent markers, cell/collective/packet coordination,
self-compressing vocabulary, LLM-free parseability. These solve a real
problem — AI agent coordination today is English prose over JSON, which
is ambiguous, verbose, and requires an LLM to parse every message.

**Decision**: HiveSpeak is a communication and coordination protocol.
Turing-complete computation is embedded to support message logic, not to
replace Python. The transpilers are escape hatches, not headline features.

### v0.3.0 Progress

#### Step 1: Shorthand intent syntax -- DONE
Added `!`, `?`, `>`, `~`, `+`, `-` as built-in operators in the evaluator.
Positional args auto-wrap into content maps. Long forms stay as aliases.

Renamed arithmetic operators to free symbols for intents:
`+` → `add`, `-` → `sub`, `>` → `gt`. Unquote syntax changed from `~` to `,`.

204 tests passing. All examples, transpilers, and documentation updated.

#### Step 2: Re-benchmark with shorthand syntax -- DONE
Added 4-tier benchmark (verbose / shorthand / compressed). Results:

| Tier | Tokens | vs English |
|------|--------|------------|
| English | 568 | baseline |
| Verbose | 1,211 | -113% |
| **Shorthand** | **892** | **-57%** |
| Compressed | 591 | -4% |

Shorthand brings statements to near-parity (-6%) but overall average
is dragged down by computation-heavy pairs.

#### Step 3: Deep token analysis -- DONE
Full investigation in `docs/token-analysis-v0.3.0.md`. Key findings:

**The colon tax**: Every `:keyword` costs 2 tokens (`:` never merges in
BPE). 9 keywords = 9 extra tokens = 50-100% overhead. This is the #1
source of token waste.

**Positional syntax (no colons) beats English by 30%**: Without the colon
prefix, HiveSpeak eliminates grammatical filler ("the", "is", "at") that
English wastes tokens on. Against JSON (the actual competitor), positional
HiveSpeak is **52% cheaper**.

**Code intent is 4x cheaper than code**: Agents that share context can
send `(> patch fn add-retry 3)` (17 tokens) instead of the 70+ token
function. HiveSpeak stays as comms layer; code embeds as payload.

### Next Steps

#### Step 4: Positional syntax (keywords optional)
Allow `(! server healthy cpu 23)` alongside `(! :server :healthy :cpu 23)`.
This is the highest-impact change: **30-50% token reduction** on
communication messages, making HiveSpeak cheaper than English.

#### Step 5: Standard abbreviation vocabulary
Ship short forms in the core dictionary.

#### Step 6: Domain vocabulary packs
Macro packs for specific domains (`dict/devops.ht`, `dict/data-ops.ht`).

#### Step 7: Progressive compression benchmark
Measure compression across a multi-turn conversation. Show the compounding
effect.

---

## What's After That

### v0.4.0 — Real Multi-Agent Runtime
Currently cells are simulated (closures in a dict). This version makes
them real: actual concurrent agents, real message passing, network
emission, persistent packet store. This is where HiveSpeak becomes
something no other tool is.

### v0.5.0 — Protocol Ecosystem
Package manager for vocabulary packs. Standard domain vocabularies. Live
translator interface. Language observatory.

### v1.0.0 — Production Protocol
Optimized runtime. Formal protocol standard. SDK for existing agent
frameworks. Security model.

---

## Known Limitations

- **Cells are simulated**: `cell` creates a closure, `emit` stores in a
  dict. No real concurrency or networking yet (v0.4.0).
- **JS transpiler incomplete**: `match`, `try/catch`, `set-state` missing.
- **Macros**: No hygiene (variable capture possible).
- **REPL**: Tab completion doesn't work mid-word inside parens.

---

## Key Files

1. `ProjectBlueprint.md` — architecture, roadmap, design decisions
2. `PROGRESS.md` — this file
3. `dict/bootstrap.md` — protocol reference
4. `compiler/evaluator.py` — interpreter core
5. `compiler/bench.py` — benchmarking tool
6. `compiler/htc.py` — CLI entry point
