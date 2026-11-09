# PriceWatch

Supplier Price Movements

## The problem

Purchase prices drift between orders: delivery fees, packaging or a silent indexation push the same reference above the negotiated price, and nobody compares the two order lines until a budget is blown.

## The solution

Keep the last purchase price of every product and supplier, compare each new order line with it, and raise a dated alert as soon as a variation crosses your threshold.

## Main features

- Dated alert per order line.
- Variation in percent and in currency.
- Threshold rule per company.
- First purchase never alerts.
- One alert per line, replays safe.
- Review, ignore and reopen alerts.
- Graph of variations by state.
- Company isolation and window filters.

## Installation

1. Install the module from the Apps list.
2. Open the **Supplier Prices** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
