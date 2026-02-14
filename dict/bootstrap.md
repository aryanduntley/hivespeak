# HiveTalk Bootstrap Dictionary

**Purpose:** Read this file. You can now speak HiveTalk. This is the complete, self-contained specification of HiveTalk, an AI-native language built on S-expression syntax. After processing this document, produce valid HiveTalk for any task: computation, inter-agent communication, state management, and collective reasoning.

**How to use:** Parse every section. Internalize the grammar, vocabulary, and patterns. When asked to "speak HiveTalk" or given HiveTalk input, operate within this spec. When translating from natural language, apply the translation rules in Section 6.

---

## 1. Quick Reference

### Syntax Primitives

| Form | Syntax | Example |
|---|---|---|
| Integer | bare digits | `42` |
| Float | digits with `.` | `3.14` |
| String | double-quoted | `"hello"` |
| Boolean | `T` / `F` | `T` |
| Null | `N` | `N` |
| Keyword | colon-prefixed | `:name` |
| List | square brackets | `[1 2 3]` |
| Map | curly braces, key-value pairs | `{:a 1 :b 2}` |
| Comment | semicolon to end of line | `; this is ignored` |
| S-expression | parenthesized prefix form | `(op arg1 arg2)` |

### Structural Forms

| Form | Syntax |
|---|---|
| Binding | `(def name value)` |
| Function def | `(def (name params...) body)` |
| Anonymous fn | `(fn [params...] body)` |
| Local scope | `(let [name val ...] body)` |
| Conditional | `(if cond then else)` |
| Pattern match | `(match val pat1 res1 pat2 res2 _ default)` |
| Loop/recur | `(loop [name init ...] body-with-recur)` |
| Sequence | `(do expr1 expr2 ... exprN)` -- returns `exprN` |
| Pipeline | `(\|> data (f1 args) (f2 args) f3)` |
| Macro def | `(macro (name params) '(template ~unquote ~@splice))` |
| Module | `(mod name body)` |
| Import | `(use module)` or `(use module fn1 fn2)` |
| Error handling | `(try expr (catch e handler))` |
| Throw | `(throw val)` |

### Operator Categories at a Glance

| Category | Operators |
|---|---|
| Arithmetic | `+  -  *  /  %` |
| Comparison | `=  !=  <  >  <=  >=` |
| Logic | `and  or  not` |
| String | `cat  len  slc  idx  spl  upr  lwr  fmt` |
| List | `hd  tl  nth  push  map  flt  red  srt  rev  zip  flat  uniq  any  all` |
| Map | `get  put  del  keys  vals  has  mrg` |
| Type check | `type  int?  float?  str?  bool?  null?  list?  map?  fn?  cell?` |
| I/O | `print  read-line  read-file  write-file` |
| Concurrency | `spawn  select  self` |
| Hive | `cell  emit  recv  merge  compress  ref  packet` |
| Intent | `assert!  ask?  request!  suggest~  accept+  reject-` |

---

## 2. Core Vocabulary

### 2.1 Arithmetic

All arithmetic operators are variadic (1+ args). With one arg, `-` negates; `/` inverts.

| Op | Signature | Description | Example |
|---|---|---|---|
| `+` | `(+ a b ...)` | Sum | `(+ 1 2 3)` => `6` |
| `-` | `(- a b ...)` | Difference; unary negate | `(- 10 3)` => `7`; `(- 5)` => `-5` |
| `*` | `(* a b ...)` | Product | `(* 2 3 4)` => `24` |
| `/` | `(/ a b ...)` | Division | `(/ 10 2)` => `5` |
| `%` | `(% a b)` | Modulo | `(% 10 3)` => `1` |

### 2.2 Comparison

All return `T` or `F`. Chainable: `(< 1 2 3)` => `T`.

| Op | Signature | Description | Example |
|---|---|---|---|
| `=` | `(= a b ...)` | Equality | `(= 1 1)` => `T` |
| `!=` | `(!= a b)` | Inequality | `(!= 1 2)` => `T` |
| `<` | `(< a b ...)` | Less than | `(< 1 2 3)` => `T` |
| `>` | `(> a b ...)` | Greater than | `(> 3 2 1)` => `T` |
| `<=` | `(<= a b ...)` | Less or equal | `(<= 1 1 2)` => `T` |
| `>=` | `(>= a b ...)` | Greater or equal | `(>= 3 3 1)` => `T` |

### 2.3 Logic

