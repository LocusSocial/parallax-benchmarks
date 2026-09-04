"""Return eligibility implementation for the current 30-day policy."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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


def _customer_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as error:
        raise ValueError(
            "customer_timezone must be a valid IANA timezone"
        ) from error


def is_return_eligible(request: ReturnRequest) -> bool:
    """Return whether a request is within the delivery-based return window."""

    _require_aware(request.purchased_at, "purchased_at")
    _require_aware(request.delivered_at, "delivered_at")
    _require_aware(request.requested_at, "requested_at")
    customer_zone = _customer_zone(request.customer_timezone)

    delivered_instant = request.delivered_at.astimezone(timezone.utc)
    requested_instant = request.requested_at.astimezone(timezone.utc)
    if requested_instant < delivered_instant:
        return False

    delivered_date = request.delivered_at.astimezone(customer_zone).date()
    requested_date = request.requested_at.astimezone(customer_zone).date()
    return delivered_date <= requested_date <= delivered_date + timedelta(days=30)
