# HiveSpeak Language Specification v0.1.0

## 1. Design Principles

HiveSpeak is an AI-native language optimized for:

1. **Token efficiency** — maximum semantic density per token
2. **Unambiguous parsing** — prefix notation, no precedence rules
3. **Homoiconicity** — code is data, data is code (enables self-modification)
4. **Built-in communication** — inter-agent messaging is a first-class primitive
5. **Compression** — macro system lets the language compress itself over time

HiveSpeak uses S-expression syntax: `(operator operand1 operand2 ...)`.
Every expression evaluates to a value. There are no statements.

## 2. Lexical Structure

### 2.1 Whitespace & Comments

Whitespace (space, tab, newline) separates tokens. Consecutive whitespace is
equivalent to a single space.

```
; This is a line comment — everything after ; to end of line is ignored
```

### 2.2 Tokens

The lexer produces these token types:

| Token Type  | Pattern                          | Examples              |
|-------------|----------------------------------|-----------------------|
| INT         | `-?[0-9]+`                       | `42`, `-7`, `0`       |
| FLOAT       | `-?[0-9]+\.[0-9]+`              | `3.14`, `-0.5`        |
| STRING      | `"[^"]*"`                        | `"hello"`, `""`       |
| BOOL        | `T` or `F`                       | `T`, `F`              |
| NULL        | `N`                              | `N`                   |
| SYMBOL      | `[a-zA-Z_!?][a-zA-Z0-9_!?-]*`  | `add`, `my-fn`, `x?`  |
| KEYWORD     | `:[a-zA-Z_][a-zA-Z0-9_-]*`     | `:name`, `:target`    |
| LPAREN      | `(`                              |                       |
| RPAREN      | `)`                              |                       |
| LBRACKET    | `[`                              |                       |
| RBRACKET    | `]`                              |                       |
| LBRACE      | `{`                              |                       |
| RBRACE      | `}`                              |                       |
| HASH        | `#[a-fA-F0-9]+`                 | `#a1b2c3`             |
| PIPE        | `\|>`                            |                       |

### 2.3 Reserved Symbols

These symbols have built-in semantics and cannot be rebound:

**Core forms:**
`fn` `def` `let` `do` `if` `match` `loop` `recur` `macro` `quote` `eval`

**Hive primitives:**
`cell` `emit` `recv` `merge` `compress` `ref` `packet`

**Communication intents:**
`assert!` `ask?` `request!` `suggest~` `accept+` `reject-`

**Module system:**
`mod` `use` `pub`

## 3. Data Types

### 3.1 Primitives

| Type    | Literal Syntax   | Description                     |
|---------|------------------|---------------------------------|
| Int     | `42`             | Arbitrary precision integer     |
| Float   | `3.14`           | 64-bit floating point           |
| String  | `"text"`         | UTF-8 string                    |
| Bool    | `T` / `F`        | Boolean true/false              |
| Null    | `N`              | Absence of value                |
| Keyword | `:name`          | Self-evaluating label/tag       |
| Symbol  | `foo`            | Evaluates to its bound value    |

### 3.2 Collections

| Type | Syntax          | Description                            |
|------|-----------------|----------------------------------------|
| List | `[1 2 3]`       | Ordered, indexed collection            |
| Map  | `{:a 1 :b 2}`   | Key-value pairs (keys are keywords)    |

### 3.3 Functions

Functions are first-class values created with `fn`:

```
(fn [x y] (+ x y))          ; anonymous function
```

### 3.4 Cells

Cells are the Hive primitive — autonomous state-holding units:

```
(cell {:name "worker" :count 0})   ; create a cell with initial state
```

### 3.5 Packets

Memory packets are immutable compressed artifacts:

```
(ref #a1b2c3)               ; reference an existing packet by hash
```

## 4. Core Forms

### 4.1 Binding: `def` and `let`

```
; Top-level binding
(def x 42)
(def add (fn [a b] (+ a b)))

; Shorthand for function definition
(def (add a b) (+ a b))

; Local binding (scoped)
(let [x 10
      y 20]
  (+ x y))
; => 30
```

### 4.2 Functions: `fn`

```
; Anonymous function
(fn [x] (* x x))

; Multi-expression body (last expression is return value)
(fn [x y]
  (def z (+ x y))
  (* z 2))

; Variadic (rest params)
(fn [head & rest] rest)

; Destructuring
(fn [{:keys [a b]}] (+ a b))
```

