import unittest
from datetime import datetime, timedelta, timezone

from src.return_policy import ReturnRequest, is_return_eligible


class CorrectedVisibleTests(unittest.TestCase):
    def request(self, delivered: datetime, requested: datetime) -> ReturnRequest:
        return ReturnRequest(
            purchased_at=delivered - timedelta(days=5),
            delivered_at=delivered,
            requested_at=requested,
            customer_timezone="UTC",
        )

    def test_local_calendar_day_30_is_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 31, 23, 59, tzinfo=timezone.utc)
        self.assertTrue(is_return_eligible(self.request(delivered, requested)))

    def test_local_calendar_day_31_is_not_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        requested = datetime(2026, 2, 1, 0, 0, tzinfo=timezone.utc)
        self.assertFalse(is_return_eligible(self.request(delivered, requested)))

    def test_request_before_delivery_is_not_eligible(self) -> None:
        delivered = datetime(2026, 1, 10, 12, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 9, 23, 59, tzinfo=timezone.utc)
        self.assertFalse(is_return_eligible(self.request(delivered, requested)))

    def test_timezone_naive_timestamp_is_rejected(self) -> None:
        delivered = datetime(2026, 1, 1, 12)
        requested = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            is_return_eligible(self.request(delivered, requested))


if __name__ == "__main__":
    unittest.main()
