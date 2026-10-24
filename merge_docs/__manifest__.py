# -*- coding: utf-8 -*-
{
    'name': 'MergeDocs - Customer Document Dossier',
    'version': '18.0.1.0.0',
    'summary': 'Merge quotations, orders, delivery notes and invoices for one customer into a single PDF dossier with a cover page.',
    'description': '''MergeDocs - Customer Document Dossier
=====================================
Your customer does not want twelve PDFs. They want one file.

MergeDocs builds a single dossier for a customer: quotations, confirmed
orders, delivery notes and invoices, in chronological order, with a cover
page, a table of contents and one page per document. The PDF is archived on
the dossier for audit and for your customer portal.

* Load every document of a customer for a period in one click.
* Quotations, orders, delivery notes, invoices and credit notes.
* Cover page and table of contents.
* One page per document, with lines and totals.
* PDF archived as an attachment.
* Multi-company and multi-currency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Productivity/Documents',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'account',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/doc_merge_0_views.xml',
        'views/menus.xml',
        'report/merge_docs_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
