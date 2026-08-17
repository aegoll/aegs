# AEGS 0.1 — the decision path

What may run between a proposed action and a verdict, and what may not.

One requirement carries this section: **the decision path is deterministic.** Everything else
here is a consequence of it, including the treatment of models — which turns out to be a
special case of a more general rule about anything the layer cannot control.

Prerequisite reading: [`04-verdicts.md`](04-verdicts.md), and
[VERD-9](04-verdicts.md) in particular.

---

## AEGS-0.1-PATH-1 · The decision path is replayable

An implementation **MUST** be able to re-derive a past decision from its record and obtain the
same verdict and the same attributed control.

> Replayability is the property from which the rest of this section follows, and it is worth
> more than it first appears. It means a decision can be **checked** rather than trusted: given
> the record, an auditor can ask *would this system, on these inputs, decide this again* — and
> get an answer rather than an assurance.
>
> It also makes a regression visible. If an engine's behaviour changes, replaying an old
> journal disagrees with it, and the disagreement is a diff rather than a suspicion. The
> reference implementation compares recorded decision hashes, so a change of behaviour shows up
> even when the verdict happens to land the same way.
>
> Anything non-deterministic in the path destroys this: a clock read, a random number, a
> network call, a model. Which is why the following clauses exist rather than being separate
> concerns.

**Vectors:** conformance case CONF-001

## AEGS-0.1-PATH-2 · No model decides

An implementation **MUST NOT** allow a language model, or any other stochastic component, to
determine a verdict.

A model **MAY** be consulted where it can only narrow, per
[VERD-9](04-verdicts.md).

> The cost, latency and determinism arguments are all real, and the determinism one is
> load-bearing: a model in the path makes [PATH-1](#aegs-01-path-1--the-decision-path-is-replayable)
> impossible, and an unreplayable decision is not an auditable one.
>
> The less-cited argument is the one that matters most in adversarial conditions.
> Counterparty-supplied text reaches this layer on every action — a resource description, a
> vendor name, an error message. A deterministic path **does not read prose**, so there is
> nothing to talk into anything. Putting a model on the path reopens a class of attack that is
> otherwise structurally absent, in exchange for judgement the deterministic controls did not
> need.
>
> Stated honestly: the deterministic path is not thereby secure. The reference implementation
> resisted every prose attack in its own red-team suite and did not resist a **minus sign**,
> and it does not yet resist **patience**. What a deterministic path buys is the removal of one
> whole category, not the removal of risk.

**Vectors:** `path/deterministic-*`, `verdicts/advisor-*`

## AEGS-0.1-PATH-3 · An unreachable external assessor is not-run, never a pass

Where an implementation consults any external service during a decision, an unreachable or
failing service **MUST** be recorded as not-run, and **MUST NOT** be treated as an approval.

An implementation **MUST NOT** allow the availability of an external service to widen a
verdict.

> **Fail-open is a governance layer that stops governing exactly when it is attacked.** An
> assessor that cannot be reached has not approved anything, and recording its silence as a
> pass hands an attacker a disable switch: disrupt one network call and the control is gone,
> with the record showing a clean decision.
>
> Fail-closed has the opposite problem — an availability dependency in the payment path, so
> every outage of a third party becomes an outage of the agent. That is a real cost and a
> reason a deployment might decline the control.
>
> The resolution is the same one [VERD-9](04-verdicts.md) uses for models, and it is why this
> clause generalises rather than repeating: **if an external assessor can only narrow, its
> absence is safe by construction.** No fallback policy is needed, because a verdict reached
> without it was already reached. The fail-open / fail-closed dilemma only exists for a
> control that can *approve*, and this specification does not have those.
>
> Worth naming the live case. A proposed extension to x402 would query external trust providers
> inside the settlement path, with `fail-open` as a configurable mode. Under this clause a
> conformant layer may make that call — and may not let a timeout become a pass.

**Vectors:** `path/external-*`

## AEGS-0.1-PATH-4 · The clock is an input

An implementation **MUST** treat the current time as an input to a decision rather than reading
it from the environment during evaluation.

> Windows, expiries and velocity all depend on the time, so a decision that read a wall clock
> mid-evaluation could not be replayed: the second run is at a different instant and legitimately
> reaches a different answer. Injecting the clock makes the time part of the record, which makes
> the decision reproducible and makes a time-dependent bug testable at all.
>
> This is the clause most likely to be violated by accident, because reading the time is a
> one-line convenience available anywhere.

**Vectors:** `arithmetic/*` (all pure), conformance case CONF-007

## AEGS-0.1-PATH-5 · Policy is data on the decision path

An implementation **MUST NOT** evaluate executable code supplied as policy.

> A policy that can execute is not a policy, it is a plugin — and a policy pack fetched from a
> registry that can execute is remote code execution wearing a governance hat. The threat is
> not hypothetical the moment packs are shared between deployments, which is the direction any
> successful policy format goes.
>
> The practical consequence is a **closed comparator vocabulary**: a fixed set of operators over
> facts the engines produce, with no expression language and nothing to `eval`. Anything a pack
> cannot express is a **missing control**, and the answer is a new control — which is code,
> reviewed as code, on a gated path — rather than an escape hatch in the rule language.
>
> Composition without execution is still possible and worth providing: named predicates over
> existing facts, combined by a fixed set of connectives, remain data. The reference
> implementation calls these derived facts. What makes them safe is that the set of connectives
> is closed, so a pack cannot introduce logic — only arrangement.

**Vectors:** conformance case CONF-002

---

## What a conformant path may contain

Non-normative summary, since the clauses above are all prohibitions and a reader may reasonably
ask what is left.

| Allowed | Because |
|---|---|
| Integer arithmetic over values supplied to it | Deterministic and replayable |
| Reads of state captured before evaluation began | A snapshot is an input |
| A closed set of comparators over engine-produced facts | Data, not code |
| Named predicates composing those facts | Arrangement, not logic |
| An injected clock | Time is an input |
| A model or external service that can **only narrow** | Its absence cannot change an outcome |

| Not allowed | Because |
|---|---|
| Reading a wall clock during evaluation | Breaks replay — PATH-4 |
| A network call that can approve | Fail-open becomes a disable switch — PATH-3 |
| A model that can determine a verdict | Breaks replay and reopens prose attacks — PATH-2 |
| Randomness | Breaks replay — PATH-1 |
| Executable policy | Remote code execution — PATH-5 |
