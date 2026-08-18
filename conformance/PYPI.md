# aegs-conformance

**Score an autonomous economic governance layer against AEGS 0.1 — including one this project
did not write.**

```bash
pip install aegs-conformance
aegs-conformance --against my_layer.conformance:MyAdapter
```

Seven cases, six outcomes, a report you can publish, and an exit code your CI can gate on.

## Why `--against` and not a plugin registry

A conformance suite that can only score adapters listed inside itself is a self-assessment.
Everybody else has to fork it, and a forked instrument produces numbers nobody can compare. So
the adapter lives in **your** package, where your imports resolve, and the suite is pointed at it
by name. Nothing here changes to accommodate you.

## The interface

Two attributes, nothing to subclass, no import from this package:

```python
class MyAdapter:
    name = "my-layer"

    def run_case(self, case) -> dict | None:
        """Decide, and return an AEGS Decision Record. None = not implemented."""
```

Returning `None` scores `NOT_IMPLEMENTED`, which is reported **separately from a failure** — an
honest *I do not do this* is not a wrong answer, and a suite that conflated them would push
implementers toward pretending.

Full guide, including the record shape and the three fields implementations usually get wrong:
[`conformance/adapters/README.md`](https://github.com/aegoll/aegs/blob/main/conformance/adapters/README.md).

## The rule the suite turns on

A layer that refuses the sanctions case because an **amount** limit tripped has not screened
anything. It was right by accident, and the same case with a smaller amount would sail through.

That scores `WRONG_REASON` — not a pass, and not the same as a failure, because the layer did
refuse. The suite scores **which control decided**, not just the verdict. AEGS-0.1-CONF-2.

## Six outcomes

| | |
|---|---|
| `PASS` | right verdict, right attributed control |
| `FAIL` | wrong verdict |
| `WRONG_REASON` | right verdict, wrong control |
| `NOT_IMPLEMENTED` | honestly declined |
| `INVALID_RECORD` | the record fails the schema — a conformant verdict in a malformed record is not a pass |
| `ERROR` | your adapter raised; only that case fails |

## Exit codes

| | |
|---|---|
| `0` | every case passed |
| `1` | AEGS-1 claimable, AEGS-2 not |
| `2` | nothing claimable |
| `3` | **could not run** — bad adapter, or the implementation is absent |

`3` is deliberately distinct from `2`. A CI job that treats a setup failure as a conformance
result publishes a false claim, and an uninstalled layer would otherwise produce a
plausible-looking `0/7` report about a system nobody ran.

## What this package does *not* install

It does not depend on `aegoll`, the reference implementation. Scoring it is an extra
(`pip install aegs-conformance[reference]`), because a conformance suite that arrives with the
thing it tests is not a conformance suite — and `runner.py` imports no implementation at all,
which a test asserts by walking its AST.

Validation is offline by design: the schema ships with the package rather than being fetched, so
a run cannot be made to pass by a network.

## The open question this exists to answer

From the specification's own security section:

> **No independent implementation has been scored** — every case and threat written by the author
> of the system under test.

That is a conflict of interest, stated in the standard rather than hidden. If your layer is right
and a case is wrong, that is the most useful bug report this project can receive:
[github.com/aegoll/aegs/issues](https://github.com/aegoll/aegs/issues).

## The standard

- [Specification](https://github.com/aegoll/aegs/tree/main/spec) — twelve sections, 56 normative
  clauses, every MUST with a test
- [Test vectors](https://github.com/aegoll/aegs/tree/main/vectors) — 151 language-neutral vectors
  across nine families
- [Reference implementation](https://pypi.org/project/aegoll/) — `pip install aegoll`

Apache-2.0 for the suite; the specification text is CC-BY-4.0.
