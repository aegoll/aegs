# Contributing to AEGS

A standard without a change process is a document. This is the process.

By contributing you agree your work is licensed per the directory it lands in — CC-BY-4.0
for specification text, Apache-2.0 for code. See [`LICENSES.md`](LICENSES.md).

---

## The shape of a change

Four kinds, with different bars.

| Kind | Example | Bar |
|---|---|---|
| **Editorial** | typo, clarified sentence, broken link | PR, no issue needed |
| **Clarification** | a normative statement that two readers read two ways | issue first, then PR. Must state both readings |
| **Extension** | a new control, a new binding, a profile addition | issue → discussion → PR, with vectors |
| **Breaking** | changes what a conformant implementation must do | issue → discussion → PR → version bump, with a migration note |

## Before you write a specification change

Open an issue that answers three questions:

1. **What can a conformant implementation do today that it should not, or not do that it should?**
2. **Why is this not expressible in an existing control?** A new control is a real cost — every implementation pays it forever.
3. **What breaks if we do nothing?** If the answer is "nothing yet", the change is early.

## Rules for specification text

Non-negotiable, because they are what makes the spec testable rather than aspirational.

- **RFC 2119 language** — MUST, MUST NOT, SHOULD, MAY — used precisely, not for emphasis.
- **Every MUST needs a test.** A normative statement with no conformance case or test vector
  is a wish. CI fails a `MUST` that has no cross-reference.
- **Absent ≠ not-run ≠ unknown ≠ zero.** Four distinct states. Any new field must say which
  of the four its omission means, and must never permit zero-filling for a control that did
  not run.
- **Every control may only narrow a verdict.** Nothing in AEGS may let a control widen a
  verdict another one set.
- **Money is integer atomic units.** No floats, anywhere, in any example. Conversions state
  their rounding mode explicitly rather than inheriting a language default.
- **Order matters where attribution matters.** The final verdict is order-independent; the
  attributed control is not, and conformance scores attribution.
- **No compliance claims.** AEGS supports compliance work; it does not confer it. No row, no
  sentence, no README says otherwise.
- **Rail-independent by default.** Anything that only makes sense on one rail belongs in
  `bindings/`, not in a core schema.

## Rules for schemas

- JSON Schema **Draft 2020-12**.
- `additionalProperties: false` unless there is a stated reason.
- Every schema carries `aegsVersion`.
- Every schema has at least one example under `schemas/examples/`. A schema with no example
  gets read three ways.
- Prefer a content hash to a label for any `version` field. Labels get reused across edited
  rules; hashes cannot.
- A field that can never be populated is worse than an absent one — it claims a capability.
  This has happened here before.

## Rules for vectors

Every vector is one JSON file naming: the normative clause it checks, the input, and the
expected **verdict, attributed control, resulting envelope state, and record hash** — all
four. A vector that checks only the verdict cannot catch the most common real defect, which
is a correct answer reached with no evidence the control existed.

Sequence and concurrency vectors must be *executable*, not merely declared. A single-request
runner cannot express structuring or velocity evasion, which are exactly the attacks that
matter.

## Rules for bindings

State the unit of account, atomic precision, settlement finality semantics, counterparty
identity shape, reversibility, and what "vendor" means on that rail. Bind to **behaviour and
digests, not wire shape** — the rails' own field placement moves, and a binding pinned to it
breaks on someone else's merge.

## Conformance and the crosswalk

- Conformance cases are **data, not code**, and the runner imports no implementation.
- Adding a case means adding it for every level it affects, and saying what previously-passing
  implementations now fail.
- Crosswalk rows need a **primary source**. A row from a secondary summary is labelled as
  such; a row with no source is labelled **UNSOURCED** and stays that way until sourced.
  Do not tidy an unsourced row into a sourced-looking one.
- Legal readings need a qualified reviewer before external use. Contributors are welcome to
  draft; nobody here is a substitute for that review.

## Versioning

`AEGS 0.1` moves independently of any implementation's version. Every record and declaration
states both. Patch: editorial. Minor: additive, backwards-compatible for conformant
implementations. Major: anything that changes what conformance requires.

Errata are published rather than silently corrected. An errata list is a sign of health.

## What gets declined

- A control that only one implementation would ever use.
- Anything requiring a network call inside the decision path without specifying what happens
  when it is unreachable. `not-run` is an answer; `pass` is not.
- A rule language. AEGS specifies that policy be identifiable and content-addressed, not how
  it is written — two implementations may express the same intent very differently.
- Compliance claims, however hedged.
