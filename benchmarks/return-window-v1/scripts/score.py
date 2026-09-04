#!/usr/bin/env python3
"""Score a return-window submission against the independent business-goal oracle."""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BENCHMARK = SCRIPT.parents[1]
ORACLE = BENCHMARK / "oracle_tests"


def digest_paths(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(set(paths), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        body = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(body).to_bytes(8, "big"))
        digest.update(body)
    return digest.hexdigest()


def implementation_paths(root: Path) -> list[Path]:
    included = []
    for directory in (root / "src", root / "tests"):
        if directory.is_dir():
            included.extend(directory.rglob("*.py"))
    return included


def context_paths(root: Path) -> list[Path]:
    included = implementation_paths(root)
    for name in ("BUSINESS_GOAL.md", "SPEC.md", "PARALLAX_TASK.txt"):
        path = root / name
        if path.is_file():
            included.append(path)
    return included


def visible_result(root: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return {"exit_code": completed.returncode, "output": completed.stdout}


def oracle_result(root: Path) -> dict:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    loader = unittest.TestLoader()
    suite = loader.discover(str(ORACLE), pattern="test_*.py")
    # Collect stable identities before running. unittest replaces completed tests with None by
    # default to release references, so walking the suite after execution loses the evidence we
    # need for requirement-level scoring.
    def tests_in(node):
        for item in node:
            if isinstance(item, unittest.TestSuite):
                yield from tests_in(item)
            elif item is not None:
                yield item

    all_names = sorted(test.id().split(".")[-1] for test in tests_in(suite))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    failed_names = {
        test.id().split(".")[-1]
        for test, _ in list(result.failures) + list(result.errors)
    }
    passed_names = [name for name in all_names if name not in failed_names]
    return {
        "total": result.testsRun,
        "passed": len(passed_names),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "passed_requirements": passed_names,
        "failed_requirements": sorted(failed_names),
        "output": stream.getvalue(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    submission = args.submission.resolve()
    if not (submission / "src" / "return_policy.py").is_file():
        raise SystemExit(f"not a return-window submission: {submission}")

    visible = visible_result(submission)
    oracle = oracle_result(submission)
    report = {
        "benchmark": "return-window-v1",
        "implementation_sha256": digest_paths(submission, implementation_paths(submission)),
        "submission_sha256": digest_paths(submission, context_paths(submission)),
        "visible_tests": visible,
        "oracle": oracle,
        "score": f"{oracle['passed']}/{oracle['total']}",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.json_out:
        args.json_out.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
