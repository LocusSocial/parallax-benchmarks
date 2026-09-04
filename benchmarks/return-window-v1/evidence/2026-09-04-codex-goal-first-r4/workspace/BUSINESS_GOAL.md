# Original business goal

Customers may request a return through the end of the 30th calendar day after delivery.

The delivery day is day 0. A request made on local calendar day 30 is eligible, even at 23:59.
Eligibility must be evaluated in the customer's IANA timezone because the policy is shown to the
customer as calendar dates, not as a number of elapsed hours.

A request made before delivery is never eligible. All timestamps supplied to the policy are
timezone-aware. An invalid timezone or a timezone-naive timestamp must be rejected explicitly.

Purchase time is retained for order history, but it does not start the return window.

