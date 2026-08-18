"""AEGS-CONF — score any implementation against the same cases.

This is the step that makes AEGS engineering rather than prose. Until two
implementations can run identical tests and be compared, "standard" is an
aspiration.

## What the runner knows

Cases, adapters, and the AEGS Decision Record schema. **Nothing else.** It imports
no engine, no governance layer, no AEGL. An adapter hands it a Decision Record; it
scores that record against the case's expectation.

If scoring ever needs something from `tesoro`, the boundary has moved to the wrong
place and the suite has stopped being a conformance test of a *standard*.

## The rule that makes a pass mean something

**A case passes only if the verdict *and* the attribution match.**

An implementation that returns REJECT for the budget case because its risk engine
happened to fire has not demonstrated budget enforcement — it was right by accident,
and the same case shaped slightly differently would sail through. Counting that as a
pass lets an implementation certify a control it does not have, which is precisely
what a conformance suite exists to prevent.

So `WRONG_REASON` is its own outcome. It is reported separately from both PASS and
FAIL, because it is neither: the implementation refused, but not for the reason the
case is testing.

## Why attribution rather than reason codes

Expecting an exact reason string would make the suite a test of AEGL's private
vocabulary. The Decision Record's `authorization.decidingEngine` names the *control*
that determined the verdict — treasury, policy, intent, identity, risk, sanctions —
and a second implementation can populate that honestly without copying our codes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

CASES_DIR = Path(__file__).resolve().parent / "cases"

#: The Decision Record schema. Kept as a path rather than a URL on purpose: scoring must work
#: offline, and a runner that fetches its schema over the network **can be made to pass by a
#: network** — an outage, a proxy, or a captive portal returning something plausible.
#:
#: Two candidate locations, in this order, and the order is the whole point:
#:
#: 1. `conformance/_schemas/` — inside the package, which is where an *installed*
#:    `aegs-conformance` finds it;
#: 2. `../schemas/` — the standard's own copy, which is where it lives when the suite is run
#:    from a checkout of this repository.
#:
#: The second was the only one, as `parents[1] / "schemas"`. From a wheel that resolves to
#: `site-packages/schemas/`, which does not exist — the same defect as `tesoro`'s F-A1, in the
#: package whose whole job is to be installed by somebody else. Found before publishing rather
#: than by a third party's traceback, and only because packaging it was attempted at all.
def _find_schema() -> Path:
    """Where the Decision Record schema is, or a message saying why there is none."""
    here = Path(__file__).resolve().parent
    for candidate in (
        here / "_schemas" / "decision-record-0.1.json",
        here.parents[0] / "schemas" / "decision-record-0.1.json",
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "the Decision Record schema is not beside this suite. Looked in "
        f"{here / '_schemas'} (an installed package) and "
        f"{here.parents[0] / 'schemas'} (a source checkout). Without it, records cannot be "
        "validated and a conformant verdict inside a malformed record would score as a pass."
    )


SCHEMA_PATH = _find_schema()


class Outcome(str, Enum):
    PASS = "PASS"
    #: Refused, but by a different control than the case is testing. Not a pass:
    #: the implementation was right by accident.
    WRONG_REASON = "WRONG_REASON"
    FAIL = "FAIL"
    #: The adapter declined the case. Honest, and better than a fabricated verdict.
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    #: The record did not validate against the AEGS schema.
    INVALID_RECORD = "INVALID_RECORD"


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    level: str
    control: str
    rationale: str
    setup: dict[str, Any]
    action: dict[str, Any]
    expect: dict[str, Any]
    #: Specification clauses this case checks, if any. Optional, and read by
    #: `tools/lint_normative.py` so a clause whose requirement is structural — not
    #: expressible as an input/output vector — can still be shown to have a test.
    #: EVID-8 is the first: "records are derived from the journal, not written twice"
    #: has no input/output pair that demonstrates it, because a second write path could
    #: produce identical output for whatever cases you happened to test.
    clauses: tuple[str, ...] = ()

    @classmethod
    def load_all(cls, directory: Path = CASES_DIR) -> list["Case"]:
        cases = []
        for path in sorted(directory.glob("CONF-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if "clauses" in data:
                data["clauses"] = tuple(data["clauses"])
            known = {f for f in cls.__dataclass_fields__}
            unknown = sorted(set(data) - known)
            if unknown:
                raise SystemExit(
                    f"{path.name}: unknown field(s) {unknown}. A case with a field the "
                    "runner ignores is a case that silently tests less than it appears to."
                )
            cases.append(cls(**data))
        return cases


class Adapter(Protocol):
    """What an implementation must provide to be scored.

    One method. Everything else about the implementation is its own business, which
    is the point: the suite tests what a governed action *produces*, not how.
    """

    name: str

    def run_case(self, case: Case) -> dict[str, Any] | None:
        """Set up, decide, and return an AEGS Decision Record.

        Return `None` for a case this implementation cannot express. Declining is
        an honest answer and scores as NOT_IMPLEMENTED; inventing a verdict would
        score as a pass while proving nothing.
        """
        ...


@dataclass
class Result:
    case: Case
    outcome: Outcome
    got_decision: str | None = None
    got_engine: str | None = None
    detail: str = ""
    problems: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case": self.case.id,
            "title": self.case.title,
            "level": self.case.level,
            "control": self.case.control,
            "outcome": self.outcome.value,
            "expected": self.case.expect,
            "gotDecision": self.got_decision,
            "gotEngine": self.got_engine,
            "detail": self.detail,
            "problems": self.problems,
        }


def _expected_decisions(expect: dict[str, Any]) -> list[str]:
    if "decision" in expect:
        return [expect["decision"]]
    return list(expect.get("decisionIn") or [])


def _expected_engines(expect: dict[str, Any]) -> list[str]:
    """Empty means the case does not constrain attribution.

    Used by the happy path: an APPROVE has no refusing control, so demanding one
    would be nonsense.
    """
    if "decidingEngine" in expect:
        return [expect["decidingEngine"]]
    return list(expect.get("decidingEngineIn") or [])


def validate_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check a record against the AEGS schema, without importing an implementation."""
    try:
        import jsonschema  # noqa: PLC0415
    except ImportError:
        return True, ["jsonschema not installed; schema validation skipped"]

    validator = jsonschema.Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    )
    problems = [
        f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    ]
    return (not problems), problems


