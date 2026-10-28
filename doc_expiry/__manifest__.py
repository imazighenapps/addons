# -*- coding: utf-8 -*-
{
    'name': 'DocExpiry - Document Expiry and Renewal Tracking',
    'version': '19.0.1.0.0',
    'summary': 'Keep every contract, insurance policy, certificate and licence in one register with automatic expiry status, reminder dates and one-click renewals.',
    'description': '''DocExpiry - Document Expiry and Renewal Tracking
================================================
The insurance policy expired three weeks ago and nobody noticed until the
claim was refused.

DocExpiry gives Odoo Community a single register for every document that has
an end date: contracts, insurance policies, certificates, licences, audits
and permits. Each category carries a default validity in days and a reminder
lead time, so the expiry date is filled automatically from the issue date and
the reminder date is computed for you. A live status tells the team at a
glance whether a document is valid, about to expire or already expired, and a
daily scheduler logs a reminder as soon as a document enters its warning
window. Renewing a document is one click: the issue and expiry dates move
forward, and the old and new dates stay in the renewal history.

* Central register for all expiring documents.
* Categories with default validity and reminder lead time.
* Expiry date proposed from the issue date.
* Live status: valid, expiring soon, expired.
* Days left and reminder date computed automatically.
* One-click renewal with a complete history.
* Daily scheduler that logs reminders once per document per day.
* Multi-company, searchable and free of any Enterprise dependency.''',
    'author': 'Farid SLIMANI',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Farid%20SLIMANI',
    'category': 'Productivity/Documents',
    'license': 'OPL-1',
    'price': 59.0,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/expiry_document_0_views.xml',
        'views/expiry_category_1_views.xml',
        'views/expiry_log_2_views.xml',
        'views/menus.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
