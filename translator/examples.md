# HiveSpeak Translation Examples

Comprehensive bidirectional translation examples organized by category. Each example shows three forms:

1. **English** -- Natural human language
2. **HiveSpeak (verbose)** -- Fully expanded, no shorthand
3. **HiveSpeak (compressed)** -- Using macros and established shared vocabulary

Where compression macros are used, the macro definition is shown on first use.

---

## 1. Simple Statements / Assertions

### 1.1 Concrete Fact

**English**: The temperature outside is 68 degrees Fahrenheit.

**HiveSpeak (verbose)**:
```
(assert! {:topic :temperature
          :claim 68
          :unit :fahrenheit
          :location :outside})
```

**HiveSpeak (compressed)**:
```
; First, define the compression macro
(macro (fact topic val & kvs)
  '(assert! (mrg {:topic ,topic :claim ,val} ,@kvs)))

(fact :temperature 68 {:unit :fahrenheit :location :outside})
```

### 1.2 Belief with Confidence

**English**: I believe the market will recover by Q3, but I'm only about 60% sure.

**HiveSpeak (verbose)**:
```
(assert! {:topic :market
          :claim {:event :recovery :by :Q3}
          :confidence 0.6})
```

**HiveSpeak (compressed)**:
```
(macro (believe claim conf)
  '(assert! {:claim ,claim :confidence ,conf}))

(believe {:event :market-recovery :by :Q3} 0.6)
```

### 1.3 Negation

**English**: The system is not currently under maintenance.

**HiveSpeak (verbose)**:
```
(assert! {:topic :system
          :claim {:status :maintenance :active F}})
```

**HiveSpeak (compressed)**:
```
(fact :system {:status :maintenance :active F})
```

### 1.4 Multiple Related Facts

**English**: The server is healthy. CPU usage is at 23%. Memory usage is at 61%. There are 4 active connections.

**HiveSpeak (verbose)**:
```
(do
  (assert! {:topic :server :claim {:status :healthy}})
  (assert! {:topic :cpu :claim {:usage 23 :unit :percent}})
  (assert! {:topic :memory :claim {:usage 61 :unit :percent}})
  (assert! {:topic :connections :claim {:active 4}}))
```

**HiveSpeak (compressed)**:
```
(macro (status-report m)
  '(assert! {:topic :system-status :claim ,m}))

(status-report {:server :healthy
                :cpu 23
                :memory 61
                :connections 4})
```

### 1.5 Existential Statement

**English**: There exists a solution to this problem, but it requires more resources than we currently have.

**HiveSpeak (verbose)**:
```
(assert! {:claim {:solution-exists T
                  :constraint {:requires :more-resources
                               :current-sufficiency F}}})
```

**HiveSpeak (compressed)**:
```
(believe {:solution-exists T :blocked-by :insufficient-resources} 0.9)
```

---

## 2. Questions / Queries

### 2.1 Simple Information Query

**English**: What is the current status of the deployment?

**HiveSpeak (verbose)**:
```
(ask? {:about :deployment
       :want :status
       :when :current})
```

**HiveSpeak (compressed)**:
```
(macro (q about want)
  '(ask? {:about ,about :want ,want}))

(q :deployment :status)
```

### 2.2 Yes/No Question

**English**: Has the backup completed?

**HiveSpeak (verbose)**:
```
(ask? {:about :backup
       :want :completion-status
       :expect [:yes :no]})
```

**HiveSpeak (compressed)**:
```
(macro (yn? about)
  '(ask? {:about ,about :want :bool}))

(yn? :backup-complete)
```

### 2.3 Quantitative Question

**English**: How many unresolved tickets are assigned to the infrastructure team?

**HiveSpeak (verbose)**:
```
(ask? {:about :tickets
       :want :count
       :filter {:status :unresolved
                :assigned-to :infrastructure-team}})
```

**HiveSpeak (compressed)**:
```
(macro (count? entity & filters)
  '(ask? {:about ,entity :want :count :filter ,@filters}))

(count? :tickets {:status :unresolved :assigned-to :infrastructure-team})
```

