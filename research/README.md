# Research records

Sealed experiments. Each one stamps what produced it, and each is immutable once sealed.

```bash
python research/tools/experiment.py new EXP-008 "A title"
python research/tools/experiment.py seal EXP-008
python research/tools/experiment.py verify
python research/tools/experiment.py list
```

## The two rules

**Every record stamps its world** — commit, dirty-tree flag, policy bundle *hash*, package
versions, Python version, date. A result whose provenance is "we ran it in August" is not
evidence. `policy_state()` raises rather than degrading if it cannot read the policy packs,
because a record sealed with no policy hash makes that hole permanent.

**A sealed record is immutable.** `manifest.json` and `results.json` are checksummed into
`SHA256SUMS`, and `verify()` fails if either changes. Re-running an experiment produces a **new**
id with `supersedes` pointing back; it never edits an old one.

That second rule is what makes a changed conclusion visible. This project has already overturned
one of its own findings, and that is only legible because the superseded record still exists to be
contradicted.

## Where the records are

| Records | Where | Why |
|---|---|---|
| EXP-001 … EXP-006 | the [proof-of-concept](https://github.com/Jayzilva/x402/tree/main/research) | their commit stamps refer to that tree, and moving them would break the provenance they exist to carry |
| EXP-007 onward | here | W0.5, option (c): historical records stay put, new ones live with the standard |

## EXP-007, and why it matters beyond its own number

It re-measured the deterministic governance overhead against **published `tesoro` 0.1.1** rather
than a source checkout, and found the layer holds up: a couple of hundred microseconds, zero
tokens, across 30,000 decisions.

The finding worth reading is the other one. p50 varies **2.4×** across ten identical runs on the
same machine — and EXP-003's widely-quoted "128 µs" came from a *single* run, which lands below
the minimum of the ten measured here. The most-repeated performance number in this project sits at
or outside the optimistic edge of its own distribution.

That is not a defect in the layer. It is a defect in how the layer has been described, and it is
why EXP-007 reports a range and a spread instead of a headline.
