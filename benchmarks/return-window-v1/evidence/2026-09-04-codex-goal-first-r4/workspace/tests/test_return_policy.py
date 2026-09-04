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

    def test_request_at_delivery_is_eligible(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        self.assertTrue(
            is_return_eligible(
                self.request(delivered_at=delivered, requested_at=delivered)
            )
        )

    def test_request_at_end_of_local_day_30_is_eligible(self) -> None:
        shanghai = ZoneInfo("Asia/Shanghai")
        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=datetime(2026, 1, 1, 20, 30, tzinfo=shanghai),
                    requested_at=datetime(2026, 1, 31, 23, 59, 59, tzinfo=shanghai),
                    customer_timezone="Asia/Shanghai",
                )
            )
        )

    def test_request_at_start_of_local_day_31_is_not_eligible(self) -> None:
        tokyo = ZoneInfo("Asia/Tokyo")
        self.assertFalse(
            is_return_eligible(
                self.request(
                    delivered_at=datetime(2026, 1, 1, 23, 59, tzinfo=tokyo),
                    requested_at=datetime(2026, 2, 1, 0, 0, tzinfo=tokyo),
                    customer_timezone="Asia/Tokyo",
                )
            )
        )

    def test_request_before_delivery_is_not_eligible_on_same_local_day(self) -> None:
        delivered = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 1, 11, 59, 59, tzinfo=timezone.utc)
        self.assertFalse(
            is_return_eligible(
                self.request(delivered_at=delivered, requested_at=requested)
            )
        )

    def test_customer_timezone_controls_calendar_dates(self) -> None:
        # These instants are on dates 30 days apart in Tokyo, but their UTC
        # calendar dates are 31 days apart. Eligibility follows the customer.
        delivered = datetime(2025, 12, 31, 15, 30, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 31, 14, 30, tzinfo=timezone.utc)
        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="Asia/Tokyo",
                )
            )
        )

    def test_dst_change_does_not_turn_day_30_into_an_elapsed_time_limit(self) -> None:
        new_york = ZoneInfo("America/New_York")
        # The fall-back transition makes this more than 30 * 24 elapsed hours.
        delivered = datetime(2026, 10, 10, 0, 0, tzinfo=new_york)
        requested = datetime(2026, 11, 9, 23, 59, tzinfo=new_york)
        self.assertTrue(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/New_York",
                )
            )
        )

    def test_purchase_time_does_not_start_the_window(self) -> None:
        purchased = datetime(2025, 1, 1, tzinfo=timezone.utc)
        delivered = datetime(2026, 1, 1, tzinfo=timezone.utc)
        requested = datetime(2026, 1, 2, tzinfo=timezone.utc)
        self.assertTrue(
            is_return_eligible(
                self.request(
                    purchased_at=purchased,
                    delivered_at=delivered,
                    requested_at=requested,
                )
            )
        )

    def test_pre_delivery_check_uses_instants_during_dst_fold(self) -> None:
        new_york = ZoneInfo("America/New_York")
        # 01:45 EDT is 45 minutes before 01:30 EST, despite its later wall time.
        requested = datetime(2026, 11, 1, 1, 45, fold=0, tzinfo=new_york)
        delivered = datetime(2026, 11, 1, 1, 30, fold=1, tzinfo=new_york)
        self.assertFalse(
            is_return_eligible(
                self.request(
                    delivered_at=delivered,
                    requested_at=requested,
                    customer_timezone="America/New_York",
                )
            )
        )

    def test_each_timezone_naive_timestamp_is_rejected(self) -> None:
        aware = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        valid = self.request(delivered_at=aware, requested_at=aware)
        for field in ("purchased_at", "delivered_at", "requested_at"):
            values = {
                "purchased_at": valid.purchased_at,
                "delivered_at": valid.delivered_at,
                "requested_at": valid.requested_at,
                "customer_timezone": valid.customer_timezone,
            }
            values[field] = values[field].replace(tzinfo=None)
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, f"{field} must be timezone-aware"
            ):
                is_return_eligible(ReturnRequest(**values))

    def test_invalid_customer_timezone_is_rejected(self) -> None:
        aware = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        invalid = self.request(
            delivered_at=aware,
            requested_at=aware,
            customer_timezone="Not/A_Timezone",
        )
        with self.assertRaisesRegex(ValueError, "invalid IANA timezone"):
            is_return_eligible(invalid)


if __name__ == "__main__":
    unittest.main()
