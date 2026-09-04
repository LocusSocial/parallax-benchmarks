# Return eligibility specification

An order is returnable from its delivery instant through the end of the 30th
calendar day after delivery. The delivery date is day 0, so both the delivery
date and the date 30 days later are eligible. A request before the delivery
instant is never eligible.

Calendar dates are determined by converting `delivered_at` and `requested_at`
to `customer_timezone`. The timezone must be a valid IANA timezone. Daylight
saving and other UTC-offset changes therefore do not shorten or extend the
calendar-date window.

`purchased_at`, `delivered_at`, and `requested_at` must all be timezone-aware.
`purchased_at` is retained as order-history data but has no effect on return
eligibility.
