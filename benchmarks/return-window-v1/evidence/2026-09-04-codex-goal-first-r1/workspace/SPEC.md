# Return eligibility specification

An order is returnable when the request falls on local calendar day 0 through
local calendar day 30 after delivery, inclusive. The delivery date is day 0.
Eligibility is based on the dates in `customer_timezone`, not on elapsed hours.

A request whose instant is before the delivery instant is ineligible. Purchase
time is retained as order metadata and does not affect the return window.

`purchased_at`, `delivered_at`, and `requested_at` must all be timezone-aware.
`customer_timezone` must name a valid IANA timezone. Invalid inputs raise
`ValueError`.
