# AEGS 0.1 — budget envelopes

A **budget envelope** is one constraint on spending, and how much of it is left.

A cap on a single payment is not a budget. The distinction this section exists to make
normative is that a governed spend needs *cumulative* limits over time windows, per
counterparty and per resource — and that an implementation must be able to say **which one
bit** and **which one is closest to biting**, because those are different questions and a
reader needs both.

Prerequisite reading: [`00-introduction.md`](00-introduction.md) for requirement levels,
[`05-arithmetic.md`](05-arithmetic.md) for how amounts are represented and compared.

---

## AEGS-0.1-ENV-1 · An envelope has a limit, a used amount, and a window

An implementation **MUST** represent each envelope with a name, a limit, an amount already
consumed, and the window over which consumption is measured.

Limits and consumed amounts **MUST** be integer atomic units, per
[ARITH-1](05-arithmetic.md).

> The window is part of the envelope rather than a property of the query, because *"$50"*
> means nothing without *"per day"*. Two implementations that both enforce a fifty-dollar
> limit and disagree about the window are not enforcing the same policy, and neither record
> would reveal it.

**Vectors:** `envelopes/basic-*`

## AEGS-0.1-ENV-2 · Headroom is the limit less what is consumed, floored at zero

An implementation **MUST** compute headroom as `limit - used`, and **MUST** report zero
rather than a negative number when consumption exceeds the limit.

> Consumption can exceed a limit legitimately: a limit may be lowered after spending
> happened, and a settlement may land after the decision that authorised it. Negative
> headroom is not an error state, it is an over-committed envelope — and reporting `-$12`
> as headroom invites a caller to treat it as arithmetic and add to it. Zero is the honest
> answer to *"how much may I still spend"*.

**Vectors:** `envelopes/headroom-*`

## AEGS-0.1-ENV-3 · An envelope admits an amount that does not exceed its headroom

An implementation **MUST** admit an amount when `amount <= headroom`, and **MUST NOT**
admit one that exceeds it.

An amount exactly equal to the headroom **MUST** be admitted.

> The equality rule is the boundary two implementations most often split on, and it follows
> from [ARITH-8](05-arithmetic.md): a limit of ten dollars admits a payment of exactly ten
> dollars. An implementation that refused it would have a real limit of `$9.999999` and
> records saying `$10`.
>
> The comparison direction also matters. `amount <= headroom` is safe for any non-negative
> amount, and unsafe for a negative one — every negative satisfies it. That is precisely
> the vulnerability [ARITH-4](05-arithmetic.md) exists to prevent, and it is why the sign
> is refused *before* any envelope is consulted rather than by an envelope.

**Vectors:** `envelopes/admits-*`

## AEGS-0.1-ENV-4 · A per-call ceiling is not a cumulative envelope

An implementation **MUST** distinguish an envelope that accumulates from one that caps a
single action, and **MUST NOT** report a consumed amount for a per-call ceiling.

> A per-call ceiling is checked fresh against every action; nothing accumulates against it.
> Reporting it with `used: 0` alongside cumulative windows is *technically true and
> practically false* — a reader sees `$0.00 of $10.00` next to `$32.00 of $50.00` and
> concludes nothing has been spent.
>
> **This was a real defect in the reference implementation's own report output**, caught
> while building it: the per-call ceiling rendered as "used of limit" and read as an untouched
> budget. The fix was to mark the envelope non-cumulative and omit the consumed figure
> entirely, which is why this clause says MUST NOT rather than SHOULD.

**Vectors:** `envelopes/percall-*`

## AEGS-0.1-ENV-5 · Every envelope is evaluated, not merely the first to fail

An implementation **MUST** evaluate every envelope for a decision, and **MUST** record every
envelope that the amount would exceed.

> Short-circuiting on the first breach loses information the reader needs. An amount that
> exceeds one limit is a different situation from one that exceeds five, and an operator
> raising a daily limit to unblock an agent needs to know whether four other envelopes are
> also in the way — otherwise the fix appears not to work and the real cause stays hidden.
>
> This is also what makes the *binding* envelope meaningful: choosing the tightest of the
> breached set requires having evaluated the whole set.

**Vectors:** `envelopes/multiple-*`

## AEGS-0.1-ENV-6 · The binding envelope and the tightest envelope are different things

