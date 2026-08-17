"""Validate the profile manifests, and enforce the one rule a schema cannot express.

    python tools/check_profiles.py

JSON Schema can say a profile is well-formed. It cannot say that a profile which
`extends` another may only **tighten** its requirements — that is a relationship between
two documents, and it is the rule that keeps the levels meaningful. Without it, `aegs-2`
could quietly relax something `aegs-1` requires, and a higher level would be weaker than
a lower one while both still validated.

Also checks that every `MUST_EXERCISE` control names a `recordPath`. A requirement with
nowhere to look for its evidence is not checkable, and an uncheckable MUST is a wish —
the same rule the specification and the vector suite follow.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parents[1]
PROFILES = HERE / "profiles"
SCHEMA = HERE / "schemas" / "profile-0.1.json"

#: Strictly ordered. `extends` may move a control up this ladder, never down.
RANK = {"OPTIONAL": 0, "MUST_RECORD": 1, "MUST_EXERCISE": 2}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def requirements(profile: dict) -> dict[str, str]:
    """control -> requirement. A control absent from the list is OPTIONAL by omission."""
    return {c["control"]: c["requirement"] for c in profile["controls"]}


def main() -> int:
    if not PROFILES.is_dir():
        print(f"no profiles at {PROFILES}")
        return 1

    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    profiles: dict[str, dict] = {}
    problems: list[str] = []

    for path in sorted(PROFILES.glob("*.json")):
        data = load(path)
        for error in sorted(validator.iter_errors(data), key=str):
            problems.append(f"{path.name}: {'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}")
        if not problems:
            if data["profile"] != path.stem:
                problems.append(
                    f"{path.name}: declares profile {data['profile']!r} but the filename says "
                    f"{path.stem!r}. A config names a profile by id; the two must agree or "
                    "the file a scorer loads is not the profile it thinks it loaded."
                )
            profiles[data["profile"]] = data

    for name, data in profiles.items():
        for control in data["controls"]:
            if control["requirement"] == "MUST_EXERCISE" and not control.get("recordPath"):
                problems.append(
                    f"{name}: {control['control']} is MUST_EXERCISE with no recordPath. "
                    "A requirement with nowhere to look for its evidence is not checkable."
                )

        parent_name = data.get("extends")
        if not parent_name:
            continue
        parent = profiles.get(parent_name)
        if parent is None:
            problems.append(f"{name}: extends unknown profile {parent_name!r}")
            continue
        child_reqs, parent_reqs = requirements(data), requirements(parent)
        for control, required in parent_reqs.items():
            inherited = child_reqs.get(control, "OPTIONAL")
            if RANK[inherited] < RANK[required]:
                problems.append(
                    f"{name}: relaxes {control} from {required} (inherited from "
                    f"{parent_name}) to {inherited}. A profile may only tighten what it "
                    "extends — otherwise a higher level is weaker than a lower one."
                )

    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"{len(profiles)} profile(s) valid: {', '.join(sorted(profiles))}")
    for name in sorted(profiles):
        reqs = requirements(profiles[name])
        counts = {level: sum(1 for r in reqs.values() if r == level) for level in RANK}
        print(
            f"  {name:8} MUST_EXERCISE {counts['MUST_EXERCISE']:2}  "
            f"MUST_RECORD {counts['MUST_RECORD']:2}  OPTIONAL {counts['OPTIONAL']:2}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
