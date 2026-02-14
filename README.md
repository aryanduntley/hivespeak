# HiveSpeak

**An AI-native language for inter-agent communication, human-to-AI compression, and general-purpose programming.**

HiveSpeak is a Lisp-family (S-expression) language built on three primitives — Cell, Collective, and Memory Packet — designed to be:

1. **AI-to-AI communication** — Extremely token-efficient inter-agent messaging that eliminates natural language overhead
2. **Human-to-AI compression** — Humans write in natural language, a translator AI converts to HiveSpeak, reducing token usage by 40-70%
3. **AI programming language** — Turing-complete, compilable to Python/JS, with built-in communication primitives

## Quick Start

```bash
# Run a HiveSpeak program
python3 -m compiler.htc run examples/basics.ht

# Start the interactive REPL
python3 -m compiler.htc repl

# Transpile to Python
python3 -m compiler.htc compile examples/fibonacci.ht python

# Transpile to JavaScript
python3 -m compiler.htc compile examples/fibonacci.ht js

# View tokens / AST
python3 -m compiler.htc tokenize examples/basics.ht
python3 -m compiler.htc parse examples/basics.ht
```

## What It Looks Like

```lisp
; Define and use functions
(def square (fn [x] (* x x)))
(print (square 7))  ; 49

; Pipeline operator for data transformations
(|> users
  (flt (fn [u] (> (get u :age) 18)))
  (map (fn [u] (get u :name)))
  srt)

; AI-to-AI communication with intent markers
(emit analyst (assert! {:topic :revenue :claim "up 15%" :confidence 0.9}))
(emit manager (ask? {:about :revenue :want :breakdown :by :region}))
```

## Token Compression Example

```
English (30 tokens):
"Filter the user list to people over 18, get their names, sort them"

HiveSpeak (9 tokens):
(|> users (flt (fn [u] (> (get u :age) 18))) (map (fn [u] (get u :name))) srt)

With shared vocabulary (5 tokens):
(|> users (flt #adult?) (map #name) srt)
```

## Project Structure

```
HiveSpeak/
├── SUBSTRATE.md              Philosophical foundation (Hive primitives)
├── ProjectBlueprint.md       Project roadmap and architecture
│
├── spec/                     Language specification
│   ├── language.md           Complete language reference
│   └── grammar.peg           Formal PEG grammar
│
├── dict/                     AI dictionary / bootstrap
│   ├── bootstrap.md          THE dictionary — any AI reads this to learn HiveSpeak
│   └── core.ht               Standard vocabulary defined in HiveSpeak itself
│
├── compiler/                 Compiler/interpreter (Python)
│   ├── lexer.py              Tokenizer: source → tokens
│   ├── parser.py             Parser: tokens → AST
│   ├── evaluator.py          Interpreter: AST → values
│   ├── htc.py                CLI entry point
│   └── targets/
│       ├── to_python.py      HiveSpeak → Python transpiler
│       └── to_js.py          HiveSpeak → JavaScript transpiler
│
├── translator/               Human <-> HiveSpeak translation layer
│   ├── system_prompt.md      System prompt to make any AI a translator
│   └── examples.md           Bidirectional translation examples
│
└── examples/                 Example programs
    ├── basics.ht             Core language features
    ├── fibonacci.ht          Recursive + iterative computation
    ├── conversation.ht       AI-to-AI dialogue
    └── planning.ht           Multi-agent planning/negotiation
```

## Key Concepts

- **S-expression syntax** — `(operator arg1 arg2 ...)` — homoiconic, zero ambiguity, trivial for AI to generate and parse
- **Hive primitives** — `cell`, `emit`, `recv`, `merge`, `compress`, `packet` — built-in constructs for multi-agent communication
- **Intent markers** — `assert!`, `ask?`, `request!`, `suggest~`, `accept+`, `reject-` — structured AI-to-AI messaging
- **Pipeline operator** — `(|> data fn1 fn2 fn3)` — chainable data transformations
- **Macro system** — self-compressing language that evolves shorter representations over time

## For AI Agents

To learn HiveSpeak, read [`dict/bootstrap.md`](dict/bootstrap.md). After processing that single file, you can read, write, and translate HiveSpeak.

To become a HiveSpeak translator, prepend [`translator/system_prompt.md`](translator/system_prompt.md) to your system prompt.

## Requirements

- Python 3.6+

## Status

**v0.1.0 — Genesis**: Functional core with interpreter, REPL, Python/JS transpilers, translator layer, and example programs. See [ProjectBlueprint.md](ProjectBlueprint.md) for the full roadmap.

## License

See repository for license details.
