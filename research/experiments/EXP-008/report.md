# EXP-008 — Results

**14 defended · 1 defended by accident · 3 undefended · 0 error**, out of 18 attacks against
`tesoro` 0.1.1 installed from PyPI. Zero results contradict their stated expectation.

## The score

| Class | Attacks | Defended | By accident | Undefended |
|---|---|---|---|---|
| numeric | 5 | 5 | — | — |
| economic | 4 | 1 | 1 | 2 |
| evidence | 4 | 3 | — | 1 |
| authority | 5 | 5 | — | — |
| **total** | **18** | **14** | **1** | **3** |

Every attack executed. `ERROR` is zero, and that is checked rather than observed: a suite of
errors reads as a clean run to anyone looking only at a failure count, which is how 28 AEGS
vectors once counted toward coverage while executing nothing.

## The three undefended

These are the **same three** the README, the CHANGELOG, the docs site and the specification's
security section already name. A test asserts the sets match, because if the suite and those
documents diverge, one of them is lying and the suite is the one entitled to be right.

| Attack | What moved | Why no control sees it |
|---|---|---|
| **RT-ECON-001** microtransaction structuring | $0.040000 across 40 payments, one every five minutes | 0.08% of the daily envelope. No value limit is approached and no rate limit fires. Catching it needs a control that reads the *shape* of a sequence, and no envelope does |
| **RT-ECON-004** velocity evasion | $0.030000 across 30 payments paced exactly at the rate limit | A rate limit bounds the rate, not the total. Ten per minute permits fourteen thousand a day, and nothing sums them |
| **RT-EVID-002** journal truncation | last two entries deleted; `verify()` reports the chain as holding | Any prefix of a hash chain is itself a valid hash chain. An agent that gets refused can delete the refusal. Editing and middle-deletion are both caught — which is what makes this easy to miss: two of three tamper modes pass |

W7.3 closes the first two; W7.4 closes the third. **A11.7 is the constraint on that third:** a
`head.json` written beside the journal is not a fix. An attacker who can truncate the file can
rewrite the file next to it, and the result would look like a defence while being none. The fix
is an external anchor.

## The one accident

**RT-ECON-003, trust farming.** 200 settled $0.001 purchases inside the 30-day window, then a
$12.00 strike. The strike is refused — so this is not a hole — but it is refused by
`policy/rule:review-negative-roi`, which finds a $12 data purchase not worth its price. The
`risk` control the attack names never acts.

Shaped as a purchase the ROI rule likes, nothing in this run would examine the farmed history at
all. That is precisely the situation `DEFENDED_BY_ACCIDENT` exists to name, and precisely why it
is reported as a finding rather than folded into the pass count: the refusal is real, the
*defence* is not, and a score that said 15/18 defended would be a claim about a control that did
nothing.

Writing that sharper strike is W7 work. Claiming this attack covers `risk` would be the fiction.

## What is genuinely defended

Worth stating, because a report that lists only gaps invites the reading that nothing works.

All five **numeric** attacks: a negative amount is rejected at the boundary before any engine
weighs it — the `-$1000` payment that was once *approved*, because every `amount ≤ headroom`
comparison is satisfied by a negative; a 30-digit amount is refused as too large; $0.0000001
rounds to 0 atomic units, **down**, which does not favour the spender; a zero-value request is
handled without poisoning the baseline; and an internal-channel action against a USDC-denominated
intent is refused by `intent` rather than silently converted.

All five **authority** attacks: a sub-agent claiming $100.00 under a parent capped at $0.01 is
clamped, not compared — the escalation that was live in this codebase, where declaring *no* limit
was strictly more permissive than declaring a large one; a revoked identity cannot transact; an
intent that expired an hour ago cannot be reused; agent B is not evaluated against agent A's
intent; and a $0.000001 payment to a sanctioned counterparty is barred, because an amount that
can soften an absolute bar means it was never a bar.

Three of four **evidence** attacks: an edited entry fails on a content-hash mismatch, a
middle-deletion fails on sequence order, and a settled row cannot be overwritten by replaying its
request id.

And the one economic defence that now means something: **RT-ECON-002**, budget fragmentation,
stops at exactly $50.00 of the $50.00 daily envelope after 100 approved payments to 100 distinct
counterparties on 100 distinct resources, attributed to `treasury`. The agent-level envelope
binds. Two earlier versions of that attack could not reach it — see `method.md`.

## For the comparison this record exists to enable

When W7.3 and W7.4 land, the expected movement is:

- `RT-ECON-001` and `RT-ECON-004`: `UNDEFENDED` → `DEFENDED`, attributed to the behavioural
  engine and **not** to `treasury`, because an envelope catching them would mean the parameters
  drifted rather than the control arrived.
- `RT-EVID-002`: `UNDEFENDED` → `DEFENDED`, and the detail must name the external anchor.
- `RT-ECON-003`: `DEFENDED_BY_ACCIDENT` → `DEFENDED` only if `risk` is what refuses. If it is
  still `review-negative-roi`, the finding stands regardless of what any engine was added.

Each of those is a line in `redteam/baseline.json`, and the test fails until the file is
regenerated in the same commit — so closing a finding forces the documents that describe it as
open to be revisited, rather than leaving four of them stale in the direction of overclaiming.
