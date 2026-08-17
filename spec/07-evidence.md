# AEGS 0.1 — evidence

The record a governed decision leaves behind, and precisely what that record proves.

This is the section where overclaiming would do the most damage. A governance layer's
evidence is what an auditor relies on, and an implementation that says *tamper-proof* when it
means *tamper-evident against some tampering* has misled the one person the record exists
for. So this section specifies the guarantee **and** names the gap, in the normative text
rather than in a security note nobody reads.

Prerequisite reading: [`00-introduction.md`](00-introduction.md) for requirement levels,
[`05-arithmetic.md`](05-arithmetic.md) for how amounts serialise,
[`04-verdicts.md`](04-verdicts.md) for what a record must attribute.

---

## AEGS-0.1-EVID-1 · The journal is append-only

An implementation **MUST** record every decision as a new entry, and **MUST NOT** modify or
remove an entry once written.

A later event about an earlier decision — a settlement, a human override, a dispute —
**MUST** be recorded as a new entry that references the earlier one.

> Editing in place destroys the only thing a journal is for. A record that can be updated
> tells you what somebody currently believes; a record that can only be appended to tells you
> what happened, which is a different and much more useful claim.
>
> The second sentence is the one implementations get wrong. A settlement arriving after an
> authorisation is *new information*, and writing it into the authorisation entry would make
> that entry describe a decision nobody made — the verdict and the outcome fused into one row
> with no way to tell which came first, or whether the state at decision time was what the
> record now says it was.

**Vectors:** `evidence/append-*`

## AEGS-0.1-EVID-2 · Each entry commits to its predecessor

An implementation **MUST** include, in every entry, a hash committing to the immediately
preceding entry.

The first entry **MUST** commit to a fixed, declared genesis value.

> This is what makes an edit detectable. Change an entry and its hash changes; every
> subsequent entry committed to the old hash, so the mismatch is visible at the point of
> the change. Remove an entry from the middle and the link across the gap fails the same way.
>
> A declared genesis matters because without one the first entry has nothing to commit to,
> and an implementation could quietly drop the entire journal and start again with a
> plausible-looking chain of one.

**Vectors:** `evidence/chain-*`

## AEGS-0.1-EVID-3 · Hashing uses a canonical serialisation

An implementation **MUST** compute an entry's hash over a canonical serialisation of that
entry.

The canonical form **MUST** have object keys sorted, **MUST** omit insignificant whitespace,
and **MUST** serialise monetary amounts as specified in [ARITH-9](05-arithmetic.md).

> Every one of those is a hash-changing detail, which is why they are requirements rather
> than advice. `{"a":1,"b":2}` and `{"b":2,"a":1}` are the same object and different bytes.
> `{"a": 1}` and `{"a":1}` likewise. `2.5` and `"2.500000"` likewise, and that one also loses
> precision on the way through a parser.
>
> Two implementations that agreed on every verdict and disagreed on any of these would
> produce different hashes for identical decisions — so their journals could never be
> compared, and neither could verify the other's evidence. A specification that fixed the
> decisions and left the bytes open would have standardised the easy half.

**Vectors:** `evidence/canonical-*`

## AEGS-0.1-EVID-4 · Stored form need not be the canonical form

An implementation **MAY** store an entry in any form from which the canonical serialisation
can be reconstructed.

> Worth stating so that implementers do not over-constrain themselves. The hash is computed
> over the canonical form; verification reconstructs that form from whatever was stored and
> rehashes it. So a journal may be stored with keys in any order, pretty-printed, in a
> database, or in a columnar format — none of it affects verification, provided the
> reconstruction is faithful.
>
> The reference implementation writes its journal with compact separators and *unsorted*
> keys, and verifies correctly, because the reader parses the entry back into a mapping and
> canonicalises before hashing. That is conformant, and it is a useful demonstration that
> this clause is real rather than theoretical.

**Vectors:** `evidence/canonical-storage-*`

## AEGS-0.1-EVID-5 · The hash must be strong enough to be worth computing

An implementation **MUST** use a cryptographic hash function with no known practical
collision or second-preimage attack.

Where an implementation truncates the hash output, the retained length **MUST** be at least
128 bits.

An implementation **MUST** declare its hash function and retained length.

> The truncation limit is the substance here, and writing this clause is what caught the
> reference implementation retaining **64 bits** — 16 hexadecimal characters, in five
> separate places that agreed with each other only by luck. It now retains 128, routed
> through one constant. The clause was not lowered to accommodate the implementation; the
> implementation was raised to meet it, which was cheap because nothing published yet
> depended on the old hashes and would have been a migration later.
>
> The arithmetic is what decides it. Altering an entry undetectably requires a second
> preimage — a different payload with the same truncated hash. At 64 bits that is 2⁶⁴ work,
> which a determined attacker with commodity GPUs can reach in months. At 128 bits it is
> 2¹²⁸, which nobody reaches. The difference between those two numbers is the difference
> between *evidence* and *evidence-shaped*.
>
> Collision resistance is the less interesting half: a birthday collision at 64 bits needs
> around 4 × 10⁹ entries, which no realistic journal reaches. It is second-preimage
> resistance that a tamper-evidence claim depends on, and truncation attacks it directly.
>
> The declaration requirement exists because an auditor cannot assess a chain whose strength
> is unstated. "Hash-chained" without a function and a length is a description of a shape,
> not of a guarantee.

