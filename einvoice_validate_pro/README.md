# EInvoiceValidatePro - E-Invoicing Checks for CII and UBL Future mandats

## The problem

Structured e-invoices such as UBL, Factur-X or XRechnung are rejected by the receiving platform as soon as a total, a tax or a party name is inconsistent, and the accountant usually learns about it days later when the payment is already late. There is no simple Odoo screen to see which posted invoices would survive an e-invoicing check.

## The solution

Generate a compliant e-invoicing XML document from every posted customer invoice and run plain compliance checks before the new e-invoicing mandates.

## Main features

- One-click UBL-style XML generation from a posted customer invoice.
- Target format Factur-X, UBL or XRechnung on the same check record.
- Checks on number, date, customer, lines, totals, VAT and currency.
- Issues with a code, a severity and the offending field.
- Valid or invalid verdict, with warnings that do not block.
- Reset to draft, re-generate and re-check after every correction.
- Chatter audit trail of every generation and validation.
- Multi-company and multi-currency, no external Python dependency.

## Installation

1. Install the module from the Apps list.
2. Open the **E-Invoice Checks** menu.
3. Create your first record and follow the guided empty state.

## Compatibility

- Odoo 20.0 Community and Enterprise.
- Odoo 18.0 and 19.0 versions are provided separately.
- No external Python dependency.

## License

OPL-1 (Odoo Proprietary License).
