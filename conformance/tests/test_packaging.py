"""The suite has to work when *installed*, not only when run from this checkout.

That is the whole claim of B5.2: `pip install aegs-conformance` and score a layer this project has
never seen. It was not true. `runner.py` resolved the Decision Record schema as
`Path(__file__).parents[1] / "schemas" / ...`, which is right from a checkout and resolves to
`site-packages/schemas/` from a wheel — a directory that does not exist. So the packaged suite
could not have validated anything.

The same defect as `tesoro`'s F-A1, in the one package whose entire purpose is to be installed by
somebody else. Found by attempting the packaging rather than by a third party's traceback, which is
the argument for packaging before claiming a suite is standalone.

These tests are what keep it true.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CONFORMANCE = REPO / "conformance"

if str(CONFORMANCE) not in sys.path:
    sys.path.insert(0, str(CONFORMANCE))


def project() -> dict:
    path = REPO / "pyproject.toml"
    if not path.is_file():
        pytest.skip("no pyproject.toml; nothing to assert about packaging")
    return tomllib.loads(path.read_text(encoding="utf-8"))


# --- the runtime data has to travel with the package ----------------------


def test_the_schema_is_inside_the_package():
    """Not `../schemas/`. From a wheel that is `site-packages/schemas/`, which is nothing."""
    vendored = CONFORMANCE / "_schemas" / "decision-record-0.1.json"
    assert vendored.is_file(), (
        f"{vendored} is missing, so an installed suite has no schema and cannot validate a "
        "record -- meaning a conformant verdict inside a malformed record would score as a pass"
    )


def test_the_vendored_schema_matches_the_canonical_one():
    """A stale copy would score records against a document nobody publishes."""
    canonical = json.loads(
        (REPO / "schemas" / "decision-record-0.1.json").read_text(encoding="utf-8")
    )
    vendored = json.loads(
        (CONFORMANCE / "_schemas" / "decision-record-0.1.json").read_text(encoding="utf-8")
    )
    assert canonical == vendored, (
        "the packaged schema has drifted from schemas/decision-record-0.1.json. Never edit the "
        "vendored copy: edit the canonical one and copy it down."
    )


def test_the_runner_finds_its_schema_without_reaching_outside_the_package():
    """The property, rather than the path.

    Asserts the resolved schema lives **under `conformance/`**, so the lookup cannot silently go
    back to depending on a sibling directory that a wheel does not have.
    """
    import runner

    assert runner.SCHEMA_PATH.is_file()
    resolved = runner.SCHEMA_PATH.resolve()
    assert CONFORMANCE.resolve() in resolved.parents, (
        f"the schema resolved to {resolved}, outside the package. From an installed wheel that "
        "path does not exist."
    )


def test_every_case_is_declared_as_package_data():
    """Seven JSON files that must travel with the wheel. Without them the suite installs with
    nothing to run — which fails loudly, but only for whoever installed it."""
    declared = project()["tool"]["setuptools"]["package-data"]["conformance"]
    assert any("cases/*.json" in d for d in declared), declared
    assert any("_schemas/*.json" in d for d in declared), declared

    cases = sorted((CONFORMANCE / "cases").glob("*.json"))
    assert len(cases) >= 7, f"only {len(cases)} cases on disk"


# --- what the package may and may not depend on ---------------------------


def test_the_suite_does_not_depend_on_the_implementation_it_tests():
    """A conformance suite that arrives with the thing it tests is not a conformance suite.

    `tesoro` is an *extra*, never a dependency. Someone scoring their own layer must not be made
    to install a competing one to do it.
    """
    deps = project()["project"]["dependencies"]
    assert not [d for d in deps if "tesoro" in d.lower()], (
        f"the suite depends on the reference implementation: {deps}"
    )
    extras = project()["project"]["optional-dependencies"]
    assert any("tesoro" in d for d in extras.get("reference", [])), (
        "scoring the reference implementation should still be possible via "
        "`pip install aegs-conformance[reference]`"
    )


def test_jsonschema_is_a_hard_dependency_here():
    """Unlike in `tesoro`, where validation is optional because the layer governs correctly
    without it.

    This package's whole job is to judge whether somebody else's records conform. A scorer that
    could not validate would report a conformant verdict inside a malformed record as a pass, and
    there is no useful degraded mode for that.
    """
    deps = project()["project"]["dependencies"]
    assert any("jsonschema" in d for d in deps), deps


def test_the_console_script_points_at_something_real():
    """A broken entry point is only discovered by whoever installs it."""
    scripts = project()["project"]["scripts"]
    target = scripts["aegs-conformance"]
    module_name, function = target.split(":")

    module = __import__(module_name.replace("conformance.", ""), fromlist=[function])
    assert callable(getattr(module, function)), f"{target} is not callable"


def test_the_tests_are_not_shipped():
    """These tests assert things about the repository -- a `pyproject.toml`, a canonical
    `schemas/` directory -- that an installed copy does not have. Shipping them would hand a
    user a suite whose own tests fail on their machine for reasons that are not their problem.
    """
    excluded = project()["tool"]["setuptools"]["packages"]["find"].get("exclude", [])
    assert any("tests" in pattern for pattern in excluded), excluded


# --- the extension point --------------------------------------------------


def test_an_external_adapter_can_be_named_without_editing_the_suite():
    """B5.9, and the reason `--against` exists.

    A suite that can only score adapters listed inside itself is a self-assessment: everyone else
    forks it, and a forked instrument produces numbers nobody can compare. So this checks that a
    `module:Class` spec is resolvable — with a class defined right here, which is about as
    external as a test can arrange.
    """
    import run

    module = sys.modules[__name__]
    setattr(module, "_ProbeAdapter", _ProbeAdapter)

    adapter = run.load_external(f"{__name__}:_ProbeAdapter")
    assert adapter.name == "probe"
    assert callable(adapter.run_case)


def test_a_malformed_adapter_spec_is_a_setup_error_not_a_score():
    """Exit 3, never 2. A CI job that treats a setup failure as a conformance result publishes a
    false claim."""
    import run

    assert run.main(["--against", "no-colon-here"]) == run.EXIT_COULD_NOT_RUN
    assert run.main(["--against", "no.such.module:Adapter"]) == run.EXIT_COULD_NOT_RUN


def test_an_adapter_missing_the_contract_is_refused_with_the_name_of_what_is_missing():
    """"Does not conform" is unactionable. "missing run_case" is a to-do."""
    import run

    module = sys.modules[__name__]
    setattr(module, "_HalfAdapter", _HalfAdapter)

    with pytest.raises(SystemExit) as excinfo:
        run.load_external(f"{__name__}:_HalfAdapter")
    assert "run_case" in str(excinfo.value)


def test_exit_codes_distinguish_the_three_outcomes():
    """`0` all passed, `1` AEGS-1 only, `2` nothing claimable. Three answers, not two: "did not
    reach AEGS-2" and "failed AEGS-1" are different results."""
    import run

    assert run.exit_code({"passed": 7, "cases": 7, "levels": {}}) == run.EXIT_ALL_PASSED
    assert run.exit_code({
        "passed": 5, "cases": 7,
        "levels": {"AEGS-1": {"claimable": True}, "AEGS-2": {"claimable": False}},
    }) == run.EXIT_LEVEL_1_ONLY
    assert run.exit_code({
        "passed": 2, "cases": 7,
        "levels": {"AEGS-1": {"claimable": False}, "AEGS-2": {"claimable": False}},
    }) == run.EXIT_NOTHING_CLAIMABLE


class _ProbeAdapter:
    name = "probe"

    def run_case(self, case):  # noqa: ANN001, ANN201
        return None


class _HalfAdapter:
    name = "half"
    # no run_case, on purpose
