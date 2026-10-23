# Cleaning Ops Lite (Odoo 18)

Run a small cleaning or soft-services company on Odoo 18 Community.

## Scope
- Customer sites with area, access notes and assigned agents.
- Recurring visit plans (daily, weekly, biweekly, monthly, quarterly) with
  automatic next-date computation and daily visit generation.
- Agent check-in / check-out with automatic duration calculation and guards.
- Quality score and checklist per visit.
- Billing per visit or per square metre, with one-click invoicing from a
  completed visit.

## Install
Copy `cleaning_ops_lite` into your addons path, update the apps list, install.
Depends on base, mail, uom, sale.

## Tests
`odoo -d <db> -i cleaning_ops_lite --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.