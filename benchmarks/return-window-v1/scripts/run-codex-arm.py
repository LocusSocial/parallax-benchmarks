#!/usr/bin/env python3
"""Run and preserve one reproducible Codex comparison arm."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BENCHMARK = SCRIPT.parents[1]
PREPARE = SCRIPT.parent / "prepare.py"
SCORE = SCRIPT.parent / "score.py"
PROMPTS = {
    "spec-bound": BENCHMARK / "prompts" / "spec-bound-review.md",
    "goal-first": BENCHMARK / "prompts" / "goal-first-single.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=sorted(PROMPTS))
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="high")
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.mkdir(parents=True)
    workspace = output / "workspace"
    prompt = PROMPTS[args.arm].read_bytes()
    subprocess.run(
        [sys.executable, str(PREPARE), "--arm", args.arm, str(workspace)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    before = run_json([sys.executable, str(SCORE), str(workspace)])
    (output / "before.json").write_text(
        json.dumps(before, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "prompt.md").write_bytes(prompt)

    version = subprocess.run(
        ["codex", "--version"], check=True, text=True, stdout=subprocess.PIPE
    ).stdout.strip()
    command = [
        "codex",
        "exec",
        "-C",
        str(workspace),
        "--approve-for-me",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--model",
        args.model,
        "--config",
        f'model_reasoning_effort="{args.reasoning_effort}"',
        "--output-last-message",
        str(output / "final-message.md"),
        "-",
    ]
    started_at = utc_now()
    with (output / "transcript.log").open("wb") as transcript:
        completed = subprocess.run(
            command,
            input=prompt,
            stdout=transcript,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finished_at = utc_now()
    transcript_body = (output / "transcript.log").read_bytes()
    token_matches = re.findall(rb"tokens used\s*\n([0-9,]+)", transcript_body)
    tokens_used = int(token_matches[-1].replace(b",", b"")) if token_matches else None
    duration_seconds = (
        datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
        - datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    ).total_seconds()
    after = run_json([sys.executable, str(SCORE), str(workspace)])
    (output / "after.json").write_text(
        json.dumps(after, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    metadata = {
        "arm": args.arm,
        "benchmark": "return-window-v1",
        "codex_cli_version": version,
        "command": command,
        "duration_seconds": duration_seconds,
        "exit_code": completed.returncode,
        "finished_at": finished_at,
        "model": args.model,
        "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
        "reasoning_effort": args.reasoning_effort,
        "started_at": started_at,
        "starting_implementation_sha256": before["implementation_sha256"],
        "tokens_used": tokens_used,
        "transcript_sha256": hashlib.sha256(transcript_body).hexdigest(),
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "exit_code": completed.returncode, "score": after["score"]}))
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
