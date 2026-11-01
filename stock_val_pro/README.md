# StockValPro - Stock Valuation Report for Month-End Closing

## The problem

At month-end the stock valuation is rebuilt by hand from an export of stock moves and a cost list that is never in sync, so the inventory total cannot be reconciled with the ledger and the auditor has no detail behind it.

## The solution

Month-end stock valuation per product from done moves, valued at cost, with totals, slow movers and a confirm lock for the closing file.

## Main features

- One valuation line per product for any period.
- Inbound and outbound quantities from done moves only.
- Values frozen at the standard cost of the generation date.
- Net balance quantity and value per product.
- Report totals computed from the lines.
- Slow mover flag for products received but never issued.
- Confirmed reports locked against regeneration.
- Multi-company, optional location filter, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Stock Valuation** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 18.0 Community and Enterprise.
- Odoo 19.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
