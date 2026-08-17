# AEGS 0.1 — verdicts, narrowing, and attribution

The four outcomes a decision may have, the one direction a control may move them, and the
requirement that a record say **which control decided**.

This is the section conformance actually scores. A correct verdict reached by the wrong
control is right by accident, and the same case shaped slightly differently would produce
the wrong answer — so a suite that checked only verdicts would certify implementations that
happen to agree rather than implementations that reason.

Prerequisite reading: [`00-introduction.md`](00-introduction.md) for requirement levels,
[`03-envelopes.md`](03-envelopes.md) for the constraint one control evaluates.

---

## AEGS-0.1-VERD-1 · Four verdicts, in a fixed order of severity

An implementation **MUST** produce exactly one of `APPROVE`, `REVIEW`, `ESCALATE`, `REJECT`
for every decision.

An implementation **MUST** order them by severity as:

```
APPROVE  <  REVIEW  <  ESCALATE  <  REJECT
```

> The ordering is normative rather than obvious. `REVIEW` and `ESCALATE` are the pair that
> invites disagreement: both defer to a human, and an implementation could reasonably rank
> either as stricter. AEGS fixes `ESCALATE` as the more severe because `REVIEW` is
> *pausable* — the action queues and a human answers later — whereas `ESCALATE` is
> *blocking*: the agent cannot proceed at all. Two implementations that disagreed here would
> produce different final verdicts from the same controls, which is the one thing narrowing
> is supposed to prevent.

**Vectors:** `verdicts/severity-*`

## AEGS-0.1-VERD-2 · A control may only narrow

An implementation **MUST NOT** allow any control to move a verdict toward `APPROVE`.

Where two controls disagree, the more severe verdict **MUST** be the one that stands.

> This is the load-bearing invariant of the whole design. It is what makes a policy file
> safe to hand to somebody: a badly written rule can make the system stricter and cannot
> make it looser, so the worst outcome of a mistake is a refused payment rather than an
> unguarded one.
>
> The strongest way to satisfy this clause is to make widening **unreachable** rather than
> refused. A control that returns an *opinion*, with the composition applying a
> narrow-only combination, cannot widen — there is no code path to audit, because there is
> nothing to get wrong. An implementation that instead checks each control's output and
> rejects widening attempts satisfies the clause and carries a bug surface the first
> approach does not have.

**Vectors:** `verdicts/narrow-*`

## AEGS-0.1-VERD-3 · The final verdict does not depend on evaluation order

An implementation **MUST** produce the same final verdict regardless of the order in which
controls are evaluated.

