# ScanPack Desk

Barcode Pick Validation

## The problem

Odoo Community validates a picking without any proof that the physical items were prepared: the Validate button is free. Barcode pick validation exists only in the Enterprise app, so small Community warehouses improvise with paper lists and discover the picking errors when the customer does.

## The solution

Validate pickings by barcode scan: accepted scans are logged, unexpected barcodes are refused, and validation stays blocked while prepared differs from requested, unless a manager grants a reason-tracked exception.

## Main features

- One scan field per picking: product barcode or internal reference.
- Accepted scans grow the prepared quantity of the exact pick line.
- Unexpected barcodes are refused and written to the scan journal.
- Validation blocked while prepared does not match requested.
- Manager exception with a mandatory reason, written to the journal.
- Immutable scan journal per picking: who, what, when and why.
- Scan quantity per scan is configurable for packed lines.
- Multi-company and multi-currency safe, no Enterprise dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **Scan Pack** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 19.0 Community and Enterprise.
- Odoo 18.0 and 20.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
