"""Run AEGS-CONF against an implementation.

    python conformance/run.py --adapter aegoll
    python conformance/run.py --adapter stub          # proves the suite discriminates
    python conformance/run.py --adapter aegoll --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from runner import Case, format_report, report, run  # noqa: E402

ADAPTERS = {
    "aegoll": ("adapters.aegoll_adapter", "AegollAdapter"),
    "stub": ("adapters.stub_adapter", "StubAdapter"),
}


def load_adapter(name: str):
    if name not in ADAPTERS:
        raise SystemExit(
            f"unknown adapter {name!r}. Available: {', '.join(sorted(ADAPTERS))}.\n"
            "A new implementation adds one file under conformance/adapters/ and an "
            "entry here -- nothing else in the suite changes."
        )
    module_name, class_name = ADAPTERS[name]
    module = __import__(module_name, fromlist=[class_name])

    # A missing implementation is a setup problem, not a conformance failure. Without
    # this, an uninstalled implementation produces a plausible-looking "0/7 passed,
    # AEGS-1 claimable: no" report -- a document somebody could publish, and one that
    # says something false about a system that was never actually run.
    check = getattr(module, "implementation_available", None)
    if check is not None and not check():
        raise SystemExit(
            f"cannot score {name!r}: " + getattr(module, "NOT_INSTALLED", "not importable")
        )

    return getattr(module, class_name)()


def main() -> int:
    parser = argparse.ArgumentParser(description="AEGS-CONF conformance suite")
    parser.add_argument("--adapter", default="aegoll", choices=sorted(ADAPTERS))
    parser.add_argument("--case", action="append", help="run only these case ids")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", metavar="PATH", help="write the JSON report here")
    args = parser.parse_args()

    adapter = load_adapter(args.adapter)
    cases = Case.load_all()
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c.id in wanted]

    data = report(adapter.name, run(adapter, cases))

    if args.out:
        Path(args.out).write_text(json.dumps(data, indent=2) + chr(10), encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_report(data))

    # Non-zero when anything did not pass, so CI can gate on it.
    return 0 if data["passed"] == data["cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
