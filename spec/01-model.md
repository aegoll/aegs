# AEGS 0.1 — the model

Who acts, on whose authority, against whom, and with what.

This section defines terms and imposes almost nothing. That is deliberate: a specification
that constrains the *shape* of a deployment excludes deployments it was never asked about,
and the useful requirements are about what gets **recorded**, not about how a system is
arranged. Those live in [`02-controls.md`](02-controls.md) and after.

Prerequisite reading: [`00-introduction.md`](00-introduction.md).

---

## AEGS-0.1-MODEL-1 · The parties

Four roles. A single legal or natural person may hold several, and a deployment may leave some
implicit.

| Role | Is |
|---|---|
| **agent** | The software taking the economic action. The thing being governed |
| **controller** | Whoever bears the financial consequence — the party whose money it is |
| **operator** | Whoever runs the agent day to day. Often the controller, not necessarily |
| **counterparty** | Whoever would receive the payment |

> The controller and the operator come apart more often than a first design assumes, and the
> distinction matters for exactly one reason: **the controller's interest is what a governance
> layer protects, and the operator is who configures it.** An operator raising a limit is
> acting on the controller's money, so the record has to be able to say who did what — which
> is why an override is journalled with its author rather than applied silently.
>
> A counterparty is a role, not an identity. On one rail it is a wallet address, on another a
> merchant category code, on a third a service endpoint. What AEGS requires of it is only that
> a decision can name it consistently enough for a per-counterparty envelope to mean
> something.

## AEGS-0.1-MODEL-2 · The action

An **economic action** is a proposal to move value out, evaluated before it happens.

An action carries at minimum: an amount, an asset, a counterparty, and the resource or purpose
it is for.

> "Before it happens" is the whole substance. A layer that records what an agent spent is
> accounting; a layer that decides whether it may is governance. Everything in this
> specification assumes the decision precedes the movement, and an implementation that
> evaluated afterwards would satisfy the schemas and none of the point.
>
> The minimum contents are what the controls need to be able to say anything: an envelope
> needs an amount, a per-counterparty envelope needs a counterparty, and an intent check needs
> to know what the spending was *for*. A deployment that cannot supply the purpose can still
> use the rest — it simply has no intent control, and its records say so rather than implying
> one.

## AEGS-0.1-MODEL-3 · The two channels

Every action belongs to exactly one **channel**:

| Channel | Is |
|---|---|
| **internal** | What the agent spends on its own operation — inference, tools, compute |
| **external** | What the agent pays out to a counterparty |

> Not a taxonomy for its own sake. The two differ in currency, in counterparty, and in failure
> mode, and the consequence is [ENV-9](03-envelopes.md): they never share an envelope.
>
> The failure modes are worth naming because they pull in opposite directions. An exhausted
> *internal* budget means the agent cannot finish thinking, and there is no human to ask
> mid-run — so the right answer is to refuse the run rather than queue it, because starting a
> run that cannot complete wastes the budget that was already short. An exhausted *external*
> budget means a purchase cannot proceed, and queueing it for a human is often exactly right.
> One layer, two channels, two different senses of "out of money".

## AEGS-0.1-MODEL-4 · Controls, policy, and profile

Three things that are routinely conflated, and each is a different kind of object.

| | Is | Written by |
|---|---|---|
| **control** | A capability: something an implementation can assess and record | the implementation |
| **policy** | Rules over what controls produce | whoever deploys |
| **profile** | Which controls must exist, and what must be recorded | this specification |

> The confusion to avoid is between *policy* and *profile*, because both look like
> configuration. A profile is a **conformance contract**: it says a trust assessment must
> happen and be recorded. A policy says *what to do* with the resulting score. An
> implementation enforces a profile and executes a policy, and it can be conformant while
> executing a policy nobody sensible would deploy — conformance is about evidence
> completeness, not about whether the rules are wise.
>
> See [`09-profiles.md`](09-profiles.md) for the profile mechanism and
> [`02-controls.md`](02-controls.md) for the control set.

## AEGS-0.1-MODEL-5 · What AEGS does not model

Stated so the boundary is visible rather than discovered.

- **Settlement.** Whether money actually moved, and what happens when it half-moves, belongs to the payment rail. AEGS records the *decision* and can record a settlement as a later event; it does not specify one.
- **Identity proofing.** Whether a counterparty is who it claims is out of scope. AEGS carries what an implementation knows and requires it to say how it knows.
- **Pricing.** What a resource *should* cost is a judgement AEGS has no view on. A control may compare a price to a history, which is a different and much weaker claim.
- **Orchestration.** How an agent decides to want something is entirely outside this specification. AEGS begins at the proposal.
