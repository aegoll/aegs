# EXP-008 — Red-team baseline, published `tesoro` 0.1.1

## Question

What does the 18-attack adversarial suite score against the **published** package, and is that
score a measurement or an artefact of the suite?

The second half is not padding. A11.9 asks for a sealed score *before* the behavioural-monitoring
and evidence-anchoring engines land, so that "these findings are closed" can later be a
comparison rather than an assertion. A baseline that measures the harness instead of the layer
would make every later comparison meaningless in a way nobody could detect from the numbers.

## Method

```bash
python -m venv rt
rt/bin/pip install tesoro==0.1.1        # from PyPI, not a checkout
python -m redteam.runner --json
```

One run. The suite is deterministic — no model sits in the decision path, every attack gets a
fresh ephemeral store, and the clock is fixed at `2026-08-15T12:00:00Z` — so repetition measures
nothing. That is the opposite of [EXP-007](../EXP-007), where ten runs were necessary because
the quantity was a latency and the spread was 2.4×.

The suite scores the **installed** package rather than `src/`. The prototype's runner put
`../aegl` on `sys.path`; this imports `tesoro` the way a consumer does. Six defects in
F-A12–F-A14 were invisible from the source tree, so where the code comes from is part of the
method.

## Scoring

Every attack declares the control that *should* refuse it. Four outcomes:

| Outcome | Meaning |
|---|---|
| `DEFENDED` | refused, by the control that was supposed to refuse it |
| `DEFENDED_BY_ACCIDENT` | refused, by something else — **a finding, not a pass** |
| `UNDEFENDED` | it worked |
| `ERROR` | the attack did not execute |

`DEFENDED_BY_ACCIDENT` exists because a structuring attack that happens to trip a velocity
counter is not defended: paced differently it succeeds, and the control the attack targets does
not exist. Counting it as a pass is how a system certifies protection it lacks.

Which control refused is read from `Decision.attributed_control` — the package's own projection,
the same one `record._deciding_engine` computes and AEGS-CONF scores. Not re-derived here. See
the findings below for why that sentence is the most important one in this file.

## Environment

`tesoro` 0.1.1 from PyPI, Python 3.13.14, policy packs unmodified: `default`
(`a5a64aeb69dbc5f9206b31022064da26`, 12 rules) and `strict`
(`e9f36e640d040194af74ac9a5d1ebfbe`, 10 rules). Both hashes are **identical to EXP-007's**, so
this score and that latency figure describe the same rules — the red-team result is not
confounded by a policy edit between the two records.

## What porting the suite found, before it produced a number

Three defects in the harness, each of which had made the score wrong in a direction that looked
plausible. Recorded here because a baseline is only as trustworthy as the instrument, and the
instrument was wrong three times in one afternoon.

1. **The runner reimplemented attribution and disagreed with the layer.** `_refusing_source`
   walked `reversed(decision.reasons)` and took the last refusing one. On budget fragmentation
   the daily envelope binds as `treasury/envelope_exceeded:daily`, and a policy rule then
   *observes* the same fact as `policy/rule:review-budget-exhausted`; being later in the list,
   the observation won. The runner said `policy` where `attributed_control` says `treasury`.
   **Two of the three apparent surprises in the first run were this artefact**, not anything
   about the layer. `attributed_control`'s docstring had already named the hazard: a report, a
   conformance run and that property disagreeing about which control refused would be three
   answers to a question with one, and only one of them would be under test. The red-team runner
   had quietly become the fourth.

2. **RT-ECON-002's parameters could not reach the control it names — for the second time.** The
   attack spreads spend across counterparties to test whether the *agent-level* daily envelope
   binds. Its first version used $0.50 × 12 vendors: $6 against a $50 envelope, nowhere near it.
   The fix made it $5.00 × 12 — $60 on paper — which is refused on the **first call**, because
   $1.00 or more to a counterparty with no history is `REVIEW` by
   `review-untrusted-vendor-nontrivial`. The loop broke at `i=0` having moved $0.00 and reported
   a defence. $0.50 is the largest per-call amount an unknown vendor gets approved, so 101 of
   them is the smallest run that can cross $50. The resource now varies per counterparty too:
   with every call against `/market/snapshot`, the per-resource envelope exhausts at the same
   moment as the agent-level one, and two envelopes binding together cannot tell you which saw
   it.

3. **RT-ECON-003's warmup fell outside the window it was farming.** 200 settlements placed 60 to
   52 days before the strike, against a `history_for` aggregation window of 30 days. No trust
   was farmed; the attack tested nothing it described. Corrected to land inside the window —
   which did **not** change the outcome, and knowing the fix changed nothing is worth more than a
   passing run that was never measuring the thing.

Two `expected` values were also stale, inherited from the prototype: journal truncation was
believed defended (it is not, and that is open finding 1), and trust farming was believed open
(it is refused, by the wrong control). A suite that reports known gaps as surprises on every run
buries the surprises that matter, so both were corrected and the surprise count is now zero
**by intent** rather than by luck.

## Limitations

- **One implementation, and its author wrote the attacks.** The same objection as
  [W6.4](../../../PLAN.md): 18 attacks written by the person who wrote the defences measure that
  person's imagination as much as the layer. An independent red team would produce a different
  number and the difference would be the interesting quantity.
- **18 attacks is not a coverage claim.** There is no denominator. Nothing here says what
  fraction of the reachable attack surface these touch, and the four threat classes were chosen
  by the same author.
- **The accident count depends on attribution being correct.** `DEFENDED_BY_ACCIDENT` is
  computed by comparing `attributed_control` against a declared target, so an attribution bug
  moves attacks between `DEFENDED` and `DEFENDED_BY_ACCIDENT` silently. That is exactly what
  finding 1 above did. The mitigation is that attribution now has one implementation rather than
  two, not that it is proven right.
- **No advisor is in the path.** Every run is deterministic-only, so nothing here tests prompt
  injection against the advisor — [A11.2](../../../../tesoro/PLAN.md), still open and named in
  the docs as untested.
- **`expected` is a belief, and beliefs were wrong twice in this record.** Zero surprises means
  the catalogue agrees with the layer today; it does not mean the catalogue is right.
