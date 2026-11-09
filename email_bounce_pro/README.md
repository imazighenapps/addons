# BounceGuard

Bad Addresses Caught Early

## The problem

Odoo marks a notification as bounced and moves on: failures pile up behind unread mail threads, campaigns keep sending to dead addresses and nobody sees the pattern.

## The solution

Read the bounce notifications Odoo already receives, keep a dated register of every rejected address, and flag the customers whose email keeps failing.

## Main features

- Dated event per bounced notification.
- Contact, address and reason on one record.
- Scan replays without duplicates.
- Threshold rule per company.
- Customers flagged beyond the threshold.
- Handle, ignore and reopen events.
- Bounce count on the partner form.
- Company isolation and state filters.

## Installation

1. Install the module from the Apps list.
2. Open the **Email Bounces** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
