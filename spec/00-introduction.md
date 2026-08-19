# AEGS 0.1 — introduction and conventions

**Autonomous Economic Governance Standard**, version 0.1. Draft.

An open specification for the layer that decides whether an autonomous agent may spend, and
for the evidence it must produce.

The claim, in one line: **autonomous payment should not mean unrestricted payment.**

---

## AEGS-0.1-INTRO-1 · Scope

This specification describes a **buyer-side** governance layer: the component that decides,
before a payment is attempted, whether it should happen at all — and records why.

Payment protocols answer *how* an agent pays. AEGS answers *whether it should*. The two are
deliberately separate concerns, and at least one payment protocol says so in its own
specification text: x402's `auth-hints` extension states that spend limits, budgets and
policy enforcement "remain separate concerns".

## AEGS-0.1-INTRO-2 · Non-goals

AEGS does **not**:

- define a payment protocol, settlement mechanism, or wire format for moving money;
- specify a rule language. Two conformant implementations may express the same policy very differently, and a crosswalk between them is a policy question rather than a schema one;
- confer regulatory compliance. It is intended to *support* compliance work. No clause here, and no row in the crosswalk, says an implementation complies with anything;
- require any particular programming language, storage engine, or deployment shape.

## AEGS-0.1-INTRO-3 · Requirement levels

*Constrains this document, not implementations.*

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are to be
interpreted as described in RFC 2119. They appear in capitals when used normatively and in
lower case when used as ordinary English.

## AEGS-0.1-INTRO-4 · Clause identifiers and testability

*Constrains this document, not implementations.* Enforced by `tools/lint_normative.py`,
which is this clause's own test.

Every normative statement carries an identifier of the form:

```
AEGS-0.1-<SECTION>-<n>
```

**Every clause containing a MUST or MUST NOT MUST be referenced by at least one conformance
case or test vector.** This is enforced by `tools/lint_normative.py` in CI, not by review.

The reason is blunt: a MUST with no test is a wish. A specification whose requirements
cannot be checked produces implementations that claim conformance and disagree about what it
means, which is worse than having no specification — the disagreement is now invisible.

A clause with no `MUST` needs no test. It is prose, and prose is allowed to explain.

## AEGS-0.1-INTRO-4a · Clause identifiers are permanent

*Constrains this document, not implementations.*

The general form of a clause identifier is:

```
AEGS-<version>-<SECTION>-<n>[<suffix>]
```

`<version>` is the version of this specification in which the clause was **introduced**. It is
**not** the version of the document that contains it. [INTRO-4](#aegs-01-intro-4--clause-identifiers-and-testability)
writes the form with a literal `0.1` because every clause published so far was introduced in
0.1; that is an instance of this rule, not an exception to it.

A clause identifier, once published, **MUST NOT** be renumbered, restamped with a later version,
or reused for a different requirement.

It follows that a future release of this specification will contain clauses stamped with earlier
versions, and that the set of `AEGS-0.1-*` identifiers will be the same set then as it is now.
Reading a `0.1` stamp in a later document as "outdated" will be a misreading: it will mean
"unchanged since 0.1", which is the stronger statement.

The optional lowercase `<suffix>` exists so that a clause can be inserted between two existing
ones — `INTRO-4a` sits after `INTRO-4` — without renumbering the clauses after it.

> Written down because it was previously a decision recorded only in a tool. The comment above
> the clause-matching regex in `tools/check_vectors.py` read *"the optional lowercase suffix lets
> a clause be inserted without renumbering its neighbours — renumbering breaks every citation"*,
> and nothing in the specification said so. A rule enforced by a regex and stated nowhere is a
> rule the next editor breaks in good faith.
>
> The cost of getting this wrong is not cosmetic. Clause identifiers are what a conformance
> report cites, what a test vector's `clause` field names, and what a security advisory points
> at. Restamping all ninety 0.1 clauses as `0.2` on a future release would invalidate 151
> vector citations and every conformance result ever published, in exchange for nothing.

## AEGS-0.1-INTRO-5 · Conformance vocabulary

| Term | Means |
|---|---|
| **implementation** | Software that makes governance decisions and emits AEGS records |
| **control** | One of the thirteen named capabilities in [`02-controls.md`](02-controls.md) |
| **profile** | A conformance contract naming the controls an implementation is required to exercise, and the evidence it is required to emit. See [`profiles/`](../profiles/README.md) |
| **policy** | What the rules actually are. Written by whoever deploys an implementation, not by this standard |
| **decision** | One evaluation of one proposed economic action, producing a verdict |
| **verdict** | One of `APPROVE`, `REVIEW`, `ESCALATE`, `REJECT` |
| **channel** | `internal` (what the agent spends thinking) or `external` (what it pays out) |
| **counterparty** | The party that would receive the payment |
| **atomic units** | The smallest indivisible unit of the asset. See [`05-arithmetic.md`](05-arithmetic.md) |

**Profile and policy are not the same thing**, and conflating them causes trouble later. A
profile is written by this standard and says which controls must exist. A policy is written
by a deployment and says what the rules are. An implementation enforces a profile; it
executes a policy.

## AEGS-0.1-INTRO-6 · What is not established

Stated in the specification itself rather than in a footnote, because a standard that
overclaims is worse than one that admits its edges.

- **AML/CFT effectiveness is not addressed.** Three controls — `AMLAssessment`, `ComplianceAssessment`, `IncidentRecord` — are defined as interfaces with no requirement above `OPTIONAL` in any profile, because no known implementation has an engine behind them. Requiring something unimplementable does not raise the bar; it makes the bar decorative.
- **Sanctions screening is not specified as a matching problem.** The reference implementation carries a boolean on a counterparty object: no list, no matching algorithm, no jurisdiction model.
- **The FATF Travel Rule is a known gap.** AEGS carries no originator or beneficiary data, which matters for any deployment moving value between regulated parties. Named rather than quietly omitted.
- **No independent implementation has been scored.** The conformance suite has, at the time of writing, only ever scored implementations written by this specification's own author. That is the largest open question about this document, and it is the reason the vectors exist.

## Documents

| | |
|---|---|
| [`00-introduction.md`](00-introduction.md) | this document |
| [`05-arithmetic.md`](05-arithmetic.md) | money: atomic units, rounding, boundaries, refusals |
| `01`–`04`, `06`–`12` | model, controls, channels, verdicts, four states, evidence, identity, profiles, decision path, conformance, security. **Not yet written** |
| [`../profiles/README.md`](../profiles/README.md) | the profile mechanism |
| [`../schemas/`](../schemas/) | the thirteen interface objects, as JSON Schema |
| [`../vectors/README.md`](../vectors/README.md) | language-neutral test vectors |

Sections are being written alongside their vectors, one family at a time, rather than as
prose first and tests later. That ordering is deliberate: writing the vector is what
discovers whether a `MUST` is actually checkable.
