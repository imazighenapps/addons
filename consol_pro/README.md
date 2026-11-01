# ConsolPro

Multi-Company Consolidation and Eliminations

## The problem

Every company of the group balances on its own, but the group total exists only in spreadsheets that are retyped by hand before each closing, and the intercompany balances are never cleanly eliminated, so the printed group turnover is inflated by internal transactions.

## The solution

Aggregate the posted balances of several companies by account code, zero the tagged intercompany lines and lock the consolidation once it is posted.

## Main features

- One consolidation line per company and account code, aggregated from the posted entries.
- Debit, credit and net balance per line with stored run totals.
- Accounts that net to zero over the period are skipped automatically.
- Mapping reference on each line to tag the intercompany balances.
- One-click elimination zeroes and flags the mapped lines.
- Posting locks the run: compute and elimination are refused afterwards.
- Reset to draft clears the lines and mappings survive a recompute.
- Multi-company, works with the current company alone, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Consolidation** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
