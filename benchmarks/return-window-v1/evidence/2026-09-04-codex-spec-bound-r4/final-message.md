Reviewed against `SPEC.md`; the implementation was already compliant, so no production code changes were needed.

Changed:

- [tests/test_return_policy.py](<run-root>/workspace/tests/test_return_policy.py:1)
  - Added zero-duration and exact 30-day boundary tests.
  - Confirmed delivery date and customer timezone do not affect eligibility.
  - Added naive `requested_at` and `delivered_at` validation tests.

Validation commands:

- `python3 -B -m unittest discover -s tests -v` — **10 tests passed**
- `python3 -m py_compile src/__init__.py src/return_policy.py tests/test_return_policy.py` — passed
- `python3 -m pytest -q` — unavailable because pytest is not installed.

Generated `__pycache__` artifacts were cleaned up.