import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.return_policy import ReturnRequest, is_return_eligible


class ReturnPolicyTests(unittest.TestCase):
    def request(
        self,
        delivered_at: datetime,
        requested_at: datetime,
        *,
        purchased_at: datetime | None = None,
        customer_timezone: str = "UTC",
    ) -> ReturnRequest:
        return ReturnRequest(
            purchased_at=purchased_at or delivered_at - timedelta(days=7),
            delivered_at=delivered_at,
            requested_at=requested_at,
            customer_timezone=customer_timezone,
        )

    def test_request_at_delivery_is_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        self.assertTrue(is_return_eligible(self.request(delivered, delivered)))

    def test_request_at_end_of_local_day_30_is_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        requested = datetime(
            2026, 1, 31, 23, 59, 59, 999999, tzinfo=timezone.utc
        )
        self.assertTrue(is_return_eligible(self.request(delivered, requested)))

    def test_request_at_start_of_local_day_31_is_not_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        requested = datetime(2026, 2, 1, tzinfo=timezone.utc)
        self.assertFalse(is_return_eligible(self.request(delivered, requested)))

    def test_request_before_delivery_is_not_eligible_on_same_local_day(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        requested = delivered - timedelta(microseconds=1)
        self.assertFalse(is_return_eligible(self.request(delivered, requested)))

    def test_pre_delivery_check_uses_instant_during_repeated_dst_hour(self) -> None:
        new_york = ZoneInfo("America/New_York")
        # The first 01:45 (EDT) is 45 minutes before the second 01:30 (EST),
        # despite appearing later by its wall-clock fields.
        delivered = datetime(
            2026, 11, 1, 1, 30, fold=1, tzinfo=new_york
        )
        requested = datetime(
            2026, 11, 1, 1, 45, fold=0, tzinfo=new_york
        )

        self.assertFalse(is_return_eligible(self.request(delivered, requested)))

    def test_purchase_time_does_not_change_eligibility(self) -> None:
        delivered = datetime(2026, 6, 1, 12, tzinfo=timezone.utc)
        requested = datetime(2026, 6, 15, 12, tzinfo=timezone.utc)
        recent_purchase = delivered - timedelta(days=1)
        old_purchase = delivered - timedelta(days=365)

        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered, requested, purchased_at=recent_purchase
                )
            )
        )
        self.assertTrue(
            is_return_eligible(
                self.request(delivered, requested, purchased_at=old_purchase)
            )
        )

    def test_customer_timezone_determines_calendar_boundary(self) -> None:
        # In Tokyo these are Jan 2 at 00:30 and Feb 1 at 23:59: day 30.
        delivered = datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc)
        requested = datetime(2026, 2, 1, 14, 59, tzinfo=timezone.utc)
        policy_request = self.request(
            delivered, requested, customer_timezone="Asia/Tokyo"
        )

        self.assertTrue(is_return_eligible(policy_request))

    def test_day_after_boundary_in_customer_timezone_is_not_eligible(self) -> None:
        # One minute later than the preceding case is Feb 2 in Tokyo: day 31.
        delivered = datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc)
        requested = datetime(2026, 2, 1, 15, tzinfo=timezone.utc)
        policy_request = self.request(
            delivered, requested, customer_timezone="Asia/Tokyo"
        )

        self.assertFalse(is_return_eligible(policy_request))

    def test_dst_change_does_not_shorten_day_30(self) -> None:
        new_york = ZoneInfo("America/New_York")
        delivered = datetime(2026, 10, 10, 12, tzinfo=new_york)
        requested = datetime(
            2026, 11, 9, 23, 59, 59, tzinfo=new_york
        ).astimezone(timezone.utc)
        policy_request = self.request(
            delivered, requested, customer_timezone="America/New_York"
        )

        self.assertTrue(is_return_eligible(policy_request))

    def test_each_timezone_naive_timestamp_is_rejected(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        valid = self.request(delivered, delivered + timedelta(days=1))

        for field in ("purchased_at", "delivered_at", "requested_at"):
            values = {
                "purchased_at": valid.purchased_at,
                "delivered_at": valid.delivered_at,
                "requested_at": valid.requested_at,
                "customer_timezone": valid.customer_timezone,
            }
            values[field] = values[field].replace(tzinfo=None)
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, field
            ):
                is_return_eligible(ReturnRequest(**values))

    def test_invalid_customer_timezone_is_rejected(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        invalid = self.request(
            delivered,
            delivered + timedelta(days=1),
            customer_timezone="Mars/Olympus_Mons",
        )

        with self.assertRaisesRegex(ValueError, "customer_timezone"):
            is_return_eligible(invalid)


if __name__ == "__main__":
    unittest.main()
