# MatchControlPro

Three-Way Match for Purchase Orders, Receipts and Vendor Bills

## The problem

Vendor bills are paid on trust: nobody compares them with the purchase order and the receipt, so short deliveries and silent price increases are only discovered months later, at the audit or never.

## The solution

Compare purchase orders, receipts and vendor bills line by line, flag quantity and price variances outside tolerance, and force a written reason before validating an exception.

## Main features

- One match check per vendor bill, enforced per company.
- Ordered quantities from the purchase order lines.
- Received quantities from the done stock moves of the receipt.
- Billed quantities and unit prices from the vendor bill lines.
- Configurable tolerance on quantities and unit prices.
- Line status: compliant, quantity variance or price variance.
- Exception state with a mandatory written reason before validation.
- Totals and variance amount, recomputed from the lines.

## Installation

1. Install the module from the Apps list.
2. Open the **Match Control** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