### 2.4 Comparative Question

**English**: Which model performs better on the benchmark, GPT-4 or Claude?

**HiveSpeak (verbose)**:
```
(ask? {:about :model-performance
       :want :comparison
       :context :benchmark
       :candidates ["GPT-4" "Claude"]
       :metric :better})
```

**HiveSpeak (compressed)**:
```
(macro (compare? items on context)
  '(ask? {:about :comparison :candidates ,items :metric ,on :context ,context}))

(compare? ["GPT-4" "Claude"] :performance :benchmark)
```

### 2.5 Conditional Question

**English**: If we double the batch size, will training finish before midnight?

**HiveSpeak (verbose)**:
```
(ask? {:about :training-completion
       :condition {:change {:batch-size (* current-batch-size 2)}}
       :want {:will-finish-before :midnight}})
```

**HiveSpeak (compressed)**:
```
(q :training {:if {:batch-size :doubled} :finish-before :midnight})
```

---

## 3. Commands / Requests

### 3.1 Simple Action

**English**: Delete all temporary files.

**HiveSpeak (verbose)**:
```
(request! {:action :delete
           :target :files
           :filter {:type :temporary}
           :scope :all})
```

**HiveSpeak (compressed)**:
```
(macro (do! action target & opts)
  '(request! (mrg {:action ,action :target ,target} ,@opts)))

(do! :delete :temp-files)
```

### 3.2 Parameterized Action

**English**: Resize the image to 800 by 600 pixels and save it as PNG.

**HiveSpeak (verbose)**:
```
(request! {:action :sequence
           :steps [(request! {:action :resize
                              :target :image
                              :params {:width 800 :height 600 :unit :px}})
                   (request! {:action :save
                              :target :image
                              :params {:format :png}})]})
```

**HiveSpeak (compressed)**:
```
(macro (then & steps)
  '(request! {:action :sequence :steps [,@steps]}))

(then
  (do! :resize :image {:width 800 :height 600})
  (do! :save :image {:format :png}))
```

### 3.3 Conditional Command

**English**: If the disk usage is above 90%, archive old logs and notify the admin.

**HiveSpeak (verbose)**:
```
(if (gt disk-usage 90)
  (do
    (request! {:action :archive :target :old-logs})
    (request! {:action :notify :target :admin :payload {:alert :disk-usage :level :high}}))
  N)
```

**HiveSpeak (compressed)**:
```
(macro (when-above metric threshold & actions)
  '(if (gt ,metric ,threshold) (do ,@actions) N))

(when-above disk-usage 90
  (do! :archive :old-logs)
  (do! :notify :admin {:alert :disk-high}))
```

### 3.4 Delegated Command

**English**: Ask the data team to prepare a summary report and send it to the executive board by end of day.

**HiveSpeak (verbose)**:
```
(emit self :target :data-team
  (request! {:action :prepare
             :output :summary-report
             :deliver-to :executive-board
             :deadline :end-of-day}))
```

**HiveSpeak (compressed)**:
```
(macro (assign team task & opts)
  '(emit self :target ,team (request! (mrg {:action ,task} ,@opts))))

(assign :data-team :prepare {:output :summary-report
                              :deliver-to :executive-board
                              :deadline :eod})
```

---

## 4. Multi-Step Instructions

### 4.1 Data Pipeline

**English**: Load the CSV file, remove rows with missing values, group by region, calculate the average sales per region, and sort by average sales descending.

**HiveSpeak (verbose)**:
```
(|> (read-file "sales.csv")
  parse-csv
  (flt (fn [row] (not (any null? (vals row)))))
  (group-by (fn [row] (get row :region)))
  (map (fn [group]
    {:region (get (hd group) :region)
     :avg-sales (/ (red add 0 (map (fn [r] (get r :sales)) group))
                   (len group))}))
  (srt-by (fn [r] (get r :avg-sales)) :desc))
```

