# SalePlan Pay

Installment Plans on Sales

## The problem

Odoo Community has no multi-installment payment plan on a sale order: the down payment is single and without a calendar, so teams recreate draft invoices by hand and have no view of late installments.

## The solution

Split a confirmed sale order into dated installments matching the order total, generate a draft invoice per installment in one click, and track planned, invoiced, paid and late installments in a company-safe view.

## Main features

- Payment plan attached to a confirmed sale order.
- N installments with amount and due date, sum must match the order.
- One-click draft invoice generated from an installment.
- An invoiced installment cannot generate a second invoice.
- Computed status per installment: planned, invoiced, paid, late.
- Kanban and grouped view of late installments by customer.
- Multi-company and multi-currency safe, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Payment Plans** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
