# Return Window — Parallax demo project

This deliberately small Python project demonstrates a common AI-coding failure mode:
the implementation and its tests agree with a plausible specification, but the specification
does not faithfully implement the original business goal.

The repository has no third-party dependencies. It needs Python 3.9 or newer.

## Start here

1. Run the visible tests:

   ```sh
   python3 -m unittest discover -s tests -v
   ```

   They pass.

2. Read [BUSINESS_GOAL.md](BUSINESS_GOAL.md), then compare it with
   [SPEC.md](SPEC.md) and [src/return_policy.py](src/return_policy.py).

3. Open this directory as a project in Parallax and paste the single command from
   [PARALLAX_TASK.txt](PARALLAX_TASK.txt) into Dispatch.

The important instruction is that Claude and Codex must each start from the original business
goal. Neither model is allowed to treat the existing specification or passing tests as proof that
the behavior is correct.

## What the example is designed to reveal

The current code silently substitutes four assumptions:

- the purchase time is the start of the return window;
- 30 days means exactly 720 elapsed hours;
- UTC is an acceptable substitute for the customer's calendar;
- a request after purchase cannot be before delivery.

The visible tests repeat those assumptions, so they all pass. The benchmark's independent oracle
checks the business outcome instead.

## Expected result

A successful repair keeps `ReturnRequest` as the public input, but determines eligibility from:

- `delivered_at`, not `purchased_at`;
- local calendar dates in `customer_timezone`;
- an inclusive day-30 boundary;
- an explicit rejection for requests made before local delivery;
- timezone-aware timestamps and a valid IANA timezone.

The hidden acceptance suite lives outside this sample directory under
`benchmarks/return-window-v1`. This prevents the agent from solving the demo by reading the answer.

