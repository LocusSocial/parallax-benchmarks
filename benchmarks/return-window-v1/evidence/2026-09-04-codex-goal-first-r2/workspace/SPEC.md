# Return eligibility specification

An order is returnable from its delivery instant through the end of the 30th
calendar day after delivery. The delivery date is day 0, so both the delivery
date and the date 30 days later are included.

Eligibility is based on dates in `customer_timezone`, which must name a valid
IANA timezone. Convert `delivered_at` and `requested_at` to that timezone before
comparing their calendar dates. Do not implement the window as 30 elapsed
24-hour periods; daylight-saving changes and source timestamp offsets must not
alter the customer-visible dates.

A request whose instant precedes the delivery instant is not eligible, even if
both timestamps fall on the same local date. `purchased_at` is retained but is
not part of the eligibility calculation.

All supplied timestamps must be timezone-aware. A timezone-naive timestamp or
an invalid customer timezone is rejected with `ValueError`.