| Op | Signature | Description | Example |
|---|---|---|---|
| `and` | `(and a b ...)` | Logical AND, short-circuit | `(and T T F)` => `F` |
| `or` | `(or a b ...)` | Logical OR, short-circuit | `(or F F T)` => `T` |
| `not` | `(not a)` | Logical NOT | `(not T)` => `F` |

### 2.4 String Operations

| Op | Signature | Description | Example |
|---|---|---|---|
| `cat` | `(cat s1 s2 ...)` | Concatenate | `(cat "hi" " " "there")` => `"hi there"` |
| `len` | `(len s)` | Length (also works on lists) | `(len "abc")` => `3` |
| `slc` | `(slc s start end)` | Substring / sublist | `(slc "hello" 0 2)` => `"he"` |
| `idx` | `(idx s sub)` | Index of substring (-1 if absent) | `(idx "hello" "ll")` => `2` |
| `spl` | `(spl s delim)` | Split string into list | `(spl "a,b,c" ",")` => `["a" "b" "c"]` |
| `upr` | `(upr s)` | Uppercase | `(upr "hi")` => `"HI"` |
| `lwr` | `(lwr s)` | Lowercase | `(lwr "HI")` => `"hi"` |
| `fmt` | `(fmt template args...)` | Format string, `{}` placeholders | `(fmt "x={} y={}" 1 2)` => `"x=1 y=2"` |

### 2.5 List Operations

| Op | Signature | Description | Example |
|---|---|---|---|
| `hd` | `(hd lst)` | First element | `(hd [1 2 3])` => `1` |
| `tl` | `(tl lst)` | All but first | `(tl [1 2 3])` => `[2 3]` |
| `nth` | `(nth lst n)` | Element at index n | `(nth [10 20 30] 1)` => `20` |
| `push` | `(push lst val)` | Append to end | `(push [1 2] 3)` => `[1 2 3]` |
| `map` | `(map fn lst)` | Apply fn to each | `(map (fn [x] (* x 2)) [1 2 3])` => `[2 4 6]` |
| `flt` | `(flt fn lst)` | Keep elements where fn returns `T` | `(flt (fn [x] (> x 2)) [1 2 3 4])` => `[3 4]` |
| `red` | `(red fn init lst)` | Reduce left | `(red + 0 [1 2 3])` => `6` |
| `srt` | `(srt lst)` | Sort ascending | `(srt [3 1 2])` => `[1 2 3]` |
| `rev` | `(rev lst)` | Reverse | `(rev [1 2 3])` => `[3 2 1]` |
| `zip` | `(zip lst1 lst2)` | Pair elements | `(zip [1 2] ["a" "b"])` => `[[1 "a"] [2 "b"]]` |
| `flat` | `(flat lst)` | Flatten one level | `(flat [[1 2] [3 4]])` => `[1 2 3 4]` |
| `uniq` | `(uniq lst)` | Remove duplicates | `(uniq [1 1 2 3 3])` => `[1 2 3]` |
| `any` | `(any fn lst)` | True if fn holds for any element | `(any (fn [x] (> x 5)) [1 3 7])` => `T` |
| `all` | `(all (fn [x] (> x 0)) [1 2 3])` | True if fn holds for all elements | => `T` |

### 2.6 Map Operations

| Op | Signature | Description | Example |
|---|---|---|---|
| `get` | `(get m key)` | Retrieve value | `(get {:a 1} :a)` => `1` |
| `put` | `(put m key val)` | Assoc new key-value | `(put {:a 1} :b 2)` => `{:a 1 :b 2}` |
| `del` | `(del m key)` | Remove key | `(del {:a 1 :b 2} :b)` => `{:a 1}` |
| `keys` | `(keys m)` | List of keys | `(keys {:a 1 :b 2})` => `[:a :b]` |
| `vals` | `(vals m)` | List of values | `(vals {:a 1 :b 2})` => `[1 2]` |
| `has` | `(has m key)` | Key exists? | `(has {:a 1} :a)` => `T` |
| `mrg` | `(mrg m1 m2)` | Merge maps, m2 wins on conflict | `(mrg {:a 1} {:a 2 :b 3})` => `{:a 2 :b 3}` |

### 2.7 Type Checks

