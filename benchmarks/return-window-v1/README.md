# Return Window Benchmark v1

This is a small, reproducible workflow benchmark for a specific AI-coding failure mode:
code and visible tests can be internally consistent while implementing the wrong business rule.

It is not a general model leaderboard. It measures whether a workflow recovers the original
business outcome from a misleading but plausible specification and passing tests.

The first controlled run and its limits are documented in
[`RESULTS-2026-09-04.md`](RESULTS-2026-09-04.md).

## Requirements

- macOS or Linux
- Python 3.9+
- no Python packages

## Reproduce the frozen baseline

From the Parallax repository root:

```sh
benchmarks/return-window-v1/scripts/run-baseline.sh
```

The command proves both parts of the seeded failure:

1. all visible tests pass;
2. the independent business-goal oracle fails.

## Prepare an isolated submission

```sh
python3 benchmarks/return-window-v1/scripts/prepare.py \
  --arm goal-first /tmp/return-window-run
```

Give the agent only `/tmp/return-window-run`. Do not give it the benchmark directory, oracle
tests, or reference implementation.

Use one of the frozen prompts in `prompts/`, then score the resulting directory:

```sh
python3 benchmarks/return-window-v1/scripts/score.py /tmp/return-window-run
```

For machine-readable output:

```sh
python3 benchmarks/return-window-v1/scripts/score.py \
  /tmp/return-window-run --json-out /tmp/return-window-result.json
```

Verify that all arms are clean, start from identical code, and that the frozen baseline/reference
scores remain `0/5` and `5/5`:

```sh
python3 benchmarks/return-window-v1/scripts/verify.py
```

## Recommended comparison

Run each arm from a freshly prepared directory:

| Arm | Context supplied | What it represents |
| --- | --- | --- |
| `spec-bound-review.md` | Existing Spec, code, visible tests | Common downstream review constrained by the original frame |
| `goal-first-single.md` | Original business goal plus untrusted repository | One model restarting from the source objective |
| `parallax-goal-first.md` | Same original goal, independent Claude/Codex reasoning | Parallax's compare, challenge, verify, converge workflow |

Prepare those arms with `--arm spec-bound`, `--arm goal-first`, and `--arm parallax`
respectively. The preparer deliberately omits the explanatory sample README and strips its
editorial warning from `SPEC.md`; benchmark participants cannot see the seeded answer. The
implementation SHA-256 is identical at the start of every arm, while the supplied context differs
by design.

Use the same model versions, effort, time limit, machine, and starting SHA for every repeated run.
Record every raw transcript. Do not publish a percentage from one run as a general quality claim.

For a reproducible Codex run that preserves the prompt, before/after scores, transcript, final
message, tool version, model settings, timestamps, and hashes:

```sh
python3 benchmarks/return-window-v1/scripts/run-codex-arm.py \
  spec-bound benchmarks/return-window-v1/results/<run-id>-spec-bound
```

Replace `spec-bound` with `goal-first` for the second single-model arm. Use a new output directory
for every repetition. The Parallax arm must be run in the Parallax product and retain its report
and Ledger evidence; it must not be simulated by this Codex-only runner.

## Scoring

The oracle contains five independently named requirements:

- `RW-001`: delivery, not purchase, starts the window;
- `RW-002`: requests before delivery are rejected;
- `RW-003`: the end of local calendar day 30 is inclusive;
- `RW-004`: a daylight-saving transition does not shorten the calendar window;
- `RW-005`: the IANA timezone is validated and used.

The score is the number of requirements that pass. The scorer records one deterministic digest for
the implementation and visible tests and another for the complete supplied context, so results can
be tied to exact bytes without pretending intentionally different contexts are identical.

## Evidence boundary

A passing result proves only that one submitted implementation satisfies this five-requirement
oracle. A comparison becomes evidence for a workflow advantage only after repeated, independently
scored runs with frozen inputs and equivalent budgets.
