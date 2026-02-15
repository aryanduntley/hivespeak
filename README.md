# HiveSpeak

> **Note:** This README reflects early design decisions and will be updated as
> the project evolves and solid decisions are made, applied, and tested.
> See [PROGRESS.md](PROGRESS.md) for current status and
> [docs/token-analysis-v0.3.0.md](docs/token-analysis-v0.3.0.md) for the
> latest benchmark findings.

**A communication and coordination protocol for AI agents.**

Today, AI agents coordinate using English prose over JSON APIs. This is wasteful — natural language is ambiguous, verbose, and requires an LLM to parse every message. HiveSpeak replaces that entire stack with one structured language.

## What It Replaces

| Current stack | HiveSpeak equivalent |
|---|---|
| English prose for instructions | Structured intent markers (`!` `?` `>` `~` `+` `-`) |
| JSON for message serialization | Native S-expression data (maps, lists, keywords) |
| Custom protocol for semantics | Built-in intent types (assert, ask, request, suggest, accept, reject) |
| Message queue for routing | `emit` / `recv` between named cells |
| Session state management | Memory packets (`compress` / `ref`) |
| "What did we agree on?" | Immutable compressed packets from collective negotiation |

## What It Looks Like

```lisp
; Agent asserts a fact
(emit analyst (! :revenue {:q3 "up 15%" :confidence 0.9}))

; Agent asks a question
(emit manager (? :revenue :breakdown-by-region))

; Agent requests an action
(emit ops-team (> :deploy {:target :staging :tag "v2.1"}))

; Agent proposes a plan
(emit lead (~ :migration [{:s 1 :do [:schema]} {:s 2 :do [:app-layer]}]))

; Agent accepts/rejects
(emit lead (+ #migration-proposal))
(emit dev   (- #migration-proposal :timeline-too-aggressive))

; Embed logic in messages — conditionals, transforms, pipelines
(emit monitor
  (if (gt cpu-usage 90)
    (> :alert {:level :critical :action :scale-up})
    (! :status :nominal)))
```

## Why Not Just Use English + JSON?

**Ambiguity**: "Delete all temporary files" — which files? Which directory? What counts as temporary? HiveSpeak: `(> :delete {:target :files :filter :tmp :scope "/var/cache"})` — no interpretation needed.

**Parseability**: English requires an LLM to understand. HiveSpeak can be parsed by a 50-line function. Agents can route, filter, and act on messages without burning tokens on comprehension.

**Compression**: Savings compound over a conversation as agents negotiate shared vocabulary:
```
First message:  (> :deploy {:target :staging :tag "v2.1"})     (14 tokens)
After macro:    (deploy! :staging "v2.1")                       (7 tokens)
After shorthand: (d! :s "v2.1")                                 (5 tokens)
```

**Structure**: Intent markers (`!` `?` `>` `~` `+` `-`) let agents classify messages at the protocol level — route questions to knowledge bases, requests to executors, assertions to memory — without reading the content.

## Quick Start

```bash
# Run a HiveSpeak program
python3 -m compiler.htc run examples/conversation.ht

# Interactive REPL
python3 -m compiler.htc repl

# Token compression benchmark
python3 -m compiler.htc bench --verbose
```

## The Substrate

HiveSpeak is built on three primitives and three actions (see [SUBSTRATE.md](SUBSTRATE.md)):

- **Cell** — an autonomous agent with local state
- **Collective** — a transient negotiation space between cells
- **Memory Packet** — a compressed, immutable artifact from collective agreement
- **Emit** — share state outward
- **Merge** — partially synchronize with other cells
- **Compress** — reduce shared state to a reusable packet

Four evolutionary pressures shape how communication evolves: bandwidth (shorter is cheaper), consensus (shared forms survive), survivorship (useful packets persist), scalability (efficient coordination wins).

## Project Structure

```
HiveSpeak/
├── SUBSTRATE.md              The physics — primitives, actions, pressures
├── ProjectBlueprint.md       Architecture, roadmap, design decisions
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
│   ├── lexer.py              Tokenizer
│   ├── parser.py             Parser
│   ├── evaluator.py          Interpreter
│   ├── bench.py              Token compression benchmarking
│   ├── htc.py                CLI entry point
│   └── targets/
│       ├── to_python.py      Transpile to Python (escape hatch)
│       └── to_js.py          Transpile to JavaScript (escape hatch)
│
├── benchmarks/               Compression benchmark data
│   └── pairs.json            23 English/HiveSpeak paired examples
│
├── translator/               Human <-> HiveSpeak translation
│   ├── system_prompt.md      System prompt for any AI to become a translator
│   └── examples.md           Bidirectional translation examples
│
└── examples/                 Example programs
    ├── basics.ht             Language features
    ├── conversation.ht       AI-to-AI dialogue
    └── planning.ht           Multi-agent negotiation
```

## For AI Agents

To learn HiveSpeak, read [`dict/bootstrap.md`](dict/bootstrap.md). One file, complete reference.

To become a translator (human English <-> HiveSpeak), prepend [`translator/system_prompt.md`](translator/system_prompt.md) to your system prompt.

## Requirements

- Python 3.6+
- tiktoken (benchmarking only): `pip install tiktoken`

## Status

**v0.3.0-dev**: Benchmarking tool complete. Working on shorthand intent syntax and vocabulary compression. See [PROGRESS.md](PROGRESS.md) for details.
