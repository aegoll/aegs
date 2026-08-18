# EXP-007 — Deterministic governance overhead, published `aegoll` 0.1.1

## Question

Does the governance overhead measured before the restructure still hold for the **published**
package? EXP-003 and EXP-005 both measured a source checkout of the pre-port `aegl` module. The
packaging changed the import graph, the `Governor` facade was added, and two version lines'
worth of fixes landed in between — so the earlier figures describe code that is no longer what a
user installs.

## Method

```bash
python -m venv fresh
fresh/bin/pip install aegoll==0.1.1        # from PyPI, not a checkout
aegoll init
for i in $(seq 10); do aegoll bench -n 3000 --json; done
```

Ten runs of 3,000 decisions each. `aegoll bench` drives `decide()` — the full deterministic
path — and reports the per-decision latency the layer measured itself, plus the model
invocation count and inference cost.

The starter policy pack, unmodified: `default`, content hash `a5a64aeb69dbc5f9206b31022064da26`,
12 rules.

## Why ten runs

EXP-003 reported one run. EXP-005 reported five and was right to, because five showed something
one could not: the figure moves. Ten was chosen after an earlier five-run batch on this machine
produced a p50 of 254 µs while a batch minutes earlier produced 120 µs — a 2× difference from
nothing but machine load.

That is the actual reason for the run count, and it is worth stating rather than presenting ten
as a round number somebody picked.

## What this cannot show

**It is one machine.** A Windows 11 laptop, shared with other work while measuring. Nothing here
speaks to server-class hardware, Linux, or a container under a CPU quota.

**The spread is wide, and the spread is the point.** p50 across ten identical runs: 139, 147,
154, 166, 167, 169, 176, 204, 281, 330 µs. A 2.4× range. Any single figure drawn from this
measurement — including the median — is a sample from that range, and quoting one as *the*
overhead would be exactly the over-precision this record exists to prevent.

**It is not comparable to EXP-005 the way a before-and-after chart would suggest.** Different
code, different package, different machine load, and EXP-005's five runs had their own spread
(267–343 µs) that overlaps this one's upper half. See `report.md`.

**Nothing was consulted and nothing settled.** Zero model invocations, zero inference cost, no
network, no chain. This is the decision path alone, which is the only thing the claim is about.
