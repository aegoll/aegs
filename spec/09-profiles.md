# AEGS 0.1 — profiles

Which controls must exist, and what a record must say about them.

A profile is a **conformance contract**. The manifests in [`../profiles/`](../profiles/README.md)
are the machine-readable half; this is the half that says what the requirement levels mean and
why a profile is forbidden from doing the one thing it looks like it should be able to do.

Prerequisite reading: [`01-model.md`](01-model.md) for profile against policy,
[`02-controls.md`](02-controls.md) for the control set.

---

## AEGS-0.1-PROF-1 · A profile never changes a verdict

An implementation **MUST NOT** allow the selected profile to affect a verdict.

> This is the clause that keeps profiles meaningful, and it is the one a reasonable designer
> would get wrong. A profile *looks* like a strictness setting — `aegs-2` requires more than
> `aegs-1`, so surely it decides more conservatively?
>
> It must not, and the consequence of letting it is precise: two implementations at the same
> profile could then **disagree on outcomes while both claiming conformance**. The profile would
> have become a second policy language, weaker than the real one and with no rules written down.
> A conformance claim would then say nothing about what a system does.
>
> So a profile is about **evidence completeness**, and only that. Given a decision, were the
> controls this profile requires actually exercised, and does the record show it? Strictness
> belongs in a policy pack, which is where a deployment can see and change it.

**Vectors:** conformance case CONF-006

## AEGS-0.1-PROF-2 · Three requirement levels

A profile assigns each control one of:

| Level | Means |
|---|---|
| `MUST_EXERCISE` | Runs on every in-scope decision, and the record shows it ran |
| `MUST_RECORD` | The record states the control's position when the control exists |
| `OPTIONAL` | May be absent entirely; absence is not a finding |

An implementation **MUST** treat a control absent from a profile's list as `OPTIONAL`.

> The distinction between the first two is the one that took a bug to get right.
> `MUST_EXERCISE` asks *did the control run* and needs a value that is evidence. `MUST_RECORD`
> asks *does the record state a position* and is satisfied by an explicit null.
>
> The example that fixes it: `intentId: null` is the record saying *no intent was declared*.
> That is a **recorded position**, and exactly what [STATE-1](06-four-states.md) asks for.
> Scoring it as a failure punishes an implementation for being honest and pushes the next one
> toward omitting the key instead — which is strictly worse, because a missing key cannot be
> told apart from a control that does not exist.
>
> So: a missing key fails `MUST_RECORD`; a null one satisfies it. That asymmetry is the whole
> content of having two levels rather than one.

**Vectors:** `fourstates/*`

## AEGS-0.1-PROF-3 · A required control names where its evidence lives

Every control a profile requires above `OPTIONAL` **MUST** be accompanied by the location in a
record where its evidence appears.

> A requirement with nowhere to look for its evidence is not checkable, and an uncheckable
> requirement is the same wish this specification's own conventions forbid. The manifest field
> is called `recordPath`, and its presence is what lets a scorer read a record and reach a
> verdict rather than an opinion.
>
> This is enforced mechanically: `tools/check_profiles.py` fails a `MUST_EXERCISE` control with
> no `recordPath`.

**Vectors:** conformance case CONF-006

## AEGS-0.1-PROF-4 · A profile that extends another may only tighten it

Where a profile declares that it extends another, it **MUST NOT** assign any inherited control a
weaker requirement level than the profile it extends.

> Without this, a higher level could be **weaker** than a lower one while both validated
> perfectly — `aegs-2` could quietly drop a requirement `aegs-1` makes, and a declaration of
> `aegs-2` would then mean less than a declaration of `aegs-1`. The levels would stop being
> ordered, and an ordering is the only thing that makes a level worth claiming.
>
> JSON Schema cannot express this, because it is a relationship between two documents rather
> than a property of one. So it is checked by `tools/check_profiles.py`, and the check was
> verified by planting a relaxation and confirming it failed — a rule enforced by a check nobody
> has seen fail is a rule of unknown strength.

**Vectors:** `profiles/extends-*`

## AEGS-0.1-PROF-5 · An implementation declares the profile it enforces

An implementation **MUST** state which profile it is enforcing, and **MUST** provide a way to
enforce none.

> The first half is what makes a record self-describing: a decision scored against `aegs-1` and
> one scored against `aegs-2` are different claims, and a record that does not say which is
> unassessable.
>
> The second half is a requirement about **escape hatches**, and it is deliberate. A deployment
> that cannot opt out of conformance reporting will fork the implementation to remove it — and a
> fork puts that deployment beyond the reach of every subsequent fix, including security ones. An
> opt-out that works keeps them inside. So `none` is a real profile, listing every control as
> `OPTIONAL`, rather than an absence of one.
>
> An implementation enforcing `none` makes no conformance claim, and **should say so where a
> user will see it** — a green check that guarantees nothing is worse than no check.

**Vectors:** `profiles/none-*`

## AEGS-0.1-PROF-6 · A profile requires nothing unimplementable

A profile defined by this specification **MUST NOT** require a control for which no known
implementation has an engine.

> A constraint on this document rather than on implementations, and the reason it is normative
> is that violating it is tempting. Requiring `AMLAssessment` at `MUST_EXERCISE` would make
> `aegs-2` look considerably more serious, and would make it unsatisfiable — so every
> implementation would claim `aegs-1`, the higher level would go unused, and the specification
> would have gained a decoration.
>
> Requiring something nobody can do does not raise a bar. It makes the bar ornamental, and moves
> the real bar down to whatever level people can actually reach.
>
> The three controls this excludes — `AMLAssessment`, `ComplianceAssessment` as an engine, and
> `IncidentRecord` — get a profile when there is an engine to point at, and not before.

**Vectors:** `profiles/unimplementable-*`

---

## The profiles this specification defines

| Profile | For | Required controls |
|---|---|---|
| [`none`](../profiles/none.json) | No enforcement. A working opt-out | 0 |
| [`aegs-1`](../profiles/aegs-1.json) | Baseline: budget, policy, decision, attribution, evidence, intent, identity | 7 |
| [`aegs-2`](../profiles/aegs-2.json) | Adds counterparty screening and risk; tightens identity | 9 |

`aegs-1` is the sensible default because it is the level a complete record can actually reach
today. `aegs-2` is reachable. Neither requires a control nobody has.
