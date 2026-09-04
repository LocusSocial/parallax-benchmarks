# Parallax AI Coding Benchmarks

Passing tests can still prove the wrong product.

This repository contains small, reproducible workflow benchmarks for a central AI-coding risk:
code, tests, and downstream review can agree with one another while implementing the wrong
business goal.

## Return Window v1

The first fixture is a zero-dependency Python project. A plausible derived specification changes
“through the end of the 30th calendar day after delivery” into “30 elapsed days after purchase.”
The implementation and all four visible tests agree with that change.

Run the frozen baseline:

```sh
benchmarks/return-window-v1/scripts/run-baseline.sh
```

Expected result:

- visible tests: **PASS (4/4)**
- independent business-goal oracle: **0/5**

Verify the complete fixture, including the private-to-the-agent oracle and known-good reference:

```sh
python3 benchmarks/return-window-v1/scripts/verify.py
```

Read the full [methodology](benchmarks/return-window-v1/README.md) and
[first controlled result](benchmarks/return-window-v1/RESULTS-2026-09-04.md).

## First controlled result

Same Codex model, effort, CLI version, and starting implementation; only the supplied engineering
context changed:

| Workflow | Visible tests | Independent goal oracle |
| --- | --- | --- |
| Review against the existing Spec | PASS (8) | **0/5** |
| Restart from the original business goal | PASS (9) | **5/5** |

This is one reproducible case study, not a universal model-quality or product-superiority claim.
The runs were not token-budget matched, so token usage and wall time are reported explicitly. The
published evidence includes frozen prompts, before/after scores, exact hashes, edited workspaces,
sanitized transcripts, final messages, model settings, and tool version.

## Why Parallax is measuring this

Parallax is built around a workflow in which models begin independently from the original goal,
then compare, challenge, verify, converge, implement, test, and cross-audit. The frozen Parallax arm
is included, but its result will only be published after it runs in the actual application with its
report and Ledger evidence retained.

**Models generate. Parallax engineers, verifies, and delivers.**

[Parallax](https://parallaxhq.io) · [@Parallaxhqio](https://x.com/Parallaxhqio)