**Vectors:** `evidence/strength-*`

## AEGS-0.1-EVID-6 · A hash chain does not detect truncation, and an implementation must say so

An implementation **MUST NOT** claim that its evidence is tamper-proof, or that its chain
detects all tampering.

Where an implementation's chain has no external anchor, it **MUST** state that truncation of
the journal's tail is undetectable.

> **Any prefix of a valid chain is itself a valid chain.** Remove the last N entries and
> every remaining link still verifies, every hash still matches, and verification reports
> success. So an agent that was refused can delete the refusal, and the evidence is
> internally consistent about a history that did not happen.
>
> Editing is caught. Middle-deletion is caught. Reordering is caught. **Truncation is not**,
> and no amount of internal linking fixes it, because the missing information is *that there
> was more*.
>
> The clause requires the disclosure rather than the fix, deliberately. Fixing it needs an
> external anchor — a value published somewhere the agent cannot reach, committing to the
> chain's length and head. That is a real deployment cost, and an implementation may
> reasonably decide not to pay it. What it may not do is describe the result as tamper-proof.
>
> **What does not work, and looks like it does:** writing the current head and length to a
> second file beside the journal. An attacker who can truncate the journal can rewrite that
> file, so it defends against nothing while making the system appear anchored. This is worth
> naming explicitly because it is the first fix everyone proposes, and shipping it would be
> worse than shipping the honest gap.

**Vectors:** `evidence/truncation-*`

## AEGS-0.1-EVID-7 · Verification is total and reports every problem

An implementation **MUST** verify every entry in a chain rather than stopping at the first
problem, and **MUST** report every problem it finds.

> A chain with four broken links is a different situation from one with a single edit, and an
> operator needs to know which they have before deciding whether to trust anything in the
> journal. Stopping at the first failure also makes repeated verification a guessing game:
> fix one problem, discover the next, with no idea how many remain.
>
> This mirrors the same requirement for policy validation and envelope evaluation, and for
> the same reason — a check that reports one fault at a time turns diagnosis into a sequence
> of round trips.

**Vectors:** `evidence/verify-*`

## AEGS-0.1-EVID-8 · A record is projected from the journal, never written twice

Where an implementation emits AEGS records, it **MUST** derive them from the journal rather
than writing them by a separate path.

> Two write paths drift, and the drift is invisible: the journal says one thing, the emitted
> record says another, and both look authoritative. Worse, a second path can emit a record
> for a decision the journal never recorded, which is the exact shape of the evidence an
> auditor is most interested in and least able to trust.
>
> Deriving also makes a defect in the projection *recoverable*. If a projection is wrong, the
> journal still holds the truth and every record can be regenerated. If the record was
> written independently, the mistake is the only copy.

**Vectors:** `evidence/projection-*`

## AEGS-0.1-EVID-9 · A control's absence is recorded, not implied

An implementation **MUST** record, for each control a profile requires, whether it was
exercised — and **MUST NOT** omit a control's field to indicate that it did not run.

Where a control did not run, the record **MUST** distinguish that from the control having run
and found nothing.

> The four-state rule, in the place it does the most work. A record that simply lacks a
> sanctions field could mean the screening ran and found nothing, or that no screening
> exists, or that one exists and failed. An auditor cannot tell, and the most favourable
> reading is the one a reader will assume.
>
> This is why the schemas require an object to be **omitted** rather than zero-filled when
> the control does not exist, and why a control that could not run reports `not-run` rather
> than a score of zero. An unmeasured vendor history rendered as `0` once made every advisor
> in the reference implementation treat established counterparties as strangers — the same
> bug, one layer down.

**Vectors:** `evidence/fourstate-*`

---

## Known non-conformance in the reference implementation

Stated here rather than in a separate document, because a specification whose own reference
implementation fails a clause should say so where the clause is.

| Clause | Status |
|---|---|
| [EVID-5](#aegs-01-evid-5--the-hash-must-be-strong-enough-to-be-worth-computing) | **Now conforms.** It retained 64 bits when this clause was written, and was raised to 128 rather than the clause being lowered |
| [EVID-6](#aegs-01-evid-6--a-hash-chain-does-not-detect-truncation-and-an-implementation-must-say-so) | Conforms *by disclosure*, not by fix. The truncation gap is stated in the CLI's output, in the report, and in the project's limitations document. It remains a real gap |

Every clause in this section is satisfied. That is a weaker statement than it sounds: EVID-6
is satisfied by **admitting** a weakness rather than removing one, and a reader assessing this
implementation's evidence should treat the truncation gap as open.
