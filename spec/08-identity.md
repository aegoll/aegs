# AEGS 0.1 — identity and delegation

Who is acting, under whose authority, and how little of that a counterparty needs to know.

Two ideas carry this section. **Pseudonymous by default**, because a governance layer that
leaks its principal's finances to the party being paid has created a harm it was installed to
prevent. And the **delegation clamp**, because an agent that can spawn a sub-agent with more
authority than itself has no authority limit at all.

Prerequisite reading: [`01-model.md`](01-model.md) for the roles,
[`03-envelopes.md`](03-envelopes.md) for what a limit is.

---

## AEGS-0.1-ID-1 · An action names its actor

An implementation **MUST** record which agent took each action.

> The minimum on which everything else rests. An envelope scoped per agent, a delegation
> clamp, an intent — none of them mean anything if a record cannot say who acted.
>
> Note what this does *not* require: that the actor be identified to anyone outside the
> deployment. Recording and disclosing are separate operations, and the next two clauses keep
> them apart.

**Vectors:** conformance case CONF-007

## AEGS-0.1-ID-2 · Pseudonymous by default

An implementation **MUST NOT** disclose the controller, the operator, the agent's wallets, or
its spending limits to a counterparty unless explicitly configured to.

> **`spendingLimits` is the sharpest field in the whole specification**, and the reason is
> uncomfortable once seen: telling a seller how much budget an agent has left invites it to
> charge exactly that. A governance layer that disclosed remaining headroom would have built a
> price oracle for the counterparty, out of the data it holds to protect the buyer.
>
> Wallets are the second-sharpest. A counterparty already sees the address paying it;
> publishing the *set* links an agent's activity across counterparties who otherwise could not
> correlate it. So the disclosure default is not "everything we know" minus secrets — it is
> nothing, plus what a counterparty demonstrably needs.
>
> "Unless explicitly configured to" is deliberate. Some deployments between regulated parties
> must disclose more, and a specification forbidding it outright would be unusable there. What
> it may not be is the default, or implicit.

**Vectors:** `identity/disclose-*`

## AEGS-0.1-ID-3 · Selective disclosure is an operation, not a filter applied later

An implementation **MUST** provide disclosure as an explicit operation that names its audience,
and **MUST NOT** rely on a caller to redact a full record.

> The failure mode is specific and common: a system builds one rich object, hands it to
> whichever layer is rendering, and expects that layer to omit the sensitive parts. It works
> until one caller forgets, and the caller who forgets is usually the newest integration.
>
> Making disclosure an operation moves the decision to where the knowledge is. `disclose("vendor")`
> and `disclose("auditor")` are different projections of the same identity, and the
> implementation — which knows what `spendingLimits` means — decides what each contains. A
> caller that wanted more has to ask for a different audience, which is a visible act.
>
> An auditor projection may reasonably contain everything. An audit that cannot see the
> controller cannot establish accountability, which is what an audit is for.

**Vectors:** `identity/disclose-*`

## AEGS-0.1-ID-4 · A delegate may never exceed its delegator

Where an implementation supports delegation, a sub-agent's effective authority **MUST** be the
narrower of its own and its delegator's.

An implementation **MUST NOT** allow a delegation chain to increase authority at any step.

> Without this, an authority limit is a suggestion. An agent limited to ten dollars that can
> create a sub-agent limited to a thousand has a limit of a thousand, reached by one extra
> function call — and the record would show a compliant parent and a compliant child.
>
> The clamp composes down a chain of any length, and it composes the same way verdicts do: take
> the narrower at every step. That is why the rule is stated as *narrower of its own and its
> delegator's* rather than *not more than the root* — a three-deep chain where the middle agent
> is tightly limited must constrain the leaf, even if the root is generous.
>
> Note the interaction with envelopes. A delegation clamp limits *authority*; an envelope
> limits *spend*. An agent may be authorised for a hundred dollars and have four left, and both
> constraints apply. Conflating them would let a generous delegation refill a budget.

**Vectors:** `identity/delegate-*`

## AEGS-0.1-ID-5 · Revocation takes effect immediately and is recorded

Where an implementation supports revoking an agent's authority, a revoked agent's subsequent
actions **MUST** be refused, and the refusal **MUST** be attributable to the identity control.

> Immediacy is the requirement that has teeth. A revocation that applies at the next
> configuration reload leaves a window, and the window is exactly when it matters — revocation
> is what an operator reaches for when something is already going wrong.
>
> Attribution matters here for the same reason it does everywhere: a refused agent whose record
> says only *"policy"* sends an operator to the wrong file. See
> [VERD-4](04-verdicts.md).

**Vectors:** conformance case CONF-007

---

## What this section does not require

- **Proof of identity.** AEGS carries what an implementation knows about a counterparty and requires it to say *how* it knows. Whether the claim is true is out of scope, and an implementation asserting a verified counterparty without a verification method has overclaimed under [STATE-2](06-four-states.md).
- **A particular identifier scheme.** Wallets, DIDs, account numbers and opaque strings are all acceptable. What matters is that a per-counterparty envelope can be scoped consistently.
- **Originator and beneficiary data.** AEGS carries none, which is a named gap against the FATF Travel Rule and matters for any deployment moving value between regulated parties. Stated in [`00-introduction.md`](00-introduction.md) and repeated here because this is the section a reader would look in.