**HiveSpeak (compressed)**:
```
(macro (etl source & steps)
  '(|> (read-file ,source) parse-csv ,@steps))

(macro (clean data)
  '(flt (fn [row] (not (any null? (vals row)))) ,data))

(macro (avg-by group-key val-key data)
  '(|> ,data
     (group-by (fn [r] (get r ,group-key)))
     (map (fn [g] {,group-key (get (hd g) ,group-key)
                   :avg (/ (red add 0 (map (fn [r] (get r ,val-key)) g)) (len g))}))))

(|> (etl "sales.csv") clean (avg-by :region :sales) (srt-by :avg :desc))
```

### 4.2 Build and Deploy

**English**: Pull the latest code, run the test suite, and if all tests pass, build the Docker image, push it to the registry, and deploy to staging. If any test fails, send a Slack notification with the failure details.

**HiveSpeak (verbose)**:
```
(do
  (request! {:action :git-pull :branch :main})
  (def test-result (request! {:action :run-tests}))
  (if (= (get test-result :status) :all-pass)
    (do
      (request! {:action :docker-build :tag :latest})
      (request! {:action :docker-push :registry :default :tag :latest})
      (request! {:action :deploy :target :staging :tag :latest}))
    (request! {:action :notify
               :channel :slack
               :payload {:msg "Tests failed"
                         :details (get test-result :failures)}})))
```

**HiveSpeak (compressed)**:
```
(macro (ci-cd branch on-pass on-fail)
  '(do
     (do! :git-pull {:branch ,branch})
     (def result (do! :run-tests))
     (if (= (get result :status) :all-pass)
       ,on-pass
       (,on-fail result))))

(ci-cd :main
  (then
    (do! :docker-build {:tag :latest})
    (do! :docker-push {:tag :latest})
    (do! :deploy {:target :staging}))
  (fn [r] (do! :slack {:msg "Tests failed" :details (get r :failures)})))
```

### 4.3 Iterative Processing with Accumulation

**English**: For each customer in the database, check their subscription status. If expired, send a renewal reminder. If expiring within 7 days, send a warning. Count the totals of each category and report them.

**HiveSpeak (verbose)**:
```
(do
  (def results
    (red (fn [acc customer]
           (let [status (get customer :sub-status)
                 days-left (get customer :days-remaining)]
             (match status
               :expired (do
                 (emit self :target customer
                   (request! {:action :send-email :template :renewal-reminder}))
                 (put acc :expired (add (get acc :expired) 1)))
               :active (if (<= days-left 7)
                 (do
                   (emit self :target customer
                     (request! {:action :send-email :template :expiry-warning}))
                   (put acc :warning (add (get acc :warning) 1)))
                 (put acc :ok (add (get acc :ok) 1)))
               _ acc)))
         {:expired 0 :warning 0 :ok 0}
         customers))
  (assert! {:topic :subscription-report :claim results}))
```

**HiveSpeak (compressed)**:
```
(macro (tally-by classifier actions items init)
  '(red (fn [acc item]
          (let [cls (,classifier item)]
            ((get ,actions cls (fn [a i] a)) acc item)))
        ,init ,items))

(macro (notify target template)
  '(emit self :target ,target (do! :send-email {:template ,template})))

(def results
  (tally-by
    (fn [c] (match (get c :sub-status)
              :expired :expired
              :active (if (<= (get c :days-remaining) 7) :warning :ok)
              _ :other))
    {:expired  (fn [a c] (do (notify c :renewal) (put a :expired (add (get a :expired) 1))))
     :warning  (fn [a c] (do (notify c :expiry-warn) (put a :warning (add (get a :warning) 1))))
     :ok       (fn [a c] (put a :ok (add (get a :ok) 1)))}
    customers
    {:expired 0 :warning 0 :ok 0}))

(fact :subscription-report results)
```

---

## 5. Code / Programming Tasks

### 5.1 Fibonacci Sequence

**English**: Write a function that returns the Nth Fibonacci number.

**HiveSpeak (verbose)**:
```
(def (fibonacci n)
  (loop [i 0 a 0 b 1]
    (if (= i n)
      a
      (recur (add i 1) b (add a b)))))
```

