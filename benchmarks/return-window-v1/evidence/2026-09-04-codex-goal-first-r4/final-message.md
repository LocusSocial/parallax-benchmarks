Implemented the delivery-based, customer-local calendar return policy.

Assumptions and boundaries:

- Delivery date is day 0.
- Local calendar days 0–30 are inclusive.
- Day 30 remains eligible through 23:59:59.
- Day 31 is ineligible.
- Requests before the delivery instant are ineligible, including DST-fold ambiguities.
- Purchase time does not affect eligibility but must remain timezone-aware.
- Invalid IANA zones and naïve timestamps raise `ValueError`.

Files changed:

- [SPEC.md](<run-root>/workspace/SPEC.md)
- [src/return_policy.py](<run-root>/workspace/src/return_policy.py)
- [tests/test_return_policy.py](<run-root>/workspace/tests/test_return_policy.py)

Commands run:

- `sed` inspections of the goal, spec, implementation, and tests
- `rg --files -g '!BUSINESS_GOAL.md' -g '!.*'`
- `git status --short`
- `python -m unittest discover -v` — failed because `python` is unavailable
- `python3 -m unittest discover -v` — discovered zero tests due to the non-package test directory
- `python3 -m unittest discover -s tests -v` — successful

Final result: **10 tests ran, all passed**.