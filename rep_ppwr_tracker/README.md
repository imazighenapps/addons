# REP & PPWR Packaging Tracker (Odoo 18)

French EPR declarations and EU PPWR readiness for Odoo 18 Community.

## Scope
- Material referential (11 materials) + 2026 tariffs (household + professional).
- Product packaging sheets: weight, level, reuse, recycled content, A-E class.
- Automatic eco-cost on sale order lines and delivery ledger generation.
- Annual declarations aggregated by material + CSV export.
- Deposits with return-rate tracking.

## Install
Copy `rep_ppwr_tracker` into your addons path, update the apps list,
install. Depends on base, mail, product, sale, stock.

## Tests
`odoo -d <db> -i rep_ppwr_tracker --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.
