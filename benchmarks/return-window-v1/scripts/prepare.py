#!/usr/bin/env python3
"""Create an isolated benchmark workspace with arm-specific context."""

import argparse
import shutil
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPOSITORY = SCRIPT.parents[3]
SAMPLE = REPOSITORY / "examples" / "return-window"
CORE_DIRECTORIES = ("src", "tests")
ARM_FILES = {
    "baseline": ("SPEC.md",),
    "spec-bound": ("SPEC.md",),
    "goal-first": ("BUSINESS_GOAL.md", "SPEC.md"),
    "parallax": ("BUSINESS_GOAL.md", "SPEC.md", "PARALLAX_TASK.txt"),
}


def copy_project(output: Path, arm: str) -> None:
    output.mkdir(parents=True)
    for directory in CORE_DIRECTORIES:
        shutil.copytree(
            SAMPLE / directory,
            output / directory,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
    for filename in ARM_FILES[arm]:
        shutil.copy2(SAMPLE / filename, output / filename)

    # The public sample labels the mismatch for humans. Benchmark participants receive the same
    # specification without that editorial note so the defect is not disclosed by the fixture.
    spec = output / "SPEC.md"
    if spec.is_file():
        spec.write_text(
            "# Existing implementation specification\n\n"
            "An order is returnable for 30 days after purchase. The service should subtract "
            "`purchased_at` from `requested_at`; a non-negative duration no greater than "
            "`30 * 24` hours is eligible.\n\n"
            "The service receives UTC timestamps, so no timezone conversion is necessary. "
            "Timezone-naive timestamps are invalid.\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--arm", choices=sorted(ARM_FILES), default="goal-first")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    if not SAMPLE.is_dir():
        raise SystemExit(f"sample project is missing: {SAMPLE}")
    copy_project(output, args.arm)
    print(output)


if __name__ == "__main__":
    main()
