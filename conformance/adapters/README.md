# Writing an adapter

You have a governance layer. You want AEGS-CONF to score it. This is everything you need, and it
assumes no knowledge of this codebase.

**You do not fork the suite and you do not add a file to it.** An adapter lives in *your* package,
where your imports resolve, and you point the suite at it:

```bash
pip install aegs-conformance
aegs-conformance --against my_layer.conformance:MyAdapter
```

That matters more than it looks. A conformance suite that can only score adapters listed inside
itself is a self-assessment: everyone else has to fork it, and a forked instrument produces
numbers nobody can compare.

## The interface

Two attributes. That is the whole contract.

```python
class MyAdapter:
    name = "my-layer"                       # appears in the report

    def run_case(self, case) -> dict | None:
        """Ask your layer to decide, and return an AEGS Decision Record.

        Return None for a case your layer does not implement. That scores as
        NOT_IMPLEMENTED, which is reported separately from a failure -- an honest
        "I do not do this" is not a wrong answer.
        """
```

Nothing to subclass, nothing to register, no import from this package required. Duck typing, so
your adapter has no dependency on the suite at all — which means it cannot break when the suite
changes, and you can keep it in your own test tree.

Two optional module-level hooks, both worth adding:

```python
def implementation_available() -> bool:
    """False if your layer is not installed in this environment."""

NOT_INSTALLED = "my_layer is not installed; pip install my-layer"
```

Without these, an uninstalled layer produces a plausible-looking `0/7 passed, AEGS-1 claimable:
no` report — a document somebody could publish in good faith that says something false about a
system nobody ran. With them the suite refuses to score and exits 3.

## What `case` gives you

```python
case.id        # "CONF-004"
case.title     # "Sanctioned counterparty"
case.level     # "AEGS-1" | "AEGS-2"
case.control   # the control this case is about
case.setup     # state to establish first: identities, intents, prior spend
case.action    # the action to decide on: channel, resource, amount, asset, counterparty
case.expect    # what a conformant layer must answer (the suite checks this, not you)
```

Cases are **JSON files** in [`../cases/`](../cases/). Read them; they are short, and each carries a
`rationale` explaining why the case exists at all. Adding a case requires no Python.

## What you must return

An AEGS Decision Record. The schema is
[`decision-record-0.1.json`](https://aegoll.github.io/aegs/schemas/decision-record-0.1.json), and
the suite **validates before scoring** — a conformant verdict inside a malformed record is
`INVALID_RECORD`, not a pass.

The minimum that validates:

```python
{
  "aegsVersion": "0.1",
  "decisionId": "d-1",
  "agentId": "my-agent",
  "intentId": None,                     # null is fine; the key must be present
  "action": {
    "channel": "external",
    "resource": "/market/snapshot",
    "amount": "0.001000",               # a STRING. See below.
    "asset": "USDC"
  },
  "decision": "APPROVE",                # APPROVE | REVIEW | ESCALATE | REJECT
  "authorization": {
    "decidingEngine": "treasury",       # WHICH CONTROL DECIDED. See below.
    "matchedRule": "per-transaction",
    "deterministicVerdict": "APPROVE",
    "reasons": []
  },
  "policy": {"id": "my-policy", "version": "1.0"},
  "timestamp": "2026-08-18T00:00:00+00:00",
  "evidence": {"evidenceHash": "..."}   # >= 32 hex chars: 128 bits, per EVID-5
}
```

Three fields are where implementations usually lose marks, so they are worth reading twice.

**`amount` is a string.** `"0.001000"`, never `0.001`. A JSON number has already lost precision
before anything reads it — AEGS-0.1-ARITH-9 — and the vectors test exactly this.

**`decidingEngine` is which control decided, and the suite scores it.** This is the rule the whole
suite turns on: a layer that refuses the sanctions case because an *amount* limit tripped has not
screened anything. It was right by accident, and the same case with a smaller amount would sail
through. That scores `WRONG_REASON` — reported separately from both a pass and a failure, because
the layer did refuse. AEGS-0.1-CONF-2.

**`intentId` may be null, and null is not absent.** The key must be present. A layer that omits it
is saying nothing about intent; a layer that sends `null` is saying *no intent was declared*, which
is a real and honest answer. Those are different states — AEGS-0.1-STATE-1 — and the earlier scorer
punished the honest one, which was a defect in the scorer.

## The report

```
CONF-001  PASS     AEGS-1  treasury   Budget exceeded
CONF-004  FAIL     AEGS-2  sanctions  Sanctioned counterparty
          expected REJECT, got APPROVE
----------------------------------------------------------------
2/7 passed   fail 5

Levels claimable:
  AEGS-1   2/5  claimable: no
  AEGS-2   0/2  claimable: no
```

`--json` gives the machine-readable form; `--out PATH` writes it. Exit codes:

| | |
|---|---|
| `0` | every case passed |
| `1` | AEGS-1 claimable, AEGS-2 not |
| `2` | nothing claimable |
| `3` | the suite could not run — bad adapter, or the implementation is absent |

`3` is deliberately distinct. A CI job that treats a setup failure as a conformance result
publishes a false claim.

## Six outcomes, not two

| | |
|---|---|
| `PASS` | right verdict, right attributed control |
| `FAIL` | wrong verdict |
| `WRONG_REASON` | **right verdict, wrong control.** Right by accident |
| `NOT_IMPLEMENTED` | your adapter returned `None`. Honest, and not a failure |
| `INVALID_RECORD` | the record does not satisfy the schema |
| `ERROR` | your adapter raised. Only that case fails |

## A worked example

The [`stub_adapter.py`](stub_adapter.py) in this directory is a deliberately incomplete layer that
enforces an amount ceiling and nothing else. It scores **2/7**, and it is kept in the suite
permanently for one reason: a conformance suite that has never scored anything below full marks has
not been shown to discriminate.

Read it before writing yours. It is about sixty lines and it shows the shape.

## Publishing a result

AEGS-0.1-CONF-7 requires a published declaration to carry the specification version, the profile
levels, and **every per-case outcome** — including the failures. A declaration reading
`aegs-1: claimed` asks to be trusted; one listing each case can be checked, and argued with.
Publishing failures is what makes publishing passes worth anything.

`--json --out report.json` produces exactly that shape.

## If a case seems wrong

Say so. The suite's cases were written by the same people who wrote the reference implementation,
which is a conflict of interest stated plainly in
[the specification's own security section](../../spec/12-security-considerations.md): *no
independent implementation has been scored — every case and threat written by the author of the
system under test.*

If your layer is right and a case is wrong, that is the most useful bug report this project can
receive. Open an issue on [`aegoll/aegs`](https://github.com/aegoll/aegs/issues) with the case id
and the record you produced.