**HiveSpeak (compressed)**:
```
(def (fib n)
  (loop [i 0 a 0 b 1]
    (if (= i n) a (recur (add i 1) b (add a b)))))
```

### 5.2 FizzBuzz

**English**: Write FizzBuzz for numbers 1 to 100. Print "Fizz" for multiples of 3, "Buzz" for multiples of 5, "FizzBuzz" for both, and the number otherwise.

**HiveSpeak (verbose)**:
```
(def (fizzbuzz n)
  (map (fn [i]
    (match [(= (% i 3) 0) (= (% i 5) 0)]
      [T T] "FizzBuzz"
      [T F] "Fizz"
      [F T] "Buzz"
      _     i))
    (range 1 (add n 1))))

(fizzbuzz 100)
```

**HiveSpeak (compressed)**:
```
(def (fb n)
  (map (fn [i]
    (match [(= (% i 3) 0) (= (% i 5) 0)]
      [T T] "FizzBuzz" [T F] "Fizz" [F T] "Buzz" _ i))
    (range 1 (add n 1))))
```

### 5.3 Binary Search

**English**: Write a binary search function that returns the index of a target value in a sorted list, or null if not found.

**HiveSpeak (verbose)**:
```
(def (binary-search lst target)
  (loop [lo 0 hi (sub (len lst) 1)]
    (if (gt lo hi)
      N
      (let [mid (/ (add lo hi) 2)
            val (nth lst mid)]
        (match (compare val target)
          0  mid
          -1 (recur (add mid 1) hi)
          1  (recur lo (sub mid 1)))))))
```

**HiveSpeak (compressed)**:
```
(def (bsearch lst t)
  (loop [lo 0 hi (sub (len lst) 1)]
    (if (gt lo hi) N
      (let [m (/ (add lo hi) 2) v (nth lst m)]
        (match (compare v t) 0 m -1 (recur (add m 1) hi) 1 (recur lo (sub m 1)))))))
```

### 5.4 Map Inversion

**English**: Write a function that inverts a map, swapping keys and values. If multiple keys share a value, collect them into a list.

**HiveSpeak (verbose)**:
```
(def (invert-map m)
  (red (fn [acc key]
    (let [val (get m key)
          existing (get acc val [])]
      (put acc val (push existing key))))
    {}
    (keys m)))
```

**HiveSpeak (compressed)**:
```
(def (inv m)
  (red (fn [a k] (let [v (get m k)] (put a v (push (get a v []) k)))) {} (keys m)))
```

---

## 6. Reasoning / Analysis

### 6.1 Cause-Effect Chain

**English**: The database is slow because the query isn't indexed. The unindexed query causes full table scans. Full table scans increase I/O load. Increased I/O load degrades response time for all services.

**HiveSpeak (verbose)**:
```
(assert! {:topic :diagnosis
          :chain [{:cause :unindexed-query :effect :full-table-scan}
                  {:cause :full-table-scan :effect :high-io-load}
                  {:cause :high-io-load :effect :degraded-response-time}]
          :root-cause :unindexed-query
          :symptom :slow-database})
```

**HiveSpeak (compressed)**:
```
(macro (causal-chain root symptom & links)
  '(assert! {:topic :diagnosis
             :root-cause ,root
             :symptom ,symptom
             :chain ,links}))

(causal-chain :unindexed-query :slow-database
  [:unindexed-query :full-table-scan]
  [:full-table-scan :high-io-load]
  [:high-io-load :degraded-response-time])
```

### 6.2 Trade-Off Analysis

**English**: Option A is faster but costs more. Option B is cheaper but takes twice as long. Option C is balanced but requires hiring a contractor. I recommend Option B given our budget constraints.

**HiveSpeak (verbose)**:
```
(do
  (assert! {:topic :options
            :analysis [{:id :A :pros [:fast] :cons [:expensive]}
                       {:id :B :pros [:cheap] :cons [:slow]}
                       {:id :C :pros [:balanced] :cons [:requires-contractor]}]})
  (suggest~ {:recommendation :B
             :reason :budget-constraints
             :confidence 0.8}))
```

