"""Return eligibility for the delivery-based, local-calendar-day policy."""

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class ReturnRequest:
    purchased_at: datetime
    delivered_at: datetime
    requested_at: datetime
    customer_timezone: str


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


def is_return_eligible(request: ReturnRequest) -> bool:
    """Return whether a request is within the inclusive local-date window."""

    _require_aware(request.purchased_at, "purchased_at")
    _require_aware(request.delivered_at, "delivered_at")
    _require_aware(request.requested_at, "requested_at")

    try:
        customer_timezone = ZoneInfo(request.customer_timezone)
    except (ZoneInfoNotFoundError, TypeError, ValueError) as error:
        raise ValueError(
            f"invalid IANA timezone: {request.customer_timezone!r}"
        ) from error

    # Normalize before comparing: datetime comparisons with the same tzinfo
    # object use wall-clock values, which are ambiguous during a DST fold.
    if request.requested_at.astimezone(timezone.utc) < request.delivered_at.astimezone(
        timezone.utc
    ):
        return False

    delivered_date = request.delivered_at.astimezone(customer_timezone).date()
    requested_date = request.requested_at.astimezone(customer_timezone).date()
    calendar_days = (requested_date - delivered_date).days
    return 0 <= calendar_days <= 30
