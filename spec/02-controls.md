# AEGS 0.1 — the control set

Thirteen named capabilities, what each is for, and what a record must say about it.

A **control** is something an implementation can assess and record. It is not a module, a
service, or a file — two controls may live in one function and one control may span three
services. What AEGS fixes is the *name*, so that a profile can require it and a record can
attribute a decision to it.

Prerequisite reading: [`01-model.md`](01-model.md),
[`06-four-states.md`](06-four-states.md) for how a control reports having not run.

---

## AEGS-0.1-CTRL-1 · The control names are closed

An implementation **MUST NOT** attribute a decision to a control name outside the set defined
here, except for names it defines itself and documents.

> A closed core set is what makes a conformance report comparable. If `treasury` meant a budget
> in one implementation and a counterparty check in another, a profile requiring it would
> require two different things and every report would need a translation table.
>
> Extension is allowed and expected — an implementation may add controls this specification did
> not anticipate. What it may not do is *reuse* a defined name for something else, because that
> is the one form of extension a reader cannot detect.

**Vectors:** `verdicts/attribution-*`

## AEGS-0.1-CTRL-2 · The set

| Control | Answers | Engine-backed in the reference implementation |
|---|---|---|
| **AgentIdentity** | Who is acting, under whose authority | yes |
| **EconomicIntent** | What the agent was sent to do | yes |
| **Policy** | What the rules say about this action | yes |
| **BudgetEnvelope** | How much is left, and which limit binds | yes |
| **RiskAssessment** | How risky this action looks | yes |
| **TrustAssessment** | What is known about this counterparty | yes |
| **GovernanceDecision** | The verdict | yes |
| **EvidenceRecord** | What happened, append-only | yes, truncation gap open |
| **Authorization** | Which control decided | yes |
| **ConformanceDeclaration** | What this implementation claims | yes |
| **AMLAssessment** | Financial-crime screening | **no engine** |
| **ComplianceAssessment** | Controls exercised against a profile | yes, as a profile assessment |
| **IncidentRecord** | What went wrong, and what was done | **no engine** |

Each is described below only where it needs more than its one-line answer.

## AEGS-0.1-CTRL-3 · EconomicIntent

An implementation supporting this control **MUST** distinguish *no intent declared* from *an
intent that has expired*.

> **The question no other control can ask.** Treasury, trust, risk and policy will all approve a
> perfectly ordinary purchase by a repurposed agent: the amount is fine, the counterparty is
> known, the pattern is unremarkable. None of them knows what the spending was *for*.
>
> The expiry distinction is a real defect, caught by a conformance case rather than by a unit
> test. An implementation filtered expired intents out of its lookup, so a lapsed agent was
> waved through as *ungoverned by intent* — indistinguishable in the record from an agent that
> never declared one. The engine was correct throughout and the lookup was wrong, which is why
> the unit tests passed: they called the engine directly.

**Vectors:** conformance cases CONF-003, CONF-007

## AEGS-0.1-CTRL-4 · TrustAssessment

An implementation supporting this control **MUST** distinguish a cold-start value from a
measured one.

> A new counterparty is not a distrusted one, and the difference has to survive into the record.
> An implementation reporting a cold-start score as though it were measured is asserting
> knowledge it does not have — and one reporting *no data* as a zero score is the original
> four-state bug, which is where that rule came from.
>
> AEGS says nothing about how trust is computed. Earned standing, settled-transaction counts,
> dispute penalties and external reputation are all implementation choices. What is required is
> that the record say whether the number was measured.

**Vectors:** `fourstates/*`

## AEGS-0.1-CTRL-5 · RiskAssessment

An implementation supporting this control **MUST NOT** treat a risk score as a verdict.

> The engine measures how risky an action inherently is; **policy** decides how much of that is
> acceptable at a given exposure. Keeping them apart is what makes a risk score *evidence*
> rather than a decision, and it is why a low-value action can proceed with an unfamiliar
> counterparty while the same score at a higher value does not.
>
> Fusing them produces a control whose threshold is invisible: the record shows a refusal
> attributed to risk, and nobody can see what number would have been acceptable.
>
> Stated plainly, because this control invites overclaiming: a risk score's **accuracy** is not
> a conformance property. The reference implementation's weights are hand-chosen and have never
> been validated against outcomes. AEGS requires that a score be produced, recorded, and
> distinguishable from an unmeasured one — not that it be right.

**Vectors:** `verdicts/narrow-*`

## AEGS-0.1-CTRL-6 · AMLAssessment

An implementation **MUST NOT** assert an AML screening it did not perform.

Where an implementation carries no screening capability, the control **MUST** be absent from
the record rather than present and empty.

> This control is defined as an interface and required by no profile, and the reason is worth
> being explicit about: **no known implementation has an engine behind it.** Requiring it would
> make every profile unsatisfiable, which does not raise the bar — it makes the bar decorative.
>
> What the reference implementation has is a boolean on a counterparty object. No list, no
> matching algorithm, no jurisdiction model, no fuzzy name resolution. That is a *flag*, not a
> screening, and the specification says so here rather than letting a schema's existence imply
> otherwise.
>
> The FATF Travel Rule is a named gap: AEGS carries no originator or beneficiary data at all,
> which matters for any deployment moving value between regulated parties.

**Vectors:** `fourstates/omission-*`

## AEGS-0.1-CTRL-7 · ComplianceAssessment

Where an implementation emits this control, it **MUST** state the profile the assessment was
made against.

> *"We run a trust engine"* is a capability claim. *"This decision exercised TrustAssessment
> under aegs-2"* is a checkable statement about one action. The difference is the profile, and a
> compliance assessment without one is the first sentence wearing the second's clothes.

**Vectors:** conformance case CONF-006

## AEGS-0.1-CTRL-8 · IncidentRecord

An implementation **MUST NOT** modify an incident record after writing it.

> Defined as an interface with no engine anywhere, like AMLAssessment. It is specified rather
> than omitted because the append-only requirement is the part that would be got wrong first:
> an incident is exactly the kind of record a system is tempted to *update* as understanding
> improves, and an incident history that can be edited is a summary of current beliefs rather
> than a record of what happened.
>
> A correction is a new record referencing the earlier one. Same rule as
> [EVID-1](07-evidence.md), stated here because this is the control a reader would look under.

**Vectors:** `evidence/append-*`

---

## Which controls a profile requires

Not this section's business. See [`09-profiles.md`](09-profiles.md) and the manifests in
[`../profiles/`](../profiles/README.md) — a control's *existence* is defined here, and whether
a deployment must have it is a profile question.

Three controls sit at `OPTIONAL` in every profile: **AMLAssessment**, **ComplianceAssessment**
and **IncidentRecord**. The first and third have no engine anywhere; the second is required
only in the sense that any implementation emitting it must name a profile.
