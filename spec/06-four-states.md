# AEGS 0.1 — the four states

**absent ≠ not-run ≠ unknown ≠ zero.**

The shortest section in the specification, and the one whose violation is hardest to notice.
Every other section leans on it: the profile mechanism checks it, the evidence rules require
it, and the arithmetic rules are a special case of it.

Prerequisite reading: [`00-introduction.md`](00-introduction.md).

---

## AEGS-0.1-STATE-1 · Four distinct states, never collapsed

For every value a control may report, an implementation **MUST** distinguish:

| State | Means |
|---|---|
| **absent** | The control does not exist in this implementation |
| **not-run** | The control exists and did not run for this action |
| **unknown** | The control ran and could not determine an answer |
| **zero** | The control ran, determined an answer, and the answer is zero |

An implementation **MUST NOT** represent any of these as any other.

> **This came from a real bug, and the bug is the argument.** An unmeasured counterparty
> history rendered as `0` made every advisor in the reference implementation treat established
> counterparties as strangers. Nothing crashed; nothing logged. The system simply became
> maximally suspicious of exactly the parties it had the most evidence about, because *"I have
> no data"* had been written down as *"the data says zero"*.
>
> The four states are not pedantry about nulls. They are four different things an auditor might
> need to conclude, and collapsing any pair destroys a conclusion:
>
> * **absent vs not-run** — is there a sanctions screening in this system at all? If the field is missing either way, deleting the screening changes nothing observable.
> * **not-run vs unknown** — did the screening skip this action, or run and fail? The first is a coverage gap; the second is an outage.
> * **unknown vs zero** — is the counterparty's trust score zero, or unmeasured? The first says *we know they are untrustworthy*; the second says *we know nothing*. A policy acting on the first is informed; acting on the second it is guessing while appearing informed.
>
> The most favourable reading is the one a reader assumes, which is why the burden is on the
> record to be explicit rather than on the reader to be careful.

**Vectors:** `fourstates/*`

## AEGS-0.1-STATE-2 · Omission means absent, and nothing else

Where a control does not exist, an implementation **MUST** omit its object from the record
rather than emitting it zero-filled.

Where a control exists, its object **MUST** be present, and **MUST** carry an explicit
indication of whether it ran.

> This is what makes the count of schemas honest. AEGS defines thirteen controls and no known
> implementation has engines for all of them — so an implementation that emitted all thirteen
> objects, zero-filled, would be asserting thirteen capabilities and possessing fewer. The
> schemas require omission precisely so that the *presence* of an object is a claim, and a
> claim can be checked.
>
> The second sentence closes the obvious dodge. If omission meant *absent* and a present-but-
> empty object meant nothing in particular, an implementation could satisfy the first sentence
> and still be unreadable. A control that exists says so, and says whether it ran.

**Vectors:** `fourstates/omission-*`

## AEGS-0.1-STATE-3 · A measured zero is reported as a measurement

An implementation **MUST** report a genuine zero as a value, and **MUST NOT** treat it as a
missing value.

> The mirror of STATE-1, and easy to get backwards while defending against it. A budget with
> zero headroom is a **measurement**; a screening that ran and found nothing is a
> **measurement**; a risk score of exactly zero is a **measurement**. An implementation that
> mapped falsy values to *unknown* — a natural thing to write in a language where `0` and
> `None` are both falsy — would punish accurate reporting and would be as wrong as the
> original bug, in the other direction.
>
> The practical test: `0`, `false`, and an empty list are answers. `null` and a missing key are
> not.

**Vectors:** `fourstates/zero-*`

## AEGS-0.1-STATE-4 · A verdict is never a state

An implementation **MUST NOT** use a verdict to express the absence of an opinion.

Where a control has nothing to say about an action, it **MUST** express that as no opinion
rather than as `APPROVE`.

> A control that voted `APPROVE` to mean *"no objection from me"* would be indistinguishable
> from one that examined the action and endorsed it. Since verdicts combine by narrowing, the
> vote is harmless to the outcome — and it is *not* harmless to the record, which would show a
> control affirming something it never looked at.
>
> This is the four-state rule applied to verdicts: silence and approval are different states,
> and `APPROVE` is not the empty value.

**Vectors:** `verdicts/narrow-*`, `fourstates/no-opinion`

---

## An independent convergence, worth recording

The x402 project's proposed trust-provider extension uses three outcomes — `PASS`, `FAIL`, and
**`UNCERTAIN`** — arriving at a distinct not-determined state from an entirely separate
direction, for a different protocol, solving a different problem.

That is weak evidence of a real distinction rather than a local preference. A rule that two
independent designs reach is more likely to be about the domain than about either designer.
Cited because a specification asserting *"these four states are necessary"* should say when
somebody else found some of them too.
