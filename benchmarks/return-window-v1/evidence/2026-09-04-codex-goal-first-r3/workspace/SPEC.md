# Return-window policy specification

An order is returnable from its delivery instant through the end of the 30th calendar day after
delivery in the customer's IANA timezone. The delivery date is day 0, so the eligible local-date
range is inclusive from the delivery date through `delivery date + 30 days`.

A request whose instant is before delivery is ineligible, including one that falls on the same
local calendar date. Eligibility is based on local dates rather than elapsed hours, so daylight
saving transitions do not shorten or extend the window.

`purchased_at` is retained for order history and does not determine eligibility. All three
timestamps must be timezone-aware. A timezone-naive timestamp or an invalid customer IANA
timezone is rejected with `ValueError`.