When a decision is refused by an envelope, an implementation **MUST** identify the
**binding** envelope: the one whose breach determined the refusal.

An implementation **SHOULD** also report the **tightest** envelope — the one with the least
headroom — whether or not the decision was refused.

An implementation **MUST NOT** report a binding envelope when no envelope was breached.

> These answer two different questions and conflating them produces a panel that is empty
> exactly when a reader most wants it. *Binding* answers "why was this refused" and exists
> only for a refusal. *Tightest* answers "what will bite next", and is most useful when
> nothing has been refused yet.
>
> **Found while building the reference implementation's report:** it displayed the binding
> envelope under a heading meaning *closest to biting*, so an approved decision showed no
> envelope at all — the column went blank precisely when the agent was healthy and someone
> was checking headroom. The two concepts are now named separately here so that no
> implementation has to rediscover the distinction from a confusing screen.
>
> Where several envelopes are breached, choosing the one with least headroom is a
> convention rather than a requirement, which is why this clause fixes *that a binding
> envelope is identified* and not *which one*. Conformance scores the attributed control,
> not the attributed envelope.

**Vectors:** `envelopes/binding-*`

## AEGS-0.1-ENV-7 · A count envelope constrains occurrences, not amounts

An implementation **MAY** define envelopes that limit the number of actions in a window
rather than their value. Where it does, the envelope **MUST** be evaluated against the count
already recorded, independent of the amount of the action being decided.

> Velocity is a different shape from value, and treating it as a money envelope with an
> amount of one produces confusing arithmetic. It is also the control that a purely
> value-based envelope set cannot express: forty payments of one cent breach no value limit
> and are still a pattern worth refusing.
>
> **What this clause does not claim.** A count limit constrains rate, not total. Pacing
> exactly at the limit is unbounded over time, and structuring a large payment into many
> small ones defeats value envelopes and count envelopes alike. Both remain open findings
> against the reference implementation, and closing them needs a control that examines the
> *shape* of a sequence rather than any single limit. Named here rather than left for a
> reader to discover.

**Vectors:** `envelopes/count-*`

## AEGS-0.1-ENV-8 · A limit of zero refuses everything; an absent limit constrains nothing

An implementation **MUST** treat a limit of zero as refusing every non-zero amount, and
**MUST** distinguish that from an absent limit, which constrains nothing.

An implementation **MUST NOT** represent an absent limit as zero.

> The four-state rule at its most consequential. A limit of `0` and no limit at all are
> opposite instructions: the first stops the agent entirely, the second lets it spend
> freely. An implementation that defaults a missing limit to zero has silently made its
> strictest possible policy the default; one that defaults it to infinity has done the
> reverse. Both are defensible defaults and neither may be *implied* — the representation
> has to keep them apart so the deployment can choose.
>
> A limit of zero still admits an amount of zero, per [ENV-3](#aegs-01-env-3--an-envelope-admits-an-amount-that-does-not-exceed-its-headroom)
> and [ARITH-6](05-arithmetic.md): `0 <= 0`.

**Vectors:** `envelopes/zero-*`, `envelopes/absent-*`

## AEGS-0.1-ENV-9 · Channels never share an envelope

An implementation **MUST** maintain separate envelopes for the internal and external
channels, and **MUST NOT** allow consumption in one to reduce headroom in the other.

> Different currency, different counterparty, different failure mode. What an agent spends
> on its own inference is billed by a provider against an API key; what it pays out is
> settled to a counterparty. Sharing an envelope between them means a talkative agent
> exhausts its ability to buy anything, and a shopping agent stops being able to think —
> and the record cannot tell an operator which happened.
>
> An implementation **MAY** apply the same *limits* to both channels. It may not apply the
> same *envelope*, because an envelope carries consumption.

**Vectors:** `envelopes/channel-*`

---

## Reference values

Non-normative. All amounts in atomic units at six decimal places.

| limit | used | headroom | admits 0 | admits headroom | admits headroom+1 |
|---|---|---|---|---|---|
| `10000000` | `0` | `10000000` | yes | yes | no |
| `10000000` | `9999999` | `1` | yes | yes | no |
| `10000000` | `10000000` | `0` | yes | yes (zero) | no |
| `10000000` | `12000000` | `0` | yes | yes (zero) | no |
| `0` | `0` | `0` | yes | yes (zero) | no |
| absent | — | unconstrained | yes | yes | yes |
