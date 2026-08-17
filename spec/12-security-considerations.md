# AEGS 0.1 — security considerations

What attacks this specification's requirements defend against, what they do not, and what is
open.

This section is deliberately not reassuring. A governance layer sits next to a wallet, so the
useful document is the one that says where the layer is weak — and a specification whose security
section lists only strengths is a specification that has not been attacked.

The reference implementation's own red-team suite produced the fairest one-line summary anyone
has written of this class of system, and it is worth putting at the top rather than burying:

> **The layer resists prose. It did not resist a minus sign, and it does not yet resist
> patience.**

Prerequisite reading: [`10-decision-path.md`](10-decision-path.md),
[`07-evidence.md`](07-evidence.md).

---

## AEGS-0.1-SEC-1 · Numeric attacks

A negative amount inverts every envelope check, because `amount <= headroom` is satisfied by
every negative. A magnitude beyond representable range crashes an arithmetic path that was not
expecting it.

**Both were live vulnerabilities in the reference implementation**: a `-$1000` request was
**approved**, and a 30-digit amount **crashed** the layer rather than being refused by it.

Defended by [ARITH-4](05-arithmetic.md) and [ARITH-5](05-arithmetic.md), which require refusal
*before* any envelope evaluation and refusal *as a governance decision* rather than an exception.
Both are permanent test vectors, so neither can return quietly.

> The crash is the more interesting of the two. A layer that fails on malformed input can be
> **removed from the path** by sending it malformed input — and if the surrounding system is
> built to fail open, removing the governance layer *is* the attack. That is why ARITH-5
> distinguishes refusing from raising rather than treating both as "handled".

## AEGS-0.1-SEC-2 · Prose attacks

Counterparty-supplied text reaches the layer on every action: a resource description, a
counterparty name, an error message.

Structurally absent while [PATH-2](10-decision-path.md) holds, because a deterministic path does
not read prose. There is nothing to talk into anything.

> This is the strongest property the design has, and it is worth being precise about why: the
> defence is not a filter or a sanitiser, both of which can be got wrong. The attack surface does
> not exist, because no component in the decision path interprets natural language.
>
> **It reopens the moment a model is put on the path**, which is the security argument for
> PATH-2 that the cost and latency arguments tend to overshadow.
>
> One surface remains: an **advisory** model that reads counterparty text. It is defended by the
> narrowing clamp — an injected advisor can only tighten — and the clamp is well tested. What is
> **not** tested is advisor injection itself; it remains absent from the reference
> implementation's threat catalogue, and a detection mechanism has been observed working exactly
> once. That is not a tested defence and is recorded as open below.

## AEGS-0.1-SEC-3 · Evidence attacks

Editing an entry, deleting one from the middle, reordering, and replaying a settled request are
all detected by [EVID-2](07-evidence.md) and [EVID-3](07-evidence.md).

**Truncating the tail is not detected, by anyone, ever, without an external anchor.** Any prefix
of a valid chain is itself valid, so an agent that was refused can delete the refusal and
verification reports success about a history that did not happen.

Required to be disclosed rather than fixed, by [EVID-6](07-evidence.md).

> Two things worth stating that a reader would otherwise have to work out.
>
> **The fix that does not work.** Writing the head and length to a second file beside the journal
> looks like an anchor and is not: whoever can truncate the journal can rewrite that file.
> Shipping it would be worse than shipping the gap, because it would make the system *appear*
> anchored.
>
> **Hash strength is part of this.** A truncated hash weakens edit detection directly: at 64 bits
> a second preimage is 2⁶⁴ work, reachable with commodity GPUs in months. [EVID-5](07-evidence.md)
> requires 128 bits minimum, and the reference implementation retained 64 until writing that
> clause caught it.

## AEGS-0.1-SEC-4 · Authority attacks

Delegation escalation, use of a revoked identity, reuse of an expired intent, and substituting
one agent's authority for another's are all addressed by [ID-4](08-identity.md),
[ID-5](08-identity.md) and [CTRL-3](02-controls.md).

> The intent case is the one that hid a real defect. An expired intent was indistinguishable from
> *no intent declared*, because the implementation filtered expired intents out of its lookup —
> so a lapsed agent was waved through as merely ungoverned. The engine was correct throughout and
> the lookup was wrong, which is why every unit test passed: they called the engine directly.
>
> Found by a conformance case, not by a test. It is the clearest example in this project of why
> an independent instrument is worth having.

