# -*- coding: utf-8 -*-
{
    'name': 'EInvoiceValidatePro',
    'version': '18.0.1.0.0',
    'summary': 'Generate a compliant e-invoicing XML document from every posted customer invoice and run plain compliance checks before the new e-invoicing mandates.',
    'description': '''EInvoiceValidatePro - E-Invoicing Checks for CII and UBL Future mandats
======================================================================
E-invoicing mandates are arriving country by country across Europe:
France, Germany, Belgium, Poland and Spain are all phasing in structured
electronic invoices such as UBL, Factur-X (CII) or XRechnung, and they
will soon replace the classic PDF sent by email. A structured document is
not a PDF: it is a machine-readable XML file whose number, dates, party
names, tax lines and totals must all agree, or the receiving platform
rejects it outright. The worst part is when you learn about a rejection:
it usually happens days or weeks later, sometimes only when the customer
complains that the invoice never arrived and the payment is late.
Because the structural checks run deep inside the platform validators,
the accountant has no simple screen to see which invoices are ready and
which ones will bounce. EInvoiceValidatePro adds that screen to Odoo.
For every posted customer invoice you generate a minimal but
syntactically valid UBL-style XML built with the Python standard library
only, then you run a battery of plain checks on the invoice and its XML:
the invoice number, the invoice date, the customer name, at least one
invoice line, the consistency between the line sums, the untaxed amount
and the tax-inclusive total, the VAT collected when the customer carries
a VAT number, and the currency. Every problem is written as an issue with
a code, a severity and the offending field, so correcting an invoice
means reading a short list instead of debugging a validator report.
Validated invoices can be reset and generated again after a correction,
and the chatter keeps the full audit trail of what was checked and when.

* One-click UBL-style XML generation from a posted customer invoice.
* Target format Factur-X, UBL or XRechnung on the same check record.
* Checks on number, date, customer, lines, totals, VAT and currency.
* Issues with a code, a severity and the offending field.
* Valid or invalid verdict, with warnings that do not block.
* Reset to draft, re-generate and re-check after every correction.
* Chatter audit trail of every generation and validation.
* Multi-company, no external Python dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 99.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/einvoice_check_0_views.xml',
        'views/einvoice_issue_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
