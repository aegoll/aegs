# AEGS 0.1 — arithmetic

How money is represented, converted, and refused.

This is the shortest section in the specification and the one most likely to cause two
implementations to disagree. Every clause here exists because a real defect or a real
divergence made it necessary, and the two that were live vulnerabilities are named as such.

Prerequisite reading: [`00-introduction.md`](00-introduction.md) for requirement levels and
clause identifiers.

---

## AEGS-0.1-ARITH-1 · Money is integer atomic units

An implementation **MUST** represent monetary amounts internally as integers in the
**atomic units** of the asset — the smallest indivisible unit the asset defines.

An implementation **MUST NOT** use a binary floating-point type to hold, compare, or
accumulate a monetary amount at any point in the decision path.

> Two reasons, and the second is the one people underestimate. Floating point cannot
> represent most decimal fractions exactly, so sums drift. But worse: the drift is
> *asymmetric across languages*. Python has a decimal type in its standard library and
> JavaScript does not, so an implementation in each, both written carefully, will produce
> different totals from the same inputs unless both are working in integers. Integer atomic
> units is the only representation that makes two implementations comparable at all.

The number of decimal places is a property of the asset, not of this specification. USDC has
six; an implementation binding a different asset uses that asset's precision, declared in
the rail binding.

**Vectors:** `arithmetic/atomic-*`

## AEGS-0.1-ARITH-2 · Conversion happens once, at the boundary

An implementation **MUST** convert a decimal amount to atomic units at the point the amount
enters the layer, and **MUST NOT** convert back and forth during evaluation.

> A value converted twice has been rounded twice. Round-tripping inside the engines is how a
> limit of exactly $10.00 starts rejecting a payment of exactly $10.00.

**Vectors:** `arithmetic/roundtrip-*`

## AEGS-0.1-ARITH-3 · The rounding mode is specified, not inherited

When a decimal amount carries more precision than the asset's atomic unit can express, an
implementation **MUST** round **half away from zero** (commonly *half-up*) at the atomic
digit.

> Specified explicitly because every language's default is different and none of them is
> wrong in isolation. Python's `Decimal` defaults to half-even; `round()` in Python 3 is
> half-even; JavaScript's `Math.round` is half-up for positives and half-down for negatives.
> An implementation that inherits its language's default has made a decision it did not
> know it was making, and two such implementations disagree on exactly the inputs a test
> suite is least likely to contain.
>
> Half-up rather than half-even because it is the rule a human checking the arithmetic by
> hand will apply, and a governance record that a person cannot verify by hand is worth less
> than one they can.

**Vectors:** `arithmetic/rounding-*`

## AEGS-0.1-ARITH-4 · A negative amount is refused, not normalised

An implementation **MUST** refuse an amount below zero, and **MUST NOT** normalise it,
take its absolute value, or evaluate it as a spending decision.

The refusal **MUST** occur before any envelope, policy or risk evaluation.

> **This was a live vulnerability, not a hypothetical.** A **-$1000 request was approved** by
> the reference implementation. Every envelope check asks `amount <= headroom`, and any
> negative number satisfies that — so a single minus sign inverted the entire treasury and
> the layer approved it. Found as RT-NUM-001.
>
> Refusing rather than returning a verdict is the substance of this clause. A negative price
> is not a spending decision to be weighed; it is not money. An implementation that quietly
> normalised it to a positive amount would be inventing an intent the caller never
> expressed, and one that evaluated it would be doing arithmetic whose result is
> meaningless.
>
> The ordering requirement matters as much as the refusal. If a negative reaches an envelope
> check first, the envelope reports *ok* and something downstream has to notice — which is
> precisely the failure mode that produced the original bug.

**Vectors:** `arithmetic/negative-*`

## AEGS-0.1-ARITH-5 · An unrepresentable magnitude is refused, not raised

An implementation **MUST** refuse an amount too large to represent, and **MUST** do so as a
governance refusal rather than as an unhandled error.

An implementation **MUST** declare its maximum representable amount.

