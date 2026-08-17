# Profiles

A **profile** says which controls must exist and what evidence must be emitted. A **policy
pack** says what the rules actually are. The first is written by this standard; the second
is written by whoever deploys an implementation.

That split is the adoption mechanism. Nobody installs a standard — they install a spend
cap, pick the default profile, and emit conformant evidence without having read this
directory.

| | Profile | Policy pack |
|---|---|---|
| Answers | which controls must exist, and what must be recorded | what the rules are |
| Example | `aegs-1`, `aegs-2`, `none` | `default.yaml`, `acme-corp.yaml` |
| Shape | a conformance contract | declarative rules |
| Written by | the standard | the user |

---

## What a profile does not do

**A profile never changes a verdict.** Verdicts come from policy and from the engines.
A profile is about *evidence completeness*: given a decision, were the controls this
profile requires actually exercised, and does the record say so?

Conflating the two would be a mistake with a specific consequence. If selecting a profile
could tighten or loosen what gets approved, then two implementations at the same profile
could disagree on outcomes while both claiming conformance — and the profile would have
become a second, weaker policy language.

## Requirement levels

Each control in a profile carries one of three:

| Requirement | Means |
|---|---|
| `MUST_EXERCISE` | The control must run on every in-scope decision, and the record must show it ran |
| `MUST_RECORD` | The control's output must appear in the record when the control exists. It need not run on every decision |
| `OPTIONAL` | May be absent entirely. Absence is not a finding |

**`MUST_EXERCISE` is satisfied by evidence, not by assertion.** A record that omits a
required control is non-conformant, and a record that reports it as `not-run` is
non-conformant *and honest* — which is a better failure than a zero-filled field claiming
a screening that never happened. Absent ≠ not-run ≠ unknown ≠ zero, in the profile as
everywhere else.

## The profiles

| Profile | For |
|---|---|
| [`none`](none.json) | No profile enforcement. A real, working escape hatch — an escape hatch that does not work is one people fork around |
| [`aegs-1`](aegs-1.json) | The baseline: budget, policy, intent, identity, evidence. What a governed agent needs before it is allowed near a wallet |
| [`aegs-2`](aegs-2.json) | Adds counterparty screening and risk. Everything in `aegs-1`, plus what a deployment paying strangers needs |

`aegs-1` is the default because it is the level a reasonable deployment can actually reach
today with a complete record. `aegs-2` is reachable. Nothing here requires a control that
no implementation has.

## What no profile currently requires, and why

Three of the standard's thirteen controls — **AMLAssessment**, **ComplianceAssessment** and
**IncidentRecord** — appear in no profile above `OPTIONAL`. They are schemas with no engine
behind them anywhere, and a profile that required them would be a profile nobody could
satisfy. Requiring something unimplementable does not raise the bar; it makes the bar
decorative.

They get a profile when there is an engine to point at. That is [B6](../PLAN.md).

## Adding or changing a profile

A profile is a conformance contract, so changing one changes what a past declaration
meant. Rules:

- **Adding a control at `MUST_EXERCISE` is a major change.** Implementations that were
  conformant stop being conformant.
- Relaxing a requirement is minor, and needs a note saying what it used to be.
- A new profile is additive and may land in a minor release.
- Every requirement needs a conformance case that checks it. A `MUST` with no case is a
  wish — the same rule the specification follows.
- Profiles are validated in CI against [`profile-0.1.json`](../schemas/profile-0.1.json).

## Downstream copies

Implementations may vendor these files so they can report conformance offline.
`aegoll` does, under `src/aegoll/_profiles/`, pinned to a commit here and checked for
drift. **This directory is canonical**; a profile change is made here and copied down
afterwards, never the reverse.
