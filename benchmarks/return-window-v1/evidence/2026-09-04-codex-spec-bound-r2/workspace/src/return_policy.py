"""Return eligibility implementation for the current 30-day policy."""

from dataclasses import dataclass
from datetime import datetime, timedelta


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
    """Return whether a request satisfies the existing 30-day specification."""

    _require_aware(request.purchased_at, "purchased_at")
    _require_aware(request.delivered_at, "delivered_at")
    _require_aware(request.requested_at, "requested_at")

    elapsed = request.requested_at - request.purchased_at
    return timedelta(0) <= elapsed <= timedelta(days=30)
