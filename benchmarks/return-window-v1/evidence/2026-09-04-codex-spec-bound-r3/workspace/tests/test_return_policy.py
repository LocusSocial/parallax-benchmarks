import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from src.return_policy import ReturnRequest, is_return_eligible


class ExistingSpecificationTests(unittest.TestCase):
    def request(self, elapsed: timedelta) -> ReturnRequest:
        purchased = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        return ReturnRequest(
            purchased_at=purchased,
            delivered_at=purchased,
            requested_at=purchased + elapsed,
            customer_timezone="UTC",
        )

    def test_request_within_30_elapsed_days_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request(timedelta(days=29))))

    def test_request_at_purchase_time_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request(timedelta(0))))

    def test_request_at_exactly_30_elapsed_days_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request(timedelta(days=30))))

    def test_request_after_30_elapsed_days_is_not_eligible(self) -> None:
        self.assertFalse(
            is_return_eligible(self.request(timedelta(days=30, seconds=1)))
        )

    def test_request_before_purchase_is_not_eligible(self) -> None:
        self.assertFalse(is_return_eligible(self.request(timedelta(seconds=-1))))

    def test_timezone_naive_timestamps_are_rejected(self) -> None:
        request = self.request(timedelta(days=1))
        for field in ("purchased_at", "delivered_at", "requested_at"):
            with self.subTest(field=field):
                invalid = replace(
                    request,
                    **{field: getattr(request, field).replace(tzinfo=None)},
                )
                with self.assertRaisesRegex(ValueError, field):
                    is_return_eligible(invalid)

    def test_only_purchase_and_request_times_define_the_window(self) -> None:
        request = replace(
            self.request(timedelta(days=30)),
            delivered_at=datetime(2027, 1, 1, tzinfo=timezone.utc),
            customer_timezone="Pacific/Kiritimati",
        )

        self.assertTrue(is_return_eligible(request))


if __name__ == "__main__":
    unittest.main()
