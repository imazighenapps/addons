# -*- coding: utf-8 -*-
{
    'name': 'ReportForge - No-Code Document Templates',
    'version': '18.0.1.0.0',
    'summary': 'Build your own PDF documents with placeholders, no QWeb developer needed: quotes, invoices, letters and product sheets.',
    'description': '''ReportForge - No-Code Document Templates
=======================================
Change your document layout without a developer.

ReportForge lets you write a template with simple placeholders such as
{{ name }} or {{ partner_id.name }}, add a table of lines with {{ lines }},
and generate a professional PDF from any record. Every generated document
is versioned and archived, so you always know which template produced it.

* No-code templates with placeholders for any field.
* Automatic line tables for quotations and invoices.
* Header and footer per template.
* Generate a PDF from a contact, a quotation, an invoice or a product.
* Versioning: each document keeps its template version.
* Archived PDF attachment for audit.
* Works with Odoo Community and Enterprise.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Productivity/Productivity',
    'license': 'OPL-1',
    'price': 129.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'sale',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/forge_template_0_views.xml',
        'views/forge_document_1_views.xml',
        'views/menus.xml',
        'report/forge_report.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
