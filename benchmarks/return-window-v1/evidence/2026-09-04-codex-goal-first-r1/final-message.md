Implemented the delivery-based, customer-local calendar return window.

Assumptions and boundaries:

- Delivery date is day 0; local days 0–30 are eligible.
- All of local day 30 is eligible; day 31 is not.
- Requests before the delivery instant are ineligible.
- DST and UTC elapsed hours do not affect the calendar-day calculation.
- Purchase time is validated but otherwise ignored; no additional purchase chronology rule was invented.
- Naive timestamps and invalid IANA timezone identifiers raise `ValueError`.

Files changed:

- [SPEC.md](<run-root>/workspace/SPEC.md)
- [src/return_policy.py](<run-root>/workspace/src/return_policy.py)
- [tests/test_return_policy.py](<run-root>/workspace/tests/test_return_policy.py)

Test commands and results:

- `python3 -m unittest discover -s tests -v` — **9 tests passed**
- `python3 -m unittest discover -v` — discovered no tests because `tests/` is not a package
- `python3 -m pytest -q` — unavailable; pytest is not installed
- `python -m unittest discover -v` — unavailable; no `python` alias
- `git diff --check` — no whitespace errors reported for tracked changes; this workspace is untracked by its enclosing repository.