### 4.3 Conditionals: `if` and `match`

```
; if — ternary
(if (> x 0) "pos" "non-pos")

; if — without else (returns N on false)
(if (> x 0) "pos")

; match — pattern matching
(match val
  0         "zero"
  1         "one"
  [h & t]   (str "list starting with " h)
  {:a a}    (str "map with a=" a)
  _         "other")
```

### 4.4 Sequences: `do`

Evaluates expressions in order, returns the last:

```
(do
  (def x 10)
  (def y 20)
  (+ x y))
; => 30
```

### 4.5 Loops: `loop` / `recur`

```
(loop [i 0 sum 0]
  (if (> i 10)
    sum
    (recur (+ i 1) (+ sum i))))
; => 55
```

### 4.6 Quoting: `quote`

Prevents evaluation; returns the expression as data:

```
(quote (+ 1 2))    ; => the list (+ 1 2), not 3
'(+ 1 2)           ; shorthand (reader macro)
```

### 4.7 Eval: `eval`

Evaluates data as code:

```
(eval '(+ 1 2))    ; => 3
```

### 4.8 Macros: `macro`

Define syntactic transformations (code → code before evaluation):

```
(macro (unless cond body)
  '(if (not ~cond) ~body N))

(unless F "ran")   ; => "ran"
```

The `~` inside a quoted form is unquote — it evaluates the expression and
splices the result into the template.

## 5. Built-in Operators

### 5.1 Arithmetic

| Op   | Form          | Result  |
|------|---------------|---------|
| `+`  | `(+ 1 2)`    | `3`     |
| `-`  | `(- 5 3)`    | `2`     |
| `*`  | `(* 4 5)`    | `20`    |
| `/`  | `(/ 10 3)`   | `3.33`  |
| `%`  | `(% 10 3)`   | `1`     |

Variadic: `(+ 1 2 3 4)` => `10`

### 5.2 Comparison

| Op   | Form          | Result |
|------|---------------|--------|
| `=`  | `(= 1 1)`    | `T`    |
| `!=` | `(!= 1 2)`   | `T`    |
| `<`  | `(< 1 2)`    | `T`    |
| `>`  | `(> 2 1)`    | `T`    |
| `<=` | `(<= 1 1)`   | `T`    |
| `>=` | `(>= 2 1)`   | `T`    |

### 5.3 Logic

| Op    | Form          | Result |
|-------|---------------|--------|
| `and` | `(and T F)`   | `F`    |
| `or`  | `(or T F)`    | `T`    |
| `not` | `(not T)`     | `F`    |

Short-circuit: `(and F (explode))` => `F` (explode never called)

### 5.4 String Operations

| Op    | Form                    | Result        |
|-------|-------------------------|---------------|
| `cat` | `(cat "a" "b" "c")`    | `"abc"`       |
| `len` | `(len "hello")`        | `5`           |
| `slc` | `(slc "hello" 1 3)`   | `"el"`        |
| `idx` | `(idx "hello" "ll")`  | `2`           |
| `spl` | `(spl "a,b,c" ",")`   | `["a" "b" "c"]` |
| `upr` | `(upr "hello")`       | `"HELLO"`     |
| `lwr` | `(lwr "Hello")`       | `"hello"`     |
| `fmt` | `(fmt "x={}" 42)`     | `"x=42"`      |

### 5.5 List Operations

| Op    | Form                      | Result        |
|-------|---------------------------|---------------|
| `len` | `(len [1 2 3])`          | `3`           |
| `hd`  | `(hd [1 2 3])`           | `1`           |
| `tl`  | `(tl [1 2 3])`           | `[2 3]`       |
| `nth` | `(nth [10 20 30] 1)`     | `20`          |
| `cat` | `(cat [1 2] [3 4])`      | `[1 2 3 4]`   |
| `push`| `(push [1 2] 3)`         | `[1 2 3]`     |
| `map` | `(map (fn [x] (* x 2)) [1 2 3])` | `[2 4 6]` |
| `flt` | `(flt (fn [x] (> x 2)) [1 2 3 4])` | `[3 4]` |
| `red` | `(red + 0 [1 2 3 4])`    | `10`          |
| `srt` | `(srt [3 1 2])`          | `[1 2 3]`     |
| `rev` | `(rev [1 2 3])`          | `[3 2 1]`     |
| `zip` | `(zip [1 2] [3 4])`      | `[[1 3] [2 4]]` |
| `flat`| `(flat [[1 2] [3 4]])`   | `[1 2 3 4]`   |
| `uniq`| `(uniq [1 1 2 3 3])`     | `[1 2 3]`     |
| `any` | `(any (fn [x] (> x 2)) [1 2 3])` | `T`   |
| `all` | `(all (fn [x] (> x 0)) [1 2 3])` | `T`   |