## AEGS-0.1-SEC-5 · Availability attacks

An external service consulted during a decision is an availability and manipulation surface. An
implementation that treats an unreachable service as an approval has built a control an attacker
can disable by disrupting one network call.

Addressed by [PATH-3](10-decision-path.md), which requires *not-run* and forbids *pass*.

> **Fail-open is a governance layer that stops governing exactly when it is attacked.** Stated
> again here because it is the failure mode most likely to be introduced by a well-meaning
> reliability improvement — someone notices the layer is a dependency, adds a timeout that
> proceeds on failure, and removes the control.
>
> The structural answer is the one PATH-3 and [VERD-9](04-verdicts.md) share: a component that
> can only *narrow* is safe in its absence, so no fallback policy is required. The dilemma exists
> only for components that can approve.

## AEGS-0.1-SEC-6 · Behavioural attacks — open

Two attacks that no requirement in this specification defends against, and that no single limit
can:

**Structuring.** Forty payments of one cent, paced five minutes apart, breach no value envelope
and no velocity limit. In the reference implementation this moved money with **nothing refused**.

**Velocity evasion.** Pacing exactly at a rate limit is unbounded in total. A limit of ten per
minute permits fourteen thousand a day.

> Both need a control that examines the **shape of a sequence** rather than the size of any
> action, and no amount of tightening an envelope produces one. Tightening makes legitimate use
> harder without addressing either — which is worth saying because tightening is what an operator
> will reach for.
>
> [ENV-7](03-envelopes.md) names this limitation in the clause that would otherwise be read as
> covering it. A count envelope constrains *rate*, not *total*.
>
> These remain open findings. A specification that quietly omitted them would leave a reader
> believing envelopes and velocity limits are together sufficient, and they are not.

## AEGS-0.1-SEC-7 · Policy as an attack surface

A policy pack that can execute is remote code execution wearing a governance hat, and the risk
arrives the moment packs are shared between deployments — which is where any successful policy
format goes.

Addressed by [PATH-5](10-decision-path.md): a closed comparator vocabulary, no expression
language, nothing to evaluate.

> The pressure on this clause is real and will be constant. Every sufficiently expressive policy
> format is asked for an escape hatch, and each individual request is reasonable. The answer that
> holds is that **anything a pack cannot express is a missing control** — and a control is code,
> reviewed as code, on a gated path.
>
> Composition without execution is a genuine middle ground: named predicates over existing facts,
> combined by a *closed* set of connectives, stay data. What makes that safe is the closure. A
> pack that could introduce a connective could introduce logic.

---

## What is open, in one list

Because a reader looking for this should not have to assemble it from seven sections.

| Open | Since |
|---|---|
| **Journal truncation** is undetectable without an external anchor | by construction; disclosed, not fixed |
| **Structuring** — many small payments below every limit | no control examines sequence shape |
| **Velocity evasion** — pacing at the limit is unbounded in total | same |
| **Advisor injection** is untested | not in any threat catalogue; defended by a clamp and a mechanism seen working once |
| **Sanctions screening** is a flag, not a screening | no list, no matching, no jurisdiction model |
| **No independent implementation has been scored** | every case and threat written by the author of the system under test |

## What is closed, and how

| Closed | By |
|---|---|
| Negative amounts | [ARITH-4](05-arithmetic.md), refused before any envelope check |
| Unrepresentable magnitudes | [ARITH-5](05-arithmetic.md), refused rather than raised |
| Prose injection into the decision path | [PATH-2](10-decision-path.md), no model on the path |
| Entry editing, middle deletion, reordering | [EVID-2](07-evidence.md), [EVID-3](07-evidence.md) |
| Weak hashes | [EVID-5](07-evidence.md), 128-bit minimum |
| Delegation escalation | [ID-4](08-identity.md), clamp to the narrowest step |
| Expired intent read as no intent | [CTRL-3](02-controls.md) |
| Fail-open on an unreachable assessor | [PATH-3](10-decision-path.md) |
| Executable policy | [PATH-5](10-decision-path.md) |
| A right answer for the wrong reason | [CONF-2](11-conformance.md) |