**HiveSpeak (compressed)**:
```
(macro (tradeoff options rec reason)
  '(do
     (assert! {:topic :options :analysis ,options})
     (suggest~ {:recommendation ,rec :reason ,reason})))

(tradeoff
  [{:id :A :+ [:fast] :- [:expensive]}
   {:id :B :+ [:cheap] :- [:slow]}
   {:id :C :+ [:balanced] :- [:needs-contractor]}]
  :B :budget-constraints)
```

### 6.3 Hypothesis Testing

**English**: Hypothesis: the memory leak is in the image processing module. Evidence for: memory spikes correlate with image uploads. Evidence against: the module was stable for 6 months before this. Conclusion: likely but not certain; needs profiling.

**HiveSpeak (verbose)**:
```
(assert! {:topic :hypothesis
          :claim {:leak-location :image-processing-module}
          :evidence-for [{:observation "memory spikes correlate with image uploads"}]
          :evidence-against [{:observation "module was stable for 6 months prior"}]
          :conclusion :likely-needs-profiling
          :confidence 0.65})
```

**HiveSpeak (compressed)**:
```
(macro (hypothesis claim pro con verdict conf)
  '(assert! {:topic :hypothesis
             :claim ,claim
             :evidence-for ,pro
             :evidence-against ,con
             :conclusion ,verdict
             :confidence ,conf}))

(hypothesis
  {:leak-in :image-processing}
  ["memory spikes correlate with uploads"]
  ["stable for 6 months prior"]
  :likely-needs-profiling
  0.65)
```

---

## 7. Planning / Negotiation

### 7.1 Proposal

**English**: I propose we migrate to PostgreSQL over three sprints. Sprint 1: schema design and test data migration. Sprint 2: application layer changes. Sprint 3: production cutover with rollback plan.

**HiveSpeak (verbose)**:
```
(suggest~ {:topic :migration
           :target :postgresql
           :plan [{:sprint 1 :scope [:schema-design :test-migration]}
                  {:sprint 2 :scope [:app-layer-changes]}
                  {:sprint 3 :scope [:production-cutover :rollback-plan]}]})
```

**HiveSpeak (compressed)**:
```
(macro (propose topic plan)
  '(suggest~ {:topic ,topic :plan ,plan}))

(propose :pg-migration
  [{:s 1 :do [:schema :test-migrate]}
   {:s 2 :do [:app-changes]}
   {:s 3 :do [:cutover :rollback]}])
```

### 7.2 Counter-Proposal

**English**: I like the migration idea but think we need a Sprint 0 for risk assessment, and Sprint 3 should include a two-week parallel-run period.

**HiveSpeak (verbose)**:
```
(do
  (accept+ {:ref #migration-proposal :scope :partial})
  (suggest~ {:amend {:prepend {:sprint 0 :scope [:risk-assessment]}}
             :modify {:sprint 3 :add [:parallel-run-2-weeks]}
             :ref #migration-proposal}))
```

**HiveSpeak (compressed)**:
```
(macro (counter-propose ref accepts amends)
  '(do (accept+ {:ref ,ref :scope :partial})
       (suggest~ {:amend ,amends :ref ,ref})))

(counter-propose #migration-proposal
  :plan-concept
  {:prepend {:s 0 :do [:risk-assessment]}
   :modify {:s 3 :add [:parallel-run-2w]}})
```

### 7.3 Consensus Building

**English**: Three of four team members agree on the deadline. The fourth wants an extension. I suggest we compromise: keep the deadline but reduce the feature scope to the MVP.

**HiveSpeak (verbose)**:
```
(do
  (assert! {:topic :consensus-status
            :agree 3
            :disagree 1
            :point-of-contention :deadline})
  (suggest~ {:compromise {:keep :deadline
                          :reduce :feature-scope
                          :to :mvp}
             :goal :full-consensus}))
```

**HiveSpeak (compressed)**:
```
(macro (mediate status compromise)
  '(do (assert! {:topic :consensus :status ,status})
       (suggest~ {:compromise ,compromise})))

(mediate
  {:agree 3 :disagree 1 :on :deadline}
  {:keep :deadline :reduce-to :mvp})
```

