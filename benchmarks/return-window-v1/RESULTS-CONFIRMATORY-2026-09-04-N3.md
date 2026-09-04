# Return Window v1 — confirmatory repetitions (N=3 per arm)

Date: 2026-09-04  
Protocol: [`PROTOCOL-2026-09-04-N3.md`](PROTOCOL-2026-09-04-N3.md)  
Status: complete; six of six planned runs valid

The repetition plan was frozen after the exploratory `r1` pair and before `r2`–`r4` ran. The
exploratory run is not pooled into the result below.

## Confirmatory result

| Arm | Run | Oracle score | Visible tests | Tokens | Wall time |
| --- | --- | ---: | --- | ---: | ---: |
| Spec-bound | `r2` | **0/5** | PASS | 29,862 | 182.7 s |
| Spec-bound | `r3` | **0/5** | PASS | 16,947 | 130.0 s |
| Spec-bound | `r4` | **0/5** | PASS | 29,719 | 154.0 s |
| Goal-first | `r2` | **5/5** | PASS | 49,729 | 275.1 s |
| Goal-first | `r3` | **5/5** | PASS | 43,022 | 292.6 s |
| Goal-first | `r4` | **5/5** | PASS | 37,852 | 219.3 s |

Observed in the three frozen repetitions:

- Spec-bound: **3/3 runs scored 0/5**.
- Goal-first: **3/3 runs scored 5/5**.
- Every run exited successfully and passed its visible test suite.
- Every run began with implementation SHA-256
  `f6cb78961a354f314aa03eff7585a4a18fd67c680197c1228c98f689987b05a4`.
- Every run used `gpt-5.6-sol`, high reasoning effort, and `codex-cli 0.153.0`.

## Compute disclosure

The arms were not token- or time-budget matched:

| Arm | Mean tokens | Median tokens | Mean wall time | Median wall time |
| --- | ---: | ---: | ---: | ---: |
| Spec-bound | 25,509 | 29,719 | 155.6 s | 154.0 s |
| Goal-first | 43,534 | 43,022 | 262.3 s | 275.1 s |

In these runs, Goal-first used about 71% more tokens and 69% more wall time on average. That cost
is material and is reported rather than normalized away.

## Interpretation

For this known-answer fixture, changing the workflow context repeatedly changed the delivered
business result. Reviewing against the existing Spec consistently reinforced the wrong frame,
while restarting from the original customer promise consistently recovered all five requirements.

This strengthens the evidence that the problem Parallax targets is real: more internally
consistent code and tests do not guarantee the intended product was built.

It still does not isolate a multi-model effect, demonstrate a cost advantage, establish a general
success rate, or prove Parallax product superiority. Those claims require the actual Parallax arm,
more fixtures, matched budgets where appropriate, and multiple model/version families.

## Evidence

Each published run contains:

- frozen prompt and prompt SHA-256;
- before/after scorer JSON;
- edited workspace;
- model, CLI, effort, token count, timing, and implementation hashes;
- sanitized transcript and final message;
- raw transcript SHA-256, with the raw machine-specific transcript retained privately.
