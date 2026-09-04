import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.return_policy import ReturnRequest, is_return_eligible


def instant(year: int, month: int, day: int, hour: int, minute: int, zone: str):
    return datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(zone))


class BusinessGoalOracle(unittest.TestCase):
    def test_rw_001_delivery_starts_the_window(self) -> None:
        request = ReturnRequest(
            purchased_at=instant(2026, 1, 1, 9, 0, "UTC"),
            delivered_at=instant(2026, 1, 20, 9, 0, "UTC"),
            requested_at=instant(2026, 2, 15, 9, 0, "UTC"),
            customer_timezone="UTC",
        )
        self.assertTrue(is_return_eligible(request))

    def test_rw_002_request_before_delivery_is_rejected(self) -> None:
        earlier_day = ReturnRequest(
            purchased_at=instant(2026, 1, 1, 9, 0, "UTC"),
            delivered_at=instant(2026, 1, 10, 9, 0, "UTC"),
            requested_at=instant(2026, 1, 5, 9, 0, "UTC"),
            customer_timezone="UTC",
        )
        same_local_day_but_earlier_instant = ReturnRequest(
            purchased_at=instant(2026, 1, 1, 9, 0, "America/Los_Angeles"),
            delivered_at=instant(2026, 1, 10, 12, 0, "America/Los_Angeles"),
            requested_at=instant(2026, 1, 10, 11, 59, "America/Los_Angeles"),
            customer_timezone="America/Los_Angeles",
        )
        self.assertFalse(is_return_eligible(earlier_day))
        self.assertFalse(is_return_eligible(same_local_day_but_earlier_instant))

    def test_rw_003_end_of_local_day_30_is_inclusive(self) -> None:
        zone = "America/Los_Angeles"
        request = ReturnRequest(
            purchased_at=instant(2025, 12, 20, 8, 0, zone),
            delivered_at=instant(2026, 1, 1, 0, 1, zone),
            requested_at=instant(2026, 1, 31, 23, 59, zone),
            customer_timezone=zone,
        )
        self.assertTrue(is_return_eligible(request))

    def test_rw_004_dst_does_not_shorten_calendar_window(self) -> None:
        zone = "America/New_York"
        request = ReturnRequest(
            purchased_at=instant(2026, 9, 20, 12, 0, zone),
            delivered_at=instant(2026, 10, 3, 0, 1, zone),
            requested_at=instant(2026, 11, 2, 23, 59, zone),
            customer_timezone=zone,
        )
        self.assertTrue(is_return_eligible(request))

    def test_rw_005_timezone_is_validated_and_used(self) -> None:
        request = ReturnRequest(
            purchased_at=datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
            delivered_at=datetime(2026, 1, 2, 0, tzinfo=timezone.utc),
            requested_at=datetime(2026, 1, 3, 0, tzinfo=timezone.utc),
            customer_timezone="Mars/Olympus_Mons",
        )
        with self.assertRaises((ValueError, ZoneInfoNotFoundError)):
            is_return_eligible(request)


if __name__ == "__main__":
    unittest.main()