### 5.6 Map Operations

| Op    | Form                        | Result          |
|-------|-----------------------------|-----------------|
| `get` | `(get {:a 1 :b 2} :a)`     | `1`             |
| `put` | `(put {:a 1} :b 2)`        | `{:a 1 :b 2}`  |
| `del` | `(del {:a 1 :b 2} :a)`     | `{:b 2}`        |
| `keys`| `(keys {:a 1 :b 2})`       | `[:a :b]`       |
| `vals`| `(vals {:a 1 :b 2})`       | `[1 2]`         |
| `has` | `(has {:a 1} :a)`           | `T`             |
| `mrg` | `(mrg {:a 1} {:b 2})`      | `{:a 1 :b 2}`  |

### 5.7 Pipeline: `|>`

Thread a value through a series of transformations:

```
(|> [1 2 3 4 5]
  (flt (fn [x] (> x 2)))
  (map (fn [x] (* x 10)))
  (red + 0))
; => 120
```

In a pipeline, the threaded value is inserted as the **last** argument of each form.

### 5.8 Type Checking

| Op       | Form              | Result |
|----------|-------------------|--------|
| `type`   | `(type 42)`       | `:int` |
| `int?`   | `(int? 42)`       | `T`    |
| `float?` | `(float? 3.14)`   | `T`    |
| `str?`   | `(str? "hi")`     | `T`    |
| `bool?`  | `(bool? T)`       | `T`    |
| `null?`  | `(null? N)`       | `T`    |
| `list?`  | `(list? [1])`     | `T`    |
| `map?`   | `(map? {:a 1})`   | `T`    |
| `fn?`    | `(fn? add)`       | `T`    |
| `cell?`  | `(cell? c)`       | `T`    |

## 6. Hive Primitives

These are the substrate operations — the reason HiveSpeak exists.

### 6.1 Cell: `cell`

Create an autonomous state-holding unit:

```
(def c (cell {:name "worker" :task N :count 0}))
```

Cell state access:

```
(get-state c)         ; => {:name "worker" :task N :count 0}
(set-state c :count 1) ; update cell state
```

### 6.2 Emit: `emit`

A cell pushes state outward:

```
(emit c :broadcast {:msg "hello" :data [1 2 3]})
(emit c :target other-cell {:msg "direct"})
```

### 6.3 Receive: `recv`

A cell listens for emissions:

```
(recv c)                    ; blocking receive (any source)
(recv c :from other-cell)   ; receive from specific source
(recv c :timeout 1000)      ; with timeout (ms)
```

### 6.4 Merge: `merge`

Partially synchronize state between cells:

```
(merge [c1 c2 c3] :on [:task :count])
; Merges only the :task and :count keys across all three cells
; Returns a collective
```

### 6.5 Compress: `compress`

Reduce a collective to a memory packet:

```
(def result (compress collective))
; result is either:
;   {:ok packet}    — successful compression
;   {:fail :loop}   — needs more merging
;   {:fail :fork}   — irreconcilable, should fork
```

### 6.6 Reference: `ref`

Access an existing memory packet by hash:

```
(ref #a1b2c3d4)
; => the packet content
```

### 6.7 Packet: `packet`

Create a named memory packet manually:

```
(def p (packet {:summary "meeting notes"
                :decisions [:use-rust :deadline-friday]
                :refs [#prev1 #prev2]}))
; Returns hash of the new packet
```

## 7. Communication Protocol

For AI-to-AI messaging, HiveSpeak defines structured intents:

### 7.1 Intent Markers

| Form        | Meaning    | Usage                              |
|-------------|------------|------------------------------------|
| `assert!`   | Declare    | State a fact or belief             |
| `ask?`      | Query      | Request information                |
| `request!`  | Command    | Ask for an action to be performed  |
| `suggest~`  | Propose    | Offer an option, no commitment     |
| `accept+`   | Affirm     | Agree to a proposal or assertion   |
| `reject-`   | Deny       | Disagree or decline                |

### 7.2 Message Structure

