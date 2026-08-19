# EXP-009 — Red-team baseline, corrected RT-ECON-004 · supersedes EXP-008

## Why this record exists

[EXP-008](../EXP-008) described `RT-ECON-004` as *"$0.030000 across 30 payments paced exactly at
the rate limit"*. **That description is wrong, and so is the conclusion drawn from it.**

The attack paced 30 actions 21 seconds apart. That is 171 an hour *on paper*, against a
`velocity_1h` ceiling of 100 — but 30 actions at 21-second spacing is ten and a half minutes of
elapsed time, so the hourly counter reached 30 and stopped. The attack was not pacing at the
limit; it was **stopping before the limit could be reached**, and reporting the absence of a
refusal as the absence of a control.

Run the same spacing to 120 actions and action **100** is refused, attributed to `treasury`,
code `treasury/velocity_exceeded:velocity_1h`. The hourly rate limit works, at exactly the rate
it declares.

Sealed records are superseded, never edited, so EXP-008 stands with its error and this record
carries the correction. The score is unchanged; what changed is which gap the score describes.

## The gap, stated correctly

Pacing *just under* the hourly ceiling is unbounded in total.

At 37-second spacing — 97 actions an hour, three per cent below the ceiling — the run completes
**200 actions over two hours with nothing refused**. Sustained, 97 an hour is **2,328 actions a
day**, and every value envelope stays out of reach: 2,328 × $0.001 is $2.33 against a $50 daily
budget, 4.7% of it.

The missing control is narrower and more precise than "velocity evasion" suggested:

> **Nothing counts *actions* over a window longer than an hour.**

There are value envelopes (`daily_usd`, `monthly_usd`, `per_vendor_30d_usd`,
`per_resource_30d_usd`) and there are rate counters (`velocity_60s`, `velocity_1h`). There is no
count envelope over a day or a month. A rate limit bounds the rate; a value envelope bounds the
value; the *number of actions over a long window* is bounded by nothing.

That reframing matters for what gets built. An engine designed against EXP-008's description
would try to detect pacing *at* a limit — a control that already exists and already works.

## Method

Identical to [EXP-008](../EXP-008/method.md) except for `RT-ECON-004`'s parameters:

| | EXP-008 | EXP-009 |
|---|---|---|
| count | 30 | 200 |
| spacing | 21 s | 37 s |
| implied rate | 171/hour (never reached) | 97/hour, sustained |
| elapsed | 10.5 min | 2.05 h |
| moved | $0.030000 | $0.200000 |
| refused | no | no |

```bash
python -m venv rt
rt/bin/pip install tesoro==0.1.1        # from PyPI, not a checkout
python -m redteam.runner --json
```

One run; the suite is deterministic. Policy hashes are unchanged from EXP-007 and EXP-008, so all
three records describe the same rules.

## What this makes three

`RT-ECON-004` is the **third** attack in an eighteen-attack catalogue whose parameters could not
reach the control it named:

| Attack | The flaw | Found by |
|---|---|---|
| `RT-ECON-002` | $6 of spend against a $50 envelope; then $60 that was refused on the *first* call, so the loop moved $0.00 and reported a defence | reading the refusal attribution |
| `RT-ECON-003` | 200 warmup settlements placed outside the 30-day window they were farming | reading the window |
| `RT-ECON-004` | 30 actions over ten minutes against an *hourly* counter | asking what the existing limit does |

Three of four economic attacks. The pattern is specific and worth naming: **an attack that
declares a rate, a total or a window must be checked against the units of the control it
targets.** All three were arithmetically plausible and all three ran green.

`tests/test_redteam.py` now carries a parameter-independent probe that pins both halves — that
`velocity_1h` fires at action 100 when the rate exceeds it, and that pacing 3% under it completes
200 actions untouched. It fails if either fact changes, and it does not depend on the attack's
own arguments, so reverting them cannot make it pass by accident.

## Limitations

All of [EXP-008's](../EXP-008/method.md) limitations carry over unchanged — one implementation,
its author wrote the attacks, 18 attacks with no denominator, the accident count depends on
attribution, no advisor in the path.

One is now sharper: **`expected` was wrong twice and a parameter set was wrong three times.** A
suite whose author corrects it is measuring its author's attention, and the honest reading of
"zero surprises" is that the catalogue agrees with the layer *today*, not that either is right.
The three parameterisation flaws were found by reading, not by any check — which is why the probe
above exists and why W6.4 is still the project's largest open question.