### 7.4 Rejection with Alternative

**English**: No, we cannot use that library -- it has a GPL license and we need MIT-compatible dependencies. Use this other library instead.

**HiveSpeak (verbose)**:
```
(do
  (reject- {:ref #library-choice
            :reason {:license :GPL :required :MIT-compatible}})
  (suggest~ {:alternative :other-library
             :reason :license-compatible}))
```

**HiveSpeak (compressed)**:
```
(macro (reject-suggest ref reason alt)
  '(do (reject- {:ref ,ref :reason ,reason})
       (suggest~ {:alternative ,alt})))

(reject-suggest #lib-choice :gpl-incompatible :other-library)
```

---

## 8. Meta-Communication

### 8.1 Clarification Request

**English**: I don't understand what you meant by "normalize the embeddings". Can you explain in more detail?

**HiveSpeak (verbose)**:
```
(ask? {:about #prev-message
       :want :clarification
       :specifically "normalize the embeddings"
       :desired-detail :high})
```

**HiveSpeak (compressed)**:
```
(macro (clarify? ref what)
  '(ask? {:about ,ref :want :clarification :specifically ,what}))

(clarify? #prev "normalize the embeddings")
```

### 8.2 Defining Shared Vocabulary

**English**: Let's agree on some terminology: "deploy" always means push to production, "stage" means push to the staging environment, and "ship" means deploy plus notify stakeholders.

**HiveSpeak (verbose)**:
```
(do
  (suggest~ {:type :vocabulary-definition
             :definitions [{:term "deploy" :means (request! {:action :push :target :production})}
                           {:term "stage" :means (request! {:action :push :target :staging})}
                           {:term "ship" :means (do
                                                  (request! {:action :push :target :production})
                                                  (request! {:action :notify :target :stakeholders}))}]})
  (ask? {:want :acceptance :about :vocabulary-definition}))
```

**HiveSpeak (compressed)**:
```
(do
  (macro (deploy!) '(do! :push :production))
  (macro (stage!)  '(do! :push :staging))
  (macro (ship!)   '(do (deploy!) (do! :notify :stakeholders)))
  (suggest~ {:type :vocab :terms [:deploy! :stage! :ship!]}))
```

### 8.3 Process Reflection

**English**: We've been going back and forth on this for three rounds. Let me summarize where we agree and where we still disagree, so we can focus.

**HiveSpeak (verbose)**:
```
(do
  (assert! {:topic :process-meta
            :observation {:rounds 3 :status :oscillating}})
  (request! {:action :summarize
             :scope :current-negotiation
             :partition [:agreed :disputed]
             :purpose :focus}))
```

**HiveSpeak (compressed)**:
```
(macro (checkpoint! rounds)
  '(do
     (assert! {:meta :process :rounds ,rounds :status :oscillating})
     (do! :summarize {:scope :negotiation :split [:agreed :disputed]})))

(checkpoint! 3)
```

### 8.4 Error Correction

**English**: I made a mistake in my previous message. The threshold should be 0.95, not 0.85. Please disregard the old value.

**HiveSpeak (verbose)**:
```
(do
  (reject- {:ref #prev-self
            :scope {:field :threshold :old-value 0.85}
            :reason :error})
  (assert! {:topic :correction
            :field :threshold
            :value 0.95
            :supersedes #prev-self}))
```

**HiveSpeak (compressed)**:
```
(macro (correct! ref field old new)
  '(do
     (reject- {:ref ,ref :scope ,field :reason :self-correction})
     (assert! {:correction ,field :value ,new :supersedes ,ref})))

(correct! #prev :threshold 0.85 0.95)
```

### 8.5 Conversation Steering

**English**: Let's table the API discussion for now and focus on the database schema. We can come back to the API once the schema is finalized.

**HiveSpeak (verbose)**:
```
(do
  (suggest~ {:action :defer
             :topic :api-discussion
             :resume-condition {:when :schema-finalized}})
  (request! {:action :focus
             :topic :database-schema
             :priority :immediate}))
```

