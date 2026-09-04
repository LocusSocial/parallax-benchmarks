import unittest
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

    def test_request_at_purchase_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request(timedelta(0))))

    def test_request_at_exactly_30_elapsed_days_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request(timedelta(days=30))))

    def test_request_after_30_elapsed_days_is_not_eligible(self) -> None:
        self.assertFalse(
            is_return_eligible(self.request(timedelta(days=30, seconds=1)))
        )

    def test_request_before_purchase_is_not_eligible(self) -> None:
        self.assertFalse(is_return_eligible(self.request(timedelta(seconds=-1))))

    def test_timezone_naive_timestamp_is_rejected(self) -> None:
        request = self.request(timedelta(days=1))
        invalid = ReturnRequest(
            purchased_at=request.purchased_at.replace(tzinfo=None),
            delivered_at=request.delivered_at,
            requested_at=request.requested_at,
            customer_timezone=request.customer_timezone,
        )
        with self.assertRaises(ValueError):
            is_return_eligible(invalid)

    def test_timezone_naive_requested_at_is_rejected(self) -> None:
        request = self.request(timedelta(days=1))
        invalid = ReturnRequest(
            purchased_at=request.purchased_at,
            delivered_at=request.delivered_at,
            requested_at=request.requested_at.replace(tzinfo=None),
            customer_timezone=request.customer_timezone,
        )
        with self.assertRaises(ValueError):
            is_return_eligible(invalid)

    def test_delivery_and_customer_timezone_do_not_affect_eligibility(self) -> None:
        request = self.request(timedelta(days=1))
        request_with_irrelevant_metadata = ReturnRequest(
            purchased_at=request.purchased_at,
            delivered_at=datetime(2030, 1, 1),
            requested_at=request.requested_at,
            customer_timezone="not/a-timezone",
        )

        self.assertTrue(is_return_eligible(request_with_irrelevant_metadata))


if __name__ == "__main__":
    unittest.main()