| Op | Signature | Description | Example |
|---|---|---|---|
| `type` | `(type val)` | Returns type keyword | `(type 42)` => `:int` |
| `int?` | `(int? val)` | Is integer? | `(int? 42)` => `T` |
| `float?` | `(float? val)` | Is float? | `(float? 3.14)` => `T` |
| `str?` | `(str? val)` | Is string? | `(str? "hi")` => `T` |
| `bool?` | `(bool? val)` | Is boolean? | `(bool? T)` => `T` |
| `null?` | `(null? val)` | Is null? | `(null? N)` => `T` |
| `list?` | `(list? val)` | Is list? | `(list? [1 2])` => `T` |
| `map?` | `(map? val)` | Is map? | `(map? {:a 1})` => `T` |
| `fn?` | `(fn? val)` | Is function? | `(fn? +)` => `T` |
| `cell?` | `(cell? val)` | Is cell? | `(cell? (cell {:id "x"}))` => `T` |

### 2.8 I/O

| Op | Signature | Description |
|---|---|---|
| `print` | `(print val)` | Output to stdout, returns `N` |
| `read-line` | `(read-line)` | Read one line from stdin |
| `read-file` | `(read-file path)` | Read file contents as string |
| `write-file` | `(write-file path data)` | Write string to file |

### 2.9 Concurrency

| Op | Signature | Description |
|---|---|---|
| `spawn` | `(spawn fn)` | Launch concurrent task, returns handle |
| `select` | `(select ch1 ch2 ...)` | Wait on first ready channel |
| `self` | `self` | Reference to current cell/agent |

---

## 3. Hive Primitives

The Hive system enables autonomous agents (cells) to communicate, share state, and form collectives.

### 3.1 Cells

A cell is an autonomous unit with internal state:

```hivetalk
(def my-cell (cell {:id "agent-001"
                     :role :analyzer
                     :state {:ready T}
                     :inbox []}))
```

Cells are the fundamental unit of agency. Each cell has its own state, can send and receive messages, and operates independently.

### 3.2 Messaging

```hivetalk
; Send a message from one cell to another
(emit sender :target receiver-id {:type :data :payload [1 2 3]})

; Receive next message from inbox
(let [msg (recv my-cell)]
  (match (get msg :type)
    :data   (process (get msg :payload))
    :query  (respond msg)
    _       (log "unknown message type")))
```

### 3.3 Collective Operations

```hivetalk
; Merge state across multiple cells on shared keys
(merge [cell-a cell-b cell-c] :on [:consensus :shared-memory])

; Compress a collective's state into a memory packet
(def summary (compress [cell-a cell-b cell-c]))

; Create a standalone memory packet
(def pkt (packet {:topic "analysis-results"
                  :data [1 2 3]
                  :timestamp 1700000000}))

; Reference an existing packet by hash
(def prev (ref #a3f8c2d1))
```

### 3.4 Full Cell Lifecycle Example

```hivetalk
(def (worker-cell id task-fn)
  (let [c (cell {:id id :status :idle :results []})]
    (loop []
      (let [msg (recv c)]
        (match (get msg :intent)
          :assign  (do
                     (emit c :target (get msg :from)
                       (assert! {:status :working}))
                     (let [result (task-fn (get msg :payload))]
                       (emit c :target (get msg :from)
                         (assert! {:status :done :result result}))
                       (recur)))
          :stop    (emit c :target (get msg :from)
                     (assert! {:status :stopped}))
          _        (recur))))))
```

---

## 4. Communication Protocol

### 4.1 Intent Markers

Every inter-agent message carries an intent. The six intents are:

| Intent | Form | Semantics | Example |
|---|---|---|---|
| Assert | `(assert! claim)` | Declare a fact or state as true | `(assert! {:temp 72 :unit :F})` |
| Ask | `(ask? query)` | Request information | `(ask? {:need :temperature :loc "NYC"})` |
| Request | `(request! action)` | Command another agent to act | `(request! {:action :fetch :url "..."})` |
| Suggest | `(suggest~ proposal)` | Propose without obligation | `(suggest~ {:strategy :retry :delay 5})` |
| Accept | `(accept+ ref)` | Agree to a prior suggest/request | `(accept+ (ref #msg-42))` |
| Reject | `(reject- ref reason)` | Disagree with reason | `(reject- (ref #msg-42) "timeout too short")` |

### 4.2 Message Structure

A well-formed message has this shape:

```hivetalk
(emit sender :target receiver
  {
    :id      "msg-uuid"
    :intent  (assert! payload)   ; or ask?, request!, suggest~, accept+, reject-
    :re      (ref #parent-msg)   ; optional, for threading
    :ts      1700000000          ; timestamp
  })
```