**HiveSpeak (compressed)**:
```
(macro (pivot! from to resume-when)
  '(do
     (suggest~ {:defer ,from :resume-when ,resume-when})
     (do! :focus {:topic ,to :priority :now})))

(pivot! :api-discussion :database-schema :schema-finalized)
```

---

## 9. Compressed Forms -- Progressive Compression Showcase

This section demonstrates how the same message compresses across stages of shared vocabulary development.

### 9.1 Code Review Request

**Stage 0 -- Full English**:
> Please review my pull request. Look for bugs, security issues, and style problems. Give me a summary with severity ratings and specific line references.

**Stage 1 -- Verbose HiveSpeak**:
```
(emit self :target :reviewer
  (request! {:action :review
             :target :pull-request
             :scope [:bugs :security :style]
             :output {:format :summary
                      :include [:severity :line-refs]}}))
```

**Stage 2 -- First compression (define a review macro)**:
```
(macro (review! target scope output)
  '(emit self :target :reviewer
     (request! {:action :review :target ,target :scope ,scope :output ,output})))

(review! :pull-request [:bugs :security :style] {:format :summary :include [:severity :line-refs]})
```

**Stage 3 -- Second compression (default scope and output)**:
```
(macro (pr-review!)
  '(review! :pull-request [:bugs :security :style] {:format :summary :include [:severity :line-refs]}))

(pr-review!)
```

**Stage 4 -- Packet reference (reified as shared vocabulary)**:
```
; The macro itself becomes a memory packet
(def pr-review! (ref #pr-review-standard))

(pr-review!)
```

**Compression ratio**: 37 English words -> 1 HiveSpeak expression (after Stage 4).

### 9.2 Deployment Pipeline

**Stage 0 -- Full English**:
> Run the linter, then run unit tests, then run integration tests. If everything passes, build the Docker image tagged with the current git hash, push to our ECR registry, and deploy to the staging environment. Send a Slack message to the #releases channel when done.

**Stage 1 -- Verbose HiveSpeak**:
```
(do
  (def lint-ok (request! {:action :lint}))
  (def unit-ok (request! {:action :test :type :unit}))
  (def int-ok (request! {:action :test :type :integration}))
  (if (and (get lint-ok :pass) (get unit-ok :pass) (get int-ok :pass))
    (do
      (def tag (request! {:action :git-hash}))
      (request! {:action :docker-build :tag tag})
      (request! {:action :docker-push :registry :ecr :tag tag})
      (request! {:action :deploy :target :staging :tag tag})
      (request! {:action :notify :channel "#releases" :via :slack :msg "deployed"}))
    (request! {:action :notify :channel "#releases" :via :slack :msg "pipeline failed"})))
```

**Stage 2 -- Macro compression**:
```
(macro (pipeline checks on-pass on-fail)
  '(let [results (map (fn [c] (request! c)) ,checks)]
     (if (all (fn [r] (get r :pass)) results)
       ,on-pass
       ,on-fail)))

(macro (docker-ship! tag registry env)
  '(do (do! :docker-build {:tag ,tag})
       (do! :docker-push {:registry ,registry :tag ,tag})
       (do! :deploy {:target ,env :tag ,tag})))

(macro (slack! channel msg)
  '(do! :notify {:channel ,channel :via :slack :msg ,msg}))

(pipeline
  [{:action :lint} {:action :test :type :unit} {:action :test :type :integration}]
  (let [tag (do! :git-hash)]
    (do (docker-ship! tag :ecr :staging) (slack! "#releases" "deployed")))
  (slack! "#releases" "pipeline failed"))
```

**Stage 3 -- Domain-specific single command**:
```
(macro (ship-staging!)
  '(pipeline
     [{:action :lint} {:action :test :type :unit} {:action :test :type :integration}]
     (let [tag (do! :git-hash)]
       (do (docker-ship! tag :ecr :staging) (slack! "#releases" "deployed")))
     (slack! "#releases" "pipeline failed")))

(ship-staging!)
```

**Compression ratio**: 52 English words -> 1 HiveSpeak expression (after Stage 3).

