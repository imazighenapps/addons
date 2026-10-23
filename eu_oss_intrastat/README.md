# EU OSS & Intrastat Tracker (Odoo 20)

EU cross-border threshold and Intrastat readiness for Odoo 20 Community.

## Scope
- OSS (goods) and IOSS (distance sales) thresholds tracked separately,
  pre-loaded at EUR 10,000 and EUR 150.
- Cumulative sales per country per year, with a live percentage of the
  threshold and a Below / Near / Required status.
- Daily cron recomputing the counters from posted customer invoices.
- Intrastat declaration lines auto-prepared from posted invoices, with
  dispatch/arrival direction, derived country and partner codes, and a
  Draft / Ready / Declared workflow.
- CSV export per period and direction.

## Install
Copy `eu_oss_intrastat` into your addons path, update the apps list, install.
Depends on base, mail, account.

## Tests
`odoo -d <db> -i eu_oss_intrastat --test-enable --stop-after-init`

## Licence
OPL-1. Author: Farid SLIMANI.

## Scope honesty
This module tracks thresholds and prepares the data. It does not file returns
to the tax authority on your behalf and is not a tax advice tool.