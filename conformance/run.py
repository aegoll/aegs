"""Run AEGS-CONF against an implementation.

    aegs-conformance --adapter aegoll
    aegs-conformance --adapter stub                        # proves the suite discriminates
    aegs-conformance --against my_layer.conformance:Adapter  # your own, no suite changes
    aegs-conformance --adapter aegoll --json --out report.json

**`--against` is the point of this file.** A conformance suite that only scores adapters listed
inside itself is not an instrument, it is a self-assessment: anyone outside would have to fork the
suite to be measured by it, and a forked instrument measures nothing anybody else can compare
against. `--against` takes `module:Class` and imports it from wherever the caller's environment
puts it, so scoring an implementation this project has never seen needs no edit here at all.

Exit codes are by **level achieved**, not merely pass/fail, because "did not reach AEGS-2" and
"failed AEGS-1" are different results and a CI gate should be able to tell them apart:

    0   every case passed
    1   AEGS-1 claimable, AEGS-2 not
    2   nothing claimable
    3   the suite could not run (bad adapter, implementation absent)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from runner import Case, format_report, report, run  # noqa: E402

#: Adapters that ship with the suite. Two, and both are here for a reason: `aegoll` is the
#: reference implementation, and `stub` exists to fail — a suite that has never scored anything
#: below full marks has not been shown to discriminate.
#:
#: This dict is a convenience, not the extension mechanism. Use `--against` for anything else.
ADAPTERS = {
    "aegoll": ("adapters.aegoll_adapter", "AegollAdapter"),
    "stub": ("adapters.stub_adapter", "StubAdapter"),
}

EXIT_ALL_PASSED = 0
EXIT_LEVEL_1_ONLY = 1
EXIT_NOTHING_CLAIMABLE = 2
EXIT_COULD_NOT_RUN = 3


def load_adapter(name: str) -> Any:
    """One of the adapters shipped with the suite."""
    if name not in ADAPTERS:
        raise SystemExit(
            f"unknown adapter {name!r}. Shipped: {', '.join(sorted(ADAPTERS))}.\n"
            "To score your own implementation, use --against module:Class -- you do not need "
            "to add anything to this suite."
        )
    module_name, class_name = ADAPTERS[name]
    return _instantiate(__import__(module_name, fromlist=[class_name]), class_name, name)


def load_external(spec: str) -> Any:
    """An adapter named as `module:Class`, imported from the caller's environment.

    Deliberately importing by name rather than by file path. An adapter is code that has to
    import the implementation it scores, so it belongs in that implementation's own package where
    its dependencies resolve — not as a loose file the suite side-loads and hopes about.
    """
    if ":" not in spec:
        raise SystemExit(
            f"--against wants module:Class, got {spec!r}.\n"
            "For example: --against my_layer.conformance:MyAdapter\n"
            "The module must be importable in this environment; see "
            "conformance/adapters/README.md."
        )

    module_name, class_name = spec.rsplit(":", 1)
    try:
        module = __import__(module_name, fromlist=[class_name])
    except ImportError as exc:
        raise SystemExit(
            f"cannot import {module_name!r}: {exc}\n"
            "The adapter and the implementation it scores must both be importable here. "
            "Installing your implementation into the same environment as this suite is the "
            "usual answer."
        ) from None

    return _instantiate(module, class_name, spec)


def _instantiate(module: Any, class_name: str, label: str) -> Any:
    """Build the adapter, refusing early rather than scoring an absent implementation.

    A missing implementation is a **setup problem, not a conformance failure**. Without this
    check an uninstalled layer produces a plausible-looking `0/7 passed, AEGS-1 claimable: no`
    report — a document somebody could publish in good faith, and one that says something false
    about a system that was never run.
    """
    check = getattr(module, "implementation_available", None)
    if check is not None and not check():
        raise SystemExit(
            f"cannot score {label!r}: "
            + getattr(module, "NOT_INSTALLED", "the implementation is not importable")
        )

    adapter = getattr(module, class_name, None)
    if adapter is None:
        available = [n for n in dir(module) if n.endswith("Adapter")]
        raise SystemExit(
            f"{module.__name__} has no {class_name!r}."
            + (f" Did you mean one of {available}?" if available else "")
        )

    instance = adapter()
    for required in ("name", "run_case"):
        if not hasattr(instance, required):
            raise SystemExit(
                f"{class_name} is missing {required!r}. An adapter needs a `name` and a "
                "`run_case(case)`; see conformance/adapters/README.md."
            )
    return instance


def exit_code(data: dict[str, Any]) -> int:
    """The result, as something a CI job can branch on."""
    if data["passed"] == data["cases"]:
        return EXIT_ALL_PASSED
    levels = data.get("levels") or {}
    if levels.get("AEGS-1", {}).get("claimable"):
        return EXIT_LEVEL_1_ONLY
    return EXIT_NOTHING_CLAIMABLE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aegs-conformance",
        description="AEGS-CONF: score an implementation against AEGS 0.1",
        epilog=(
            "exit codes: 0 all cases passed, 1 AEGS-1 only, 2 nothing claimable, "
            "3 could not run"
        ),
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--adapter", choices=sorted(ADAPTERS),
        help="an adapter shipped with the suite",
    )
    source.add_argument(
        "--against", metavar="module:Class",
        help="your own adapter, imported from this environment",
    )
    parser.add_argument("--case", action="append", help="run only these case ids")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", metavar="PATH", help="write the JSON report here")
    parser.add_argument(
        "--list-cases", action="store_true", help="print the cases and exit"
    )
    args = parser.parse_args(argv)

    cases = Case.load_all()

    if args.list_cases:
        for case in cases:
            print(f"  {case.id}  {case.level:8} {case.control:18} {case.title}")
        return EXIT_ALL_PASSED

    try:
        if args.against:
            adapter = load_external(args.against)
        else:
            adapter = load_adapter(args.adapter or "aegoll")
    except SystemExit as exc:
        # Re-raised as code 3 rather than argparse's 2, so "could not run" is never confused
        # with "nothing claimable". A CI job that treats a setup failure as a conformance
        # result publishes a false claim.
        print(exc, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    if args.case:
        wanted = set(args.case)
        unknown = wanted - {c.id for c in cases}
        if unknown:
            print(f"no such case(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        cases = [c for c in cases if c.id in wanted]

    data = report(adapter.name, run(adapter, cases))

    if args.out:
        Path(args.out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_report(data))

    if args.case:
        # A partial run cannot support a level claim, and returning 0 for "the two cases I chose
        # passed" would let a subset be published as conformance.
        print(
            "\n  partial run: "
            f"{len(cases)} of {len(Case.load_all())} cases. No level is claimable from a "
            "subset.",
            file=sys.stderr,
        )
        return EXIT_ALL_PASSED if data["passed"] == data["cases"] else EXIT_NOTHING_CLAIMABLE

    return exit_code(data)


if __name__ == "__main__":
    raise SystemExit(main())
