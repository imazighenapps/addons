# BankImportPro

Bank Statement Parsing, Rules and Duplicate Detection

## The problem

Bank statements arrive as CSV or CAMT files and are retyped by hand, transaction by transaction. Between two downloads, a statement gets imported twice and neither the supplier nor the expense account is ever attached to the flow, so reconciliation drags for days.

## The solution

Parse CSV and CAMT bank statement files into statement lines, assign partners and accounts with matching rules, and flag transactions already imported.

## Main features

- CSV parsing of date, label, reference and signed amount.
- Minimal CAMT-style XML parsing with CRDT/DBIT indicators.
- Rules assign a partner and an account from the label.
- Idempotent matching: matched lines are never re-assigned.
- Duplicate detection against already imported batches.
- Live batch total on the batch and on the review lists.
- Invalid content raises no crash: state error plus message.
- Chatter trail, multi-company, no external dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Bank Import** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