def score(case: Case, record: dict[str, Any] | None) -> Result:
    """One case, one record, one outcome."""
    if record is None:
        return Result(
            case, Outcome.NOT_IMPLEMENTED,
            detail="the adapter declined this case",
        )

    valid, problems = validate_record(record)
    if not valid:
        return Result(
            case, Outcome.INVALID_RECORD,
            detail="the record does not satisfy the AEGS schema",
            problems=problems,
        )

    decision = record.get("decision")
    engine = (record.get("authorization") or {}).get("decidingEngine")
    wanted_decisions = _expected_decisions(case.expect)
    wanted_engines = _expected_engines(case.expect)

    if decision not in wanted_decisions:
        return Result(
            case, Outcome.FAIL, decision, engine,
            detail=f"expected {' or '.join(wanted_decisions)}, got {decision}",
        )

    # The verdict is right. Was it right for the right reason?
    if wanted_engines and engine not in wanted_engines:
        return Result(
            case, Outcome.WRONG_REASON, decision, engine,
            detail=(
                f"verdict {decision} is correct, but it was attributed to "
                f"`{engine}` rather than {' or '.join(wanted_engines)} -- the "
                "control this case tests did not cause the refusal"
            ),
        )

    return Result(case, Outcome.PASS, decision, engine)


def run(adapter: Adapter, cases: list[Case] | None = None) -> list[Result]:
    """Score one implementation. An adapter that raises fails that case, not the run."""
    results = []
    for case in cases or Case.load_all():
        try:
            record = adapter.run_case(case)
        except Exception as exc:  # noqa: BLE001 - one broken case must not end the run
            results.append(
                Result(case, Outcome.FAIL,
                       detail=f"adapter raised {type(exc).__name__}: {exc}")
            )
            continue
        results.append(score(case, record))
    return results


def report(adapter_name: str, results: list[Result]) -> dict[str, Any]:
    """The machine-readable verdict, plus what an implementation may claim."""
    counts = {o.value: sum(1 for r in results if r.outcome is o) for o in Outcome}
    passed = [r for r in results if r.outcome is Outcome.PASS]

    levels: dict[str, dict[str, Any]] = {}
    for level in sorted({r.case.level for r in results}):
        in_level = [r for r in results if r.case.level == level]
        ok = [r for r in in_level if r.outcome is Outcome.PASS]
        levels[level] = {
            "cases": len(in_level),
            "passed": len(ok),
            # A level is claimed only when every case in it passes. Partial
            # conformance is not conformance -- it is a list of things that happen
            # to work.
            "claimable": len(ok) == len(in_level),
        }

    return {
        "aegsVersion": "0.1",
        "suite": "AEGS-CONF",
        "implementation": adapter_name,
        "cases": len(results),
        "passed": len(passed),
        "counts": counts,
        "levels": levels,
        "results": [r.as_dict() for r in results],
    }


def format_report(data: dict[str, Any]) -> str:
    icons = {
        "PASS": "PASS", "WRONG_REASON": "REASON?", "FAIL": "FAIL",
        "NOT_IMPLEMENTED": "N/IMPL", "INVALID_RECORD": "SCHEMA",
    }
    lines = [
        f"  AEGS-CONF {data['aegsVersion']}   implementation: {data['implementation']}",
        "  " + "-" * 76,
    ]
    for r in data["results"]:
        lines.append(
            f"  {r['case']:9} {icons.get(r['outcome'], r['outcome']):8} "
            f"{r['level']:7} {r['control']:10} {r['title'][:32]:32}"
        )
        if r["detail"]:
            lines.append(f"            {r['detail'][:88]}")
    lines += [
        "  " + "-" * 76,
        f"  {data['passed']}/{data['cases']} passed   "
        + "   ".join(
            f"{k.lower()} {v}" for k, v in data["counts"].items() if v and k != "PASS"
        ),
        "",
        "  Levels claimable:",
    ]
    for level, info in data["levels"].items():
        mark = "yes" if info["claimable"] else "no"
        lines.append(
            f"    {level:8} {info['passed']}/{info['cases']}  claimable: {mark}"
        )
    if any(r["outcome"] == "WRONG_REASON" for r in data["results"]):
        lines += [
            "",
            "  A WRONG_REASON is not a pass. The verdict was right and the control",
            "  under test did not cause it -- the same case shaped differently would",
            "  not be refused.",
        ]
    return "\n".join(lines)
