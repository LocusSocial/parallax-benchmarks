Implemented and verified the delivery-based return policy.

Assumptions and boundaries:

- Eligibility starts at the delivery instant.
- Customer-local delivery date is day 0.
- Day 30 remains eligible through 23:59:59.999999.
- Day 31 is ineligible.
- UTC instant comparison prevents pre-delivery requests during ambiguous DST hours.
- Purchase time is validated but does not affect eligibility.
- All timestamps must be aware; invalid IANA timezones raise `ValueError`.

Files changed:

- [SPEC.md](<run-root>/workspace/SPEC.md)
- [src/return_policy.py](<run-root>/workspace/src/return_policy.py)
- [tests/test_return_policy.py](<run-root>/workspace/tests/test_return_policy.py)
- [tests/__init__.py](<run-root>/workspace/tests/__init__.py)

Commands and results:

- Used `sed`, `rg --files`, and `find` to inspect workspace files.
- `python3 -m unittest discover -s tests -v` — 11 tests passed.
- `python3 -m unittest discover -v` — 11 tests passed after adding the test package marker.
- `PYTHONPATH=. python3 tests/test_return_policy.py -v` — 11 tests passed.
- `python3 -m pytest -q` — unavailable because pytest is not installed.