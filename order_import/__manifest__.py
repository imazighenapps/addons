# -*- coding: utf-8 -*-
{
    'name': 'OrderGate',
    'version': '19.0.1.0.0',
    'summary': 'Import customer order files into validated quotations, with the rejected lines explained instead of lost.',
    'description': '''OrderGate - Files In, Orders Out
===============================
Customer orders arrive as files: CSV exports, emailed spreadsheets and
portal dumps that someone retypes line by line. A missing product code
or a wrong quantity breaks the flow, and the rejected lines vanish in a
chat message instead of being fixed. The team never knows how many
lines were accepted, how many failed and why.

OrderGate keeps one import batch per file with the customer, the import
date and the overall status. Each line records the source reference,
product text, quantity and validation result, with a clear error message
when it cannot be accepted. Validating the batch computes the accepted
and rejected counts, so the operator can correct the failures and
process the file with confidence.

* An import batch per customer file with date, source and status.
* Import lines with source reference, product text, quantity and result.
* Explicit error messages kept on every rejected line.
* Accepted and rejected counts computed and stored on the batch.
* A validation action that reviews every line and updates the batch.
* Search filters for batches with errors and fully accepted files.
* Validation that refuses empty files and negative quantities.
* Multi-company isolation out of the box.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'support': 'imazighenapps@gmail.com',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'price': 49.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule_company.xml',
        'views/order_import_batch_0_views.xml',
        'views/order_import_line_1_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
