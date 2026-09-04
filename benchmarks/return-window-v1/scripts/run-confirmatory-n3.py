#!/usr/bin/env python3
"""Run the frozen 2026-09-04 three-pair confirmatory sequence."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BENCHMARK = SCRIPT.parents[1]
RUNNER = SCRIPT.parent / "run-codex-arm.py"
RESULTS = BENCHMARK / "results"
ORDER = {
    2: ("spec-bound", "goal-first"),
    3: ("goal-first", "spec-bound"),
    4: ("spec-bound", "goal-first"),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    records = []
    for repetition, arms in ORDER.items():
        for arm in arms:
            name = f"2026-09-04-codex-{arm}-r{repetition}"
            output = RESULTS / name
            if output.exists():
                raise SystemExit(f"refusing to overwrite existing run: {output}")
            print(f"START {name} {now()}", flush=True)
            completed = subprocess.run(
                [sys.executable, str(RUNNER), arm, str(output)], check=False
            )
            after_path = output / "after.json"
            score = None
            if after_path.is_file():
                score = json.loads(after_path.read_text(encoding="utf-8"))["score"]
            record = {
                "arm": arm,
                "exit_code": completed.returncode,
                "finished_at": now(),
                "name": name,
                "repetition": repetition,
                "score": score,
                "valid": completed.returncode == 0 and score is not None,
            }
            records.append(record)
            print(f"DONE  {name} exit={completed.returncode} score={score} {now()}", flush=True)
            if not record["valid"]:
                manifest = RESULTS / "2026-09-04-confirmatory-n3-progress.json"
                manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
                raise SystemExit("infrastructure failure; preserve this attempt and rerun explicitly")

    manifest = RESULTS / "2026-09-04-confirmatory-n3-progress.json"
    manifest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"COMPLETE {manifest}", flush=True)


if __name__ == "__main__":
    main()
