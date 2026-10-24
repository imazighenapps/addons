# -*- coding: utf-8 -*-
{
    'name': 'PdfBatch - Batch PDF Printing',
    'version': '19.0.1.0.0',
    'summary': 'Select invoices, preview, merge them into one numbered PDF and archive the result, instead of printing one document at a time.',
    'description': '''PdfBatch - Batch PDF Printing
=============================
Print 50 invoices in one click, not 50.

Select the invoices you want in the list, create a batch, preview it, and
PdfBatch builds a single PDF with all the documents, one after the other,
with an optional watermark and a cover page. The PDF is stored on the batch
so you can download or email it later.

* Select any number of customer invoices or credit notes.
* One merged PDF, each document starting on a new page.
* Cover page with period, customer and total.
* Optional watermark (Draft, Copy, Confidential...).
* Preview before printing.
* PDF archived as an attachment for audit.
* Multi-company.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'price': 39.0,
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
        'views/pdf_batch_0_views.xml',
        'views/menus.xml',
        'report/pdf_batch_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
