# AEGS 0.1 — conformance

What a conformance claim means, what evidence it needs, and what it does not assert.

The short version: conformance means **an implementation's records show the controls a profile
requires, exercised for the right reasons.** It does not mean the implementation is secure, that
its policy is sensible, or that its scores are accurate — and this section says so in normative
text so that a claim cannot be quoted as though it did.

Prerequisite reading: [`09-profiles.md`](09-profiles.md),
[`04-verdicts.md`](04-verdicts.md) for attribution.

---

## AEGS-0.1-CONF-1 · A claim names a profile and a specification version

A conformance claim **MUST** state the profile claimed and the version of this specification it
was assessed against.

> Two independently moving version lines, and a claim missing either is unassessable. An
> implementation's own version says nothing about which requirements it met, and a profile name
> means different things across specification versions — `aegs-2` today and `aegs-2` after a
> major revision are different contracts.
>
> This is why every record carries both, and why a declaration that carries only *"conformant"*
> is a marketing statement.

**Vectors:** conformance case CONF-006

## AEGS-0.1-CONF-2 · A right answer for the wrong reason is not a pass

A conformance assessment **MUST** score the attributed control, not only the verdict.

Where a verdict is correct and the attributed control is not the one under test, the result
**MUST** be recorded distinctly from both a pass and a failure.

> **This is the clause that makes the whole scheme worth running**, and it came from finding two
> real defects that 229 passing tests could not see.
>
> An implementation that returns `REJECT` for a budget case because its *risk* engine happened
> to fire has not demonstrated budget enforcement. It was right by accident, and the same case
> shaped slightly differently would sail through — so counting it as a pass lets an
> implementation certify a control it does not have. That is precisely what a conformance suite
> exists to prevent.
>
> The third outcome matters as much as the requirement. `WRONG_REASON` is neither a pass nor a
> failure: the implementation *did* refuse, and not for the reason under test. Collapsing it
> into either loses information — into *pass* and the suite is toothless, into *fail* and an
> implementation with a defensible design is told it is broken.
>
> Both defects this caught had the same shape: a correct verdict reached in a way that left no
> evidence the control existed. A sanctions bar recorded as a policy refusal, and an expired
> intent indistinguishable from no intent. Delete the control in either case and every test
> still passed.

**Vectors:** `verdicts/attribution-*`

## AEGS-0.1-CONF-3 · Declining a case is an honest outcome

An implementation **MUST** be able to decline a conformance case it cannot express, and a
declined case **MUST NOT** be scored as a pass.

> An implementation that cannot express a case has three options, and only one is acceptable:
> decline it, fail it, or **invent a verdict**. The third scores as a pass and proves nothing,
> so the suite has to make declining available — otherwise it has created an incentive to
> fabricate.
>
> A declined case is also more informative than a failure. *"This implementation has no intent
> control"* is a clear statement about scope; *"this implementation got the intent case wrong"*
> suggests a bug that does not exist.

**Vectors:** conformance case CONF-005

## AEGS-0.1-CONF-4 · A level is claimed only when every case in it passes

An implementation **MUST NOT** claim a level for which any case is unpassed.

> No partial credit, and the reason is that a partial level is uninterpretable. *"aegs-2, four of
> five"* tells a reader nothing they can rely on, because they do not know which one failed and
> cannot know whether it was the one they care about.
>
> An implementation is free to report per-case results, and should. What it may not do is
> describe the level as claimed.

**Vectors:** conformance case CONF-004

## AEGS-0.1-CONF-5 · The scorer imports no implementation

A conformance suite **MUST** score records rather than calling into the implementation under
test.

> A suite that imports the thing it tests can only ever test that thing. Scoring *records* means
> an implementation in any language, of any architecture, can be assessed by writing one adapter
> — and it means the suite cannot accidentally depend on an internal behaviour that happens to
> be shared.
>
> The corollary is that a conformance suite **ships separately from its subject**. A suite
> bundled with the implementation it certifies is not a conformance suite; it is that
> implementation's test directory with an ambitious name.

**Vectors:** conformance case CONF-001

## AEGS-0.1-CONF-6 · A conformance claim asserts nothing about correctness

A conformance claim **MUST NOT** be described as establishing security, regulatory compliance,
or the accuracy of any score an implementation produces.

> The clause exists because the claim will be quoted, and it will be quoted by someone who wants
> it to mean more than it does.
>
> What conformance establishes: the required controls ran, the record says so, and refusals were
> attributed to the control that caused them. That is genuinely useful and it is narrow.
>
> What it does not establish, each of which is a real gap rather than a legal hedge:
>
> * **Security.** The reference implementation passes every case and has three open red-team findings. It resists prose attacks and did not resist a minus sign.
> * **Compliance.** No clause here maps to any regulation. The crosswalk places controls *relative* to frameworks and says explicitly that no row asserts compliance.
> * **Score accuracy.** A risk score's weights are an implementation's own choice, and the reference implementation's have never been validated against outcomes. Conformance requires a score to be produced and recorded, not to be right.
> * **AML effectiveness.** Not addressed at all. Demonstrating it needs labelled financial-crime data this project does not have.
> * **Independent review.** At the time of writing, every case, threat and label in this specification was written by the author of the system under test.

**Vectors:** conformance case CONF-006

## AEGS-0.1-CONF-7 · A declaration may be published, including a failing one

Anyone **MAY** run the conformance suite against any implementation and publish the result.

A published declaration **MUST** include the specification version, the profile, and the
per-case outcomes.

> Publishing failures is what makes publishing passes worth anything. A registry containing only
> successes is a marketing channel, and readers learn to discount it; one containing both is
> evidence.
>
> Requiring per-case outcomes rather than a summary is the same point at a smaller scale. A
> declaration reading *"aegs-1: claimed"* asks to be trusted; one listing seven cases and their
> outcomes can be checked, and disputed.

**Vectors:** conformance case CONF-006

---

## The open question this section exists to answer

Stated plainly, because it is the most important fact about this specification's current status:

**No implementation written by anyone other than this specification's author has ever been
scored.**

Every case, every threat, every label was written by the person who wrote the system under test.
That is a conflict of interest, not a formality, and it is the reason the test vectors exist —
they are runnable against a half-built implementation in any language, before there is anything
to score.

Until an independent implementation has been assessed, a conformance claim here demonstrates
internal consistency and nothing about interoperability.
