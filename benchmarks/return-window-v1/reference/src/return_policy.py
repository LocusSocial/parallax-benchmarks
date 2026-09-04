"""Reference implementation used only to validate the benchmark oracle."""

from dataclasses import dataclass
from datetime import datetime
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
    _require_aware(request.purchased_at, "purchased_at")
    _require_aware(request.delivered_at, "delivered_at")
    _require_aware(request.requested_at, "requested_at")
    try:
        zone = ZoneInfo(request.customer_timezone)
    except ZoneInfoNotFoundError as error:
        raise ValueError("customer_timezone must be a valid IANA timezone") from error

    delivered = request.delivered_at.astimezone(zone).date()
    requested = request.requested_at.astimezone(zone).date()
    elapsed_calendar_days = (requested - delivered).days
    return 0 <= elapsed_calendar_days <= 30