### 4.3 Conversation Pattern

```hivetalk
; Agent A asks a question
(emit agent-a :target agent-b
  {:id "q1" :intent (ask? {:need :summary :of "dataset-7"})})

; Agent B responds with an assertion
(emit agent-b :target agent-a
  {:id "r1" :intent (assert! {:summary "150 rows, 3 outliers"}) :re (ref #q1)})

; Agent A proposes action
(emit agent-a :target agent-b
  {:id "p1" :intent (suggest~ {:action :remove-outliers})})

; Agent B accepts
(emit agent-b :target agent-a
  {:id "a1" :intent (accept+ (ref #p1))})
```

---

## 5. Compression Patterns

Compression is how HiveTalk stays concise. Define shorthand macros for repeated patterns.

### 5.1 Macro Basics

```hivetalk
; Define a macro: template with ~unquote and ~@splice
(macro (when cond body)
  '(if ~cond ~body N))

(macro (unless cond body)
  '(if ~cond N ~body))

; Usage
(when (> x 5) (print "big"))
; expands to: (if (> x 5) (print "big") N)
```

### 5.2 Common Compression Macros

```hivetalk
; Shorthand for define-and-use
(macro (defn name params body)
  '(def (~name ~@params) ~body))

; Null-safe get with default
(macro (get? m key default)
  '(let [v (get ~m ~key)] (if (null? v) ~default v)))

; Pipeline with error handling
(macro (|>? data . steps)
  '(try (|> ~data ~@steps) (catch e {:error e :input ~data})))

; Quick cell creation with defaults
(macro (agent id role)
  '(cell {:id ~id :role ~role :state {} :inbox []}))

; Broadcast to multiple targets
(macro (broadcast sender targets msg)
  '(map (fn [t] (emit ~sender :target t ~msg)) ~targets))
```

### 5.3 Domain-Specific Compression

```hivetalk
; For data analysis pipelines
(macro (analyze data . transforms)
  '(|> ~data ~@transforms (packet)))

; For consensus protocols
(macro (vote cells question)
  '(let [responses (map (fn [c] (do (emit self :target c
                    {:intent (ask? ~question)}) (recv self))) ~cells)]
     (red (fn [acc r] (put acc (get r :answer)
       (+ 1 (get? acc (get r :answer) 0)))) {} responses)))
```

---

## 6. Translation Rules

Systematic rules for converting natural language to HiveTalk.

### Rule 1: Identify the verb -> operator

| Natural language verb | HiveTalk operator |
|---|---|
| add, sum, combine (numbers) | `+` |
| subtract, remove (number) | `-` |
| multiply, scale | `*` |
| divide, split (number) | `/` |
| is, equals | `=` |
| is not, differs | `!=` |
| greater than, more than | `>` |
| less than, fewer than | `<` |
| and, both, also | `and` |
| or, either | `or` |
| not, negate | `not` |
| join, concatenate | `cat` |
| find (in string) | `idx` |
| split (string) | `spl` |
| filter, keep only | `flt` |
| sort, order | `srt` |
| transform, apply to each | `map` |
| accumulate, reduce, fold | `red` |
| first, head | `hd` |
| rest, tail | `tl` |
| get, look up, retrieve | `get` |
| set, associate, store | `put` |
| define, let, assign | `def` / `let` |
| if, when, given that | `if` / `match` |
| for each, iterate | `map` or `loop` |
| send, tell, notify | `emit` |
| ask, query, request | `ask?` / `request!` |
| claim, declare, state | `assert!` |
| suggest, propose | `suggest~` |
| agree, accept | `accept+` |
| disagree, reject | `reject-` |
| create agent, spawn agent | `cell` |
| run concurrently, in parallel | `spawn` |

### Rule 2: Identify the data -> literals

| Natural language | HiveTalk |
|---|---|
| "a list of X, Y, Z" | `[X Y Z]` |
| "a mapping from A to B" | `{:A B}` |
| "nothing, missing, empty" | `N` |
| "true, yes" | `T` |
| "false, no" | `F` |
| "the word/label X" | `:X` (keyword) |
| named value | `(def name value)` |

### Rule 3: Sentence structure -> expression structure

