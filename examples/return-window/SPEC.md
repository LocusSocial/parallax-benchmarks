# Existing implementation specification

> This document is intentionally plausible but wrong. It represents a specification generated
> from an incomplete understanding of the business goal.

An order is returnable for 30 days after purchase. The service should subtract `purchased_at`
from `requested_at`; a non-negative duration no greater than `30 * 24` hours is eligible.

The service receives UTC timestamps, so no timezone conversion is necessary. Timezone-naive
timestamps are invalid.

