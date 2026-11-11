# OrderGate

Files In, Orders Out

## The problem

Customer order files are retyped by hand and rejected lines disappear, so operators cannot see what failed, why it failed or how much of the file was accepted.

## The solution

Import customer order files into validated quotations, with the rejected lines explained instead of lost.

## Main features

- An import batch per customer file with date, source and status.
- Import lines with source reference, product text, quantity and result.
- Explicit error messages kept on every rejected line.
- Accepted and rejected counts computed and stored on the batch.
- A validation action that reviews every line and updates the batch.
- Search filters for batches with errors and fully accepted files.
- Validation that refuses empty files and negative quantities.
- Multi-company isolation out of the box.

## Installation

1. Install the module from the Apps list.
2. Open the **Order Imports** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 18.0 Community and Enterprise.
- Odoo 19.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