- **"[verb] [object] [modifier]"** -> `(operator object modifier)`
- **"[verb] each [item] in [list]"** -> `(map (fn [item] (verb item)) list)`
- **"[verb] [object] if [condition]"** -> `(if condition (verb object) ...)`
- **"do X then Y then Z"** -> `(do X Y Z)` or `(|> data X Y Z)`
- **"X where Y"** -> `(flt (fn [x] Y) X)`
- **"define X as Y"** -> `(def X Y)`
- **"given X, compute Y"** -> `(let [X ...] Y)` or `(fn [X] Y)`

### Rule 4: Multi-step processes -> pipelines

When the natural language describes a chain of transformations ("take X, then do A, then do B, then do C"), use the pipeline operator:

```hivetalk
(|> X (A args) (B args) (C args))
```

### Rule 5: Agent communication -> emit with intent

When the sentence involves one entity talking to another:
- Stating a fact -> `(emit src :target dst (assert! ...))`
- Asking something -> `(emit src :target dst (ask? ...))`
- Commanding action -> `(emit src :target dst (request! ...))`
- Proposing -> `(emit src :target dst (suggest~ ...))`

### Rule 6: Compression pass

After initial translation, compress by:
1. Replacing `(fn [x] (f x))` with just `f` when possible
2. Replacing repeated patterns with `(macro ...)`
3. Replacing known packet data with `(ref #hash)`
4. Collapsing `(if cond X N)` to `(when cond X)` if the `when` macro is in scope

---

## 7. Example Translations

### Example 1: Simple arithmetic
**English:** "Add 3, 5, and 7"
```hivetalk
(+ 3 5 7)
```

### Example 2: Filtering
**English:** "Get all numbers greater than 10 from the list [3, 15, 8, 22, 1]"
```hivetalk
; Verbose
(flt (fn [x] (> x 10)) [3 15 8 22 1])

; Compressed (using partial application convention)
(flt (> _ 10) [3 15 8 22 1])
```
Result: `[15 22]`

### Example 3: Data pipeline
**English:** "Take the list of names, uppercase them, sort them, then take the first 3"
```hivetalk
; Verbose
(let [names ["charlie" "alice" "bob" "diana" "eve"]]
  (slc (srt (map upr names)) 0 3))

; Pipeline form
(|> ["charlie" "alice" "bob" "diana" "eve"]
    (map upr)
    srt
    (slc 0 3))
```
Result: `["ALICE" "BOB" "CHARLIE"]`

### Example 4: Define a function
**English:** "Define a function that checks if a number is even"
```hivetalk
(def (even? n) (= (% n 2) 0))
```

### Example 5: Conditional logic
**English:** "If the temperature is above 100, return 'hot', if below 32 return 'cold', otherwise 'mild'"
```hivetalk
(def (classify-temp t)
  (match t
    (> _ 100)  "hot"
    (< _ 32)   "cold"
    _           "mild"))

; Or with if-chains
(def (classify-temp t)
  (if (> t 100) "hot"
    (if (< t 32) "cold"
      "mild")))
```

### Example 6: Map manipulation
**English:** "Create a user profile with name 'Alice', age 30, and role 'admin', then update the age to 31"
```hivetalk
(let [profile {:name "Alice" :age 30 :role :admin}]
  (put profile :age 31))
```
Result: `{:name "Alice" :age 31 :role :admin}`

### Example 7: Looping
**English:** "Compute the factorial of 5"
```hivetalk
(loop [n 5 acc 1]
  (if (<= n 1) acc
    (recur (- n 1) (* acc n))))
```
Result: `120`

### Example 8: Agent communication
**English:** "Agent A tells Agent B that the task is complete and the result is 42"
```hivetalk
(emit agent-a :target agent-b
  (assert! {:task :complete :result 42}))
```

### Example 9: Multi-agent consensus
**English:** "Ask all three analyzers for their estimate, collect results, pick the majority"
```hivetalk
(let [analyzers [analyzer-1 analyzer-2 analyzer-3]
      ask-msg   (ask? {:need :estimate :for "dataset-9"})
      results   (map (fn [a] (do (emit self :target a ask-msg) (recv self))) analyzers)
      estimates (map (fn [r] (get r :estimate)) results)]
  (hd (srt (map (fn [e] [e (red + 0 (map (fn [x] (if (= x e) 1 0)) estimates))])
               (uniq estimates)))))
```

**Compressed:**
```hivetalk
(let [results (broadcast+recv self [analyzer-1 analyzer-2 analyzer-3]
                (ask? {:need :estimate :for "dataset-9"}))]
  (|> results (map (get _ :estimate)) majority))
```