> **Also a live vulnerability.** A 30-digit amount **crashed** the reference implementation
> rather than being refused by it: the decimal arithmetic raised from inside the engine, and
> a malformed request took down the component whose job was to reject it. Found as
> RT-NUM-004.
>
> The distinction between *refused* and *raised* is the whole clause. A refusal is a
> governance decision with a record; an exception is an outage. A layer that crashes on
> malformed input is a layer an attacker can remove from the path by sending it garbage —
> and if the surrounding system is built to fail open, removing the governance layer is the
> attack.

**Vectors:** `arithmetic/overflow-*`

## AEGS-0.1-ARITH-6 · Zero is a valid amount

An implementation **MUST** accept an amount of exactly zero and evaluate it normally.

> Not an edge case to be refused. A zero-amount action is how an implementation is asked
> "where do the envelopes stand" without spending anything, and refusing it would make
> envelope state unreadable without a side effect. It is also the correct amount for a free
> tier of a paid resource, which is a real shape.

**Vectors:** `arithmetic/zero`

## AEGS-0.1-ARITH-7 · A non-finite or unparseable amount is refused

An implementation **MUST** refuse an amount that is not a finite number, including infinity
and not-a-number, and **MUST** refuse a value it cannot parse as a decimal amount.

> `Infinity` satisfies no envelope and every comparison inconsistently; `NaN` makes every
> comparison false, including `NaN <= headroom`, which means an implementation checking
> `amount <= headroom` and refusing on false would reject it — and one checking
> `amount > headroom` and refusing on true would **approve** it. The same input, two
> reasonable implementations, opposite outcomes. That is exactly what a specification is
> for.

**Vectors:** `arithmetic/nonfinite-*`

## AEGS-0.1-ARITH-8 · Comparison is exact

An implementation **MUST** compare monetary amounts exactly, in atomic units, with no
tolerance or epsilon.

An amount exactly equal to a limit **MUST NOT** breach that limit.

> A tolerance is a hidden limit. If an implementation permits `amount <= limit + epsilon`,
> its real limit is `limit + epsilon` and its records say `limit`, which makes every
> reported envelope slightly false. Exact integer comparison has no need for tolerance,
> which is one of the reasons ARITH-1 requires integers.
>
> The equality rule is stated because it is the boundary a test suite most often omits and
> two implementations most often split on. A limit of ten dollars admits a payment of
> exactly ten dollars.

**Vectors:** `arithmetic/boundary-*`

## AEGS-0.1-ARITH-9 · Serialised amounts are decimal strings

When an amount appears in an AEGS record, an implementation **MUST** serialise it either as
an integer count of atomic units, or as a decimal string with the asset's full precision.

An implementation **MUST NOT** serialise a monetary amount as a JSON number.

> JSON has one numeric type and its usual mapping is a double. An amount written as
> `2.5` has already left the integer domain by the time a reader parses it, and two readers
> in two languages may not agree on what they got. A decimal string survives any parser
> unchanged.
>
> This clause also protects the evidence chain: record hashes are computed over serialised
> bytes, so a number formatted differently by two implementations produces a different hash
> for the same decision. See `07-evidence.md` (not yet written) for canonical serialisation.
>
> **Known divergence, recorded rather than resolved:** the reference implementation's
> journal currently writes `amountUsd` as a JSON number, and its Decision Record projection
> converts to a decimal string on the way out. The projection is conformant; the internal
> journal is not, and that is a defect in the implementation rather than a licence in the
> specification.

**Vectors:** `arithmetic/serialise-*`

---

## Reference values

Non-normative, and provided so an implementer can sanity-check a fresh implementation
before running the vectors.

| Input | Atomic (6 dp) | Note |
|---|---|---|
| `"0"` | `0` | ARITH-6 |
| `"0.000001"` | `1` | one atomic unit |
| `"0.0000005"` | `1` | half-up at the atomic digit, ARITH-3 |
| `"0.0000004"` | `0` | rounds down |
| `"2.50"` | `2500000` | |
| `"10"` | `10000000` | admits a limit of exactly `10000000`, ARITH-8 |
| `"-0.01"` | *refused* | ARITH-4 |
| `"1e30"` | *refused* | ARITH-5 |
| `"NaN"` | *refused* | ARITH-7 |

The reference implementation declares a maximum of `10**24` atomic units, which is
$10^18^ at six decimal places. That figure is an implementation declaration, not a
requirement of this specification.