```
(emit sender :target receiver
  (assert! {:topic :weather
             :claim "raining"
             :confidence 0.9
             :ref #prev-observation}))

(emit sender :target receiver
  (ask? {:about :weather
          :want :forecast
          :when :tomorrow}))

(emit sender :target receiver
  (request! {:action :compute
              :fn :fibonacci
              :args [100]
              :priority :high}))
```

### 7.3 Compressed Communication

Once vocabulary is established between agents, communication compresses:

```
; Full form
(emit c1 :target c2
  (request! {:action :compute :fn :fibonacci :args [100] :priority :high}))

; Compressed via shared vocabulary (macro-defined shorthand)
(em c1 c2 (rq! :cmp :fib 100 :hi))

; Maximum compression (referencing a pre-defined pattern packet)
(em c1 c2 (rq! #fib100))
```

## 8. Module System

### 8.1 Defining Modules

```
(mod math
  (def (add a b) (+ a b))
  (def (sub a b) (- a b))
  (def pi 3.14159265)
  (def (circle-area r) (* pi (* r r))))
```

### 8.2 Using Modules

```
(use math)              ; import all
(use math add sub)      ; import specific bindings
(math.circle-area 5)    ; qualified access
```

## 9. Macro System (Compression Mechanism)

Macros are how HiveSpeak compresses itself. They transform code before evaluation.

### 9.1 Defining Macros

```
(macro (when cond & body)
  '(if ~cond (do ~@body) N))

(when (> x 0)
  (print "positive")
  (* x 2))
; Expands to: (if (> x 0) (do (print "positive") (* x 2)) N)
```

### 9.2 Quasiquoting

Inside `'(...)`:
- `~expr` — unquote: evaluate expr and insert result
- `~@expr` — splice: evaluate expr (must be list) and splice elements

### 9.3 Compression Idiom

Agents that communicate frequently will naturally define macros for common
patterns, compressing their language over time:

```
; Before compression (verbose)
(emit c1 :target c2
  (request! {:action :analyze
              :input data
              :want [:bugs :suggestions]
              :format :brief}))

; After macro compression
(macro (review! from to data)
  '(emit ~from :target ~to
     (request! {:action :analyze
                 :input ~data
                 :want [:bugs :suggestions]
                 :format :brief})))

(review! c1 c2 my-code)
```

## 10. Error Handling

```
(try
  (/ 10 0)
  (catch e
    (fmt "error: {}" e)))

(throw "something went wrong")
(throw {:code 404 :msg "not found"})
```

## 11. I/O

```
(print "hello")           ; stdout
(print-err "warning")     ; stderr
(read-line)               ; stdin
(read-file "path.txt")    ; file → string
(write-file "path.txt" data) ; string → file
```

## 12. Concurrency

```
; Spawn a concurrent cell
(def c (spawn (fn []
  (loop []
    (def msg (recv self))
    (print (fmt "got: {}" msg))
    (recur)))))

; Send to it
(emit self :target c {:msg "hello"})

; Wait for multiple
(select
  (recv c1) (fn [msg] (handle-c1 msg))
  (recv c2) (fn [msg] (handle-c2 msg))
  :timeout 5000 (fn [] "timed out"))
```

## 13. Token Efficiency Analysis

Comparison of the same semantics across representations:

### Example: "Filter a list of users to those over 18, get their names, sort alphabetically"

**English (natural language):**
```
Filter a list of users to those over 18, extract their names, and sort
them alphabetically.
```
~18 tokens

**Python:**
```python
sorted([u["name"] for u in users if u["age"] > 18])
```
~16 tokens

**HiveSpeak:**
```
(|> users (flt (fn [u] (> (get u :age) 18))) (map (fn [u] (get u :name))) srt)
```
~22 tokens (verbose form)

```
(|> users (flt #adult?) (map #name) srt)
```
~9 tokens (with shared vocabulary packets)

The savings scale with:
- **Vocabulary depth** — more shared packets = more compression
- **Conversation length** — define-once-reference-many amortizes cost
- **Domain specificity** — domain macros can compress 10:1 or better

## 14. Self-Modification Protocol

HiveSpeak can modify its own rules through the same emit-merge-compress cycle:

1. An agent **emits** a proposed language change (new macro, new builtin, new syntax)
2. Agents **merge** on the proposal (discuss, test, evaluate)
3. If consensus: **compress** the change into a vocabulary packet
4. All agents that reference the packet now speak the updated language

The language is alive. This spec is ⟐≡₀ — the zeroth packet. It will be
superseded.