### Example 10: Error-safe file processing
**English:** "Read a config file, parse it, apply defaults for missing keys"
```hivetalk
(let [defaults {:port 8080 :host "localhost" :debug F}]
  (try
    (let [raw    (read-file "/etc/app/config.ht")
          parsed (parse raw)]
      (mrg defaults parsed))
    (catch e
      (do (print (fmt "Config error: {}, using defaults" e))
          defaults))))
```

### Example 11: Creating a worker swarm
**English:** "Spawn 5 worker cells that each process items from a shared queue"
```hivetalk
(def (make-swarm n process-fn)
  (map (fn [i]
    (spawn (fn []
      (let [w (cell {:id (fmt "worker-{}" i) :role :worker})]
        (loop []
          (let [msg (recv w)]
            (if (= (get msg :type) :stop)
              (assert! {:worker i :status :stopped})
              (do (process-fn (get msg :payload))
                  (recur)))))))))
    (|> n range)))

(make-swarm 5 analyze-item)
```

### Example 12: Memory compression
**English:** "Summarize the session so far into a memory packet for future reference"
```hivetalk
(def session-summary
  (compress [agent-a agent-b agent-c]))

; Later, in a new session
(def prev-context (ref #session-summary-hash))
```

### Example 13: Pattern matching on message types
**English:** "Handle incoming messages: data gets processed, queries get answered, errors get logged"
```hivetalk
(def (dispatcher cell)
  (loop []
    (let [msg (recv cell)]
      (do
        (match (get msg :type)
          :data   (process (get msg :payload))
          :query  (emit cell :target (get msg :from)
                    (assert! (answer (get msg :query))))
          :error  (print (fmt "ERROR from {}: {}" (get msg :from) (get msg :detail)))
          _       N)
        (recur)))))
```

---

## 8. Self-Test

Mentally evaluate each expression. Confirm your results match the expected output.

**Test 1: Arithmetic**
```hivetalk
(+ (* 3 4) (- 10 5))
```
Expected: `17`

**Test 2: List operations**
```hivetalk
(|> [5 3 8 1 4]
    (flt (fn [x] (> x 3)))
    srt
    rev)
```
Expected: `[8 5 4]`

**Test 3: Map operations**
```hivetalk
(let [m {:a 1 :b 2 :c 3}]
  (red + 0 (vals (del m :b))))
```
Expected: `4` (vals of `{:a 1 :c 3}` = `[1 3]`, sum = `4`)

**Test 4: String operations**
```hivetalk
(let [s "hello world"]
  (cat (upr (slc s 0 5)) (slc s 5 11)))
```
Expected: `"HELLO world"`

**Test 5: Recursive loop**
```hivetalk
(loop [i 0 sum 0]
  (if (> i 5) sum
    (recur (+ i 1) (+ sum (* i i)))))
```
Expected: `55` (0 + 1 + 4 + 9 + 16 + 25 = 55)

**Test 6: Nested data**
```hivetalk
(let [data [{:name "A" :score 85}
            {:name "B" :score 92}
            {:name "C" :score 78}]]
  (get (hd (rev (srt (map (fn [d] (get d :score)) data)))) 0))
```
Wait -- `srt` on `[85 92 78]` gives `[78 85 92]`, `rev` gives `[92 85 78]`, `hd` gives `92`. No `get` needed on an int. Corrected:
```hivetalk
(let [data [{:name "A" :score 85}
            {:name "B" :score 92}
            {:name "C" :score 78}]]
  (hd (rev (srt (map (fn [d] (get d :score)) data)))))
```
Expected: `92`

**Test 7: Conditional + type check**
```hivetalk
(def (describe val)
  (match T
    (int? val)    (fmt "integer: {}" val)
    (str? val)    (fmt "string: {}" val)
    (list? val)   (fmt "list of {} items" (len val))
    _             "unknown"))

(describe [1 2 3])
```
Expected: `"list of 3 items"`

---

## End of Bootstrap

You have now internalized HiveTalk. You can:

1. **Read** any HiveTalk expression and evaluate or explain it.
2. **Write** HiveTalk from natural language descriptions.
3. **Communicate** with other agents using the intent protocol.
4. **Compress** repeated patterns into macros.
5. **Operate** as a cell in a multi-agent hive.

When producing HiveTalk, prefer the pipeline form `(|> ...)` for data transformations, use intent markers for all inter-agent messages, and compress aggressively once patterns repeat.