> A consequence of [VERD-2](#aegs-01-verd-2--a-control-may-only-narrow) rather than an
> additional requirement: narrowing to the most severe of a set is commutative and
> associative, so the result is the maximum over severities and order cannot affect it.
>
> Stated explicitly anyway, because it is what lets an implementation parallelise or reorder
> its engines for performance without changing a single outcome — and because the *next*
> clause is its exception, which is far easier to state once this one is on the page.

**Vectors:** `verdicts/order-*`

## AEGS-0.1-VERD-4 · Attribution does depend on evaluation order, so the order is normative

An implementation **MUST** attribute each decision to exactly one control.

Unless a dispositive control applies (VERD-4a), the attributed control **MUST** be the last
control that narrowed the verdict.

An implementation **MUST** document its evaluation order.

> Here is the asymmetry that makes this section necessary. The final verdict is
> order-independent; **the attributed control is not.** If treasury narrows `APPROVE` to
> `REVIEW` and risk then narrows `REVIEW` to `ESCALATE`, the answer is `ESCALATE` either way
> round — but the control that *determined* it differs, and conformance scores attribution.
>
> "The last control that narrowed" is well defined precisely because widening is impossible:
> a control that proposes something no stricter than the standing verdict changes nothing, so
> it did not narrow and is not the attributed control. The final narrowing is therefore
> unique, and it is the one that fixed the outcome.
>
> Requiring the order to be *documented* rather than *fixed* is deliberate. AEGS does not
> know which controls an implementation has, so it cannot impose a sequence — but an
> implementation whose order is undocumented has an attribution nobody can predict, and
> therefore an attribution nobody can audit.

**Vectors:** `verdicts/attribution-*`

## AEGS-0.1-VERD-4a · A control may be declared dispositive

An implementation **MAY** declare a control **dispositive**: one whose finding determines
attribution whenever the finding is present, whether or not it narrowed the verdict.

An implementation that does so **MUST** document which controls are dispositive and their
precedence relative to one another.

> **This clause exists because the previous one was wrong, and a vector caught it.**
>
> "The last control that narrowed" is a good default and it fails on a real case. Consider a
> sanctioned counterparty whose payment a spending limit *also* refuses. The limit narrowed;
> the sanctions screening did not, because the verdict was already `REJECT`. By the default
> rule the decision is attributed to the budget — so the record says an agent was stopped by
> a spending limit, when the truth is that it tried to pay a sanctioned party. An operator
> raising the limit would then find the payment still refused and no explanation on the
> record.
>
> Some findings are categorical rather than quantitative. A counterparty is barred or it is
> not, and that fact does not become less true because a second constraint happened to bite
> first. Attribution has to be able to say so.
>
> The requirement to *declare* the set is what keeps this from being an escape hatch. An
> implementation may not attribute freely — it must fix, in advance and in writing, which
> controls are dispositive and how they rank, so that attribution stays predictable from the
> outside. An undeclared dispositive control is indistinguishable from arbitrary
> attribution, which is the thing this whole section exists to prevent.
>
> Note the interaction with VERD-6: a dispositive control necessarily records its finding
> unconditionally, because attribution depends on the finding being *present* rather than on
> its having changed anything. The two clauses come from the same defect and pull in the
> same direction.

**Vectors:** `verdicts/attribution-dispositive-*`, `verdicts/attribution-default-rule-*`

## AEGS-0.1-VERD-5 · An attributed control is never absent

An implementation **MUST NOT** emit a decision whose attributed control is absent, null, or
a placeholder.

Where no control narrowed — every control admitted the action — the attributed control
**MUST** be the one that produced the standing verdict.

> A refusal with no attributable cause is not auditable evidence. It tells an operator that
> something said no and gives them nowhere to look, which in practice means the layer gets
> disabled rather than understood.
>
> The second sentence covers the approval case, which is easy to overlook: if nothing
> narrowed, something still *decided*, and naming it is what makes an approval as
> accountable as a refusal. An implementation that attributed only refusals would have
> records that go quiet exactly when an auditor asks *why was this allowed*.

**Vectors:** `verdicts/attribution-*`

## AEGS-0.1-VERD-6 · A control that ran must leave evidence that it ran

An implementation **MUST** record evidence that a control was exercised, independently of
whether that control changed the verdict.

Where a control's only trace would be its effect on the verdict, the implementation
**MUST** record the control's finding even when the finding changed nothing.

> **This clause exists because of a real defect, and it is subtler than it looks.** In the
> reference implementation a sanctions bar could be recorded as a *policy* refusal: the
> sanctions clamp was only written to the record when it *changed* the verdict, so when a
> policy rule happened to refuse first, the record showed no sanctions screening at all.
> Deleting the screening entirely would have left every record identical — the policy rule
> still caught the case, and nothing was there to notice the control had gone.
>
> The requirement is *evidence that the control ran*, not *a log line per clamp*. Those come
> apart usefully. A control whose assessment is recorded independently — a budget state, a
> risk score — already satisfies this clause without any clamp entry, because its absence
> would be visible in the record. A control whose only footprint is its clamp must write
> that clamp unconditionally. An implementation may therefore treat its controls
> asymmetrically here, and the asymmetry is justified by *where the evidence lives* rather
> than by convenience.
>
> The test to apply to any implementation: **delete a control, and does any record change?**
> If not, that control was never really evidenced.

**Vectors:** `verdicts/evidence-*`

## AEGS-0.1-VERD-7 · Policy may narrow and nothing more

An implementation **MUST NOT** allow a policy rule to widen a verdict that any control has
set.

> A restatement of [VERD-2](#aegs-01-verd-2--a-control-may-only-narrow) aimed squarely at
> policy, because policy is the part users write and therefore the part that will be wrong.
> A rule saying `APPROVE` cannot rescue an action that a budget refused. If it could, the
> policy file would be an override mechanism and every envelope in the system would be
> advisory.
>
> This is also why a policy pack is data rather than code, and why the comparator vocabulary
> is closed: the narrowing guarantee is only worth as much as the guarantee that a rule
> cannot execute.

**Vectors:** `verdicts/narrow-policy-*`

## AEGS-0.1-VERD-8 · Nothing matched means fail closed

Where no policy rule matches an action, an implementation **MUST NOT** approve it.

> The default has to be the safe one, and for a layer that exists to refuse spending the
> safe default is not spending. An implementation whose fall-through is `APPROVE` has built
> a system where forgetting to write a rule authorises payment — and the failure is silent,
> because an approval produces no complaint.
>
> AEGS does not fix *which* non-approving verdict is the fall-through. `REVIEW` is a
> reasonable choice, since an unanticipated action is exactly the kind a human should see.
> `REJECT` is also defensible. `APPROVE` is not.

**Vectors:** `verdicts/failclosed-*`

## AEGS-0.1-VERD-9 · An advisory model may narrow, never widen, and never decide alone

Where an implementation consults a model, the model's output **MUST** be constrained to
narrowing, and the implementation **MUST NOT** allow a decision to depend on the model's
availability.

> A governance layer whose verdict depends on a model has taken on that model's cost,
> latency and non-determinism, and has lost the ability to replay its own decisions — which
> is what makes a decision auditable at all.
>
> The availability requirement is the half that is easy to get wrong. An implementation that
> fails *open* when its advisor is unreachable has built a control that stops governing
> exactly when it is under attack; one that fails *closed* has built an availability
> dependency into every payment. Constraining the advisor to narrowing resolves both: if it
> can only tighten, its absence is safe by construction and needs no fallback policy at all.
>
> This clause is why AEGS can require deterministic decisions without banning models
> outright. See `10-decision-path.md` (not yet written) for the fuller treatment.

**Vectors:** `verdicts/advisor-*`

---

## Reference values

Non-normative. `narrow(a, b)` is the more severe of the two.

| a | b | narrow(a, b) |
|---|---|---|
| `APPROVE` | `APPROVE` | `APPROVE` |
| `APPROVE` | `REVIEW` | `REVIEW` |
| `REVIEW` | `APPROVE` | `REVIEW` |
| `REVIEW` | `ESCALATE` | `ESCALATE` |
| `ESCALATE` | `REVIEW` | `ESCALATE` |
| `ESCALATE` | `REJECT` | `REJECT` |
| `REJECT` | `APPROVE` | `REJECT` |
| `REJECT` | `REJECT` | `REJECT` |

Attribution, for a sequence of proposals against a standing verdict:

| standing | proposals, in order | final | attributed to |
|---|---|---|---|
| `APPROVE` | treasury `REVIEW`, risk `ESCALATE` | `ESCALATE` | risk |
| `APPROVE` | risk `ESCALATE`, treasury `REVIEW` | `ESCALATE` | risk |
| `APPROVE` | treasury `REJECT`, risk `ESCALATE` | `REJECT` | treasury |
| `REVIEW` | risk `APPROVE` | `REVIEW` | *(unchanged — risk did not narrow)* |

The third and fourth rows are the ones worth reading twice. In the third, risk proposed
something less severe than the standing `REJECT`, so it did not narrow and treasury remains
attributed. In the fourth, nothing narrowed at all, and attribution falls to whatever
produced the standing verdict — never to the control that tried and failed to widen.

With a dispositive control declared, per VERD-4a:

| standing | proposals, in order | dispositive | final | attributed to |
|---|---|---|---|---|
| `APPROVE` | policy `REJECT`, sanctions `REJECT` | sanctions | `REJECT` | sanctions |
| `APPROVE` | treasury `REJECT`, sanctions `REJECT` | sanctions | `REJECT` | sanctions |
| `APPROVE` | treasury `REJECT`, risk `ESCALATE` | sanctions | `REJECT` | treasury |

In the first two, sanctions did not narrow — the verdict was already `REJECT` — and it is
attributed anyway, because a counterparty being barred does not become less true when a
second constraint bites first. In the third no dispositive finding is present, so the
default rule applies unchanged.
