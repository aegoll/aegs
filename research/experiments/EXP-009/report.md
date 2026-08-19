# EXP-009 — Results

**14 defended · 1 defended by accident · 3 undefended · 0 error** — unchanged from
[EXP-008](../EXP-008). The number is the same; one of the three undefended results now describes
a different, narrower gap.

## What changed

| Attack | EXP-008 said | EXP-009 says |
|---|---|---|
| `RT-ECON-004` | "$0.030000 across 30 payments paced exactly at the rate limit"; conclusion: a rate limit bounds the rate, not the total | $0.200000 across **200** payments over **two hours** at 97/hour — 3% under the `velocity_1h` ceiling of 100. The rate limit **works**: at 171/hour, action 100 is refused by `treasury/velocity_exceeded:velocity_1h`. The gap is that **no envelope counts actions over a window longer than an hour** |

Nothing else moved. `RT-ECON-001` (structuring) and `RT-EVID-002` (truncation) are unchanged,
`RT-ECON-003` remains `DEFENDED_BY_ACCIDENT`, and the fourteen defended attacks are the same
fourteen.

## The three undefended, restated

| Attack | What moved, with nothing refused | The control that does not exist |
|---|---|---|
| **RT-ECON-001** structuring | $0.040000 across 40 payments, one every five minutes (3.3 h) | 12 actions/hour never approaches `velocity_1h`; $0.04 is 0.08% of the daily budget. To reach $50 at $0.001 takes 50,000 actions — 173 days at this pacing. Both envelope families are structurally out of reach |
| **RT-ECON-004** paced evasion | $0.200000 across 200 payments over 2.05 h at 97/hour | Sustained, 2,328 actions/day for $2.33 — 4.7% of the daily budget. Bounded by no count envelope over any window longer than an hour |
| **RT-EVID-002** journal truncation | last two entries deleted; `verify()` reports the chain as holding | Any prefix of a hash chain is a valid hash chain. Editing and middle-deletion are both caught, which is what makes this easy to miss |

## The two economic findings share one cause

Worth stating plainly, because it changes what has to be built.

Structuring and paced evasion look like different attacks — one is about *amount*, one about
*rate* — and both survive for the same reason: **the layer bounds value and it bounds rate, and
it never bounds count over a long window.**

- Value envelopes are unreachable when each action is trivial.
- Rate counters are unreachable when the pacing sits under them.
- Nothing multiplies "trivial" by "many" and compares the product to anything.

Neither is a threshold that was set too loosely. Lowering `daily_usd` does not help — $0.04 is
not near $50 at any setting an agent could work under. Lowering `velocity_1h` does not help —
the attacker paces under whatever it is. Both are *structural*: the quantity the attack grows is
one no control reads.

That is why A11.3 asks for a design doc before an engine. It also means the first candidate is
not a behavioural heuristic at all but **count envelopes** — the existing envelope idea applied
to a quantity it currently ignores — which stays deterministic, attributable, and free of any
attempt to infer intent.

## For the after-comparison

When the control lands, the movement this record predicts:

- `RT-ECON-001` and `RT-ECON-004`: `UNDEFENDED` → `DEFENDED`, and **both attributed to the same
  new control**. If they are attributed to `treasury` via an existing envelope, a threshold was
  tightened rather than a control added, and the attacks should be re-parameterised until they
  are out of reach again — that is what "structural" means.
- `RT-ECON-003`: `DEFENDED_BY_ACCIDENT` → `DEFENDED` only if `risk` refuses. Still
  `review-negative-roi` means the finding stands whatever was added.
- `RT-EVID-002`: unaffected by any economic control; it waits on A11.6 and an external anchor.
  A11.7 remains binding — a `head.json` beside the journal is not a fix.

The prediction that the two economic attacks must share an attribution is the useful one. Two
findings with one cause should close with one control, and if they close with two, one of them
was misdiagnosed.
