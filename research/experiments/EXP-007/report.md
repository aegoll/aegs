# EXP-007 — findings

## Result

Ten runs of 3,000 decisions against **published `aegoll` 0.1.1**, installed from PyPI into a
clean virtual environment:

| | p50 | p99 |
|---|---|---|
| median of ten runs | **168 µs** | 398 µs |
| range | 139 – 330 µs | 272 – 1218 µs |
| spread | **2.4×** | 4.5× |

Zero model invocations. Zero inference cost. The deterministic path stayed deterministic across
30,000 decisions.

## Interpretation

**The overhead claim holds.** A governed decision costs a couple of hundred microseconds and no
tokens. A run making two decisions adds well under a millisecond, which is the claim the design
rests on, and it survives packaging.

**The comparison with EXP-005 does not support a speed-up story, and it is worth saying so
directly.** EXP-005 reported a p50 median of 299 µs; this reports 168 µs. That looks like a 1.8×
improvement and should not be read as one:

- EXP-005 measured a **source checkout of the pre-port `aegl` module**. This measures a
  published wheel. Different code, different import graph.
- EXP-005's own five runs ranged 267–343 µs. This one ranges 139–330 µs. **The ranges overlap.**
- Both were measured on a shared laptop, and this experiment demonstrates that machine load alone
  moves the figure by more than 2×.

The defensible statement is: *the overhead is in the same order of magnitude as before the
restructure, and both measurements are too noisy to claim a difference.* Anything stronger would
be reading precision into a number that does not have it.

## The finding that matters more than the number

**Every previous overhead figure in this project was quoted without an error bar, and at least one
was a single run.** EXP-003 reported "p50 128 µs, p99 211 µs" from one run of 3,000 decisions, and
that figure has since been repeated in a README, a CLI doc and a measurement harness as though it
were a property of the system.

It is a property of one run on one machine. This experiment's ten runs put 128 µs *below* the
observed minimum of 139 µs — so the most-quoted number in the project is, on this machine, at the
optimistic edge of the distribution or outside it.

That is not a defect in the layer. It is a defect in how the layer's performance has been
described, and it is the reason this record reports a range and a spread rather than a headline.

## Limitations

- **One machine**, Windows 11, shared with other work. No server-class or Linux measurement
  exists.
- **p50 spread 2.4×** across identical runs. Treat any single figure as a sample.
- **Not a comparison** with any other governance layer — none has been measured, because no
  independent implementation of AEGS has been scored at all.
- **Decision path only.** No model, no network, no settlement. The end-to-end cost of a governed
  agent run is dominated by the model call and is measured separately, in
  [`harness/`](https://github.com/aegoll/aegoll-integrations/tree/main/harness).

## What should change because of this

1. **Stop quoting 128 µs as the overhead.** Where a single number is needed, "~200 µs, and it
   varies by 2× with machine load" is honest and nearly as short.
2. `aegoll bench` should report a spread when run repeatedly, or say plainly that one invocation
   is one sample. Raised as a follow-up rather than fixed here, because changing the tool during
   a measurement of the tool is how a result becomes unreproducible.

## Supersedes

`EXP-005`, for the overhead figure only. EXP-005's other content — the engine-count attribution
and the intent/identity comparison — is not re-measured here and stands.

**EXP-005 is not edited or deleted.** A superseded record still exists to be contradicted; that
is the whole mechanism, and this record only means something because the earlier one is still
there to disagree with.
