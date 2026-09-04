import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.return_policy import ReturnRequest, is_return_eligible


class ReturnPolicyTests(unittest.TestCase):
    def request(
        self,
        *,
        delivered_at: datetime,
        requested_at: datetime,
        purchased_at: datetime | None = None,
        customer_timezone: str = "UTC",
    ) -> ReturnRequest:
        return ReturnRequest(
            purchased_at=purchased_at
            or datetime(2025, 12, 1, 12, tzinfo=timezone.utc),
            delivered_at=delivered_at,
            requested_at=requested_at,
            customer_timezone=customer_timezone,
        )

    def test_delivery_day_is_eligible(self) -> None:
        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
                    requested_at=datetime(2026, 1, 1, 23, 59, tzinfo=timezone.utc),
                )
            )
        )

    def test_end_of_local_day_30_is_eligible_even_after_30_elapsed_days(self) -> None:
        los_angeles = ZoneInfo("America/Los_Angeles")
        request = self.request(
            delivered_at=datetime(2026, 1, 1, 0, 1, tzinfo=los_angeles),
            requested_at=datetime(2026, 1, 31, 23, 59, tzinfo=los_angeles),
            customer_timezone="America/Los_Angeles",
        )
        self.assertTrue(is_return_eligible(request))

    def test_start_of_local_day_31_is_not_eligible(self) -> None:
        tokyo = ZoneInfo("Asia/Tokyo")
        request = self.request(
            delivered_at=datetime(2026, 1, 1, 23, 59, tzinfo=tokyo),
            requested_at=datetime(2026, 2, 1, 0, 0, tzinfo=tokyo),
            customer_timezone="Asia/Tokyo",
        )
        self.assertFalse(is_return_eligible(request))

    def test_customer_timezone_controls_calendar_dates(self) -> None:
        # These UTC dates differ by 31, but both local dates are one day earlier.
        request = self.request(
            delivered_at=datetime(2026, 1, 2, 7, 30, tzinfo=timezone.utc),
            requested_at=datetime(2026, 2, 1, 7, 59, tzinfo=timezone.utc),
            customer_timezone="America/Los_Angeles",
        )
        self.assertTrue(is_return_eligible(request))

    def test_dst_transition_does_not_shorten_calendar_window(self) -> None:
        new_york = ZoneInfo("America/New_York")
        request = self.request(
            delivered_at=datetime(2026, 2, 15, 0, 0, tzinfo=new_york),
            requested_at=datetime(2026, 3, 17, 23, 59, tzinfo=new_york),
            customer_timezone="America/New_York",
        )
        self.assertTrue(is_return_eligible(request))

    def test_purchase_time_does_not_start_window(self) -> None:
        request = self.request(
            purchased_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            delivered_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
            requested_at=datetime(2026, 5, 31, tzinfo=timezone.utc),
        )
        self.assertTrue(is_return_eligible(request))

    def test_request_before_delivery_is_not_eligible(self) -> None:
        request = self.request(
            delivered_at=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            requested_at=datetime(2026, 1, 1, 11, 59, 59, tzinfo=timezone.utc),
        )
        self.assertFalse(is_return_eligible(request))

    def test_each_timezone_naive_timestamp_is_rejected(self) -> None:
        request = self.request(
            delivered_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            requested_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        for field in ("purchased_at", "delivered_at", "requested_at"):
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, f"{field} must be timezone-aware"
            ):
                values = vars(request) | {
                    field: getattr(request, field).replace(tzinfo=None)
                }
                is_return_eligible(ReturnRequest(**values))

    def test_invalid_customer_timezone_is_rejected(self) -> None:
        request = self.request(
            delivered_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            requested_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            customer_timezone="Not/A_Real_Zone",
        )
        with self.assertRaisesRegex(ValueError, "invalid customer_timezone"):
            is_return_eligible(request)


if __name__ == "__main__":
    unittest.main()
