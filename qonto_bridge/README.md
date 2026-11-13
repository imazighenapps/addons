# Qonto Bridge

Bank transactions and expenses in sync

## The problem

Qonto bank transactions and expenses are reconciled manually in Odoo, wasting time and creating errors during month-end closing.

## The solution

Import Qonto transactions, match them to payments and expenses, and track synchronization status from Odoo.

## Main features

- Connection profile with organization slug and credential reference.
- Transaction records with amount, date, label and counterpart.
- Reconciliation states (new, matched, ignored) and actions.
- Link to account move/payment references.
- Sync log history and last sync timestamp.
- Attachment references and internal notes.
- Company-aware records and access control.
- No external Python dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Qonto Bridge** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
