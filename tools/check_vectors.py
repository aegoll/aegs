"""Validate the vectors themselves, and report clause coverage.

    python tools/check_vectors.py

Three checks, and the second is the one that catches real mistakes:

1. Every vector validates against `vectors/schema.json`.
2. Every vector's `id` matches its file path. An id that disagrees with its filename makes
   a failure report point at the wrong file, which is worse than no report.
3. Every vector's `clause` names a clause that actually exists in `spec/`. A vector citing
   `AEGS-0.1-ARITH-99` looks like coverage and is not.

Coverage in the other direction — every MUST having a vector — is `lint_normative.py`.
Together they close the loop: no orphan vectors, no untested requirements.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parents[1]
VECTORS = HERE / "vectors"
SPEC = HERE / "spec"
SCHEMA = VECTORS / "schema.json"

#: A clause heading. The optional lowercase suffix lets a clause be inserted
#: without renumbering its neighbours -- renumbering breaks every citation.
CLAUSE = re.compile(r"^##\s+(AEGS-\d+\.\d+-[A-Z]+-\d+[a-z]?)\b", re.M)


def declared_clauses() -> set[str]:
    """Every clause identifier the specification defines."""
    found: set[str] = set()
    for path in sorted(SPEC.glob("*.md")):
        found |= set(CLAUSE.findall(path.read_text(encoding="utf-8")))
    return found


def main() -> int:
    if not VECTORS.is_dir():
        print(f"no vectors at {VECTORS}")
        return 1
    if not SCHEMA.is_file():
        print(f"no vector schema at {SCHEMA}")
        return 1

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    clauses = declared_clauses()
    problems: list[str] = []
    coverage: dict[str, int] = {}
    families: dict[str, int] = {}
    total = 0

    for path in sorted(VECTORS.rglob("*.json")):
        if path.name == "schema.json":
            continue
        total += 1
        rel = path.relative_to(VECTORS).as_posix()
        try:
            vector = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{rel}: not valid JSON: {exc}")
            continue

        for error in sorted(validator.iter_errors(vector), key=str):
            where = "/".join(str(p) for p in error.path) or "<root>"
            problems.append(f"{rel}: {where}: {error.message}")

        expected_id = rel.removesuffix(".json")
        if vector.get("id") != expected_id:
            problems.append(
                f"{rel}: id is {vector.get('id')!r} but the path says {expected_id!r}. "
                "A failure report would point at the wrong file."
            )

        clause = vector.get("clause")
        if clause:
            coverage[clause] = coverage.get(clause, 0) + 1
            if clauses and clause not in clauses:
                problems.append(
                    f"{rel}: cites {clause}, which no clause in spec/ defines. A vector "
                    "citing a clause that does not exist looks like coverage and is not."
                )

        families[rel.split("/")[0]] = families.get(rel.split("/")[0], 0) + 1

    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"{total} vector(s) valid")
    for family, count in sorted(families.items()):
        print(f"  {family:12} {count}")
    print(f"\ncovering {len(coverage)} clause(s):")
    for clause, count in sorted(coverage.items()):
        print(f"  {clause:22} {count} vector(s)")

    uncited = sorted(clauses - set(coverage)) if clauses else []
    if uncited:
        # Not a failure here. `lint_normative.py` decides whether an uncited clause is a
        # problem, because only it knows whether the clause contains a MUST.
        print(f"\n{len(uncited)} declared clause(s) with no vector:")
        for clause in uncited:
            print(f"  {clause}")
        print("  (lint_normative.py fails only those containing a MUST)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