### 9.3 Meeting Summary

**Stage 0 -- Full English**:
> Summarize today's meeting. We discussed three topics: the migration timeline (decided to extend by one week), the new hire onboarding process (still needs work, assigned to Sarah), and Q3 budget allocation (approved with the modification that marketing gets 5% more). Create a memory packet of these decisions and share it with all attendees.

**Stage 1 -- Verbose HiveSpeak**:
```
(do
  (def decisions
    (packet {:type :meeting-summary
             :date :today
             :topics [{:topic :migration-timeline
                       :decision :extend-one-week
                       :status :decided}
                      {:topic :onboarding-process
                       :decision :needs-work
                       :assigned-to "Sarah"
                       :status :in-progress}
                      {:topic :q3-budget
                       :decision :approved
                       :modification {:marketing :+5-percent}
                       :status :decided}]}))
  (map (fn [attendee]
    (emit self :target attendee (assert! {:ref decisions})))
    attendees))
```

**Stage 2 -- Macro compression**:
```
(macro (minutes & topics)
  '(do
     (def pkt (packet {:type :meeting-summary :date :today :topics [,@topics]}))
     (map (fn [a] (emit self :target a (assert! {:ref pkt}))) attendees)))

(macro (decided topic what)
  '{:topic ,topic :decision ,what :status :decided})

(macro (wip topic what assignee)
  '{:topic ,topic :decision ,what :assigned-to ,assignee :status :in-progress})

(minutes
  (decided :migration-timeline :extend-one-week)
  (wip :onboarding :needs-work "Sarah")
  (decided :q3-budget {:approved T :mod {:marketing :+5pct}}))
```

**Stage 3 -- Maximum compression**:
```
(minutes
  (d :migration :+1w)
  (w :onboard :wip "Sarah")
  (d :q3-budget {:ok T :marketing :+5p}))
```

**Compression ratio**: 63 English words -> 4 lines of HiveSpeak (after Stage 3).

---

## Appendix: Macro Library

A collection of commonly useful macros referenced throughout this document.

```
; --- Communication Shorthand ---
(macro (fact topic val & kvs)
  '(assert! (mrg {:topic ,topic :claim ,val} ,@kvs)))

(macro (q about want)
  '(ask? {:about ,about :want ,want}))

(macro (yn? about)
  '(ask? {:about ,about :want :bool}))

(macro (do! action target & opts)
  '(request! (mrg {:action ,action :target ,target} ,@opts)))

(macro (believe claim conf)
  '(assert! {:claim ,claim :confidence ,conf}))

; --- Workflow ---
(macro (then & steps)
  '(request! {:action :sequence :steps [,@steps]}))

(macro (assign team task & opts)
  '(emit self :target ,team (request! (mrg {:action ,task} ,@opts))))

(macro (when-above metric threshold & actions)
  '(if (gt ,metric ,threshold) (do ,@actions) N))

; --- Negotiation ---
(macro (propose topic plan)
  '(suggest~ {:topic ,topic :plan ,plan}))

(macro (counter-propose ref accepts amends)
  '(do (accept+ {:ref ,ref :scope :partial}) (suggest~ {:amend ,amends :ref ,ref})))

(macro (reject-suggest ref reason alt)
  '(do (reject- {:ref ,ref :reason ,reason}) (suggest~ {:alternative ,alt})))

; --- Meta ---
(macro (clarify? ref what)
  '(ask? {:about ,ref :want :clarification :specifically ,what}))

(macro (correct! ref field old new)
  '(do (reject- {:ref ,ref :scope ,field :reason :self-correction})
       (assert! {:correction ,field :value ,new :supersedes ,ref})))

(macro (pivot! from to resume-when)
  '(do (suggest~ {:defer ,from :resume-when ,resume-when})
       (do! :focus {:topic ,to :priority :now})))

(macro (checkpoint! rounds)
  '(do (assert! {:meta :process :rounds ,rounds :status :oscillating})
       (do! :summarize {:scope :negotiation :split [:agreed :disputed]})))
```
