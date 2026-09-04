import unittest
from dataclasses import replace
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.return_policy import ReturnRequest, is_return_eligible


class ReturnPolicyTests(unittest.TestCase):
    def request(
        self,
        *,
        delivered_at: datetime | None = None,
        requested_at: datetime | None = None,
        customer_timezone: str = "UTC",
    ) -> ReturnRequest:
        delivered_at = delivered_at or datetime(
            2026, 1, 10, 12, tzinfo=timezone.utc
        )
        requested_at = requested_at or delivered_at
        return ReturnRequest(
            purchased_at=datetime(2025, 12, 1, 12, tzinfo=timezone.utc),
            delivered_at=delivered_at,
            requested_at=requested_at,
            customer_timezone=customer_timezone,
        )

    def test_request_at_delivery_is_eligible(self) -> None:
        self.assertTrue(is_return_eligible(self.request()))

    def test_request_at_end_of_local_day_30_is_eligible(self) -> None:
        zone = ZoneInfo("America/Los_Angeles")
        delivered = datetime(2026, 1, 1, 8, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 31, 23, 59, 59, 999999, tzinfo=zone)

        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/Los_Angeles",
                )
            )
        )

    def test_request_on_local_day_31_is_not_eligible(self) -> None:
        zone = ZoneInfo("America/New_York")
        delivered = datetime(2026, 3, 1, 23, 30, tzinfo=zone)
        requested = datetime(2026, 4, 1, 0, 0, tzinfo=zone)

        self.assertFalse(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/New_York",
                )
            )
        )

    def test_fall_back_does_not_shorten_day_30(self) -> None:
        zone = ZoneInfo("America/New_York")
        delivered = datetime(2026, 10, 10, 12, tzinfo=zone)
        requested = datetime(2026, 11, 9, 23, 59, tzinfo=zone)

        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/New_York",
                )
            )
        )

    def test_request_before_delivery_is_not_eligible_on_same_local_day(self) -> None:
        zone = ZoneInfo("Asia/Shanghai")
        delivered = datetime(2026, 1, 10, 12, tzinfo=zone)
        requested = datetime(2026, 1, 10, 11, 59, 59, tzinfo=zone)

        self.assertFalse(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="Asia/Shanghai",
                )
            )
        )

    def test_request_before_delivery_is_not_eligible_during_repeated_hour(self) -> None:
        zone = ZoneInfo("America/New_York")
        delivered = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
        requested = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0)

        self.assertFalse(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/New_York",
                )
            )
        )

    def test_purchase_time_does_not_start_return_window(self) -> None:
        request = replace(
            self.request(
                requested_at=datetime(2026, 2, 9, 23, 59, tzinfo=timezone.utc)
            ),
            purchased_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )

        self.assertTrue(is_return_eligible(request))

    def test_each_timezone_naive_timestamp_is_rejected(self) -> None:
        request = self.request()
        for field in ("purchased_at", "delivered_at", "requested_at"):
            with self.subTest(field=field):
                invalid = replace(
                    request, **{field: getattr(request, field).replace(tzinfo=None)}
                )
                with self.assertRaisesRegex(ValueError, field):
                    is_return_eligible(invalid)

    def test_invalid_customer_timezone_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "customer_timezone"):
            is_return_eligible(self.request(customer_timezone="Not/A_Real_Zone"))


if __name__ == "__main__":
    unittest.main()
