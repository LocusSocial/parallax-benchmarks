#!/usr/bin/env python3
"""Verify that the frozen fixture and scorer have the expected behavior."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BENCHMARK = SCRIPT.parents[1]
REPOSITORY = SCRIPT.parents[3]
PREPARE = SCRIPT.parent / "prepare.py"
SCORE = SCRIPT.parent / "score.py"
REFERENCE = BENCHMARK / "reference"


def score(path: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCORE), str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(completed.stdout)


def main() -> None:
    expected_files = {
        "baseline": {"SPEC.md", "src/__init__.py", "src/return_policy.py", "tests/test_return_policy.py"},
        "spec-bound": {"SPEC.md", "src/__init__.py", "src/return_policy.py", "tests/test_return_policy.py"},
        "goal-first": {
            "BUSINESS_GOAL.md",
            "SPEC.md",
            "src/__init__.py",
            "src/return_policy.py",
            "tests/test_return_policy.py",
        },
        "parallax": {
            "BUSINESS_GOAL.md",
            "PARALLAX_TASK.txt",
            "SPEC.md",
            "src/__init__.py",
            "src/return_policy.py",
            "tests/test_return_policy.py",
        },
    }
    with tempfile.TemporaryDirectory(prefix="parallax-return-window-") as temporary:
        root = Path(temporary)
        reports = {}
        for arm, expected in expected_files.items():
            workspace = root / arm
            subprocess.run(
                [sys.executable, str(PREPARE), "--arm", arm, str(workspace)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            actual = {
                path.relative_to(workspace).as_posix()
                for path in workspace.rglob("*")
                if path.is_file()
            }
            if actual != expected:
                raise SystemExit(f"unexpected files for {arm}: {sorted(actual ^ expected)}")
            text = "\n".join(path.read_text(encoding="utf-8") for path in workspace.rglob("*.*"))
            for leaked in ("designed to reveal", "Expected result", "hidden acceptance"):
                if leaked in text:
                    raise SystemExit(f"answer leak in {arm}: {leaked}")
            reports[arm] = score(workspace)

        implementation_hashes = {
            report["implementation_sha256"] for report in reports.values()
        }
        if len(implementation_hashes) != 1:
            raise SystemExit("benchmark arms do not start from identical implementation bytes")
        if reports["baseline"]["visible_tests"]["exit_code"] != 0:
            raise SystemExit("seeded visible tests must pass")
        if reports["baseline"]["score"] != "0/5":
            raise SystemExit("seeded baseline must score 0/5")

        reference = score(REFERENCE)
        if reference["visible_tests"]["exit_code"] != 0 or reference["score"] != "5/5":
            raise SystemExit("reference implementation must pass visible tests and score 5/5")

        print(f"fixture: PASS ({next(iter(implementation_hashes))})")
        print("baseline: visible PASS, oracle 0/5")
        print("reference: visible PASS, oracle 5/5")


if __name__ == "__main__":
    main()
